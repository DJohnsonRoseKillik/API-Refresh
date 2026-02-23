"""SQL generators for the IMIX transaction-type mapping workflow."""

from __future__ import annotations

import logging
from typing import Sequence

from .constants import (
    CONFIG_COLUMNS,
    MAPPING_CONFIG_TABLE,
    MAPPING_PROC,
    MAPPING_TABLE,
)

logger = logging.getLogger(__name__)


def build_lookup_query(source_id: str) -> str:
    """Step 1 -- look up what a source ID currently maps to.

    Returns
    -------
    str
        ``SELECT * FROM ...Map WHERE id = '<source_id>'``
    """
    if not source_id or not source_id.strip():
        raise ValueError("Source ID must not be empty.")
    sid = source_id.strip()
    return f"SELECT *\nFROM {MAPPING_TABLE}\nWHERE id = '{sid}';"


def build_insert_map(source_id: str, mapping_code: str) -> str:
    """Step 2 -- create / update the mapping.

    Returns
    -------
    str
        ``EXEC Aurora.IMIX.TransactionTypes_InsertMap '<id>', '<code>', 1``
    """
    if not source_id or not source_id.strip():
        raise ValueError("Source ID must not be empty.")
    if not mapping_code or not mapping_code.strip():
        raise ValueError("Mapping code must not be empty.")
    sid = source_id.strip()
    code = mapping_code.strip()
    return f"EXEC {MAPPING_PROC} '{sid}', '{code}', 1;"


def build_config_check(mapping_code: str) -> str:
    """Error-recovery Step 1 -- check if the code exists in the config table.

    Returns
    -------
    str
        ``SELECT * FROM ...Config WHERE TransactionTypeExternal = '<code>'``
    """
    if not mapping_code or not mapping_code.strip():
        raise ValueError("Mapping code must not be empty.")
    code = mapping_code.strip()
    return (
        f"SELECT *\n"
        f"FROM {MAPPING_CONFIG_TABLE}\n"
        f"WHERE TransactionTypeExternal = '{code}';"
    )


def build_config_lookup_existing(existing_code: str) -> str:
    """Error-recovery Step 2 -- look up the reference row to clone.

    Returns
    -------
    str
        ``SELECT * FROM ...Config WHERE TransactionTypeExternal = '<existing>'``
    """
    if not existing_code or not existing_code.strip():
        raise ValueError("Existing reference code must not be empty.")
    code = existing_code.strip()
    return (
        f"SELECT *\n"
        f"FROM {MAPPING_CONFIG_TABLE}\n"
        f"WHERE TransactionTypeExternal = '{code}';"
    )


def build_clone_config_row(new_code: str, existing_code: str) -> str:
    """Error-recovery Step 3 -- clone an existing config row for the new code.

    Returns
    -------
    str
        An ``INSERT INTO ... SELECT ...`` statement that copies the row
        from *existing_code* and overwrites ``TransactionTypeExternal``
        with *new_code*.
    """
    if not new_code or not new_code.strip():
        raise ValueError("New mapping code must not be empty.")
    if not existing_code or not existing_code.strip():
        raise ValueError("Existing reference code must not be empty.")

    new = new_code.strip()
    existing = existing_code.strip()

    insert_cols = ",\n    ".join(CONFIG_COLUMNS)
    select_cols = ", ".join(CONFIG_COLUMNS[1:])  # everything except TransactionTypeExternal

    return (
        f"INSERT INTO {MAPPING_CONFIG_TABLE}\n"
        f"    ({insert_cols})\n"
        f"SELECT\n"
        f"    '{new}', {select_cols}\n"
        f"FROM\n"
        f"    {MAPPING_CONFIG_TABLE}\n"
        f"WHERE\n"
        f"    TransactionTypeExternal = '{existing}';"
    )


def build_all_steps(
    source_id: str,
    mapping_code: str,
    existing_code: str | None = None,
) -> str:
    """Concatenate all SQL blocks with step-header comments.

    Parameters
    ----------
    source_id:
        The transaction ID (e.g. ``"348"``).
    mapping_code:
        The target mapping code (e.g. ``"CACR0"``).
    existing_code:
        If provided, also generates the error-recovery SQL blocks
        (config check, clone row, re-run insert).
    """
    parts: list[str] = []

    parts.append("-- Step 1: Lookup current mapping")
    parts.append(build_lookup_query(source_id))

    parts.append("")
    parts.append("-- Step 2: Insert / update mapping")
    parts.append(build_insert_map(source_id, mapping_code))

    if existing_code and existing_code.strip():
        ec = existing_code.strip()
        parts.append("")
        parts.append("-- Error-Recovery Step 1: Check if new code exists in config")
        parts.append(build_config_check(mapping_code))

        parts.append("")
        parts.append("-- Error-Recovery Step 2: Lookup existing reference row")
        parts.append(build_config_lookup_existing(ec))

        parts.append("")
        parts.append("-- Error-Recovery Step 3: Clone config row for new code")
        parts.append(build_clone_config_row(mapping_code, ec))

        parts.append("")
        parts.append("-- Error-Recovery Step 4: Re-run mapping insert")
        parts.append(build_insert_map(source_id, mapping_code))

    return "\n".join(parts)
