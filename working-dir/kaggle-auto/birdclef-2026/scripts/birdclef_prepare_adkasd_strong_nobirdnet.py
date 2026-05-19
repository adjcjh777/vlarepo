#!/usr/bin/env python3
"""Prepare an attributed Adkasd strong candidate with BirdNET disabled.

This helper materializes a Kaggle Run-mode candidate only. It does not submit to
the competition.
"""

from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path


COMPETITION = "birdclef-2026"
SOURCE_DIR = Path("/tmp/bc26_scan_may19_turn2/adkasd_strong")
DEST_DIR = Path("birdclef-2026/notebooks/v93-attributed-adkasd-strong-nobirdnet")
SOURCE_NOTEBOOK = "birdclef-2026-sub-v4-5-strong.ipynb"
SOURCE_METADATA = "kernel-metadata.json"
NEW_KERNEL_ID = "junhaochengadjcjh7u7/bc26-v93-attributed-adkasd-strong-nobirdnet"
NEW_TITLE = "bc26-v93-attributed-adkasd-strong-nobirdnet"


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
    patched_birdnet = False
    for cell in notebook.get("cells", []):
        source = cell.get("source", "")
        is_list = isinstance(source, list)
        text = "".join(source) if is_list else str(source)

        if cell.get("cell_type") == "markdown":
            cell.pop("outputs", None)
            cell.pop("execution_count", None)
        elif cell.get("cell_type") == "code":
            cell["outputs"] = []
            cell["execution_count"] = None

        needle = "_bn_model_path  = _find_birdnet_model()\n    _bn_labels_path = _find_birdnet_labels()"
        if needle in text:
            text = text.replace(
                needle,
                (
                    'print("BirdNET explicitly disabled for v93 license compatibility.")\n'
                    "    _bn_model_path = None\n"
                    "    _bn_labels_path = None"
                ),
                1,
            )
            patched_birdnet = True
        cell["source"] = text.splitlines(keepends=True) if is_list else text

    if not patched_birdnet:
        raise ValueError("expected BirdNET model lookup block not found")

    notebook.setdefault("metadata", {}).setdefault("codex_v93_patch", {})
    notebook["metadata"]["codex_v93_patch"] = {
        "birdnet": "disabled",
        "outputs": "cleared_before_runmode_push",
        "intent": "runmode evidence only while v91 is pending",
    }
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
            "dataset_sources": [src for src in metadata.get("dataset_sources", []) if src],
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
                "`adkasd/birdclef-2026-sub-v4-5-strong`.",
                "",
                "Local changes:",
                "- clear executed notebook outputs before Kaggle Run-mode push;",
                "- remove an empty dataset source entry;",
                "- explicitly disable BirdNET and remove any BirdNET model source;",
                "- keep CPU-only/no-internet metadata.",
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
    print("PLAN: materialize v93 as Run-mode-only evidence; do not submit.")
    if not args.execute:
        print("DRY_RUN: no files written.")
        return 0
    materialize(args.source_dir, args.dest_dir, args.overwrite)
    print("MATERIALIZED:", args.dest_dir)
    print("NEXT: Kaggle Run-mode push, output/runtime audit, and decision brief.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
