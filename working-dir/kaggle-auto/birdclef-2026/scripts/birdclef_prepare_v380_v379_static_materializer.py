#!/usr/bin/env python3
"""Prepare v380 static materializer for the v379 deployable distillation route."""

from __future__ import annotations

import argparse
import importlib.util
import json
import shutil
import textwrap
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "birdclef-2026/notebooks/v107-rankceiling-perch-guarded"
DEST = ROOT / "birdclef-2026/notebooks/v380-v379-static-distill"
NOTEBOOK = "submission.ipynb"
NEW_KERNEL_ID = "junhaochengadjcjh7u7/bc26-v380-v379-static-distill"
NEW_TITLE = "bc26-v380-v379-static-distill"
V379_PATH = ROOT / "birdclef-2026/scripts/birdclef_probe_v379_v377_deployable_distill.py"
SPEC_PATH = ROOT / "experiments/v380_v379_static_distill_spec.json"
LOCAL_SUB = ROOT / "experiments/v380_v379_static_distill_local_submission.csv"
CSV = ROOT / "experiments/v380_v379_static_materializer_20260524.csv"
REPORT = ROOT / "experiments/v380_v379_static_materializer_20260524.md"
RUNTIME = ROOT / "artifacts/runtime_v380_v379_static_materializer_20260524.json"
LINEAGE = ROOT / "artifacts/lineage_v380_v379_static_materializer_20260524.json"
MARKER = "CODEX_V380_V379_STATIC_DISTILL_PATCH"
FOLLOWUP_LABELS = ["47158son17", "516975", "116570", "47158son25", "chacha1", "47158son10", "47158son21"]


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")


def load_v379():
    spec = importlib.util.spec_from_file_location("birdclef_probe_v379_v377_deployable_distill", V379_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {V379_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def fit_full_ridge(X: np.ndarray, y: np.ndarray, alpha: float) -> dict[str, list[float]]:
    mu = X.mean(axis=0)
    sigma = X.std(axis=0)
    sigma[sigma < 1e-8] = 1.0
    x_s = (X - mu) / sigma
    reg = np.eye(x_s.shape[1]) * alpha
    reg[0, 0] = 0.0
    beta = np.linalg.pinv(x_s.T @ x_s + reg) @ x_s.T @ y
    return {
        "mean": [float(x) for x in mu],
        "scale": [float(x) for x in sigma],
        "beta": [float(x) for x in beta],
    }


def build_spec_and_local_candidate() -> tuple[dict[str, object], dict[str, object], pd.DataFrame]:
    v379 = load_v379()
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
    meta = v379.row_features(anchor_df["row_id"].astype(str).tolist())
    prior = v379.prior_for_rows(meta, labels, class_names)
    anchor_rank = v379.column_rank01(anchor)
    prior_rank = v379.column_rank01(prior)
    temporal = v379.temporal_max(anchor, meta)
    oracle, _ = v379.v377_oracle(anchor, teacher, class_names)

    alpha = 0.01
    blend_weight = 0.70
    min_delta = 0.0
    min_prior_rank = 0.0
    class_index = {c: i for i, c in enumerate(class_names)}
    coefs: dict[str, dict[str, list[float]]] = {}
    local = anchor.copy()
    active_cells = 0
    for label in FOLLOWUP_LABELS:
        idx = class_index[label]
        X = v379.class_features(idx, anchor, anchor_rank, prior, prior_rank, temporal, meta)
        target_delta = np.maximum(oracle[:, idx] - anchor[:, idx], 0.0)
        coef = fit_full_ridge(X, target_delta, alpha)
        coefs[label] = coef
        source_delta = np.clip(((X - np.asarray(coef["mean"])) / np.asarray(coef["scale"])) @ np.asarray(coef["beta"]), 0.0, 1.0)
        source = np.clip(anchor[:, idx] + source_delta, 0.0, 1.0)
        mask = (source > anchor[:, idx] + min_delta) & (prior_rank[:, idx] >= min_prior_rank)
        if mask.any():
            local[mask, idx] = np.clip((1.0 - blend_weight) * local[mask, idx] + blend_weight * source[mask], 0.0, 1.0)
            active_cells += int(mask.sum())

    groups = v379.row_groups(anchor_df["row_id"])
    anchor_score = v379.score_values(y_true, anchor, class_names)
    local_score = v379.score_values(y_true, local, class_names)
    anchor_aucs = v379.per_class_auc(y_true, anchor)
    local_aucs = v379.per_class_auc(y_true, local)
    anchor_fold = v379.fold_stats(y_true, anchor, class_names, groups)
    local_fold = v379.fold_stats(y_true, local, class_names, groups)
    anchor_weak = v379.weak_mean(anchor_aucs, class_names, FOLLOWUP_LABELS)
    local_weak = v379.weak_mean(local_aucs, class_names, FOLLOWUP_LABELS)
    corr_anchor = float(np.corrcoef(anchor.ravel(), local.ravel())[0, 1])

    spec = {
        "patch_marker": MARKER,
        "source_route": "v107-rankceiling-perch-guarded",
        "candidate": "v380-v379-static-distill",
        "labels": FOLLOWUP_LABELS,
        "alpha": alpha,
        "target_mode": "delta",
        "blend_weight": blend_weight,
        "min_delta": min_delta,
        "min_prior_rank": min_prior_rank,
        "feature_names": [
            "bias",
            "anchor_value",
            "anchor_rank01",
            "site_hour_prior",
            "prior_rank01",
            "temporal_max",
            "temporal_delta",
            "anchor_x_prior_rank",
            "row_top1",
            "row_top1_minus_top2",
            "hour_sin",
            "hour_cos",
            "end_scaled",
        ],
        "coefs_by_class": coefs,
        "runtime_policy": "runtime uses only v107 submission, competition train_soundscapes_labels, sample row ids, and fixed coefficients",
    }
    metrics = {
        "active_cells": active_cells,
        "anchor_macro_auc": anchor_score["macro_auc"],
        "local_macro_auc": local_score["macro_auc"],
        "macro_gain": float(local_score["macro_auc"] - anchor_score["macro_auc"]),
        "anchor_top1_hit": anchor_score["top1_hit"],
        "local_top1_hit": local_score["top1_hit"],
        "anchor_top5_hit": anchor_score["top5_hit"],
        "local_top5_hit": local_score["top5_hit"],
        "anchor_fold_std": anchor_fold[1],
        "local_fold_std": local_fold[1],
        "fold_std_delta": float(local_fold[1] - anchor_fold[1]),
        "anchor_weak_followup_auc": anchor_weak,
        "local_weak_followup_auc": local_weak,
        "weak_followup_gain": float(local_weak - anchor_weak),
        "corr_vs_anchor": corr_anchor,
    }
    out_df = anchor_df[["row_id", *class_names]].copy()
    out_df[class_names] = local
    return spec, metrics, out_df


def notebook_patch_code(spec: dict[str, object]) -> str:
    payload = json.dumps(spec, sort_keys=True)
    return f'''

# {MARKER}
# Static deployable distillation layer for v379/v380. It uses only the
# v107-generated submission, competition train soundscape labels, row_id
# metadata, and fixed coefficients embedded below.
import json as _v380_json
import math as _v380_math
import re as _v380_re
from pathlib import Path as _V380Path

_V380_SPEC = _v380_json.loads({payload!r})
_V380_BASE = _V380Path("/kaggle/input/competitions/birdclef-2026")
if not _V380_BASE.exists():
    _V380_BASE = _V380Path("/kaggle/input/birdclef-2026")

_v380_sample = pd.read_csv(_V380_BASE / "sample_submission.csv")
_v380_sample["row_id"] = _v380_sample["row_id"].astype(str)
_v380_class_cols = [c for c in _v380_sample.columns if c != "row_id"]
_v380_anchor = pd.read_csv("submission.csv")
_v380_anchor["row_id"] = _v380_anchor["row_id"].astype(str)
if list(_v380_anchor.columns) != list(_v380_sample.columns):
    raise RuntimeError("v380 refuses to run: v107 anchor submission columns do not match sample")
if _v380_anchor["row_id"].tolist() != _v380_sample["row_id"].tolist():
    raise RuntimeError("v380 refuses to run: v107 anchor row order does not match sample")

def _v380_row_features(row_ids):
    rows = []
    pat = _v380_re.compile(r"^(?P<prefix>.+?)_(?P<site>S\\d+)_(?P<date>\\d{{8}})_(?P<time>\\d{{6}})_(?P<end>\\d+)$")
    for row_id in row_ids:
        m = pat.match(str(row_id))
        if m:
            hour = int(m.group("time")[:2])
            end = int(m.group("end"))
            site = m.group("site")
            file_stem = "_".join(str(row_id).split("_")[:-1])
        else:
            hour, end, site, file_stem = -1, -1, "SUNK", str(row_id)
        rows.append({{"row_id": row_id, "file_stem": file_stem, "site": site, "hour": hour, "end_sec": end}})
    return pd.DataFrame(rows)

def _v380_train_label_meta(labels, class_names):
    rows = []
    y_rows = []
    cidx = {{c: i for i, c in enumerate(class_names)}}
    pat_time = _v380_re.compile(r"\\d{{6}}$")
    for row in labels.itertuples(index=False):
        stem = _V380Path(str(row.filename)).stem
        parts = stem.split("_")
        site = next((p for p in parts if _v380_re.fullmatch(r"S\\d+", p)), "SUNK")
        hour = int(parts[-1][:2]) if parts and pat_time.match(parts[-1]) else -1
        try:
            end = int(str(row.end).split(":")[-1])
        except Exception:
            end = -1
        target = np.zeros(len(class_names), dtype=np.float32)
        for label in str(row.primary_label).split(";"):
            idx = cidx.get(label)
            if idx is not None:
                target[idx] = 1.0
        rows.append({{"file_stem": stem, "site": site, "hour": hour, "end_sec": end}})
        y_rows.append(target)
    return pd.DataFrame(rows), np.vstack(y_rows)

def _v380_prior_for_rows(meta, class_names):
    labels = pd.read_csv(_V380_BASE / "train_soundscapes_labels.csv")
    train_meta, y = _v380_train_label_meta(labels, class_names)
    global_p = y.mean(axis=0)
    site_values = train_meta["site"].astype(str).to_numpy()
    hour_values = train_meta["hour"].astype(int).to_numpy()
    out = np.zeros((len(meta), len(class_names)), dtype=np.float32)
    for i, row in meta.iterrows():
        same_site_hour = (site_values == str(row["site"])) & (hour_values == int(row["hour"]))
        same_site = site_values == str(row["site"])
        same_hour = hour_values == int(row["hour"])
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

def _v380_column_rank01(values):
    order = np.argsort(values, axis=0, kind="mergesort")
    ranks = np.empty_like(values, dtype=np.float32)
    col_idx = np.arange(values.shape[1])[None, :]
    rank_values = np.linspace(0.0, 1.0, values.shape[0], endpoint=True, dtype=np.float32)[:, None]
    ranks[order, col_idx] = rank_values
    return ranks

def _v380_temporal_max(values, meta):
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

def _v380_class_features(cls_idx, anchor, anchor_rank, prior, prior_rank, temporal, meta):
    top_order = np.argsort(anchor, axis=1)
    top1 = anchor[np.arange(anchor.shape[0]), top_order[:, -1]]
    top2 = anchor[np.arange(anchor.shape[0]), top_order[:, -2]]
    hour = meta["hour"].astype(float).to_numpy()
    end = meta["end_sec"].astype(float).to_numpy()
    hour_angle = np.where(hour >= 0, 2 * np.pi * hour / 24.0, 0.0)
    end_scaled = np.where(end >= 0, end / 60.0, 0.0)
    return np.column_stack([
        np.ones(anchor.shape[0], dtype=np.float32),
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
    ]).astype(np.float32)

_v380_values = _v380_anchor[_v380_class_cols].to_numpy(np.float32)
if not np.isfinite(_v380_values).all() or _v380_values.min() < 0 or _v380_values.max() > 1:
    raise RuntimeError("v380 refuses to run: anchor probabilities invalid")
_v380_meta = _v380_row_features(_v380_anchor["row_id"].astype(str).tolist())
_v380_prior = _v380_prior_for_rows(_v380_meta, _v380_class_cols)
_v380_anchor_rank = _v380_column_rank01(_v380_values)
_v380_prior_rank = _v380_column_rank01(_v380_prior)
_v380_temporal = _v380_temporal_max(_v380_values, _v380_meta)
_v380_out = _v380_values.copy()
_v380_class_index = {{c: i for i, c in enumerate(_v380_class_cols)}}
_v380_rows = []
for _v380_label in _V380_SPEC["labels"]:
    if _v380_label not in _v380_class_index:
        continue
    _v380_idx = _v380_class_index[_v380_label]
    _v380_coef = _V380_SPEC["coefs_by_class"][_v380_label]
    _v380_x = _v380_class_features(_v380_idx, _v380_values, _v380_anchor_rank, _v380_prior, _v380_prior_rank, _v380_temporal, _v380_meta)
    _v380_mean = np.asarray(_v380_coef["mean"], dtype=np.float32)
    _v380_scale = np.asarray(_v380_coef["scale"], dtype=np.float32)
    _v380_beta = np.asarray(_v380_coef["beta"], dtype=np.float32)
    _v380_delta = np.clip(((_v380_x - _v380_mean) / _v380_scale) @ _v380_beta, 0.0, 1.0)
    _v380_source = np.clip(_v380_values[:, _v380_idx] + _v380_delta, 0.0, 1.0)
    _v380_mask = (_v380_source > _v380_values[:, _v380_idx] + float(_V380_SPEC["min_delta"])) & (
        _v380_prior_rank[:, _v380_idx] >= float(_V380_SPEC["min_prior_rank"])
    )
    if _v380_mask.any():
        _v380_out[_v380_mask, _v380_idx] = np.clip(
            (1.0 - float(_V380_SPEC["blend_weight"])) * _v380_out[_v380_mask, _v380_idx]
            + float(_V380_SPEC["blend_weight"]) * _v380_source[_v380_mask],
            0.0,
            1.0,
        )
    _v380_rows.append({{
        "class_name": _v380_label,
        "active_rows": int(_v380_mask.sum()),
        "anchor_mean": float(_v380_values[:, _v380_idx].mean()),
        "final_mean": float(_v380_out[:, _v380_idx].mean()),
    }})

_v380_final = _v380_anchor.copy()
_v380_final[_v380_class_cols] = _v380_out
_v380_check = _v380_final[_v380_class_cols].to_numpy(np.float32)
if list(_v380_final.columns) != list(_v380_sample.columns):
    raise RuntimeError("v380 final column mismatch")
if _v380_final["row_id"].astype(str).tolist() != _v380_sample["row_id"].astype(str).tolist():
    raise RuntimeError("v380 final row order mismatch")
if not np.isfinite(_v380_check).all() or _v380_check.min() < 0 or _v380_check.max() > 1:
    raise RuntimeError("v380 final probabilities invalid")
_v380_anchor.to_csv("submission_v107_anchor.csv", index=False)
_v380_final.to_csv("submission.csv", index=False)
pd.DataFrame(_v380_rows).to_csv("v380_static_distill_summary.csv", index=False)
pd.DataFrame([{{"patch": "{MARKER}", "rows": len(_v380_final), "cols": len(_v380_final.columns), "active_cells": int(sum(r["active_rows"] for r in _v380_rows)), "min": float(_v380_check.min()), "max": float(_v380_check.max())}}]).to_csv("v380_static_distill_diagnostics.csv", index=False)
print("v380 static distill patch complete")
'''


def append_patch_cell(path: Path, spec: dict[str, object]) -> dict[str, object]:
    nb = json.loads(path.read_text(encoding="utf-8"))
    marker_count = sum(MARKER in "".join(cell.get("source", [])) for cell in nb.get("cells", []))
    if marker_count:
        return {"patched": True, "patch_marker_count": int(marker_count), "patch_mode": "already-present"}
    nb.setdefault("cells", []).append(
        {
            "cell_type": "code",
            "execution_count": None,
            "id": "v380-v379-static-distill",
            "metadata": {},
            "outputs": [],
            "source": notebook_patch_code(spec).splitlines(keepends=True),
        }
    )
    path.write_text(json.dumps(nb, indent=1) + "\n", encoding="utf-8")
    return {"patched": True, "patch_marker_count": 1, "patch_mode": "append-final-cell"}


def materialize(spec: dict[str, object], overwrite: bool) -> dict[str, object]:
    if DEST.exists():
        if not overwrite:
            raise FileExistsError(f"destination exists: {DEST}")
        shutil.rmtree(DEST)
    shutil.copytree(SRC, DEST)
    metadata_path = DEST / "kernel-metadata.json"
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    metadata.update(
        {
            "id": NEW_KERNEL_ID,
            "title": NEW_TITLE,
            "code_file": NOTEBOOK,
            "is_private": True,
            "enable_gpu": False,
            "enable_tpu": False,
            "enable_internet": False,
        }
    )
    metadata_path.write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    patch_info = append_patch_cell(DEST / NOTEBOOK, spec)
    (DEST / "ATTRIBUTION.md").write_text(
        textwrap.dedent(
            """
            # v380 v379 Static Distillation Attribution

            This candidate is an original derivative of the local v107
            license-clean Perch-only route. It preserves v107's declared
            public Perch inputs and appends a fixed-coefficient, CPU-only
            post-processing layer learned in the v379 local probe.

            The appended layer uses only the v107-generated submission,
            competition train soundscape labels, row_id-derived temporal
            metadata, and fixed coefficients embedded in the notebook. It
            does not read diagnostic teacher outputs at inference time.

            This materialization is for static audit only until a separate
            Run-mode gate authorizes any Kaggle push. It is not a real
            competition submission candidate by itself.
            """
        ).strip()
        + "\n",
        encoding="utf-8",
    )
    return {
        "source_dir": str(SRC),
        "dest_dir": str(DEST),
        "notebook": NOTEBOOK,
        "kernel_id": NEW_KERNEL_ID,
        "title": NEW_TITLE,
        **patch_info,
        "metadata": metadata,
    }


def static_audit(info: dict[str, object], spec: dict[str, object], local_metrics: dict[str, object]) -> dict[str, object]:
    nb_text = (DEST / NOTEBOOK).read_text(encoding="utf-8") if DEST.exists() else ""
    patch_cell_count = 0
    patch_text = ""
    if (DEST / NOTEBOOK).exists():
        nb = json.loads((DEST / NOTEBOOK).read_text(encoding="utf-8"))
        for cell in nb.get("cells", []):
            source = "".join(cell.get("source", []))
            if MARKER in source:
                patch_cell_count += 1
                patch_text += source
    metadata = info.get("metadata", {})
    dataset_sources = list(metadata.get("dataset_sources", [])) if isinstance(metadata, dict) else []
    model_sources = list(metadata.get("model_sources", [])) if isinstance(metadata, dict) else []
    checks = {
        "destination_exists": DEST.exists(),
        "notebook_exists": (DEST / NOTEBOOK).exists(),
        "metadata_exists": (DEST / "kernel-metadata.json").exists(),
        "attribution_exists": (DEST / "ATTRIBUTION.md").exists(),
        "marker_cell_once": patch_cell_count == 1,
        "cpu_disabled_gpu": metadata.get("enable_gpu") is False if isinstance(metadata, dict) else False,
        "cpu_disabled_tpu": metadata.get("enable_tpu") is False if isinstance(metadata, dict) else False,
        "internet_disabled": metadata.get("enable_internet") is False if isinstance(metadata, dict) else False,
        "competition_source": "birdclef-2026" in list(metadata.get("competition_sources", [])) if isinstance(metadata, dict) else False,
        "keeps_clean_dataset_sources": dataset_sources == ["rishikeshjani/perch-onnx-for-birdclef-2026"],
        "keeps_clean_model_sources": model_sources == ["google/bird-vocalization-classifier/TensorFlow2/perch_v2_cpu/1"],
        "no_unknown_metadata_sources": "jaejohn/perch-meta" not in dataset_sources and "tuckerarrants/bc2026-distilled-sed-public" not in dataset_sources,
        "no_unknown_patch_runtime_sources": "jaejohn/perch-meta" not in patch_text and "tuckerarrants/bc2026-distilled-sed-public" not in patch_text,
        "writes_submission_csv": "submission.csv" in patch_text,
        "writes_diagnostics": "v380_static_distill_diagnostics.csv" in patch_text,
        "row_order_guard": "row order mismatch" in patch_text,
        "range_guard": "probabilities invalid" in patch_text,
        "spec_has_all_labels": list(spec.get("labels", [])) == FOLLOWUP_LABELS,
        "local_no_top5_regression": float(local_metrics["local_top5_hit"]) >= float(local_metrics["anchor_top5_hit"]),
        "local_fold_std_not_worse": float(local_metrics["fold_std_delta"]) <= 0.0,
    }
    block_count = sum(not v for v in checks.values())
    if block_count:
        decision = "HOLD-v380-static-materializer-blocked-NO-PUSH-NO-SUBMIT"
        next_action = "Fix static materializer blockers before any Run-mode push."
    else:
        decision = "READY-v380-static-materializer-audit-NO-PUSH-NO-SUBMIT"
        next_action = "Build a guarded Run-mode push/audit pair only if a fresh submit-window and risk review authorizes it."
    return {
        "checks": checks,
        "block_count": block_count,
        "decision": decision,
        "next_recommended_action": next_action,
    }


def write_outputs(info: dict[str, object], spec: dict[str, object], metrics: dict[str, object], audit: dict[str, object], elapsed: float) -> None:
    updated = utc_now()
    SPEC_PATH.parent.mkdir(parents=True, exist_ok=True)
    SPEC_PATH.write_text(json.dumps(spec, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    RUNTIME.parent.mkdir(parents=True, exist_ok=True)
    runtime = {
        "timestamp_utc": updated,
        "elapsed_seconds": round(elapsed, 4),
        "experiment_id": "v380-v379-static-materializer",
        "materialization": {k: v for k, v in info.items() if k != "metadata"},
        "local_metrics": metrics,
        "audit": audit,
        "decision": audit["decision"],
    }
    RUNTIME.write_text(json.dumps(runtime, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    LINEAGE.write_text(
        json.dumps(
            {
                "timestamp_utc": updated,
                "source_notebook": str(SRC),
                "destination_notebook": str(DEST),
                "source_probe": str(V379_PATH),
                "spec": str(SPEC_PATH),
                "local_submission": str(LOCAL_SUB),
                "kernel_id": NEW_KERNEL_ID,
                "patch_marker": MARKER,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    row = {
        "experiment_id": "v380-v379-static-materializer",
        "updated_utc": updated,
        "source_dir": str(SRC),
        "dest_dir": str(DEST),
        "kernel_id": NEW_KERNEL_ID,
        "marker_count": int(audit["checks"]["marker_cell_once"]),
        "block_count": audit["block_count"],
        "local_macro_auc": metrics["local_macro_auc"],
        "macro_gain": metrics["macro_gain"],
        "local_top1_hit": metrics["local_top1_hit"],
        "local_top5_hit": metrics["local_top5_hit"],
        "fold_std_delta": metrics["fold_std_delta"],
        "weak_followup_gain": metrics["weak_followup_gain"],
        "corr_vs_anchor": metrics["corr_vs_anchor"],
        "decision": audit["decision"],
    }
    pd.DataFrame([row]).to_csv(CSV, index=False)
    checks_lines = "\n".join(f"- `{k}`: `{v}`" for k, v in audit["checks"].items())
    REPORT.write_text(
        textwrap.dedent(
            f"""
            # v380 v379 Static Materializer

            Updated: {updated}

            Status: `{audit['decision']}`.

            ## Research Question

            Can the v379 deployable-distill candidate be materialized as a
            static, CPU-only, no-internet v107 notebook patch with fixed
            coefficients and no diagnostic teacher runtime dependency?

            ## Implementation Summary

            - Source notebook: `{SRC}`
            - Destination notebook: `{DEST}`
            - Kernel id: `{NEW_KERNEL_ID}`
            - Patch marker: `{MARKER}`
            - Spec: `{SPEC_PATH}`
            - Local materialized submission: `{LOCAL_SUB}`
            - Runtime policy: `{spec['runtime_policy']}`

            ## Local Metrics

            - Macro: `{metrics['anchor_macro_auc']:.8f}` -> `{metrics['local_macro_auc']:.8f}` (`{metrics['macro_gain']:+.8f}`)
            - Top1: `{metrics['anchor_top1_hit']:.8f}` -> `{metrics['local_top1_hit']:.8f}`
            - Top5: `{metrics['anchor_top5_hit']:.8f}` -> `{metrics['local_top5_hit']:.8f}`
            - Fold std delta: `{metrics['fold_std_delta']:+.8f}`
            - Weak follow-up gain: `{metrics['weak_followup_gain']:+.8f}`
            - Corr vs anchor: `{metrics['corr_vs_anchor']:.8f}`

            ## Static Audit

            {checks_lines}

            ## Decision

            - `{audit['decision']}`
            - Next: {audit['next_recommended_action']}
            """
        ).strip()
        + "\n",
        encoding="utf-8",
    )


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--overwrite", action="store_true")
    args = ap.parse_args()
    started = time.time()
    spec, metrics, local_df = build_spec_and_local_candidate()
    LOCAL_SUB.parent.mkdir(parents=True, exist_ok=True)
    local_df.to_csv(LOCAL_SUB, index=False)
    info = materialize(spec, overwrite=args.overwrite)
    audit = static_audit(info, spec, metrics)
    write_outputs(info, spec, metrics, audit, time.time() - started)
    print(f"decision={audit['decision']}")
    print(f"block_count={audit['block_count']}")
    print(f"local_macro={metrics['local_macro_auc']:.8f} gain={metrics['macro_gain']:+.8f}")
    print(f"fold_std_delta={metrics['fold_std_delta']:+.8f} weak_gain={metrics['weak_followup_gain']:+.8f}")
    print(f"dest={DEST}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
