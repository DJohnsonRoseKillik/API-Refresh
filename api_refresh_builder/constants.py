"""Centralised constants for the API Refresh SQL Builder."""

from __future__ import annotations

import re

# ---------------------------------------------------------------------------
# Stored procedure mapping
# ---------------------------------------------------------------------------
STORED_PROCEDURES: dict[str, str] = {
    "Global Plus": (
        "[ServiceBroker].[crm_MSCRM].[Entity_Process_Log__ManualInsert_GlobalPlus]"
    ),
    "IMIX": (
        "[ServiceBroker].[crm_MSCRM].[Entity_Process_Log__ManualInsert_IMIX]"
    ),
}

REFRESH_FAMILIES: list[str] = list(STORED_PROCEDURES.keys())

# ---------------------------------------------------------------------------
# Default TargetTypes (order matters – custom types appended after these)
# ---------------------------------------------------------------------------
DEFAULT_TARGET_TYPES: list[str] = [
    "Contact",
    "Account",
    "CustomerAddress",
    "ft_Product",
    "ProductAffiliations",
]

# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------
CODE_PATTERN: re.Pattern[str] = re.compile(r"^[A-Za-z0-9_\-]+$")

# ---------------------------------------------------------------------------
# Mapping workflow
# ---------------------------------------------------------------------------
MAPPING_TABLE: str = "Aurora.IMIX.TransactionTypes_TransactionTypeExternal_Map"
MAPPING_CONFIG_TABLE: str = (
    "Aurora.IMIX.TransactionTypes_TransactionTypeExternal_Config"
)
MAPPING_PROC: str = "Aurora.IMIX.TransactionTypes_InsertMap"

CONFIG_COLUMNS: list[str] = [
    "TransactionTypeExternal",
    "TransactionType",
    "TransferType",
    "Shares",
    "TDW_Description",
    "TDW_SourceTable",
]

# ---------------------------------------------------------------------------
# CRM Amendments workflow
# ---------------------------------------------------------------------------
CRM_TRANSACTIONS_TABLE: str = "ClientTransactions.mba.transactions"
CRM_CONTRIBUTIONS_TABLE: str = "ClientTransactions.mba.transactions_contribution"

CRM_UPDATABLE_FIELDS: list[str] = [
    "Narrative2",
    "TransactionTypeExternal",
]

# ---------------------------------------------------------------------------
# UI defaults
# ---------------------------------------------------------------------------
PREVIEW_COUNT: int = 25
