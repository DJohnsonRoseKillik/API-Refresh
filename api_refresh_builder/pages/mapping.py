"""Transaction-type mapping wizard page."""

from __future__ import annotations

import logging

import streamlit as st

from api_refresh_builder.mapping_builder import (
    build_all_steps,
    build_clone_config_row,
    build_config_check,
    build_config_lookup_existing,
    build_insert_map,
    build_lookup_query,
)
from api_refresh_builder.ui_helpers import copy_buttons

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Session-state helpers
# ---------------------------------------------------------------------------
_STEP_KEY = "mapping_step"


def _current_step() -> int:
    return st.session_state.get(_STEP_KEY, 1)


def _set_step(n: int) -> None:
    st.session_state[_STEP_KEY] = n


# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------

def _sidebar() -> tuple[str, str]:
    """Render sidebar inputs and return (source_id, mapping_code)."""
    source_id: str = st.text_input(
        "Source ID",
        placeholder="e.g. 149_1033 or 348",
        help="The transaction type ID from the ticket.",
    )
    mapping_code: str = st.text_input(
        "Target mapping code",
        placeholder="e.g. SCSH or CACR0",
        help="Leave blank if you need to look it up first (Step 1).",
    )
    return source_id.strip(), mapping_code.strip()


# ---------------------------------------------------------------------------
# Page renderer
# ---------------------------------------------------------------------------

def render() -> None:
    """Render the Mapping wizard page."""
    st.header("Transaction Type Mapping")
    st.caption(
        "Generate SQL for IMIX transaction-type mapping requests. "
        "Work through the steps or use **Show all SQL** at the bottom."
    )

    with st.sidebar:
        source_id, mapping_code = _sidebar()

    # -- Step navigation --
    step = _current_step()

    # ------------------------------------------------------------------ #
    # Step 1 – Lookup
    # ------------------------------------------------------------------ #
    st.subheader("Step 1: Lookup current mapping")
    st.markdown(
        "Run this query to find what the source ID currently maps to. "
        "Use the result to confirm the target mapping code."
    )

    if not source_id:
        st.info("Enter a **Source ID** in the sidebar to begin.")
        return

    try:
        lookup_sql = build_lookup_query(source_id)
    except ValueError as exc:
        st.error(str(exc))
        return

    st.code(lookup_sql, language="sql")
    copy_buttons(lookup_sql, key_suffix="_map_s1")

    col_next1, _ = st.columns([1, 3])
    with col_next1:
        if st.button("Proceed to Step 2 \u2192", key="goto_step2"):
            _set_step(2)
            st.rerun()

    if step < 2:
        return

    # ------------------------------------------------------------------ #
    # Step 2 – Insert mapping
    # ------------------------------------------------------------------ #
    st.divider()
    st.subheader("Step 2: Insert / update mapping")

    if not mapping_code:
        st.warning("Enter the **Target mapping code** in the sidebar to generate the EXEC statement.")
        return

    try:
        insert_sql = build_insert_map(source_id, mapping_code)
    except ValueError as exc:
        st.error(str(exc))
        return

    st.code(insert_sql, language="sql")
    copy_buttons(insert_sql, key_suffix="_map_s2")

    # ------------------------------------------------------------------ #
    # Error-recovery expander
    # ------------------------------------------------------------------ #
    st.divider()
    with st.expander("Known error: *TransactionTypeExternal does not exist in Config table*", expanded=False):
        st.markdown(
            "If the EXEC above fails with this error, the mapping code "
            "doesn't exist in the config table yet. Follow the steps below."
        )

        existing_code: str = st.text_input(
            "Existing reference code (closest match from Middle Office)",
            placeholder="e.g. SCSHS",
            key="existing_ref_code",
            help="Contact Middle Office to find the closest existing code to clone from.",
        ).strip()

        if not existing_code:
            st.info("Enter the existing reference code to generate error-recovery SQL.")
        else:
            # ER Step 1 – confirm new code is missing
            st.markdown("**ER Step 1:** Confirm the new code is missing from config")
            er1_sql = build_config_check(mapping_code)
            st.code(er1_sql, language="sql")
            copy_buttons(er1_sql, key_suffix="_er1")

            # ER Step 2 – look up existing reference row
            st.markdown("**ER Step 2:** Look up existing reference row to clone")
            er2_sql = build_config_lookup_existing(existing_code)
            st.code(er2_sql, language="sql")
            copy_buttons(er2_sql, key_suffix="_er2")

            # ER Step 3 – clone config row
            st.markdown("**ER Step 3:** Clone config row for the new code")
            er3_sql = build_clone_config_row(mapping_code, existing_code)
            st.code(er3_sql, language="sql")
            copy_buttons(er3_sql, key_suffix="_er3")

            # ER Step 4 – re-run insert
            st.markdown("**ER Step 4:** Re-run the mapping insert")
            st.code(insert_sql, language="sql")
            copy_buttons(insert_sql, key_suffix="_er4")

    # ------------------------------------------------------------------ #
    # Show all SQL
    # ------------------------------------------------------------------ #
    st.divider()
    existing_for_all = st.session_state.get("existing_ref_code", "").strip() or None

    with st.expander("Show all SQL", expanded=False):
        try:
            all_sql = build_all_steps(source_id, mapping_code, existing_for_all)
        except ValueError as exc:
            st.error(str(exc))
            return
        st.code(all_sql, language="sql")
        copy_buttons(all_sql, key_suffix="_map_all")

    # ------------------------------------------------------------------ #
    # Reset
    # ------------------------------------------------------------------ #
    if st.button("Reset wizard", key="reset_mapping"):
        _set_step(1)
        st.rerun()

    st.divider()
    st.caption(
        "This tool only **generates** SQL text. "
        "It does not connect to or execute against any database."
    )
