#!/usr/bin/env python3
"""Probe a license-clean transfer of the v103 guard/rescue idea.

v103/v102 remain strong local evidence, but they are not clean prize-route
candidates because some runtime dependencies have unknown license metadata.
This probe transfers the mechanism, not the artifact: it uses only clean local
branch outputs as lightweight stand-ins for in-notebook evidence, then applies
row confidence preservation, positive-evidence rescue gates, support floors, and
rank calibration over a clean EcoProto anchor.

This script is local-only and never submits to Kaggle.
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


def column_rank01(values: np.ndarray) -> np.ndarray:
    order = np.argsort(values, axis=0, kind="mergesort")
    ranks = np.empty_like(values, dtype=np.float64)
    col_idx = np.arange(values.shape[1])[None, :]
    rank_values = np.linspace(0.0, 1.0, values.shape[0], endpoint=True)[:, None]
    ranks[order, col_idx] = rank_values
    return ranks


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
    v103_ref: np.ndarray | None,
    config: dict[str, object],
    selected: list[dict[str, object]],
    active_cells: int,
) -> dict[str, object]:
    macro = multilabel_macro_auc(y_true, values, class_names)
    micro = binary_roc_auc(y_true.ravel(), values.ravel())
    top1 = topk_hit_rate(y_true, values, 1)
    top5 = topk_hit_rate(y_true, values, 5)
    corr_anchor = float(np.corrcoef(anchor.ravel(), values.ravel())[0, 1])
    corr_v103 = "" if v103_ref is None else f"{float(np.corrcoef(v103_ref.ravel(), values.ravel())[0, 1]):.8f}"
    return {
        "name": name,
        "anchor": config.get("anchor", ""),
        "min_support": config.get("min_support", ""),
        "min_delta": config.get("min_delta", ""),
        "weight": config.get("weight", ""),
        "rank_margin": config.get("rank_margin", ""),
        "top1_threshold": config.get("top1_threshold", ""),
        "top1_margin": config.get("top1_margin", ""),
        "macro_auc": "" if macro["mean_auc"] is None else f"{macro['mean_auc']:.8f}",
        "micro_auc": "" if micro is None else f"{micro:.8f}",
        "top1_hit": "" if top1 is None else f"{top1:.8f}",
        "top5_hit": "" if top5 is None else f"{top5:.8f}",
        "scored_classes": macro["scored_classes"],
        "corr_vs_anchor": f"{corr_anchor:.8f}",
        "mad_vs_anchor": f"{float(np.mean(np.abs(anchor - values))):.8f}",
        "corr_vs_v103_diagnostic": corr_v103,
        "classes_mixed": len({str(row["class_name"]) for row in selected}),
        "active_cells": active_cells,
        "sources_used": ";".join(sorted({str(row["source"]) for row in selected})),
        "selected_classes": ";".join(str(row["class_name"]) for row in selected[:80]),
        "min": f"{float(np.nanmin(values)):.8f}",
        "max": f"{float(np.nanmax(values)):.8f}",
    }


def build_clean_rescue(
    anchor: np.ndarray,
    anchor_rank: np.ndarray,
    support: np.ndarray,
    support_gate: np.ndarray,
    anchor_auc: np.ndarray,
    side_auc: dict[str, np.ndarray],
    side_rank: dict[str, np.ndarray],
    side_rankcal: dict[str, np.ndarray],
    class_names: list[str],
    min_support: int,
    min_delta: float,
    weight: float,
    rank_margin: float,
    top1_threshold: float,
    top1_margin: float,
) -> tuple[np.ndarray, list[dict[str, object]], int]:
    mixed = anchor.copy()
    top_order = np.argsort(anchor, axis=1)
    top1_idx = top_order[:, -1]
    top1_val = anchor[np.arange(anchor.shape[0]), top1_idx]
    top2_val = anchor[np.arange(anchor.shape[0]), top_order[:, -2]]
    confident_row = (top1_val >= top1_threshold) & ((top1_val - top2_val) >= top1_margin)

    selected: list[dict[str, object]] = []
    active_cells = 0

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

        side_col = side_rankcal[source_name][:, idx]
        positive = side_col > anchor[:, idx]
        rank_evidence = side_rank[source_name][:, idx] > (anchor_rank[:, idx] + rank_margin)

        # Preserve confident anchor winners by only allowing the winner class to
        # move in those rows. Non-winner rescue is still allowed in uncertain rows.
        preserve = confident_row & (top1_idx != idx)
        mask = positive & rank_evidence & ~preserve
        if not mask.any():
            continue

        col_weight = weight * support_gate[idx]
        mixed[mask, idx] = np.clip(
            anchor[mask, idx] + col_weight * (side_col[mask] - anchor[mask, idx]),
            0.0,
            1.0,
        )
        cells = int(mask.sum())
        active_cells += cells
        selected.append(
            {
                "class_name": class_name,
                "support": int(support[idx]),
                "source": source_name,
                "anchor_auc": f"{anchor_auc[idx]:.8f}",
                "side_auc": f"{best_auc:.8f}",
                "delta": f"{delta:.8f}",
                "active_cells": cells,
            }
        )

    return mixed, selected, active_cells


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", type=Path, default=ROOT / "birdclef-2026/data")
    parser.add_argument("--output-csv", type=Path, default=ROOT / "experiments/v128_clean_rescue_transfer_probe.csv")
    parser.add_argument(
        "--selection-csv",
        type=Path,
        default=ROOT / "experiments/v128_clean_rescue_transfer_selection.csv",
    )
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
        SourceSpec("v103_diagnostic_only", ROOT / "birdclef-2026/outputs/v103-guarded-macro-risk-rescue-v1/submission.csv", "diagnostic"),
    ]

    frames = {source.name: load_submission(source.path, class_names) for source in sources}
    row_ids = frames[sources[0].name]["row_id"].astype(str).tolist()
    for source in sources[1:]:
        if frames[source.name]["row_id"].astype(str).tolist() != row_ids:
            raise ValueError(f"{source.name} row_id order mismatch")

    y_true = labels_to_targets(frames[sources[0].name][["row_id"]], labels, class_names)
    values = {name: df[class_names].to_numpy(dtype=np.float64) for name, df in frames.items()}
    support = y_true.sum(axis=0).astype(np.float64)
    support_gate = np.clip(np.log1p(support) / np.log1p(max(1.0, float(support.max()))), 0.25, 1.0)

    rows: list[dict[str, object]] = []
    selections: list[dict[str, object]] = []
    anchors = [source for source in sources if source.role == "anchor"]
    sides = [source for source in sources if source.role == "clean_side"]
    v103_ref = values.get("v103_diagnostic_only")

    for anchor_spec in anchors:
        anchor = values[anchor_spec.name]
        anchor_rank = column_rank01(anchor)
        anchor_auc = per_class_auc(y_true, anchor, class_names)
        side_auc = {side.name: per_class_auc(y_true, values[side.name], class_names) for side in sides}
        side_rank = {side.name: column_rank01(values[side.name]) for side in sides}
        side_rankcal = {side.name: rankcal_to_anchor(values[side.name], anchor) for side in sides}

        rows.append(
            score_values(
                f"{anchor_spec.name}_baseline",
                anchor,
                y_true,
                class_names,
                anchor,
                v103_ref,
                {"anchor": anchor_spec.name},
                [],
                0,
            )
        )

        for min_support in [5, 10, 15, 20]:
            for min_delta in [0.0, 0.005, 0.01, 0.02]:
                for weight in [0.35, 0.50, 0.70, 0.90]:
                    for rank_margin in [0.0, 0.05, 0.10]:
                        for top1_threshold in [0.70, 0.80, 0.90]:
                            config = {
                                "anchor": anchor_spec.name,
                                "min_support": min_support,
                                "min_delta": min_delta,
                                "weight": weight,
                                "rank_margin": rank_margin,
                                "top1_threshold": top1_threshold,
                                "top1_margin": 0.08,
                            }
                            mixed, selected, active_cells = build_clean_rescue(
                                anchor,
                                anchor_rank,
                                support,
                                support_gate,
                                anchor_auc,
                                side_auc,
                                side_rank,
                                side_rankcal,
                                class_names,
                                min_support,
                                min_delta,
                                weight,
                                rank_margin,
                                top1_threshold,
                                0.08,
                            )
                            name = (
                                f"v128_{anchor_spec.name}_min{min_support}_d{min_delta:g}"
                                f"_w{weight:g}_rm{rank_margin:g}_t{top1_threshold:g}"
                            )
                            rows.append(score_values(name, mixed, y_true, class_names, anchor, v103_ref, config, selected, active_cells))
                            for row in selected:
                                selections.append({"candidate": name, **config, **row})

    rows.sort(key=lambda r: (float(r["macro_auc"] or -1), float(r["top5_hit"] or -1)), reverse=True)
    args.output_csv.parent.mkdir(parents=True, exist_ok=True)
    with args.output_csv.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    args.selection_csv.parent.mkdir(parents=True, exist_ok=True)
    with args.selection_csv.open("w", encoding="utf-8", newline="") as f:
        fieldnames = [
            "candidate",
            "anchor",
            "min_support",
            "min_delta",
            "weight",
            "rank_margin",
            "top1_threshold",
            "top1_margin",
            "class_name",
            "support",
            "source",
            "anchor_auc",
            "side_auc",
            "delta",
            "active_cells",
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(selections)

    print(f"wrote {args.output_csv} rows={len(rows)}")
    print(f"wrote {args.selection_csv} rows={len(selections)}")
    for row in rows[:12]:
        print(
            row["name"],
            row["macro_auc"],
            row["micro_auc"],
            row["top5_hit"],
            row["classes_mixed"],
            row["active_cells"],
            row["corr_vs_anchor"],
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
