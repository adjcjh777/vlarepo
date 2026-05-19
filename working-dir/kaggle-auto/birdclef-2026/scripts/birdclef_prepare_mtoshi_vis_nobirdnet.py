#!/usr/bin/env python3
"""Prepare an attributed Mtoshi visual/Proto-SED candidate with BirdNET disabled.

This helper only materializes a local Kaggle Run-mode candidate. It never
submits to the competition.
"""

from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path


COMPETITION = "birdclef-2026"
SOURCE_DIR = Path("/tmp/bc26_scan_may19_round2/beicicc_mtoshi_vis")
DEST_DIR = Path("birdclef-2026/notebooks/v92-attributed-mtoshi-vis-nobirdnet")
SOURCE_NOTEBOOK = "bc26-mtoshi-vis-may18.ipynb"
SOURCE_METADATA = "kernel-metadata.json"
NEW_KERNEL_ID = "junhaochengadjcjh7u7/bc26-v92-attributed-mtoshi-vis-nobirdnet"
NEW_TITLE = "bc26-v92-attributed-mtoshi-vis-nobirdnet"


def source_checks(source_dir: Path) -> None:
    for name in [SOURCE_NOTEBOOK, SOURCE_METADATA]:
        if not (source_dir / name).exists():
            raise FileNotFoundError(source_dir / name)
    metadata = json.loads((source_dir / SOURCE_METADATA).read_text())
    if metadata.get("enable_gpu") is not False:
        raise ValueError("source metadata is not CPU-only")
    if metadata.get("enable_internet") is not False:
        raise ValueError("source metadata enables internet")
    if COMPETITION not in (metadata.get("competition_sources") or []):
        raise ValueError(f"source metadata is missing competition source {COMPETITION}")


def patch_notebook(path: Path) -> None:
    notebook = json.loads(path.read_text())
    cells = notebook.get("cells", [])
    if cells:
        first = cells[0]
        first["cell_type"] = "code"
        first["source"] = [
            'print("v92 safety patch: removed non-inference flow diagram dependency.")\n',
        ]
        first["outputs"] = []
        first["execution_count"] = None

    patched_birdnet = False
    patched_checks = False
    for cell in cells:
        source = cell.get("source", "")
        is_list = isinstance(source, list)
        text = "".join(source) if is_list else str(source)
        if "birdclef-flow-diagram" in text or "IPython.display import Image" in text:
            cell["cell_type"] = "code"
            cell["source"] = [
                'print("v92 safety patch: skipped original flow diagram display cell.")\n',
            ]
            cell["outputs"] = []
            cell["execution_count"] = None
            continue
        needle = "_bn_model_path = _find_birdnet_model()\n_bn_labels_path = _find_birdnet_labels()"
        if needle in text:
            text = text.replace(
                needle,
                (
                    'print("BirdNET explicitly disabled for v92 license compatibility.")\n'
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
        if check_needle in text and "v92 safety patch" not in text:
            text = text.replace(
                check_needle,
                (
                    '# v92 safety patch: make final diagnostics a hard submission gate.\\n'
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
            "dataset_sources": [
                src
                for src in metadata.get("dataset_sources", [])
                if "birdclef-flow-diagram" not in src.lower()
            ],
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
                "`beicicc/bc26-mtoshi-vis-may18`.",
                "",
                "Local changes:",
                "- remove the flow-diagram display dependency;",
                "- explicitly disable BirdNET and remove any BirdNET model source;",
                "- keep CPU-only/no-internet metadata;",
                "- add hard final row-order, column-order, finite, duplicate-row, and range checks.",
                "",
                "This is Run-mode evidence only while v91 is pending. Do not submit it without",
                "a fresh candidate-specific decision brief and rules compliance pass.",
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
    print("PLAN: materialize v92 as Run-mode-only evidence; do not submit.")
    if not args.execute:
        print("DRY_RUN: no files written.")
        return 0
    materialize(args.source_dir, args.dest_dir, args.overwrite)
    print("MATERIALIZED:", args.dest_dir)
    print("NEXT: Kaggle Run-mode push, output/runtime audit, and decision brief.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
