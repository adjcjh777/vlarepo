#!/usr/bin/env python3
"""Audit v387 Run-mode schema/runtime output."""

from __future__ import annotations

import argparse
import json
import math
import re
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
from kaggle.api.kaggle_api_extended import KaggleApi


ROOT = Path(__file__).resolve().parents[1]
KERNEL = "junhaochengadjcjh7u7/bc26-v387-v386-static-distill"
OUT_DIR = ROOT / "birdclef-2026/outputs/v387-v386-static-distill-runmode"
STATUS_PATH = ROOT / "experiments/v387_runmode_status.md"
RUNTIME_PATH = ROOT / "artifacts/runtime_v387_runmode_status.json"
LINEAGE_PATH = ROOT / "artifacts/lineage_v387_runmode_status.json"
SAMPLE_PATH = ROOT / "birdclef-2026/data/sample_submission.csv"
DIAGNOSTICS = ["v387_static_distill_diagnostics.csv", "v387_static_distill_summary.csv", "submission_v107_anchor.csv"]
TARGET_RUNTIME_SEC = 70 * 60
HARD_RUNTIME_SEC = 90 * 60


def now_utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")


def status_text(api: KaggleApi) -> str:
    try:
        return str(api.kernels_status(KERNEL))
    except Exception as exc:  # noqa: BLE001
        return json.dumps({"status": "STATUS_ERROR", "failureMessage": f"{type(exc).__name__}: {exc}"})


def logs_text(out_dir: Path) -> str:
    if not out_dir.exists():
        return ""
    return "\n".join(p.read_text(encoding="utf-8", errors="replace") for p in sorted(out_dir.glob("*.log")))


def runtime_seconds(status: str, out_dir: Path) -> int | None:
    for pattern in [
        r'"runTimeSeconds"\s*:\s*(\d+)',
        r"'runTimeSeconds':\s*(\d+)",
        r"runTimeSeconds[=:]\s*(\d+)",
    ]:
        match = re.search(pattern, status)
        if match:
            return int(match.group(1))
    logs = logs_text(out_dir)
    log_times = [float(x) for x in re.findall(r'"time"\s*:\s*(\d+(?:\.\d+)?)', logs)]
    if log_times:
        return int(max(log_times))
    for pattern in [r"real\s+(\d+(?:\.\d+)?)", r"Total wall time.*?(\d+(?:\.\d+)?)\s*min"]:
        match = re.search(pattern, logs, flags=re.IGNORECASE)
        if match:
            value = float(match.group(1))
            if "min" in match.group(0).lower():
                value *= 60.0
            return int(value)
    return None


def csv_schema(path: Path) -> dict[str, object]:
    sample = pd.read_csv(SAMPLE_PATH)
    if not path.exists():
        return {"available": False, "path": str(path)}
    df = pd.read_csv(path)
    values = df.drop(columns=["row_id"], errors="ignore").to_numpy(dtype="float64")
    has_values = bool(getattr(values, "size", 0))
    return {
        "available": True,
        "path": str(path),
        "rows": int(len(df)),
        "columns": int(df.shape[1]),
        "matches_sample_columns": list(df.columns) == list(sample.columns),
        "matches_sample_row_order": "row_id" in df.columns and df["row_id"].astype(str).tolist() == sample["row_id"].astype(str).tolist(),
        "matches_sample_row_set": "row_id" in df.columns and set(df["row_id"].astype(str)) == set(sample["row_id"].astype(str)),
        "contains_train_rows": "row_id" in df.columns and bool(df["row_id"].astype(str).str.contains("_Train_").any()),
        "duplicate_row_id": "row_id" not in df.columns or bool(df["row_id"].duplicated().any()),
        "has_nan": bool(pd.isna(values).any()) if has_values else True,
        "has_inf": bool(math.isinf(float(values.max())) or math.isinf(float(values.min()))) if has_values else True,
        "range_ok": bool(has_values and values.min() >= 0.0 and values.max() <= 1.0),
        "min_pred": float(values.min()) if has_values else None,
        "max_pred": float(values.max()) if has_values else None,
        "mean": float(values.mean()) if has_values else None,
        "std": float(values.std()) if has_values else None,
    }


def schema_ok(schema: dict[str, object]) -> bool:
    return all(
        [
            schema.get("available"),
            schema.get("matches_sample_columns"),
            schema.get("matches_sample_row_order"),
            schema.get("matches_sample_row_set"),
            not schema.get("contains_train_rows", True),
            not schema.get("duplicate_row_id", True),
            not schema.get("has_nan", True),
            not schema.get("has_inf", True),
            schema.get("range_ok"),
        ]
    )


def diagnostic_schema(path: Path) -> dict[str, object]:
    if not path.exists():
        return {"available": False, "path": str(path)}
    df = pd.read_csv(path)
    return {
        "available": True,
        "path": str(path),
        "rows": int(len(df)),
        "columns": int(df.shape[1]),
        "column_names": list(df.columns),
    }


def log_flags(out_dir: Path) -> dict[str, object]:
    text = logs_text(out_dir)
    return {
        "available": bool(text),
        "traceback": "Traceback" in text,
        "v387_printed": "v387 dry-run tolerant static distill patch complete" in text,
        "dryrun_row_mismatch_tolerated": "v387 dry-run row mismatch tolerated" in text,
        "unknown_license_dataset_text": "jaejohn/perch-meta" in text or "tuckerarrants/bc2026-distilled-sed-public" in text,
    }


def decision(status: str, submission: dict[str, object], diagnostics: dict[str, dict[str, object]], flags: dict[str, object], runtime_sec: int | None) -> str:
    status_upper = status.upper()
    if "STATUS_ERROR" in status_upper and not (submission.get("available") and flags.get("v387_printed")):
        return "WAIT-status-error"
    if any(term in status_upper for term in ['"STATUS": "CANCEL', '"STATUS": "ERROR', '"STATUS": "FAILED']):
        return "REJECT-v387-runmode-failed"
    local_complete = submission.get("available") and flags.get("v387_printed") and not flags.get("traceback")
    if "COMPLETE" not in status_upper and not local_complete:
        return "WAIT-running"
    if flags.get("traceback"):
        return "REJECT-v387-log-traceback"
    if flags.get("unknown_license_dataset_text"):
        return "REJECT-v387-unknown-license-runtime-text"
    missing_diag = [name for name, rep in diagnostics.items() if not rep.get("available")]
    if missing_diag:
        return "HOLD-v387-diagnostics-missing"
    if not schema_ok(submission):
        if submission.get("available") and submission.get("matches_sample_columns") and submission.get("contains_train_rows") and flags.get("dryrun_row_mismatch_tolerated"):
            if runtime_sec is not None and runtime_sec <= TARGET_RUNTIME_SEC:
                return "READY-v387-runmode-dryrun-runtime-proof"
            return "HOLD-v387-dryrun-runtime-unverified"
        return "REJECT-v387-submission-schema"
    if runtime_sec is not None and runtime_sec > HARD_RUNTIME_SEC:
        return "REJECT-v387-runtime-hardcap"
    if runtime_sec is not None and runtime_sec <= TARGET_RUNTIME_SEC:
        return "READY-v387-runmode-schema-runtime-proof"
    return "HOLD-v387-runtime-unverified"


def write_status(status: str, fetched: bool, submission: dict[str, object], diagnostics: dict[str, dict[str, object]], flags: dict[str, object], runtime_sec: int | None, dec: str) -> None:
    lines = [
        "# v387 Run-mode Status",
        "",
        f"Updated: {now_utc()}",
        "",
        f"- Kernel: `{KERNEL}`",
        f"- Kaggle status: `{status}`",
        f"- Output dir: `{OUT_DIR.relative_to(ROOT)}`",
        f"- Fetched: `{fetched}`",
        f"- Runtime seconds: `{runtime_sec}`",
        f"- Runtime target seconds: `{TARGET_RUNTIME_SEC}`",
        f"- Runtime hard cap seconds: `{HARD_RUNTIME_SEC}`",
        f"- Decision: `{dec}`",
        "",
        "## Submission Schema",
        "",
    ]
    for key, value in submission.items():
        lines.append(f"- {key}: `{value}`")
    lines += ["", "## Diagnostics", ""]
    for name, rep in diagnostics.items():
        lines.append(f"### {name}")
        for key, value in rep.items():
            lines.append(f"- {key}: `{value}`")
        lines.append("")
    lines += ["## Log Flags", ""]
    for key, value in flags.items():
        lines.append(f"- {key}: `{value}`")
    if OUT_DIR.exists():
        lines += ["", "## Files", ""]
        for path in sorted(OUT_DIR.rglob("*"))[:140]:
            if path.is_file():
                lines.append(f"- `{path.relative_to(OUT_DIR)}`")
    lines += [
        "",
        "## Submit Gate",
        "",
        "No real competition submission is made by this audit. v387 may become a candidate for later guarded submission only if this audit reports READY and a separate competition-submit gate is explicitly authorized.",
    ]
    STATUS_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")
    RUNTIME_PATH.parent.mkdir(parents=True, exist_ok=True)
    RUNTIME_PATH.write_text(
        json.dumps(
            {
                "experiment_id": "v387_runmode_status",
                "updated_utc": now_utc(),
                "kernel": KERNEL,
                "status": status,
                "fetched": fetched,
                "runtime_seconds": runtime_sec,
                "decision": dec,
                "submission": submission,
                "diagnostics": diagnostics,
                "log_flags": flags,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    LINEAGE_PATH.write_text(
        json.dumps(
            {
                "experiment_id": "v387_runmode_status",
                "source_notebook": "birdclef-2026/notebooks/v387-v386-static-distill",
                "outputs": [str(p.relative_to(ROOT)) for p in sorted(OUT_DIR.glob("*"))] if OUT_DIR.exists() else [],
                "submitted": False,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--fetch-if-complete", action="store_true")
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()

    api = KaggleApi()
    api.authenticate()
    status = status_text(api)
    fetched = False
    if args.fetch_if_complete and "COMPLETE" in status.upper():
        OUT_DIR.mkdir(parents=True, exist_ok=True)
        api.kernels_output(KERNEL, path=str(OUT_DIR), quiet=False)
        fetched = True
    submission = csv_schema(OUT_DIR / "submission.csv")
    diagnostics = {name: diagnostic_schema(OUT_DIR / name) for name in DIAGNOSTICS}
    flags = log_flags(OUT_DIR)
    runtime_sec = runtime_seconds(status, OUT_DIR)
    dec = decision(status, submission, diagnostics, flags, runtime_sec)
    if args.write:
        write_status(status, fetched, submission, diagnostics, flags, runtime_sec, dec)
    print(f"checked_at={now_utc()}")
    print(f"kernel={KERNEL}")
    print(f"status={status}")
    print(f"fetched={fetched}")
    print(f"runtime_seconds={runtime_sec}")
    print(f"decision={dec}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
