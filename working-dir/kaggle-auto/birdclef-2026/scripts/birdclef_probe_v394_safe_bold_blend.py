#!/usr/bin/env python3
"""Local safe/bold final portfolio blend probe.

Research question:
Can a convex blend of the v391 safe_final and v387 bold_final local candidates
dominate either endpoint on robustness while v387's real submission is pending?
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
EXPERIMENTS = ROOT / "experiments"
ARTIFACTS = ROOT / "artifacts"
ANCHOR_SUB = ROOT / "birdclef-2026/outputs/v107-rankceiling-perch-guarded-v1/submission.csv"
BOLD_SUB = EXPERIMENTS / "v387_v386_static_distill_local_submission.csv"
SAFE_SUB = EXPERIMENTS / "v391_v386_safe_static_distill_local_submission.csv"
CSV = EXPERIMENTS / "v394_safe_bold_blend_20260524.csv"
REPORT = EXPERIMENTS / "v394_safe_bold_blend_20260524.md"
RUNTIME = ARTIFACTS / "runtime_v394_safe_bold_blend_20260524.json"
FOLLOWUP_LABELS = ["47158son17", "516975", "116570", "47158son25", "chacha1", "47158son10", "47158son21"]


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser()
    ap.add_argument("--output-csv", default=str(CSV))
    ap.add_argument("--report", default=str(REPORT))
    ap.add_argument("--runtime-json", default=str(RUNTIME))
    return ap.parse_args()


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")


def load_v379():
    spec = importlib.util.spec_from_file_location("birdclef_probe_v379_v377_deployable_distill", V379_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {V379_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_submission(path: Path, class_names: list[str] | None = None) -> pd.DataFrame:
    df = pd.read_csv(path)
    if "row_id" not in df.columns:
        raise ValueError(f"{path} missing row_id")
    if class_names is None:
        return df
    missing = [c for c in class_names if c not in df.columns]
    if missing:
        raise ValueError(f"{path} missing class columns: {missing[:8]}")
    return df[["row_id", *class_names]].copy()


def weak_mean(v379, y_true: np.ndarray, values: np.ndarray, class_names: list[str]) -> float:
    aucs = v379.per_class_auc(y_true, values)
    return v379.weak_mean(aucs, class_names, FOLLOWUP_LABELS)


def score(v379, y_true: np.ndarray, groups: np.ndarray, class_names: list[str], anchor: np.ndarray, values: np.ndarray) -> dict[str, float]:
    base = v379.score_values(y_true, values, class_names)
    fold = v379.fold_stats(y_true, values, class_names, groups)
    return {
        "macro_auc": float(base["macro_auc"]),
        "micro_auc": float(base["micro_auc"]),
        "top1_hit": float(base["top1_hit"]),
        "top5_hit": float(base["top5_hit"]),
        "fold_mean": float(fold[0]),
        "fold_std": float(fold[1]),
        "fold_min": float(fold[2]),
        "weak_followup_auc": weak_mean(v379, y_true, values, class_names),
        "corr_vs_anchor": float(np.corrcoef(anchor.ravel(), values.ravel())[0, 1]),
        "changed_cells": int((np.abs(values - anchor) > 1e-12).sum()),
        "max_abs_delta": float(np.abs(values - anchor).max()),
        "mean_abs_delta": float(np.abs(values - anchor).mean()),
    }


def per_class_regressions(v379, y_true: np.ndarray, anchor: np.ndarray, values: np.ndarray) -> tuple[int, int, float]:
    anchor_aucs = v379.per_class_auc(y_true, anchor)
    value_aucs = v379.per_class_auc(y_true, values)
    deltas = value_aucs - anchor_aucs
    finite = deltas[np.isfinite(deltas)]
    return (
        int((finite < -0.001).sum()),
        int((finite < -0.003).sum()),
        float(finite.min()) if len(finite) else float("nan"),
    )


def main() -> int:
    args = parse_args()
    started = time.time()
    v379 = load_v379()
    anchor_df = load_submission(ANCHOR_SUB)
    class_names = [c for c in anchor_df.columns if c != "row_id"]
    safe_df = load_submission(SAFE_SUB, class_names)
    bold_df = load_submission(BOLD_SUB, class_names)
    if anchor_df["row_id"].astype(str).tolist() != safe_df["row_id"].astype(str).tolist():
        raise ValueError("anchor and safe row orders differ")
    if anchor_df["row_id"].astype(str).tolist() != bold_df["row_id"].astype(str).tolist():
        raise ValueError("anchor and bold row orders differ")

    labels = pd.read_csv(v379.DATA / "train_soundscapes_labels.csv")
    y_true = v379.labels_to_targets(anchor_df[["row_id"]], labels, class_names)
    groups = v379.row_groups(anchor_df["row_id"])
    anchor = anchor_df[class_names].to_numpy(dtype=np.float64)
    safe = safe_df[class_names].to_numpy(dtype=np.float64)
    bold = bold_df[class_names].to_numpy(dtype=np.float64)

    anchor_metrics = score(v379, y_true, groups, class_names, anchor, anchor)
    safe_metrics = score(v379, y_true, groups, class_names, anchor, safe)
    bold_metrics = score(v379, y_true, groups, class_names, anchor, bold)

    rows: list[dict[str, object]] = []
    for bold_weight in np.linspace(0.0, 1.0, 21):
        values = np.clip((1.0 - bold_weight) * safe + bold_weight * bold, 0.0, 1.0)
        metrics = score(v379, y_true, groups, class_names, anchor, values)
        reg_lt001, reg_lt003, worst_delta = per_class_regressions(v379, y_true, anchor, values)
        rows.append(
            {
                "candidate": f"safe{1.0-bold_weight:.2f}_bold{bold_weight:.2f}",
                "safe_weight": round(float(1.0 - bold_weight), 2),
                "bold_weight": round(float(bold_weight), 2),
                "macro_auc": metrics["macro_auc"],
                "macro_gain": metrics["macro_auc"] - anchor_metrics["macro_auc"],
                "weak_followup_auc": metrics["weak_followup_auc"],
                "weak_followup_gain": metrics["weak_followup_auc"] - anchor_metrics["weak_followup_auc"],
                "fold_std": metrics["fold_std"],
                "fold_std_delta": metrics["fold_std"] - anchor_metrics["fold_std"],
                "fold_min": metrics["fold_min"],
                "top1_hit": metrics["top1_hit"],
                "top5_hit": metrics["top5_hit"],
                "corr_vs_anchor": metrics["corr_vs_anchor"],
                "changed_cells": metrics["changed_cells"],
                "max_abs_delta": metrics["max_abs_delta"],
                "mean_abs_delta": metrics["mean_abs_delta"],
                "class_regressions_lt_001": reg_lt001,
                "material_class_regressions_lt_003": reg_lt003,
                "worst_class_delta": worst_delta,
            }
        )
    df = pd.DataFrame(rows)
    pass_df = df[
        (df["macro_gain"] >= 0.0015)
        & (df["weak_followup_gain"] >= 0.006)
        & (df["fold_std_delta"] <= 0)
        & (df["top5_hit"] >= anchor_metrics["top5_hit"])
        & (df["material_class_regressions_lt_003"].eq(0))
    ].copy()
    pass_df["portfolio_score"] = (
        pass_df["macro_gain"] * 1000.0
        + (-pass_df["fold_std_delta"]) * 500.0
        + pass_df["weak_followup_gain"] * 100.0
        - pass_df["changed_cells"] * 0.0001
    )
    best = pass_df.sort_values("portfolio_score", ascending=False).iloc[0] if len(pass_df) else df.sort_values("macro_gain", ascending=False).iloc[0]
    if len(pass_df) and best["candidate"] not in {"safe1.00_bold0.00", "safe0.00_bold1.00"}:
        decision = "PROMOTE-v394-safe-bold-blend-LOCAL-ONLY-NO-SUBMIT"
        next_action = "Materialize only after v387 resolves and only if this blended portfolio is needed over v391/v387 endpoints."
    else:
        decision = "HOLD-v394-endpoints-dominate-NO-SUBMIT"
        next_action = "Keep v387 as bold_final and v391 as safe_final; no blended materialization needed now."

    out_csv = Path(args.output_csv)
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_csv, index=False)
    runtime = {
        "timestamp_utc": utc_now(),
        "experiment_id": "v394-safe-bold-blend",
        "decision": decision,
        "elapsed_seconds": round(time.time() - started, 4),
        "anchor": anchor_metrics,
        "safe_v391": safe_metrics,
        "bold_v387": bold_metrics,
        "pass_count": int(len(pass_df)),
        "best": best.to_dict(),
        "next_recommended_action": next_action,
    }
    Path(args.runtime_json).parent.mkdir(parents=True, exist_ok=True)
    Path(args.runtime_json).write_text(json.dumps(runtime, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    top = df.sort_values(["macro_gain", "fold_std_delta"], ascending=[False, True]).head(8)
    lines = [
        "# v394 Safe/Bold Blend Probe",
        "",
        f"Updated: {runtime['timestamp_utc']}",
        "",
        f"Status: `{decision}`.",
        "",
        "## Research Question",
        "",
        "Can a convex blend of the v391 safe_final and v387 bold_final local candidates dominate either endpoint on robustness while v387's real submission is pending?",
        "",
        "## Result",
        "",
        f"- Pass-count: `{len(pass_df)}`",
        f"- Best portfolio candidate: `{best['candidate']}`",
        f"- Best macro gain: `{float(best['macro_gain']):+.8f}`",
        f"- Best fold std delta: `{float(best['fold_std_delta']):+.8f}`",
        f"- Best weak gain: `{float(best['weak_followup_gain']):+.8f}`",
        f"- Decision: `{decision}`",
        f"- Next: {next_action}",
        "",
        "## Endpoint Metrics",
        "",
        f"- safe v391: macro_gain `{safe_metrics['macro_auc'] - anchor_metrics['macro_auc']:+.8f}`, fold_std_delta `{safe_metrics['fold_std'] - anchor_metrics['fold_std']:+.8f}`, weak_gain `{safe_metrics['weak_followup_auc'] - anchor_metrics['weak_followup_auc']:+.8f}`",
        f"- bold v387: macro_gain `{bold_metrics['macro_auc'] - anchor_metrics['macro_auc']:+.8f}`, fold_std_delta `{bold_metrics['fold_std'] - anchor_metrics['fold_std']:+.8f}`, weak_gain `{bold_metrics['weak_followup_auc'] - anchor_metrics['weak_followup_auc']:+.8f}`",
        "",
        "## Top Macro Rows",
        "",
        top[
            [
                "candidate",
                "macro_gain",
                "fold_std_delta",
                "weak_followup_gain",
                "top5_hit",
                "changed_cells",
                "material_class_regressions_lt_003",
            ]
        ].to_csv(index=False),
    ]
    Path(args.report).write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"decision={decision}")
    print(f"pass_count={len(pass_df)}")
    print(f"best={best['candidate']} macro_gain={float(best['macro_gain']):+.8f} fold_std_delta={float(best['fold_std_delta']):+.8f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
