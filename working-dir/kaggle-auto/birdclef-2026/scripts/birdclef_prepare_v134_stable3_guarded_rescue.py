#!/usr/bin/env python3
"""Prepare v134 stable3 guarded rescue notebook.

This is a narrow follow-up after v127 score collapse. Instead of the broader
five-class raw-side router, v134 keeps only the stable top5-preserving clean
component confirmed by v129/v130/v131:

- 47158son13
- 47158son22
- 47158son23

All three use the v112/backtracking side signal. The notebook also carries a
row-level top-hit guard inspired by v103 so the route remains explicitly
anti-collapse oriented.
"""

from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path


SOURCE_DIR = Path("birdclef-2026/notebooks/v110-ecoproto-clean-blend")
DEST_DIR = Path("birdclef-2026/notebooks/v134-stable3-guarded-rescue")
NOTEBOOK = "submission.ipynb"
NEW_KERNEL_ID = "junhaochengadjcjh7u7/bc26-v134-stable3-guarded-rescue"
NEW_TITLE = "bc26-v134-stable3-guarded-rescue"


def _split_source(cell: dict) -> str:
    src = cell.get("source", "")
    if isinstance(src, list):
        return "".join(src)
    return str(src)


def _set_source(cell: dict, source: str) -> None:
    cell["source"] = source.splitlines(keepends=True)


def _router_cell() -> str:
    return r'''# V134 stable3 guarded rescue.
# This is the narrow anti-collapse follow-up after v127. It keeps only the
# stable three-class clean component found by v129-v131 and adds a row-level
# top-hit preservation guard inspired by v103.

v134_clean_anchor = final_probs.copy().astype(np.float32)

V134_SELECTED = [
    {"label": "47158son13", "side_col": 0, "support_proxy": 22},
    {"label": "47158son22", "side_col": 0, "support_proxy": 22},
    {"label": "47158son23", "side_col": 0, "support_proxy": 22},
]
V134_PROXY_MAX_SUPPORT = 44.0
V134_WEIGHT = 0.90
V134_TOP1_THRESHOLD = 0.70
V134_TOP1_MARGIN = 0.08

def _v134_rankcal_column(side_col, anchor_col):
    side_col = np.asarray(side_col, dtype=np.float32)
    anchor_col = np.asarray(anchor_col, dtype=np.float32)
    out = np.empty_like(anchor_col, dtype=np.float32)
    order = np.argsort(side_col, kind="mergesort")
    out[order] = np.sort(anchor_col).astype(np.float32)
    return out

def _v134_support_gate(support_value):
    return float(np.clip(np.log1p(float(support_value)) / np.log1p(V134_PROXY_MAX_SUPPORT), 0.25, 1.0))

def _v134_run_backtracking_selected(paths, selected_cols, batch_files=16):
    sed_path = Path("/kaggle/input/datasets/backtracking/birdclef2026-clean-sed-b0/fold0_best_overall.onnx")
    if not sed_path.exists():
        hits = sorted(Path("/kaggle/input").rglob("fold0_best_overall.onnx"))
        if not hits:
            raise FileNotFoundError("V134 Backtracking SED model not found")
        sed_path = hits[0]
    opts = ort.SessionOptions()
    opts.intra_op_num_threads = 4
    opts.inter_op_num_threads = 1
    opts.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
    sess = ort.InferenceSession(str(sed_path), sess_options=opts, providers=["CPUExecutionProvider"])
    input_name = sess.get_inputs()[0].name
    out_map = {o.name: i for i, o in enumerate(sess.get_outputs())}
    out_idx = out_map.get("clip_logits", 0)
    print("V134 Backtracking side model:", sed_path)
    paths = [Path(p) for p in paths]
    rows = len(paths) * N_WINDOWS
    cols = sorted(set(int(c) for c in selected_cols))
    out = np.zeros((rows, len(cols)), dtype=np.float32)
    w = 0
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as io_executor:
        for start in tqdm(range(0, len(paths), batch_files), desc="V134 Backtracking raw side"):
            batch_paths = paths[start:start + batch_files]
            audio_batch = list(io_executor.map(read_audio, batch_paths))
            x = np.empty((len(batch_paths) * N_WINDOWS, WINDOW_SAMPLES), dtype=np.float32)
            br = w
            for bi, _path in enumerate(batch_paths):
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

backtracking_cols = [row["side_col"] for row in V134_SELECTED]
v134_backtracking = _v134_run_backtracking_selected(test_paths, backtracking_cols) if backtracking_cols else {}

top_order = np.argsort(v134_clean_anchor, axis=1)
top1_idx = top_order[:, -1]
top1_val = v134_clean_anchor[np.arange(len(v134_clean_anchor)), top1_idx]
top2_val = v134_clean_anchor[np.arange(len(v134_clean_anchor)), top_order[:, -2]]
confident_row = (top1_val >= V134_TOP1_THRESHOLD) & ((top1_val - top2_val) >= V134_TOP1_MARGIN)

v134_final = v134_clean_anchor.copy()
summary_rows = []
for row in V134_SELECTED:
    class_idx = label_to_idx[row["label"]]
    raw_side = v134_backtracking[int(row["side_col"])]
    rankcal = _v134_rankcal_column(raw_side, v134_clean_anchor[:, class_idx])
    gate = _v134_support_gate(row["support_proxy"])
    mix = V134_WEIGHT * gate
    candidate = np.clip(
        (1.0 - mix) * v134_clean_anchor[:, class_idx] + mix * rankcal,
        0.0,
        1.0,
    ).astype(np.float32)
    positive = candidate > v134_clean_anchor[:, class_idx]
    preserve = confident_row & (top1_idx != class_idx)
    mask = positive & ~preserve
    v134_final[mask, class_idx] = candidate[mask]
    summary_rows.append({
        "label": row["label"],
        "side_col": int(row["side_col"]),
        "support_proxy": int(row["support_proxy"]),
        "support_gate": gate,
        "mix": mix,
        "active_rows": int(mask.sum()),
        "anchor_mean": float(v134_clean_anchor[:, class_idx].mean()),
        "side_mean": float(raw_side.mean()),
        "rankcal_mean": float(rankcal.mean()),
        "final_mean": float(v134_final[:, class_idx].mean()),
    })

final_probs = v134_final.astype(np.float32)
summary = pd.DataFrame(summary_rows)
summary.to_csv("v134_guarded_summary.csv", index=False)
pd.DataFrame([
    {
        "branch": "v110_clean_anchor",
        "min": float(v134_clean_anchor.min()),
        "max": float(v134_clean_anchor.max()),
        "mean": float(v134_clean_anchor.mean()),
        "std": float(v134_clean_anchor.std()),
    },
    {
        "branch": "v134_stable3_guarded",
        "min": float(final_probs.min()),
        "max": float(final_probs.max()),
        "mean": float(final_probs.mean()),
        "std": float(final_probs.std()),
    },
]).to_csv("v134_guarded_branch_summary.csv", index=False)
print("V134 guarded rows:")
print(summary)
print(f"V134 final score range: [{final_probs.min():.6f}, {final_probs.max():.6f}]")
print(f"V134 final score mean/std: {final_probs.mean():.6f}/{final_probs.std():.6f}")

del v134_backtracking, v134_clean_anchor, v134_final
gc.collect()
'''


def patch_notebook(path: Path) -> None:
    nb = json.loads(path.read_text())
    cells = nb["cells"]

    cells[0]["source"] = [
        "# BirdCLEF+ 2026 - V134 Original: Stable3 Guarded Rescue\n",
        "\n",
        "Provenance: this notebook continues the clean original non-Tsubasa line, "
        "but narrows it to the stable three-class `v112` component after v127 "
        "collapsed on the public leaderboard.\n",
        "\n",
        "Original experiment: v129-v131 showed the stable top5-preserving component "
        "is `47158son13/22/23 + v112_backtracking_remap + positive`. v134 keeps "
        "that component and adds a row-level top-hit preservation guard inspired "
        "by v103. Run-mode only until runtime, schema, proxy, correlation, and "
        "compliance evidence pass.\n",
    ]

    for cell in cells:
        src = _split_source(cell)
        src = src.replace("V110", "V134").replace("v110", "v134")
        src = src.replace("bc26-v110-ecoproto-cleanblend", "bc26-v134-stable3-guarded-rescue")
        _set_source(cell, src)

    submit_idx = None
    for idx, cell in enumerate(cells):
        if 'submission.to_csv("submission.csv", index=False)' in _split_source(cell):
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
                "This candidate continues the original clean non-Tsubasa line.",
                "",
                "Original v134 change:",
                "- starts from the single-final-layer v110 clean EcoProto anchor;",
                "- narrows the route to the stable clean `v112` triad: 47158son13/22/23;",
                "- keeps only positive rescue updates for those three classes;",
                "- adds a row-level top-hit preservation guard inspired by v103;",
                "- avoids prior output CSV mounts and broad same-family expansion;",
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
