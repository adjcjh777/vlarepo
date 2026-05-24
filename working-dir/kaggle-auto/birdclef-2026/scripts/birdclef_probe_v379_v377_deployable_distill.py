#!/usr/bin/env python3
"""Deployable distillation probe for the v377 teacher-signal candidate.

Research question:
Can the v377 teacher movement be distilled into hidden-test-computable features
from the license-clean v107 branch, train-soundscape priors, and temporal
context, so that no v103 output is needed at inference time?
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import re
import time
from pathlib import Path
import sys

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from src.metrics import binary_roc_auc, multilabel_macro_auc  # noqa: E402


EXPERIMENTS = ROOT / "experiments"
ARTIFACTS = ROOT / "artifacts"
DATA = ROOT / "birdclef-2026/data"
V107_SUB = ROOT / "birdclef-2026/outputs/v107-rankceiling-perch-guarded-v1/submission.csv"
V103_SUB = ROOT / "birdclef-2026/outputs/v103-guarded-macro-risk-rescue-v1/submission.csv"
FOLLOWUP_LABELS = ["47158son17", "516975", "116570", "47158son25", "chacha1", "47158son10", "47158son21"]


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser()
    ap.add_argument("--output-csv", default=str(EXPERIMENTS / "v379_v377_deployable_distill_20260524.csv"))
    ap.add_argument("--report", default=str(EXPERIMENTS / "v379_v377_deployable_distill_20260524.md"))
    ap.add_argument("--runtime-json", default=str(ARTIFACTS / "runtime_v379_v377_deployable_distill_20260524.json"))
    return ap.parse_args()


def labels_to_targets(meta: pd.DataFrame, labels: pd.DataFrame, class_names: list[str]) -> np.ndarray:
    label_map: dict[str, set[str]] = {}
    for row in labels.itertuples(index=False):
        try:
            end_sec = int(str(row.end).split(":")[-1])
        except Exception:
            continue
        label_map[f"{Path(str(row.filename)).stem}_{end_sec}"] = {x for x in str(row.primary_label).split(";") if x}
    class_index = {c: i for i, c in enumerate(class_names)}
    y = np.zeros((len(meta), len(class_names)), dtype=np.uint8)
    for i, row_id in enumerate(meta["row_id"].astype(str).tolist()):
        for label in label_map.get(row_id, set()):
            idx = class_index.get(label)
            if idx is not None:
                y[i, idx] = 1
    return y


def row_groups(row_ids: pd.Series) -> np.ndarray:
    return row_ids.astype(str).str.replace(r"_\d+$", "", regex=True).to_numpy()


def row_features(row_ids: list[str]) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    pat = re.compile(r"^(?P<prefix>.+?)_(?P<site>S\d+)_(?P<date>\d{8})_(?P<time>\d{6})_(?P<end>\d+)$")
    for row_id in row_ids:
        match = pat.match(str(row_id))
        if match:
            hour = int(match.group("time")[:2])
            end = int(match.group("end"))
            site = match.group("site")
            file_stem = "_".join(str(row_id).split("_")[:-1])
        else:
            hour, end, site, file_stem = -1, -1, "SUNK", str(row_id)
        rows.append({"row_id": row_id, "file_stem": file_stem, "site": site, "hour": hour, "end_sec": end})
    return pd.DataFrame(rows)


def train_label_meta(labels: pd.DataFrame, class_names: list[str]) -> tuple[pd.DataFrame, np.ndarray]:
    rows: list[dict[str, object]] = []
    y_rows: list[np.ndarray] = []
    cidx = {c: i for i, c in enumerate(class_names)}
    pat_time = re.compile(r"\d{6}$")
    for row in labels.itertuples(index=False):
        stem = Path(str(row.filename)).stem
        parts = stem.split("_")
        site = next((p for p in parts if re.fullmatch(r"S\d+", p)), "SUNK")
        hour = int(parts[-1][:2]) if parts and pat_time.match(parts[-1]) else -1
        try:
            end = int(str(row.end).split(":")[-1])
        except Exception:
            end = -1
        target = np.zeros(len(class_names), dtype=np.float64)
        for label in str(row.primary_label).split(";"):
            idx = cidx.get(label)
            if idx is not None:
                target[idx] = 1.0
        rows.append({"file_stem": stem, "site": site, "hour": hour, "end_sec": end})
        y_rows.append(target)
    return pd.DataFrame(rows), np.vstack(y_rows)


def prior_for_rows(meta: pd.DataFrame, labels: pd.DataFrame, class_names: list[str]) -> np.ndarray:
    train_meta, y = train_label_meta(labels, class_names)
    global_p = y.mean(axis=0)
    site_values = train_meta["site"].astype(str).to_numpy()
    hour_values = train_meta["hour"].astype(int).to_numpy()
    out = np.zeros((len(meta), len(class_names)), dtype=np.float64)
    for i, row in meta.iterrows():
        site = str(row["site"])
        hour = int(row["hour"])
        same_site_hour = (site_values == site) & (hour_values == hour)
        same_site = site_values == site
        same_hour = hour_values == hour
        if same_site_hour.sum() >= 3:
            p = y[same_site_hour].mean(axis=0)
        elif same_site.sum() >= 3:
            p = y[same_site].mean(axis=0)
        elif same_hour.sum() >= 3:
            p = y[same_hour].mean(axis=0)
        else:
            p = global_p
        out[i] = 0.8 * p + 0.2 * global_p
    return out


def column_rank01(values: np.ndarray) -> np.ndarray:
    order = np.argsort(values, axis=0, kind="mergesort")
    ranks = np.empty_like(values, dtype=np.float64)
    col_idx = np.arange(values.shape[1])[None, :]
    rank_values = np.linspace(0.0, 1.0, values.shape[0], endpoint=True)[:, None]
    ranks[order, col_idx] = rank_values
    return ranks


def temporal_max(values: np.ndarray, meta: pd.DataFrame) -> np.ndarray:
    out = values.copy()
    files = meta["file_stem"].astype(str).to_numpy()
    ends = meta["end_sec"].astype(int).to_numpy()
    for file_stem in sorted(set(files.tolist())):
        idx = np.where(files == file_stem)[0]
        idx = idx[np.argsort(ends[idx])]
        if len(idx) <= 1:
            continue
        local = values[idx]
        prev_vals = np.vstack([local[:1], local[:-1]])
        next_vals = np.vstack([local[1:], local[-1:]])
        out[idx] = np.maximum.reduce([local, prev_vals, next_vals])
    return out


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


def score_values(y_true: np.ndarray, values: np.ndarray, class_names: list[str]) -> dict[str, float | int]:
    macro = multilabel_macro_auc(y_true, values, class_names)
    micro = binary_roc_auc(y_true.ravel(), values.ravel())
    return {
        "macro_auc": float(macro["mean_auc"]) if macro["mean_auc"] is not None else float("nan"),
        "micro_auc": float(micro) if micro is not None else float("nan"),
        "top1_hit": float(topk_hit_rate(y_true, values, 1) or 0.0),
        "top5_hit": float(topk_hit_rate(y_true, values, 5) or 0.0),
        "scored_classes": int(macro["scored_classes"]),
    }


def per_class_auc(y_true: np.ndarray, values: np.ndarray) -> np.ndarray:
    out = np.full(values.shape[1], np.nan, dtype=np.float64)
    for idx in range(values.shape[1]):
        auc = binary_roc_auc(y_true[:, idx], values[:, idx])
        if auc is not None:
            out[idx] = auc
    return out


def weak_mean(aucs: np.ndarray, class_names: list[str], labels: list[str]) -> float:
    idx = [class_names.index(label) for label in labels if label in class_names]
    vals = [float(aucs[i]) for i in idx if np.isfinite(aucs[i])]
    return float(np.mean(vals)) if vals else float("nan")


def fold_stats(y_true: np.ndarray, values: np.ndarray, class_names: list[str], groups: np.ndarray) -> tuple[float, float, float]:
    scores: list[float] = []
    for group in sorted(set(groups)):
        mask = groups == group
        macro = multilabel_macro_auc(y_true[mask], values[mask], class_names)
        if macro["mean_auc"] is not None:
            scores.append(float(macro["mean_auc"]))
    if not scores:
        return float("nan"), float("nan"), float("nan")
    arr = np.asarray(scores, dtype=np.float64)
    return float(arr.mean()), float(arr.std(ddof=0)), float(arr.min())


def v377_oracle(anchor: np.ndarray, teacher: np.ndarray, class_names: list[str]) -> tuple[np.ndarray, int]:
    out = anchor.copy()
    cidx = {c: i for i, c in enumerate(class_names)}
    anchor_rank = column_rank01(anchor)
    teacher_rank = column_rank01(teacher)
    active = 0
    for label in FOLLOWUP_LABELS:
        idx = cidx[label]
        mask = (teacher[:, idx] > anchor[:, idx]) & (teacher_rank[:, idx] > anchor_rank[:, idx])
        out[mask, idx] = np.clip(0.7 * out[mask, idx] + 0.3 * teacher[mask, idx], 0.0, 1.0)
        active += int(mask.sum())
    return out, active


def class_features(
    cls_idx: int,
    anchor: np.ndarray,
    anchor_rank: np.ndarray,
    prior: np.ndarray,
    prior_rank: np.ndarray,
    temporal: np.ndarray,
    meta: pd.DataFrame,
) -> np.ndarray:
    top_order = np.argsort(anchor, axis=1)
    top1 = anchor[np.arange(anchor.shape[0]), top_order[:, -1]]
    top2 = anchor[np.arange(anchor.shape[0]), top_order[:, -2]]
    hour = meta["hour"].astype(float).to_numpy()
    end = meta["end_sec"].astype(float).to_numpy()
    hour_angle = np.where(hour >= 0, 2 * np.pi * hour / 24.0, 0.0)
    end_scaled = np.where(end >= 0, end / 60.0, 0.0)
    return np.column_stack(
        [
            np.ones(anchor.shape[0]),
            anchor[:, cls_idx],
            anchor_rank[:, cls_idx],
            prior[:, cls_idx],
            prior_rank[:, cls_idx],
            temporal[:, cls_idx],
            temporal[:, cls_idx] - anchor[:, cls_idx],
            anchor[:, cls_idx] * prior_rank[:, cls_idx],
            top1,
            top1 - top2,
            np.sin(hour_angle),
            np.cos(hour_angle),
            end_scaled,
        ]
    )


def ridge_predict_oof(
    X: np.ndarray,
    y: np.ndarray,
    groups: np.ndarray,
    alpha: float,
) -> np.ndarray:
    pred = np.zeros_like(y, dtype=np.float64)
    for group in sorted(set(groups)):
        hold = groups == group
        train = ~hold
        xtr = X[train]
        ytr = y[train]
        mu = xtr.mean(axis=0)
        sigma = xtr.std(axis=0)
        sigma[sigma < 1e-8] = 1.0
        xtr_s = (xtr - mu) / sigma
        xh_s = (X[hold] - mu) / sigma
        reg = np.eye(xtr_s.shape[1]) * alpha
        reg[0, 0] = 0.0
        beta = np.linalg.pinv(xtr_s.T @ xtr_s + reg) @ xtr_s.T @ ytr
        pred[hold] = xh_s @ beta
    return np.clip(pred, 0.0, 1.0)


def f8(value: object) -> str:
    if isinstance(value, str):
        return value
    try:
        v = float(value)
    except Exception:
        return str(value)
    if not math.isfinite(v):
        return ""
    return f"{v:.8f}"


def main() -> int:
    args = parse_args()
    started = time.time()
    sample = pd.read_csv(DATA / "sample_submission.csv", nrows=1)
    class_names = sample.columns[1:].astype(str).tolist()
    cidx = {c: i for i, c in enumerate(class_names)}
    labels = pd.read_csv(DATA / "train_soundscapes_labels.csv")

    anchor_df = pd.read_csv(V107_SUB)
    teacher_df = pd.read_csv(V103_SUB)
    if anchor_df["row_id"].astype(str).tolist() != teacher_df["row_id"].astype(str).tolist():
        raise ValueError("v107 and v103 row_id orders differ")
    row_ids = anchor_df["row_id"].astype(str).tolist()
    anchor = anchor_df[class_names].to_numpy(dtype=np.float64)
    teacher = teacher_df[class_names].to_numpy(dtype=np.float64)
    y_true = labels_to_targets(anchor_df[["row_id"]], labels, class_names)
    groups = row_groups(anchor_df["row_id"])
    meta = row_features(row_ids)
    prior = prior_for_rows(meta, labels, class_names)
    anchor_rank = column_rank01(anchor)
    prior_rank = column_rank01(prior)
    temporal = temporal_max(anchor, meta)

    oracle, oracle_active = v377_oracle(anchor, teacher, class_names)
    anchor_score = score_values(y_true, anchor, class_names)
    oracle_score = score_values(y_true, oracle, class_names)
    anchor_aucs = per_class_auc(y_true, anchor)
    anchor_weak = weak_mean(anchor_aucs, class_names, FOLLOWUP_LABELS)
    anchor_fold_mean, anchor_fold_std, anchor_fold_min = fold_stats(y_true, anchor, class_names, groups)

    class_preds: dict[tuple[float, str], dict[str, np.ndarray]] = {}
    for alpha in [0.01, 0.1, 1.0, 10.0]:
        class_preds[(alpha, "delta")] = {}
        class_preds[(alpha, "value")] = {}
        for label in FOLLOWUP_LABELS:
            idx = cidx[label]
            X = class_features(idx, anchor, anchor_rank, prior, prior_rank, temporal, meta)
            target_value = oracle[:, idx]
            target_delta = np.maximum(oracle[:, idx] - anchor[:, idx], 0.0)
            class_preds[(alpha, "value")][label] = ridge_predict_oof(X, target_value, groups, alpha)
            class_preds[(alpha, "delta")][label] = ridge_predict_oof(X, target_delta, groups, alpha)

    rows: list[dict[str, object]] = []
    for alpha in [0.01, 0.1, 1.0, 10.0]:
        for target_mode in ["delta", "value"]:
            for blend_weight in [0.30, 0.50, 0.70, 1.00]:
                for min_delta in [0.0, 0.005, 0.01, 0.02]:
                    for min_prior_rank in [0.0, 0.25, 0.50]:
                        out = anchor.copy()
                        active = 0
                        for label in FOLLOWUP_LABELS:
                            idx = cidx[label]
                            if target_mode == "delta":
                                source = np.clip(anchor[:, idx] + class_preds[(alpha, target_mode)][label], 0.0, 1.0)
                            else:
                                source = class_preds[(alpha, target_mode)][label]
                            mask = (source > anchor[:, idx] + min_delta) & (prior_rank[:, idx] >= min_prior_rank)
                            if not mask.any():
                                continue
                            out[mask, idx] = np.clip(
                                (1.0 - blend_weight) * out[mask, idx] + blend_weight * source[mask],
                                0.0,
                                1.0,
                            )
                            active += int(mask.sum())
                        score = score_values(y_true, out, class_names)
                        aucs = per_class_auc(y_true, out)
                        weak = weak_mean(aucs, class_names, FOLLOWUP_LABELS)
                        fold_mean, fold_std, fold_min = fold_stats(y_true, out, class_names, groups)
                        macro_gain = float(score["macro_auc"] - anchor_score["macro_auc"])
                        weak_gain = weak - anchor_weak
                        fold_std_delta = fold_std - anchor_fold_std
                        corr_anchor = float(np.corrcoef(anchor.ravel(), out.ravel())[0, 1])
                        corr_oracle = float(np.corrcoef(oracle.ravel(), out.ravel())[0, 1])
                        promote = (
                            macro_gain >= 0.0015
                            or weak_gain >= 0.006
                            or (fold_std_delta <= 0.0 and macro_gain > 0.0005)
                            or corr_anchor < 0.97
                        )
                        if score["top5_hit"] + 1e-12 < anchor_score["top5_hit"]:
                            promote = False
                        rows.append(
                            {
                                "candidate": f"alpha{alpha:g}_{target_mode}_bw{blend_weight:g}_d{min_delta:g}_pr{min_prior_rank:g}",
                                "alpha": alpha,
                                "target_mode": target_mode,
                                "blend_weight": blend_weight,
                                "min_delta": min_delta,
                                "min_prior_rank": min_prior_rank,
                                "active_cells": active,
                                "macro_auc": score["macro_auc"],
                                "macro_gain": macro_gain,
                                "micro_auc": score["micro_auc"],
                                "top1_hit": score["top1_hit"],
                                "top5_hit": score["top5_hit"],
                                "fold_macro_mean": fold_mean,
                                "fold_macro_std": fold_std,
                                "fold_macro_min": fold_min,
                                "fold_std_delta": fold_std_delta,
                                "weak_followup_mean_auc": weak,
                                "weak_followup_gain": weak_gain,
                                "corr_vs_anchor": corr_anchor,
                                "corr_vs_v377_oracle": corr_oracle,
                                "decision": "PROMOTE-deployable-distill-candidate" if promote else "HOLD-no-promotion-gate",
                            }
                        )

    rows.sort(
        key=lambda r: (
            str(r["decision"]).startswith("PROMOTE"),
            float(r["macro_gain"]),
            float(r["weak_followup_gain"]),
            -float(r["fold_std_delta"]),
        ),
        reverse=True,
    )
    promoted = [r for r in rows if str(r["decision"]).startswith("PROMOTE")]
    best = rows[0]
    decision = (
        "PROMOTE-v379-deployable-v377-distill-NO-PUSH-NO-SUBMIT"
        if promoted
        else "HOLD-v379-v377-not-yet-deployably-distilled-NO-PUSH-NO-SUBMIT"
    )

    out_csv = Path(args.output_csv)
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    with out_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        for row in rows:
            writer.writerow({k: f8(v) for k, v in row.items()})

    runtime = {
        "timestamp_utc": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
        "decision": decision,
        "candidate_count": len(rows),
        "promoted_count": len(promoted),
        "anchor": anchor_score,
        "v377_oracle": oracle_score,
        "v377_oracle_active_cells": oracle_active,
        "anchor_fold_macro_mean": anchor_fold_mean,
        "anchor_fold_macro_std": anchor_fold_std,
        "anchor_fold_macro_min": anchor_fold_min,
        "anchor_weak_followup_mean_auc": anchor_weak,
        "best_candidate": best,
        "deployable_feature_policy": "uses v107 scores/ranks, train_soundscape site-hour priors, row_id temporal context; v103 used only to form local training target and never as inference input",
        "runtime_seconds": round(time.time() - started, 3),
    }
    runtime_path = Path(args.runtime_json)
    runtime_path.parent.mkdir(parents=True, exist_ok=True)
    runtime_path.write_text(json.dumps(runtime, indent=2, sort_keys=True), encoding="utf-8")

    report = Path(args.report)
    lines = [
        "# v379 v377 Deployable Distillation Probe",
        "",
        f"Updated: {runtime['timestamp_utc']}",
        "",
        f"Status: `{decision}`.",
        "",
        "## Research Question",
        "",
        "Can the v377 teacher movement be distilled into hidden-test-computable features from the license-clean v107 branch, train-soundscape priors, and temporal context, so that no v103 output is needed at inference time?",
        "",
        "## Inference Feature Policy",
        "",
        "- Candidate inference uses v107 scores/ranks, train_soundscape site-hour priors, row_id-derived temporal context, and fixed coefficients.",
        "- v103 is used only in this local probe to define the distillation target; it is not an inference dependency.",
        "- No Kaggle push or real competition submission is authorized by this probe.",
        "",
        "## Baselines",
        "",
        f"- v107 anchor macro: `{f8(anchor_score['macro_auc'])}`, top5: `{f8(anchor_score['top5_hit'])}`, fold std: `{f8(anchor_fold_std)}`",
        f"- v377 oracle macro: `{f8(oracle_score['macro_auc'])}`, top5: `{f8(oracle_score['top5_hit'])}`, active cells: `{oracle_active}`",
        f"- anchor follow-up weak mean AUC: `{f8(anchor_weak)}`",
        "",
        "## Result",
        "",
        f"- Candidates screened: `{len(rows)}`",
        f"- Promoted local candidates: `{len(promoted)}`",
        f"- Best candidate: `{best['candidate']}`",
        f"- Best macro: `{f8(best['macro_auc'])}` / gain `{f8(best['macro_gain'])}`",
        f"- Best weak follow-up gain: `{f8(best['weak_followup_gain'])}`",
        f"- Best fold std delta: `{f8(best['fold_std_delta'])}`",
        f"- Best corr vs anchor: `{f8(best['corr_vs_anchor'])}`",
        f"- Best corr vs v377 oracle: `{f8(best['corr_vs_v377_oracle'])}`",
        "",
        "## Top Candidates",
        "",
        "| candidate | macro_gain | weak_gain | fold_std_delta | top5 | corr_anchor | corr_oracle | decision |",
        "|---|---:|---:|---:|---:|---:|---:|---|",
    ]
    for row in rows[:12]:
        formatted = {k: f8(v) for k, v in row.items()}
        lines.append(
            "| {candidate} | {macro_gain} | {weak_followup_gain} | {fold_std_delta} | {top5_hit} | {corr_vs_anchor} | {corr_vs_v377_oracle} | {decision} |".format(
                **formatted
            )
        )
    lines.extend(
        [
            "",
            "## Decision",
            "",
            f"- `{decision}`",
            "- If promoted, next step is a static notebook materializer that embeds fixed coefficients and repeats the same feature policy.",
            "- If held, v377 remains a useful teacher diagnostic only, not a submit-ready route.",
        ]
    )
    report.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"decision={decision}")
    print(f"candidates={len(rows)} promoted={len(promoted)}")
    print(f"best_candidate={best['candidate']}")
    print(f"best_macro={f8(best['macro_auc'])} macro_gain={f8(best['macro_gain'])}")
    print(f"best_weak_gain={f8(best['weak_followup_gain'])}")
    print(f"best_fold_std_delta={f8(best['fold_std_delta'])}")
    print(f"corr_anchor={f8(best['corr_vs_anchor'])} corr_oracle={f8(best['corr_vs_v377_oracle'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
