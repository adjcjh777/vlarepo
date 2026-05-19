#!/usr/bin/env python3
"""Prepare v121 class-selective clean Tsubasa sidecar candidate.

v121 refines v120 while v120 is pending.  Instead of blending the Tsubasa
sidecar globally, it applies a stronger sidecar only to a small class list
selected by train-window proxy evidence and only when the sidecar is
meaningfully above the clean anchor for that cell.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import shutil
from pathlib import Path


SOURCE_DIR = Path("birdclef-2026/notebooks/v103-guarded-macro-risk-rescue")
DEST_DIR = Path("birdclef-2026/notebooks/v121-class-selective-tsubasa")
NOTEBOOK = "submission.ipynb"
NEW_KERNEL_ID = "junhaochengadjcjh7u7/bc26-v121-class-selective-tsubasa"
NEW_TITLE = "bc26-v121-class-selective-tsubasa"
V120_SCRIPT = Path("birdclef-2026/scripts/birdclef_prepare_v120_clean_tsubasa_sidecar.py")

SELECTED_CLASSES = [
    "47158son13",
    "47158son15",
    "47158son16",
    "47158son21",
    "47158son22",
    "47158son23",
    "516975",
    "chacha1",
    "grekis",
    "plcjay1",
]


def _split_source(cell: dict) -> str:
    src = cell.get("source", "")
    if isinstance(src, list):
        return "".join(src)
    return str(src)


def _set_source(cell: dict, source: str) -> None:
    cell["source"] = source.splitlines(keepends=True)


def _load_v120_module():
    spec = importlib.util.spec_from_file_location("bc26_v120_prepare", V120_SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot import {V120_SCRIPT}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def patch_v121_notebook(path: Path) -> None:
    nb = json.loads(path.read_text())
    cells = nb["cells"]

    cells[0]["source"] = [
        "# BirdCLEF+ 2026 - V121 Original: Class-Selective Tsubasa Sidecar\n",
        "\n",
        "Provenance: this notebook refines the license-clean v120 line while v120 "
        "is pending. It still uses only the CC0 Tsubasa ConvNeXt SED fold as a "
        "sidecar, recomputes the Perch-only clean anchor inside the same "
        "CPU/no-internet notebook, and avoids prior output CSVs plus "
        "unknown-license SED/cache inputs.\n",
        "\n",
        "Original experiment: local proxy showed the global v120 sidecar improves "
        "macro but hurts top5. v121 uses a class-selective gate instead: only "
        "10 train-window-supported classes can receive the sidecar, and only in "
        "cells where `sidecar > clean_anchor + 0.02`; those cells use a "
        "`0.60 clean_anchor + 0.40 sidecar` blend. Run-mode only while v120 "
        "is pending; no real submission before v120 score is known.\n",
    ]

    for cell in cells:
        src = _split_source(cell)
        src = src.replace("V120", "V121").replace("v120", "v121")
        src = src.replace("bc26-v120-clean-tsubasa-sidecar", "bc26-v121-class-selective-tsubasa")
        src = src.replace("0.85 clean_anchor + 0.15 Tsubasa_sidecar", "class-selective Tsubasa sidecar")
        src = src.replace("v121_clean_tsubasa_branch_summary.csv", "v121_class_selective_tsubasa_summary.csv")
        _set_source(cell, src)

    final_idx = None
    for i, cell in enumerate(cells):
        src = _split_source(cell)
        if "v121_clean_anchor_probs = final_probs.copy()" in src:
            final_idx = i
            break
    if final_idx is None:
        raise ValueError("could not find v121 final blend cell")

    src = _split_source(cells[final_idx])
    start = src.index("v121_clean_anchor_probs = final_probs.copy()")
    replacement = f'''v121_clean_anchor_probs = final_probs.copy()
v121_selected_classes = {json.dumps(SELECTED_CLASSES)}
v121_selected_mask = np.array([label in set(v121_selected_classes) for label in PRIMARY_LABELS], dtype=bool)
v121_cell_gate = (
    v121_selected_mask.reshape(1, -1)
    & (v121_tsubasa_sidecar_probs > (v121_clean_anchor_probs + 0.02))
)
v121_mix = np.where(v121_cell_gate, 0.40, 0.0).astype(np.float32)
final_probs = ((1.0 - v121_mix) * v121_clean_anchor_probs + v121_mix * v121_tsubasa_sidecar_probs).astype(np.float32)
v121_branch_summary = pd.DataFrame(
    [
        {{
            "branch": "clean_anchor",
            "weight": "base",
            "min": float(v121_clean_anchor_probs.min()),
            "max": float(v121_clean_anchor_probs.max()),
            "mean": float(v121_clean_anchor_probs.mean()),
            "std": float(v121_clean_anchor_probs.std()),
        }},
        {{
            "branch": "tsubasa_sidecar",
            "weight": "gated",
            "min": float(v121_tsubasa_sidecar_probs.min()),
            "max": float(v121_tsubasa_sidecar_probs.max()),
            "mean": float(v121_tsubasa_sidecar_probs.mean()),
            "std": float(v121_tsubasa_sidecar_probs.std()),
        }},
        {{
            "branch": "v121_class_selective_blend",
            "weight": "0.40_on_gate",
            "min": float(final_probs.min()),
            "max": float(final_probs.max()),
            "mean": float(final_probs.mean()),
            "std": float(final_probs.std()),
        }},
    ]
)
v121_branch_summary.to_csv("v121_class_selective_tsubasa_summary.csv", index=False)
print(f"V121 selected sidecar classes: {{v121_selected_classes}}")
print(f"V121 sidecar gate cells: {{int(v121_cell_gate.sum())}} / {{v121_cell_gate.size}}")
print(f"V121 final blend: clean anchor base with 0.40 Tsubasa sidecar on gated cells")
print(f"V121 final score range: [{{final_probs.min():.6f}}, {{final_probs.max():.6f}}]")
print(f"V121 final score mean/std: {{final_probs.mean():.6f}}/{{final_probs.std():.6f}}")
'''
    _set_source(cells[final_idx], src[:start] + replacement)
    path.write_text(json.dumps(nb, ensure_ascii=False) + "\n")


def materialize(source_dir: Path, dest_dir: Path, overwrite: bool) -> None:
    if dest_dir.exists():
        if not overwrite:
            raise FileExistsError(dest_dir)
        shutil.rmtree(dest_dir)
    v120 = _load_v120_module()
    v120.materialize(source_dir, dest_dir, overwrite=False)

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
    patch_v121_notebook(dest_dir / NOTEBOOK)
    (dest_dir / "ATTRIBUTION.md").write_text(
        "\n".join(
            [
                "# Attribution",
                "",
                "This candidate continues the private original clean v110/v116/v120 line.",
                "",
                "Original v121 change:",
                "- uses the CC0 `tsubasatech/birdclef-2026-snowflake-sed` ConvNeXt ONNX fold as a class-selective sidecar;",
                "- recomputes a Perch-only clean anchor in the same notebook;",
                "- applies the sidecar only to 10 pre-declared train-window-supported classes and only when the sidecar exceeds the anchor by 0.02;",
                "- does not mount prior output CSVs or unknown-license SED/cache dependencies;",
                "- keeps CPU-only/no-internet metadata and writes class-selective branch diagnostics.",
                "",
                "Run-mode only while v120 real submission is pending.",
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
    print("NEXT: static audit and Kaggle Run-mode only; no real submit while v120 is pending.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
