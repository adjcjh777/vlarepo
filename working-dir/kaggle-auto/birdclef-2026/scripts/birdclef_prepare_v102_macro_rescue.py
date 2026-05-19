#!/usr/bin/env python3
"""Prepare v102 original macro-risk rescue candidate from the private v86 line."""

from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path


SOURCE_DIR = Path("birdclef-2026/notebooks/v86-original-midsupport-proberescue")
DEST_DIR = Path("birdclef-2026/notebooks/v102-original-macro-risk-rescue")
SOURCE_NOTEBOOK = "submission.ipynb"
SOURCE_METADATA = "kernel-metadata.json"
NEW_KERNEL_ID = "junhaochengadjcjh7u7/bc26-v102-original-macro-risk-rescue"
NEW_TITLE = "bc26-v102-original-macro-risk-rescue"


OLD_BLOCK = """# Use stronger rescue for non-aves mid-support classes, where the v70-style probe
# signal helped the local proxy most without the all-class collapse seen in v85.
rescue_mix = np.zeros(N_CLASSES, dtype=np.float32)
rescue_mix[mid_support] = 0.50
rescue_mix[non_aves_mid] = 0.72
rescue_mix[(support < 5) | (support > 150)] = 0.0
rescue_mix = rescue_mix.reshape(1, -1)
final_probs = ((1.0 - rescue_mix) * v84_like + rescue_mix * probe_rescue).astype(np.float32)

# Gentle temporal context only for rescued cells: enough to preserve overlapping events,
# much weaker than v85's broad rank-power push.
def _context_mean(arr):
    pv_ctx = arr.reshape(len(test_paths), N_WINDOWS, N_CLASSES).copy()
    ctx = pv_ctx.copy()
    for ii in range(1, N_WINDOWS - 1):
        ctx[:, ii] = 0.78 * pv_ctx[:, ii] + 0.11 * pv_ctx[:, ii - 1] + 0.11 * pv_ctx[:, ii + 1]
    ctx[:, 0] = 0.90 * pv_ctx[:, 0] + 0.10 * pv_ctx[:, 1]
    ctx[:, -1] = 0.90 * pv_ctx[:, -1] + 0.10 * pv_ctx[:, -2]
    return ctx.reshape(-1, N_CLASSES).astype(np.float32)

probe_ctx = _context_mean(probe_consensus_probs)
ctx_mask = (rescue_mix > 0) & (probe_ctx > 0.90) & (sed_rank > 0.78)
ctx_mix = np.where(ctx_mask, 0.055, 0.0).astype(np.float32)
final_probs = ((1.0 - ctx_mix) * final_probs + ctx_mix * probe_ctx).astype(np.float32)

# Keep low-support classes on the conservative macro anchor.
low_guard = (support < 3).reshape(1, -1)
final_probs = np.where(low_guard, 0.92 * macro_probs + 0.08 * final_probs, final_probs).astype(np.float32)

print(f"V86 mid-support probe rescue: rescue_classes={int((rescue_mix.ravel()>0).sum())}/{N_CLASSES}; non_aves_rescue={int(non_aves_mid.sum())}; ctx_cells={int(ctx_mask.sum())}/{ctx_mask.size}; final mean/std={final_probs.mean():.6f}/{final_probs.std():.6f}")
print(f"V86 components: macro mean/std={macro_probs.mean():.6f}/{macro_probs.std():.6f}; v84_like mean/std={v84_like.mean():.6f}/{v84_like.std():.6f}; probe_rescue mean/std={probe_rescue.mean():.6f}/{probe_rescue.std():.6f}; dualprobe mean/std={probe_consensus_probs.mean():.6f}/{probe_consensus_probs.std():.6f}")
print(f"OOF refs: Perch raw={perch_auc_raw_ref.mean():.3f}, Perch cal={perch_auc_cal_ref.mean():.3f}, SED={sed_auc_ref.mean():.3f}, delta={auc_delta.mean():+.3f}")
print(f"SED weights sedfirst={sed_w_sedfirst.mean():.3f}, adaptive={sed_w_adaptive.mean():.3f}, safety={sed_w_safety.mean():.3f}")
print(f"View mix: v86 = conservative v84 anchor plus mid-support private probe rescue")
print(f"Prior strength mean={prior_strength.mean():.3f}, applied mean={prior_mix.mean():.4f}, file scale mean={file_scale.mean():.3f}")
print(f"Spike-smoothed score range: [{final_probs.min():.6f}, {final_probs.max():.6f}]")
print(f"Score mean/std: {final_probs.mean():.6f}/{final_probs.std():.6f}")
"""


NEW_BLOCK = """# V102 original macro-risk rescue policy.
# This replaces v86's broad mid-support gate with a class-wise policy derived
# from local OOF risk, support, taxa, and SED/Perch disagreement. Public
# notebooks are not copied here; this is a workspace-original meta-layer.
base_risk = np.nan_to_num(perch_auc_cal_ref, nan=0.0).astype(np.float32)
sed_advantage = (sed_auc_ref - perch_auc_cal_ref).astype(np.float32)
texture_taxa = np.isin(class_names, ["Amphibia", "Insecta"])

protect_anchor = base_risk >= 0.85
rare_floor = support < 5
macro_weak = mid_support & (base_risk < 0.60)
macro_mild = mid_support & (base_risk >= 0.60) & (base_risk < 0.70)
texture_prior_rescue = texture_taxa & mid_support & (sed_advantage > 0.08)

rescue_mix = np.zeros(N_CLASSES, dtype=np.float32)
rescue_mix[macro_mild] = 0.28
rescue_mix[macro_weak] = 0.56
rescue_mix[macro_weak & texture_taxa] = 0.66
rescue_mix[texture_prior_rescue] = np.maximum(rescue_mix[texture_prior_rescue], 0.40)
rescue_mix[protect_anchor] = np.minimum(rescue_mix[protect_anchor], 0.08)
rescue_mix[rare_floor] = 0.0

sed_rescue_view = (0.50 * view_sedfirst + 0.30 * view_adaptive + 0.20 * probe_consensus_probs).astype(np.float32)
probe_rescue_view = (0.170 * anchor_v13 + 0.060 * anchor_v23 + 0.770 * probe_consensus_probs).astype(np.float32)
rescue_view = np.where(texture_prior_rescue.reshape(1, -1), sed_rescue_view, probe_rescue_view).astype(np.float32)

rescue_mix_2d = rescue_mix.reshape(1, -1)
final_probs = ((1.0 - rescue_mix_2d) * v84_like + rescue_mix_2d * rescue_view).astype(np.float32)

def _context_mean(arr):
    pv_ctx = arr.reshape(len(test_paths), N_WINDOWS, N_CLASSES).copy()
    ctx = pv_ctx.copy()
    for ii in range(1, N_WINDOWS - 1):
        ctx[:, ii] = 0.78 * pv_ctx[:, ii] + 0.11 * pv_ctx[:, ii - 1] + 0.11 * pv_ctx[:, ii + 1]
    ctx[:, 0] = 0.90 * pv_ctx[:, 0] + 0.10 * pv_ctx[:, 1]
    ctx[:, -1] = 0.90 * pv_ctx[:, -1] + 0.10 * pv_ctx[:, -2]
    return ctx.reshape(-1, N_CLASSES).astype(np.float32)

probe_ctx = _context_mean(probe_consensus_probs)
ctx_mask = (rescue_mix_2d > 0.25) & (probe_ctx > 0.90) & (sed_rank > 0.78)
ctx_mix = np.where(ctx_mask, 0.045, 0.0).astype(np.float32)
final_probs = ((1.0 - ctx_mix) * final_probs + ctx_mix * probe_ctx).astype(np.float32)

# Strong classes and rare classes keep conservative behavior; weak mid-support
# classes get a controlled rescue rather than v85-style global aggression.
protect_guard = protect_anchor.reshape(1, -1)
rare_guard = rare_floor.reshape(1, -1)
final_probs = np.where(protect_guard, 0.90 * macro_probs + 0.10 * final_probs, final_probs).astype(np.float32)
final_probs = np.where(rare_guard, 0.94 * macro_probs + 0.06 * final_probs, final_probs).astype(np.float32)

v102_counts = {
    "protect_anchor": int(protect_anchor.sum()),
    "rare_floor": int(rare_floor.sum()),
    "macro_weak": int(macro_weak.sum()),
    "macro_mild": int(macro_mild.sum()),
    "texture_prior_rescue": int(texture_prior_rescue.sum()),
    "active_rescue": int((rescue_mix > 0).sum()),
    "ctx_cells": int(ctx_mask.sum()),
}
print(f"V102 original macro-risk rescue counts: {v102_counts}")
print(f"V102 rescue mix range/mean: [{rescue_mix.min():.3f}, {rescue_mix.max():.3f}] / {rescue_mix.mean():.4f}")
print(f"V102 components: macro mean/std={macro_probs.mean():.6f}/{macro_probs.std():.6f}; v84_like mean/std={v84_like.mean():.6f}/{v84_like.std():.6f}; rescue_view mean/std={rescue_view.mean():.6f}/{rescue_view.std():.6f}; dualprobe mean/std={probe_consensus_probs.mean():.6f}/{probe_consensus_probs.std():.6f}")
print(f"OOF refs: Perch raw={perch_auc_raw_ref.mean():.3f}, Perch cal={perch_auc_cal_ref.mean():.3f}, SED={sed_auc_ref.mean():.3f}, delta={auc_delta.mean():+.3f}")
print(f"SED weights sedfirst={sed_w_sedfirst.mean():.3f}, adaptive={sed_w_adaptive.mean():.3f}, safety={sed_w_safety.mean():.3f}")
print(f"View mix: v102 = conservative v84 anchor plus OOF/taxa/support-conditioned original rescue")
print(f"Prior strength mean={prior_strength.mean():.3f}, applied mean={prior_mix.mean():.4f}, file scale mean={file_scale.mean():.3f}")
print(f"Spike-smoothed score range: [{final_probs.min():.6f}, {final_probs.max():.6f}]")
print(f"Score mean/std: {final_probs.mean():.6f}/{final_probs.std():.6f}")
"""


def patch_notebook(path: Path) -> None:
    notebook = json.loads(path.read_text())
    cells = notebook.get("cells", [])
    if not cells:
        raise ValueError("empty notebook")
    cells[0]["source"] = [
        "# BirdCLEF+ 2026 - V102 Original: Macro-Risk Rescue\\n",
        "\\n",
        "Provenance: this notebook continues the private original v13/v20/v23/v70/v73/v76/v83/v84/v86 fast-ONNX line in this workspace. It uses public Perch v2 ONNX and public distilled SED ONNX model assets as external inputs with attribution, but the final macro-risk rescue policy is written here. Public notebooks remain idea references only; no public notebook code is copied.\\n",
        "\\n",
        "Experiment: v102 replaces v86's broad mid-support probe rescue with a class-wise policy derived from local OOF risk, support, taxa, and SED/Perch disagreement. The goal is to add a real workspace-original increment instead of only forking public-reference solutions. Run-mode only until validated.\\n",
    ]

    patched = False
    for cell in cells:
        text = "".join(cell.get("source", ""))
        if OLD_BLOCK in text:
            text = text.replace(OLD_BLOCK, NEW_BLOCK)
            cell["source"] = text.splitlines(keepends=True)
            patched = True
            break
    if not patched:
        raise ValueError("expected v86 final rescue block not found")
    path.write_text(json.dumps(notebook, ensure_ascii=False) + "\n")


def materialize(source_dir: Path, dest_dir: Path, overwrite: bool) -> None:
    if dest_dir.exists():
        if not overwrite:
            raise FileExistsError(dest_dir)
        shutil.rmtree(dest_dir)
    shutil.copytree(source_dir, dest_dir)

    metadata_path = dest_dir / SOURCE_METADATA
    metadata = json.loads(metadata_path.read_text())
    metadata.update(
        {
            "id": NEW_KERNEL_ID,
            "title": NEW_TITLE,
            "code_file": SOURCE_NOTEBOOK,
            "is_private": True,
            "enable_gpu": False,
            "enable_tpu": False,
            "enable_internet": False,
        }
    )
    metadata_path.write_text(json.dumps(metadata, indent=2) + "\n")
    patch_notebook(dest_dir / SOURCE_NOTEBOOK)
    (dest_dir / "ATTRIBUTION.md").write_text(
        "\n".join(
            [
                "# Attribution",
                "",
                "This candidate continues the private original v86 line.",
                "",
                "Original v102 change:",
                "- replace the broad v86 mid-support rescue gate with a class-wise macro-risk policy;",
                "- derive rescue behavior from local OOF risk, support, taxa, and SED/Perch disagreement;",
                "- protect high-AUC and rare classes while selectively rescuing weak mid-support classes;",
                "- keep CPU-only/no-internet metadata and public, recorded model/data inputs.",
                "",
                "This is a workspace-original meta-layer. Do not submit while v101 is pending",
                "or without v102 Run-mode evidence and candidate-specific compliance review.",
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
    print("NEXT: static audit and Kaggle Run-mode push only; no real submit while v101 is pending.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
