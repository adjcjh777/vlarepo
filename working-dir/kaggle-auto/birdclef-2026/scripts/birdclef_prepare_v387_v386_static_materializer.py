#!/usr/bin/env python3
"""Materialize the v386 parameter-stressed v383 route as a static notebook.

This creates a Run-mode candidate only. It does not push to Kaggle and does
not make a competition submission.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import time
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
V380_PREP = ROOT / "birdclef-2026/scripts/birdclef_prepare_v380_v379_static_materializer.py"
V383_PREP = ROOT / "birdclef-2026/scripts/birdclef_prepare_v383_v380_dryrun_tolerant.py"
V386_PROBE = ROOT / "birdclef-2026/scripts/birdclef_probe_v386_v383_param_stress.py"
DEST = ROOT / "birdclef-2026/notebooks/v387-v386-static-distill"
NEW_KERNEL_ID = "junhaochengadjcjh7u7/bc26-v387-v386-static-distill"
NEW_TITLE = "bc26-v387-v386-static-distill"
SPEC_PATH = ROOT / "experiments/v387_v386_static_distill_spec.json"
LOCAL_SUB = ROOT / "experiments/v387_v386_static_distill_local_submission.csv"
CSV = ROOT / "experiments/v387_v386_static_materializer_20260524.csv"
REPORT = ROOT / "experiments/v387_v386_static_materializer_20260524.md"
RUNTIME = ROOT / "artifacts/runtime_v387_v386_static_materializer_20260524.json"
LINEAGE = ROOT / "artifacts/lineage_v387_v386_static_materializer_20260524.json"
MARKER = "CODEX_V387_V386_STATIC_DISTILL_PATCH"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def build_v386_spec_and_local_candidate() -> tuple[dict[str, object], dict[str, object], pd.DataFrame]:
    v380 = load_module("birdclef_prepare_v380_v379_static_materializer", V380_PREP)
    v386 = load_module("birdclef_probe_v386_v383_param_stress", V386_PROBE)
    spec, _, _ = v380.build_spec_and_local_candidate()
    for coef in spec["coefs_by_class"].values():
        coef["beta"] = [float(x) * 1.25 for x in coef["beta"]]
    spec.update(
        {
            "candidate": "v387-v386-static-distill",
            "patch_marker": MARKER,
            "source_route": "v383-param-stress-selected-blend1-delta0-pr0-scale1.25",
            "blend_weight": 1.0,
            "min_delta": 0.0,
            "min_prior_rank": 0.0,
            "delta_scale_materialized_into_beta": 1.25,
            "runtime_policy": "runtime uses v107 submission, competition train_soundscape labels, row_id context, fixed coefficients scaled by v386, and tolerates v107 train-row dry-run fallback",
        }
    )

    v379, class_names, y_true, groups, anchor, prior_rank, deltas = v386.build_base()
    values, active_cells = v386.make_candidate(
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
    local_metrics = v386.score_candidate(v379, y_true, groups, class_names, anchor, values)
    metrics = {
        "active_cells": active_cells,
        "anchor_macro_auc": anchor_metrics["macro_auc"],
        "local_macro_auc": local_metrics["macro_auc"],
        "macro_gain": local_metrics["macro_auc"] - anchor_metrics["macro_auc"],
        "anchor_top1_hit": anchor_metrics["top1_hit"],
        "local_top1_hit": local_metrics["top1_hit"],
        "anchor_top5_hit": anchor_metrics["top5_hit"],
        "local_top5_hit": local_metrics["top5_hit"],
        "anchor_fold_std": anchor_metrics["fold_std"],
        "local_fold_std": local_metrics["fold_std"],
        "fold_std_delta": local_metrics["fold_std"] - anchor_metrics["fold_std"],
        "anchor_weak_followup_auc": anchor_metrics["weak_followup_auc"],
        "local_weak_followup_auc": local_metrics["weak_followup_auc"],
        "weak_followup_gain": local_metrics["weak_followup_auc"] - anchor_metrics["weak_followup_auc"],
        "corr_vs_anchor": local_metrics["corr_vs_anchor"],
    }
    anchor_df = pd.read_csv(v379.V107_SUB)
    out_df = anchor_df[["row_id", *class_names]].copy()
    out_df[class_names] = values
    return spec, metrics, out_df


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()

    started = time.time()
    v383 = load_module("birdclef_prepare_v383_v380_dryrun_tolerant", V383_PREP)
    spec, metrics, local_df = build_v386_spec_and_local_candidate()
    LOCAL_SUB.parent.mkdir(parents=True, exist_ok=True)
    local_df.to_csv(LOCAL_SUB, index=False)

    v383.DEST = DEST
    v383.NEW_KERNEL_ID = NEW_KERNEL_ID
    v383.NEW_TITLE = NEW_TITLE
    v383.SPEC_PATH = SPEC_PATH
    v383.LOCAL_SUB = LOCAL_SUB
    v383.CSV = CSV
    v383.REPORT = REPORT
    v383.RUNTIME = RUNTIME
    v383.LINEAGE = LINEAGE
    v383.MARKER = MARKER

    v380 = load_module("birdclef_prepare_v380_v379_static_materializer", V380_PREP)
    info = v383.materialize(spec, args.overwrite, v380)
    nb_path = DEST / "submission.ipynb"
    nb_text = nb_path.read_text(encoding="utf-8")
    nb_text = nb_text.replace("v383_static_distill_summary.csv", "v387_static_distill_summary.csv")
    nb_text = nb_text.replace("v383_static_distill_diagnostics.csv", "v387_static_distill_diagnostics.csv")
    nb_text = nb_text.replace(
        "v383 dry-run tolerant static distill patch complete",
        "v387 dry-run tolerant static distill patch complete",
    )
    nb_text = nb_text.replace(
        "v383 dry-run row mismatch tolerated",
        "v387 dry-run row mismatch tolerated",
    )
    nb_path.write_text(nb_text, encoding="utf-8")
    audit = v383.static_audit(info, spec, metrics)
    if audit["decision"] == "READY-v383-dryrun-tolerant-static-audit-NO-PUSH-NO-SUBMIT":
        audit["decision"] = "READY-v387-v386-static-materializer-audit-NO-PUSH-NO-SUBMIT"
        audit["next_recommended_action"] = "Build a guarded v387 Run-mode push/audit pair after v383 real-submit decision is resolved."
    v383.write_outputs(info, spec, metrics, audit, time.time() - started)

    runtime = json.loads(RUNTIME.read_text(encoding="utf-8"))
    runtime["experiment_id"] = "v387-v386-static-materializer"
    runtime["decision"] = audit["decision"]
    runtime["selected_v386_params"] = {
        "blend": 1.0,
        "min_delta": 0.0,
        "min_prior_rank": 0.0,
        "delta_scale": 1.25,
    }
    RUNTIME.write_text(json.dumps(runtime, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    df = pd.read_csv(CSV)
    df["experiment_id"] = "v387-v386-static-materializer"
    df["kernel_id"] = NEW_KERNEL_ID
    df["decision"] = audit["decision"]
    df.to_csv(CSV, index=False)

    report = REPORT.read_text(encoding="utf-8")
    report = report.replace("# v383 v380 Dry-run-tolerant Static Materializer", "# v387 v386 Static Materializer")
    report = report.replace("v383-v380-dryrun-tolerant", "v387-v386-static-materializer")
    report = report.replace("Can the v380 materializer be repaired so Kaggle Run-mode dry-run\n            train-row fallback no longer crashes while preserving real\n            sample-row guards and the clean v107 runtime policy?", "Can the v386 parameter-stressed v383 route be materialized as a static CPU-only notebook while preserving the dry-run tolerant real sample-row guard?")
    report = report.replace("Macro gain retained", "Macro gain")
    REPORT.write_text(report, encoding="utf-8")

    print(f"decision={audit['decision']}")
    print(f"block_count={audit['block_count']}")
    print(f"macro_gain={metrics['macro_gain']:.8f} fold_std_delta={metrics['fold_std_delta']:+.8f}")
    print(f"dest={DEST}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
