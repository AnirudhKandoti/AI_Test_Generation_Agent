"""Gemini-backed test generation agent (no dummy fallback)."""

from __future__ import annotations

import ast
from dataclasses import dataclass
from pathlib import Path
from typing import List

from .config import GEMINI_API_KEY, GEMINI_MODEL_NAME, FORBIDDEN_IMPORTS
from .prompt_templates import build_test_generation_prompt

import google.generativeai as genai  # make import errors visible


@dataclass
class GenerationResult:
    module_path: Path
    output_path: Path
    used_dummy: bool  # always False now
    violations: List[str]
PATH_BOOTSTRAP = """import sys
from pathlib import Path

# Ensure the src/utils folder is on sys.path so we can import math_ops.py
PROJECT_ROOT = Path(__file__).resolve().parents[2]
SRC_UTILS = PROJECT_ROOT / "src" / "utils"
sys.path.insert(0, str(SRC_UTILS))

"""

def _discover_functions(module_path: Path) -> List[ast.FunctionDef]:
    source = module_path.read_text(encoding="utf-8")
    tree = ast.parse(source)
    return [node for node in tree.body if isinstance(node, ast.FunctionDef)]


def _call_gemini(prompt: str) -> str:
    """Call Gemini with the given prompt and return raw text."""
    if not GEMINI_API_KEY:
        raise RuntimeError(
            "GEMINI_API_KEY is not configured. "
            "Set it in agent/config.py."
        )

    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel(GEMINI_MODEL_NAME)
    response = model.generate_content(prompt)
    text = response.text or ""
    return text.strip()


def _detect_forbidden_imports(code: str) -> List[str]:
    violations: List[str] = []
    for forbidden in FORBIDDEN_IMPORTS:
        if forbidden in code:
            violations.append(forbidden)
    return violations


def generate_tests_for_module(module_path: str, output_dir: str = "tests/generated") -> GenerationResult:
    """Generate a single pytest file with tests for all functions in a module."""
    module = Path(module_path)
    if not module.exists():
        raise FileNotFoundError(module)

    functions = _discover_functions(module)
    if not functions:
        raise ValueError(f"No top-level functions found in {module}")

    module_name = module.stem

    # Build a combined prompt for all functions in the module
    src_text = module.read_text(encoding="utf-8")
    prompt_parts: List[str] = []
    for func in functions:
        func_source = ast.get_source_segment(src_text, func) or ""
        prompt_parts.append(
            build_test_generation_prompt(
                module_name=module_name,
                func_name=func.name,
                func_source=func_source,
            )
        )

    full_prompt = "\n\n".join(prompt_parts)
    raw_code = _call_gemini(full_prompt)

    # Basic sanitation: strip markdown fences if present.
    for fence in ("```python", "```py", "```"):
        if fence in raw_code:
            raw_code = raw_code.replace(fence, "")
    raw_code = raw_code.strip()

    violations = _detect_forbidden_imports(raw_code)

    output_dir_path = Path(output_dir)
    output_dir_path.mkdir(parents=True, exist_ok=True)
    output_path = output_dir_path / f"test_{module_name}_generated.py"
    
    full_code = PATH_BOOTSTRAP + raw_code + "\n"
    output_path.write_text(full_code, encoding="utf-8")

    return GenerationResult(
        module_path=module,
        output_path=output_path,
        used_dummy=False,   # <- we always say False now
        violations=violations,
    )
