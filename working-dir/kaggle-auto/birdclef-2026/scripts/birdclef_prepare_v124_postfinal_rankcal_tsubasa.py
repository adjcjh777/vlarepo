#!/usr/bin/env python3
"""Prepare v124 post-final rank-calibrated Tsubasa sidecar candidate.

v123 proved that rank-calibrated single-pass Tsubasa evidence is memory-safe
but too muted when injected before the final EcoProto/rank-launch layer.  v124
runs the clean final layer once, then applies a lightweight post-final
rank-calibrated sidecar correction on the same 10 class set.  It avoids the
v120/v121 double-final memory pattern while preserving a more direct sidecar
effect.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import shutil
from pathlib import Path


SOURCE_DIR = Path("birdclef-2026/notebooks/v103-guarded-macro-risk-rescue")
DEST_DIR = Path("birdclef-2026/notebooks/v124-postfinal-rankcal-tsubasa")
NOTEBOOK = "submission.ipynb"
NEW_KERNEL_ID = "junhaochengadjcjh7u7/bc26-v124-postfinal-rankcal"
NEW_TITLE = "bc26-v124-postfinal-rankcal"
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


def patch_v124_notebook(path: Path) -> None:
    nb = json.loads(path.read_text())
    cells = nb["cells"]

    cells[0]["source"] = [
        "# BirdCLEF+ 2026 - V124 Original: Post-Final Rank-Calibrated Tsubasa\n",
        "\n",
        "Provenance: this notebook continues the license-clean v116/v120-v123 "
        "line. It keeps the single-final-layer memory profile, uses the CC0 "
        "Tsubasa ConvNeXt SED fold only as a sparse sidecar, and avoids prior "
        "output CSVs plus unknown-license SED/cache inputs.\n",
        "\n",
        "Original experiment: v123's pre-final rank-calibrated sidecar was "
        "memory-safe but too muted after the final layer. v124 runs the clean "
        "final layer once, then applies a lightweight post-final sidecar "
        "correction on the same 10 selected classes when the sidecar rank is "
        "ahead of the clean final rank by 0.02.\n",
    ]

    for cell in cells:
        src = _split_source(cell)
        src = src.replace("V116", "V124").replace("v116", "v124")
        src = src.replace("bc26-v116-tsubasa-convnext-sed", "bc26-v124-postfinal-rankcal")
        src = src.replace("v124_tsubasa_convnext_sed_remap_diagnostics.csv", "v124_postfinal_tsubasa_remap_diagnostics.csv")
        _set_source(cell, src)

    remap_idx = None
    final_idx = None
    for i, cell in enumerate(cells):
        src = _split_source(cell)
        if "sed_probs = ((1.0 - rank_mix) * sed_test_view + rank_mix * rank_view)" in src:
            remap_idx = i
        if "final_probs = (0.40 * v107_like_probs + 0.60 * v109_like_probs)" in src:
            final_idx = i
    if remap_idx is None:
        raise ValueError("could not find v124 SED remap cell")
    if final_idx is None:
        raise ValueError("could not find v124 final layer cell")

    src = _split_source(cells[remap_idx])
    marker = 'print("V124 remap diagnostics saved: v124_postfinal_tsubasa_remap_diagnostics.csv")\n'
    if marker not in src:
        raise ValueError("could not find remap diagnostic marker")
    sidecar_capture = f'''

# V124 keeps a lightweight rank-calibrated Tsubasa sidecar for post-final use,
# but feeds the clean Perch surrogate into the expensive final layer so that
# the final layer runs exactly once.
v124_tsubasa_sed_probs = sed_probs.copy()
v124_clean_sed_probs = (1.0 / (1.0 + np.exp(-np.clip(scores_test, -50, 50)))).astype(np.float32)
v124_clean_sed_auc = np.nan_to_num(per_class_auc_cal, nan=0.50).astype(np.float32)

def _v124_rank_cols(values):
    return pd.DataFrame(np.asarray(values, dtype=np.float32)).rank(axis=0, pct=True).to_numpy(np.float32)

v124_tsubasa_rank = _v124_rank_cols(v124_tsubasa_sed_probs)
v124_tsubasa_rankcal = np.empty_like(v124_clean_sed_probs, dtype=np.float32)
for _ci in range(N_CLASSES):
    _side_order = np.argsort(v124_tsubasa_rank[:, _ci])
    _clean_sorted = np.sort(v124_clean_sed_probs[:, _ci]).astype(np.float32)
    v124_tsubasa_rankcal[_side_order, _ci] = _clean_sorted

v124_selected_classes = {json.dumps(SELECTED_CLASSES)}
v124_selected_set = set(v124_selected_classes)
v124_selected_mask = np.array([label in v124_selected_set for label in PRIMARY_LABELS], dtype=bool)

sed_probs = v124_clean_sed_probs.astype(np.float32)
sed_per_class_auc = v124_clean_sed_auc.astype(np.float32)
print(f"V124 stored rank-calibrated sidecar for post-final use: range=[{{v124_tsubasa_rankcal.min():.6f}}, {{v124_tsubasa_rankcal.max():.6f}}]")
print("V124 final layer input: clean Perch surrogate; final layer will run once")
'''
    _set_source(cells[remap_idx], src.replace(marker, marker + sidecar_capture))

    src = _split_source(cells[final_idx])
    marker = 'print(f"V124 post-cleanblend score mean/std: {final_probs.mean():.6f}/{final_probs.std():.6f}")\n'
    if marker not in src:
        raise ValueError("could not find final score marker")
    post_final = '''

# V124 post-final lightweight sidecar.  This is intentionally cheaper than
# recomputing a Tsubasa final layer: it compares ranks against the clean final
# output and only nudges selected classes where Tsubasa is ahead.
v124_clean_final_probs = final_probs.copy()
v124_clean_final_rank = _rank01(v124_clean_final_probs)
v124_postfinal_gate = (
    v124_selected_mask.reshape(1, -1)
    & (v124_tsubasa_rank > (v124_clean_final_rank + 0.02))
)
v124_postfinal_mix = np.where(v124_postfinal_gate, 0.30, 0.0).astype(np.float32)
final_probs = ((1.0 - v124_postfinal_mix) * v124_clean_final_probs + v124_postfinal_mix * v124_tsubasa_rankcal).astype(np.float32)
v124_postfinal_summary = pd.DataFrame(
    [
        {
            "branch": "clean_final",
            "role": "base",
            "min": float(v124_clean_final_probs.min()),
            "max": float(v124_clean_final_probs.max()),
            "mean": float(v124_clean_final_probs.mean()),
            "std": float(v124_clean_final_probs.std()),
        },
        {
            "branch": "tsubasa_rankcal_sidecar",
            "role": "postfinal_sidecar",
            "min": float(v124_tsubasa_rankcal.min()),
            "max": float(v124_tsubasa_rankcal.max()),
            "mean": float(v124_tsubasa_rankcal.mean()),
            "std": float(v124_tsubasa_rankcal.std()),
        },
        {
            "branch": "v124_postfinal_blend",
            "role": "submission",
            "min": float(final_probs.min()),
            "max": float(final_probs.max()),
            "mean": float(final_probs.mean()),
            "std": float(final_probs.std()),
        },
    ]
)
v124_postfinal_summary.to_csv("v124_postfinal_tsubasa_summary.csv", index=False)
print(f"V124 selected sidecar classes: {v124_selected_classes}")
print(f"V124 post-final rank-margin gate cells: {int(v124_postfinal_gate.sum())} / {v124_postfinal_gate.size}")
print("V124 final layer mode: clean final once plus post-final rank-calibrated sidecar")
print(f"V124 final score range: [{final_probs.min():.6f}, {final_probs.max():.6f}]")
print(f"V124 final score mean/std: {final_probs.mean():.6f}/{final_probs.std():.6f}")
'''
    _set_source(cells[final_idx], src.replace(marker, marker + post_final))
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
    patch_v124_notebook(dest_dir / NOTEBOOK)
    (dest_dir / "ATTRIBUTION.md").write_text(
        "\n".join(
            [
                "# Attribution",
                "",
                "This candidate continues the private original clean v110/v116/v120-v123 line.",
                "",
                "Original v124 change:",
                "- runs the clean EcoProto/rank-launch final layer once;",
                "- keeps a lightweight rank-calibrated CC0 Tsubasa sidecar for post-final correction;",
                "- applies the sidecar only to 10 pre-declared train-window-supported classes with rank margin 0.02;",
                "- avoids the v120/v121 double-final memory pattern;",
                "- does not mount prior output CSVs or unknown-license SED/cache dependencies;",
                "- keeps CPU-only/no-internet metadata and writes post-final diagnostics.",
                "",
                "Run-mode only until v124 runtime, schema, proxy, correlation, and compliance evidence pass.",
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
