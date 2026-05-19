#!/usr/bin/env python3
"""Prepare v122 single-pass class-selective Tsubasa sidecar candidate.

v120/v121 showed that a clean Perch anchor plus a Tsubasa sidecar can improve
the local proxy, but v120 failed hidden-test evaluation with a RAM error after
recomputing the expensive final layer twice.  v122 keeps v121's original sparse
class gate, moves it before the final EcoProto/rank-launch layer, and lets the
final layer run exactly once.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import shutil
from pathlib import Path


SOURCE_DIR = Path("birdclef-2026/notebooks/v103-guarded-macro-risk-rescue")
DEST_DIR = Path("birdclef-2026/notebooks/v122-singlepass-class-selective-tsubasa")
NOTEBOOK = "submission.ipynb"
NEW_KERNEL_ID = "junhaochengadjcjh7u7/bc26-v122-singlepass-cls-tsubasa"
NEW_TITLE = "bc26-v122-singlepass-cls-tsubasa"
V116_SCRIPT = Path("birdclef-2026/scripts/birdclef_prepare_v116_tsubasa_convnext_sed.py")

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


def _load_v116_module():
    spec = importlib.util.spec_from_file_location("bc26_v116_prepare", V116_SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot import {V116_SCRIPT}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def patch_v122_notebook(path: Path) -> None:
    nb = json.loads(path.read_text())
    cells = nb["cells"]

    cells[0]["source"] = [
        "# BirdCLEF+ 2026 - V122 Original: Single-Pass Class-Selective Tsubasa\n",
        "\n",
        "Provenance: this notebook continues the license-clean v116/v120/v121 "
        "line after v120 failed hidden-test evaluation with a RAM error. It "
        "uses the CC0 Tsubasa ConvNeXt SED fold only as a sparse evidence "
        "source and keeps CPU-only/no-internet metadata.\n",
        "\n",
        "Original experiment: v121's class-selective sidecar improved the local "
        "proxy, but v120/v121 recomputed the final decision layer twice. v122 "
        "moves the same 10-class margin gate into the SED probability view "
        "before EcoProto/rank-launch, then runs the final layer once. This is "
        "the memory-reduced follow-up required before any real submission.\n",
    ]

    for cell in cells:
        src = _split_source(cell)
        src = src.replace("V116", "V122").replace("v116", "v122")
        src = src.replace("bc26-v116-tsubasa-convnext-sed", "bc26-v122-singlepass-cls-tsubasa")
        src = src.replace("v122_tsubasa_convnext_sed_remap_diagnostics.csv", "v122_singlepass_tsubasa_remap_diagnostics.csv")
        _set_source(cell, src)

    remap_idx = None
    for i, cell in enumerate(cells):
        src = _split_source(cell)
        if "sed_probs = ((1.0 - rank_mix) * sed_test_view + rank_mix * rank_view)" in src:
            remap_idx = i
            break
    if remap_idx is None:
        raise ValueError("could not find v122 SED remap cell")

    src = _split_source(cells[remap_idx])
    marker = 'print("V122 remap diagnostics saved: v122_singlepass_tsubasa_remap_diagnostics.csv")\n'
    if marker not in src:
        raise ValueError("could not find remap diagnostic marker")
    hybrid = f'''

# V122 memory-reduced innovation: inject the v121 class-selective Tsubasa
# evidence before the expensive final layer, then run that final layer once.
v122_tsubasa_sed_probs = sed_probs.copy()
v122_tsubasa_sed_auc = sed_per_class_auc.copy()
v122_clean_sed_probs = (1.0 / (1.0 + np.exp(-np.clip(scores_test, -50, 50)))).astype(np.float32)
v122_clean_sed_auc = np.nan_to_num(per_class_auc_cal, nan=0.50).astype(np.float32)
v122_selected_classes = {json.dumps(SELECTED_CLASSES)}
v122_selected_set = set(v122_selected_classes)
v122_selected_mask = np.array([label in v122_selected_set for label in PRIMARY_LABELS], dtype=bool)
v122_cell_gate = (
    v122_selected_mask.reshape(1, -1)
    & (v122_tsubasa_sed_probs > (v122_clean_sed_probs + 0.02))
)
v122_mix = np.where(v122_cell_gate, 0.40, 0.0).astype(np.float32)
sed_probs = ((1.0 - v122_mix) * v122_clean_sed_probs + v122_mix * v122_tsubasa_sed_probs).astype(np.float32)
sed_per_class_auc = np.where(
    v122_selected_mask,
    np.maximum(v122_clean_sed_auc, np.nan_to_num(v122_tsubasa_sed_auc, nan=0.50)),
    v122_clean_sed_auc,
).astype(np.float32)
v122_singlepass_summary = pd.DataFrame(
    [
        {{
            "branch": "clean_sed_surrogate",
            "role": "base",
            "min": float(v122_clean_sed_probs.min()),
            "max": float(v122_clean_sed_probs.max()),
            "mean": float(v122_clean_sed_probs.mean()),
            "std": float(v122_clean_sed_probs.std()),
        }},
        {{
            "branch": "tsubasa_sed_view",
            "role": "gated_sidecar",
            "min": float(v122_tsubasa_sed_probs.min()),
            "max": float(v122_tsubasa_sed_probs.max()),
            "mean": float(v122_tsubasa_sed_probs.mean()),
            "std": float(v122_tsubasa_sed_probs.std()),
        }},
        {{
            "branch": "v122_singlepass_hybrid_sed",
            "role": "final_layer_input",
            "min": float(sed_probs.min()),
            "max": float(sed_probs.max()),
            "mean": float(sed_probs.mean()),
            "std": float(sed_probs.std()),
        }},
    ]
)
v122_singlepass_summary.to_csv("v122_singlepass_tsubasa_summary.csv", index=False)
print(f"V122 selected sidecar classes: {{v122_selected_classes}}")
print(f"V122 pre-final sidecar gate cells: {{int(v122_cell_gate.sum())}} / {{v122_cell_gate.size}}")
print("V122 final layer mode: single pass after SED-level hybridization")
print(f"V122 hybrid SED range: [{{sed_probs.min():.6f}}, {{sed_probs.max():.6f}}]")
print(f"V122 hybrid SED mean/std: {{sed_probs.mean():.6f}}/{{sed_probs.std():.6f}}")

import gc
del v122_tsubasa_sed_probs, v122_clean_sed_probs, v122_mix, v122_cell_gate
gc.collect()
'''
    _set_source(cells[remap_idx], src.replace(marker, marker + hybrid))

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
    patch_v122_notebook(dest_dir / NOTEBOOK)
    (dest_dir / "ATTRIBUTION.md").write_text(
        "\n".join(
            [
                "# Attribution",
                "",
                "This candidate continues the private original clean v110/v116/v120/v121 line.",
                "",
                "Original v122 change:",
                "- preserves v121's 10-class Tsubasa sidecar gate;",
                "- moves the sidecar blend before the EcoProto/rank-launch final layer;",
                "- runs the expensive final layer once instead of recomputing clean and sidecar finals;",
                "- uses only CC0 Tsubasa and CC0 Perch ONNX dataset inputs plus the Google Perch model source;",
                "- does not mount prior output CSVs or unknown-license SED/cache dependencies;",
                "- keeps CPU-only/no-internet metadata and writes single-pass diagnostics.",
                "",
                "Run-mode only until v122 runtime, schema, proxy, correlation, memory-risk, and compliance evidence pass.",
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
    print("NEXT: static audit and Kaggle Run-mode only; no real submit before evidence review.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
