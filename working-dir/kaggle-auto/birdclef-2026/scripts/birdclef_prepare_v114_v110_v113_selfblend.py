#!/usr/bin/env python3
"""Prepare v114 self-contained v110/v113 clean blend.

v114 tests the small local blend gain from v113 without attaching local output
CSVs as Kaggle inputs. It starts from the v113 LantingGuo MelNorm notebook,
keeps both SED views in memory, runs the final decision layer twice, and blends:

    final = 0.85 * v110_like + 0.15 * v113_like

The experiment remains CPU-only, no-internet, and license-clean.
"""

from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path


SOURCE_DIR = Path("birdclef-2026/notebooks/v113-lantingguo-melnorm-ecoproto")
DEST_DIR = Path("birdclef-2026/notebooks/v114-v110-v113-selfblend")
NOTEBOOK = "submission.ipynb"
NEW_KERNEL_ID = "junhaochengadjcjh7u7/bc26-v114-clean-selfblend"
NEW_TITLE = "bc26-v114-clean-selfblend"


def _split_source(cell: dict) -> str:
    src = cell.get("source", "")
    if isinstance(src, list):
        return "".join(src)
    return str(src)


def _set_source(cell: dict, source: str) -> None:
    cell["source"] = source.splitlines(keepends=True)


def _wrap_final_cell(source: str) -> str:
    indented = "\n".join("    " + line if line else "" for line in source.splitlines())
    return f"""# V114 self-contained final layer.
# Run the clean final layer twice in the same notebook:
# - v110_like: Perch-only clean fallback SED surrogate.
# - v113_like: LantingGuo MelNormProbe sidecar.
def _compute_v114_branch(branch_name, sed_probs_input, sed_auc_input):
    print(f"V114 computing branch: {{branch_name}}")
    sed_probs = sed_probs_input.astype(np.float32)
    sed_per_class_auc = sed_auc_input.astype(np.float32)
{indented}
    return final_probs.astype(np.float32)

final_probs_v110_like = _compute_v114_branch("v110_like", sed_probs_v110_like, sed_per_class_auc_v110_like)
final_probs_v113_like = _compute_v114_branch("v113_like", sed_probs_v113_like, sed_per_class_auc_v113_like)
final_probs = (0.85 * final_probs_v110_like + 0.15 * final_probs_v113_like).astype(np.float32)
branch_delta = final_probs_v113_like - final_probs_v110_like
pd.DataFrame({{
    "branch": ["v110_like", "v113_like", "v114_blend"],
    "mean": [float(final_probs_v110_like.mean()), float(final_probs_v113_like.mean()), float(final_probs.mean())],
    "std": [float(final_probs_v110_like.std()), float(final_probs_v113_like.std()), float(final_probs.std())],
    "min": [float(final_probs_v110_like.min()), float(final_probs_v113_like.min()), float(final_probs.min())],
    "max": [float(final_probs_v110_like.max()), float(final_probs_v113_like.max()), float(final_probs.max())],
}}).to_csv("v114_branch_summary.csv", index=False)
print(f"V114 blend weights: v110_like=0.85, v113_like=0.15")
print(f"V114 branch delta mean/std/min/max: {{branch_delta.mean():.6f}}/{{branch_delta.std():.6f}}/{{branch_delta.min():.6f}}/{{branch_delta.max():.6f}}")
print(f"V114 final score range: [{{final_probs.min():.6f}}, {{final_probs.max():.6f}}]")
print(f"V114 final score mean/std: {{final_probs.mean():.6f}}/{{final_probs.std():.6f}}")
"""


def patch_notebook(path: Path) -> None:
    nb = json.loads(path.read_text())
    cells = nb["cells"]

    cells[0]["source"] = [
        "# BirdCLEF+ 2026 - V114 Original: Self-Contained v110/v113 Clean Blend\n",
        "\n",
        "Provenance: this notebook continues the private original v86/v102/v103 and "
        "clean v110-v113 line. It does not attach local output CSVs. Instead, it "
        "computes both the v110-like Perch-only clean fallback and the v113-like "
        "LantingGuo MelNormProbe branch inside one CPU/no-internet Kaggle notebook.\n",
        "\n",
        "Experiment: v114 materializes the local `0.85*v110 + 0.15*v113` probe as a "
        "self-contained notebook. Run-mode only; do not submit unless proxy and "
        "compliance evidence justify spending a daily slot.\n",
    ]

    for cell in cells:
        src = _split_source(cell)
        if "V113 license-clean branch: LantingGuo MelNormProbe" in src:
            append = """

# V114 keeps both clean SED views for a self-contained blend.
sed_probs_v113_like = sed_probs.copy()
sed_per_class_auc_v113_like = sed_per_class_auc.copy()
sed_probs_v110_like = _sigmoid_np(scores_test).astype(np.float32)
sed_per_class_auc_v110_like = np.nan_to_num(per_class_auc_cal, nan=0.50).astype(np.float32)
pd.DataFrame({
    "primary_label": PRIMARY_LABELS,
    "support": Y_FULL.sum(axis=0).astype(int),
    "sed_auc_v110_like": sed_per_class_auc_v110_like,
    "sed_auc_v113_like": sed_per_class_auc_v113_like,
    "sed_auc_delta": sed_per_class_auc_v113_like - sed_per_class_auc_v110_like,
}).to_csv("v114_branch_auc_diagnostics.csv", index=False)
print("V114 prepared branch SED views: v110_like Perch-only + v113_like LantingGuo MelNorm")
"""
            _set_source(cell, src + append)
            break
    else:
        raise ValueError("could not find v113 MelNorm SED cell")

    for cell in cells:
        src = _split_source(cell)
        if src.startswith("# V68 original final layer:"):
            _set_source(cell, _wrap_final_cell(src))
            break
    else:
        raise ValueError("could not find final layer cell")

    path.write_text(json.dumps(nb, ensure_ascii=False) + "\n")


def materialize(source_dir: Path, dest_dir: Path, overwrite: bool) -> None:
    if dest_dir.exists():
        if not overwrite:
            raise FileExistsError(dest_dir)
        shutil.rmtree(dest_dir)
    shutil.copytree(source_dir, dest_dir)

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
                "lantingguo/birdclef2026-own-sed-b0-v5-onnx",
            ],
            "kernel_sources": [],
            "competition_sources": ["birdclef-2026"],
            "model_sources": [
                "google/bird-vocalization-classifier/TensorFlow2/perch_v2_cpu/1"
            ],
        }
    )
    meta_path.write_text(json.dumps(meta, indent=2) + "\n")
    patch_notebook(dest_dir / NOTEBOOK)
    (dest_dir / "ATTRIBUTION.md").write_text(
        "\n".join(
            [
                "# Attribution",
                "",
                "This candidate continues the private original v86/v102/v103 and clean v110-v113 line.",
                "",
                "Original v114 change:",
                "- computes a v110-like Perch-only clean fallback branch inside the notebook;",
                "- computes a v113-like LantingGuo MelNormProbe branch inside the notebook;",
                "- blends the two internal branches at 0.85/0.15 based on the local v113 blend probe;",
                "- does not attach local output CSVs or prior notebook outputs as Kaggle inputs;",
                "- keeps CPU-only/no-internet metadata and public, recorded Perch plus CC0 LantingGuo inputs.",
                "",
                "Run-mode only until v114 runtime, schema, proxy, and compliance evidence pass.",
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
