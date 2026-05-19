#!/usr/bin/env python3
"""Prepare v119 CC0 Roniheka HGNet SED EcoProto candidate.

v119 continues the license-clean v112/v114 line but swaps the weak
backtracking raw-audio SED branch for the CC0
`roniheka/birdclef-2026-a90v2-distilled-hgnet-onnx` five-fold HGNet ONNX
source. The downstream remap/trust/EcoProto logic stays workspace-original.
"""

from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path


SOURCE_DIR = Path("birdclef-2026/notebooks/v112-clean-sed-remap-ecoproto")
DEST_DIR = Path("birdclef-2026/notebooks/v119-roniheka-hgnet-sed")
NOTEBOOK = "submission.ipynb"
NEW_KERNEL_ID = "junhaochengadjcjh7u7/bc26-v119-roniheka-hgnet-sed"
NEW_TITLE = "bc26-v119-roniheka-hgnet-sed"


def _split_source(cell: dict) -> str:
    src = cell.get("source", "")
    if isinstance(src, list):
        return "".join(src)
    return str(src)


def _set_source(cell: dict, source: str) -> None:
    cell["source"] = source.splitlines(keepends=True)


def _hgnet_setup_source() -> str:
    return """# V119: audited CC0 Roniheka HGNet SED ensemble.
HGNET_ROOT = Path("/kaggle/input/datasets/roniheka/birdclef-2026-a90v2-distilled-hgnet-onnx")
HGNET_MODEL_NAMES = [f"a90v2_fold{i}.onnx" for i in range(5)]
HGNET_SED_PATHS = []
for model_name in HGNET_MODEL_NAMES:
    cand = HGNET_ROOT / model_name
    if not cand.exists():
        hits = sorted(Path("/kaggle/input").rglob(model_name))
        if not hits:
            raise FileNotFoundError(f"No Roniheka HGNet SED ONNX model found: {model_name}")
        cand = hits[0]
    HGNET_SED_PATHS.append(cand)

sed_opts = ort.SessionOptions()
sed_opts.intra_op_num_threads = 4
sed_opts.inter_op_num_threads = 1
sed_opts.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
clean_sed_sessions = []
for sed_path in HGNET_SED_PATHS:
    sess = ort.InferenceSession(str(sed_path), sess_options=sed_opts, providers=["CPUExecutionProvider"])
    input_name = sess.get_inputs()[0].name
    out_map = {o.name: i for i, o in enumerate(sess.get_outputs())}
    clean_sed_sessions.append((sess, input_name, out_map, sed_path))
    print("Using V119 Roniheka HGNet SED:", sed_path)
    print("HGNet SED inputs:", [(x.name, x.shape, x.type) for x in sess.get_inputs()])
    print("HGNet SED outputs:", [(x.name, x.shape, x.type) for x in sess.get_outputs()])
print(f"V119 Roniheka HGNet SED ensemble size: {len(clean_sed_sessions)}")
"""


def _replace_run_clean_sed_fast(source: str) -> str:
    start = source.find("def run_clean_sed_fast(")
    if start < 0:
        raise ValueError("run_clean_sed_fast not found")
    end = source.find("\n\ndef ", start + len("def run_clean_sed_fast("))
    if end < 0:
        end = len(source)
    replacement = r'''
HGNET_N_MELS = 256
HGNET_N_FFT = 2048
HGNET_HOP = 512
HGNET_FMIN = 20
HGNET_FMAX = 16000
HGNET_TOP_DB = 80
HGNET_TIME = 313

def _chunks_to_hgnet_mel_batch(chunks):
    batch = np.empty((len(chunks), 1, HGNET_N_MELS, HGNET_TIME), dtype=np.float32)
    for i, chunk in enumerate(chunks):
        mel = librosa.feature.melspectrogram(
            y=chunk,
            sr=SR,
            n_fft=HGNET_N_FFT,
            hop_length=HGNET_HOP,
            n_mels=HGNET_N_MELS,
            fmin=HGNET_FMIN,
            fmax=HGNET_FMAX,
            power=2.0,
        )
        mel = librosa.power_to_db(mel, top_db=HGNET_TOP_DB)
        mel = (mel - mel.mean()) / (mel.std() + 1e-6)
        if mel.shape[1] < HGNET_TIME:
            mel = np.pad(mel, ((0, 0), (0, HGNET_TIME - mel.shape[1])), mode="edge")
        batch[i, 0] = mel[:, :HGNET_TIME]
    return batch

def run_clean_sed_fast(paths, batch_files=8, desc="V119 HGNet SED inference"):
    """Run the audited CC0 HGNet SED ONNX ensemble over 12 five-second windows."""
    paths = [Path(p) for p in paths]
    rows = len(paths) * N_WINDOWS
    row_ids = np.empty(rows, object)
    fnames = np.empty(rows, object)
    logits_out = np.zeros((rows, N_CLASSES), np.float32)
    w = 0
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as io_executor:
        for start in tqdm(range(0, len(paths), batch_files), desc=desc):
            batch_paths = paths[start:start + batch_files]
            audio_batch = list(io_executor.map(read_audio, batch_paths))
            chunks = []
            br = w
            for path, audio in zip(batch_paths, audio_batch):
                chunks.extend(list(audio.reshape(N_WINDOWS, WINDOW_SAMPLES)))
                stem = path.stem
                row_ids[w:w+N_WINDOWS] = [f"{stem}_{t}" for t in range(5, 65, 5)]
                fnames[w:w+N_WINDOWS] = path.name
                w += N_WINDOWS
            x = _chunks_to_hgnet_mel_batch(chunks)
            logits_acc = None
            for sess, input_name, out_map, sed_path in clean_sed_sessions:
                outs = sess.run(None, {input_name: x})
                out_idx = out_map.get("logits", out_map.get("clip_logits", 0))
                logits = outs[out_idx].astype(np.float32)
                if logits.shape[1] != N_CLASSES:
                    raise ValueError(f"HGNet SED class mismatch for {sed_path}: {logits.shape[1]} vs {N_CLASSES}")
                logits_acc = logits if logits_acc is None else logits_acc + logits
            logits_out[br:w] = (logits_acc / max(1, len(clean_sed_sessions))).astype(np.float32)
            del x, logits, logits_acc, outs, audio_batch, chunks
            gc.collect()
    return pd.DataFrame({"row_id": row_ids, "filename": fnames}), logits_out
'''
    return source[:start] + replacement + source[end:]


def patch_notebook(path: Path) -> None:
    nb = json.loads(path.read_text())
    cells = nb["cells"]

    cells[0]["source"] = [
        "# BirdCLEF+ 2026 - V119 Original: Roniheka HGNet SED EcoProto\n",
        "\n",
        "Provenance: this notebook continues the clean v112/v114 line. It keeps "
        "unknown-license `jaejohn/perch-meta` and `tuckerarrants/bc2026-distilled-sed-public` "
        "out of runtime, rebuilds train Perch features in-notebook, and uses the "
        "CC0 `roniheka/birdclef-2026-a90v2-distilled-hgnet-onnx` five-fold ONNX "
        "source as the SED branch.\n",
        "\n",
        "Original experiment: v119 reuses the workspace-original train-window "
        "column remap, trust-strength calibration, and EcoProto/rank-launch clean "
        "blend, but tests a stronger clean HGNet SED source. Run-mode only; do not "
        "submit unless runtime, schema, proxy, correlation, and compliance evidence pass.\n",
    ]

    for cell in cells:
        src = _split_source(cell)
        src = src.replace("V112", "V119").replace("v112", "v119")
        src = src.replace("backtracking/birdclef2026-clean-sed-b0", "roniheka/birdclef-2026-a90v2-distilled-hgnet-onnx")
        src = src.replace("Clean SED", "Roniheka HGNet SED")
        src = src.replace("clean SED", "Roniheka HGNet SED")
        src = src.replace("clean_sed_remap", "roniheka_hgnet_sed_remap")
        src = src.replace("v119_Roniheka HGNet_sed_remap_diagnostics.csv", "v119_roniheka_hgnet_sed_remap_diagnostics.csv")
        src = src.replace("continues the clean v119/v114 line", "continues the clean v112/v114 line")
        src = src.replace("audited CC0 raw-audio SED", "audited CC0 HGNet mel SED")
        _set_source(cell, src)

    for cell in cells:
        src = _split_source(cell)
        if "CLEAN_SED_PATH" in src:
            _set_source(cell, _hgnet_setup_source())
            break
    else:
        raise ValueError("could not find clean SED setup cell")

    for cell in cells:
        src = _split_source(cell)
        if "def run_clean_sed_fast(" in src:
            _set_source(cell, _replace_run_clean_sed_fast(src))
            break
    else:
        raise ValueError("could not find clean SED helper cell")

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
                "roniheka/birdclef-2026-a90v2-distilled-hgnet-onnx",
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
                "This candidate continues the private original and clean v112/v114 line.",
                "",
                "Original v119 change:",
                "- uses the CC0 `roniheka/birdclef-2026-a90v2-distilled-hgnet-onnx` five-fold ONNX dataset;",
                "- replaces the weaker `backtracking/birdclef2026-clean-sed-b0` raw-audio branch;",
                "- keeps the workspace-original train-window remap and trust-strength calibration;",
                "- rebuilds train Perch features inside the Kaggle notebook;",
                "- avoids `jaejohn/perch-meta` and `tuckerarrants/bc2026-distilled-sed-public`;",
                "- keeps CPU-only/no-internet metadata and emits class-level remap diagnostics.",
                "",
                "Run-mode only until v119 runtime, schema, proxy, correlation, and compliance evidence pass.",
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
