#!/usr/bin/env python3
"""Prepare v120 clean anchor plus Tsubasa sidecar blend.

v120 converts the v116 negative result into a controlled diversity sidecar.
The same Kaggle notebook first computes the CC0 Tsubasa ConvNeXt SED branch,
then switches the SED view back to the Perch-only clean surrogate to recompute
a v110-like clean anchor. The final prediction is a light probability blend:
0.85 clean anchor + 0.15 Tsubasa sidecar.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import shutil
from pathlib import Path


SOURCE_DIR = Path("birdclef-2026/notebooks/v103-guarded-macro-risk-rescue")
DEST_DIR = Path("birdclef-2026/notebooks/v120-clean-tsubasa-sidecar")
NOTEBOOK = "submission.ipynb"
NEW_KERNEL_ID = "junhaochengadjcjh7u7/bc26-v120-clean-tsubasa-sidecar"
NEW_TITLE = "bc26-v120-clean-tsubasa-sidecar"
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


def patch_v120_notebook(path: Path) -> None:
    nb = json.loads(path.read_text())
    cells = nb["cells"]

    cells[0]["source"] = [
        "# BirdCLEF+ 2026 - V120 Original: Clean Anchor + Tsubasa Sidecar\n",
        "\n",
        "Provenance: this notebook continues the license-clean v110/v116 line. "
        "It uses the CC0 `tsubasatech/birdclef-2026-snowflake-sed` ConvNeXt SED "
        "fold only as a low-correlation sidecar, then recomputes a Perch-only "
        "clean anchor inside the same CPU/no-internet notebook.\n",
        "\n",
        "Original experiment: local proxy showed that v116 alone is weak but "
        "complementary. v120 therefore uses a constrained `0.85 clean_anchor + "
        "0.15 Tsubasa_sidecar` probability blend, with no prior output CSVs or "
        "unknown-license SED/cache inputs mounted at runtime. Run-mode only; do "
        "not submit unless runtime, schema, proxy, correlation, and compliance "
        "evidence pass.\n",
    ]

    for cell in cells:
        src = _split_source(cell)
        src = src.replace("V116", "V120").replace("v116", "v120")
        src = src.replace("bc26-v116-tsubasa-convnext-sed", "bc26-v120-clean-tsubasa-sidecar")
        src = src.replace("v120_tsubasa_convnext_sed_remap_diagnostics.csv", "v120_tsubasa_sidecar_remap_diagnostics.csv")
        _set_source(cell, src)

    final_idx = None
    for i, cell in enumerate(cells):
        src = _split_source(cell)
        if "final_probs = (0.40 * v107_like_probs + 0.60 * v109_like_probs)" in src:
            final_idx = i
            break
    if final_idx is None:
        raise ValueError("could not find final probability cell")

    original_final = _split_source(cells[final_idx])
    clean_anchor_final = original_final.replace("V120", "V120 clean-anchor")
    blend_tail = r'''
v120_tsubasa_sidecar_probs = final_probs.copy()
print(
    f"V120 captured Tsubasa sidecar: "
    f"range=[{v120_tsubasa_sidecar_probs.min():.6f}, {v120_tsubasa_sidecar_probs.max():.6f}], "
    f"mean/std={v120_tsubasa_sidecar_probs.mean():.6f}/{v120_tsubasa_sidecar_probs.std():.6f}"
)

# Recompute a v110-like clean anchor without external SED/cache inputs.  This
# keeps the Tsubasa branch as a small sidecar rather than letting it define the
# anchor distribution.
sed_per_class_auc = np.nan_to_num(per_class_auc_cal, nan=0.50).astype(np.float32)
sed_probs = (1.0 / (1.0 + np.exp(-np.clip(scores_test, -50, 50)))).astype(np.float32)
print(
    f"V120 clean-anchor Perch surrogate SED view: "
    f"shape={sed_probs.shape}, range=[{sed_probs.min():.6f}, {sed_probs.max():.6f}]"
)
'''
    final_blend = r'''
v120_clean_anchor_probs = final_probs.copy()
final_probs = (0.85 * v120_clean_anchor_probs + 0.15 * v120_tsubasa_sidecar_probs).astype(np.float32)
v120_branch_summary = pd.DataFrame(
    [
        {
            "branch": "clean_anchor",
            "weight": 0.85,
            "min": float(v120_clean_anchor_probs.min()),
            "max": float(v120_clean_anchor_probs.max()),
            "mean": float(v120_clean_anchor_probs.mean()),
            "std": float(v120_clean_anchor_probs.std()),
        },
        {
            "branch": "tsubasa_sidecar",
            "weight": 0.15,
            "min": float(v120_tsubasa_sidecar_probs.min()),
            "max": float(v120_tsubasa_sidecar_probs.max()),
            "mean": float(v120_tsubasa_sidecar_probs.mean()),
            "std": float(v120_tsubasa_sidecar_probs.std()),
        },
        {
            "branch": "v120_blend",
            "weight": 1.00,
            "min": float(final_probs.min()),
            "max": float(final_probs.max()),
            "mean": float(final_probs.mean()),
            "std": float(final_probs.std()),
        },
    ]
)
v120_branch_summary.to_csv("v120_clean_tsubasa_branch_summary.csv", index=False)
print("V120 final blend weights: clean_anchor=0.85, tsubasa_sidecar=0.15")
print(f"V120 final score range: [{final_probs.min():.6f}, {final_probs.max():.6f}]")
print(f"V120 final score mean/std: {final_probs.mean():.6f}/{final_probs.std():.6f}")
'''
    _set_source(cells[final_idx], original_final + blend_tail + clean_anchor_final + final_blend)
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
    patch_v120_notebook(dest_dir / NOTEBOOK)
    (dest_dir / "ATTRIBUTION.md").write_text(
        "\n".join(
            [
                "# Attribution",
                "",
                "This candidate continues the private original clean v110/v116 line.",
                "",
                "Original v120 change:",
                "- uses the CC0 `tsubasatech/birdclef-2026-snowflake-sed` ConvNeXt ONNX fold as a low-correlation sidecar;",
                "- recomputes a Perch-only clean anchor in the same notebook;",
                "- emits a constrained `0.85 clean_anchor + 0.15 Tsubasa_sidecar` probability blend;",
                "- does not mount prior output CSVs or unknown-license SED/cache dependencies;",
                "- keeps CPU-only/no-internet metadata and writes branch summary diagnostics.",
                "",
                "Run-mode only until v120 runtime, schema, proxy, correlation, and compliance evidence pass.",
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
