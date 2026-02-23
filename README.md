# API Refresh SQL Builder

Local Streamlit app that converts a spreadsheet of entity/API codes into a
ready-to-run `EXEC` statement for SQL Server Management Studio (SSMS).

## Quick start

```bash
# 1. Create a virtual environment (recommended)
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS / Linux

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the app
streamlit run app.py
```

The browser opens automatically at `http://localhost:8501`.

## Usage

1. **Upload** a `.xls`, `.xlsx`, or `.csv` file containing entity codes in the
   first column.
2. **Configure** options in the sidebar:
   - Refresh family (Global Plus / IMIX)
   - Target types (checkboxes + custom text input)
   - Deduplicate toggle
   - Strict validation toggle
   - Debug toggle
3. **Copy** the generated SQL and paste it into SSMS.

## Running tests

```bash
pip install pytest
pytest
```

## Project structure

```
app.py                         # Streamlit UI entry point
api_refresh_builder/
    __init__.py
    constants.py               # Config & constants
    parsing.py                 # File parsing & code extraction
    validation.py              # Regex validation helpers
    sql_builder.py             # SQL EXEC statement generator
tests/
    test_parsing.py
    test_sql_builder.py
requirements.txt
pyproject.toml
```

## Troubleshooting

| Symptom | Fix |
|---|---|
| `ModuleNotFoundError: No module named 'openpyxl'` | `pip install openpyxl` |
| `.xls` files fail | `pip install xlrd` |
| Clipboard button doesn't work | Install `pyperclip` or use the browser-based copy button |
| `streamlit: command not found` | Activate your virtual environment or `pip install streamlit` |

## Security

This tool **only generates SQL text**. It never connects to or executes
queries against any database.
