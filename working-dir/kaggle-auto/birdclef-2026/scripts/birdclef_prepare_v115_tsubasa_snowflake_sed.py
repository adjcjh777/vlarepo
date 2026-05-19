#!/usr/bin/env python3
"""Prepare v115 Tsubasa Snowflake SED EcoProto branch.

v115 continues the license-clean v110-v114 line with a new CC0 SED source:

    tsubasatech/birdclef-2026-snowflake-sed

The notebook reuses the v112 clean-SED remap/EcoProto scaffold, but swaps the
raw-audio SED input to a two-model Snowflake ONNX ensemble. It keeps the
train-window column remap and trust-strength layer so this remains an original,
auditable calibration step rather than a blind public-source copy.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import shutil
from pathlib import Path


SOURCE_DIR = Path("birdclef-2026/notebooks/v103-guarded-macro-risk-rescue")
DEST_DIR = Path("birdclef-2026/notebooks/v115-tsubasa-snowflake-sed")
NOTEBOOK = "submission.ipynb"
NEW_KERNEL_ID = "junhaochengadjcjh7u7/bc26-v115-tsubasa-snowflake-sed"
NEW_TITLE = "bc26-v115-tsubasa-snowflake-sed"
V112_SCRIPT = Path("birdclef-2026/scripts/birdclef_prepare_v112_clean_sed_remap_ecoproto.py")


def _split_source(cell: dict) -> str:
    src = cell.get("source", "")
    if isinstance(src, list):
        return "".join(src)
    return str(src)


def _set_source(cell: dict, source: str) -> None:
    cell["source"] = source.splitlines(keepends=True)


def _load_v112_module():
    spec = importlib.util.spec_from_file_location("bc26_v112_prepare", V112_SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot import {V112_SCRIPT}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _snowflake_setup_source() -> str:
    return """# V115: audited CC0 Tsubasa Snowflake SED ensemble.
SNOWFLAKE_ROOT = Path("/kaggle/input/datasets/tsubasatech/birdclef-2026-snowflake-sed")
SNOWFLAKE_MODEL_NAMES = [
    "sed_convnext-tiny_fold0.onnx",
    "sed_tf-efficientnetv2-m_fold0.onnx",
]
CLEAN_SED_PATHS = []
for model_name in SNOWFLAKE_MODEL_NAMES:
    cand = SNOWFLAKE_ROOT / model_name
    if not cand.exists():
        hits = sorted(Path("/kaggle/input").rglob(model_name))
        if not hits:
            raise FileNotFoundError(f"No Snowflake SED ONNX model found: {model_name}")
        cand = hits[0]
    CLEAN_SED_PATHS.append(cand)

sed_opts = ort.SessionOptions()
sed_opts.intra_op_num_threads = 4
sed_opts.inter_op_num_threads = 1
sed_opts.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
clean_sed_sessions = []
for sed_path in CLEAN_SED_PATHS:
    sess = ort.InferenceSession(str(sed_path), sess_options=sed_opts, providers=["CPUExecutionProvider"])
    input_name = sess.get_inputs()[0].name
    out_map = {o.name: i for i, o in enumerate(sess.get_outputs())}
    clean_sed_sessions.append((sess, input_name, out_map, sed_path))
    print("Using V115 Snowflake SED:", sed_path)
    print("Snowflake SED inputs:", [(x.name, x.shape, x.type) for x in sess.get_inputs()])
    print("Snowflake SED outputs:", [(x.name, x.shape, x.type) for x in sess.get_outputs()])
print(f"V115 Snowflake SED ensemble size: {len(clean_sed_sessions)}")
"""


def _patch_helper_source(source: str) -> str:
    start_token = "            outs = clean_sed_session.run(None, {clean_sed_input_name: x})\n"
    end_token = "            del x, logits, outs, audio_batch"
    new = """            logits_acc = None
            for sess, input_name, out_map, sed_path in clean_sed_sessions:
                outs = sess.run(None, {input_name: x})
                out_idx = out_map.get("clip_logits", out_map.get("logits", 0))
                logits = outs[out_idx].astype(np.float32)
                if logits.shape[1] != N_CLASSES:
                    raise ValueError(f"Snowflake SED class mismatch for {sed_path}: {logits.shape[1]} vs {N_CLASSES}")
                logits_acc = logits if logits_acc is None else logits_acc + logits
            logits = (logits_acc / max(1, len(clean_sed_sessions))).astype(np.float32)
            logits_out[br:w] = logits
            del x, logits, logits_acc, outs, audio_batch"""
    start = source.find(start_token)
    end = source.find(end_token, start)
    if start < 0 or end < 0:
        raise ValueError("Could not patch clean SED helper inference block")
    end += len(end_token)
    return source[:start] + new + source[end:]


def patch_v115_notebook(path: Path) -> None:
    nb = json.loads(path.read_text())
    cells = nb["cells"]

    cells[0]["source"] = [
        "# BirdCLEF+ 2026 - V115 Original: Tsubasa Snowflake SED EcoProto\n",
        "\n",
        "Provenance: this notebook continues the private original v86/v102/v103 and "
        "license-clean v110-v114 line. It removes the unknown-license `jaejohn/perch-meta` "
        "and `tuckerarrants/bc2026-distilled-sed-public` dependencies, rebuilds train "
        "Perch features in-notebook, and uses `tsubasatech/birdclef-2026-snowflake-sed` "
        "(CC0-1.0) as the clean raw-audio SED source.\n",
        "\n",
        "Original experiment: v115 runs a two-model Snowflake SED ONNX ensemble and then "
        "applies the workspace-original train-window column remap plus trust-strength "
        "calibration before the EcoProto/rank-launch clean blend. Run-mode only; do not "
        "submit unless runtime, schema, proxy, correlation, and compliance evidence pass.\n",
    ]

    for cell in cells:
        src = _split_source(cell)
        src = src.replace("V112", "V115").replace("v112", "v115")
        src = src.replace("backtracking/birdclef2026-clean-sed-b0", "tsubasatech/birdclef-2026-snowflake-sed")
        src = src.replace("Clean SED", "Snowflake SED")
        src = src.replace("clean SED", "Snowflake SED")
        src = src.replace("clean_sed_remap", "snowflake_sed_remap")
        src = src.replace("v115_Snowflake_sed_remap_diagnostics.csv", "v115_snowflake_sed_remap_diagnostics.csv")
        _set_source(cell, src)

    for cell in cells:
        src = _split_source(cell)
        if "SNOWFLAKE_MODEL_NAMES" in src or "CLEAN_SED_PATH" in src:
            _set_source(cell, _snowflake_setup_source())
            break
    else:
        raise ValueError("Could not find SED setup cell")

    for cell in cells:
        src = _split_source(cell)
        if "def run_Snowflake_sed_fast" in src or "def run_clean_sed_fast" in src:
            src = src.replace("def run_Snowflake_sed_fast", "def run_clean_sed_fast")
            src = _patch_helper_source(src)
            _set_source(cell, src)
            break
    else:
        raise ValueError("Could not find SED helper cell")

    # Keep function/variable names expected by downstream cells stable after the
    # cosmetic text replacement above.
    for cell in cells:
        src = _split_source(cell)
        src = src.replace("run_Snowflake_sed_fast", "run_clean_sed_fast")
        src = src.replace("Snowflake_sed_meta", "clean_sed_meta")
        src = src.replace("Snowflake_sed_train_logits", "clean_sed_train_logits")
        src = src.replace("Snowflake_sed_test_logits", "clean_sed_test_logits")
        src = src.replace("raw_Snowflake_sed_train_probs", "raw_clean_sed_train_probs")
        src = src.replace("raw_Snowflake_sed_test_probs", "raw_clean_sed_test_probs")
        _set_source(cell, src)

    path.write_text(json.dumps(nb, ensure_ascii=False) + "\n")


def materialize(source_dir: Path, dest_dir: Path, overwrite: bool) -> None:
    if dest_dir.exists():
        if not overwrite:
            raise FileExistsError(dest_dir)
        shutil.rmtree(dest_dir)

    v112 = _load_v112_module()
    v112.materialize(source_dir, dest_dir, overwrite=False)

    meta_path = dest_dir / "kernel-metadata.json"
    meta = json.loads(meta_path.read_text())
    meta.update(
        {
            "id": NEW_KERNEL_ID,
            "title": NEW_TITLE,
            "code_file": NOTEBOOK,
            "is_private": True,
            "enable_gpu": False,
            "enable_tpu": False,
            "enable_internet": False,
            "dataset_sources": [
                "rishikeshjani/perch-onnx-for-birdclef-2026",
                "tsubasatech/birdclef-2026-snowflake-sed",
            ],
            "kernel_sources": [],
            "competition_sources": ["birdclef-2026"],
            "model_sources": [
                "google/bird-vocalization-classifier/TensorFlow2/perch_v2_cpu/1"
            ],
        }
    )
    meta_path.write_text(json.dumps(meta, indent=2) + "\n")

    patch_v115_notebook(dest_dir / NOTEBOOK)
    (dest_dir / "ATTRIBUTION.md").write_text(
        "\n".join(
            [
                "# Attribution",
                "",
                "This candidate continues the private original v86/v102/v103 and clean v110-v114 line.",
                "",
                "Original v115 change:",
                "- uses the CC0 `tsubasatech/birdclef-2026-snowflake-sed` ONNX dataset;",
                "- ensembles `sed_convnext-tiny_fold0.onnx` and `sed_tf-efficientnetv2-m_fold0.onnx` inside the notebook;",
                "- keeps the workspace-original train-window column remap and trust-strength calibration from v112;",
                "- rebuilds train Perch features inside the Kaggle notebook instead of using `jaejohn/perch-meta`;",
                "- avoids `tuckerarrants/bc2026-distilled-sed-public`;",
                "- keeps CPU-only/no-internet metadata and emits class-level remap diagnostics.",
                "",
                "Run-mode only until v115 runtime, schema, proxy, correlation, and compliance evidence pass.",
                "",
            ]
        )
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-dir", type=Path, default=SOURCE_DIR)
    parser.add_argument("--dest-dir", type=Path, default=DEST_DIR)
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()
    print("source_dir=", args.source_dir)
    print("dest_dir=", args.dest_dir)
    print("new_kernel_id=", NEW_KERNEL_ID)
    print("execute=", args.execute)
    if not args.execute:
        print("DRY_RUN: no files written.")
        return 0
    materialize(args.source_dir, args.dest_dir, args.overwrite)
    print("MATERIALIZED:", args.dest_dir)
    print("NEXT: static audit, Kaggle Run-mode push only, then compliance report.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
