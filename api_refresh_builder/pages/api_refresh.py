"""API Refresh SQL Builder page."""

from __future__ import annotations

import logging

import streamlit as st

from api_refresh_builder.constants import (
    DEFAULT_TARGET_TYPES,
    PREVIEW_COUNT,
    REFRESH_FAMILIES,
)
from api_refresh_builder.parsing import ParseResult, parse_codes
from api_refresh_builder.sql_builder import build_sql
from api_refresh_builder.ui_helpers import copy_buttons

logger = logging.getLogger(__name__)


def _sidebar() -> tuple[str, list[str], bool, bool, bool]:
    """Render sidebar options and return selections."""
    refresh_family: str = st.selectbox(
        "Refresh family",
        options=REFRESH_FAMILIES,
        index=0,
    )

    st.subheader("Target Types")
    selected_defaults: list[str] = []
    for tt in DEFAULT_TARGET_TYPES:
        if st.checkbox(tt, value=True, key=f"tt_{tt}"):
            selected_defaults.append(tt)

    custom_types_raw: str = st.text_input(
        "Custom target types (comma-separated)",
        value="",
        help="Additional types appended after the defaults above.",
    )
    custom_types: list[str] = [
        t.strip() for t in custom_types_raw.split(",") if t.strip()
    ]
    all_target_types: list[str] = selected_defaults + custom_types

    st.divider()

    dedupe: bool = st.checkbox("Deduplicate codes", value=True)
    strict: bool = st.checkbox(
        "Strict validation",
        value=False,
        help="Block SQL generation when invalid codes exist.",
    )
    debug: bool = st.checkbox(
        "Debug (@debug=1)",
        value=False,
        help="If there are issues add @debug=1 to begin troubleshooting",
    )

    return refresh_family, all_target_types, dedupe, strict, debug


def render() -> None:
    """Render the API Refresh SQL Builder page."""
    st.header("API Refresh SQL Builder")
    st.caption(
        "Upload a spreadsheet of entity codes \u2192 generate a ready-to-run "
        "EXEC statement for SSMS."
    )

    # -- Sidebar options --
    with st.sidebar:
        refresh_family, all_target_types, dedupe, strict, debug = _sidebar()

    # -- File upload --
    uploaded = st.file_uploader(
        "Upload spreadsheet (.xls, .xlsx, .csv)",
        type=["xls", "xlsx", "csv"],
    )

    if uploaded is None:
        st.info("Upload a file to get started.")
        return

    # -- Parse --
    try:
        result: ParseResult = parse_codes(
            uploaded.getvalue(),
            uploaded.name,
            dedupe=dedupe,
        )
    except Exception as exc:
        st.error(f"Failed to parse file: {exc}")
        logger.exception("Parsing error")
        return

    # -- Stats --
    st.subheader("Parsing results")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total codes found", result.total_found)
    c2.metric("Valid codes", result.valid_count)
    c3.metric("Invalid codes", result.invalid_count)
    c4.metric("Duplicates removed", result.duplicates_removed)

    # -- Preview --
    with st.expander(f"Preview \u2013 first {PREVIEW_COUNT} valid codes", expanded=False):
        if result.valid_codes:
            st.code(", ".join(result.valid_codes[:PREVIEW_COUNT]), language=None)
        else:
            st.warning("No valid codes found.")

    if result.invalid_codes:
        with st.expander("Invalid codes", expanded=False):
            st.warning(
                f"{result.invalid_count} code(s) failed validation and will be excluded."
            )
            st.code(", ".join(result.invalid_codes), language=None)

    # -- Guard rails --
    if strict and result.invalid_codes:
        st.error(
            "Strict validation is ON and invalid codes were found. "
            "Fix the input or disable strict validation."
        )
        return

    if not result.valid_codes:
        st.error("No valid codes available to build SQL.")
        return

    if not all_target_types:
        st.warning("Select at least one target type in the sidebar.")
        return

    # -- Build SQL --
    try:
        sql: str = build_sql(
            result.valid_codes,
            refresh_family,
            all_target_types,
            debug=debug,
        )
    except ValueError as exc:
        st.error(str(exc))
        return

    st.subheader("Generated SQL")
    st.code(sql, language="sql")
    copy_buttons(sql, key_suffix="_api")

    st.divider()
    st.caption(
        "This tool only **generates** SQL text. "
        "It does not connect to or execute against any database."
    )
