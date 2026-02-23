"""Tests for api_refresh_builder.sql_builder."""

from __future__ import annotations

import pytest

from api_refresh_builder.sql_builder import build_sql


class TestBuildSQL:
    """Verify deterministic SQL formatting."""

    CODES = ["CODE1", "CODE2", "CODE3"]
    TYPES = ["Contact", "Account", "CustomerAddress"]

    def test_global_plus_no_debug(self):
        sql = build_sql(self.CODES, "Global Plus", self.TYPES, debug=False)
        expected = (
            "EXEC [ServiceBroker].[crm_MSCRM].[Entity_Process_Log__ManualInsert_GlobalPlus]\n"
            "    @EntityCodes = 'CODE1,CODE2,CODE3',\n"
            "    @TargetTypes = 'Contact,Account,CustomerAddress';"
        )
        assert sql == expected

    def test_imix_with_debug(self):
        sql = build_sql(self.CODES, "IMIX", self.TYPES, debug=True)
        expected = (
            "EXEC [ServiceBroker].[crm_MSCRM].[Entity_Process_Log__ManualInsert_IMIX]\n"
            "    @EntityCodes = 'CODE1,CODE2,CODE3',\n"
            "    @TargetTypes = 'Contact,Account,CustomerAddress',\n"
            "    @debug = 1;"
        )
        assert sql == expected

    def test_single_code_single_type(self):
        sql = build_sql(["ONLY"], "Global Plus", ["Contact"])
        assert "@EntityCodes = 'ONLY'" in sql
        assert "@TargetTypes = 'Contact';" in sql

    def test_combined_target_types(self):
        types = ["Contact", "Account", "CustomType"]
        sql = build_sql(["X"], "IMIX", types)
        assert "@TargetTypes = 'Contact,Account,CustomType';" in sql

    def test_no_codes_raises(self):
        with pytest.raises(ValueError, match="No codes"):
            build_sql([], "IMIX", ["Contact"])

    def test_no_types_raises(self):
        with pytest.raises(ValueError, match="No target types"):
            build_sql(["A"], "IMIX", [])

    def test_unknown_family_raises(self):
        with pytest.raises(ValueError, match="Unknown refresh family"):
            build_sql(["A"], "BadFamily", ["Contact"])

    def test_debug_omitted_when_false(self):
        sql = build_sql(["A"], "IMIX", ["Contact"], debug=False)
        assert "@debug" not in sql

    def test_trailing_semicolon(self):
        for debug in (True, False):
            sql = build_sql(["A"], "IMIX", ["Contact"], debug=debug)
            assert sql.rstrip().endswith(";")
