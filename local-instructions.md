# Local Development Instructions

These instructions are for using the Molnify artefact with Claude Code on your local machine.
In the sandbox/app-builder environment, Python and tooling are pre-installed - these steps don't apply there.

## Python Setup

This skill bundles a prebuilt wheel (`molnify_app_builder-<version>-py3-none-any.whl`)
alongside the Python sources. Installing the wheel makes the `AppBuilder` library
importable from any working directory and puts the helper commands on your PATH. Install
it into whichever Python environment you use - pick the case that matches your setup
(`SKILL_DIR` is this skill's directory):

```bash
# Into an existing project virtualenv (activate it first, or call its pip directly):
pip install "$SKILL_DIR"/molnify_app_builder-*.whl

# Into a fresh project-local virtualenv:
python3 -m venv .venv && .venv/bin/pip install "$SKILL_DIR"/molnify_app_builder-*.whl

# Shared across projects (one venv beside the skill, reused everywhere):
python3 -m venv "$SKILL_DIR/.venv" && "$SKILL_DIR/.venv/bin/pip" install "$SKILL_DIR"/molnify_app_builder-*.whl
```

`pip` pulls in `openpyxl` automatically. After installing, in that environment:

- `from molnify_builder import AppBuilder` works from any directory - write your build
  scripts wherever you like.
- **`molnify-inspect-excel <file.xlsx>`** - analyze a plain Excel file before conversion
  (cell values, formulas, colors, charts, dependency analysis).
- **`molnify-validate <file.xlsx>`** - check a built Molnify app for common issues.

You can also run the tools without installing, straight from the skill directory:
`python "$SKILL_DIR/molnify_validate.py" <file.xlsx>`.

See `python.md` for full documentation, openpyxl examples, and color conventions.

## Deploying Apps

Apps are uploaded through the web interface - there is no API.

1. Go to `https://app.molnify.com/#ajax/createApp` (requires login)
2. Select your `.xlsx` file and upload
3. The app is available at `app.molnify.com/app/<id>` (where `<id>` is the ID metadata value)

Uploading with the **same ID** replaces the existing app. This is how you update apps - the ID provides continuity for URLs, database tables, and scenarios.

## Companion Guides

The main reference covers most tasks. The companion files are for **specific needs** - read them when the task requires it:

- **`creating-from-scratch.md`** - AppBuilder usage, row tracking, dropdowns, interleaving
- **`converting-excel.md`** - Converting a plain Excel file (no color coding) into a Molnify app
- **`styling.md`** - DOM structure, CSS selectors, CSS Grid escape pattern, Bootstrap overrides. Read for **layout restructuring** (moving panels, custom grids, non-standard column arrangements). Not needed for basic color/font changes.
- **`styling-examples.md`** - Complete layout recipes (dashboards, sidebars, kiosk, dark theme, etc.). Read when you need a **starting point for a specific layout**.
- **`design.md`** - Visual design principles: typography, color, hierarchy, composition, and avoiding generic AI aesthetics. **Read before choosing fonts, colors, or visual direction** for any app.
- **`patterns.md`** - Wizards, grouped forms, master-detail, conditional forms. Read when implementing a **specific UX pattern** - these are tested implementations, don't reinvent them.
- **`database.md`** - Database tables, schema provisioning, autofill, reading and writing data
- **`report-templates.md`** - Report template engines (HTML, DOCX, XLSX), template syntax
- **`custom-frontend.md`** - Replace Molnify's default UI entirely with a headless, fully custom frontend
- **`advanced-topics.md`** - DOM lifecycle, JS execution details, setValueForVariable debouncing, troubleshooting
- **`python.md`** - openpyxl examples, color conventions, working with formulas
- **`examples/`** - Complete app examples: expense tracker, sales dashboard, financial model
