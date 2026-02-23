"""Tests for api_refresh_builder.parsing."""

from __future__ import annotations

import io

import pandas as pd
import pytest

from api_refresh_builder.parsing import parse_codes


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _csv_bytes(rows: list[list[str]]) -> bytes:
    """Build raw CSV bytes from a list of rows (no header row)."""
    lines = [",".join(r) for r in rows]
    return "\n".join(lines).encode("utf-8")


def _xlsx_bytes(values: list[str]) -> bytes:
    """Build an in-memory .xlsx from a single-column list of values."""
    df = pd.DataFrame(values)
    buf = io.BytesIO()
    df.to_excel(buf, index=False, header=False, engine="openpyxl")
    return buf.getvalue()


# ---------------------------------------------------------------------------
# CSV parsing
# ---------------------------------------------------------------------------

class TestCSVParsing:
    def test_basic_csv(self):
        raw = _csv_bytes([["ABC123"], ["DEF456"], ["GHI789"]])
        result = parse_codes(raw, "codes.csv")
        assert result.valid_codes == ["ABC123", "DEF456", "GHI789"]

    def test_strips_whitespace(self):
        raw = _csv_bytes([["  ABC123  "], [" DEF456"]])
        result = parse_codes(raw, "codes.csv")
        assert result.valid_codes == ["ABC123", "DEF456"]

    def test_ignores_blanks(self):
        raw = _csv_bytes([["ABC123"], [""], ["DEF456"]])
        result = parse_codes(raw, "codes.csv")
        assert result.valid_codes == ["ABC123", "DEF456"]


# ---------------------------------------------------------------------------
# Excel (.xlsx) parsing
# ---------------------------------------------------------------------------

class TestExcelParsing:
    def test_basic_xlsx(self):
        raw = _xlsx_bytes(["CODE1", "CODE2", "CODE3"])
        result = parse_codes(raw, "data.xlsx")
        assert result.valid_codes == ["CODE1", "CODE2", "CODE3"]

    def test_header_as_data(self):
        """First cell must be included even though pandas might treat it as a header."""
        raw = _xlsx_bytes(["BER0152C", "XYZ999", "ABC001"])
        result = parse_codes(raw, "ticket.xlsx")
        assert result.valid_codes[0] == "BER0152C"
        assert len(result.valid_codes) == 3


# ---------------------------------------------------------------------------
# Dedupe
# ---------------------------------------------------------------------------

class TestDedupe:
    def test_dedupe_preserves_first_occurrence_order(self):
        raw = _csv_bytes([["A"], ["B"], ["A"], ["C"], ["B"]])
        result = parse_codes(raw, "dup.csv", dedupe=True)
        assert result.valid_codes == ["A", "B", "C"]
        assert result.duplicates_removed == 2

    def test_no_dedupe_keeps_all(self):
        raw = _csv_bytes([["A"], ["B"], ["A"]])
        result = parse_codes(raw, "dup.csv", dedupe=False)
        assert result.valid_codes == ["A", "B", "A"]
        assert result.duplicates_removed == 0


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

class TestValidation:
    def test_invalid_codes_excluded(self):
        raw = _csv_bytes([["GOOD1"], ["BAD!@#"], ["ALSO_GOOD"]])
        result = parse_codes(raw, "mixed.csv")
        assert result.valid_codes == ["GOOD1", "ALSO_GOOD"]
        assert result.invalid_codes == ["BAD!@#"]

    def test_stats_correct(self):
        raw = _csv_bytes([["A"], ["B"], ["A"], ["!!!"]])
        result = parse_codes(raw, "s.csv", dedupe=True)
        assert result.total_found == 4
        assert result.valid_count == 2  # A, B (one A deduped)
        assert result.invalid_count == 1
        assert result.duplicates_removed == 1
