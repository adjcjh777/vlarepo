#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import math
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
from kaggle.api.kaggle_api_extended import KaggleApi


ROOT = Path(__file__).resolve().parents[1]
BC = ROOT / "birdclef-2026"
EXP = ROOT / "experiments"
KAGGLE_BIN = Path("/Users/junhaocheng/Library/Python/3.9/bin/kaggle")
KERNEL = "junhaochengadjcjh7u7/bc26-v134-stable3-guarded-rescue"
OUTPUT_DIR = BC / "outputs" / "v134-stable3-guarded-rescue-v1"
SAMPLE = BC / "data" / "sample_submission.csv"
REFERENCE_FILES = [
    BC / "outputs" / "v110-ecoproto-clean-blend-v1" / "submission.csv",
    BC / "outputs" / "v114-v110-v113-selfblend-v1" / "submission.csv",
    BC / "outputs" / "v127-memorysafe-nontsubasa-router-v1" / "submission.csv",
]
MAX_CPU_SECONDS = 90 * 60


def now_utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")


def run(cmd: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)


def fetch_outputs(force: bool) -> tuple[bool, str]:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    cmd = [str(KAGGLE_BIN), "kernels", "output", KERNEL, "-p", str(OUTPUT_DIR)]
    if force:
        cmd.append("--force")
    proc = run(cmd)
    return proc.returncode == 0, proc.stdout


def audit_csv(path: Path, sample_path: Path) -> dict[str, str]:
    sample = pd.read_csv(sample_path)
    df = pd.read_csv(path)
    values = df.drop(columns=["row_id"], errors="ignore")
    numeric = values.apply(pd.to_numeric, errors="coerce")
    arr = numeric.to_numpy(dtype=float)
    finite = np.isfinite(arr)
    has_nan = bool(np.isnan(arr).any())
    has_inf = bool(np.isinf(arr).any())
    min_pred = float(np.nanmin(arr)) if arr.size else math.nan
    max_pred = float(np.nanmax(arr)) if arr.size else math.nan
    return {
        "path": str(path.relative_to(ROOT)),
        "rows": str(df.shape[0]),
        "columns": str(df.shape[1]),
        "matches_sample_columns": str(list(df.columns) == list(sample.columns)),
        "matches_sample_row_order": str(df["row_id"].tolist() == sample["row_id"].tolist() if "row_id" in df.columns else False),
        "duplicate_row_id": str(bool(df["row_id"].duplicated().any()) if "row_id" in df.columns else True),
        "has_nan": str(has_nan),
        "has_inf": str(has_inf),
        "finite_fraction": f"{finite.mean():.8f}" if arr.size else "",
        "min_pred": f"{min_pred:.12g}" if np.isfinite(min_pred) else "",
        "max_pred": f"{max_pred:.12g}" if np.isfinite(max_pred) else "",
        "range_ok": str(np.isfinite(min_pred) and np.isfinite(max_pred) and min_pred >= 0.0 and max_pred <= 1.0),
        "mean": f"{np.nanmean(arr):.12g}" if arr.size else "",
        "std": f"{np.nanstd(arr):.12g}" if arr.size else "",
        "gt_0_9": str(int(np.nansum(arr > 0.9))) if arr.size else "0",
        "lt_0_1": str(int(np.nansum(arr < 0.1))) if arr.size else "0",
    }


def parse_runtime_seconds(text: str) -> float | None:
    values: list[float] = []
    patterns = [
        r'"time"\s*:\s*([0-9]+(?:\.[0-9]+)?)',
        r"(?:elapsed|runtime|total).*?([0-9]+(?:\.[0-9]+)?)\s*s",
        r"([0-9]+(?:\.[0-9]+)?)\s*seconds",
        r"nbconvert.*?([0-9]+(?:\.[0-9]+)?)s",
    ]
    for pattern in patterns:
        for match in re.finditer(pattern, text, flags=re.IGNORECASE):
            values.append(float(match.group(1)))
    return max(values) if values else None


def read_log_text(output_dir: Path) -> str:
    chunks = []
    for path in sorted(output_dir.glob("*.log")) + sorted(output_dir.glob("*.json")):
        try:
            chunks.append(path.read_text(encoding="utf-8", errors="ignore"))
        except Exception:
            pass
    return "\n".join(chunks)


def compare_predictions(candidate_path: Path, reference_paths: list[Path]) -> list[dict[str, str]]:
    cand = pd.read_csv(candidate_path)
    if "row_id" not in cand.columns:
        return []
    rows = []
    cand = cand.set_index("row_id")
    cand_cols = [c for c in cand.columns]
    for ref_path in reference_paths:
        if not ref_path.exists():
            continue
        ref = pd.read_csv(ref_path)
        if "row_id" not in ref.columns:
            continue
        ref = ref.set_index("row_id")
        common_rows = cand.index.intersection(ref.index)
        common_cols = [c for c in cand_cols if c in ref.columns]
        if len(common_rows) == 0 or len(common_cols) == 0:
            rows.append(
                {
                    "reference_path": str(ref_path.relative_to(ROOT)),
                    "common_rows": "0",
                    "common_cols": str(len(common_cols)),
                    "pearson": "",
                    "mad": "",
                    "max_abs_diff": "",
                    "note": "no_common_rows_or_cols",
                }
            )
            continue
        a = cand.loc[common_rows, common_cols].to_numpy(dtype=float).ravel()
        b = ref.loc[common_rows, common_cols].to_numpy(dtype=float).ravel()
        mask = np.isfinite(a) & np.isfinite(b)
        pearson = float(np.corrcoef(a[mask], b[mask])[0, 1]) if int(mask.sum()) >= 2 else math.nan
        diff = np.abs(a[mask] - b[mask]) if int(mask.sum()) else np.array([])
        rows.append(
            {
                "reference_path": str(ref_path.relative_to(ROOT)),
                "common_rows": str(len(common_rows)),
                "common_cols": str(len(common_cols)),
                "pearson": "" if not np.isfinite(pearson) else f"{pearson:.8f}",
                "mad": "" if diff.size == 0 else f"{float(diff.mean()):.12g}",
                "max_abs_diff": "" if diff.size == 0 else f"{float(diff.max()):.12g}",
                "note": "",
            }
        )
    return rows


def write_csv(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--fetch", action="store_true")
    parser.add_argument("--force-fetch", action="store_true")
    args = parser.parse_args()

    EXP.mkdir(exist_ok=True)
    api = KaggleApi()
    api.authenticate()
    status = str(api.kernels_status(KERNEL))

    fetch_ok = None
    fetch_log = ""
    if args.fetch and "COMPLETE" in status:
        fetch_ok, fetch_log = fetch_outputs(args.force_fetch)

    submission = OUTPUT_DIR / "submission.csv"
    schema_rows: list[dict[str, str]] = []
    compare_rows: list[dict[str, str]] = []
    log_text = read_log_text(OUTPUT_DIR)
    runtime = parse_runtime_seconds(log_text) if log_text else None

    if submission.exists():
        schema_rows.append(audit_csv(submission, SAMPLE))
        compare_rows = compare_predictions(submission, REFERENCE_FILES)
        write_csv(
            EXP / "v134_correlation_vs_references.csv",
            compare_rows,
            ["reference_path", "common_rows", "common_cols", "pearson", "mad", "max_abs_diff", "note"],
        )
        write_csv(
            EXP / "v134_schema_report.csv",
            schema_rows,
            [
                "path",
                "rows",
                "columns",
                "matches_sample_columns",
                "matches_sample_row_order",
                "duplicate_row_id",
                "has_nan",
                "has_inf",
                "finite_fraction",
                "min_pred",
                "max_pred",
                "range_ok",
                "mean",
                "std",
                "gt_0_9",
                "lt_0_1",
            ],
        )

    report = EXP / "v134_runmode_status.md"
    with report.open("w", encoding="utf-8") as f:
        f.write("# v134 Runmode Status\n\n")
        f.write(f"Updated: {now_utc()}\n\n")
        f.write(f"- Kernel: `{KERNEL}`\n")
        f.write(f"- Kaggle status: `{status}`\n")
        f.write(f"- Output dir: `{OUTPUT_DIR.relative_to(ROOT)}`\n")
        if fetch_ok is not None:
            f.write(f"- Fetch attempted: `{fetch_ok}`\n")
        if runtime is not None:
            f.write(f"- Parsed runtime seconds: `{runtime:.1f}`\n")
            f.write(f"- Runtime under 90 minutes: `{runtime <= MAX_CPU_SECONDS}`\n")
        if schema_rows:
            row = schema_rows[0]
            f.write("\n## Submission Schema\n")
            for key in [
                "rows",
                "columns",
                "matches_sample_columns",
                "matches_sample_row_order",
                "duplicate_row_id",
                "has_nan",
                "has_inf",
                "range_ok",
                "min_pred",
                "max_pred",
                "mean",
                "std",
                "gt_0_9",
                "lt_0_1",
            ]:
                f.write(f"- {key}: `{row[key]}`\n")
        if compare_rows:
            f.write("\n## Reference Comparison\n")
            for row in compare_rows:
                suffix = f" {row['note']}" if row["note"] else ""
                f.write(
                    f"- `{row['reference_path']}` common_rows={row['common_rows']} "
                    f"pearson={row['pearson']} mad={row['mad']} max_abs_diff={row['max_abs_diff']}{suffix}\n"
                )
        f.write("\n## Automatic Decision\n")
        if "COMPLETE" not in status:
            f.write("- Wait. Run-mode is not complete; do not promote.\n")
        elif not submission.exists():
            f.write("- HOLD. `submission.csv` has not been fetched yet.\n")
        elif runtime is not None and runtime > MAX_CPU_SECONDS:
            f.write("- REJECT for real submission until runtime is below 90 minutes.\n")
        elif schema_rows and schema_rows[0]["has_nan"] == "False" and schema_rows[0]["has_inf"] == "False" and schema_rows[0]["range_ok"] == "True":
            f.write("- Candidate may proceed to local proxy/correlation review, but no real submit yet.\n")
        else:
            f.write("- HOLD. Schema or numeric checks are incomplete or failing.\n")
        if fetch_log:
            f.write("\n## Fetch Log\n```text\n")
            f.write(fetch_log[-3000:])
            f.write("\n```\n")

    print(f"status={status}")
    print(f"status_report={report}")
    if fetch_ok is not None:
        print(f"fetch_ok={fetch_ok}")
    if runtime is not None:
        print(f"runtime_seconds={runtime:.1f}")
    if schema_rows:
        print("schema_rows=", len(schema_rows))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
