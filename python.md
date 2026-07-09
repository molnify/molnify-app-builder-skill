# Python Development Environment

Companion to the main reference.

A Python virtual environment is included for programmatically working with Molnify Excel apps.

**When to use raw openpyxl vs AppBuilder:**
- **Creating a new app from scratch** → Use `AppBuilder` (see `creating-from-scratch.md`)
- **Modifying an existing Excel file** (adding cells, changing formulas, reading structure) → Use raw openpyxl with the patterns below

## Setup

This skill ships a prebuilt wheel alongside the Python sources. Install the wheel into a
Python environment to make `AppBuilder` importable from any working directory and to put
the `molnify-validate` and `molnify-inspect-excel` commands on your PATH. See
`local-instructions.md` for the install recipes (`pip` pulls in `openpyxl` automatically).

## Installed Libraries
- **openpyxl** - Read/write Excel xlsx files, supports formulas, charts, and styling

## Included Scripts

Two ready-made scripts are provided for converting Excel files into Molnify apps:

- **`molnify_inspect_excel.py <file.xlsx>`** (installed command: `molnify-inspect-excel`) - Analyzes a plain Excel file before conversion. Outputs cell values, formulas, colors, conditional formatting, charts, named ranges, data validations, and a formula dependency analysis that identifies potential inputs and outputs.
- **`molnify_validate.py <converted_file.xlsx>`** (installed command: `molnify-validate`) - Checks a converted Molnify app for common issues: missing metadata, incorrect colors, missing `molnifyIgnore`, input formulas referencing other inputs, chart structure problems. Returns exit code 0 if no errors, 1 otherwise.

## Cell Color Conventions

Molnify identifies cell types by **exact** color matching (no tolerance). When **creating** apps, use the recommended colors below. When **reading/parsing** apps, be aware that the backend also accepts the additional variants listed for compatibility with Google Sheets and older Excel versions.

### Recommended colors (use these when creating apps)

Input `#00B050`, Output `#FF0000`, Chart/Table `#0070C0`, Action `#FFFF00`, Metadata `#7030A0`.

### Also accepted (for parsing existing apps)

| Cell Type | Hex | Origin |
|-----------|-----|--------|
| Input | `#008000` | Excel 2011 Mac |
| Input | `#00FF00` | Google Sheets |
| Input | `#34A853` | Google Sheets "standard green" |
| Output | `#EE0000` | Excel standard red |
| Chart/Table | `#3366FF` | Excel 2011 Mac |
| Chart/Table | `#0000FF` | Google Sheets |
| Metadata | `#660066` | Excel 2011 Mac |
| Metadata | `#9900FF` | Google Sheets |
| Metadata | `#FF00FF` | Google Sheets (magenta) |

**Important:** The backend uses exact byte matching with no tolerance. Colors not in the tables above will be ignored, even if they look similar.

To read an app's structure programmatically, use `molnify-inspect-excel` rather than hand-rolling openpyxl color parsing. When writing cells with openpyxl, apply the colors above via `PatternFill(start_color='00B050', end_color='00B050', fill_type='solid')`; a cell comment becomes the input's `details` tooltip.

## Working with Formulas

openpyxl preserves Excel formulas. When you read a cell with a formula:
- `cell.value` returns the formula string (e.g., `=A1+B1`)
- To get the calculated value, use `data_only=True` when loading:

```python
# Load with formulas
wb_formulas = load_workbook('app.xlsx')
print(wb_formulas['Sheet1']['C1'].value)  # "=A1+B1"

# Load with calculated values (requires Excel to have saved values)
wb_values = load_workbook('app.xlsx', data_only=True)
print(wb_values['Sheet1']['C1'].value)  # 42
```

## Important: openpyxl Inline String Incompatibility

openpyxl writes string cells as **inline strings** (`t="inlineStr"` with `<is><t>` elements) instead of using the **shared string table** (`t="s"` with `xl/sharedStrings.xml`). Molnify's calculation engine does not correctly propagate changes through inline-string cells, which causes formulas to not recalculate when inputs change.

**If you use `AppBuilder`**, this is handled automatically - `AppBuilder.save()` converts inline strings to shared strings as a post-processing step.

**If you use raw openpyxl, you must call `_convert_inline_strings()` from `molnify_builder.py` after *every* `save()`.** This applies whether you build a new workbook with `Workbook()` **or edit an existing file with `load_workbook()`** - openpyxl rewrites string cells as inline strings on save regardless of how they were stored on disk, so re-saving an already-converted (shared-string) file re-introduces the problem.

```python
from openpyxl import load_workbook
from molnify_builder import _convert_inline_strings

wb = load_workbook('my-app.xlsx')
# ... edit cells, add a dropdown, etc. ...
wb.save('my-app.xlsx')
_convert_inline_strings('my-app.xlsx')  # Required after EVERY openpyxl save
```

This bites hardest with dropdowns: the option values written into the named range become inline strings, so the dropdown renders but the selected value never propagates through formulas.

openpyxl also writes empty `<v/>` elements on formula cells, which Molnify may interpret as "already evaluated to empty." The conversion function removes these as well.

## Tips

1. **Always backup** before modifying Excel files programmatically
2. **Preserve formatting** - openpyxl maintains most formatting, but test thoroughly
3. **Named ranges** - Molnify uses named ranges extensively; access via `wb.defined_names`
4. **Data validation** - Dropdown lists use Excel's data validation; access via `sheet.data_validations`

## Common Pitfall: Hardcoded Cell References

**For new apps**, use `AppBuilder` - it returns row numbers from `add_input()`/`add_output()` so formulas are always correct. See `creating-from-scratch.md`.

**For raw openpyxl** (modifying existing files), never hardcode cell references. Track actual positions:

```python
row = 1
# ... metadata ...
row += 2

initial_row = row
ws.cell(row=row, column=2, value=1000)
row += 1

final_row = row
ws.cell(row=row, column=2, value=1500)
row += 1

# Build formula from tracked positions - not from a mental model of where cells are
ws.cell(row=row + 1, column=2, value=f"=B{final_row}-B{initial_row}")
```
