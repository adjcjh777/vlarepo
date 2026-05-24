#!/usr/bin/env python3
"""Local parameter stress for the v383 deployable distill route.

Research question:
Can stricter prior-rank/delta/blend gates improve the v383 fixed-coefficient
distill candidate's robustness without changing the underlying CV split or
runtime feature family?
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
V379_PATH = ROOT / "birdclef-2026/scripts/birdclef_probe_v379_v377_deployable_distill.py"
V380_PATH = ROOT / "birdclef-2026/scripts/birdclef_prepare_v380_v379_static_materializer.py"
EXPERIMENTS = ROOT / "experiments"
ARTIFACTS = ROOT / "artifacts"
CSV = EXPERIMENTS / "v386_v383_param_stress_20260524.csv"
REPORT = EXPERIMENTS / "v386_v383_param_stress_20260524.md"
RUNTIME = ARTIFACTS / "runtime_v386_v383_param_stress_20260524.json"
FOLLOWUP_LABELS = ["47158son17", "516975", "116570", "47158son25", "chacha1", "47158son10", "47158son21"]


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser()
    ap.add_argument("--output-csv", default=str(CSV))
    ap.add_argument("--report", default=str(REPORT))
    ap.add_argument("--runtime-json", default=str(RUNTIME))
    return ap.parse_args()


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def build_base():
    v379 = load_module("birdclef_probe_v379_v377_deployable_distill", V379_PATH)
    v380 = load_module("birdclef_prepare_v380_v379_static_materializer", V380_PATH)
    sample = pd.read_csv(v379.DATA / "sample_submission.csv", nrows=1)
    class_names = sample.columns[1:].astype(str).tolist()
    labels = pd.read_csv(v379.DATA / "train_soundscapes_labels.csv")
    anchor_df = pd.read_csv(v379.V107_SUB)
    teacher_df = pd.read_csv(v379.V103_SUB)
    if anchor_df["row_id"].astype(str).tolist() != teacher_df["row_id"].astype(str).tolist():
        raise ValueError("v107 and v103 row_id orders differ")

    anchor = anchor_df[class_names].to_numpy(dtype=np.float64)
    teacher = teacher_df[class_names].to_numpy(dtype=np.float64)
    y_true = v379.labels_to_targets(anchor_df[["row_id"]], labels, class_names)
    groups = v379.row_groups(anchor_df["row_id"])
    meta = v379.row_features(anchor_df["row_id"].astype(str).tolist())
    prior = v379.prior_for_rows(meta, labels, class_names)
    anchor_rank = v379.column_rank01(anchor)
    prior_rank = v379.column_rank01(prior)
    temporal = v379.temporal_max(anchor, meta)
    oracle, _ = v379.v377_oracle(anchor, teacher, class_names)

    class_index = {c: i for i, c in enumerate(class_names)}
    deltas: dict[str, np.ndarray] = {}
    for label in FOLLOWUP_LABELS:
        idx = class_index[label]
        X = v379.class_features(idx, anchor, anchor_rank, prior, prior_rank, temporal, meta)
        target_delta = np.maximum(oracle[:, idx] - anchor[:, idx], 0.0)
        coef = v380.fit_full_ridge(X, target_delta, alpha=0.01)
        source_delta = np.clip(((X - np.asarray(coef["mean"])) / np.asarray(coef["scale"])) @ np.asarray(coef["beta"]), 0.0, 1.0)
        deltas[label] = source_delta
    return v379, class_names, y_true, groups, anchor, prior_rank, deltas


def per_class_auc(v379, y_true: np.ndarray, values: np.ndarray) -> np.ndarray:
    return v379.per_class_auc(y_true, values)


def weak_mean(v379, aucs: np.ndarray, class_names: list[str]) -> float:
    return v379.weak_mean(aucs, class_names, FOLLOWUP_LABELS)


def score_candidate(v379, y_true, groups, class_names, anchor, values) -> dict[str, float]:
    score = v379.score_values(y_true, values, class_names)
    fold = v379.fold_stats(y_true, values, class_names, groups)
    aucs = per_class_auc(v379, y_true, values)
    return {
        "macro_auc": float(score["macro_auc"]),
        "micro_auc": float(score["micro_auc"]),
        "top1_hit": float(score["top1_hit"]),
        "top5_hit": float(score["top5_hit"]),
        "fold_mean": float(fold[0]),
        "fold_std": float(fold[1]),
        "fold_min": float(fold[2]),
        "weak_followup_auc": weak_mean(v379, aucs, class_names),
        "corr_vs_anchor": float(np.corrcoef(anchor.ravel(), values.ravel())[0, 1]),
    }


def make_candidate(anchor: np.ndarray, prior_rank: np.ndarray, class_names: list[str], deltas: dict[str, np.ndarray], blend: float, min_delta: float, min_prior_rank: float, delta_scale: float) -> tuple[np.ndarray, int]:
    out = anchor.copy()
    class_index = {c: i for i, c in enumerate(class_names)}
    active = 0
    for label, source_delta in deltas.items():
        idx = class_index[label]
        scaled_delta = np.clip(source_delta * delta_scale, 0.0, 1.0)
        source = np.clip(anchor[:, idx] + scaled_delta, 0.0, 1.0)
        mask = (source > anchor[:, idx] + min_delta) & (prior_rank[:, idx] >= min_prior_rank)
        if mask.any():
            out[mask, idx] = np.clip((1.0 - blend) * out[mask, idx] + blend * source[mask], 0.0, 1.0)
            active += int(mask.sum())
    return out, active


def markdown_table(df: pd.DataFrame, columns: list[str]) -> str:
    lines = ["| " + " | ".join(columns) + " |", "| " + " | ".join(["---"] * len(columns)) + " |"]
    for row in df[columns].itertuples(index=False):
        vals: list[str] = []
        for value in row:
            if isinstance(value, float):
                vals.append(f"{value:.8f}")
            else:
                vals.append(str(value))
        lines.append("| " + " | ".join(vals) + " |")
    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    started = time.time()
    v379, class_names, y_true, groups, anchor, prior_rank, deltas = build_base()
    anchor_metrics = score_candidate(v379, y_true, groups, class_names, anchor, anchor)

    rows: list[dict[str, object]] = []
    for blend in [0.35, 0.50, 0.70, 0.85, 1.00]:
        for min_delta in [0.0, 0.0025, 0.005, 0.01]:
            for min_prior_rank in [0.0, 0.25, 0.50, 0.70, 0.85]:
                for delta_scale in [0.75, 1.00, 1.25]:
                    values, active = make_candidate(
                        anchor, prior_rank, class_names, deltas, blend, min_delta, min_prior_rank, delta_scale
                    )
                    metrics = score_candidate(v379, y_true, groups, class_names, anchor, values)
                    rows.append(
                        {
                            "candidate": f"blend{blend:g}_delta{min_delta:g}_pr{min_prior_rank:g}_scale{delta_scale:g}",
                            "blend": blend,
                            "min_delta": min_delta,
                            "min_prior_rank": min_prior_rank,
                            "delta_scale": delta_scale,
                            "active_cells": active,
                            "macro_auc": metrics["macro_auc"],
                            "macro_gain": metrics["macro_auc"] - anchor_metrics["macro_auc"],
                            "micro_auc": metrics["micro_auc"],
                            "top1_hit": metrics["top1_hit"],
                            "top5_hit": metrics["top5_hit"],
                            "fold_std": metrics["fold_std"],
                            "fold_std_delta": metrics["fold_std"] - anchor_metrics["fold_std"],
                            "fold_min": metrics["fold_min"],
                            "weak_followup_auc": metrics["weak_followup_auc"],
                            "weak_followup_gain": metrics["weak_followup_auc"] - anchor_metrics["weak_followup_auc"],
                            "corr_vs_anchor": metrics["corr_vs_anchor"],
                        }
                    )

    df = pd.DataFrame(rows)
    df = df.sort_values(
        ["macro_gain", "weak_followup_gain", "fold_std_delta", "active_cells"],
        ascending=[False, False, True, False],
    ).reset_index(drop=True)

    v383 = df.loc[
        (df["blend"].eq(0.70))
        & (df["min_delta"].eq(0.0))
        & (df["min_prior_rank"].eq(0.0))
        & (df["delta_scale"].eq(1.0))
    ].iloc[0]
    best = df.iloc[0]
    best_non_v383 = df.loc[df["candidate"].ne(v383["candidate"])].iloc[0]

    promoted = (
        best["macro_gain"] >= 0.0015
        and best["top5_hit"] + 1e-12 >= anchor_metrics["top5_hit"]
        and best["fold_std_delta"] <= 1e-12
    )
    better_than_v383 = (
        best["macro_auc"] > float(v383["macro_auc"]) + 1e-6
        or (
            best["macro_auc"] >= float(v383["macro_auc"]) - 0.0001
            and best["fold_std"] < float(v383["fold_std"]) - 1e-6
        )
    )
    if promoted and better_than_v383:
        decision = "PROMOTE-v386-param-stress-candidate-NO-PUSH-NO-SUBMIT"
        next_action = "Materialize the selected v386 parameter set only after v383 submit decision is resolved."
    else:
        decision = "HOLD-v386-no-better-than-v383-NO-PUSH-NO-SUBMIT"
        next_action = "Keep v383 as the current submit-ready candidate and search a different mechanism family."

    out_csv = Path(args.output_csv)
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_csv, index=False)

    runtime = {
        "timestamp_utc": utc_now(),
        "experiment_id": "v386-v383-param-stress",
        "decision": decision,
        "elapsed_seconds": round(time.time() - started, 4),
        "candidate_count": int(len(df)),
        "anchor": anchor_metrics,
        "v383_reference": v383.to_dict(),
        "best": best.to_dict(),
        "best_non_v383": best_non_v383.to_dict(),
        "next_recommended_action": next_action,
    }
    Path(args.runtime_json).parent.mkdir(parents=True, exist_ok=True)
    Path(args.runtime_json).write_text(json.dumps(runtime, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    top = df.head(12).copy()
    report_lines = [
        "# v386 v383 Param Stress",
        "",
        f"Updated: {runtime['timestamp_utc']}",
        "",
        f"Status: `{decision}`.",
        "",
        "## Research Question",
        "",
        "Can stricter prior-rank/delta/blend gates improve the v383 fixed-coefficient distill candidate's robustness without changing the underlying CV split or runtime feature family?",
        "",
        "## Result",
        "",
        f"- Candidates screened: `{len(df)}`",
        f"- v383 reference: `{v383['candidate']}` macro_gain `{float(v383['macro_gain']):+.8f}`, fold_std_delta `{float(v383['fold_std_delta']):+.8f}`, weak_gain `{float(v383['weak_followup_gain']):+.8f}`",
        f"- Best: `{best['candidate']}` macro_gain `{float(best['macro_gain']):+.8f}`, fold_std_delta `{float(best['fold_std_delta']):+.8f}`, weak_gain `{float(best['weak_followup_gain']):+.8f}`",
        f"- Decision: `{decision}`",
        f"- Next: {next_action}",
        "",
        "## Top Candidates",
        "",
        markdown_table(
            top,
            [
                "candidate",
                "active_cells",
                "macro_gain",
                "fold_std_delta",
                "weak_followup_gain",
                "top5_hit",
                "corr_vs_anchor",
            ],
        ),
    ]
    Path(args.report).write_text("\n".join(report_lines) + "\n", encoding="utf-8")

    print(f"decision={decision}")
    print(f"candidate_count={len(df)}")
    print(f"best={best['candidate']} macro_gain={float(best['macro_gain']):+.8f} fold_std_delta={float(best['fold_std_delta']):+.8f}")
    print(f"v383={v383['candidate']} macro_gain={float(v383['macro_gain']):+.8f} fold_std_delta={float(v383['fold_std_delta']):+.8f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
