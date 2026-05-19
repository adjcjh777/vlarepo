#!/usr/bin/env python3
"""Probe v118 EcoHabitat selective rescue formulas.

This is an original local-only probe. Public kernels inspected on 2026-05-19
suggested habitat/acoustic-context ideas, but their runnable artifacts were not
submission-safe. This script tests a lightweight, self-contained alternative:
class-selective v113 rescue over the clean v110 branch, gated by internal
per-class diagnostics and row-level prediction geometry.
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


def score_prediction(
    name: str,
    values: np.ndarray,
    y_true: np.ndarray,
    class_names: list[str],
    formula: str,
) -> dict[str, object]:
    macro = multilabel_macro_auc(y_true, values, class_names)
    micro = binary_roc_auc(y_true.ravel(), values.ravel())
    top1 = topk_hit_rate(y_true, values, 1)
    top5 = topk_hit_rate(y_true, values, 5)
    return {
        "name": name,
        "formula": formula,
        "rows": values.shape[0],
        "classes": values.shape[1],
        "target_positives": int(y_true.sum()),
        "scored_classes": macro["scored_classes"],
        "macro_auc": "" if macro["mean_auc"] is None else f"{macro['mean_auc']:.8f}",
        "micro_auc": "" if micro is None else f"{micro:.8f}",
        "top1_hit": "" if top1 is None else f"{top1:.8f}",
        "top5_hit": "" if top5 is None else f"{top5:.8f}",
        "min": f"{np.nanmin(values):.8f}",
        "max": f"{np.nanmax(values):.8f}",
        "mean": f"{np.nanmean(values):.8f}",
        "std": f"{np.nanstd(values):.8f}",
    }


def load_submission(path: Path, class_names: list[str]) -> pd.DataFrame:
    df = pd.read_csv(path)
    missing = [c for c in ["row_id", *class_names] if c not in df.columns]
    if missing:
        raise ValueError(f"{path} missing columns: {missing[:5]}")
    return df[["row_id", *class_names]].copy()


def normalized(values: np.ndarray) -> np.ndarray:
    lo = float(np.nanmin(values))
    hi = float(np.nanmax(values))
    return (values - lo) / (hi - lo + 1e-9)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--v110",
        type=Path,
        default=ROOT / "birdclef-2026/outputs/v110-ecoproto-clean-blend-v1/submission.csv",
    )
    parser.add_argument(
        "--v113",
        type=Path,
        default=ROOT / "birdclef-2026/outputs/v113-lantingguo-melnorm-ecoproto-v1/submission.csv",
    )
    parser.add_argument(
        "--v114",
        type=Path,
        default=ROOT / "birdclef-2026/outputs/v114-v110-v113-selfblend-v1/submission.csv",
    )
    parser.add_argument(
        "--branch-diag",
        type=Path,
        default=ROOT / "birdclef-2026/outputs/v114-v110-v113-selfblend-v1/v114_branch_auc_diagnostics.csv",
    )
    parser.add_argument("--data-dir", type=Path, default=ROOT / "birdclef-2026/data")
    parser.add_argument(
        "--output-csv",
        type=Path,
        default=ROOT / "experiments/v118_ecohabitat_selective_probe.csv",
    )
    args = parser.parse_args()

    sample = pd.read_csv(args.data_dir / "sample_submission.csv", nrows=1)
    class_names = list(sample.columns[1:])
    labels = pd.read_csv(args.data_dir / "train_soundscapes_labels.csv")

    v110 = load_submission(args.v110, class_names)
    v113 = load_submission(args.v113, class_names)
    v114 = load_submission(args.v114, class_names)
    row_ids = v110["row_id"].astype(str).tolist()
    if row_ids != v113["row_id"].astype(str).tolist() or row_ids != v114["row_id"].astype(str).tolist():
        raise ValueError("v110/v113/v114 row_id order mismatch")

    y_true = labels_to_targets(v110[["row_id"]], labels, class_names)
    p110 = v110[class_names].to_numpy(dtype=np.float64)
    p113 = v113[class_names].to_numpy(dtype=np.float64)
    p114 = v114[class_names].to_numpy(dtype=np.float64)

    diag = pd.read_csv(args.branch_diag).set_index("primary_label").loc[class_names]
    auc_delta = diag["sed_auc_delta"].to_numpy(dtype=np.float64)
    support = diag["support"].to_numpy(dtype=np.float64)
    support_gate = np.clip(np.log1p(support) / np.log1p(max(1.0, float(support.max()))), 0.25, 1.0)

    entropy = -(
        p110 * np.log(np.clip(p110, 1e-8, 1.0))
        + (1.0 - p110) * np.log(np.clip(1.0 - p110, 1e-8, 1.0))
    ).mean(axis=1)
    disagreement = np.abs(p113 - p110).mean(axis=1)
    eco_gate = 0.65 * normalized(entropy) + 0.35 * normalized(disagreement)

    row_gates = {
        "flat": np.ones(len(p110)),
        "entropy": normalized(entropy),
        "diff": normalized(disagreement),
        "eco": eco_gate,
        "inv_eco": 1.0 - eco_gate,
    }

    rows: list[dict[str, object]] = [
        score_prediction("v110", p110, y_true, class_names, "baseline"),
        score_prediction("v113", p113, y_true, class_names, "baseline"),
        score_prediction("v114", p114, y_true, class_names, "0.85*v110+0.15*v113"),
    ]

    for threshold in [-0.05, 0.0, 0.01, 0.02, 0.04, 0.08]:
        for slope in [0.04, 0.08, 0.12, 0.20]:
            class_gate = np.clip((auc_delta - threshold) / slope, 0.0, 1.0) * support_gate
            for row_gate_name, row_gate in row_gates.items():
                for alpha in [0.10, 0.15, 0.20, 0.25, 0.30, 0.40, 0.55, 0.75, 1.00]:
                    values = np.clip(
                        p110 + alpha * row_gate[:, None] * class_gate[None, :] * (p113 - p110),
                        0.0,
                        1.0,
                    )
                    name = f"th{threshold:g}_sl{slope:g}_{row_gate_name}_a{alpha:g}"
                    formula = (
                        "clip(v110 + alpha*row_gate*support_gate*"
                        "clip((auc_delta-threshold)/slope,0,1)*(v113-v110))"
                    )
                    rows.append(score_prediction(name, values, y_true, class_names, formula))

    rows.sort(key=lambda r: float(r["macro_auc"] or -1), reverse=True)
    args.output_csv.parent.mkdir(parents=True, exist_ok=True)
    with args.output_csv.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    print(f"wrote {args.output_csv} rows={len(rows)}")
    for row in rows[:10]:
        print(row["name"], row["macro_auc"], row["micro_auc"], row["top5_hit"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
