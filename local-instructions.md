# Local Development Instructions

These instructions are for using the Molnify artefact with Claude Code on your local machine.
In the sandbox/app-builder environment, Python and tooling are pre-installed — these steps don't apply there.

## Python Setup

A virtual environment is included with openpyxl for working with Excel files:

```bash
./setup.sh                    # First time: create the venv
source .venv/bin/activate     # Activate before running any Python
```

Two utility scripts are provided:
- **`python inspect_excel.py <file.xlsx>`** — Analyze a plain Excel file before conversion (cell values, formulas, colors, charts, dependency analysis)
- **`python validate.py <file.xlsx>`** — Check a built Molnify app for common issues

See `python.md` for full documentation, openpyxl examples, and color conventions.

## Deploying Apps

Apps are uploaded through the web interface — there is no API.

1. Go to `https://app.molnify.com/#ajax/createApp` (requires login)
2. Select your `.xlsx` file and upload
3. The app is available at `app.molnify.com/app/<id>` (where `<id>` is the ID metadata value)

Uploading with the **same ID** replaces the existing app. This is how you update apps — the ID provides continuity for URLs, database tables, and scenarios.
