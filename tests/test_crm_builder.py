"""Tests for api_refresh_builder.crm_builder."""

from __future__ import annotations

import pytest

from api_refresh_builder.crm_builder import (
    build_full_flow,
    build_post_check,
    build_pre_check,
    build_update,
)


class TestBuildPreCheck:
    def test_single_ref(self):
        sql = build_pre_check(["IMIX.CT.123"])
        assert "ClientTransactions.mba.transactions" in sql
        assert "ClientTransactions.mba.transactions_contribution" in sql
        assert "'IMIX.CT.123'" in sql

    def test_multiple_refs(self):
        sql = build_pre_check(["IMIX.CT.1", "IMIX.CT.2", "IMIX.CT.3"])
        assert "'IMIX.CT.1', 'IMIX.CT.2', 'IMIX.CT.3'" in sql

    def test_strips_whitespace(self):
        sql = build_pre_check(["  IMIX.CT.1  ", " IMIX.CT.2 "])
        assert "'IMIX.CT.1'" in sql
        assert "'IMIX.CT.2'" in sql

    def test_empty_refs_raises(self):
        with pytest.raises(ValueError, match="reference"):
            build_pre_check([])

    def test_blank_refs_raises(self):
        with pytest.raises(ValueError, match="reference"):
            build_pre_check(["", "  "])

    def test_ends_with_semicolon(self):
        sql = build_pre_check(["IMIX.CT.1"])
        assert sql.rstrip().endswith(";")


class TestBuildUpdate:
    def test_single_field(self):
        sql = build_update(
            ["IMIX.CT.1"],
            {"Narrative2": "Employer Contribution"},
        )
        assert "UPDATE ClientTransactions.mba.transactions" in sql
        assert "SET Narrative2 = 'Employer Contribution'" in sql
        assert "WHERE ref IN ('IMIX.CT.1')" in sql

    def test_multiple_fields(self):
        sql = build_update(
            ["IMIX.CT.1"],
            {"Narrative2": "Employer Contribution", "TransactionTypeExternal": "EMPLOYER"},
        )
        assert "Narrative2 = 'Employer Contribution'" in sql
        assert "TransactionTypeExternal = 'EMPLOYER'" in sql

    def test_multiple_refs_in_clause(self):
        sql = build_update(
            ["IMIX.CT.1", "IMIX.CT.2"],
            {"TransactionTypeExternal": "CASHT"},
        )
        assert "'IMIX.CT.1', 'IMIX.CT.2'" in sql

    def test_strips_whitespace_on_fields(self):
        sql = build_update(
            ["IMIX.CT.1"],
            {"  Narrative2  ": "  Employer  "},
        )
        assert "Narrative2 = 'Employer'" in sql

    def test_empty_refs_raises(self):
        with pytest.raises(ValueError, match="reference"):
            build_update([], {"Narrative2": "X"})

    def test_empty_fields_raises(self):
        with pytest.raises(ValueError, match="field"):
            build_update(["IMIX.CT.1"], {})

    def test_blank_field_values_raises(self):
        with pytest.raises(ValueError, match="field"):
            build_update(["IMIX.CT.1"], {"Narrative2": "  "})

    def test_ends_with_semicolon(self):
        sql = build_update(["IMIX.CT.1"], {"Narrative2": "X"})
        assert sql.rstrip().endswith(";")


class TestBuildPostCheck:
    def test_matches_pre_check_content(self):
        refs = ["IMIX.CT.1", "IMIX.CT.2"]
        pre = build_pre_check(refs)
        post = build_post_check(refs)
        assert pre == post

    def test_empty_raises(self):
        with pytest.raises(ValueError, match="reference"):
            build_post_check([])


class TestBuildFullFlow:
    def test_contains_all_sections(self):
        sql = build_full_flow(
            ["IMIX.CT.1"],
            {"Narrative2": "Employer Contribution"},
        )
        assert "-- Pre-check" in sql
        assert "-- UPDATE" in sql
        assert "-- Post-check" in sql

    def test_contains_select_and_update(self):
        sql = build_full_flow(
            ["IMIX.CT.1"],
            {"TransactionTypeExternal": "EMPLOYER"},
        )
        assert "SELECT *" in sql
        assert "UPDATE" in sql

    def test_ends_with_semicolon(self):
        sql = build_full_flow(
            ["IMIX.CT.1"],
            {"Narrative2": "X"},
        )
        assert sql.rstrip().endswith(";")
