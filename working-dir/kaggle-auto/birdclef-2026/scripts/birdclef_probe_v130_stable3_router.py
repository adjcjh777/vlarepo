#!/usr/bin/env python3
"""Probe a narrow stable-3 clean router from v129 evidence.

v129 showed that three classes survive leave-one-soundscape-out selection across
all folds: 47158son13, 47158son22, and 47158son23, all using the clean
v112/backtracking side source. This probe tests whether that small, stable
pattern is a better materialization target than broad same-row routers.

The probe is local-only and never submits to Kaggle.
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


def rankcal_to_anchor(side: np.ndarray, anchor: np.ndarray) -> np.ndarray:
    calibrated = np.empty_like(side, dtype=np.float64)
    side_order = np.argsort(side, axis=0, kind="mergesort")
    anchor_sorted = np.sort(anchor, axis=0)
    col_idx = np.arange(side.shape[1])
    calibrated[side_order, col_idx] = anchor_sorted
    return calibrated


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


def support_gate(y_true: np.ndarray, class_indices: list[int]) -> dict[int, float]:
    support = y_true.sum(axis=0).astype(np.float64)
    denom = np.log1p(max(1.0, float(support.max())))
    return {
        idx: float(np.clip(np.log1p(support[idx]) / denom, 0.25, 1.0))
        for idx in class_indices
    }


def apply_router(
    anchor: np.ndarray,
    side_cal: np.ndarray,
    class_indices: list[int],
    gate: dict[int, float],
    weight: float,
    mode: str,
) -> tuple[np.ndarray, int]:
    mixed = anchor.copy()
    top5_idx = np.argpartition(anchor, -5, axis=1)[:, -5:]
    active = 0
    for idx in class_indices:
        col_weight = weight * gate[idx]
        candidate = np.clip((1.0 - col_weight) * anchor[:, idx] + col_weight * side_cal[:, idx], 0.0, 1.0)
        if mode == "full":
            mask = np.ones(anchor.shape[0], dtype=bool)
        elif mode == "positive":
            mask = candidate > anchor[:, idx]
        elif mode == "top5_or_positive":
            mask = (candidate > anchor[:, idx]) | (top5_idx == idx).any(axis=1)
        else:
            raise ValueError(f"unknown mode {mode}")
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
        "min": f"{float(np.nanmin(values)):.8f}",
        "max": f"{float(np.nanmax(values)):.8f}",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", type=Path, default=ROOT / "birdclef-2026/data")
    parser.add_argument("--output-csv", type=Path, default=ROOT / "experiments/v130_stable3_router_probe.csv")
    args = parser.parse_args()

    sample = pd.read_csv(args.data_dir / "sample_submission.csv", nrows=1)
    class_names = list(sample.columns[1:])
    labels = pd.read_csv(args.data_dir / "train_soundscapes_labels.csv")

    anchors = {
        "v110_clean": ROOT / "birdclef-2026/outputs/v110-ecoproto-clean-blend-v1/submission.csv",
        "v114_clean_selfblend": ROOT / "birdclef-2026/outputs/v114-v110-v113-selfblend-v1/submission.csv",
    }
    side_path = ROOT / "birdclef-2026/outputs/v112-clean-sed-remap-ecoproto-v1/submission.csv"

    anchor_frames = {name: load_submission(path, class_names) for name, path in anchors.items()}
    side_df = load_submission(side_path, class_names)
    row_ids = next(iter(anchor_frames.values()))["row_id"].astype(str).tolist()
    for name, df in {**anchor_frames, "v112_backtracking_remap": side_df}.items():
        if df["row_id"].astype(str).tolist() != row_ids:
            raise ValueError(f"{name} row_id mismatch")

    y_true = labels_to_targets(side_df[["row_id"]], labels, class_names)
    groups = row_groups(side_df["row_id"])
    unique_groups = sorted(set(groups))
    side = side_df[class_names].to_numpy(dtype=np.float64)
    class_indices = [class_names.index(c) for c in STABLE_CLASSES]
    gate = support_gate(y_true, class_indices)

    rows: list[dict[str, object]] = []
    for anchor_name, anchor_df in anchor_frames.items():
        anchor = anchor_df[class_names].to_numpy(dtype=np.float64)
        rows.append(
            {
                **score_values(f"{anchor_name}_baseline", y_true, anchor, class_names, anchor, 0),
                "anchor": anchor_name,
                "validation": "baseline",
                "mode": "",
                "weight": "",
                "classes": ";".join(STABLE_CLASSES),
            }
        )

        side_same = rankcal_to_anchor(side, anchor)
        for weight in [0.20, 0.35, 0.50, 0.70, 0.90]:
            for mode in ["full", "positive", "top5_or_positive"]:
                same_values, same_active = apply_router(anchor, side_same, class_indices, gate, weight, mode)
                rows.append(
                    {
                        **score_values(
                            f"v130_{anchor_name}_same_{mode}_w{weight:g}",
                            y_true,
                            same_values,
                            class_names,
                            anchor,
                            same_active,
                        ),
                        "anchor": anchor_name,
                        "validation": "same_row",
                        "mode": mode,
                        "weight": weight,
                        "classes": ";".join(STABLE_CLASSES),
                    }
                )

                oof = anchor.copy()
                active_total = 0
                for group in unique_groups:
                    hold = groups == group
                    train = ~hold
                    side_hold = calibrate_holdout_to_anchor(side[train], anchor[train], side[hold])
                    mixed_hold, active = apply_router(anchor[hold], side_hold, class_indices, gate, weight, mode)
                    oof[hold] = mixed_hold
                    active_total += active
                rows.append(
                    {
                        **score_values(
                            f"v130_{anchor_name}_blocked_{mode}_w{weight:g}",
                            y_true,
                            oof,
                            class_names,
                            anchor,
                            active_total,
                        ),
                        "anchor": anchor_name,
                        "validation": "blocked",
                        "mode": mode,
                        "weight": weight,
                        "classes": ";".join(STABLE_CLASSES),
                    }
                )

    rows.sort(key=lambda r: (float(r["macro_auc"] or -1), float(r["top5_hit"] or -1)), reverse=True)
    args.output_csv.parent.mkdir(parents=True, exist_ok=True)
    with args.output_csv.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    print(f"wrote {args.output_csv} rows={len(rows)}")
    for row in rows[:12]:
        print(
            row["name"],
            row["validation"],
            row["mode"],
            row["weight"],
            row["macro_auc"],
            row["micro_auc"],
            row["top5_hit"],
            row["active_cells"],
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
