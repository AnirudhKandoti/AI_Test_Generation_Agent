from __future__ import annotations
import json
import subprocess
import sys
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import List, Dict, Any


# Where your code + tests live (relative to this file)
PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_TARGET_MODULE = PROJECT_ROOT / "src" / "utils" / "math_ops.py"

BASELINE_TESTS = [str(PROJECT_ROOT / "tests" / "baseline" / "test_math_ops_baseline.py")]
GENERATED_TESTS = [str(PROJECT_ROOT / "tests" / "generated" / "test_math_ops_generated.py")]


@dataclass
class MutationMetrics:
    suite_name: str
    target_module: str
    total_mutants: int
    killed: int
    survived: int
    mutation_score: float


# Simple character-level mutations: flip comparison and arithmetic operators.
_MUTATION_MAP = {
    ">": "<",
    "<": ">",
    "+": "-",
    "-": "+",
}


def _find_mutation_sites(source: str) -> List[int]:
    """
    Return indices in `source` where we will apply mutations.

    Very simple heuristic:
    - Only mutate chars in _MUTATION_MAP.
    - Skip anything that appears *after* a '#' on the same line (comments).
    """
    indices: List[int] = []
    line_start = 0

    for i, ch in enumerate(source):
        if ch == "\n":
            line_start = i + 1
            continue

        if ch not in _MUTATION_MAP:
            continue

        # If there's a '#' before this position on the same line, treat as comment.
        line_segment = source[line_start:i]
        if "#" in line_segment:
            continue

        indices.append(i)

    return indices


def _make_mutant(source: str, index: int) -> str:
    """Return a new mutated source where one character at `index` is flipped."""
    original = source[index]
    replacement = _MUTATION_MAP.get(original)
    if replacement is None:
        return source
    return source[:index] + replacement + source[index + 1 :]


def compute_mutation_score(
    suite_name: str,
    target_module: Path,
    test_paths: List[str],
) -> MutationMetrics:
    """
    Run a simple mutation analysis for a given test suite.

    For each mutation site in `target_module`, we:
    - write a mutated version of the file
    - run pytest on `test_paths`
    - consider non-zero exitcode => killed mutant
    """
    target_module = target_module.resolve()
    source = target_module.read_text(encoding="utf-8")

    mutation_sites = _find_mutation_sites(source)
    total = len(mutation_sites)
    killed = 0
    survived = 0

    if total == 0:
        return MutationMetrics(
            suite_name=suite_name,
            target_module=str(target_module),
            total_mutants=0,
            killed=0,
            survived=0,
            mutation_score=0.0,
        )

    for idx in mutation_sites:
        mutated = _make_mutant(source, idx)
        # Write mutated source
        target_module.write_text(mutated, encoding="utf-8")

        try:
            cmd = [sys.executable, "-m", "pytest", *test_paths]
            result = subprocess.run(
                cmd,
                cwd=PROJECT_ROOT,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            if result.returncode != 0:
                killed += 1
            else:
                survived += 1
        finally:
            # Restore original source *every time* to avoid cascading mutations
            target_module.write_text(source, encoding="utf-8")

    score = killed / total if total else 0.0

    return MutationMetrics(
        suite_name=suite_name,
        target_module=str(target_module),
        total_mutants=total,
        killed=killed,
        survived=survived,
        mutation_score=score,
    )


def real_mutation_metrics(name: str) -> Dict[str, Any]:
    """
    Drop-in replacement for the old dummy_mutation_metrics(name).

    This lets scripts that call mutation.dummy_mutation_metrics("baseline")
    keep working, but now with *real* mutation data.
    """
    if name == "baseline":
        m = compute_mutation_score("baseline", DEFAULT_TARGET_MODULE, BASELINE_TESTS)
    elif name == "generated":
        m = compute_mutation_score("generated", DEFAULT_TARGET_MODULE, GENERATED_TESTS)
    else:
        raise ValueError(f"Unknown suite name: {name!r}")

    return asdict(m)


# For backward compatibility if your existing code imports dummy_mutation_metrics:
dummy_mutation_metrics = real_mutation_metrics
def save_mutation_metrics(metrics: MutationMetrics, output_path: str) -> None:
    from pathlib import Path
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    data = asdict(metrics)
    Path(output_path).write_text(json.dumps(data, indent=2), encoding="utf-8")