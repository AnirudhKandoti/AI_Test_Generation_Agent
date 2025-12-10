"""Math utilities used as the target for AI test generation experiments.

This module intentionally mixes very simple and slightly more complex functions
so that an AI test generator has to handle:

- Normal cases
- Edge cases
- Invalid input (raising ValueError)
- Floating point behaviour
- Sequences and iteration
"""

from __future__ import annotations

from typing import Iterable, Sequence, List, Tuple


def add(a: float, b: float) -> float:
    """Return the sum of two numbers."""
    return a + b


def divide_safe(a: float, b: float) -> float:
    """Divide a by b, raising ValueError on division by zero instead of ZeroDivisionError."""
    if b == 0:
        raise ValueError("b must not be zero")
    return a / b


def mean(values: Iterable[float]) -> float:
    """Return the arithmetic mean of a non-empty iterable of numbers.

    Raises:
        ValueError: if values is empty.
    """
    vals: List[float] = list(values)
    if not vals:
        raise ValueError("values must not be empty")
    return sum(vals) / len(vals)


def clamp(value: float, lower: float, upper: float) -> float:
    """Clamp value to the inclusive range [lower, upper].

    Raises:
        ValueError: if lower > upper.
    """
    if lower > upper:
        raise ValueError("lower must be <= upper")
    if value < lower:
        return lower
    if value > upper:
        return upper
    return value


def weighted_mean(values: Sequence[float], weights: Sequence[float]) -> float:
    """Return the weighted mean of values.

    Args:
        values: sequence of numbers.
        weights: sequence of non-negative weights, same length as values.

    Raises:
        ValueError: if lengths differ, values is empty, or all weights are zero.
    """
    if len(values) != len(weights):
        raise ValueError("values and weights must have the same length")
    if not values:
        raise ValueError("values must not be empty")
    total_weight = sum(weights)
    if total_weight == 0:
        raise ValueError("total weight must not be zero")
    return sum(v * w for v, w in zip(values, weights)) / total_weight


def moving_average(values: Sequence[float], window_size: int) -> List[float]:
    """Compute a simple moving average over a 1D sequence.

    Returns a list of the same length as values, where each element is the
    average over the window ending at that position. For positions where there
    are not enough previous elements to fill the window, it uses a smaller
    window.

    Example:
        values = [1, 2, 3, 4], window_size = 2
        -> [1.0, 1.5, 2.5, 3.5]

    Raises:
        ValueError: if window_size <= 0 or values is empty.
    """
    if window_size <= 0:
        raise ValueError("window_size must be positive")
    if not values:
        raise ValueError("values must not be empty")

    result: List[float] = []
    for i in range(len(values)):
        start = max(0, i + 1 - window_size)
        window = values[start : i + 1]
        result.append(sum(window) / len(window))
    return result


def factorial(n: int) -> int:
    """Return n! for a non-negative integer n.

    Raises:
        ValueError: if n is negative.
    """
    if n < 0:
        raise ValueError("n must be non-negative")
    result = 1
    for k in range(2, n + 1):
        result *= k
    return result


def dot_product(a: Sequence[float], b: Sequence[float]) -> float:
    """Return the dot product of two sequences of equal length.

    Raises:
        ValueError: if lengths differ.
    """
    if len(a) != len(b):
        raise ValueError("vectors must have the same length")
    return sum(x * y for x, y in zip(a, b))


def solve_quadratic(a: float, b: float, c: float) -> Tuple[complex, complex]:
    """Solve a quadratic equation a*x^2 + b*x + c = 0.

    Returns:
        A tuple (r1, r2) of roots, which may be real or complex.

    Raises:
        ValueError: if a is zero (not a quadratic).
    """
    if a == 0:
        raise ValueError("a must not be zero for a quadratic equation")

    discriminant = b ** 2 - 4 * a * c
    # Allow complex roots when discriminant < 0
    import cmath

    sqrt_disc = cmath.sqrt(discriminant)
    r1 = (-b + sqrt_disc) / (2 * a)
    r2 = (-b - sqrt_disc) / (2 * a)
    return (r1, r2)
