"""Tests for api_refresh_builder.mapping_builder."""

from __future__ import annotations

import pytest

from api_refresh_builder.mapping_builder import (
    build_all_steps,
    build_clone_config_row,
    build_config_check,
    build_config_lookup_existing,
    build_insert_map,
    build_lookup_query,
)


class TestLookupQuery:
    def test_basic(self):
        sql = build_lookup_query("348")
        assert "WHERE id = '348'" in sql
        assert sql.startswith("SELECT *")

    def test_composite_id(self):
        sql = build_lookup_query("149_1033")
        assert "WHERE id = '149_1033'" in sql

    def test_strips_whitespace(self):
        sql = build_lookup_query("  348  ")
        assert "WHERE id = '348'" in sql

    def test_empty_raises(self):
        with pytest.raises(ValueError, match="Source ID"):
            build_lookup_query("")

    def test_none_raises(self):
        with pytest.raises(ValueError, match="Source ID"):
            build_lookup_query(None)  # type: ignore[arg-type]


class TestInsertMap:
    def test_basic(self):
        sql = build_insert_map("348", "CACR0")
        assert "EXEC Aurora.IMIX.TransactionTypes_InsertMap '348', 'CACR0', 1;" == sql

    def test_strips_whitespace(self):
        sql = build_insert_map("  348 ", " CACR0 ")
        assert "'348', 'CACR0'" in sql

    def test_empty_id_raises(self):
        with pytest.raises(ValueError, match="Source ID"):
            build_insert_map("", "CACR0")

    def test_empty_code_raises(self):
        with pytest.raises(ValueError, match="Mapping code"):
            build_insert_map("348", "")


class TestConfigCheck:
    def test_basic(self):
        sql = build_config_check("CACR0")
        assert "WHERE TransactionTypeExternal = 'CACR0'" in sql
        assert "Config" in sql

    def test_empty_raises(self):
        with pytest.raises(ValueError, match="Mapping code"):
            build_config_check("")


class TestConfigLookupExisting:
    def test_basic(self):
        sql = build_config_lookup_existing("SCSHS")
        assert "WHERE TransactionTypeExternal = 'SCSHS'" in sql

    def test_empty_raises(self):
        with pytest.raises(ValueError, match="Existing reference code"):
            build_config_lookup_existing("")


class TestCloneConfigRow:
    def test_basic(self):
        sql = build_clone_config_row("NEWCODE", "EXISTING")
        assert "INSERT INTO" in sql
        assert "'NEWCODE'" in sql
        assert "WHERE" in sql
        assert "TransactionTypeExternal = 'EXISTING'" in sql

    def test_contains_all_config_columns(self):
        sql = build_clone_config_row("A", "B")
        for col in ("TransactionType", "TransferType", "Shares",
                     "TDW_Description", "TDW_SourceTable"):
            assert col in sql

    def test_empty_new_raises(self):
        with pytest.raises(ValueError, match="New mapping code"):
            build_clone_config_row("", "B")

    def test_empty_existing_raises(self):
        with pytest.raises(ValueError, match="Existing reference code"):
            build_clone_config_row("A", "")


class TestBuildAllSteps:
    def test_without_error_recovery(self):
        sql = build_all_steps("348", "CACR0")
        assert "-- Step 1" in sql
        assert "-- Step 2" in sql
        assert "Error-Recovery" not in sql

    def test_with_error_recovery(self):
        sql = build_all_steps("348", "CACR0", "SCSHS")
        assert "-- Step 1" in sql
        assert "-- Step 2" in sql
        assert "-- Error-Recovery Step 1" in sql
        assert "-- Error-Recovery Step 2" in sql
        assert "-- Error-Recovery Step 3" in sql
        assert "-- Error-Recovery Step 4" in sql

    def test_empty_existing_treated_as_none(self):
        sql = build_all_steps("348", "CACR0", "  ")
        assert "Error-Recovery" not in sql

    def test_ends_with_semicolon(self):
        sql = build_all_steps("348", "CACR0")
        assert sql.rstrip().endswith(";")
