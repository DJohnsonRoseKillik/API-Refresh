"""Parse entity/API codes from uploaded spreadsheet or CSV files."""

from __future__ import annotations

import io
import logging
from dataclasses import dataclass, field
from typing import Sequence

import pandas as pd

from .constants import CODE_PATTERN

logger = logging.getLogger(__name__)


@dataclass
class ParseResult:
    """Container for parsing output and statistics."""

    raw_codes: list[str] = field(default_factory=list)
    valid_codes: list[str] = field(default_factory=list)
    invalid_codes: list[str] = field(default_factory=list)
    duplicates_removed: int = 0

    @property
    def total_found(self) -> int:
        return len(self.raw_codes)

    @property
    def valid_count(self) -> int:
        return len(self.valid_codes)

    @property
    def invalid_count(self) -> int:
        return len(self.invalid_codes)


def _read_first_column(buf: io.BytesIO, filename: str) -> list[str]:
    """Read the first column from a spreadsheet or CSV, treating row 0 as data."""
    ext = filename.rsplit(".", maxsplit=1)[-1].lower()

    if ext == "csv":
        df = pd.read_csv(buf, header=None, dtype=str)
    elif ext in ("xls", "xlsx"):
        engine = "xlrd" if ext == "xls" else "openpyxl"
        df = pd.read_excel(buf, header=None, dtype=str, engine=engine)
    else:
        raise ValueError(f"Unsupported file type: .{ext}")

    if df.empty:
        return []

    first_col: pd.Series = df.iloc[:, 0]
    return first_col.tolist()


def parse_codes(
    file_bytes: bytes,
    filename: str,
    *,
    dedupe: bool = True,
    validation_pattern: str | None = None,
) -> ParseResult:
    """Parse, clean, validate and optionally deduplicate codes.

    Parameters
    ----------
    file_bytes:
        Raw bytes of the uploaded file.
    filename:
        Original filename (used to detect format).
    dedupe:
        Remove duplicates while preserving first-occurrence order.
    validation_pattern:
        Override regex pattern string; ``None`` uses the default from constants.
    """
    buf = io.BytesIO(file_bytes)
    raw_values = _read_first_column(buf, filename)

    pattern = CODE_PATTERN if validation_pattern is None else __import__("re").compile(validation_pattern)

    raw_codes: list[str] = []
    valid_codes: list[str] = []
    invalid_codes: list[str] = []
    seen: set[str] = set()
    duplicates_removed = 0

    for val in raw_values:
        if val is None or (isinstance(val, float) and pd.isna(val)):
            continue
        code = str(val).strip()
        if not code:
            continue

        raw_codes.append(code)

        if not pattern.match(code):
            invalid_codes.append(code)
            logger.warning("Invalid code skipped: %s", code)
            continue

        if dedupe:
            if code in seen:
                duplicates_removed += 1
                continue
            seen.add(code)

        valid_codes.append(code)

    logger.info(
        "Parsed %d raw codes → %d valid, %d invalid, %d dupes removed",
        len(raw_codes),
        len(valid_codes),
        len(invalid_codes),
        duplicates_removed,
    )

    return ParseResult(
        raw_codes=raw_codes,
        valid_codes=valid_codes,
        invalid_codes=invalid_codes,
        duplicates_removed=duplicates_removed,
    )
