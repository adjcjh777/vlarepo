#!/usr/bin/env python3
"""Guarded BirdCLEF 2026 code-submission helper for vetted candidates.

Default mode is dry-run. Use --execute only after checking the current UTC day
quota and candidate order in the decision log.
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from datetime import datetime, timezone

from kaggle.api.kaggle_api_extended import KaggleApi


COMPETITION = "birdclef-2026"
FILE_NAME = "submission.csv"


@dataclass(frozen=True)
class Candidate:
    kernel: str
    version: int
    message: str
    priority_note: str


CANDIDATES: dict[str, Candidate] = {
    "v76": Candidate(
        kernel="junhaochengadjcjh7u7/bc26-v76-original-macroboost-dualprobe",
        version=1,
        message=(
            "Original private fast-ONNX dual-probe macro-boost v76; "
            "CPU-safe Run-mode ~254s; no public notebook code copied"
        ),
        priority_note="first slot after UTC reset",
    ),
    "v83": Candidate(
        kernel="junhaochengadjcjh7u7/bc26-v83-original-supportband-probeplus",
        version=1,
        message=(
            "Original private support-band probe-plus v83; CPU-safe Run-mode ~169s; "
            "submit only after v76 public feedback supports this direction"
        ),
        priority_note="second slot if v76 is promising",
    ),
    "v84": Candidate(
        kernel="junhaochengadjcjh7u7/bc26-v84-original-mlpaux-supportband",
        version=1,
        message=(
            "Original private MLP-aux support-band v84; CPU-safe Run-mode ~205s; "
            "conservative alternate behind v83"
        ),
        priority_note="alternate second slot behind v83",
    ),
    "v79": Candidate(
        kernel="junhaochengadjcjh7u7/bc26-v79-original-supportgate-dualprobe",
        version=1,
        message=(
            "Original private support-gated dual-probe v79; CPU-safe Run-mode ~247s; "
            "safe fallback if v76 underperforms"
        ),
        priority_note="fallback if v76 underperforms",
    ),
    "v85": Candidate(
        kernel="junhaochengadjcjh7u7/bc26-v85-original-eosprivate-overlapgate",
        version=1,
        message=(
            "Original private EoS-inspired rank-power overlap-gated v85; "
            "fresh post-v76/v79 candidate; CPU-only Run-mode validated; no public notebook code copied"
        ),
        priority_note="fresh candidate after v76/v79 both scored 0.925; submit only after audit",
    ),
    "v86": Candidate(
        kernel="junhaochengadjcjh7u7/bc26-v86-original-midsupport-proberescue",
        version=1,
        message=(
            "Original private mid-support probe-rescue v86; conservative v84 anchor plus "
            "controlled v70-style probe signal; CPU-only Run-mode validated; no public notebook code copied"
        ),
        priority_note="fresh candidate after v85 was too aggressive; submit only after audit",
    ),
    "v87": Candidate(
        kernel="junhaochengadjcjh7u7/bc26-v87-attributed-nina-eos5-v38plus",
        version=2,
        message=(
            "Attributed public-reference derivative of nina2025/birdclef-2026-eos-5; "
            "v87 anchors on prior 0.948 public-reference result and uses EoS5 0.04/0.96 "
            "Model_2+rank-power-0.949 blend; CPU-only Run-mode COMPLETE; not original work"
        ),
        priority_note="fresh v38-anchor public-reference improvement candidate after original v86 scored 0.925",
    ),
    "v88": Candidate(
        kernel="junhaochengadjcjh7u7/bc26-v88-attributed-zeyad-eos-parity-t3",
        version=1,
        message=(
            "Attributed public-reference derivative of zeyadmohamadezzat/birdclef-2026-eos-parity-inference; "
            "v88 EOS Parity T3 uses quantile-mix rank blend with four Proto/SED variants; "
            "CPU-only Run-mode COMPLETE; final-slot candidate after v87 scored 0.949"
        ),
        priority_note="fifth-slot candidate only after v88 Run-mode output, runtime, provenance, and material-difference checks pass",
    ),
    "v90": Candidate(
        kernel="junhaochengadjcjh7u7/bc26-v90-attributed-youssef-e1-rare-tail-birdnet",
        version=1,
        message=(
            "Attributed public-reference derivative of cocoaai/bc26-youssef-e1-rare-tail-birdnet; "
            "v90 adds BirdNET unmapped-species weighting, sonotype mirroring, and rare low-tail suppression; "
            "CPU-only Run-mode COMPLETE; not original work"
        ),
        priority_note="first UTC 2026-05-19 slot after v87=0.949/v88=0.921; submit only after v90 audit passes",
    ),
    "v91": Candidate(
        kernel="junhaochengadjcjh7u7/bc26-v91-attributed-youssef-e1-rare-tail-nobirdnet",
        version=1,
        message=(
            "Attributed public-reference derivative of cocoaai/bc26-youssef-e1-rare-tail-birdnet with "
            "BirdNET disabled for license compatibility; v91 keeps Proto/SED rare-tail and sonotype gates; "
            "CPU-only Run-mode COMPLETE; not original work"
        ),
        priority_note="first UTC 2026-05-19 submission candidate after v90 was held for BirdNET CC BY-NC risk",
    ),
    "v120": Candidate(
        kernel="junhaochengadjcjh7u7/bc26-v120-clean-tsubasa-sidecar",
        version=1,
        message=(
            "Original clean v120: Perch-only clean anchor plus 0.15 CC0 Tsubasa ConvNeXt SED sidecar; "
            "CPU-only Run-mode COMPLETE ~683s; no unknown-license runtime inputs"
        ),
        priority_note="third UTC 2026-05-19 slot candidate; bold clean macro-proxy uplift over v110/v114",
    ),
    "v127": Candidate(
        kernel="junhaochengadjcjh7u7/bc26-v127-nontsubasa-router",
        version=1,
        message=(
            "Original clean v127: memory-safe non-Tsubasa raw-side router over v110 EcoProto anchor; "
            "CPU-only Run-mode COMPLETE ~390s; Backtracking/Roniheka CC0 side evidence; no prior CSV mounts"
        ),
        priority_note="fourth UTC 2026-05-19 slot candidate; memory-safe original non-Tsubasa router after v120 RAM failure",
    ),
}


def utc_day_prefix() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def score_float(value: object) -> float | None:
    try:
        text = str(value)
        if not text:
            return None
        return float(text)
    except (TypeError, ValueError):
        return None


def is_candidate_submission(sub: object, candidate: str) -> bool:
    candidate = candidate.lower()
    haystack = " ".join(
        str(x or "")
        for x in [
            getattr(sub, "description", ""),
            getattr(sub, "url", ""),
            getattr(sub, "file_name", ""),
        ]
    ).lower()
    return bool(
        re.search(rf"\bbc26-{re.escape(candidate)}(?:-|/|\b)", haystack)
        or re.search(rf"\b{re.escape(candidate)}(?:;|,)", haystack)
    )


def print_recent_submissions(subs: list[object]) -> None:
    for i, sub in enumerate(subs[:8], 1):
        print(
            i,
            sub.date,
            "|",
            sub.status,
            "| score=",
            repr(sub.public_score),
            "| err=",
            repr(sub.error_description),
            "|",
            (sub.description or "")[:160],
        )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--candidate",
        choices=sorted(CANDIDATES),
        default="v76",
        help="vetted candidate key to submit",
    )
    parser.add_argument("--execute", action="store_true", help="actually submit to Kaggle")
    parser.add_argument(
        "--max-today",
        type=int,
        default=0,
        help="refuse if visible submissions for current UTC date exceed this count",
    )
    parser.add_argument(
        "--require-complete",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="require Kaggle kernel status to be COMPLETE before submission",
    )
    parser.add_argument(
        "--allow-before-v76-score",
        action="store_true",
        help="override the second-slot guard that waits for v76 public score",
    )
    parser.add_argument(
        "--allow-strategy-mismatch",
        action="store_true",
        help="override v83/v84/v79 score-direction checks after v76 scores",
    )
    parser.add_argument(
        "--allow-resubmit",
        action="store_true",
        help="override duplicate-candidate protection after the same candidate already has a scored row",
    )
    parser.add_argument(
        "--promising-score",
        type=float,
        default=0.948,
        help="v76 public score threshold that unlocks v83/v84 by default",
    )
    args = parser.parse_args()

    candidate = CANDIDATES[args.candidate]
    api = KaggleApi()
    api.authenticate()

    today = utc_day_prefix()
    subs = api.competition_submissions(COMPETITION)[:20]
    today_subs = [s for s in subs if str(s.date).startswith(today)]

    print(f"utc_today={today}")
    print(f"visible_today_count={len(today_subs)}")
    print_recent_submissions(subs)

    if len(today_subs) > args.max_today:
        print(
            f"REFUSE: current UTC day already has {len(today_subs)} visible submissions "
            f"(max_today={args.max_today}).",
            file=sys.stderr,
        )
        return 2

    status = api.kernels_status(candidate.kernel)
    print("candidate_key=", args.candidate)
    print("candidate_kernel=", candidate.kernel)
    print("candidate_version=", candidate.version)
    print("candidate_file=", FILE_NAME)
    print("candidate_priority=", candidate.priority_note)
    print("candidate_status=", status)
    print("candidate_message=", candidate.message)

    if args.require_complete and "COMPLETE" not in str(status):
        print(f"REFUSE: candidate status is not COMPLETE: {status}", file=sys.stderr)
        return 3

    existing_candidate_row = next((s for s in subs if is_candidate_submission(s, args.candidate)), None)
    existing_candidate_score = (
        score_float(getattr(existing_candidate_row, "public_score", "")) if existing_candidate_row else None
    )
    if existing_candidate_score is not None and not args.allow_resubmit:
        print(
            f"REFUSE: {args.candidate} already has a scored submission "
            f"({existing_candidate_score}); create a fresh candidate instead of resubmitting.",
            file=sys.stderr,
        )
        return 9

    if args.candidate != "v76" and not args.allow_before_v76_score:
        v76_row = next((s for s in subs if is_candidate_submission(s, "v76")), None)
        v76_score = score_float(getattr(v76_row, "public_score", "")) if v76_row else None
        print("v76_gate_row_found=", v76_row is not None)
        print("v76_gate_score=", v76_score)
        if v76_row is None:
            print("REFUSE: v76 submission row not found; submit/monitor v76 first.", file=sys.stderr)
            return 4
        if getattr(v76_row, "error_description", ""):
            print(
                f"REFUSE: v76 row has error: {getattr(v76_row, 'error_description', '')}",
                file=sys.stderr,
            )
            return 5
        if v76_score is None:
            print("REFUSE: v76 public score is not available yet; wait before slot two.", file=sys.stderr)
            return 6
        if not args.allow_strategy_mismatch:
            if args.candidate in {"v83", "v84"} and v76_score < args.promising_score:
                print(
                    f"REFUSE: {args.candidate} requires v76_score >= {args.promising_score}; "
                    f"got {v76_score}. Use v79 or override explicitly if needed.",
                    file=sys.stderr,
                )
                return 7
            if args.candidate == "v79" and v76_score >= args.promising_score:
                print(
                    f"REFUSE: v79 is the fallback path, but v76_score >= {args.promising_score}. "
                    "Use v83/v84 or override explicitly if needed.",
                    file=sys.stderr,
                )
                return 8

    if not args.execute:
        print("DRY_RUN: pass --execute after confirming quota reset and candidate choice.")
        return 0

    response = api.competition_submit_code(
        FILE_NAME,
        candidate.message,
        COMPETITION,
        kernel=candidate.kernel,
        kernel_version=candidate.version,
        quiet=False,
    )
    print("SUBMIT_RESPONSE=", response)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
