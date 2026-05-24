#!/usr/bin/env python3
"""Class/fold risk audit for the v387 static candidate.

Research question:
Does the v386-selected v387 candidate pass class-regression and fold-risk
checks strongly enough to remain queued behind v383 while Run-mode is pending?
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
V386_PROBE = ROOT / "birdclef-2026/scripts/birdclef_probe_v386_v383_param_stress.py"
EXPERIMENTS = ROOT / "experiments"
ARTIFACTS = ROOT / "artifacts"
CSV = EXPERIMENTS / "v388_v387_class_risk_20260524.csv"
FOLD_CSV = EXPERIMENTS / "v388_v387_fold_risk_20260524.csv"
REPORT = EXPERIMENTS / "v388_v387_class_risk_20260524.md"
RUNTIME = ARTIFACTS / "runtime_v388_v387_class_risk_20260524.json"
FOLLOWUP_LABELS = ["47158son17", "516975", "116570", "47158son25", "chacha1", "47158son10", "47158son21"]


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser()
    ap.add_argument("--class-csv", default=str(CSV))
    ap.add_argument("--fold-csv", default=str(FOLD_CSV))
    ap.add_argument("--report", default=str(REPORT))
    ap.add_argument("--runtime-json", default=str(RUNTIME))
    return ap.parse_args()


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")


def load_v386():
    spec = importlib.util.spec_from_file_location("birdclef_probe_v386_v383_param_stress", V386_PROBE)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {V386_PROBE}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def safe_auc(v379, y: np.ndarray, score: np.ndarray) -> float | None:
    auc = v379.binary_roc_auc(y, score)
    return None if auc is None else float(auc)


def fold_rows(v379, y_true: np.ndarray, groups: np.ndarray, class_names: list[str], anchor: np.ndarray, candidate: np.ndarray) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for group in sorted(set(groups)):
        mask = groups == group
        a = v379.score_values(y_true[mask], anchor[mask], class_names)
        c = v379.score_values(y_true[mask], candidate[mask], class_names)
        rows.append(
            {
                "group": group,
                "rows": int(mask.sum()),
                "anchor_macro_auc": a["macro_auc"],
                "candidate_macro_auc": c["macro_auc"],
                "macro_delta": float(c["macro_auc"] - a["macro_auc"]),
                "anchor_top5": a["top5_hit"],
                "candidate_top5": c["top5_hit"],
                "top5_delta": float(c["top5_hit"] - a["top5_hit"]),
            }
        )
    return rows


def main() -> int:
    args = parse_args()
    started = time.time()
    v386 = load_v386()
    v379, class_names, y_true, groups, anchor, prior_rank, deltas = v386.build_base()
    candidate, active_cells = v386.make_candidate(
        anchor,
        prior_rank,
        class_names,
        deltas,
        blend=1.0,
        min_delta=0.0,
        min_prior_rank=0.0,
        delta_scale=1.25,
    )
    anchor_metrics = v386.score_candidate(v379, y_true, groups, class_names, anchor, anchor)
    candidate_metrics = v386.score_candidate(v379, y_true, groups, class_names, anchor, candidate)

    class_rows: list[dict[str, object]] = []
    for idx, label in enumerate(class_names):
        anchor_auc = safe_auc(v379, y_true[:, idx], anchor[:, idx])
        cand_auc = safe_auc(v379, y_true[:, idx], candidate[:, idx])
        if anchor_auc is None or cand_auc is None:
            continue
        changed = np.abs(candidate[:, idx] - anchor[:, idx]) > 1e-12
        class_rows.append(
            {
                "primary_label": label,
                "anchor_auc": anchor_auc,
                "candidate_auc": cand_auc,
                "auc_delta": cand_auc - anchor_auc,
                "changed_rows": int(changed.sum()),
                "max_abs_delta": float(np.abs(candidate[:, idx] - anchor[:, idx]).max()),
                "mean_abs_delta": float(np.abs(candidate[:, idx] - anchor[:, idx]).mean()),
                "followup_label": label in FOLLOWUP_LABELS,
            }
        )
    class_df = pd.DataFrame(class_rows).sort_values("auc_delta").reset_index(drop=True)
    fold_df = pd.DataFrame(fold_rows(v379, y_true, groups, class_names, anchor, candidate)).sort_values("macro_delta").reset_index(drop=True)

    regressions = class_df[class_df["auc_delta"] < -0.001]
    material_regressions = class_df[class_df["auc_delta"] < -0.003]
    followup = class_df[class_df["followup_label"]]
    worsened_folds = fold_df[fold_df["macro_delta"] < -0.001]

    checks = {
        "macro_gate": candidate_metrics["macro_auc"] - anchor_metrics["macro_auc"] >= 0.0015,
        "weak_gate": candidate_metrics["weak_followup_auc"] - anchor_metrics["weak_followup_auc"] >= 0.006,
        "top5_not_worse": candidate_metrics["top5_hit"] + 1e-12 >= anchor_metrics["top5_hit"],
        "fold_std_not_worse": candidate_metrics["fold_std"] <= anchor_metrics["fold_std"] + 1e-12,
        "no_material_class_regression": len(material_regressions) == 0,
        "limited_minor_class_regressions": len(regressions) <= 2,
        "no_fold_macro_regression_gt_001": len(worsened_folds) == 0,
        "followup_mean_positive": float(followup["auc_delta"].mean()) > 0,
    }
    block_count = sum(not v for v in checks.values())
    decision = "READY-v388-v387-class-risk-pass-NO-PUSH-NO-SUBMIT" if block_count == 0 else "HOLD-v388-v387-class-risk-review-NO-PUSH-NO-SUBMIT"

    Path(args.class_csv).parent.mkdir(parents=True, exist_ok=True)
    class_df.to_csv(args.class_csv, index=False)
    fold_df.to_csv(args.fold_csv, index=False)

    runtime = {
        "timestamp_utc": utc_now(),
        "experiment_id": "v388-v387-class-risk",
        "decision": decision,
        "elapsed_seconds": round(time.time() - started, 4),
        "active_cells": active_cells,
        "checks": checks,
        "block_count": block_count,
        "anchor": anchor_metrics,
        "candidate": candidate_metrics,
        "class_regressions_lt_001": int(len(regressions)),
        "material_class_regressions_lt_003": int(len(material_regressions)),
        "worst_class": class_df.head(1).to_dict("records")[0] if len(class_df) else {},
        "best_class": class_df.tail(1).to_dict("records")[0] if len(class_df) else {},
        "worst_fold": fold_df.head(1).to_dict("records")[0] if len(fold_df) else {},
        "followup_mean_auc_delta": float(followup["auc_delta"].mean()) if len(followup) else None,
        "next_recommended_action": "Wait for v387 Run-mode proof, then run submit-readiness only if this audit remains pass." if block_count == 0 else "Inspect class/fold regressions before any v387 submit-readiness gate.",
    }
    Path(args.runtime_json).parent.mkdir(parents=True, exist_ok=True)
    Path(args.runtime_json).write_text(json.dumps(runtime, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    top_bad = class_df.head(8)
    top_good = class_df.tail(8).sort_values("auc_delta", ascending=False)
    lines = [
        "# v388 v387 Class Risk Audit",
        "",
        f"Updated: {runtime['timestamp_utc']}",
        "",
        f"Status: `{decision}`.",
        "",
        "## Research Question",
        "",
        "Does the v386-selected v387 candidate pass class-regression and fold-risk checks strongly enough to remain queued behind v383 while Run-mode is pending?",
        "",
        "## Result",
        "",
        f"- Macro gain: `{candidate_metrics['macro_auc'] - anchor_metrics['macro_auc']:+.8f}`",
        f"- Weak follow-up gain: `{candidate_metrics['weak_followup_auc'] - anchor_metrics['weak_followup_auc']:+.8f}`",
        f"- Fold std delta: `{candidate_metrics['fold_std'] - anchor_metrics['fold_std']:+.8f}`",
        f"- Top5: `{anchor_metrics['top5_hit']:.8f}` -> `{candidate_metrics['top5_hit']:.8f}`",
        f"- Class regressions < -0.001: `{len(regressions)}`",
        f"- Material class regressions < -0.003: `{len(material_regressions)}`",
        f"- Fold regressions < -0.001: `{len(worsened_folds)}`",
        f"- Block count: `{block_count}`",
        "",
        "## Checks",
        "",
    ]
    lines += [f"- `{k}`: `{v}`" for k, v in checks.items()]
    lines += [
        "",
        "## Worst Classes",
        "",
        top_bad[["primary_label", "auc_delta", "changed_rows", "max_abs_delta", "followup_label"]].to_csv(index=False),
        "## Best Classes",
        "",
        top_good[["primary_label", "auc_delta", "changed_rows", "max_abs_delta", "followup_label"]].to_csv(index=False),
        "## Decision",
        "",
        f"- `{decision}`",
        f"- Next: {runtime['next_recommended_action']}",
    ]
    Path(args.report).write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"decision={decision}")
    print(f"block_count={block_count}")
    print(f"macro_gain={candidate_metrics['macro_auc'] - anchor_metrics['macro_auc']:+.8f}")
    print(f"weak_gain={candidate_metrics['weak_followup_auc'] - anchor_metrics['weak_followup_auc']:+.8f}")
    print(f"class_regressions_lt_001={len(regressions)} material_lt_003={len(material_regressions)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
