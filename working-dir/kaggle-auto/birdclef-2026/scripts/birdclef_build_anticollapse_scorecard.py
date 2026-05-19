#!/usr/bin/env python3
"""Build a reusable anti-collapse candidate scorecard for BirdCLEF.

The goal is not to auto-pick a submit candidate blindly. It turns the current
workspace evidence into a ranked shortlist that prioritizes:

1. avoiding known collapse patterns;
2. preserving top5-like behavior;
3. preferring grouped/blocked stability over same-row optimism;
4. keeping compliance and real-score risk explicit.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
import sys

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))


@dataclass(frozen=True)
class CandidateSpec:
    candidate: str
    family: str
    evidence_type: str
    submit_window: str
    macro_proxy: float
    micro_proxy: float
    top1_proxy: float
    top5_proxy: float
    stability_signal: str
    compliance_state: str
    real_score: str
    runtime_status: str
    error_type: str
    same_family_recent_fail_count: int
    notes: str


def streak_count(ledger: pd.DataFrame, anchor_name: str) -> int:
    names = ledger["submission_name"].astype(str).tolist()
    if anchor_name not in names:
        return 0
    anchor_idx = names.index(anchor_name)
    later = ledger.iloc[anchor_idx + 1 :]
    count = 0
    anchor_score = pd.to_numeric(
        ledger.loc[ledger["submission_name"].eq(anchor_name), "public_lb_score_if_available"],
        errors="coerce",
    ).iloc[-1]
    for row in later.itertuples(index=False):
        raw = str(getattr(row, "public_lb_score_if_available", ""))
        score = pd.to_numeric(pd.Series([raw]), errors="coerce").iloc[0]
        if pd.isna(score):
            count += 1
            continue
        if score <= anchor_score:
            count += 1
        else:
            break
    return count


def collapse_bucket(spec: CandidateSpec) -> str:
    if spec.real_score not in {"", "nan"}:
        try:
            score = float(spec.real_score)
        except Exception:
            score = None
        if score is not None:
            if score < 0.90:
                return "very_high"
            if score < 0.93:
                return "high"
            if score < 0.949:
                return "medium"
            return "low"
    if spec.top5_proxy < 0.10:
        return "very_high"
    if "same family as v127" in spec.notes or "same-family" in spec.notes:
        return "medium_to_high"
    if "blocked" in spec.stability_signal or "leave-one-soundscape-out" in spec.stability_signal:
        return "low_to_medium"
    return "high"


def rank_tuple(spec: CandidateSpec) -> tuple:
    top5_ok = 1 if spec.top5_proxy >= 0.52054795 - 1e-9 else 0
    blocked = 1 if "blocked" in spec.stability_signal else 0
    compliance_clean = 1 if "clean" in spec.compliance_state.lower() or "pass" in spec.compliance_state.lower() else 0
    anti_family_fail = -spec.same_family_recent_fail_count
    risk_order = {
        "low": 5,
        "low_to_medium": 4,
        "medium": 3,
        "medium_to_high": 2,
        "high": 1,
        "very_high": 0,
    }[collapse_bucket(spec)]
    return (
        top5_ok,
        blocked,
        compliance_clean,
        anti_family_fail,
        spec.macro_proxy,
        spec.micro_proxy,
        spec.top5_proxy,
        risk_order,
    )


def main() -> int:
    experiments = ROOT / "experiments"
    output_csv = experiments / "v133_next_candidate_scorecard.csv"
    output_md = experiments / "v133_next_candidate_scorecard.md"

    ledger = pd.read_csv(experiments / "submission_ledger.csv")
    streak = streak_count(ledger, "v87-attributed-nina-eos5-v38plus")
    anchor_score = 0.949
    slot_pressure = int(ledger["submission_number_today"].dropna().astype(int).max())

    candidates = [
        CandidateSpec(
            "v134_stable3_guarded_rescue",
            "clean_router_component",
            "runmode_guarded_pool",
            "next_day_or_later",
            0.97979134,
            0.91924338,
            0.23287671,
            0.52054795,
            "blocked stable3 with positive rescue and top-hit guard",
            "HOLD-RUNMODE-PASS guarded pool",
            "",
            "runmode_complete",
            "",
            0,
            "same macro as v131 with slightly stronger anti-collapse guard, higher micro, and external Run-mode pass",
        ),
        CandidateSpec(
            "v131_stable3_top5aware",
            "clean_router_component",
            "blocked_top5aware",
            "next_day_or_later",
            0.97979134,
            0.91861043,
            0.23287671,
            0.52054795,
            "blocked top5-aware stable3 on v110/v114",
            "HOLD-clean component",
            "",
            "blocked_local_only",
            "",
            0,
            "stable3 component confirmed after v127 fallout",
        ),
        CandidateSpec(
            "v129_blocked_clean_router",
            "clean_router_grouped",
            "blocked_grouped",
            "next_day_or_later",
            0.97970207,
            0.91617178,
            0.24657534,
            0.52054795,
            "leave-one-soundscape-out gain with stable v112 triad",
            "HOLD-clean grouped evidence",
            "",
            "blocked_local_only",
            "",
            0,
            "grouped validation positive but weaker than v131",
        ),
        CandidateSpec(
            "v126_min10_w0.7_rankcal",
            "clean_router_broad",
            "same_row_support10",
            "local_only_until_extra_screen",
            0.98021860,
            0.91700965,
            0.23287671,
            0.52054795,
            "support>=10 macro gain without grouped proof",
            "PLAN-MATERIALIZE only",
            "",
            "runmode_only",
            "",
            2,
            "same family as v127; do not submit without stronger anti-collapse screen",
        ),
        CandidateSpec(
            "v103_guarded_macro_rescue",
            "original_macro_rescue",
            "same_row_high_proxy",
            "local_only_until_compliance_clear",
            0.98906455,
            0.92885549,
            0.38356164,
            0.71232877,
            "strongest proxy but no real-score proof",
            "HOLD-for-real-submit unknown-license",
            "",
            "runmode_only",
            "unknown_license",
            0,
            "mechanism-rich evidence not today's slot5",
        ),
        CandidateSpec(
            "v102_original_macro_rescue",
            "original_macro_rescue",
            "same_row_high_proxy",
            "local_only_until_compliance_clear",
            0.98897867,
            0.92916937,
            0.38356164,
            0.69863014,
            "strong proxy but weaker guard than v103",
            "HOLD mixed proxy",
            "",
            "runmode_only",
            "",
            0,
            "mechanism base not immediate submit",
        ),
        CandidateSpec(
            "v104_perch_only_guarded",
            "license_clean_perch_only",
            "same_row_clean_fallback",
            "do_not_submit",
            0.97751210,
            0.78763929,
            0.0,
            0.08219178,
            "license-clean but ranking collapse",
            "REJECT",
            "",
            "runmode_only",
            "top5_collapse",
            0,
            "retired",
        ),
        CandidateSpec(
            "v105_rankrestored_perch",
            "license_clean_perch_only",
            "same_row_clean_fallback",
            "do_not_submit",
            0.97751210,
            0.81765567,
            0.0,
            0.08219178,
            "small micro recovery but top5 still collapsed",
            "REJECT",
            "",
            "runmode_only",
            "top5_collapse",
            0,
            "retired",
        ),
        CandidateSpec(
            "v127_memorysafe_nontsubasa_router",
            "clean_router_broad",
            "real_submit",
            "retired",
            0.98008089,
            0.91595668,
            0.20547945,
            0.52054795,
            "real score invalidated same-family trust",
            "REJECT-score",
            "0.883",
            "public_lb_complete",
            "public_score_collapse",
            2,
            "real-score collapse; do not retry near-neighbor blindly",
        ),
    ]

    ranked = sorted(candidates, key=rank_tuple, reverse=True)
    rows = []
    for spec in ranked:
        rows.append(
            {
                "candidate": spec.candidate,
                "family": spec.family,
                "evidence_type": spec.evidence_type,
                "submit_window": spec.submit_window,
                "macro_proxy": f"{spec.macro_proxy:.8f}",
                "micro_proxy": f"{spec.micro_proxy:.8f}",
                "top1_proxy": f"{spec.top1_proxy:.8f}",
                "top5_proxy": f"{spec.top5_proxy:.8f}",
                "stability_signal": spec.stability_signal,
                "compliance_state": spec.compliance_state,
                "anchor_score": f"{anchor_score:.3f}",
                "delta_vs_anchor": "" if spec.real_score in {"", "nan"} else f"{float(spec.real_score) - anchor_score:.3f}",
                "evidence_level": spec.evidence_type,
                "non_positive_streak": streak,
                "same_family_recent_fail_count": spec.same_family_recent_fail_count,
                "runtime_status": spec.runtime_status,
                "error_type": spec.error_type,
                "slot_pressure": slot_pressure,
                "real_score": spec.real_score,
                "collapse_risk": collapse_bucket(spec),
                "notes": spec.notes,
            }
        )

    output_csv.parent.mkdir(parents=True, exist_ok=True)
    with output_csv.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    output_csv.write_text(output_csv.read_text(encoding="utf-8").replace("\r\n", "\n"), encoding="utf-8")

    md_lines = [
        "# v133 Next Candidate Scorecard",
        "",
        "Updated: 2026-05-19 11:34 UTC",
        "",
        "## Purpose",
        "",
        "After `v127 = 0.883`, the method-family gate is unlocked, but the next move must avoid another collapse. This scorecard turns the current evidence into a practical ranking for the next candidate window.",
        "",
        "## Ranking Logic",
        "",
        "Filter first:",
        "",
        "- reject branches with known collapse patterns such as `top1=0` or `top5` collapse;",
        "- reject unresolved `PENDING` or `ERROR-memory` candidates as immediate follow-ons;",
        "- reject broad same-family retries that do not add a stronger anti-collapse screen than `v127`.",
        "",
        "Rank second:",
        "",
        "- `macro` improvement matters;",
        "- `top5` must be preserved;",
        "- grouped / blocked stability is a strong positive;",
        "- compliance debt is a strong negative;",
        "- recent real-score collapse from the same family is a strong negative.",
        "",
        "## Current Ranking",
        "",
    ]
    for i, row in enumerate(rows, start=1):
        md_lines.append(f"{i}. `{row['candidate']}`")
        md_lines.append(
            f"   Evidence: macro `{row['macro_proxy']}`, micro `{row['micro_proxy']}`, top1 `{row['top1_proxy']}`, top5 `{row['top5_proxy']}`, `{row['stability_signal']}`."
        )
        md_lines.append(
            f"   Status: `{row['submit_window']}`, evidence `{row['evidence_level']}`, same-family recent fails `{row['same_family_recent_fail_count']}`, risk `{row['collapse_risk']}`, `{row['notes']}`."
        )
        md_lines.append("")
    md_lines.extend(
        [
            "## Current Guard",
            "",
            f"- Anchor remains `v87 = 0.949`.",
            f"- Completed non-positive streak after the anchor is `{streak}`.",
            "- Decision remains `NO-SLOT5-TODAY`; for the next real candidate window, start from the stable3 component rather than a broad near-neighbor of `v127`.",
            "",
        ]
    )
    output_md.write_text("\n".join(md_lines), encoding="utf-8")

    print(f"wrote {output_csv}")
    print(f"wrote {output_md}")
    print(f"anchor_streak={streak}")
    for row in rows[:8]:
        print(row["candidate"], row["collapse_risk"], row["submit_window"], row["macro_proxy"], row["top5_proxy"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
