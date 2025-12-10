"""Evaluation harness for baseline and generated tests.

Metrics:
- Coverage (statement + branch)
- Flakiness (multiple runs)
- Basic pass/fail statistics
"""

from __future__ import annotations

import json
import subprocess
import sys
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import List, Dict, Any


@dataclass
class SuiteMetrics:
    name: str
    test_paths: List[str]
    runs: int
    passes: int
    failures: int
    flaky_tests: int
    coverage_statement: float
    coverage_branch: float


def _run_pytest_with_coverage(test_paths: List[str]) -> int:
    """Run pytest with coverage for given test paths, returning exit code."""
    cmd = [
        sys.executable,
        "-m",
        "coverage",
        "run",
        "-m",
        "pytest",
        *test_paths,
    ]
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    return proc.returncode


def _compute_coverage() -> Dict[str, float]:
    """Compute coverage metrics using 'coverage json'."""
    subprocess.run(
        [sys.executable, "-m", "coverage", "json", "-q"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    data = json.loads(Path("coverage.json").read_text(encoding="utf-8"))
    totals = data.get("totals", {})
    stmts = totals.get("num_statements", 0) or 0
    covered = totals.get("covered_lines", 0) or 0  # <-- fix here
    branches = totals.get("num_branches", 0) or 0
    covered_branches = totals.get("covered_branches", 0) or 0

    return {
    "statement": (covered / stmts) if stmts else 0.0,
    "branch": (covered_branches / branches) if branches else 0.0,
}


def evaluate_suite(name: str, test_glob: str, runs: int = 5) -> SuiteMetrics:
    """Evaluate a test suite glob pattern over multiple runs to estimate flakiness."""
    test_paths = [str(p) for p in Path(".").glob(test_glob)]
    if not test_paths:
        raise ValueError(f"No tests matched pattern {test_glob}")

    passes = 0
    failures = 0

    # Very simple flakiness estimation: count how many times exit code changes.
    last_exit_code = None
    flakiness_events = 0

    for i in range(runs):
        exit_code = _run_pytest_with_coverage(test_paths)
        if exit_code == 0:
            passes += 1
        else:
            failures += 1

        if last_exit_code is not None and exit_code != last_exit_code:
            flakiness_events += 1
        last_exit_code = exit_code

    cov = _compute_coverage()

    return SuiteMetrics(
        name=name,
        test_paths=test_paths,
        runs=runs,
        passes=passes,
        failures=failures,
        flaky_tests=flakiness_events,  # coarse approximation
        coverage_statement=cov["statement"],
        coverage_branch=cov["branch"],
    )


def save_metrics(metrics: SuiteMetrics, output_path: str) -> None:
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    Path(output_path).write_text(json.dumps(asdict(metrics), indent=2), encoding="utf-8")
