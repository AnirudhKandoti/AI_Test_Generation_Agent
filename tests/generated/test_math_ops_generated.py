import sys
from pathlib import Path

# Ensure the src/utils folder is on sys.path so we can import math_ops.py
PROJECT_ROOT = Path(__file__).resolve().parents[2]
SRC_UTILS = PROJECT_ROOT / "src" / "utils"
sys.path.insert(0, str(SRC_UTILS))

import pytest
from math_ops import solve_quadratic

def test_solve_quadratic_normal_case():
    r1, r2 = solve_quadratic(1, -5, 6)
    assert r1 == (3+0j)
    assert r2 == (2+0j)

def test_solve_quadratic_complex_roots():
    r1, r2 = solve_quadratic(1, 2, 5)
    assert r1 == (-1+2j)
    assert r2 == (-1-2j)

def test_solve_quadratic_repeated_root():
    r1, r2 = solve_quadratic(1, -2, 1)
    assert r1 == (1+0j)
    assert r2 == (1+0j)

def test_solve_quadratic_negative_coefficients():
    r1, r2 = solve_quadratic(-1, 3, -2)
    roots = {r1, r2}
    # Accept either order: the set of roots must contain 1 and 2
    assert any(abs(root - 1) < 1e-9 for root in roots)
    assert any(abs(root - 2) < 1e-9 for root in roots)

def test_solve_quadratic_zero_c():
    r1, r2 = solve_quadratic(1, -3, 0)
    assert r1 == (3+0j)
    assert r2 == (0+0j)

def test_solve_quadratic_zero_b():
    r1, r2 = solve_quadratic(1, 0, -4)
    assert r1 == (2+0j)
    assert r2 == (-2+0j)

def test_solve_quadratic_zero_a_raises_value_error():
    with pytest.raises(ValueError):
        solve_quadratic(0, 2, 1)
