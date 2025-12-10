"""Prompt templates for the Gemini-based test generator."""

from __future__ import annotations
from textwrap import dedent

def build_test_generation_prompt(module_name: str, func_name: str, func_source: str) -> str:
    """Build a prompt to ask the model to generate pytest tests for a function."""
    return dedent(f"""        You are an expert Python testing assistant.

        Your task is to generate high-quality pytest unit tests for the given function.
        The tests must:
        - Import the function under test from its module.
        - Cover normal cases, edge cases, and error cases.
        - Use plain asserts or pytest helpers (e.g. pytest.raises).
        - Avoid any network, file system, or subprocess operations.
        - Be deterministic and fast to execute.

        Only output valid Python code for a pytest test file.
        Do not include explanations, markdown, or backticks.

        Module: {module_name}
        Function name: {func_name}

        Function source:
        {func_source}
    """)
