#!/usr/bin/env python3
"""Build a pending-safe candidate queue from existing BirdCLEF outputs.

This script is intentionally local-only. It does not submit anything to Kaggle.
It helps decide what can be researched while a real submission is pending by
ranking existing output artifacts by local proxy quality, diversity, and known
submission status.
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path
import re
import sys

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from src.metrics import binary_roc_auc, multilabel_macro_auc  # noqa: E402


def labels_to_targets(meta: pd.DataFrame, labels: pd.DataFrame, class_names: list[str]) -> np.ndarray:
    label_map: dict[str, set[str]] = {}
    for row in labels.itertuples(index=False):
        try:
            end_sec = int(str(row.end).split(":")[-1])
        except Exception:
            continue
        key = f"{Path(str(row.filename)).stem}_{end_sec}"
        label_map[key] = {x for x in str(row.primary_label).split(";") if x}

    class_index = {c: i for i, c in enumerate(class_names)}
    y = np.zeros((len(meta), len(class_names)), dtype=np.uint8)
    for i, row_id in enumerate(meta["row_id"].astype(str).tolist()):
        for lab in label_map.get(row_id, set()):
            j = class_index.get(lab)
            if j is not None:
                y[i, j] = 1
    return y


def topk_hit_rate(y_true: np.ndarray, y_score: np.ndarray, k: int) -> float | None:
    rows = np.where(y_true.sum(axis=1) > 0)[0]
    if len(rows) == 0:
        return None
    hits = 0
    for i in rows:
        top = np.argpartition(y_score[i], -k)[-k:]
        if y_true[i, top].any():
            hits += 1
    return hits / len(rows)


def candidate_key(path: Path) -> str:
    text = str(path)
    match = re.search(r"/outputs/(v\d+[^/]*)/", text)
    if match:
        return match.group(1)
    return path.parent.name


def load_submission(path: Path, class_names: list[str]) -> pd.DataFrame:
    df = pd.read_csv(path)
    missing = [c for c in ["row_id", *class_names] if c not in df.columns]
    if missing:
        raise ValueError(f"{path} missing {missing[:5]}")
    return df[["row_id", *class_names]].copy()


def ledger_status(ledger: pd.DataFrame, key: str) -> tuple[str, str]:
    if ledger.empty:
        return "", ""
    v_match = re.match(r"(v\d+)", key)
    short = v_match.group(1) if v_match else key
    rows = ledger[ledger["submission_name"].astype(str).str.contains(short, regex=False, na=False)]
    if rows.empty:
        return "", ""
    row = rows.iloc[-1]
    return str(row.get("public_lb_score_if_available", "")), str(row.get("decision_reason", ""))


def candidate_action_note(key: str, public_status: str, decision: str) -> str:
    if key.startswith("v103") or key.startswith("v102"):
        return (
            "highest local proxy; do not submit as-is because unknown-license dependencies remain; "
            "next research should reproduce the useful guard/rescue signal with clean in-notebook evidence"
        )
    if key.startswith("v121"):
        return "strong original sparse sidecar, but inherits v120 hidden-RAM risk; only useful as design evidence"
    if key.startswith("v120") or "ERROR-memory" in public_status or "memory" in decision.lower():
        return "retired hidden-test memory failure; do not queue for real submit"
    if key.startswith("v127"):
        return "current guarded real submission is pending; lock further real submits until score/error resolves"
    if key.startswith("v110") or key.startswith("v114"):
        return "clean anchor/reference branch; useful as compliance-safe baseline rather than aggressive slot candidate"
    return "research-only queue item; require compliance/runtime/proxy review before any guarded submission"


def corr_or_blank(a: np.ndarray, b: np.ndarray | None) -> str:
    if b is None or a.shape != b.shape:
        return ""
    return f"{float(np.corrcoef(a.ravel(), b.ravel())[0, 1]):.8f}"


def mad_or_blank(a: np.ndarray, b: np.ndarray | None) -> str:
    if b is None or a.shape != b.shape:
        return ""
    return f"{float(np.mean(np.abs(a - b))):.8f}"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", type=Path, default=ROOT / "birdclef-2026/data")
    parser.add_argument("--outputs-dir", type=Path, default=ROOT / "birdclef-2026/outputs")
    parser.add_argument("--ledger", type=Path, default=ROOT / "experiments/submission_ledger.csv")
    parser.add_argument("--output-csv", type=Path, default=ROOT / "experiments/v128_pending_safe_candidate_queue.csv")
    args = parser.parse_args()

    sample = pd.read_csv(args.data_dir / "sample_submission.csv", nrows=1)
    class_names = list(sample.columns[1:])
    labels = pd.read_csv(args.data_dir / "train_soundscapes_labels.csv")
    ledger = pd.read_csv(args.ledger) if args.ledger.exists() else pd.DataFrame()

    all_shapes: dict[str, tuple[int, int]] = {}
    submissions: dict[str, tuple[Path, pd.DataFrame, np.ndarray]] = {}
    for path in sorted(args.outputs_dir.glob("*/submission.csv")):
        try:
            df = load_submission(path, class_names)
        except Exception as exc:
            print(f"skip {path}: {exc}")
            continue
        key = candidate_key(path)
        all_shapes[key] = df.shape
        if len(df) < 10:
            continue
        values = df[class_names].to_numpy(dtype=np.float64)
        submissions[key] = (path, df, values)

    refs = {}
    for ref_key in [
        "v87-attributed-nina-eos5-v38plus-v2",
        "v91-attributed-youssef-e1-rare-tail-nobirdnet-v1",
        "v110-ecoproto-clean-blend-v1",
        "v127-memorysafe-nontsubasa-router-v1",
    ]:
        if ref_key in submissions:
            refs[ref_key] = submissions[ref_key][2]

    rows: list[dict[str, object]] = []
    for key, (path, df, values) in submissions.items():
        y_true = labels_to_targets(df[["row_id"]], labels, class_names)
        if y_true.sum() == 0:
            continue
        macro = multilabel_macro_auc(y_true, values, class_names)
        micro = binary_roc_auc(y_true.ravel(), values.ravel())
        top1 = topk_hit_rate(y_true, values, 1)
        top5 = topk_hit_rate(y_true, values, 5)
        public_score, decision = ledger_status(ledger, key)
        reference_note = (
            "v87/v91 archived outputs are sample-only locally, so train-window diversity is measured against v110/v127"
            if "v87-attributed-nina-eos5-v38plus-v2" in all_shapes
            and all_shapes["v87-attributed-nina-eos5-v38plus-v2"][0] < 10
            else ""
        )
        rows.append(
            {
                "key": key,
                "path": str(path.relative_to(ROOT)),
                "macro_auc": "" if macro["mean_auc"] is None else f"{macro['mean_auc']:.8f}",
                "micro_auc": "" if micro is None else f"{micro:.8f}",
                "top1_hit": "" if top1 is None else f"{top1:.8f}",
                "top5_hit": "" if top5 is None else f"{top5:.8f}",
                "scored_classes": macro["scored_classes"],
                "corr_v87": corr_or_blank(values, refs.get("v87-attributed-nina-eos5-v38plus-v2")),
                "mad_v87": mad_or_blank(values, refs.get("v87-attributed-nina-eos5-v38plus-v2")),
                "corr_v91": corr_or_blank(values, refs.get("v91-attributed-youssef-e1-rare-tail-nobirdnet-v1")),
                "corr_v110": corr_or_blank(values, refs.get("v110-ecoproto-clean-blend-v1")),
                "corr_v127": corr_or_blank(values, refs.get("v127-memorysafe-nontsubasa-router-v1")),
                "public_score_or_status": public_score,
                "ledger_decision": decision,
                "family": "original" if "-original-" in key or key.startswith("v10") or key.startswith("v11") or key.startswith("v12") else "attributed_or_mixed",
                "queue_action_note": candidate_action_note(key, public_score, decision),
                "reference_note": reference_note,
            }
        )

    rows.sort(key=lambda r: float(r["macro_auc"] or -1), reverse=True)
    args.output_csv.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        raise RuntimeError("No valid candidate rows found")
    with args.output_csv.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    print(f"wrote {args.output_csv} rows={len(rows)}")
    for row in rows[:15]:
        print(
            row["key"],
            row["macro_auc"],
            row["top5_hit"],
            row["corr_v87"],
            row["corr_v127"],
            row["public_score_or_status"],
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
