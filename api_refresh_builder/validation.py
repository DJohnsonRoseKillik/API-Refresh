"""Validation helpers for the API Refresh SQL Builder."""

from __future__ import annotations

import re
from typing import Sequence

from .constants import CODE_PATTERN


def is_valid_code(code: str, pattern: re.Pattern[str] | None = None) -> bool:
    """Return True if *code* matches the allowed pattern."""
    pat = pattern or CODE_PATTERN
    return bool(pat.match(code))


def validate_codes(
    codes: Sequence[str],
    pattern: re.Pattern[str] | None = None,
) -> tuple[list[str], list[str]]:
    """Split *codes* into (valid, invalid) lists while preserving order."""
    pat = pattern or CODE_PATTERN
    valid: list[str] = []
    invalid: list[str] = []
    for c in codes:
        (valid if pat.match(c) else invalid).append(c)
    return valid, invalid
