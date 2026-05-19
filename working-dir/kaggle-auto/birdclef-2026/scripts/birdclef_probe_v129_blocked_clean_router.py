#!/usr/bin/env python3
"""Blocked validation for clean non-Tsubasa routing.

Earlier clean router probes selected classes on the same train-window rows used
for scoring. This probe makes the originality lane stricter: for each held-out
train soundscape file, it selects per-class side sources on the other files only
and applies the learned rank-calibrated router to the held-out file.

The probe is local-only and never submits to Kaggle.
"""

from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from pathlib import Path
import sys

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from src.metrics import binary_roc_auc, multilabel_macro_auc  # noqa: E402


@dataclass(frozen=True)
class SourceSpec:
    name: str
    path: Path
    role: str


def labels_to_targets(meta: pd.DataFrame, labels: pd.DataFrame, class_names: list[str]) -> np.ndarray:
    label_map: dict[str, set[str]] = {}
    for row in labels.itertuples(index=False):
        try:
            end_sec = int(str(row.end).split(":")[-1])
        except Exception:
            continue
        key = f"{Path(str(row.filename)).stem}_{end_sec}"
        label_map[key] = {x for x in str(row.primary_label).split(";") if x}

    class_index = {c: i for i, c in enumerate(class_names)}
    y = np.zeros((len(meta), len(class_names)), dtype=np.uint8)
    for i, row_id in enumerate(meta["row_id"].astype(str).tolist()):
        for lab in label_map.get(row_id, set()):
            j = class_index.get(lab)
            if j is not None:
                y[i, j] = 1
    return y


def row_groups(row_ids: pd.Series) -> np.ndarray:
    return row_ids.astype(str).str.replace(r"_\d+$", "", regex=True).to_numpy()


def topk_hit_rate(y_true: np.ndarray, y_score: np.ndarray, k: int) -> float | None:
    rows = np.where(y_true.sum(axis=1) > 0)[0]
    if len(rows) == 0:
        return None
    hits = 0
    for i in rows:
        top = np.argpartition(y_score[i], -k)[-k:]
        if y_true[i, top].any():
            hits += 1
    return hits / len(rows)


def load_submission(path: Path, class_names: list[str]) -> pd.DataFrame:
    df = pd.read_csv(path)
    missing = [c for c in ["row_id", *class_names] if c not in df.columns]
    if missing:
        raise ValueError(f"{path} missing columns: {missing[:5]}")
    return df[["row_id", *class_names]].copy()


def per_class_auc(y_true: np.ndarray, values: np.ndarray) -> np.ndarray:
    aucs = np.full(values.shape[1], np.nan, dtype=np.float64)
    for idx in range(values.shape[1]):
        auc = binary_roc_auc(y_true[:, idx], values[:, idx])
        if auc is not None:
            aucs[idx] = auc
    return aucs


def score_values(name: str, y_true: np.ndarray, values: np.ndarray, class_names: list[str], anchor: np.ndarray) -> dict[str, object]:
    macro = multilabel_macro_auc(y_true, values, class_names)
    micro = binary_roc_auc(y_true.ravel(), values.ravel())
    top1 = topk_hit_rate(y_true, values, 1)
    top5 = topk_hit_rate(y_true, values, 5)
    return {
        "name": name,
        "macro_auc": "" if macro["mean_auc"] is None else f"{macro['mean_auc']:.8f}",
        "micro_auc": "" if micro is None else f"{micro:.8f}",
        "top1_hit": "" if top1 is None else f"{top1:.8f}",
        "top5_hit": "" if top5 is None else f"{top5:.8f}",
        "scored_classes": macro["scored_classes"],
        "corr_vs_anchor": f"{float(np.corrcoef(anchor.ravel(), values.ravel())[0, 1]):.8f}",
        "mad_vs_anchor": f"{float(np.mean(np.abs(anchor - values))):.8f}",
        "min": f"{float(np.nanmin(values)):.8f}",
        "max": f"{float(np.nanmax(values)):.8f}",
    }


def calibrate_holdout_to_anchor(
    train_side: np.ndarray,
    train_anchor: np.ndarray,
    hold_side: np.ndarray,
) -> np.ndarray:
    """Map held-out side values to the train-anchor distribution by percentile."""
    calibrated = np.empty_like(hold_side, dtype=np.float64)
    n_train = train_side.shape[0]
    if n_train == 1:
        return np.broadcast_to(train_anchor, hold_side.shape).copy()
    quant_x = np.linspace(0.0, 1.0, n_train)
    for col in range(train_side.shape[1]):
        side_sorted = np.sort(train_side[:, col])
        anchor_sorted = np.sort(train_anchor[:, col])
        pos = np.searchsorted(side_sorted, hold_side[:, col], side="right") - 1
        pct = np.clip(pos / max(1, n_train - 1), 0.0, 1.0)
        calibrated[:, col] = np.interp(pct, quant_x, anchor_sorted)
    return calibrated


def apply_fold_router(
    y_train: np.ndarray,
    anchor_train: np.ndarray,
    anchor_hold: np.ndarray,
    side_train: dict[str, np.ndarray],
    side_hold: dict[str, np.ndarray],
    class_names: list[str],
    min_support: int,
    min_delta: float,
    weight: float,
    top5_guard: bool,
) -> tuple[np.ndarray, list[dict[str, object]]]:
    anchor_auc = per_class_auc(y_train, anchor_train)
    support = y_train.sum(axis=0).astype(np.float64)
    support_gate = np.clip(np.log1p(support) / np.log1p(max(1.0, float(support.max()))), 0.25, 1.0)
    side_auc = {name: per_class_auc(y_train, values) for name, values in side_train.items()}
    side_cal = {
        name: calibrate_holdout_to_anchor(values, anchor_train, side_hold[name])
        for name, values in side_train.items()
    }

    mixed = anchor_hold.copy()
    selected: list[dict[str, object]] = []
    top5_idx = np.argpartition(anchor_hold, -5, axis=1)[:, -5:]

    for idx, class_name in enumerate(class_names):
        if support[idx] < min_support or not np.isfinite(anchor_auc[idx]):
            continue
        scored = [
            (source_name, aucs[idx])
            for source_name, aucs in side_auc.items()
            if np.isfinite(aucs[idx])
        ]
        if not scored:
            continue
        source_name, best_auc = max(scored, key=lambda x: x[1])
        delta = best_auc - anchor_auc[idx]
        if delta < min_delta:
            continue

        col_weight = weight * support_gate[idx]
        candidate_col = np.clip(
            (1.0 - col_weight) * anchor_hold[:, idx] + col_weight * side_cal[source_name][:, idx],
            0.0,
            1.0,
        )
        if top5_guard:
            in_anchor_top5 = (top5_idx == idx).any(axis=1)
            positive = candidate_col > anchor_hold[:, idx]
            mask = positive | in_anchor_top5
            if not mask.any():
                continue
            mixed[mask, idx] = candidate_col[mask]
            active_rows = int(mask.sum())
        else:
            mixed[:, idx] = candidate_col
            active_rows = int(anchor_hold.shape[0])

        selected.append(
            {
                "class_name": class_name,
                "support_train": int(support[idx]),
                "source": source_name,
                "anchor_auc_train": f"{anchor_auc[idx]:.8f}",
                "side_auc_train": f"{best_auc:.8f}",
                "delta_train": f"{delta:.8f}",
                "active_rows": active_rows,
            }
        )
    return mixed, selected


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", type=Path, default=ROOT / "birdclef-2026/data")
    parser.add_argument("--output-csv", type=Path, default=ROOT / "experiments/v129_blocked_clean_router_probe.csv")
    parser.add_argument("--selection-csv", type=Path, default=ROOT / "experiments/v129_blocked_clean_router_selection.csv")
    args = parser.parse_args()

    sample = pd.read_csv(args.data_dir / "sample_submission.csv", nrows=1)
    class_names = list(sample.columns[1:])
    labels = pd.read_csv(args.data_dir / "train_soundscapes_labels.csv")

    sources = [
        SourceSpec("v110_clean", ROOT / "birdclef-2026/outputs/v110-ecoproto-clean-blend-v1/submission.csv", "anchor"),
        SourceSpec("v114_clean_selfblend", ROOT / "birdclef-2026/outputs/v114-v110-v113-selfblend-v1/submission.csv", "anchor"),
        SourceSpec("v112_backtracking_remap", ROOT / "birdclef-2026/outputs/v112-clean-sed-remap-ecoproto-v1/submission.csv", "clean_side"),
        SourceSpec("v113_lantingguo_melnorm", ROOT / "birdclef-2026/outputs/v113-lantingguo-melnorm-ecoproto-v1/submission.csv", "clean_side"),
        SourceSpec("v119_roniheka_hgnet", ROOT / "birdclef-2026/outputs/v119-roniheka-hgnet-sed-v1/submission.csv", "clean_side"),
    ]

    frames = {source.name: load_submission(source.path, class_names) for source in sources}
    row_ids = frames[sources[0].name]["row_id"].astype(str).tolist()
    for source in sources[1:]:
        if frames[source.name]["row_id"].astype(str).tolist() != row_ids:
            raise ValueError(f"{source.name} row_id order mismatch")

    groups = row_groups(frames[sources[0].name]["row_id"])
    unique_groups = sorted(set(groups))
    y_true = labels_to_targets(frames[sources[0].name][["row_id"]], labels, class_names)
    values = {name: df[class_names].to_numpy(dtype=np.float64) for name, df in frames.items()}
    anchors = [source for source in sources if source.role == "anchor"]
    side_names = [source.name for source in sources if source.role == "clean_side"]

    rows: list[dict[str, object]] = []
    selections: list[dict[str, object]] = []

    for anchor_spec in anchors:
        anchor = values[anchor_spec.name]
        rows.append(
            {
                **score_values(f"{anchor_spec.name}_baseline", y_true, anchor, class_names, anchor),
                "anchor": anchor_spec.name,
                "min_support": "",
                "min_delta": "",
                "weight": "",
                "top5_guard": "",
                "avg_classes_per_fold": "",
                "total_selected_entries": "",
            }
        )
        for min_support in [5, 10, 15, 20]:
            for min_delta in [0.0, 0.002, 0.005, 0.01]:
                for weight in [0.35, 0.50, 0.70, 0.90]:
                    for top5_guard in [False, True]:
                        oof = anchor.copy()
                        fold_counts: list[int] = []
                        selected_entries = 0
                        candidate = (
                            f"v129_{anchor_spec.name}_min{min_support}"
                            f"_d{min_delta:g}_w{weight:g}_top5guard{int(top5_guard)}"
                        )
                        for group in unique_groups:
                            hold = groups == group
                            train = ~hold
                            side_train = {name: values[name][train] for name in side_names}
                            side_hold = {name: values[name][hold] for name in side_names}
                            mixed_hold, selected = apply_fold_router(
                                y_true[train],
                                anchor[train],
                                anchor[hold],
                                side_train,
                                side_hold,
                                class_names,
                                min_support,
                                min_delta,
                                weight,
                                top5_guard,
                            )
                            oof[hold] = mixed_hold
                            fold_counts.append(len(selected))
                            selected_entries += len(selected)
                            for row in selected:
                                selections.append(
                                    {
                                        "candidate": candidate,
                                        "anchor": anchor_spec.name,
                                        "fold_group": group,
                                        "min_support": min_support,
                                        "min_delta": min_delta,
                                        "weight": weight,
                                        "top5_guard": int(top5_guard),
                                        **row,
                                    }
                                )

                        rows.append(
                            {
                                **score_values(candidate, y_true, oof, class_names, anchor),
                                "anchor": anchor_spec.name,
                                "min_support": min_support,
                                "min_delta": min_delta,
                                "weight": weight,
                                "top5_guard": int(top5_guard),
                                "avg_classes_per_fold": f"{float(np.mean(fold_counts)):.4f}",
                                "total_selected_entries": selected_entries,
                            }
                        )

    rows.sort(key=lambda r: (float(r["macro_auc"] or -1), float(r["top5_hit"] or -1)), reverse=True)
    args.output_csv.parent.mkdir(parents=True, exist_ok=True)
    with args.output_csv.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    args.selection_csv.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "candidate",
        "anchor",
        "fold_group",
        "min_support",
        "min_delta",
        "weight",
        "top5_guard",
        "class_name",
        "support_train",
        "source",
        "anchor_auc_train",
        "side_auc_train",
        "delta_train",
        "active_rows",
    ]
    with args.selection_csv.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(selections)

    print(f"groups={len(unique_groups)} rows={len(y_true)} classes={len(class_names)}")
    print(f"wrote {args.output_csv} rows={len(rows)}")
    print(f"wrote {args.selection_csv} rows={len(selections)}")
    for row in rows[:12]:
        print(
            row["name"],
            row["macro_auc"],
            row["micro_auc"],
            row["top5_hit"],
            row["avg_classes_per_fold"],
            row["corr_vs_anchor"],
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
