#!/usr/bin/env python3
"""Prepare an attributed Alexy CNN CPU-only inference candidate.

This helper materializes a private Kaggle kernel candidate from the public
`alexycactus/birdclef-2026-cnn-infer-dataset` source. It does not submit to
the competition.
"""

from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path


COMPETITION = "birdclef-2026"
SOURCE_DIR = Path("/tmp/bc26_scan_may19_turn11/alexycactus_birdclef_2026_cnn_infer_dataset")
DEST_DIR = Path("birdclef-2026/notebooks/v101-attributed-alexy-cnn-cpu")
SOURCE_CODE = "birdclef-2026-cnn-infer-dataset.py"
SOURCE_METADATA = "kernel-metadata.json"
NEW_KERNEL_ID = "junhaochengadjcjh7u7/bc26-v101-attributed-alexy-cnn-cpu"
NEW_TITLE = "bc26-v101-attributed-alexy-cnn-cpu"


def source_checks(source_dir: Path) -> None:
    for name in [SOURCE_CODE, SOURCE_METADATA]:
        if not (source_dir / name).exists():
            raise FileNotFoundError(source_dir / name)
    metadata = json.loads((source_dir / SOURCE_METADATA).read_text())
    if metadata.get("enable_internet") is not False:
        raise ValueError("source metadata enables internet")
    if COMPETITION not in (metadata.get("competition_sources") or []):
        raise ValueError(f"source metadata is missing competition source {COMPETITION}")
    if "alexycactus/birdclef-2026-cnn-fold-checkpoints" not in (metadata.get("dataset_sources") or []):
        raise ValueError("source metadata is missing Alexy CNN fold checkpoint dataset")


def patch_code(text: str) -> str:
    text = text.replace("GPU      : ON  (used if available, falls back to CPU cleanly)", "GPU      : OFF (forced CPU-only for final-route compatibility)")
    text = text.replace("DEVICE = \"cuda\" if torch.cuda.is_available() else \"cpu\"", "DEVICE = \"cpu\"")
    text = text.replace("GPU={torch.cuda.get_device_name(0) if DEVICE == 'cuda' else 'n/a'}", "GPU=forced-off")
    text = text.replace("nb20d startup", "v101 nb20e CPU startup")

    old_fallback = """# Locate test files (with staging fallback)
test_dir = BASE_DIR / "test_soundscapes"
test_files = sorted(test_dir.glob("*.ogg")) if test_dir.exists() else []
if not test_files:
    print("test_soundscapes empty -- staging fallback: first 16 train soundscapes")
    test_files = sorted((BASE_DIR / "train_soundscapes").glob("*.ogg"))[:16]
print(f"Test files: {len(test_files)}")
"""
    new_fallback = """# Locate test files. In Kaggle Run mode the hidden test is not mounted; emit a
# valid sample-shaped prior instead of falling back to train soundscapes.
test_dir = BASE_DIR / "test_soundscapes"
test_files = sorted(test_dir.glob("*.ogg")) if test_dir.exists() else []
if not test_files:
    print("test_soundscapes empty -- staging sample-submission prior output")
    staging = sample_sub.copy()
    for _c in PRIMARY_LABELS:
        staging[_c] = 1.0 / N_CLASSES
    _vals = staging[PRIMARY_LABELS].to_numpy(dtype=float)
    assert staging.columns.tolist() == ["row_id"] + PRIMARY_LABELS
    assert not staging["row_id"].duplicated().any()
    assert np.isfinite(_vals).all()
    assert (_vals >= 0.0).all() and (_vals <= 1.0).all()
    staging.to_csv(OUT_DIR / "submission.csv", index=False)
    with open(OUT_DIR / "diagnostics_v101_staging_no_test.json", "w") as f:
        json.dump(
            {
                "notebook": "v101_alexy_cnn_cpu",
                "mode": "staging_no_test",
                "rows": int(len(staging)),
                "classes": int(N_CLASSES),
                "device": DEVICE,
                "reason": "hidden test is unavailable in Kaggle Run mode",
            },
            f,
            indent=2,
        )
    raise SystemExit(0)
print(f"Test files: {len(test_files)}")
"""
    if old_fallback not in text:
        raise ValueError("expected train fallback block not found")
    text = text.replace(old_fallback, new_fallback)

    old_submit = """assert sub.columns.tolist() == ["row_id"] + PRIMARY_LABELS
sub.to_csv(OUT_DIR / "submission.csv", index=False)
print(f"Submission saved: {sub.shape}")
"""
    new_submit = """assert sub.columns.tolist() == ["row_id"] + PRIMARY_LABELS
if len(sample_sub) > 10:
    assert sub["row_id"].astype(str).tolist() == sample_sub["row_id"].astype(str).tolist()
_sub_vals = sub[PRIMARY_LABELS].to_numpy(dtype=float)
assert not sub["row_id"].duplicated().any()
assert np.isfinite(_sub_vals).all()
assert (_sub_vals >= 0.0).all() and (_sub_vals <= 1.0).all()
sub.to_csv(OUT_DIR / "submission.csv", index=False)
print(f"Submission saved: {sub.shape}")
"""
    if old_submit not in text:
        raise ValueError("expected submission write block not found")
    text = text.replace(old_submit, new_submit)

    text = text.replace('"notebook":     "nb20e_infer_dataset"', '"notebook":     "v101_alexy_cnn_cpu"')
    return text


def materialize(source_dir: Path, dest_dir: Path, overwrite: bool) -> None:
    if dest_dir.exists():
        if not overwrite:
            raise FileExistsError(f"destination already exists: {dest_dir}")
        shutil.rmtree(dest_dir)
    shutil.copytree(source_dir, dest_dir)

    metadata_path = dest_dir / SOURCE_METADATA
    metadata = json.loads(metadata_path.read_text())
    metadata.pop("id_no", None)
    metadata.update(
        {
            "id": NEW_KERNEL_ID,
            "title": NEW_TITLE,
            "code_file": SOURCE_CODE,
            "is_private": True,
            "enable_gpu": False,
            "enable_tpu": False,
            "enable_internet": False,
            "dataset_sources": ["alexycactus/birdclef-2026-cnn-fold-checkpoints"],
            "kernel_sources": [],
            "competition_sources": [COMPETITION],
            "model_sources": [],
        }
    )
    metadata_path.write_text(json.dumps(metadata, indent=2) + "\n")

    code_path = dest_dir / SOURCE_CODE
    code_path.write_text(patch_code(code_path.read_text()), encoding="utf-8")

    (dest_dir / "ATTRIBUTION.md").write_text(
        "\n".join(
            [
                "# Attribution",
                "",
                "This candidate is an attributed public-reference derivative of",
                "`alexycactus/birdclef-2026-cnn-infer-dataset`.",
                "",
                "Local changes:",
                "- force CPU-only execution even if CUDA is present;",
                "- keep internet disabled and use only the public Alexy CNN checkpoint dataset;",
                "- remove the train_soundscapes staging fallback;",
                "- emit a sample-shaped prior only when Kaggle Run mode has no hidden test;",
                "- add final row-order, duplicate-row, finite, and range assertions.",
                "",
                "This is not original work. Do not submit without a candidate-specific",
                "rules compliance pass and a fresh decision brief.",
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

    source_checks(args.source_dir)
    print("source_dir=", args.source_dir)
    print("dest_dir=", args.dest_dir)
    print("new_kernel_id=", NEW_KERNEL_ID)
    print("execute=", args.execute)
    print("PLAN: materialize Alexy CNN as a private CPU-only candidate; do not submit.")

    if not args.execute:
        print("DRY_RUN: no files written.")
        return 0

    materialize(args.source_dir, args.dest_dir, args.overwrite)
    print("MATERIALIZED:", args.dest_dir)
    print("NEXT: static audit, Kaggle Run-mode push, output/runtime audit, then decision brief.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
