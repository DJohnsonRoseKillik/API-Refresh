"""API Refresh SQL Builder – Streamlit UI.

Launch with:
    streamlit run app.py
"""

from __future__ import annotations

import logging
import streamlit as st
import streamlit.components.v1 as components

from api_refresh_builder.constants import (
    DEFAULT_TARGET_TYPES,
    PREVIEW_COUNT,
    REFRESH_FAMILIES,
)
from api_refresh_builder.parsing import ParseResult, parse_codes
from api_refresh_builder.sql_builder import build_sql

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(name)-30s  %(levelname)-8s  %(message)s",
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="API Refresh SQL Builder",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Custom CSS
# ---------------------------------------------------------------------------
st.markdown(
    """
    <style>
    /* tighten up the main block */
    .block-container { padding-top: 2rem; max-width: 1100px; }
    /* monospace for the SQL output */
    .sql-output pre { font-family: 'Cascadia Code', 'Consolas', monospace; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Title
# ---------------------------------------------------------------------------
st.title("API Refresh SQL Builder")
st.caption("Upload a spreadsheet of entity codes → generate a ready-to-run EXEC statement for SSMS.")

# ---------------------------------------------------------------------------
# Sidebar – options
# ---------------------------------------------------------------------------
with st.sidebar:
    st.header("Options")

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
    strict: bool = st.checkbox("Strict validation", value=False,
                               help="Block SQL generation when invalid codes exist.")
    debug: bool = st.checkbox(
        "Debug (@debug=1)",
        value=False,
        help="If there are issues add @debug=1 to begin troubleshooting",
    )

# ---------------------------------------------------------------------------
# Main area – file upload
# ---------------------------------------------------------------------------
uploaded = st.file_uploader(
    "Upload spreadsheet (.xls, .xlsx, .csv)",
    type=["xls", "xlsx", "csv"],
)

if uploaded is None:
    st.info("Upload a file to get started.")
    st.stop()

# ---------------------------------------------------------------------------
# Parse
# ---------------------------------------------------------------------------
try:
    result: ParseResult = parse_codes(
        uploaded.getvalue(),
        uploaded.name,
        dedupe=dedupe,
    )
except Exception as exc:
    st.error(f"Failed to parse file: {exc}")
    logger.exception("Parsing error")
    st.stop()

# ---------------------------------------------------------------------------
# Stats
# ---------------------------------------------------------------------------
st.subheader("Parsing results")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total codes found", result.total_found)
col2.metric("Valid codes", result.valid_count)
col3.metric("Invalid codes", result.invalid_count)
col4.metric("Duplicates removed", result.duplicates_removed)

# ---------------------------------------------------------------------------
# Preview
# ---------------------------------------------------------------------------
with st.expander(f"Preview – first {PREVIEW_COUNT} valid codes", expanded=False):
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

# ---------------------------------------------------------------------------
# Guard rails
# ---------------------------------------------------------------------------
if strict and result.invalid_codes:
    st.error(
        "Strict validation is ON and invalid codes were found. "
        "Fix the input or disable strict validation."
    )
    st.stop()

if not result.valid_codes:
    st.error("No valid codes available to build SQL.")
    st.stop()

if not all_target_types:
    st.warning("Select at least one target type in the sidebar.")
    st.stop()

# ---------------------------------------------------------------------------
# Build SQL
# ---------------------------------------------------------------------------
try:
    sql: str = build_sql(
        result.valid_codes,
        refresh_family,
        all_target_types,
        debug=debug,
    )
except ValueError as exc:
    st.error(str(exc))
    st.stop()

st.subheader("Generated SQL")
st.code(sql, language="sql")

# ---------------------------------------------------------------------------
# Clipboard helpers
# ---------------------------------------------------------------------------

def _copy_via_pyperclip(text: str) -> bool:
    """Try copying with pyperclip; return True on success."""
    try:
        import pyperclip  # noqa: F811
        pyperclip.copy(text)
        return True
    except Exception:
        return False


def _js_clipboard_button(text: str, btn_label: str = "Copy SQL to clipboard (browser)") -> None:
    """Render a small HTML/JS button that copies *text* via the Clipboard API."""
    import html as _html
    escaped = _html.escape(text).replace("`", "\\`").replace("$", "\\$")
    components.html(
        f"""
        <button id="cpbtn"
                style="padding:0.5em 1.2em;font-size:0.95em;cursor:pointer;
                       border:1px solid #aaa;border-radius:6px;background:#f0f2f6;">
            {btn_label}
        </button>
        <script>
        document.getElementById("cpbtn").addEventListener("click", function() {{
            navigator.clipboard.writeText(`{escaped}`).then(function() {{
                document.getElementById("cpbtn").innerText = "Copied!";
                setTimeout(function(){{ document.getElementById("cpbtn").innerText = "{btn_label}"; }}, 2000);
            }});
        }});
        </script>
        """,
        height=50,
    )


col_a, col_b = st.columns(2)

with col_a:
    if st.button("Copy SQL to clipboard"):
        if _copy_via_pyperclip(sql):
            st.toast("SQL copied to clipboard!", icon="\u2705")
        else:
            st.warning(
                "pyperclip unavailable – use the browser button below or copy from the code block above."
            )

with col_b:
    _js_clipboard_button(sql)

st.divider()
st.caption("This tool only **generates** SQL text. It does not connect to or execute against any database.")
