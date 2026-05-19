#!/usr/bin/env python3
"""Prepare v117 conservative Tsubasa ConvNeXt SED branch.

v116 showed that the CC0 Tsubasa ConvNeXt SED source is CPU-runnable and
materially different, but its train-window column remap was too aggressive.
v117 keeps the same source and final clean-branch scaffold, but disables output
column remapping so we can isolate the raw same-index SED signal.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import shutil
from pathlib import Path


SOURCE_DIR = Path("birdclef-2026/notebooks/v103-guarded-macro-risk-rescue")
DEST_DIR = Path("birdclef-2026/notebooks/v117-tsubasa-convnext-noremap")
NOTEBOOK = "submission.ipynb"
NEW_KERNEL_ID = "junhaochengadjcjh7u7/bc26-v117-tsubasa-convnext-noremap"
NEW_TITLE = "bc26-v117-tsubasa-convnext-noremap"
V116_SCRIPT = Path("birdclef-2026/scripts/birdclef_prepare_v116_tsubasa_convnext_sed.py")


def _split_source(cell: dict) -> str:
    src = cell.get("source", "")
    if isinstance(src, list):
        return "".join(src)
    return str(src)


def _set_source(cell: dict, source: str) -> None:
    cell["source"] = source.splitlines(keepends=True)


def _load_v116_module():
    spec = importlib.util.spec_from_file_location("bc26_v116_prepare", V116_SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot import {V116_SCRIPT}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def patch_v117_notebook(path: Path) -> None:
    nb = json.loads(path.read_text())
    cells = nb["cells"]
    cells[0]["source"] = [
        "# BirdCLEF+ 2026 - V117 Original: Tsubasa ConvNeXt SED No-Remap\n",
        "\n",
        "Provenance: this notebook continues v116 after its remap-heavy branch "
        "collapsed on the local proxy. v117 keeps the CC0 Tsubasa ConvNeXt SED "
        "source but disables output-column remapping, retaining only same-index "
        "SED probabilities plus a light row-rank stabilizer inside the existing "
        "EcoProto clean-blend scaffold.\n",
        "\n",
        "Run-mode only; do not submit unless runtime, schema, proxy, correlation, "
        "and compliance evidence pass.\n",
    ]
    for cell in cells:
        src = _split_source(cell).replace("V116", "V117").replace("v116", "v117")
        src = src.replace("v117_tsubasa_convnext_sed_remap_diagnostics.csv", "v117_tsubasa_convnext_noremap_diagnostics.csv")
        marker = 'same_view_train = raw_clean_sed_train_probs\n'
        if marker in src and "remap_strength[:] = 0.0" not in src:
            src = src.replace(
                marker,
                "# V117 conservative isolation: disable train-window output-column remap.\n"
                "remap_cols = identity_cols.copy()\n"
                "remap_strength[:] = 0.0\n"
                "same_view_train = raw_clean_sed_train_probs\n",
            )
            src = src.replace(
                'rank_mix = (0.18 + 0.42 * remap_strength).reshape(1, -1).astype(np.float32)',
                'rank_mix = np.full((1, N_CLASSES), 0.08, dtype=np.float32)',
            )
        _set_source(cell, src)
    path.write_text(json.dumps(nb, ensure_ascii=False) + "\n")


def materialize(source_dir: Path, dest_dir: Path, overwrite: bool) -> None:
    if dest_dir.exists():
        if not overwrite:
            raise FileExistsError(dest_dir)
        shutil.rmtree(dest_dir)
    v116 = _load_v116_module()
    v116.materialize(source_dir, dest_dir, overwrite=False)

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
    patch_v117_notebook(dest_dir / NOTEBOOK)
    (dest_dir / "ATTRIBUTION.md").write_text(
        "\n".join(
            [
                "# Attribution",
                "",
                "This candidate continues the private original v86/v102/v103 and clean v110-v116 line.",
                "",
                "Original v117 change:",
                "- keeps the CC0 Tsubasa ConvNeXt SED source from v116;",
                "- disables the v116 output-column remap after it collapsed local proxy quality;",
                "- keeps a light same-index SED rank stabilizer plus the existing EcoProto clean blend;",
                "- preserves CPU-only/no-internet metadata and avoids unknown-license Perch/SED caches.",
                "",
                "Run-mode only until v117 runtime, schema, proxy, correlation, and compliance evidence pass.",
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
