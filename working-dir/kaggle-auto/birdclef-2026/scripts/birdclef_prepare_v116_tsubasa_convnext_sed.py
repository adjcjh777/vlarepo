#!/usr/bin/env python3
"""Prepare v116 single-model Tsubasa ConvNeXt SED branch.

v115 proved that the two-model Snowflake SED ensemble can exceed Kaggle memory
when combined with the in-notebook Perch feature rebuild. v116 keeps the same
original remap/trust/EcoProto calibration layer but loads only the lighter
`sed_convnext-tiny_fold0.onnx` model from the CC0 Tsubasa dataset.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import shutil
from pathlib import Path


SOURCE_DIR = Path("birdclef-2026/notebooks/v103-guarded-macro-risk-rescue")
DEST_DIR = Path("birdclef-2026/notebooks/v116-tsubasa-convnext-sed")
NOTEBOOK = "submission.ipynb"
NEW_KERNEL_ID = "junhaochengadjcjh7u7/bc26-v116-tsubasa-convnext-sed"
NEW_TITLE = "bc26-v116-tsubasa-convnext-sed"
V115_SCRIPT = Path("birdclef-2026/scripts/birdclef_prepare_v115_tsubasa_snowflake_sed.py")


def _split_source(cell: dict) -> str:
    src = cell.get("source", "")
    if isinstance(src, list):
        return "".join(src)
    return str(src)


def _set_source(cell: dict, source: str) -> None:
    cell["source"] = source.splitlines(keepends=True)


def _load_v115_module():
    spec = importlib.util.spec_from_file_location("bc26_v115_prepare", V115_SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot import {V115_SCRIPT}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def patch_v116_notebook(path: Path) -> None:
    nb = json.loads(path.read_text())
    cells = nb["cells"]
    cells[0]["source"] = [
        "# BirdCLEF+ 2026 - V116 Original: Tsubasa ConvNeXt SED EcoProto\n",
        "\n",
        "Provenance: this notebook continues v115 but changes the resource profile. "
        "v115's two-model Snowflake SED ensemble exceeded Kaggle memory, so v116 "
        "keeps only `sed_convnext-tiny_fold0.onnx` from the same CC0 Tsubasa dataset. "
        "The train-window remap, trust-strength calibration, and EcoProto/rank-launch "
        "clean blend remain workspace-original.\n",
        "\n",
        "Run-mode only; do not submit unless runtime, schema, proxy, correlation, and "
        "compliance evidence pass.\n",
    ]
    for cell in cells:
        src = _split_source(cell)
        src = src.replace("V115", "V116").replace("v115", "v116")
        src = src.replace("Snowflake SED ensemble size", "Tsubasa ConvNeXt SED ensemble size")
        src = src.replace(
            'SNOWFLAKE_MODEL_NAMES = [\n    "sed_convnext-tiny_fold0.onnx",\n    "sed_tf-efficientnetv2-m_fold0.onnx",\n]',
            'SNOWFLAKE_MODEL_NAMES = [\n    "sed_convnext-tiny_fold0.onnx",\n]',
        )
        src = src.replace("two-model Snowflake SED ONNX ensemble", "single ConvNeXt Snowflake SED ONNX branch")
        src = src.replace("ensembles `sed_convnext-tiny_fold0.onnx` and `sed_tf-efficientnetv2-m_fold0.onnx`", "uses only `sed_convnext-tiny_fold0.onnx`")
        src = src.replace("v116_snowflake_sed_remap_diagnostics.csv", "v116_tsubasa_convnext_sed_remap_diagnostics.csv")
        _set_source(cell, src)
    path.write_text(json.dumps(nb, ensure_ascii=False) + "\n")


def materialize(source_dir: Path, dest_dir: Path, overwrite: bool) -> None:
    if dest_dir.exists():
        if not overwrite:
            raise FileExistsError(dest_dir)
        shutil.rmtree(dest_dir)
    v115 = _load_v115_module()
    v115.materialize(source_dir, dest_dir, overwrite=False)

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
    patch_v116_notebook(dest_dir / NOTEBOOK)
    (dest_dir / "ATTRIBUTION.md").write_text(
        "\n".join(
            [
                "# Attribution",
                "",
                "This candidate continues the private original v86/v102/v103 and clean v110-v115 line.",
                "",
                "Original v116 change:",
                "- keeps the CC0 `tsubasatech/birdclef-2026-snowflake-sed` source;",
                "- uses only `sed_convnext-tiny_fold0.onnx` after v115's two-model ensemble exceeded Kaggle memory;",
                "- preserves the workspace-original train-window remap and trust-strength calibration;",
                "- rebuilds train Perch features inside the notebook and avoids unknown-license Perch/SED caches;",
                "- keeps CPU-only/no-internet metadata.",
                "",
                "Run-mode only until v116 runtime, schema, proxy, correlation, and compliance evidence pass.",
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
