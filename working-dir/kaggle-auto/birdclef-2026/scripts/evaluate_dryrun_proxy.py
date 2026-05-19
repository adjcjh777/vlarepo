#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]

import sys

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
        labs = {x for x in str(row.primary_label).split(";") if x}
        label_map[key] = labs

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


def rank_matrix(values: np.ndarray) -> np.ndarray:
    order = np.argsort(values, axis=1)
    ranks = np.empty_like(values, dtype=np.float64)
    row_idx = np.arange(values.shape[0])[:, None]
    ranks[row_idx, order] = np.linspace(0.0, 1.0, values.shape[1], endpoint=True)
    return ranks


def load_prediction(path: Path, class_names: list[str]) -> pd.DataFrame:
    df = pd.read_csv(path)
    if "row_id" not in df.columns:
        raise ValueError(f"{path} missing row_id")
    missing = [c for c in class_names if c not in df.columns]
    if missing:
        raise ValueError(f"{path} missing {len(missing)} class columns")
    return df[["row_id"] + class_names].copy()


def score_prediction(name: str, df: pd.DataFrame, y_true: np.ndarray, class_names: list[str], source: str) -> dict[str, object]:
    values = df[class_names].to_numpy(dtype=np.float64)
    macro = multilabel_macro_auc(y_true, values, class_names)
    micro = binary_roc_auc(y_true.ravel(), values.ravel())
    return {
        "name": name,
        "source": source,
        "rows": len(df),
        "classes": len(class_names),
        "target_positives": int(y_true.sum()),
        "scored_classes": macro["scored_classes"],
        "macro_auc": "" if macro["mean_auc"] is None else f"{macro['mean_auc']:.8f}",
        "micro_auc": "" if micro is None else f"{micro:.8f}",
        "top1_hit": "" if topk_hit_rate(y_true, values, 1) is None else f"{topk_hit_rate(y_true, values, 1):.8f}",
        "top5_hit": "" if topk_hit_rate(y_true, values, 5) is None else f"{topk_hit_rate(y_true, values, 5):.8f}",
        "min": f"{np.nanmin(values):.8f}",
        "max": f"{np.nanmax(values):.8f}",
        "mean": f"{np.nanmean(values):.8f}",
        "std": f"{np.nanstd(values):.8f}",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pred-dir", required=True, type=Path)
    parser.add_argument("--output-csv", required=True, type=Path)
    parser.add_argument("--pattern", default="submission*.csv")
    parser.add_argument("--data-dir", type=Path, default=ROOT / "birdclef-2026" / "data")
    args = parser.parse_args()

    sample = pd.read_csv(args.data_dir / "sample_submission.csv", nrows=1)
    class_names = list(sample.columns[1:])
    labels = pd.read_csv(args.data_dir / "train_soundscapes_labels.csv")

    preds: dict[str, pd.DataFrame] = {}
    for path in sorted(args.pred_dir.glob(args.pattern)):
        try:
            df = load_prediction(path, class_names)
        except Exception as exc:
            print(f"skip {path.name}: {exc}")
            continue
        if len(df) < 10:
            continue
        y_true = labels_to_targets(df[["row_id"]], labels, class_names)
        if y_true.sum() == 0:
            continue
        preds[path.stem] = df

    if not preds:
        raise SystemExit("no scoreable prediction files found")

    rows: list[dict[str, object]] = []
    first_key = next(iter(preds))
    base_row_ids = preds[first_key]["row_id"].astype(str).tolist()
    for name, df in preds.items():
        y_true = labels_to_targets(df[["row_id"]], labels, class_names)
        rows.append(score_prediction(name, df, y_true, class_names, str(args.pred_dir / f"{name}.csv")))

    aligned = {
        name: df
        for name, df in preds.items()
        if df["row_id"].astype(str).tolist() == base_row_ids
    }
    if {"submission_protossm", "submission_sed", "submission_nfnet"}.issubset(aligned):
        p = aligned["submission_protossm"][class_names].to_numpy(dtype=np.float64)
        s = aligned["submission_sed"][class_names].to_numpy(dtype=np.float64)
        n = aligned["submission_nfnet"][class_names].to_numpy(dtype=np.float64)
        y_true = labels_to_targets(aligned["submission_protossm"][["row_id"]], labels, class_names)
        for w in [0.01, 0.03, 0.05, 0.08, 0.10, 0.15]:
            blend = (0.60 - w / 2) * rank_matrix(p) + 0.40 * rank_matrix(s) + w * rank_matrix(n)
            blend = blend / blend.max(axis=1, keepdims=True)
            out = pd.concat(
                [
                    aligned["submission_protossm"][["row_id"]].reset_index(drop=True),
                    pd.DataFrame(blend, columns=class_names),
                ],
                axis=1,
            )
            rows.append(score_prediction(f"rank_proto_sed_nfnet_w{w:.2f}", out, y_true, class_names, "synthetic_rank_blend"))

    args.output_csv.parent.mkdir(parents=True, exist_ok=True)
    with args.output_csv.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    print(f"wrote {args.output_csv} rows={len(rows)}")
    best = sorted(rows, key=lambda r: float(r["macro_auc"] or -1), reverse=True)[:8]
    for row in best:
        print(row["name"], row["macro_auc"], row["micro_auc"], row["top5_hit"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
