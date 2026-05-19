#!/usr/bin/env python3
"""Prepare v105 rank-restored Perch-only guarded macro rescue from v103.

v105 removes runtime dependencies with unknown Kaggle metadata licenses:
- jaejohn/perch-meta
- tuckerarrants/bc2026-distilled-sed-public

It keeps the v104 license-reduced dependency set and adds a row-rank
restoration layer to recover top-hit/top5 signal lost by the Perch-only path.
"""

from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path


SOURCE_DIR = Path("birdclef-2026/notebooks/v103-guarded-macro-risk-rescue")
DEST_DIR = Path("birdclef-2026/notebooks/v105-rankrestored-perch-guarded")
NOTEBOOK = "submission.ipynb"
NEW_KERNEL_ID = "junhaochengadjcjh7u7/bc26-v105-rankrestored-perch"
NEW_TITLE = "bc26-v105-rankrestored-perch"


def _code_cell(source: str) -> dict:
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": source.splitlines(keepends=True),
    }


def patch_notebook(path: Path) -> None:
    nb = json.loads(path.read_text())
    cells = nb["cells"]

    cells[0]["source"] = [
        "# BirdCLEF+ 2026 - V105 Original: Rank-Restored Perch Guarded Rescue\n",
        "\n",
        "Provenance: this notebook continues the private original v86/v102/v103 fast-ONNX line. "
        "Like v104, it removes the unknown-license runtime dependencies `jaejohn/perch-meta` "
        "and `tuckerarrants/bc2026-distilled-sed-public`. Train Perch features are rebuilt "
        "inside the Kaggle notebook from competition train soundscapes using the public Perch "
        "ONNX bundle, and the SED branch is replaced by a Perch-only surrogate view.\n",
        "\n",
        "Experiment: v105 preserves v104's license-clean dependency set but adds an original "
        "row-rank restoration layer to recover top-hit/top5 signal lost after removing the "
        "external SED branch. Run-mode only until schema, runtime, proxy, and compliance evidence pass.\n",
    ]

    # Metadata/cache discovery cell: remove unknown-license cache lookup.
    cache_cell = "".join(cells[3]["source"])
    cache_start = cache_cell.index("CACHE_DIR = None")
    cache_cell = (
        cache_cell[:cache_start]
        + 'CACHE_DIR = None\nprint("External Perch cache disabled for v105 license-reduced run")\n'
    )
    cells[3]["source"] = cache_cell.splitlines(keepends=True)

    # Cell 7 only needs filename parsing; cached arrays are rebuilt after run_perch_fast exists.
    cell7 = "".join(cells[7]["source"])
    cell7 = cell7.split('assert CACHE_DIR is not None, "Cache not found!"')[0]
    cell7 += 'print("V105: Perch train cache will be rebuilt in-notebook after inference helpers are defined")\n'
    cells[7]["source"] = cell7.splitlines(keepends=True)

    # Split the original Perch helper cell into helper definitions and test inference.
    perch_cell = "".join(cells[13]["source"])
    split_token = 'test_dir = BASE / "test_soundscapes"'
    if split_token not in perch_cell:
        raise ValueError("could not split Perch helper cell")
    helper_src, test_src_tail = perch_cell.split(split_token, 1)
    helper_src = helper_src.replace(
        "target_dim = emb_full.shape[1]",
        "target_dim = 1536",
    ).replace(
        "test_emb = np.zeros((rows, emb_full.shape[1]), np.float32)",
        "test_emb = np.zeros((rows, 1536), np.float32)",
    )
    test_src = split_token + test_src_tail

    build_train_src = """# V105: rebuild train Perch features in-notebook to avoid the unknown-license perch-meta cache.
train_paths = [BASE / "train_soundscapes" / fn for fn in full_files]
train_paths = [p for p in train_paths if p.exists()]
print(f"V105 rebuilding Perch train features for {len(train_paths)} files")
meta_full, scores_full_raw, emb_full, _spatial_train_unused = run_perch_fast(
    train_paths, capture_spatial=False, desc="V105 Perch train feature rebuild"
)
meta_full = meta_full.set_index("row_id").loc[full_rows["row_id"].astype(str)].reset_index()
scores_full_raw = scores_full_raw[: len(meta_full)]
emb_full = emb_full[: len(meta_full)]
assert np.all(meta_full["filename"].values == full_rows["filename"].values)
print(f"V105 rebuilt train features: meta={meta_full.shape}, scores={scores_full_raw.shape}, emb={emb_full.shape}")
"""

    # Replace SED branch with a no-external-license Perch surrogate.
    sed_surrogate_src = """# V105 license-reduced branch: no external SED folds.
# Use a Perch-only surrogate view so downstream v103 guard logic remains intact
# without depending on external SED fold datasets.
sed_per_class_auc = np.nan_to_num(per_class_auc_cal, nan=0.50).astype(np.float32)
sed_rows = meta_test["row_id"].astype(str).tolist()
sed_probs = (1.0 / (1.0 + np.exp(-np.clip(scores_test, -50, 50)))).astype(np.float32)
assert sed_rows == meta_test["row_id"].astype(str).tolist(), "Perch surrogate row_id order mismatch"
print(f"V105 Perch-only surrogate view: shape={sed_probs.shape}, range=[{sed_probs.min():.6f}, {sed_probs.max():.6f}]")
"""

    final_cell = "".join(cells[15]["source"])
    final_cell = final_cell.replace(
        "# V103 original guarded macro-risk rescue policy.",
        "# V105 original rank-restored Perch-only guarded macro-risk rescue policy.",
    ).replace(
        "# This is a conservative follow-up to v102: keep the class-wise OOF/taxa/support\n# rescue idea, but only let it strongly move cells when the rescue view is\n# locally stronger than the conservative v84-like anchor. A row-level top-hit\n# guard protects high-confidence primary calls from macro rescue spillover.",
        "# This is a license-reduced follow-up to v103: keep the class-wise OOF/taxa/support\n# rescue idea, but remove SED/cache runtime dependencies with unknown licenses.\n# Rescue strength is more conservative because only Perch/probe views remain.",
    ).replace(
        "texture_prior_rescue = texture_taxa & mid_support & (sed_advantage > 0.08)",
        "texture_prior_rescue = texture_taxa & mid_support & (sed_advantage > 0.10)",
    ).replace(
        "rescue_mix[macro_mild] = 0.18\nrescue_mix[macro_weak] = 0.38\nrescue_mix[macro_weak & texture_taxa] = 0.48\nrescue_mix[texture_prior_rescue] = np.maximum(rescue_mix[texture_prior_rescue], 0.28)",
        "rescue_mix[macro_mild] = 0.12\nrescue_mix[macro_weak] = 0.28\nrescue_mix[macro_weak & texture_taxa] = 0.34\nrescue_mix[texture_prior_rescue] = np.maximum(rescue_mix[texture_prior_rescue], 0.18)",
    ).replace(
        "V103 guarded macro-risk rescue counts",
        "V105 rank-restored Perch-only guarded macro-risk rescue counts",
    ).replace(
        "V103 class rescue mix range/mean",
        "V105 class rescue mix range/mean",
    ).replace(
        "V103 effective rescue mix range/mean",
        "V105 effective rescue mix range/mean",
    ).replace(
        "V103 components:",
        "V105 components:",
    ).replace(
        "View mix: v103 = v102 original macro-risk rescue plus positive-rescue and top-hit guards",
        "View mix: v105 = Perch-only guarded rescue plus row-rank restoration without unknown-license cache/SED dependencies",
    )
    restore_block = """
# V105 row-rank restoration. v104 was compliance-clean but lost row-level ranking
# quality. This layer preserves macro guards while injecting a bounded Perch/probe
# row-rank view for non-rare, non-anchor cells.
rank_restore_view = _rank_power(
    0.42 * view_sedfirst + 0.28 * view_adaptive + 0.18 * view_perch + 0.12 * probe_consensus_probs,
    0.82,
).astype(np.float32)
restore_mask = (~rare_guard) & (~protect_guard) & (rank_restore_view > 0.70)
restore_mix = np.where(restore_mask, 0.22, 0.0).astype(np.float32)
final_probs = ((1.0 - restore_mix) * final_probs + restore_mix * rank_restore_view).astype(np.float32)

# Preserve confident row winners from the restored rank view. The mix is deliberately
# small so it can improve top-hit signal without taking over macro calibration.
restored_top = rank_restore_view.max(axis=1, keepdims=True)
restored_top_guard = (rank_restore_view >= (restored_top - 0.012)) & (restored_top >= 0.86) & (~rare_guard)
final_probs = np.where(restored_top_guard, 0.86 * final_probs + 0.14 * rank_restore_view, final_probs).astype(np.float32)
print(f"V105 row-rank restore cells: restore={int(restore_mask.sum())}, top_guard={int(restored_top_guard.sum())}")
print(f"V105 post-restore score range: [{final_probs.min():.6f}, {final_probs.max():.6f}]")
print(f"V105 post-restore score mean/std: {final_probs.mean():.6f}/{final_probs.std():.6f}")
"""
    final_cell = final_cell.replace(
        'print(f"Score mean/std: {final_probs.mean():.6f}/{final_probs.std():.6f}")\n',
        'print(f"Score mean/std: {final_probs.mean():.6f}/{final_probs.std():.6f}")\n' + restore_block,
    )
    cells[15]["source"] = final_cell.splitlines(keepends=True)

    # Reorder: helpers -> train rebuild -> OOF cells -> test inference -> SED surrogate -> final.
    new_cells = []
    new_cells.extend(cells[:9])  # includes label construction in cell 8
    new_cells.append(_code_cell(helper_src))
    new_cells.append(_code_cell(build_train_src))
    new_cells.extend(cells[9:13])  # OOF/calibration/thresholds
    new_cells.append(_code_cell(test_src))
    new_cells.append(_code_cell(sed_surrogate_src))
    new_cells.extend(cells[15:])
    nb["cells"] = new_cells

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
            "dataset_sources": ["rishikeshjani/perch-onnx-for-birdclef-2026"],
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
                "This candidate continues the private original v86/v102/v103/v104 line.",
                "",
                "Original v105 change:",
                "- removes unknown-license runtime dependencies `jaejohn/perch-meta` and `tuckerarrants/bc2026-distilled-sed-public`;",
                "- rebuilds train Perch features inside the Kaggle notebook from competition train soundscapes;",
                "- replaces the SED branch with a Perch-only surrogate view;",
                "- keeps the v103/v104 positive-rescue and top-hit guard idea with conservative rescue strengths;",
                "- adds a bounded row-rank restoration layer from license-clean Perch/probe views;",
                "- keeps CPU-only/no-internet metadata and public, recorded Perch inputs.",
                "",
                "Run-mode only until v105 runtime, schema, proxy, and compliance evidence pass.",
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
