# SQL Tools Dashboard

Local Streamlit dashboard for generating SQL statements used in day-to-day
operations. Select a task from the sidebar to get started.

## Available tools

| Tool | Description |
|------|-------------|
| **API Refresh** | Upload a spreadsheet of entity codes and generate an `EXEC` statement for the refresh stored procedure (Global Plus or IMIX). |
| **Mapping** | Step-by-step wizard for IMIX transaction-type mapping requests, including error-recovery SQL for missing config entries. |

## Quick start

```bash
# 1. Create a virtual environment (recommended)
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS / Linux

# 2. Install dependencies
python -m pip install -r requirements.txt

# 3. Run the app
python -m streamlit run app.py
```

The browser opens automatically at `http://localhost:8501`.

## Usage

### API Refresh

1. Select **API Refresh** in the sidebar.
2. **Upload** a `.xls`, `.xlsx`, or `.csv` file containing entity codes in the
   first column.
3. **Configure** options in the sidebar:
   - Refresh family (Global Plus / IMIX)
   - Target types (checkboxes + custom text input)
   - Deduplicate toggle
   - Strict validation toggle
   - Debug toggle
4. **Copy** the generated SQL and paste it into SSMS.

### Mapping

1. Select **Mapping** in the sidebar.
2. Enter the **Source ID** from the ticket (e.g. `149_1033` or `348`).
3. **Step 1** generates a lookup query -- run it in SSMS to find the current mapping.
4. Enter the **Target mapping code** (e.g. `SCSH` or `CACR0`).
5. **Step 2** generates the `EXEC` statement to create/update the mapping.
6. If you hit the *"TransactionTypeExternal does not exist in Config table"*
   error, expand the error-recovery section, enter the existing reference code
   from Middle Office, and follow the four recovery steps.
7. Use **Show all SQL** to view/copy every block at once.

## Running tests

```bash
python -m pytest
```

## Project structure

```
app.py                              # Dashboard router (Streamlit entry point)
api_refresh_builder/
    __init__.py
    constants.py                    # Config & constants
    parsing.py                      # File parsing & code extraction
    validation.py                   # Regex validation helpers
    sql_builder.py                  # API Refresh SQL generator
    mapping_builder.py              # Mapping SQL generator
    ui_helpers.py                   # Shared clipboard & CSS helpers
    pages/
        __init__.py
        api_refresh.py              # API Refresh page
        mapping.py                  # Mapping wizard page
tests/
    test_parsing.py
    test_sql_builder.py
    test_mapping_builder.py
requirements.txt
pyproject.toml
```

## Troubleshooting

| Symptom | Fix |
|---|---|
| `pip` / `streamlit` not recognised | Use `python -m pip` and `python -m streamlit run app.py` |
| `ModuleNotFoundError: No module named 'openpyxl'` | `python -m pip install openpyxl` |
| `.xls` files fail | `python -m pip install xlrd` |
| Clipboard button doesn't work | Install `pyperclip` or use the browser-based copy button |

## Security

This tool **only generates SQL text**. It never connects to or executes
queries against any database.
