#!/usr/bin/env python3
"""Prepare v123 rank-calibrated single-pass Tsubasa sidecar candidate.

v122 fixed the v120/v121 hidden-memory risk by moving the sidecar before the
final layer, but its probability-scale gate was too sparse because the Tsubasa
SED view has a much lower mean than the clean Perch surrogate.  v123 keeps the
single-pass memory profile and compares column-wise ranks instead, then maps
the sidecar ranks back onto the clean probability scale before final-layer use.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import shutil
from pathlib import Path


SOURCE_DIR = Path("birdclef-2026/notebooks/v103-guarded-macro-risk-rescue")
DEST_DIR = Path("birdclef-2026/notebooks/v123-rankcal-singlepass-tsubasa")
NOTEBOOK = "submission.ipynb"
NEW_KERNEL_ID = "junhaochengadjcjh7u7/bc26-v123-rankcal-singlepass"
NEW_TITLE = "bc26-v123-rankcal-singlepass"
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


def patch_v123_notebook(path: Path) -> None:
    nb = json.loads(path.read_text())
    cells = nb["cells"]

    cells[0]["source"] = [
        "# BirdCLEF+ 2026 - V123 Original: Rank-Calibrated Single-Pass Tsubasa\n",
        "\n",
        "Provenance: this notebook continues the license-clean v116/v120-v122 "
        "line. It keeps the v122 single-pass memory profile, uses the CC0 "
        "Tsubasa ConvNeXt SED fold only as a sparse sidecar, and avoids prior "
        "output CSVs plus unknown-license SED/cache inputs.\n",
        "\n",
        "Original experiment: v122's probability-scale gate was too sparse "
        "because Tsubasa SED probabilities are on a lower scale than the clean "
        "Perch surrogate. v123 compares column-wise ranks, maps the Tsubasa "
        "rank order onto the clean probability distribution, applies the same "
        "10-class sparse sidecar idea, then runs the final layer once.\n",
    ]

    for cell in cells:
        src = _split_source(cell)
        src = src.replace("V116", "V123").replace("v116", "v123")
        src = src.replace("bc26-v116-tsubasa-convnext-sed", "bc26-v123-rankcal-singlepass")
        src = src.replace("v123_tsubasa_convnext_sed_remap_diagnostics.csv", "v123_rankcal_tsubasa_remap_diagnostics.csv")
        _set_source(cell, src)

    remap_idx = None
    for i, cell in enumerate(cells):
        src = _split_source(cell)
        if "sed_probs = ((1.0 - rank_mix) * sed_test_view + rank_mix * rank_view)" in src:
            remap_idx = i
            break
    if remap_idx is None:
        raise ValueError("could not find v123 SED remap cell")

    src = _split_source(cells[remap_idx])
    marker = 'print("V123 remap diagnostics saved: v123_rankcal_tsubasa_remap_diagnostics.csv")\n'
    if marker not in src:
        raise ValueError("could not find remap diagnostic marker")

    hybrid = f'''

# V123 memory-reduced innovation: compare sidecar and clean views by rank,
# calibrate sidecar ranks onto the clean probability scale, then run the final
# layer once.  This avoids v120/v121 double-final memory use and fixes v122's
# under-active probability-scale gate.
v123_tsubasa_sed_probs = sed_probs.copy()
v123_tsubasa_sed_auc = sed_per_class_auc.copy()
v123_clean_sed_probs = (1.0 / (1.0 + np.exp(-np.clip(scores_test, -50, 50)))).astype(np.float32)
v123_clean_sed_auc = np.nan_to_num(per_class_auc_cal, nan=0.50).astype(np.float32)

def _v123_rank_cols(values):
    return pd.DataFrame(np.asarray(values, dtype=np.float32)).rank(axis=0, pct=True).to_numpy(np.float32)

v123_tsubasa_rank = _v123_rank_cols(v123_tsubasa_sed_probs)
v123_clean_rank = _v123_rank_cols(v123_clean_sed_probs)
v123_tsubasa_rankcal = np.empty_like(v123_clean_sed_probs, dtype=np.float32)
for _ci in range(N_CLASSES):
    _side_order = np.argsort(v123_tsubasa_rank[:, _ci])
    _clean_sorted = np.sort(v123_clean_sed_probs[:, _ci]).astype(np.float32)
    v123_tsubasa_rankcal[_side_order, _ci] = _clean_sorted

v123_selected_classes = {json.dumps(SELECTED_CLASSES)}
v123_selected_set = set(v123_selected_classes)
v123_selected_mask = np.array([label in v123_selected_set for label in PRIMARY_LABELS], dtype=bool)
v123_cell_gate = (
    v123_selected_mask.reshape(1, -1)
    & (v123_tsubasa_rank > (v123_clean_rank + 0.02))
)
v123_mix = np.where(v123_cell_gate, 0.40, 0.0).astype(np.float32)
sed_probs = ((1.0 - v123_mix) * v123_clean_sed_probs + v123_mix * v123_tsubasa_rankcal).astype(np.float32)
sed_per_class_auc = np.where(
    v123_selected_mask,
    np.maximum(v123_clean_sed_auc, np.nan_to_num(v123_tsubasa_sed_auc, nan=0.50)),
    v123_clean_sed_auc,
).astype(np.float32)
v123_rankcal_summary = pd.DataFrame(
    [
        {{
            "branch": "clean_sed_surrogate",
            "role": "base",
            "min": float(v123_clean_sed_probs.min()),
            "max": float(v123_clean_sed_probs.max()),
            "mean": float(v123_clean_sed_probs.mean()),
            "std": float(v123_clean_sed_probs.std()),
        }},
        {{
            "branch": "tsubasa_sed_rankcal",
            "role": "rankcal_sidecar",
            "min": float(v123_tsubasa_rankcal.min()),
            "max": float(v123_tsubasa_rankcal.max()),
            "mean": float(v123_tsubasa_rankcal.mean()),
            "std": float(v123_tsubasa_rankcal.std()),
        }},
        {{
            "branch": "v123_rankcal_singlepass_hybrid_sed",
            "role": "final_layer_input",
            "min": float(sed_probs.min()),
            "max": float(sed_probs.max()),
            "mean": float(sed_probs.mean()),
            "std": float(sed_probs.std()),
        }},
    ]
)
v123_rankcal_summary.to_csv("v123_rankcal_tsubasa_summary.csv", index=False)
print(f"V123 selected sidecar classes: {{v123_selected_classes}}")
print(f"V123 rank-margin gate cells: {{int(v123_cell_gate.sum())}} / {{v123_cell_gate.size}}")
print("V123 final layer mode: single pass after rank-calibrated SED hybridization")
print(f"V123 hybrid SED range: [{{sed_probs.min():.6f}}, {{sed_probs.max():.6f}}]")
print(f"V123 hybrid SED mean/std: {{sed_probs.mean():.6f}}/{{sed_probs.std():.6f}}")

import gc
del v123_tsubasa_sed_probs, v123_clean_sed_probs, v123_tsubasa_rankcal, v123_tsubasa_rank, v123_clean_rank, v123_mix, v123_cell_gate
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
    patch_v123_notebook(dest_dir / NOTEBOOK)
    (dest_dir / "ATTRIBUTION.md").write_text(
        "\n".join(
            [
                "# Attribution",
                "",
                "This candidate continues the private original clean v110/v116/v120-v122 line.",
                "",
                "Original v123 change:",
                "- preserves the single-pass memory-reduced final-layer structure from v122;",
                "- rank-calibrates the CC0 Tsubasa sidecar onto the clean Perch surrogate scale;",
                "- applies the sidecar only to 10 pre-declared train-window-supported classes with rank margin 0.02;",
                "- runs the expensive final layer once;",
                "- does not mount prior output CSVs or unknown-license SED/cache dependencies;",
                "- keeps CPU-only/no-internet metadata and writes rank-calibrated diagnostics.",
                "",
                "Run-mode only until v123 runtime, schema, proxy, correlation, and compliance evidence pass.",
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
