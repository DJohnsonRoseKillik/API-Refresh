"""SQL generators for the CRM Amendments workflow.

Generates pre-check SELECTs, UPDATE statements, and post-check SELECTs
for ClientTransactions.mba transaction amendments.
"""

from __future__ import annotations

import logging
from typing import Mapping, Sequence

from .constants import CRM_CONTRIBUTIONS_TABLE, CRM_TRANSACTIONS_TABLE

logger = logging.getLogger(__name__)


def _clean_refs(refs: Sequence[str]) -> list[str]:
    """Strip whitespace and drop blanks. Raises on empty result."""
    cleaned = [r.strip() for r in refs if r and r.strip()]
    if not cleaned:
        raise ValueError("At least one transaction reference is required.")
    return cleaned


def _ref_in_clause(refs: Sequence[str]) -> str:
    """Build a SQL ``IN (...)`` value list from refs."""
    return ", ".join(f"'{r}'" for r in refs)


def _build_select_block(refs: Sequence[str]) -> str:
    """Two SELECT statements: one against transactions, one against contributions."""
    in_clause = _ref_in_clause(refs)
    return (
        f"SELECT *\n"
        f"FROM {CRM_TRANSACTIONS_TABLE}\n"
        f"WHERE ref IN ({in_clause});\n"
        f"\n"
        f"SELECT *\n"
        f"FROM {CRM_CONTRIBUTIONS_TABLE}\n"
        f"WHERE ref IN ({in_clause});"
    )


def build_pre_check(refs: Sequence[str]) -> str:
    """Generate pre-check SELECT queries for the given transaction refs."""
    return _build_select_block(_clean_refs(refs))


def build_update(refs: Sequence[str], fields: Mapping[str, str]) -> str:
    """Generate an UPDATE statement setting *fields* on the given refs.

    Parameters
    ----------
    refs:
        Transaction references (e.g. ``["IMIX.CT.11373522"]``).
    fields:
        Column-name -> value pairs to SET
        (e.g. ``{"Narrative2": "Employer Contribution"}``).
    """
    cleaned_refs = _clean_refs(refs)

    cleaned_fields: dict[str, str] = {}
    for col, val in fields.items():
        c = col.strip()
        v = val.strip()
        if c and v:
            cleaned_fields[c] = v
    if not cleaned_fields:
        raise ValueError("At least one field/value pair is required.")

    set_clauses = ",\n    ".join(
        f"{col} = '{val}'" for col, val in cleaned_fields.items()
    )
    in_clause = _ref_in_clause(cleaned_refs)

    return (
        f"UPDATE {CRM_TRANSACTIONS_TABLE}\n"
        f"SET {set_clauses}\n"
        f"WHERE ref IN ({in_clause});"
    )


def build_post_check(refs: Sequence[str]) -> str:
    """Generate post-check SELECT queries (identical SQL to pre-check)."""
    return _build_select_block(_clean_refs(refs))


def build_full_flow(refs: Sequence[str], fields: Mapping[str, str]) -> str:
    """Concatenate pre-check, UPDATE, and post-check with comment headers."""
    cleaned = _clean_refs(refs)
    parts: list[str] = [
        "-- Pre-check: inspect current state",
        build_pre_check(cleaned),
        "",
        "-- UPDATE: apply amendments",
        build_update(cleaned, fields),
        "",
        "-- Post-check: verify changes",
        build_post_check(cleaned),
    ]
    return "\n".join(parts)
