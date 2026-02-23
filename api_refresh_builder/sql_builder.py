"""Generate the EXEC SQL block for the API refresh stored procedure."""

from __future__ import annotations

import logging
from typing import Sequence

from .constants import STORED_PROCEDURES

logger = logging.getLogger(__name__)


def build_sql(
    codes: Sequence[str],
    refresh_family: str,
    target_types: Sequence[str],
    *,
    debug: bool = False,
) -> str:
    """Build a single EXEC statement ready for SSMS.

    Parameters
    ----------
    codes:
        Validated entity codes.
    refresh_family:
        Key into ``STORED_PROCEDURES`` (e.g. ``"Global Plus"``).
    target_types:
        List of target type strings (e.g. ``["Contact", "Account"]``).
    debug:
        Append ``@debug = 1`` when True.

    Returns
    -------
    str
        A complete, copy-pasteable SQL EXEC statement.
    """
    if not codes:
        raise ValueError("No codes provided – cannot build SQL.")
    if not target_types:
        raise ValueError("No target types selected – cannot build SQL.")
    if refresh_family not in STORED_PROCEDURES:
        raise ValueError(
            f"Unknown refresh family '{refresh_family}'. "
            f"Expected one of: {list(STORED_PROCEDURES)}"
        )

    proc = STORED_PROCEDURES[refresh_family]
    codes_str = ",".join(codes)
    types_str = ",".join(target_types)

    lines: list[str] = [f"EXEC {proc}"]
    lines.append(f"    @EntityCodes = '{codes_str}',")

    if debug:
        lines.append(f"    @TargetTypes = '{types_str}',")
        lines.append("    @debug = 1;")
    else:
        lines.append(f"    @TargetTypes = '{types_str}';")

    sql = "\n".join(lines)
    logger.info("Generated SQL (%d codes, debug=%s)", len(codes), debug)
    return sql
