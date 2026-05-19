#!/usr/bin/env python3
"""Probe a stable3 clean rescue with v103-style guard rails.

This local-only probe combines:

- the stable3 clean component from v129/v130/v131;
- positive-only rescue on v112-backtracking-remap;
- a row-level top-hit preservation guard inspired by v103.

The goal is to see whether we can retain the stable3 top5-safe behavior while
adding a stronger anti-collapse screen than the previous clean-router family.
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


STABLE_CLASSES = ["47158son13", "47158son22", "47158son23"]


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


def calibrate_holdout_to_anchor(train_side: np.ndarray, train_anchor: np.ndarray, hold_side: np.ndarray) -> np.ndarray:
    calibrated = np.empty_like(hold_side, dtype=np.float64)
    n_train = train_side.shape[0]
    quant_x = np.linspace(0.0, 1.0, n_train)
    for col in range(train_side.shape[1]):
        side_sorted = np.sort(train_side[:, col])
        anchor_sorted = np.sort(train_anchor[:, col])
        pos = np.searchsorted(side_sorted, hold_side[:, col], side="right") - 1
        pct = np.clip(pos / max(1, n_train - 1), 0.0, 1.0)
        calibrated[:, col] = np.interp(pct, quant_x, anchor_sorted)
    return calibrated


def support_gate(y_true: np.ndarray, idxs: list[int]) -> dict[int, float]:
    support = y_true.sum(axis=0).astype(np.float64)
    denom = np.log1p(max(1.0, float(support.max())))
    return {idx: float(np.clip(np.log1p(support[idx]) / denom, 0.25, 1.0)) for idx in idxs}


def apply_guarded_rescue(
    anchor: np.ndarray,
    side: np.ndarray,
    idxs: list[int],
    gate: dict[int, float],
    weight: float,
    top1_threshold: float,
    top1_margin: float,
    top5_mode: bool,
) -> tuple[np.ndarray, int]:
    mixed = anchor.copy()
    top_order = np.argsort(anchor, axis=1)
    top1_idx = top_order[:, -1]
    top1_val = anchor[np.arange(anchor.shape[0]), top1_idx]
    top2_val = anchor[np.arange(anchor.shape[0]), top_order[:, -2]]
    confident_row = (top1_val >= top1_threshold) & ((top1_val - top2_val) >= top1_margin)
    top5_idx = np.argpartition(anchor, -5, axis=1)[:, -5:]
    active = 0
    for idx in idxs:
        candidate = np.clip((1.0 - weight * gate[idx]) * mixed[:, idx] + weight * gate[idx] * side[:, idx], 0.0, 1.0)
        positive = candidate > mixed[:, idx]
        preserve = confident_row & (top1_idx != idx)
        if top5_mode:
            mask = ((positive | (top5_idx == idx).any(axis=1)) & ~preserve)
        else:
            mask = positive & ~preserve
        mixed[mask, idx] = candidate[mask]
        active += int(mask.sum())
    return mixed, active


def score_values(name: str, y_true: np.ndarray, values: np.ndarray, class_names: list[str], anchor: np.ndarray, active_cells: int) -> dict[str, object]:
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
        "active_cells": active_cells,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", type=Path, default=ROOT / "birdclef-2026/data")
    parser.add_argument("--output-csv", type=Path, default=ROOT / "experiments/v134_stable3_guarded_rescue_probe.csv")
    args = parser.parse_args()

    sample = pd.read_csv(args.data_dir / "sample_submission.csv", nrows=1)
    class_names = list(sample.columns[1:])
    labels = pd.read_csv(args.data_dir / "train_soundscapes_labels.csv")

    anchor_paths = {
        "v110_clean": ROOT / "birdclef-2026/outputs/v110-ecoproto-clean-blend-v1/submission.csv",
        "v114_clean_selfblend": ROOT / "birdclef-2026/outputs/v114-v110-v113-selfblend-v1/submission.csv",
    }
    side_path = ROOT / "birdclef-2026/outputs/v112-clean-sed-remap-ecoproto-v1/submission.csv"

    anchor_frames = {name: load_submission(path, class_names) for name, path in anchor_paths.items()}
    side_df = load_submission(side_path, class_names)
    row_ids = next(iter(anchor_frames.values()))["row_id"].astype(str).tolist()
    for name, df in {**anchor_frames, "v112": side_df}.items():
        if df["row_id"].astype(str).tolist() != row_ids:
            raise ValueError(f"{name} row_id mismatch")

    y_true = labels_to_targets(side_df[["row_id"]], labels, class_names)
    groups = row_groups(side_df["row_id"])
    idxs = [class_names.index(c) for c in STABLE_CLASSES]
    gate = support_gate(y_true, idxs)
    side_values = side_df[class_names].to_numpy(dtype=np.float64)

    rows: list[dict[str, object]] = []
    for anchor_name, anchor_df in anchor_frames.items():
        anchor = anchor_df[class_names].to_numpy(dtype=np.float64)
        rows.append(
            {
                **score_values(f"{anchor_name}_baseline", y_true, anchor, class_names, anchor, 0),
                "anchor": anchor_name,
                "validation": "baseline",
                "weight": "",
                "top1_threshold": "",
                "top1_margin": "",
                "top5_mode": "",
            }
        )

        for weight in [0.5, 0.7, 0.9]:
            for top1_threshold in [0.7, 0.8, 0.9]:
                for top1_margin in [0.08, 0.12]:
                    for top5_mode in [False, True]:
                        oof = anchor.copy()
                        active = 0
                        for group in sorted(set(groups)):
                            hold = groups == group
                            train = ~hold
                            side_hold = calibrate_holdout_to_anchor(side_values[train], anchor[train], side_values[hold])
                            mixed_hold, fold_active = apply_guarded_rescue(
                                anchor[hold],
                                side_hold,
                                idxs,
                                gate,
                                weight,
                                top1_threshold,
                                top1_margin,
                                top5_mode,
                            )
                            oof[hold] = mixed_hold
                            active += fold_active
                        rows.append(
                            {
                                **score_values(
                                    f"v134_{anchor_name}_w{weight:g}_t{top1_threshold:g}_m{top1_margin:g}_top5{int(top5_mode)}",
                                    y_true,
                                    oof,
                                    class_names,
                                    anchor,
                                    active,
                                ),
                                "anchor": anchor_name,
                                "validation": "blocked",
                                "weight": weight,
                                "top1_threshold": top1_threshold,
                                "top1_margin": top1_margin,
                                "top5_mode": int(top5_mode),
                            }
                        )

    rows.sort(key=lambda r: (float(r["top5_hit"] or -1), float(r["macro_auc"] or -1), float(r["micro_auc"] or -1)), reverse=True)
    args.output_csv.parent.mkdir(parents=True, exist_ok=True)
    with args.output_csv.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    print(f"wrote {args.output_csv} rows={len(rows)}")
    for row in rows[:12]:
        print(
            row["name"],
            row["top5_hit"],
            row["macro_auc"],
            row["micro_auc"],
            row["active_cells"],
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
