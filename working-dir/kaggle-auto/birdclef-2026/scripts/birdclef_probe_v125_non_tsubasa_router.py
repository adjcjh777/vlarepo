#!/usr/bin/env python3
"""Probe a non-Tsubasa class router over clean side sources.

This is a local-only innovation probe. It does not mount prior outputs in a
candidate notebook and does not use Tsubasa branches. The goal is to test
whether clean CC0 side sources can be used as sparse class-level corrections
over the clean EcoProto anchors instead of copying or globally blending public
work.
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


def minmax01(values: np.ndarray) -> np.ndarray:
    lo = np.nanmin(values, axis=0, keepdims=True)
    hi = np.nanmax(values, axis=0, keepdims=True)
    return (values - lo) / (hi - lo + 1e-9)


def column_rank01(values: np.ndarray) -> np.ndarray:
    order = np.argsort(values, axis=0, kind="mergesort")
    ranks = np.empty_like(values, dtype=np.float64)
    col_idx = np.arange(values.shape[1])[None, :]
    rank_values = np.linspace(0.0, 1.0, values.shape[0], endpoint=True)[:, None]
    ranks[order, col_idx] = rank_values
    return ranks


def rankcal_to_anchor(side: np.ndarray, anchor: np.ndarray) -> np.ndarray:
    """Map side column ranks onto the anchor column value distribution."""
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
    formula: str,
    selected_sources: list[str],
    selected_classes: list[str],
) -> dict[str, object]:
    macro = multilabel_macro_auc(y_true, values, class_names)
    micro = binary_roc_auc(y_true.ravel(), values.ravel())
    top1 = topk_hit_rate(y_true, values, 1)
    top5 = topk_hit_rate(y_true, values, 5)
    corr = float(np.corrcoef(anchor.ravel(), values.ravel())[0, 1])
    mad = float(np.mean(np.abs(anchor - values)))
    return {
        "name": name,
        "formula": formula,
        "macro_auc": "" if macro["mean_auc"] is None else f"{macro['mean_auc']:.8f}",
        "micro_auc": "" if micro is None else f"{micro:.8f}",
        "top1_hit": "" if top1 is None else f"{top1:.8f}",
        "top5_hit": "" if top5 is None else f"{top5:.8f}",
        "scored_classes": macro["scored_classes"],
        "corr_vs_anchor": f"{corr:.8f}",
        "mad_vs_anchor": f"{mad:.8f}",
        "classes_mixed": len(selected_classes),
        "sources_used": ";".join(selected_sources),
        "selected_classes": ";".join(selected_classes[:40]),
        "min": f"{np.nanmin(values):.8f}",
        "max": f"{np.nanmax(values):.8f}",
        "mean": f"{np.nanmean(values):.8f}",
        "std": f"{np.nanstd(values):.8f}",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", type=Path, default=ROOT / "birdclef-2026/data")
    parser.add_argument(
        "--output-csv",
        type=Path,
        default=ROOT / "experiments/v125_non_tsubasa_router_probe.csv",
    )
    parser.add_argument(
        "--diagnostics-csv",
        type=Path,
        default=ROOT / "experiments/v125_non_tsubasa_router_class_diagnostics.csv",
    )
    args = parser.parse_args()

    sample = pd.read_csv(args.data_dir / "sample_submission.csv", nrows=1)
    class_names = list(sample.columns[1:])
    labels = pd.read_csv(args.data_dir / "train_soundscapes_labels.csv")

    sources = [
        SourceSpec(
            "v110_clean",
            ROOT / "birdclef-2026/outputs/v110-ecoproto-clean-blend-v1/submission.csv",
            "anchor",
        ),
        SourceSpec(
            "v114_clean_selfblend",
            ROOT / "birdclef-2026/outputs/v114-v110-v113-selfblend-v1/submission.csv",
            "anchor",
        ),
        SourceSpec(
            "v112_backtracking_remap",
            ROOT / "birdclef-2026/outputs/v112-clean-sed-remap-ecoproto-v1/submission.csv",
            "clean_side",
        ),
        SourceSpec(
            "v113_lantingguo_melnorm",
            ROOT / "birdclef-2026/outputs/v113-lantingguo-melnorm-ecoproto-v1/submission.csv",
            "clean_side",
        ),
        SourceSpec(
            "v119_roniheka_hgnet",
            ROOT / "birdclef-2026/outputs/v119-roniheka-hgnet-sed-v1/submission.csv",
            "clean_side",
        ),
    ]

    frames: dict[str, pd.DataFrame] = {}
    for source in sources:
        frames[source.name] = load_submission(source.path, class_names)

    base_ids = frames[sources[0].name]["row_id"].astype(str).tolist()
    for source in sources[1:]:
        row_ids = frames[source.name]["row_id"].astype(str).tolist()
        if row_ids != base_ids:
            raise ValueError(f"row_id mismatch for {source.name}")

    y_true = labels_to_targets(frames[sources[0].name][["row_id"]], labels, class_names)
    values = {
        source.name: frames[source.name][class_names].to_numpy(dtype=np.float64)
        for source in sources
    }

    anchors = [source for source in sources if source.role == "anchor"]
    sides = [source for source in sources if source.role == "clean_side"]

    aucs = {name: per_class_auc(y_true, pred, class_names) for name, pred in values.items()}
    support = y_true.sum(axis=0).astype(np.float64)
    support_gate = np.clip(np.log1p(support) / np.log1p(max(1.0, float(support.max()))), 0.25, 1.0)

    rows: list[dict[str, object]] = []
    diagnostics: list[dict[str, object]] = []
    for anchor_spec in anchors:
        anchor = values[anchor_spec.name]
        rows.append(
            score_values(
                anchor_spec.name,
                anchor,
                y_true,
                class_names,
                anchor,
                "baseline",
                [],
                [],
            )
        )
        anchor_auc = aucs[anchor_spec.name]
        side_arrays = {side.name: values[side.name] for side in sides}
        side_rankcal = {side.name: rankcal_to_anchor(values[side.name], anchor) for side in sides}
        side_rank = {side.name: column_rank01(values[side.name]) for side in sides}
        anchor_rank = column_rank01(anchor)

        best_side_name: list[str] = []
        best_side_auc = np.full(len(class_names), np.nan, dtype=np.float64)
        for idx, class_name in enumerate(class_names):
            scored = [
                (side.name, aucs[side.name][idx])
                for side in sides
                if np.isfinite(aucs[side.name][idx])
            ]
            if not scored:
                best_side_name.append("")
                continue
            source_name, source_auc = max(scored, key=lambda x: x[1])
            best_side_name.append(source_name)
            best_side_auc[idx] = source_auc
            diagnostics.append(
                {
                    "anchor": anchor_spec.name,
                    "class_name": class_name,
                    "support": int(support[idx]),
                    "anchor_auc": "" if not np.isfinite(anchor_auc[idx]) else f"{anchor_auc[idx]:.8f}",
                    "best_side": source_name,
                    "best_side_auc": f"{source_auc:.8f}",
                    "best_delta": ""
                    if not np.isfinite(anchor_auc[idx])
                    else f"{source_auc - anchor_auc[idx]:.8f}",
                }
            )

        for margin in [-0.04, -0.02, 0.0, 0.01, 0.02, 0.04, 0.08]:
            selected = np.isfinite(best_side_auc) & np.isfinite(anchor_auc) & ((best_side_auc - anchor_auc) > margin)
            selected_idx = np.where(selected)[0]
            if len(selected_idx) == 0:
                continue
            selected_classes = [class_names[i] for i in selected_idx]
            selected_sources = sorted({best_side_name[i] for i in selected_idx})
            for weight in [0.08, 0.12, 0.18, 0.25, 0.35, 0.50, 0.70]:
                for mode in ["prob", "rankcal", "rankcal_ranklead", "norm_residual"]:
                    mixed = anchor.copy()
                    for idx in selected_idx:
                        source_name = best_side_name[idx]
                        gate_strength = support_gate[idx]
                        if mode == "prob":
                            side_col = side_arrays[source_name][:, idx]
                            col_weight = weight * gate_strength
                        elif mode == "rankcal":
                            side_col = side_rankcal[source_name][:, idx]
                            col_weight = weight * gate_strength
                        elif mode == "rankcal_ranklead":
                            lead = side_rank[source_name][:, idx] > (anchor_rank[:, idx] + 0.05)
                            side_col = np.where(lead, side_rankcal[source_name][:, idx], anchor[:, idx])
                            col_weight = weight * gate_strength
                        else:
                            residual = minmax01(side_arrays[source_name])[:, idx] - minmax01(anchor)[:, idx]
                            side_col = np.clip(anchor[:, idx] + residual * np.std(anchor[:, idx]), 0.0, 1.0)
                            col_weight = weight * gate_strength
                        mixed[:, idx] = np.clip((1.0 - col_weight) * anchor[:, idx] + col_weight * side_col, 0.0, 1.0)

                    name = f"{anchor_spec.name}_router_m{margin:g}_w{weight:g}_{mode}"
                    formula = (
                        "per_class_best_non_tsubasa_side;"
                        f"margin={margin};weight={weight};mode={mode};support_shrink=log1p"
                    )
                    rows.append(
                        score_values(
                            name,
                            mixed,
                            y_true,
                            class_names,
                            anchor,
                            formula,
                            selected_sources,
                            selected_classes,
                        )
                    )

    rows.sort(key=lambda r: float(r["macro_auc"] or -1), reverse=True)
    args.output_csv.parent.mkdir(parents=True, exist_ok=True)
    with args.output_csv.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    args.diagnostics_csv.parent.mkdir(parents=True, exist_ok=True)
    with args.diagnostics_csv.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(diagnostics[0].keys()))
        writer.writeheader()
        writer.writerows(diagnostics)

    print(f"wrote {args.output_csv} rows={len(rows)}")
    print(f"wrote {args.diagnostics_csv} rows={len(diagnostics)}")
    for row in rows[:12]:
        print(
            row["name"],
            row["macro_auc"],
            row["micro_auc"],
            row["top5_hit"],
            row["corr_vs_anchor"],
            row["classes_mixed"],
            row["sources_used"],
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
