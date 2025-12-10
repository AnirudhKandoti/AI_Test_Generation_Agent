"""String utilities for test generation experiments."""

from __future__ import annotations

def normalize_whitespace(s: str) -> str:
    """Collapse consecutive whitespace into a single space and strip ends."""
    parts = s.split()
    return " ".join(parts)

def is_palindrome(s: str) -> bool:
    """Return True if s is a palindrome ignoring case and non-alphanumeric characters."""
    cleaned = [ch.lower() for ch in s if ch.isalnum()]
    return cleaned == list(reversed(cleaned))
