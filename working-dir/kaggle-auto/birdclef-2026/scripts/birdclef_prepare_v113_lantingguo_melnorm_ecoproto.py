#!/usr/bin/env python3
"""Prepare v113 LantingGuo MelNorm SED EcoProto blend from v103.

v113 removes runtime dependencies with unknown Kaggle metadata licenses:
- jaejohn/perch-meta
- tuckerarrants/bc2026-distilled-sed-public

It audits a second CC0 Kaggle SED ONNX asset and adds an original MelNormProbe:
two mel normalization views are run on train/test soundscape windows, then each
class gets a shrunken train-window reliability gate before the SED branch can
influence EcoProto. The goal is to test a different clean SED family without
blindly copying another notebook's preprocessing assumptions.
"""

from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path


SOURCE_DIR = Path("birdclef-2026/notebooks/v103-guarded-macro-risk-rescue")
DEST_DIR = Path("birdclef-2026/notebooks/v113-lantingguo-melnorm-ecoproto")
NOTEBOOK = "submission.ipynb"
NEW_KERNEL_ID = "junhaochengadjcjh7u7/bc26-v113-lanting-melnorm"
NEW_TITLE = "bc26-v113-lanting-melnorm"


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
        "# BirdCLEF+ 2026 - V113 Original: LantingGuo MelNorm SED EcoProto Blend\n",
        "\n",
        "Provenance: this notebook continues the private original v86/v102/v103 fast-ONNX line. "
        "Like v104, it removes the unknown-license runtime dependencies `jaejohn/perch-meta` "
        "and `tuckerarrants/bc2026-distilled-sed-public`. Train Perch features are rebuilt "
        "inside the Kaggle notebook from competition train soundscapes using the public Perch "
        "ONNX bundle. The SED branch uses the audited CC0 `lantingguo/"
        "birdclef2026-own-sed-b0-v5-onnx` ONNX asset instead of unknown-license public SED/cache.\n",
        "\n",
        "Experiment: v113 keeps the EcoProto clean-blend structure but adds MelNormProbe: "
        "two 128-mel normalization views are run, class-wise reliability is estimated from "
        "train soundscape windows, and weak classes are shrunk back toward the Perch-only "
        "surrogate. "
        "Run-mode only; do not submit unless proxy and "
        "compliance evidence justify it.\n",
    ]

    # Metadata/cache discovery cell: remove unknown-license cache lookup.
    cache_cell = "".join(cells[3]["source"])
    cache_start = cache_cell.index("CACHE_DIR = None")
    cache_cell = (
        cache_cell[:cache_start]
        + 'CACHE_DIR = None\nprint("External Perch cache disabled for v113 LantingGuo MelNorm run")\n'
    )
    cells[3]["source"] = cache_cell.splitlines(keepends=True)

    # Cell 7 only needs filename parsing; cached arrays are rebuilt after run_perch_fast exists.
    cell7 = "".join(cells[7]["source"])
    cell7 = cell7.split('assert CACHE_DIR is not None, "Cache not found!"')[0]
    cell7 += 'print("V113: Perch train cache will be rebuilt in-notebook after inference helpers are defined")\n'
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
    helper_src += """

LANTING_MEL_VARIANTS = ("zscore", "minmax")
LANTING_N_MELS = 128
LANTING_N_FFT = 2048
LANTING_HOP = 512
LANTING_FMIN = 20
LANTING_FMAX = 16000
LANTING_TOP_DB = 80

def _chunk_to_lanting_mel(chunk, variant):
    mel = librosa.feature.melspectrogram(
        y=chunk, sr=SR, n_fft=LANTING_N_FFT, hop_length=LANTING_HOP,
        n_mels=LANTING_N_MELS, fmin=LANTING_FMIN, fmax=LANTING_FMAX,
        power=2.0,
    )
    mel = librosa.power_to_db(mel, top_db=LANTING_TOP_DB).astype(np.float32)
    if variant == "zscore":
        mel = (mel - mel.mean()) / (mel.std() + 1e-6)
    elif variant == "minmax":
        mel = (mel - mel.min()) / (mel.max() - mel.min() + 1e-6)
    else:
        raise ValueError(f"Unknown mel variant: {variant}")
    return mel.astype(np.float32)

def _chunks_to_lanting_batch(chunks, variant):
    mels = [_chunk_to_lanting_mel(chunk, variant) for chunk in chunks]
    max_t = max(m.shape[1] for m in mels)
    batch = np.empty((len(mels), 1, LANTING_N_MELS, max_t), dtype=np.float32)
    for i, mel in enumerate(mels):
        if mel.shape[1] < max_t:
            mel = np.pad(mel, ((0, 0), (0, max_t - mel.shape[1])), mode="edge")
        batch[i, 0] = mel[:, :max_t]
    return batch

def run_lanting_sed_fast(paths, variant, batch_files=12, desc="LantingGuo SED inference"):
    \"\"\"Run the audited CC0 128-mel SED ONNX model over 12 five-second windows.\"\"\"
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
            for bi, path in enumerate(batch_paths):
                audio = audio_batch[bi]
                chunks.extend(list(audio.reshape(N_WINDOWS, WINDOW_SAMPLES)))
                stem = path.stem
                row_ids[w:w+N_WINDOWS] = [f"{stem}_{t}" for t in range(5, 65, 5)]
                fnames[w:w+N_WINDOWS] = path.name
                w += N_WINDOWS
            x = _chunks_to_lanting_batch(chunks, variant)
            outs = lanting_sed_session.run(None, {lanting_sed_input_name: x})
            logits = outs[lanting_sed_out_map.get("logits", 0)].astype(np.float32)
            if logits.shape[1] != N_CLASSES:
                raise ValueError(f"LantingGuo SED class mismatch: {logits.shape[1]} vs {N_CLASSES}")
            logits_out[br:w] = logits
            del x, logits, outs, audio_batch, chunks
            gc.collect()
    return pd.DataFrame({"row_id": row_ids, "filename": fnames}), logits_out
"""
    test_src = split_token + test_src_tail
    test_src = test_src.replace(
        'print("Test spatial features:", None if spatial_test is None else spatial_test.shape)\n',
        'print("Test spatial features:", None if spatial_test is None else spatial_test.shape)\n'
        'lanting_test_logits_by_variant = {}\n'
        'for _variant in LANTING_MEL_VARIANTS:\n'
        '    lanting_sed_meta_test, _logits = run_lanting_sed_fast(test_paths, _variant, desc=f"V113 LantingGuo SED test {_variant}")\n'
        '    assert lanting_sed_meta_test["row_id"].astype(str).tolist() == meta_test["row_id"].astype(str).tolist(), "LantingGuo SED row order mismatch"\n'
        '    lanting_test_logits_by_variant[_variant] = _logits\n'
        'print("LantingGuo SED test logits:", {k: v.shape for k, v in lanting_test_logits_by_variant.items()})\n',
    )

    clean_sed_setup_src = """# V113: audited CC0 LantingGuo 128-mel SED model.
LANTING_SED_PATH = Path("/kaggle/input/datasets/lantingguo/birdclef2026-own-sed-b0-v5-onnx/sed_b0.onnx")
if not LANTING_SED_PATH.exists():
    hits = sorted(Path("/kaggle/input").rglob("sed_b0.onnx"))
    if not hits:
        raise FileNotFoundError("No LantingGuo SED ONNX model found")
    LANTING_SED_PATH = hits[0]
sed_opts = ort.SessionOptions()
sed_opts.intra_op_num_threads = 4
sed_opts.inter_op_num_threads = 1
sed_opts.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
lanting_sed_session = ort.InferenceSession(str(LANTING_SED_PATH), sess_options=sed_opts, providers=["CPUExecutionProvider"])
lanting_sed_input_name = lanting_sed_session.get_inputs()[0].name
lanting_sed_out_map = {o.name: i for i, o in enumerate(lanting_sed_session.get_outputs())}
print("Using LantingGuo clean SED:", LANTING_SED_PATH)
print("LantingGuo SED inputs:", [(x.name, x.shape, x.type) for x in lanting_sed_session.get_inputs()])
print("LantingGuo SED outputs:", [(x.name, x.shape, x.type) for x in lanting_sed_session.get_outputs()])
"""

    build_train_src = """# V113: rebuild train Perch and LantingGuo clean SED features in-notebook.
train_paths = [BASE / "train_soundscapes" / fn for fn in full_files]
train_paths = [p for p in train_paths if p.exists()]
print(f"V113 rebuilding Perch train features for {len(train_paths)} files")
meta_full, scores_full_raw, emb_full, _spatial_train_unused = run_perch_fast(
    train_paths, capture_spatial=False, desc="V113 Perch train feature rebuild"
)
meta_full = meta_full.set_index("row_id").loc[full_rows["row_id"].astype(str)].reset_index()
scores_full_raw = scores_full_raw[: len(meta_full)]
emb_full = emb_full[: len(meta_full)]
assert np.all(meta_full["filename"].values == full_rows["filename"].values)
print(f"V113 rebuilt train features: meta={meta_full.shape}, scores={scores_full_raw.shape}, emb={emb_full.shape}")

lanting_train_logits_by_variant = {}
for _variant in LANTING_MEL_VARIANTS:
    lanting_sed_meta_full, _logits = run_lanting_sed_fast(
        train_paths, _variant, desc=f"V113 LantingGuo SED train {_variant}"
    )
    lanting_sed_meta_full = lanting_sed_meta_full.set_index("row_id").loc[full_rows["row_id"].astype(str)].reset_index()
    _logits = _logits[: len(lanting_sed_meta_full)]
    assert np.all(lanting_sed_meta_full["filename"].values == full_rows["filename"].values)
    lanting_train_logits_by_variant[_variant] = _logits
print("V113 rebuilt LantingGuo train logits:", {k: v.shape for k, v in lanting_train_logits_by_variant.items()})
"""

    # Replace unknown-license SED branch with the audited CC0 LantingGuo MelNormProbe view.
    sed_surrogate_src = """# V113 license-clean branch: LantingGuo MelNormProbe.
def _sigmoid_np(x):
    return (1.0 / (1.0 + np.exp(-np.clip(x, -50, 50)))).astype(np.float32)

variant_train_probs = {k: _sigmoid_np(v) for k, v in lanting_train_logits_by_variant.items()}
variant_test_probs = {k: _sigmoid_np(v) for k, v in lanting_test_logits_by_variant.items()}
variant_auc = {}
for name, probs in variant_train_probs.items():
    aucs = []
    for ci in range(N_CLASSES):
        y = Y_FULL[:, ci]
        if y.sum() == 0 or y.sum() == len(y):
            aucs.append(np.nan)
        else:
            aucs.append(roc_auc_score(y, probs[:, ci]))
    variant_auc[name] = np.array(aucs, dtype=np.float32)

variant_names = list(LANTING_MEL_VARIANTS)
auc_stack = np.vstack([variant_auc[v] for v in variant_names])
safe_auc_stack = np.nan_to_num(auc_stack, nan=0.50)
best_variant_idx = np.argmax(safe_auc_stack, axis=0).astype(np.int32)
best_auc = safe_auc_stack[best_variant_idx, np.arange(N_CLASSES)].astype(np.float32)
second_auc = np.partition(safe_auc_stack, -2, axis=0)[-2].astype(np.float32)
sed_quality = np.clip((best_auc - 0.54) / 0.30, 0.0, 1.0).astype(np.float32)
sed_margin = np.clip((best_auc - second_auc) / 0.10, 0.0, 1.0).astype(np.float32)
sed_trust = (0.18 + 0.64 * sed_quality * (0.55 + 0.45 * sed_margin)).astype(np.float32)
sed_trust[best_auc < 0.58] = 0.0
sed_trust[np.nan_to_num(Y_FULL.sum(axis=0), nan=0) < 2] = 0.0

perch_surrogate = _sigmoid_np(scores_test)
sed_selected = np.zeros_like(perch_surrogate, dtype=np.float32)
for ci in range(N_CLASSES):
    sed_selected[:, ci] = variant_test_probs[variant_names[int(best_variant_idx[ci])]][:, ci]

# Shrink weak or ambiguous mel classes back toward Perch-only behavior. This
# avoids v111/v112-style strong clean-SED failure while preserving a different
# low-correlation signal where the train-window evidence is credible.
trust_2d = sed_trust.reshape(1, -1)
sed_probs = ((1.0 - trust_2d) * perch_surrogate + trust_2d * sed_selected).astype(np.float32)
sed_rows = meta_test["row_id"].astype(str).tolist()
assert sed_rows == meta_test["row_id"].astype(str).tolist(), "LantingGuo SED row_id order mismatch"
sed_per_class_auc = best_auc.astype(np.float32)

mel_diag = pd.DataFrame({
    "primary_label": PRIMARY_LABELS,
    "support": Y_FULL.sum(axis=0).astype(int),
    "best_variant": [variant_names[int(i)] for i in best_variant_idx],
    "best_auc": best_auc,
    "second_auc": second_auc,
    "sed_quality": sed_quality,
    "sed_margin": sed_margin,
    "sed_trust": sed_trust,
})
for name in variant_names:
    mel_diag[f"auc_{name}"] = variant_auc[name]
mel_diag.to_csv("v113_lantingguo_melnorm_diagnostics.csv", index=False)
print(f"V113 LantingGuo MelNorm view: shape={sed_probs.shape}, range=[{sed_probs.min():.6f}, {sed_probs.max():.6f}]")
print(f"V113 MelNorm trust: active={(sed_trust > 0).sum()}/{N_CLASSES}, mean/max={sed_trust.mean():.4f}/{sed_trust.max():.4f}")
print(f"V113 LantingGuo train AUC ref: mean={np.nanmean(sed_per_class_auc):.4f}, min={np.nanmin(sed_per_class_auc):.4f}, active={(np.isfinite(sed_per_class_auc)).sum()}")
print("V113 MelNorm diagnostics saved: v113_lantingguo_melnorm_diagnostics.csv")
"""

    final_cell = "".join(cells[15]["source"])
    final_cell = final_cell.replace(
        "# V103 original guarded macro-risk rescue policy.",
        "# V111 original EcoProto clean-blend guarded macro-risk rescue policy.",
    ).replace(
        "# This is a conservative follow-up to v102: keep the class-wise OOF/taxa/support\n# rescue idea, but only let it strongly move cells when the rescue view is\n# locally stronger than the conservative v84-like anchor. A row-level top-hit\n# guard protects high-confidence primary calls from macro rescue spillover.",
        "# This is a license-reduced follow-up to v103: keep the class-wise OOF/taxa/support\n# rescue idea, but remove SED/cache runtime dependencies with unknown licenses.\n# Rescue strength is now driven by clean SED plus Perch/probe views.",
    ).replace(
        "texture_prior_rescue = texture_taxa & mid_support & (sed_advantage > 0.08)",
        "texture_prior_rescue = texture_taxa & mid_support & (sed_advantage > 0.10)",
    ).replace(
        "rescue_mix[macro_mild] = 0.18\nrescue_mix[macro_weak] = 0.38\nrescue_mix[macro_weak & texture_taxa] = 0.48\nrescue_mix[texture_prior_rescue] = np.maximum(rescue_mix[texture_prior_rescue], 0.28)",
        "rescue_mix[macro_mild] = 0.12\nrescue_mix[macro_weak] = 0.28\nrescue_mix[macro_weak & texture_taxa] = 0.34\nrescue_mix[texture_prior_rescue] = np.maximum(rescue_mix[texture_prior_rescue], 0.18)",
    ).replace(
        "V103 guarded macro-risk rescue counts",
        "V111 EcoProto clean-blend guarded macro-risk rescue counts",
    ).replace(
        "V103 class rescue mix range/mean",
        "V111 class rescue mix range/mean",
    ).replace(
        "V103 effective rescue mix range/mean",
        "V111 effective rescue mix range/mean",
    ).replace(
        "V103 components:",
        "V111 components:",
    ).replace(
        "View mix: v103 = v102 original macro-risk rescue plus positive-rescue and top-hit guards",
        "View mix: v111 = self-contained v107-like rank ceiling plus EcoProto rank-launch clean blend",
    )
    restore_block = """
clean_guarded_base = final_probs.copy()

# V111 EcoProto rescue. This is an original, license-clean signal built only
# from competition labels plus Perch embeddings. It avoids external SED assets:
# each class gets a train-window embedding prototype; a test row is rescued only
# when prototype similarity, site/hour prior, and temporal neighborhood agree.
def _norm_rows(x):
    x = np.asarray(x, dtype=np.float32)
    return x / (np.linalg.norm(x, axis=1, keepdims=True) + 1e-6)

def _ecoproto_rank():
    if emb_test is None:
        print("V111 EcoProto unavailable: no embedding output")
        return view_perch, np.zeros((len(meta_test), N_CLASSES), dtype=np.float32), np.zeros(N_CLASSES, dtype=bool)
    cache_pos = _cache_positions_for_full_rows()
    x_train = _norm_rows(emb_full.astype(np.float32)[cache_pos])
    x_test = _norm_rows(emb_test.astype(np.float32))
    prototypes = np.zeros((N_CLASSES, x_train.shape[1]), dtype=np.float32)
    active = np.zeros(N_CLASSES, dtype=bool)
    for ci in range(N_CLASSES):
        pos = np.flatnonzero(Y_FULL[:, ci] > 0)
        if len(pos) >= 2:
            prototypes[ci] = _norm_rows(x_train[pos].mean(axis=0, keepdims=True))[0]
            active[ci] = True
    sim = x_test @ prototypes.T
    sim[:, ~active] = np.nanmedian(sim[:, active]) if active.any() else 0.0
    sim = np.nan_to_num(sim, nan=0.0).astype(np.float32)
    centered = sim - np.median(sim, axis=0, keepdims=True)
    scaled = centered / (np.std(centered, axis=0, keepdims=True) + 1e-4)
    proto_prob = (1.0 / (1.0 + np.exp(-1.65 * np.clip(scaled, -6, 6)))).astype(np.float32)
    proto_rank = _rank_power(proto_prob, 0.72)
    print(f"V111 EcoProto active classes: {int(active.sum())}/{N_CLASSES}; sim range=[{sim.min():.4f},{sim.max():.4f}]")
    return proto_rank.astype(np.float32), proto_prob.astype(np.float32), active

proto_rank, proto_prob, proto_active = _ecoproto_rank()
eco_base = _rank_power(0.58 * proto_rank + 0.22 * prior_rank + 0.12 * view_perch + 0.08 * probe_consensus_probs, 0.82)
row_proto_peak = proto_rank.max(axis=1, keepdims=True)
row_proto_strength = np.clip((row_proto_peak - 0.58) / 0.32, 0.0, 1.0).astype(np.float32)
class_eco_gate = (
    proto_active
    & mid_support
    & (~protect_anchor)
    & (~rare_floor)
    & (perch_auc_cal_ref < 0.82)
).astype(np.float32)
class_eco_mix = (0.10 + 0.30 * np.clip((0.82 - perch_auc_cal_ref) / 0.32, 0.0, 1.0)).astype(np.float32)
class_eco_mix *= class_eco_gate
eco_mix = np.clip(row_proto_strength * class_eco_mix.reshape(1, -1), 0.0, 0.34).astype(np.float32)
final_probs = ((1.0 - eco_mix) * final_probs + eco_mix * eco_base).astype(np.float32)

# Temporal agreement rescue: raise a class only when adjacent windows also carry
# prototype evidence. This targets continuous vocal activity and avoids a global
# rank-ceiling push.
eco_pv = eco_base.reshape(len(test_paths), N_WINDOWS, N_CLASSES).copy()
eco_ctx = eco_pv.copy()
for ii in range(1, N_WINDOWS - 1):
    eco_ctx[:, ii] = 0.62 * eco_pv[:, ii] + 0.19 * eco_pv[:, ii - 1] + 0.19 * eco_pv[:, ii + 1]
eco_ctx[:, 0] = 0.86 * eco_pv[:, 0] + 0.14 * eco_pv[:, 1]
eco_ctx[:, -1] = 0.86 * eco_pv[:, -1] + 0.14 * eco_pv[:, -2]
eco_ctx = eco_ctx.reshape(-1, N_CLASSES).astype(np.float32)
temporal_mask = (eco_ctx > np.maximum(final_probs + 0.035, 0.72)) & (eco_mix > 0.06)
temporal_mix = np.where(temporal_mask, 0.13, 0.0).astype(np.float32)
final_probs = ((1.0 - temporal_mix) * final_probs + temporal_mix * eco_ctx).astype(np.float32)

# Keep v84 confident winners protected; EcoProto is a rescue sidecar, not a
# replacement for high-confidence anchor classes.
final_probs = np.where(top_hit_guard, 0.94 * v84_like + 0.06 * final_probs, final_probs).astype(np.float32)
print(f"V111 EcoProto cells: mix={int((eco_mix > 0).sum())}, temporal={int(temporal_mask.sum())}, class_gate={int(class_eco_gate.sum())}")
print(f"V111 EcoProto mix mean/max: {eco_mix.mean():.5f}/{eco_mix.max():.5f}; temporal mean={temporal_mix.mean():.5f}")
print(f"V111 post-EcoProto score range: [{final_probs.min():.6f}, {final_probs.max():.6f}]")
print(f"V111 post-EcoProto score mean/std: {final_probs.mean():.6f}/{final_probs.std():.6f}")

# V111 self-contained clean blend. First reconstruct a v107-like rank-ceiling
# branch from the pre-EcoProto guarded base, then combine it with the v109-like
# EcoProto rank-launch branch. This materializes the local probe without
# depending on prior output CSVs as Kaggle inputs.
v109_like_probs = final_probs.copy()
v107_rank_view = _rank_power(
    0.50 * view_sedfirst + 0.24 * view_perch + 0.18 * probe_consensus_probs + 0.08 * view_adaptive,
    0.62,
).astype(np.float32)
v107_restore_mask = (~rare_guard) & (~protect_guard)
v107_restore_mix = np.where(v107_restore_mask, 0.88, 0.0).astype(np.float32)
v107_like_probs = ((1.0 - v107_restore_mix) * clean_guarded_base + v107_restore_mix * v107_rank_view).astype(np.float32)
v107_top = v107_rank_view.max(axis=1, keepdims=True)
v107_top_guard = (v107_rank_view >= (v107_top - 0.030)) & (v107_top >= 0.72) & (~rare_guard)
v107_like_probs = np.where(v107_top_guard, 0.20 * v107_like_probs + 0.80 * v107_rank_view, v107_like_probs).astype(np.float32)

# The v109-like branch uses EcoProto as one term in the rank-launch view rather
# than as a standalone conservative rescue. The guard remains class-aware and
# excludes rare/protected classes.
rank_launch_view = _rank_power(
    0.42 * view_sedfirst
    + 0.18 * view_perch
    + 0.18 * probe_consensus_probs
    + 0.16 * eco_base
    + 0.06 * view_adaptive,
    0.62,
).astype(np.float32)
launch_mask = (~rare_guard) & (~protect_guard)
launch_mix = np.where(launch_mask, 0.78, 0.0).astype(np.float32)
final_probs = ((1.0 - launch_mix) * final_probs + launch_mix * rank_launch_view).astype(np.float32)

rank_top = rank_launch_view.max(axis=1, keepdims=True)
rank_top_guard = (rank_launch_view >= (rank_top - 0.030)) & (rank_top >= 0.72) & (~rare_guard)
final_probs = np.where(rank_top_guard, 0.22 * final_probs + 0.78 * rank_launch_view, final_probs).astype(np.float32)
v109_like_probs = final_probs.copy()

final_probs = (0.40 * v107_like_probs + 0.60 * v109_like_probs).astype(np.float32)
print(f"V111 v107-like cells: restore={int(v107_restore_mask.sum())}, top_guard={int(v107_top_guard.sum())}")
print(f"V111 EcoProto rank-launch cells: launch={int(launch_mask.sum())}, top_guard={int(rank_top_guard.sum())}")
print(f"V111 clean blend weights: v107_like=0.40, v109_like=0.60")
print(f"V111 post-cleanblend score range: [{final_probs.min():.6f}, {final_probs.max():.6f}]")
print(f"V111 post-cleanblend score mean/std: {final_probs.mean():.6f}/{final_probs.std():.6f}")
"""
    final_cell = final_cell.replace(
        'print(f"Score mean/std: {final_probs.mean():.6f}/{final_probs.std():.6f}")\n',
        'print(f"Score mean/std: {final_probs.mean():.6f}/{final_probs.std():.6f}")\n' + restore_block,
    )
    cells[15]["source"] = final_cell.splitlines(keepends=True)

    # Reorder: helpers -> train rebuild -> OOF cells -> test inference -> SED surrogate -> final.
    new_cells = []
    new_cells.extend(cells[:9])  # includes label construction in cell 8
    new_cells.append(_code_cell(clean_sed_setup_src))
    new_cells.append(_code_cell(helper_src))
    new_cells.append(_code_cell(build_train_src))
    new_cells.extend(cells[9:13])  # OOF/calibration/thresholds
    new_cells.append(_code_cell(test_src))
    new_cells.append(_code_cell(sed_surrogate_src))
    new_cells.extend(cells[15:])
    nb["cells"] = new_cells
    for cell in nb["cells"]:
        src = cell.get("source")
        if isinstance(src, list):
            src_text = "".join(src).replace("V111", "V113").replace("v111", "v113")
            cell["source"] = src_text.splitlines(keepends=True)
        elif isinstance(src, str):
            cell["source"] = src.replace("V111", "V113").replace("v111", "v113")

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
                "lantingguo/birdclef2026-own-sed-b0-v5-onnx",
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
                "This candidate continues the private original v86/v102/v103/v104-v112 line.",
                "",
                "Original v113 change:",
                "- removes unknown-license runtime dependencies `jaejohn/perch-meta` and `tuckerarrants/bc2026-distilled-sed-public`;",
                "- rebuilds train Perch features inside the Kaggle notebook from competition train soundscapes;",
                "- replaces the unknown-license SED branch with `lantingguo/birdclef2026-own-sed-b0-v5-onnx` (CC0-1.0);",
                "- adds MelNormProbe: zscore and minmax 128-mel views with per-class train-window trust shrinkage;",
                "- keeps the v103-v106 positive-rescue and top-hit guard idea with conservative class rescue strengths;",
                "- adds EcoProto: class embedding prototypes from competition labels, gated by site/hour priors and temporal consistency;",
                "- self-replays a v107-like rank-ceiling branch and a v109-like EcoProto rank-launch branch;",
                "- blends the two clean branches at 0.40/0.60 to preserve the v110 clean fallback structure;",
                "- keeps CPU-only/no-internet metadata and public, recorded Perch plus clean SED inputs.",
                "",
                "Run-mode only until v113 runtime, schema, proxy, and compliance evidence pass.",
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
