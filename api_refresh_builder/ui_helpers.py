"""Shared UI helpers: clipboard, CSS, and reusable widgets."""

from __future__ import annotations

import html as _html
import logging

import streamlit as st
import streamlit.components.v1 as components

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Custom CSS (injected once per page load)
# ---------------------------------------------------------------------------

_CSS = """
<style>
.block-container { padding-top: 2rem; max-width: 1100px; }
.sql-output pre { font-family: 'Cascadia Code', 'Consolas', monospace; }
</style>
"""


def inject_css() -> None:
    """Inject shared CSS into the current page."""
    st.markdown(_CSS, unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Clipboard helpers
# ---------------------------------------------------------------------------

def copy_via_pyperclip(text: str) -> bool:
    """Try copying *text* with pyperclip; return True on success."""
    try:
        import pyperclip
        pyperclip.copy(text)
        return True
    except Exception:
        return False


def js_clipboard_button(
    text: str,
    btn_label: str = "Copy SQL to clipboard (browser)",
    *,
    key: str = "cpbtn",
) -> None:
    """Render an HTML/JS button that copies *text* via the Clipboard API."""
    escaped = _html.escape(text).replace("`", "\\`").replace("$", "\\$")
    components.html(
        f"""
        <button id="{key}"
                style="padding:0.5em 1.2em;font-size:0.95em;cursor:pointer;
                       border:1px solid #aaa;border-radius:6px;background:#f0f2f6;">
            {btn_label}
        </button>
        <script>
        document.getElementById("{key}").addEventListener("click", function() {{
            navigator.clipboard.writeText(`{escaped}`).then(function() {{
                document.getElementById("{key}").innerText = "Copied!";
                setTimeout(function(){{ document.getElementById("{key}").innerText = "{btn_label}"; }}, 2000);
            }});
        }});
        </script>
        """,
        height=50,
    )


def copy_buttons(sql: str, *, key_suffix: str = "") -> None:
    """Render a pair of copy buttons (pyperclip + JS fallback) for *sql*."""
    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("Copy SQL to clipboard", key=f"cp_native{key_suffix}"):
            if copy_via_pyperclip(sql):
                st.toast("SQL copied to clipboard!", icon="\u2705")
            else:
                st.warning(
                    "pyperclip unavailable \u2013 use the browser button or copy from the code block."
                )
    with col_b:
        js_clipboard_button(sql, key=f"cpbtn{key_suffix}")
