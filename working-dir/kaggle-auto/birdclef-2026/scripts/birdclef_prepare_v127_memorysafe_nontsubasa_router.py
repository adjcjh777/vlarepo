#!/usr/bin/env python3
"""Prepare v127 memory-safe non-Tsubasa raw-side router.

v126 showed that a non-Tsubasa sparse class router remains positive after
removing the fragile one-positive class. Exact v126 materialization would need
to recompute v112/v119 final surfaces, which risks repeating the double-final
hidden-RAM failure seen in v120. v127 is the memory-safe adaptation:

- start from the single-final-layer v110 clean EcoProto anchor;
- compute only raw v112 Backtracking and v119 Roniheka side evidence after the
  clean final output is available;
- rank-calibrate each selected raw side column onto the clean anchor column;
- route only the support>=10 five-class set from v126.
"""

from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path


SOURCE_DIR = Path("birdclef-2026/notebooks/v110-ecoproto-clean-blend")
DEST_DIR = Path("birdclef-2026/notebooks/v127-memorysafe-nontsubasa-router")
NOTEBOOK = "submission.ipynb"
NEW_KERNEL_ID = "junhaochengadjcjh7u7/bc26-v127-nontsubasa-router"
NEW_TITLE = "bc26-v127-nontsubasa-router"


def _split_source(cell: dict) -> str:
    src = cell.get("source", "")
    if isinstance(src, list):
        return "".join(src)
    return str(src)


def _set_source(cell: dict, source: str) -> None:
    cell["source"] = source.splitlines(keepends=True)


def _router_cell() -> str:
    return r'''# V127 memory-safe non-Tsubasa router.
# This is a submission-path adaptation of the v126 support>=10 router.  It does
# not mount prior output CSVs and does not recompute side final layers.  Instead,
# it computes raw side evidence sequentially, rank-calibrates selected columns
# onto the clean v110 anchor, then unloads side sessions before saving.

v127_clean_anchor = final_probs.copy().astype(np.float32)

V127_SELECTED = [
    {"label": "47158son01", "source": "roniheka", "side_col": 30, "support_proxy": 11},
    {"label": "47158son13", "source": "backtracking", "side_col": 0, "support_proxy": 22},
    {"label": "47158son21", "source": "roniheka", "side_col": 50, "support_proxy": 20},
    {"label": "47158son22", "source": "backtracking", "side_col": 0, "support_proxy": 22},
    {"label": "47158son23", "source": "backtracking", "side_col": 0, "support_proxy": 22},
]
V127_PROXY_MAX_SUPPORT = 44.0
V127_WEIGHT = 0.70

def _v127_rankcal_column(side_col, anchor_col):
    side_col = np.asarray(side_col, dtype=np.float32)
    anchor_col = np.asarray(anchor_col, dtype=np.float32)
    out = np.empty_like(anchor_col, dtype=np.float32)
    order = np.argsort(side_col, kind="mergesort")
    out[order] = np.sort(anchor_col).astype(np.float32)
    return out

def _v127_support_gate(support_value):
    return float(np.clip(np.log1p(float(support_value)) / np.log1p(V127_PROXY_MAX_SUPPORT), 0.25, 1.0))

def _v127_run_backtracking_selected(paths, selected_cols, batch_files=16):
    sed_path = Path("/kaggle/input/datasets/backtracking/birdclef2026-clean-sed-b0/fold0_best_overall.onnx")
    if not sed_path.exists():
        hits = sorted(Path("/kaggle/input").rglob("fold0_best_overall.onnx"))
        if not hits:
            raise FileNotFoundError("V127 Backtracking SED model not found")
        sed_path = hits[0]
    opts = ort.SessionOptions()
    opts.intra_op_num_threads = 4
    opts.inter_op_num_threads = 1
    opts.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
    sess = ort.InferenceSession(str(sed_path), sess_options=opts, providers=["CPUExecutionProvider"])
    input_name = sess.get_inputs()[0].name
    out_map = {o.name: i for i, o in enumerate(sess.get_outputs())}
    out_idx = out_map.get("clip_logits", 0)
    print("V127 Backtracking side model:", sed_path)
    paths = [Path(p) for p in paths]
    rows = len(paths) * N_WINDOWS
    cols = sorted(set(int(c) for c in selected_cols))
    out = np.zeros((rows, len(cols)), dtype=np.float32)
    w = 0
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as io_executor:
        for start in tqdm(range(0, len(paths), batch_files), desc="V127 Backtracking raw side"):
            batch_paths = paths[start:start + batch_files]
            audio_batch = list(io_executor.map(read_audio, batch_paths))
            x = np.empty((len(batch_paths) * N_WINDOWS, WINDOW_SAMPLES), dtype=np.float32)
            br = w
            for bi, path in enumerate(batch_paths):
                x[bi*N_WINDOWS:(bi+1)*N_WINDOWS] = audio_batch[bi].reshape(N_WINDOWS, WINDOW_SAMPLES)
                w += N_WINDOWS
            logits = sess.run(None, {input_name: x})[out_idx].astype(np.float32)
            probs = 1.0 / (1.0 + np.exp(-np.clip(logits[:, cols], -50, 50)))
            out[br:w] = probs.astype(np.float32)
            del x, logits, probs, audio_batch
            gc.collect()
    del sess
    gc.collect()
    return {col: out[:, j].copy() for j, col in enumerate(cols)}

HGNET_N_MELS = 256
HGNET_N_FFT = 2048
HGNET_HOP = 512
HGNET_FMIN = 20
HGNET_FMAX = 16000
HGNET_TOP_DB = 80
HGNET_TIME = 313

def _v127_hgnet_mel_batch(chunks):
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

def _v127_run_roniheka_selected(paths, selected_cols, batch_files=8):
    root = Path("/kaggle/input/datasets/roniheka/birdclef-2026-a90v2-distilled-hgnet-onnx")
    model_paths = []
    for i in range(5):
        model_name = f"a90v2_fold{i}.onnx"
        cand = root / model_name
        if not cand.exists():
            hits = sorted(Path("/kaggle/input").rglob(model_name))
            if not hits:
                raise FileNotFoundError(f"V127 Roniheka HGNet model not found: {model_name}")
            cand = hits[0]
        model_paths.append(cand)
    opts = ort.SessionOptions()
    opts.intra_op_num_threads = 4
    opts.inter_op_num_threads = 1
    opts.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
    sessions = []
    for path in model_paths:
        sess = ort.InferenceSession(str(path), sess_options=opts, providers=["CPUExecutionProvider"])
        sessions.append((sess, sess.get_inputs()[0].name, {o.name: i for i, o in enumerate(sess.get_outputs())}, path))
        print("V127 Roniheka side model:", path)
    paths = [Path(p) for p in paths]
    rows = len(paths) * N_WINDOWS
    cols = sorted(set(int(c) for c in selected_cols))
    out = np.zeros((rows, len(cols)), dtype=np.float32)
    w = 0
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as io_executor:
        for start in tqdm(range(0, len(paths), batch_files), desc="V127 Roniheka raw side"):
            batch_paths = paths[start:start + batch_files]
            audio_batch = list(io_executor.map(read_audio, batch_paths))
            chunks = []
            br = w
            for path, audio in zip(batch_paths, audio_batch):
                chunks.extend(list(audio.reshape(N_WINDOWS, WINDOW_SAMPLES)))
                w += N_WINDOWS
            x = _v127_hgnet_mel_batch(chunks)
            acc = None
            for sess, input_name, out_map, path in sessions:
                outs = sess.run(None, {input_name: x})
                out_idx = out_map.get("logits", out_map.get("clip_logits", 0))
                logits = outs[out_idx].astype(np.float32)
                if logits.shape[1] != N_CLASSES:
                    raise ValueError(f"V127 HGNet class mismatch for {path}: {logits.shape[1]} vs {N_CLASSES}")
                acc = logits[:, cols] if acc is None else acc + logits[:, cols]
            probs = 1.0 / (1.0 + np.exp(-np.clip(acc / max(1, len(sessions)), -50, 50)))
            out[br:w] = probs.astype(np.float32)
            del x, acc, probs, outs, logits, chunks, audio_batch
            gc.collect()
    for sess, *_ in sessions:
        del sess
    gc.collect()
    return {col: out[:, j].copy() for j, col in enumerate(cols)}

backtracking_cols = [row["side_col"] for row in V127_SELECTED if row["source"] == "backtracking"]
roniheka_cols = [row["side_col"] for row in V127_SELECTED if row["source"] == "roniheka"]
v127_backtracking = _v127_run_backtracking_selected(test_paths, backtracking_cols) if backtracking_cols else {}
v127_roniheka = _v127_run_roniheka_selected(test_paths, roniheka_cols) if roniheka_cols else {}

v127_final = v127_clean_anchor.copy()
summary_rows = []
for row in V127_SELECTED:
    class_idx = label_to_idx[row["label"]]
    source_map = v127_backtracking if row["source"] == "backtracking" else v127_roniheka
    raw_side = source_map[int(row["side_col"])]
    rankcal = _v127_rankcal_column(raw_side, v127_clean_anchor[:, class_idx])
    gate = _v127_support_gate(row["support_proxy"])
    mix = V127_WEIGHT * gate
    v127_final[:, class_idx] = np.clip(
        (1.0 - mix) * v127_clean_anchor[:, class_idx] + mix * rankcal,
        0.0,
        1.0,
    ).astype(np.float32)
    summary_rows.append({
        "label": row["label"],
        "source": row["source"],
        "side_col": int(row["side_col"]),
        "support_proxy": int(row["support_proxy"]),
        "support_gate": gate,
        "mix": mix,
        "anchor_mean": float(v127_clean_anchor[:, class_idx].mean()),
        "side_mean": float(raw_side.mean()),
        "rankcal_mean": float(rankcal.mean()),
        "final_mean": float(v127_final[:, class_idx].mean()),
    })

final_probs = v127_final.astype(np.float32)
summary = pd.DataFrame(summary_rows)
summary.to_csv("v127_router_summary.csv", index=False)
pd.DataFrame([
    {
        "branch": "v110_clean_anchor",
        "min": float(v127_clean_anchor.min()),
        "max": float(v127_clean_anchor.max()),
        "mean": float(v127_clean_anchor.mean()),
        "std": float(v127_clean_anchor.std()),
    },
    {
        "branch": "v127_memorysafe_router",
        "min": float(final_probs.min()),
        "max": float(final_probs.max()),
        "mean": float(final_probs.mean()),
        "std": float(final_probs.std()),
    },
]).to_csv("v127_router_branch_summary.csv", index=False)
print("V127 selected router rows:")
print(summary)
print(f"V127 router changed cells: {len(V127_SELECTED)} columns over {len(final_probs)} rows")
print(f"V127 final score range: [{final_probs.min():.6f}, {final_probs.max():.6f}]")
print(f"V127 final score mean/std: {final_probs.mean():.6f}/{final_probs.std():.6f}")

del v127_backtracking, v127_roniheka, v127_clean_anchor, v127_final
gc.collect()
'''


def patch_notebook(path: Path) -> None:
    nb = json.loads(path.read_text())
    cells = nb["cells"]

    cells[0]["source"] = [
        "# BirdCLEF+ 2026 - V127 Original: Memory-Safe Non-Tsubasa Router\n",
        "\n",
        "Provenance: this notebook continues the license-clean v110/v125-v126 line. "
        "It excludes all Tsubasa branches, does not mount prior output CSVs, and "
        "uses only audited CC0 side model assets from Backtracking and Roniheka.\n",
        "\n",
        "Original experiment: v126 found a robust support>=10 non-Tsubasa class router "
        "but exact materialization would require recomputing side final layers. v127 "
        "keeps a single v110 clean final layer, then applies a post-final rank-calibrated "
        "raw-side router on five selected classes. Run-mode only until runtime, schema, "
        "proxy, correlation, and compliance evidence pass.\n",
    ]

    for cell in cells:
        src = _split_source(cell)
        src = src.replace("V110", "V127").replace("v110", "v127")
        src = src.replace("bc26-v110-ecoproto-cleanblend", "bc26-v127-nontsubasa-router")
        _set_source(cell, src)

    submit_idx = None
    for idx, cell in enumerate(cells):
        if "submission.to_csv(\"submission.csv\", index=False)" in _split_source(cell):
            submit_idx = idx
            break
    if submit_idx is None:
        raise ValueError("could not find submission cell")
    cells.insert(
        submit_idx,
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": _router_cell().splitlines(keepends=True),
        },
    )
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
                "backtracking/birdclef2026-clean-sed-b0",
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
                "This candidate continues the original v125-v126 non-Tsubasa router line.",
                "",
                "Original v127 change:",
                "- starts from the single-final-layer v110 clean EcoProto anchor;",
                "- excludes Tsubasa branches entirely;",
                "- computes raw Backtracking and Roniheka side evidence inside the notebook;",
                "- rank-calibrates only five support>=10 selected classes onto the clean anchor;",
                "- avoids prior output CSV mounts and side final-layer recomputation;",
                "- keeps CPU-only/no-internet metadata.",
                "",
                "Run-mode only until runtime, schema, proxy, correlation, and compliance evidence pass.",
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
    print("NEXT: JSON validate, static audit, Kaggle Run-mode push only.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
