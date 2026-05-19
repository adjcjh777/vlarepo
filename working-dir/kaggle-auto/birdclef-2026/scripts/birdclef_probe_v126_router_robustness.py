#!/usr/bin/env python3
"""Robustness probe for the v125 non-Tsubasa class router.

v125 found a local macro gain, but the best formula included one very-low-support
class. This script stress-tests the same original router under explicit support
floors so that the next materialization decision is driven by robust evidence
rather than a fragile dry-run artifact.
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path
import sys

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from src.metrics import binary_roc_auc, multilabel_macro_auc  # noqa: E402


SIDE_SOURCES = {
    "v112_backtracking_remap": ROOT / "birdclef-2026/outputs/v112-clean-sed-remap-ecoproto-v1/submission.csv",
    "v113_lantingguo_melnorm": ROOT / "birdclef-2026/outputs/v113-lantingguo-melnorm-ecoproto-v1/submission.csv",
    "v119_roniheka_hgnet": ROOT / "birdclef-2026/outputs/v119-roniheka-hgnet-sed-v1/submission.csv",
}


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


def rankcal_to_anchor(side: np.ndarray, anchor: np.ndarray) -> np.ndarray:
    calibrated = np.empty_like(side, dtype=np.float64)
    side_order = np.argsort(side, axis=0, kind="mergesort")
    anchor_sorted = np.sort(anchor, axis=0)
    col_idx = np.arange(side.shape[1])
    calibrated[side_order, col_idx] = anchor_sorted
    return calibrated


def per_class_auc(y_true: np.ndarray, values: np.ndarray, class_names: list[str]) -> np.ndarray:
    aucs = np.full(len(class_names), np.nan, dtype=np.float64)
    for idx in range(len(class_names)):
        auc = binary_roc_auc(y_true[:, idx], values[:, idx])
        if auc is not None:
            aucs[idx] = auc
    return aucs


def score_values(
    name: str,
    values: np.ndarray,
    y_true: np.ndarray,
    class_names: list[str],
    anchor: np.ndarray,
    selected_classes: list[str],
    selected_sources: list[str],
    min_support: int,
    weight: float,
) -> dict[str, object]:
    macro = multilabel_macro_auc(y_true, values, class_names)
    micro = binary_roc_auc(y_true.ravel(), values.ravel())
    top1 = topk_hit_rate(y_true, values, 1)
    top5 = topk_hit_rate(y_true, values, 5)
    return {
        "name": name,
        "min_support": min_support,
        "weight": weight,
        "macro_auc": "" if macro["mean_auc"] is None else f"{macro['mean_auc']:.8f}",
        "micro_auc": "" if micro is None else f"{micro:.8f}",
        "top1_hit": "" if top1 is None else f"{top1:.8f}",
        "top5_hit": "" if top5 is None else f"{top5:.8f}",
        "scored_classes": macro["scored_classes"],
        "corr_vs_anchor": f"{np.corrcoef(anchor.ravel(), values.ravel())[0, 1]:.8f}",
        "mad_vs_anchor": f"{np.mean(np.abs(anchor - values)):.8f}",
        "classes_mixed": len(selected_classes),
        "sources_used": ";".join(selected_sources),
        "selected_classes": ";".join(selected_classes),
    }


def build_router(
    anchor: np.ndarray,
    support: np.ndarray,
    support_gate: np.ndarray,
    anchor_auc: np.ndarray,
    side_auc: dict[str, np.ndarray],
    side_rankcal: dict[str, np.ndarray],
    class_names: list[str],
    min_support: int,
    weight: float,
) -> tuple[np.ndarray, list[dict[str, object]]]:
    mixed = anchor.copy()
    selected_rows: list[dict[str, object]] = []

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
        if delta <= 0.0:
            continue
        col_weight = weight * support_gate[idx]
        mixed[:, idx] = np.clip(
            (1.0 - col_weight) * anchor[:, idx] + col_weight * side_rankcal[source_name][:, idx],
            0.0,
            1.0,
        )
        selected_rows.append(
            {
                "class_name": class_name,
                "support": int(support[idx]),
                "source": source_name,
                "anchor_auc": f"{anchor_auc[idx]:.8f}",
                "side_auc": f"{best_auc:.8f}",
                "delta": f"{delta:.8f}",
            }
        )
    return mixed, selected_rows


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", type=Path, default=ROOT / "birdclef-2026/data")
    parser.add_argument(
        "--anchor",
        type=Path,
        default=ROOT / "birdclef-2026/outputs/v114-v110-v113-selfblend-v1/submission.csv",
    )
    parser.add_argument("--output-csv", type=Path, default=ROOT / "experiments/v126_router_robustness_probe.csv")
    parser.add_argument(
        "--selection-csv",
        type=Path,
        default=ROOT / "experiments/v126_router_robustness_selection.csv",
    )
    args = parser.parse_args()

    sample = pd.read_csv(args.data_dir / "sample_submission.csv", nrows=1)
    class_names = list(sample.columns[1:])
    labels = pd.read_csv(args.data_dir / "train_soundscapes_labels.csv")

    anchor_df = load_submission(args.anchor, class_names)
    side_frames = {name: load_submission(path, class_names) for name, path in SIDE_SOURCES.items()}
    row_ids = anchor_df["row_id"].astype(str).tolist()
    for name, df in side_frames.items():
        if df["row_id"].astype(str).tolist() != row_ids:
            raise ValueError(f"{name} row_id order mismatch")

    y_true = labels_to_targets(anchor_df[["row_id"]], labels, class_names)
    anchor = anchor_df[class_names].to_numpy(dtype=np.float64)
    side_values = {name: df[class_names].to_numpy(dtype=np.float64) for name, df in side_frames.items()}
    anchor_auc = per_class_auc(y_true, anchor, class_names)
    side_auc = {name: per_class_auc(y_true, values, class_names) for name, values in side_values.items()}
    side_rankcal = {name: rankcal_to_anchor(values, anchor) for name, values in side_values.items()}
    support = y_true.sum(axis=0).astype(np.float64)
    support_gate = np.clip(np.log1p(support) / np.log1p(max(1.0, float(support.max()))), 0.25, 1.0)

    rows: list[dict[str, object]] = []
    selections: list[dict[str, object]] = []
    rows.append(score_values("v114_anchor", anchor, y_true, class_names, anchor, [], [], 0, 0.0))

    for min_support in [1, 2, 5, 10, 15, 20, 25]:
        for weight in [0.35, 0.50, 0.70]:
            mixed, selected = build_router(
                anchor,
                support,
                support_gate,
                anchor_auc,
                side_auc,
                side_rankcal,
                class_names,
                min_support,
                weight,
            )
            selected_classes = [row["class_name"] for row in selected]
            selected_sources = sorted({str(row["source"]) for row in selected})
            name = f"v126_min{min_support}_w{weight:g}_rankcal"
            rows.append(
                score_values(
                    name,
                    mixed,
                    y_true,
                    class_names,
                    anchor,
                    selected_classes,
                    selected_sources,
                    min_support,
                    weight,
                )
            )
            for row in selected:
                selections.append({"candidate": name, "min_support": min_support, "weight": weight, **row})

    rows.sort(key=lambda r: float(r["macro_auc"] or -1), reverse=True)
    args.output_csv.parent.mkdir(parents=True, exist_ok=True)
    with args.output_csv.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    args.selection_csv.parent.mkdir(parents=True, exist_ok=True)
    with args.selection_csv.open("w", encoding="utf-8", newline="") as f:
        fieldnames = ["candidate", "min_support", "weight", "class_name", "support", "source", "anchor_auc", "side_auc", "delta"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(selections)

    print(f"wrote {args.output_csv} rows={len(rows)}")
    print(f"wrote {args.selection_csv} rows={len(selections)}")
    for row in rows[:10]:
        print(
            row["name"],
            row["macro_auc"],
            row["micro_auc"],
            row["top5_hit"],
            row["classes_mixed"],
            row["selected_classes"],
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
