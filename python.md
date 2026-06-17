# Python Development Environment

Companion to the main reference in `CLAUDE.md`.

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

| Cell Type | Color Name | RGB Value | Hex |
|-----------|------------|-----------|-----|
| Input | Green | (0, 176, 80) | `#00B050` |
| Output | Red | (255, 0, 0) | `#FF0000` |
| Chart/Table | Blue | (0, 112, 192) | `#0070C0` |
| Action | Yellow | (255, 255, 0) | `#FFFF00` |
| Metadata | Purple | (112, 48, 160) | `#7030A0` |

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

## Python Examples

### Reading a Molnify App

```python
from openpyxl import load_workbook
from openpyxl.styles import PatternFill

# All colors accepted by the Molnify backend (exact matching, no tolerance).
# First entry per type is the recommended color for new apps.
ACCEPTED_COLORS = {
    'input':    ['00B050', '008000', '00FF00', '34A853'],
    'output':   ['FF0000', 'EE0000'],
    'chart':    ['0070C0', '3366FF', '0000FF'],
    'action':   ['FFFF00'],
    'metadata': ['7030A0', '660066', '9900FF', 'FF00FF'],
}

# Flat lookup: hex -> cell type
_COLOR_TO_TYPE = {h: ct for ct, hexes in ACCEPTED_COLORS.items() for h in hexes}

def get_cell_type(cell):
    """Determine cell type from fill color (exact match)."""
    fill = cell.fill
    if fill.fill_type != 'solid':
        return None

    color = fill.fgColor
    if color and color.type == 'rgb' and color.rgb:
        rgb_hex = color.rgb[-6:].upper()
        return _COLOR_TO_TYPE.get(rgb_hex)
    return None

def analyze_molnify_app(filepath):
    """Analyze a Molnify Excel app and extract components."""
    wb = load_workbook(filepath)

    app = {
        'inputs': [],
        'outputs': [],
        'actions': [],
        'metadata': []
    }

    for sheet in wb.worksheets:
        for row in sheet.iter_rows():
            for cell in row:
                cell_type = get_cell_type(cell)
                if cell_type:
                    app[cell_type + 's' if cell_type != 'metadata' else 'metadata'].append({
                        'cell': f"{sheet.title}!{cell.coordinate}",
                        'value': cell.value,
                        'comment': cell.comment.text if cell.comment else None
                    })

    return app

# Usage
app = analyze_molnify_app('my_app.xlsx')
print(f"Found {len(app['inputs'])} inputs")
print(f"Found {len(app['outputs'])} outputs")
print(f"Found {len(app['actions'])} action cells")
print(f"Found {len(app['metadata'])} metadata cells")
```

### Creating a New Input Cell

```python
from openpyxl import load_workbook
from openpyxl.styles import PatternFill
from openpyxl.comments import Comment

def add_input(wb, sheet_name, cell_ref, name, default_value, ui_options=None, tooltip=None):
    """Add a new input cell to a Molnify app."""
    sheet = wb[sheet_name]
    cell = sheet[cell_ref]

    # Set the input color (green)
    green_fill = PatternFill(start_color='00B050', end_color='00B050', fill_type='solid')
    cell.fill = green_fill

    # Set the value
    cell.value = default_value

    # Add tooltip as comment (this becomes the 'details' field)
    if tooltip:
        cell.comment = Comment(tooltip, 'Molnify')

    # The name cell is typically to the left
    name_cell = sheet.cell(row=cell.row, column=cell.column - 1)
    name_cell.value = name

    # UI options go in a specific location or can be stored in cell metadata
    # This depends on your app structure

    return cell

# Usage
wb = load_workbook('my_app.xlsx')
add_input(wb, 'Input', 'C5', 'User Age', 25, tooltip='Enter your age in years')
wb.save('my_app.xlsx')
```

### Modifying Metadata

```python
from openpyxl import load_workbook

def set_metadata(wb, key, value, metadata_sheet='Metadata'):
    """Set a metadata value in a Molnify app."""
    sheet = wb[metadata_sheet]

    # Find the metadata key
    for row in sheet.iter_rows():
        for cell in row:
            if cell.value == key:
                # Value is typically in the next column
                value_cell = sheet.cell(row=cell.row, column=cell.column + 1)
                value_cell.value = value
                return True

    return False

# Usage
wb = load_workbook('my_app.xlsx')
set_metadata(wb, 'Name', 'My Updated App')
set_metadata(wb, 'EnabledForSave', 'TRUE')
wb.save('my_app.xlsx')
```

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

**If you use raw openpyxl**, you must call `_convert_inline_strings()` from `molnify_builder.py` after saving:

```python
from openpyxl import Workbook
from molnify_builder import _convert_inline_strings

wb = Workbook()
# ... build your workbook ...
wb.save('my-app.xlsx')
_convert_inline_strings('my-app.xlsx')  # Required for Molnify compatibility
```

openpyxl also writes empty `<v/>` elements on formula cells, which Molnify may interpret as "already evaluated to empty." The conversion function removes these as well.

## Tips

1. **Always backup** before modifying Excel files programmatically
2. **Preserve formatting** - openpyxl maintains most formatting, but test thoroughly
3. **Named ranges** - Molnify uses named ranges extensively; access via `wb.defined_names`
4. **Data validation** - Dropdown lists use Excel's data validation; access via `sheet.data_validations`

## Common Pitfall: Hardcoded Cell References

**For new apps**, use `AppBuilder` — it returns row numbers from `add_input()`/`add_output()` so formulas are always correct. See `creating-from-scratch.md`.

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

# Build formula from tracked positions — not from a mental model of where cells are
ws.cell(row=row + 1, column=2, value=f"=B{final_row}-B{initial_row}")
```
