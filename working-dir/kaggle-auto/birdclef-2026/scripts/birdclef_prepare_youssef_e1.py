#!/usr/bin/env python3
"""Prepare an attributed Youssef E1 rare-tail BirdNET candidate.

This helper materializes a local Kaggle Run-mode candidate only. It never
submits to the competition.
"""

from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path


COMPETITION = "birdclef-2026"
SOURCE_DIR = Path("/tmp/bc26_scan_may19/cocoa_youssef_e1")
DEST_DIR = Path("birdclef-2026/notebooks/v90-attributed-youssef-e1-rare-tail-birdnet")
SOURCE_NOTEBOOK = "bc26-youssef-e1-rare-tail-birdnet.ipynb"
SOURCE_METADATA = "kernel-metadata.json"
NEW_KERNEL_ID = "junhaochengadjcjh7u7/bc26-v90-attributed-youssef-e1-rare-tail-birdnet"
NEW_TITLE = "bc26-v90-attributed-youssef-e1-rare-tail-birdnet"


def source_checks(source_dir: Path) -> None:
    missing = [
        path
        for path in [
            source_dir / SOURCE_NOTEBOOK,
            source_dir / SOURCE_METADATA,
        ]
        if not path.exists()
    ]
    if missing:
        raise FileNotFoundError("missing source files: " + ", ".join(str(p) for p in missing))

    metadata = json.loads((source_dir / SOURCE_METADATA).read_text())
    if metadata.get("enable_gpu") is not False:
        raise ValueError("source metadata is not CPU-only: enable_gpu must be false")
    if metadata.get("enable_internet") is not False:
        raise ValueError("source metadata enables internet; expected false")
    if COMPETITION not in (metadata.get("competition_sources") or []):
        raise ValueError(f"source metadata is missing competition source {COMPETITION}")

    notebook = json.loads((source_dir / SOURCE_NOTEBOOK).read_text())
    kaggle_meta = notebook.get("metadata", {}).get("kaggle", {})
    if kaggle_meta.get("isGpuEnabled") is True:
        raise ValueError("notebook metadata indicates GPU is enabled")
    if kaggle_meta.get("isInternetEnabled") is True:
        raise ValueError("notebook metadata indicates internet is enabled")


def patch_notebook(path: Path) -> None:
    notebook = json.loads(path.read_text())
    patch_marker = "v90 safety patch"
    patched = False
    for cell in notebook.get("cells", []):
        source = cell.get("source", "")
        is_list = isinstance(source, list)
        text = "".join(source) if is_list else str(source)
        if patch_marker in text:
            patched = True
            continue
        needle = (
            'assert np.isfinite(sub_check[prob_cols].to_numpy()).all(), '
            '"Non-finite values found in probability columns."'
        )
        replacement = (
            '# v90 safety patch: make final diagnostics a hard submission gate.\\n'
            'assert not sub_check["row_id"].duplicated().any(), "Duplicate row_id values found."\\n'
            'expected_cols = ["row_id"] + PRIMARY_LABELS\\n'
            'assert sub_check.columns.tolist() == expected_cols, "Submission columns do not match sample_submission order."\\n'
            'assert sub_check["row_id"].astype(str).tolist() == sample_sub["row_id"].astype(str).tolist(), '
            '"Submission row order does not match sample_submission."\\n'
            + needle
        )
        if needle in text:
            text = text.replace(needle, replacement, 1)
            cell["source"] = text.splitlines(keepends=True) if is_list else text
            patched = True
            break
    if not patched:
        raise ValueError("expected final diagnostics assertion block not found")
    path.write_text(json.dumps(notebook, ensure_ascii=False) + "\n")


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
                "This candidate is an attributed public-reference derivative of",
                "`cocoaai/bc26-youssef-e1-rare-tail-birdnet`.",
                "",
                "Local changes are limited to candidate metadata and final safety checks:",
                "- keep CPU-only and no-internet metadata;",
                "- make duplicate-row, sample row-order, class-order, finite, and range checks hard gates;",
                "- do not claim this public-reference derivative as original work.",
                "",
                "It must complete Kaggle Run mode and pass candidate-specific audit before any real submission.",
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
    print("PLAN: materialize v90 as an attributed Run-mode candidate only; do not submit.")

    if not args.execute:
        print("DRY_RUN: no files written.")
        return 0

    materialize(args.source_dir, args.dest_dir, args.overwrite)
    print("MATERIALIZED:", args.dest_dir)
    print("NEXT: py_compile-equivalent JSON parse, Kaggle Run-mode push, output/runtime audit, then guarded decision.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
