"""Sandboxed execution of pytest test files with basic safety checks."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from dataclasses import dataclass, asdict
from pathlib import Path


@dataclass
class SandboxResult:
    test_file: str
    returncode: int
    timed_out: bool
    stdout: str
    stderr: str
    duration_seconds: float


# Project root: folder that contains src/, tests/, data/
PROJECT_ROOT = Path(__file__).resolve().parents[1]


def run_pytest_sandbox(test_path: str, timeout: int = 30) -> SandboxResult:
    """Run pytest on a given test file from the project root with a timeout.

    This is a light-weight sandbox: it enforces a timeout and captures output,
    but does not isolate the filesystem like a container.
    """
    test_path_obj = Path(test_path).resolve()

    # Build an environment where Python can see your code.
    env = os.environ.copy()

    extra_paths = [
        str(PROJECT_ROOT),               # so 'import src' works if src is a package
        str(PROJECT_ROOT / "src"),       # so 'from utils import ...' could work
        str(PROJECT_ROOT / "src" / "utils"),  # so 'from math_ops import ...' works
    ]
    existing = env.get("PYTHONPATH")
    env["PYTHONPATH"] = os.pathsep.join(extra_paths + ([existing] if existing else []))

    cmd = [sys.executable, "-m", "pytest", str(test_path_obj)]

    start = time.time()
    try:
        proc = subprocess.run(
            cmd,
            cwd=PROJECT_ROOT,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=timeout,
        )
        timed_out = False
    except subprocess.TimeoutExpired as exc:
        timed_out = True
        stdout = exc.stdout or ""
        stderr = exc.stderr or ""
        duration = time.time() - start
        return SandboxResult(
            test_file=str(test_path_obj),
            returncode=124,
            timed_out=True,
            stdout=stdout,
            stderr=stderr,
            duration_seconds=duration,
        )

    duration = time.time() - start
    return SandboxResult(
        test_file=str(test_path_obj),
        returncode=proc.returncode,
        timed_out=timed_out,
        stdout=proc.stdout,
        stderr=proc.stderr,
        duration_seconds=duration,
    )


def save_sandbox_result(result: SandboxResult, output_dir: str = "data/results") -> None:
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    out_path = Path(output_dir) / "sandbox_last_run.json"
    out_path.write_text(json.dumps(asdict(result), indent=2), encoding="utf-8")
