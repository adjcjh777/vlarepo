#!/usr/bin/env python3
"""Gate and optionally push v380 for Kaggle Run-mode schema/runtime proof."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from kaggle.api.kaggle_api_extended import KaggleApi


ROOT = Path(__file__).resolve().parents[1]
NOTEBOOK_DIR = ROOT / "birdclef-2026/notebooks/v380-v379-static-distill"
V380_RUNTIME = ROOT / "artifacts/runtime_v380_v379_static_materializer_20260524.json"
STATUS = ROOT / "experiments/v380_after_v380_push_gate_status.md"
KERNEL = "junhaochengadjcjh7u7/bc26-v380-v379-static-distill"


def now_utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")


def read_json(path: Path) -> dict[str, object]:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def live_pending_and_count() -> tuple[int, int, str]:
    try:
        api = KaggleApi()
        api.authenticate()
        subs = api.competition_submissions("birdclef-2026")[:20]
    except Exception as exc:  # noqa: BLE001
        return -1, -1, f"{type(exc).__name__}: {exc}"
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    count = sum(1 for sub in subs if str(getattr(sub, "date", "")).startswith(today))
    pending = sum(1 for sub in subs if "PENDING" in str(getattr(sub, "status", "") or ""))
    return pending, count, ""


def decide() -> tuple[str, str, dict[str, object]]:
    runtime = read_json(V380_RUNTIME)
    audit = runtime.get("audit", {}) if isinstance(runtime.get("audit"), dict) else {}
    metrics = runtime.get("local_metrics", {}) if isinstance(runtime.get("local_metrics"), dict) else {}
    pending, today_count, live_error = live_pending_and_count()
    required = [
        NOTEBOOK_DIR / "submission.ipynb",
        NOTEBOOK_DIR / "kernel-metadata.json",
        NOTEBOOK_DIR / "ATTRIBUTION.md",
    ]
    missing = [str(p.relative_to(ROOT)) for p in required if not p.exists()]
    metadata = read_json(NOTEBOOK_DIR / "kernel-metadata.json")
    evidence = {
        "v380_decision": runtime.get("decision", "MISSING"),
        "v380_block_count": audit.get("block_count", "MISSING"),
        "v380_macro_gain": metrics.get("macro_gain", "MISSING"),
        "v380_top5_anchor": metrics.get("anchor_top5_hit", "MISSING"),
        "v380_top5_local": metrics.get("local_top5_hit", "MISSING"),
        "notebook_dir": str(NOTEBOOK_DIR.relative_to(ROOT)),
        "missing": missing,
        "metadata_id": metadata.get("id", ""),
        "metadata_cpu": metadata.get("enable_gpu") is False,
        "metadata_no_tpu": metadata.get("enable_tpu") is False,
        "metadata_no_internet": metadata.get("enable_internet") is False,
        "dataset_sources": metadata.get("dataset_sources", []),
        "model_sources": metadata.get("model_sources", []),
        "live_pending_count": pending,
        "utc_today_visible_kaggle_count": today_count,
        "live_error": live_error,
    }
    if runtime.get("decision") != "READY-v380-static-materializer-audit-NO-PUSH-NO-SUBMIT":
        return "WAIT-v380-static-audit", "v380 static audit is not READY", evidence
    if audit.get("block_count") != 0:
        return "WAIT-v380-static-blockers", "v380 static audit has blockers", evidence
    if missing:
        return "WAIT-v380-files-missing", "v380 notebook files are missing", evidence
    if metadata.get("id") != KERNEL:
        return "WAIT-v380-metadata-id-mismatch", "metadata id does not match expected v380 kernel", evidence
    if not (evidence["metadata_cpu"] and evidence["metadata_no_tpu"] and evidence["metadata_no_internet"]):
        return "WAIT-v380-metadata-risk", "metadata is not CPU/no-TPU/no-internet", evidence
    if "jaejohn/perch-meta" in str(metadata.get("dataset_sources", [])) or "tuckerarrants/bc2026-distilled-sed-public" in str(metadata.get("dataset_sources", [])):
        return "WAIT-v380-unknown-source-risk", "metadata contains unknown-license sources", evidence
    try:
        macro_gain = float(metrics.get("macro_gain"))
        top5_local = float(metrics.get("local_top5_hit"))
        top5_anchor = float(metrics.get("anchor_top5_hit"))
    except Exception:
        return "WAIT-v380-metrics-missing", "local metrics are missing or invalid", evidence
    if macro_gain < 0.0015:
        return "WAIT-v380-promotion-gate", "local macro gain no longer meets promotion gate", evidence
    if top5_local + 1e-12 < top5_anchor:
        return "WAIT-v380-top5-regression", "local top5 regressed", evidence
    if pending > 0:
        return "WAIT-live-pending-submission", "live competition submission is pending; delay Run-mode push", evidence
    if pending < 0:
        return "WAIT-live-status-error", "could not verify live pending submissions", evidence
    return "READY-push-v380-runmode", "v380 may start Kaggle Run-mode schema/runtime proof only", evidence


def write_status(decision: str, reason: str, evidence: dict[str, object], executed: bool, output: str = "") -> None:
    lines = [
        "# v380 After-v380 Push Gate Status",
        "",
        f"Updated: {now_utc()}",
        "",
        f"- Kernel: `{KERNEL}`",
        f"- Decision: `{decision}`",
        f"- Reason: {reason}",
        f"- Execute attempted: `{executed}`",
        f"- Notebook dir: `{NOTEBOOK_DIR.relative_to(ROOT)}`",
        "",
        "## Evidence",
        "",
    ]
    for key, value in evidence.items():
        lines.append(f"- {key}: `{value}`")
    lines += [
        "",
        "## Guard",
        "",
        "- This script never makes a competition submission.",
        "- v380 Run-mode push is schema/runtime proof only.",
        "- A live pending competition submission blocks this push.",
        "- After push, run `python3 scripts/audit_v380_runmode.py --fetch-if-complete --write`.",
    ]
    if output:
        lines += ["", "## Command Output", "", "```", output.strip(), "```"]
    STATUS.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()

    decision, reason, evidence = decide()
    output = ""
    executed = False
    if args.execute:
        if decision != "READY-push-v380-runmode":
            output = "execute refused: gate is not READY"
        else:
            executed = True
            api = KaggleApi()
            api.authenticate()
            try:
                output = repr(api.kernels_push(str(NOTEBOOK_DIR)))
            except Exception as exc:  # noqa: BLE001
                decision = "WAIT-kernel-push-api-error"
                reason = f"KaggleApi.kernels_push hit {type(exc).__name__}: {exc}"
            else:
                decision = "PUSHED-v380-runmode"
                reason = "v380 Run-mode push accepted through Kaggle API; monitor with audit_v380_runmode"
    if args.write:
        write_status(decision, reason, evidence, executed, output)
    print(f"checked_at={now_utc()}")
    print(f"decision={decision}")
    print(f"reason={reason}")
    print(f"execute_attempted={executed}")
    if args.write:
        print(f"status_path={STATUS}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
