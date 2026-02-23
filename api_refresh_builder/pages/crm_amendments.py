"""CRM Amendments page -- generate UPDATE SQL for ClientTransactions.mba."""

from __future__ import annotations

import logging

import streamlit as st

from api_refresh_builder.constants import CRM_UPDATABLE_FIELDS
from api_refresh_builder.crm_builder import (
    build_full_flow,
    build_post_check,
    build_pre_check,
    build_update,
)
from api_refresh_builder.ui_helpers import copy_buttons

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------

def _sidebar() -> list[str]:
    """Render sidebar inputs and return parsed refs."""
    raw: str = st.text_area(
        "Transaction references (one per line)",
        height=160,
        placeholder="IMIX.CT.11373522\nIMIX.CT.11373523\nIMIX.CT.11373524",
        help="Enter up to 6 transaction references, one per line.",
    )
    refs = [r.strip() for r in raw.splitlines() if r.strip()]

    if refs:
        st.success(f"{len(refs)} ref(s) parsed")
    else:
        st.info("Enter at least one ref to begin.")

    return refs


# ---------------------------------------------------------------------------
# Page renderer
# ---------------------------------------------------------------------------

def render() -> None:
    """Render the CRM Amendments page."""
    st.header("CRM Amendments")
    st.caption(
        "Generate pre-check, UPDATE, and post-check SQL for "
        "ClientTransactions.mba transaction amendments."
    )

    # -- Sidebar --
    with st.sidebar:
        refs = _sidebar()

    if not refs:
        st.info("Enter transaction references in the sidebar to get started.")
        return

    # ------------------------------------------------------------------ #
    # Fields to update
    # ------------------------------------------------------------------ #
    st.subheader("Fields to update")

    fields: dict[str, str] = {}

    for field_name in CRM_UPDATABLE_FIELDS:
        checked = st.checkbox(field_name, value=False, key=f"crm_f_{field_name}")
        if checked:
            val = st.text_input(
                f"Value for {field_name}",
                key=f"crm_v_{field_name}",
                placeholder=f"Enter value for {field_name}",
            )
            if val.strip():
                fields[field_name] = val.strip()

    # Custom field
    st.markdown("**Custom field**")
    c1, c2, c3 = st.columns([2, 2, 1])
    with c1:
        custom_name = st.text_input("Field name", key="crm_custom_name", placeholder="e.g. Status")
    with c2:
        custom_val = st.text_input("Field value", key="crm_custom_val", placeholder="e.g. Active")
    with c3:
        st.markdown("<br>", unsafe_allow_html=True)
        add_custom = st.button("Add", key="crm_add_custom")

    if add_custom and custom_name.strip() and custom_val.strip():
        if "crm_custom_fields" not in st.session_state:
            st.session_state["crm_custom_fields"] = {}
        st.session_state["crm_custom_fields"][custom_name.strip()] = custom_val.strip()

    custom_fields: dict[str, str] = st.session_state.get("crm_custom_fields", {})
    fields.update(custom_fields)

    if custom_fields:
        if st.button("Clear custom fields", key="crm_clear_custom"):
            st.session_state["crm_custom_fields"] = {}
            st.rerun()

    # Summary
    if fields:
        st.markdown("**Selected fields:**")
        for col, val in fields.items():
            st.markdown(f"- `{col}` = `'{val}'`")
    else:
        st.warning("Select or add at least one field to update.")
        return

    # ------------------------------------------------------------------ #
    # Best-practice callout
    # ------------------------------------------------------------------ #
    st.info(
        "Always run the pre-check SELECT first to confirm target rows "
        "before executing the UPDATE."
    )

    # ------------------------------------------------------------------ #
    # Generated SQL
    # ------------------------------------------------------------------ #
    st.subheader("Generated SQL")

    # Pre-check
    try:
        pre_sql = build_pre_check(refs)
    except ValueError as exc:
        st.error(str(exc))
        return

    st.markdown("**Pre-check**")
    st.code(pre_sql, language="sql")
    copy_buttons(pre_sql, key_suffix="_crm_pre")

    # UPDATE
    try:
        update_sql = build_update(refs, fields)
    except ValueError as exc:
        st.error(str(exc))
        return

    st.markdown("**UPDATE**")
    st.code(update_sql, language="sql")
    copy_buttons(update_sql, key_suffix="_crm_upd")

    # Post-check
    try:
        post_sql = build_post_check(refs)
    except ValueError as exc:
        st.error(str(exc))
        return

    st.markdown("**Post-check**")
    st.code(post_sql, language="sql")
    copy_buttons(post_sql, key_suffix="_crm_post")

    # ------------------------------------------------------------------ #
    # Show all SQL
    # ------------------------------------------------------------------ #
    st.divider()
    with st.expander("Show all SQL", expanded=False):
        try:
            all_sql = build_full_flow(refs, fields)
        except ValueError as exc:
            st.error(str(exc))
            return
        st.code(all_sql, language="sql")
        copy_buttons(all_sql, key_suffix="_crm_all")

    st.divider()
    st.caption(
        "This tool only **generates** SQL text. "
        "It does not connect to or execute against any database."
    )
