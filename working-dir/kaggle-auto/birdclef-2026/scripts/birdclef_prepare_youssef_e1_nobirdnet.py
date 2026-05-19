#!/usr/bin/env python3
"""Prepare an attributed Youssef E1 rare-tail candidate with BirdNET disabled."""

from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path


COMPETITION = "birdclef-2026"
SOURCE_DIR = Path("/tmp/bc26_scan_may19/cocoa_youssef_e1")
DEST_DIR = Path("birdclef-2026/notebooks/v91-attributed-youssef-e1-rare-tail-nobirdnet")
SOURCE_NOTEBOOK = "bc26-youssef-e1-rare-tail-birdnet.ipynb"
SOURCE_METADATA = "kernel-metadata.json"
NEW_KERNEL_ID = "junhaochengadjcjh7u7/bc26-v91-attributed-youssef-e1-rare-tail-nobirdnet"
NEW_TITLE = "bc26-v91-attributed-youssef-e1-rare-tail-nobirdnet"


def source_checks(source_dir: Path) -> None:
    for name in [SOURCE_NOTEBOOK, SOURCE_METADATA]:
        if not (source_dir / name).exists():
            raise FileNotFoundError(source_dir / name)
    metadata = json.loads((source_dir / SOURCE_METADATA).read_text())
    if metadata.get("enable_gpu") is not False or metadata.get("enable_internet") is not False:
        raise ValueError("source metadata must be CPU-only and no-internet")
    if COMPETITION not in (metadata.get("competition_sources") or []):
        raise ValueError(f"source metadata is missing competition source {COMPETITION}")


def patch_notebook(path: Path) -> None:
    notebook = json.loads(path.read_text())
    patched_birdnet = False
    patched_checks = False
    for cell in notebook.get("cells", []):
        source = cell.get("source", "")
        is_list = isinstance(source, list)
        text = "".join(source) if is_list else str(source)
        needle = "_bn_model_path = _find_birdnet_model()\n_bn_labels_path = _find_birdnet_labels()"
        if needle in text:
            text = text.replace(
                needle,
                (
                    'print("BirdNET explicitly disabled for v91 license compatibility.")\n'
                    "_bn_model_path = None\n"
                    "_bn_labels_path = None"
                ),
                1,
            )
            patched_birdnet = True
        check_needle = (
            'assert np.isfinite(sub_check[prob_cols].to_numpy()).all(), '
            '"Non-finite values found in probability columns."'
        )
        if check_needle in text and "v91 safety patch" not in text:
            text = text.replace(
                check_needle,
                (
                    '# v91 safety patch: make final diagnostics a hard submission gate.\\n'
                    'assert not sub_check["row_id"].duplicated().any(), "Duplicate row_id values found."\\n'
                    'expected_cols = ["row_id"] + PRIMARY_LABELS\\n'
                    'assert sub_check.columns.tolist() == expected_cols, "Submission columns do not match sample_submission order."\\n'
                    'assert sub_check["row_id"].astype(str).tolist() == sample_sub["row_id"].astype(str).tolist(), '
                    '"Submission row order does not match sample_submission."\\n'
                    + check_needle
                ),
                1,
            )
            patched_checks = True
        cell["source"] = text.splitlines(keepends=True) if is_list else text
    if not patched_birdnet:
        raise ValueError("expected BirdNET model lookup block not found")
    if not patched_checks:
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
            "model_sources": [
                src
                for src in metadata.get("model_sources", [])
                if "birdnet-analyzer" not in src.lower()
            ],
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
                "Local changes:",
                "- BirdNET is explicitly disabled and its CC BY-NC model source is removed;",
                "- final duplicate-row, sample row-order, class-order, finite, and range checks are hard gates;",
                "- this remains an attributed public-reference derivative, not original work.",
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
    print("PLAN: materialize v91 with BirdNET disabled; do not submit.")
    if not args.execute:
        print("DRY_RUN: no files written.")
        return 0
    materialize(args.source_dir, args.dest_dir, args.overwrite)
    print("MATERIALIZED:", args.dest_dir)
    print("NEXT: Kaggle Run-mode push, output/runtime audit, then guarded decision.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
