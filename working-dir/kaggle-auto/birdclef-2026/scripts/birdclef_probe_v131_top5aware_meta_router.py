#!/usr/bin/env python3
"""Top5-aware grouped meta-router probe over clean side sources.

This local-only probe continues the original clean-router lane while v127 is
still pending. Instead of testing one fixed router, it searches for a small set
of class-source interventions under leave-one-soundscape-out validation and
optimizes a lexicographic objective:

1. preserve or improve blocked top5 hit rate
2. then improve blocked macro AUC
3. then improve blocked micro AUC

The result is evidence for whether a compact top5-aware grouped router is worth
materializing after v127 resolves.
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
class Candidate:
    class_name: str
    class_idx: int
    source_name: str
    weight: float
    mode: str
    mean_delta: float
    mean_support: float


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


def support_gate(support: np.ndarray, idx: int) -> float:
    denom = np.log1p(max(1.0, float(support.max())))
    return float(np.clip(np.log1p(support[idx]) / denom, 0.25, 1.0))


def score_tuple(y_true: np.ndarray, values: np.ndarray, class_names: list[str]) -> tuple[float, float, float, float]:
    macro = multilabel_macro_auc(y_true, values, class_names)
    micro = binary_roc_auc(y_true.ravel(), values.ravel())
    top5 = topk_hit_rate(y_true, values, 5)
    top1 = topk_hit_rate(y_true, values, 1)
    return (
        -1.0 if top5 is None else float(top5),
        -1.0 if macro["mean_auc"] is None else float(macro["mean_auc"]),
        -1.0 if micro is None else float(micro),
        -1.0 if top1 is None else float(top1),
    )


def score_dict(name: str, y_true: np.ndarray, values: np.ndarray, class_names: list[str], anchor: np.ndarray) -> dict[str, object]:
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


def apply_candidates(
    anchor: np.ndarray,
    side_cal: dict[str, np.ndarray],
    support: np.ndarray,
    candidates: list[Candidate],
) -> tuple[np.ndarray, int]:
    mixed = anchor.copy()
    top5_idx = np.argpartition(anchor, -5, axis=1)[:, -5:]
    active_cells = 0
    for cand in candidates:
        idx = cand.class_idx
        col_weight = cand.weight * support_gate(support, idx)
        candidate_col = np.clip(
            (1.0 - col_weight) * mixed[:, idx] + col_weight * side_cal[cand.source_name][:, idx],
            0.0,
            1.0,
        )
        if cand.mode == "positive":
            mask = candidate_col > mixed[:, idx]
        elif cand.mode == "top5_or_positive":
            mask = (candidate_col > mixed[:, idx]) | (top5_idx == idx).any(axis=1)
        else:
            raise ValueError(f"unknown mode {cand.mode}")
        mixed[mask, idx] = candidate_col[mask]
        active_cells += int(mask.sum())
    return mixed, active_cells


def make_candidates(
    y_true: np.ndarray,
    anchor: np.ndarray,
    side_values: dict[str, np.ndarray],
    class_names: list[str],
    min_support: int,
    min_delta: float,
) -> list[Candidate]:
    anchor_auc = per_class_auc(y_true, anchor)
    support = y_true.sum(axis=0).astype(np.float64)
    side_auc = {name: per_class_auc(y_true, values) for name, values in side_values.items()}
    candidates: list[Candidate] = []
    for idx, class_name in enumerate(class_names):
        if support[idx] < min_support or not np.isfinite(anchor_auc[idx]):
            continue
        for source_name, aucs in side_auc.items():
            if not np.isfinite(aucs[idx]):
                continue
            delta = float(aucs[idx] - anchor_auc[idx])
            if delta < min_delta:
                continue
            for weight in [0.35, 0.50, 0.70]:
                for mode in ["positive", "top5_or_positive"]:
                    candidates.append(
                        Candidate(
                            class_name=class_name,
                            class_idx=idx,
                            source_name=source_name,
                            weight=weight,
                            mode=mode,
                            mean_delta=delta,
                            mean_support=float(support[idx]),
                        )
                    )
    candidates.sort(key=lambda c: (c.mean_delta, c.mean_support), reverse=True)
    return candidates


def blocked_oof(
    base_anchor: np.ndarray,
    side_values: dict[str, np.ndarray],
    groups: np.ndarray,
    support: np.ndarray,
    selected: list[Candidate],
) -> tuple[np.ndarray, int]:
    oof = base_anchor.copy()
    active_cells = 0
    for group in sorted(set(groups)):
        hold = groups == group
        train = ~hold
        side_cal = {
            name: calibrate_holdout_to_anchor(values[train], base_anchor[train], values[hold])
            for name, values in side_values.items()
        }
        mixed_hold, active = apply_candidates(base_anchor[hold], side_cal, support, selected)
        oof[hold] = mixed_hold
        active_cells += active
    return oof, active_cells


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", type=Path, default=ROOT / "birdclef-2026/data")
    parser.add_argument("--output-csv", type=Path, default=ROOT / "experiments/v131_top5aware_meta_router_probe.csv")
    parser.add_argument("--selection-csv", type=Path, default=ROOT / "experiments/v131_top5aware_meta_router_selection.csv")
    args = parser.parse_args()

    sample = pd.read_csv(args.data_dir / "sample_submission.csv", nrows=1)
    class_names = list(sample.columns[1:])
    labels = pd.read_csv(args.data_dir / "train_soundscapes_labels.csv")

    anchors = {
        "v110_clean": ROOT / "birdclef-2026/outputs/v110-ecoproto-clean-blend-v1/submission.csv",
        "v114_clean_selfblend": ROOT / "birdclef-2026/outputs/v114-v110-v113-selfblend-v1/submission.csv",
    }
    side_paths = {
        "v112_backtracking_remap": ROOT / "birdclef-2026/outputs/v112-clean-sed-remap-ecoproto-v1/submission.csv",
        "v113_lantingguo_melnorm": ROOT / "birdclef-2026/outputs/v113-lantingguo-melnorm-ecoproto-v1/submission.csv",
        "v119_roniheka_hgnet": ROOT / "birdclef-2026/outputs/v119-roniheka-hgnet-sed-v1/submission.csv",
    }

    anchor_frames = {name: load_submission(path, class_names) for name, path in anchors.items()}
    side_frames = {name: load_submission(path, class_names) for name, path in side_paths.items()}
    row_ids = next(iter(anchor_frames.values()))["row_id"].astype(str).tolist()
    for name, df in {**anchor_frames, **side_frames}.items():
        if df["row_id"].astype(str).tolist() != row_ids:
            raise ValueError(f"{name} row_id mismatch")

    y_true = labels_to_targets(next(iter(anchor_frames.values()))[["row_id"]], labels, class_names)
    groups = row_groups(next(iter(anchor_frames.values()))["row_id"])
    support = y_true.sum(axis=0).astype(np.float64)
    side_values = {name: df[class_names].to_numpy(dtype=np.float64) for name, df in side_frames.items()}

    rows: list[dict[str, object]] = []
    selections: list[dict[str, object]] = []

    for anchor_name, anchor_df in anchor_frames.items():
        anchor = anchor_df[class_names].to_numpy(dtype=np.float64)
        base_score = score_tuple(y_true, anchor, class_names)
        rows.append(
            {
                **score_dict(f"{anchor_name}_baseline", y_true, anchor, class_names, anchor),
                "anchor": anchor_name,
                "selected_count": 0,
                "active_cells": 0,
                "objective_top5": f"{base_score[0]:.8f}",
                "objective_macro": f"{base_score[1]:.8f}",
                "objective_micro": f"{base_score[2]:.8f}",
            }
        )

        candidates = make_candidates(y_true, anchor, side_values, class_names, min_support=10, min_delta=0.002)
        selected: list[Candidate] = []
        best_values = anchor.copy()
        best_score = base_score
        best_active = 0

        # Greedy forward selection under blocked validation.
        for step in range(5):
            trial_best = None
            trial_best_values = None
            trial_best_active = None
            used_keys = {(c.class_name, c.source_name, c.weight, c.mode) for c in selected}
            used_classes = {c.class_name for c in selected}
            for cand in candidates:
                key = (cand.class_name, cand.source_name, cand.weight, cand.mode)
                if key in used_keys or cand.class_name in used_classes:
                    continue
                trial = selected + [cand]
                oof, active = blocked_oof(anchor, side_values, groups, support, trial)
                score = score_tuple(y_true, oof, class_names)
                if score[0] + 1e-12 < base_score[0]:
                    continue
                if score > best_score and (trial_best is None or score > trial_best[1]):
                    trial_best = (cand, score)
                    trial_best_values = oof
                    trial_best_active = active
            if trial_best is None:
                break
            cand, score = trial_best
            selected.append(cand)
            best_score = score
            best_values = trial_best_values
            best_active = trial_best_active

            rows.append(
                {
                    **score_dict(
                        f"v131_{anchor_name}_step{step+1}_{cand.class_name}_{cand.source_name}_{cand.mode}_w{cand.weight:g}",
                        y_true,
                        best_values,
                        class_names,
                        anchor,
                    ),
                    "anchor": anchor_name,
                    "selected_count": len(selected),
                    "active_cells": best_active,
                    "objective_top5": f"{best_score[0]:.8f}",
                    "objective_macro": f"{best_score[1]:.8f}",
                    "objective_micro": f"{best_score[2]:.8f}",
                }
            )
            selections.append(
                {
                    "anchor": anchor_name,
                    "step": step + 1,
                    "class_name": cand.class_name,
                    "source_name": cand.source_name,
                    "weight": cand.weight,
                    "mode": cand.mode,
                    "mean_delta": f"{cand.mean_delta:.8f}",
                    "mean_support": f"{cand.mean_support:.1f}",
                    "objective_top5": f"{best_score[0]:.8f}",
                    "objective_macro": f"{best_score[1]:.8f}",
                    "objective_micro": f"{best_score[2]:.8f}",
                }
            )

    args.output_csv.parent.mkdir(parents=True, exist_ok=True)
    with args.output_csv.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    args.selection_csv.parent.mkdir(parents=True, exist_ok=True)
    with args.selection_csv.open("w", encoding="utf-8", newline="") as f:
        fieldnames = [
            "anchor",
            "step",
            "class_name",
            "source_name",
            "weight",
            "mode",
            "mean_delta",
            "mean_support",
            "objective_top5",
            "objective_macro",
            "objective_micro",
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(selections)

    print(f"wrote {args.output_csv} rows={len(rows)}")
    print(f"wrote {args.selection_csv} rows={len(selections)}")
    for row in rows[:15]:
        print(
            row["name"],
            row["objective_top5"],
            row["objective_macro"],
            row["objective_micro"],
            row["selected_count"],
            row["active_cells"],
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
