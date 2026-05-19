#!/usr/bin/env python3
"""Build the v102 original macro-risk rescue table.

The table is an original meta-layer design input: it uses local OOF/per-class
evidence and training support to decide which classes should be protected,
shrunk, or rescued by a future CNN sidecar. It does not use hidden test labels
or manual listening.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "birdclef-2026" / "data"
EXPERIMENTS = ROOT / "experiments"


def explode_labels(labels: pd.DataFrame) -> pd.DataFrame:
    rows: list[tuple[str, str]] = []
    for row in labels.itertuples(index=False):
        for label in str(row.primary_label).split(";"):
            if label:
                rows.append((str(row.filename), label))
    return pd.DataFrame(rows, columns=["filename", "primary_label"])


def action_for(row: pd.Series) -> str:
    support = int(row["support"])
    base_auc = row["oof_base_auc"]
    prior_auc = row["oof_prior_auc"]
    class_group = str(row["class_name"])
    if pd.isna(base_auc):
        return "rare_prior_floor" if support > 0 else "no_oof_evidence"
    if support < 5:
        return "rare_prior_floor"
    if 5 <= support <= 150 and base_auc < 0.60:
        return "cnn_rescue_candidate"
    if class_group in {"Amphibia", "Insecta"} and not pd.isna(prior_auc) and prior_auc > base_auc + 0.08:
        return "texture_prior_rescue"
    if base_auc >= 0.85:
        return "protect_anchor"
    if base_auc < 0.70:
        return "mild_rescue"
    return "neutral"


def weights_for(action: str) -> tuple[float, float, float, float]:
    """Return anchor, sed, private_probe, cnn_sidecar class weights."""
    if action == "protect_anchor":
        return 0.70, 0.20, 0.10, 0.00
    if action == "cnn_rescue_candidate":
        return 0.35, 0.20, 0.15, 0.30
    if action == "texture_prior_rescue":
        return 0.45, 0.35, 0.15, 0.05
    if action == "rare_prior_floor":
        return 0.55, 0.25, 0.20, 0.00
    if action == "mild_rescue":
        return 0.50, 0.25, 0.15, 0.10
    return 0.60, 0.25, 0.15, 0.00


def main() -> int:
    sample = pd.read_csv(DATA / "sample_submission.csv", nrows=1)
    classes = sample.columns[1:].tolist()
    taxonomy = pd.read_csv(DATA / "taxonomy.csv").astype({"primary_label": str})
    labels = explode_labels(pd.read_csv(DATA / "train_soundscapes_labels.csv"))
    support = labels.groupby("primary_label").size().rename("support")

    per_class = pd.read_csv(EXPERIMENTS / "per_class_auc.csv")
    base = (
        per_class[
            (per_class["exp_id"] == "v87-attributed-nina-eos5-v38plus")
            & (per_class["prediction_key"] == "oof_base")
        ][["class_name", "auc"]]
        .rename(columns={"class_name": "primary_label", "auc": "oof_base_auc"})
        .astype({"primary_label": str})
    )
    prior = (
        per_class[
            (per_class["exp_id"] == "v87-attributed-nina-eos5-v38plus")
            & (per_class["prediction_key"] == "oof_prior")
        ][["class_name", "auc"]]
        .rename(columns={"class_name": "primary_label", "auc": "oof_prior_auc"})
        .astype({"primary_label": str})
    )

    out = pd.DataFrame({"primary_label": classes})
    out = out.merge(taxonomy[["primary_label", "common_name", "class_name"]], on="primary_label", how="left")
    out = out.merge(support, on="primary_label", how="left")
    out = out.merge(base, on="primary_label", how="left")
    out = out.merge(prior, on="primary_label", how="left")
    out["support"] = out["support"].fillna(0).astype(int)
    out["support_bucket"] = pd.cut(
        out["support"],
        bins=[-1, 0, 4, 20, 75, 150, 10_000],
        labels=["zero", "rare_1_4", "low_5_20", "mid_21_75", "mid_76_150", "high_151_plus"],
    ).astype(str)
    out["macro_risk_action"] = out.apply(action_for, axis=1)
    weights = np.array([weights_for(a) for a in out["macro_risk_action"]], dtype=np.float32)
    out["w_anchor"] = weights[:, 0]
    out["w_sed"] = weights[:, 1]
    out["w_private_probe"] = weights[:, 2]
    out["w_cnn_sidecar"] = weights[:, 3]
    out["risk_rank"] = (
        out["oof_base_auc"].fillna(0.0).rank(method="first", ascending=True)
        + out["support"].rank(method="first", ascending=True) * 0.01
    )
    out = out.sort_values(["macro_risk_action", "risk_rank", "primary_label"]).reset_index(drop=True)

    out_path = EXPERIMENTS / "v102_original_rescue_table.csv"
    out.to_csv(out_path, index=False)

    summary = (
        out.groupby("macro_risk_action", dropna=False)
        .agg(classes=("primary_label", "count"), mean_support=("support", "mean"), mean_base_auc=("oof_base_auc", "mean"))
        .reset_index()
        .sort_values("classes", ascending=False)
    )
    summary_path = EXPERIMENTS / "v102_original_rescue_summary.csv"
    summary.to_csv(summary_path, index=False)
    print("wrote", out_path, out.shape)
    print("wrote", summary_path, summary.shape)
    print(summary.to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
