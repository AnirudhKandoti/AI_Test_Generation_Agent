"""CLI entry point to generate tests for a given Python module."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from agent.generator import generate_tests_for_module
from agent.sandbox_runner import run_pytest_sandbox, save_sandbox_result


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate tests for a Python module using Gemini.")
    parser.add_argument("module_path", help="Path to the Python module, e.g. src/utils/math_ops.py")
    args = parser.parse_args()

    result = generate_tests_for_module(args.module_path)
    print(f"Generated tests at: {result.output_path}")
    if result.violations:
        print(f"WARNING: Forbidden imports detected in generated code: {result.violations}")
    print(f"Used dummy generator: {result.used_dummy}")

    # Run sandboxed pytest on the generated tests.
    sandbox_result = run_pytest_sandbox(str(result.output_path))
    save_sandbox_result(sandbox_result)

    print(f"Sandbox return code: {sandbox_result.returncode}")
    if sandbox_result.timed_out:
        print("Sandbox execution timed out.")


if __name__ == "__main__":
    main()
