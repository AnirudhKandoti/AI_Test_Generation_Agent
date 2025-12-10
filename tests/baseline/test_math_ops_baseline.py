import pytest
from src.utils import math_ops

def test_add_simple():
    assert math_ops.add(1, 2) == 3

def test_add_negative():
    assert math_ops.add(-1, -2) == -3

def test_divide_safe_normal():
    assert math_ops.divide_safe(6, 2) == 3

def test_divide_safe_zero():
    with pytest.raises(ValueError):
        math_ops.divide_safe(1, 0)

def test_mean_basic():
    assert math_ops.mean([1, 2, 3]) == 2

def test_mean_raises_on_empty():
    with pytest.raises(ValueError):
        math_ops.mean([])
