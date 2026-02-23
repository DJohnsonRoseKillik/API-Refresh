"""SQL Tools Dashboard – Streamlit entry point.

Launch with:
    streamlit run app.py
"""

from __future__ import annotations

import logging

import streamlit as st

from api_refresh_builder.ui_helpers import inject_css

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(name)-30s  %(levelname)-8s  %(message)s",
)

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="SQL Tools Dashboard",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_css()

# ---------------------------------------------------------------------------
# Task selector (top of sidebar)
# ---------------------------------------------------------------------------
TASKS = {
    "API Refresh": "api_refresh",
    "Mapping": "mapping",
}

with st.sidebar:
    st.title("SQL Tools")
    selected_task = st.radio(
        "Select a task",
        options=list(TASKS.keys()),
        index=0,
        key="task_selector",
    )
    st.divider()

# ---------------------------------------------------------------------------
# Route to the selected page
# ---------------------------------------------------------------------------
if TASKS[selected_task] == "api_refresh":
    from api_refresh_builder.pages.api_refresh import render
    render()
elif TASKS[selected_task] == "mapping":
    from api_refresh_builder.pages.mapping import render  # type: ignore[assignment]
    render()
