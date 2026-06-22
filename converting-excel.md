# Converting a Plain Excel File into a Molnify App

Companion to the main reference.

If you have an existing Excel workbook with formulas and data but no Molnify color coding, follow this process to turn it into a working Molnify app. The key principle is **separation**: keep the original model untouched on its own sheet(s), and create new sheets for the Molnify interface and metadata.

## Step 1: Analyze the Spreadsheet

Before touching anything, understand the workbook. Run the **inspect script** to get a structured analysis:

```bash
molnify_inspect_excel.py <file.xlsx>
```

This outputs all cell values, formulas, colors, conditional formatting, charts, named ranges, data validations, and a formula dependency analysis that identifies potential inputs and outputs. Use its output to guide the steps below.

1. **Identify the purpose** - What does the spreadsheet calculate? What are users expected to change vs. just read?
2. **Trace formula dependencies** to classify cells (the inspect script does this automatically):
   - Cells that **no other cell depends on** (leaf values the user types into) → likely **Inputs**
   - Cells that **depend on other cells but nothing depends on them** (end results) → likely **Outputs**
   - Everything in between → **intermediate calculations** (stay uncolored in the model, invisible to the user)
3. **Note any charts or summary tables** in the original file - these will need to be recreated using Molnify's own charting. The inspect script lists all native Excel charts with their type, data ranges, and axis labels.
4. **Mark original model sheets with `molnifyIgnore`** - Place the text `molnifyIgnore` in cell A1 of each original model sheet. This tells Molnify to skip color interpretation on that sheet entirely, which prevents conditional formatting or any incidental cell colors from being misread as inputs/outputs/charts. If A1 already contains data, insert a new row at the top first so existing content shifts down (and update any formulas that reference cells on that sheet accordingly).
5. **Check formulas for compatibility** - Modern Excel (365/2021) saves newer functions with internal `_xlfn.` or `_xludf.` prefixes (e.g., `_xlfn.IFS`, `_xlfn.XLOOKUP`). openpyxl preserves these prefixes in formula strings, and Molnify's calculation engine cannot parse them. You must address these before uploading:
   - **Strip the prefix** for supported functions: `IFS`, `SWITCH`, `TEXTJOIN`, `CONCAT`, `MAXIFS`, `MINIFS`, `AVERAGEIFS`, `CEILING.MATH`, `FLOOR.MATH`, `IFNA`, `NUMBERVALUE`, `DAYS`. Simply remove the `_xlfn.` part (e.g., `_xlfn.IFS(...)` → `IFS(...)`).
   - **Rewrite** unsupported functions: `XLOOKUP` → `INDEX`/`MATCH`, `FILTER` → manual ranges or helper columns, `SORT`/`UNIQUE` → sorted data ranges, `LET`/`LAMBDA` → intermediate cells or restructured formulas.
   - The `molnify_validate.py` script detects `_xlfn.`/`_xludf.` prefixes and reports them as errors.

## Step 2: Create a Metadata Sheet

Create a new sheet (e.g. named `Metadata`) as the **first sheet** in the workbook. Add purple cells (`#7030A0`) for app configuration. At minimum:

```
     A                  B
1  [purple] ID         [purple] my-app-id
2  [purple] Name       [purple] My Converted App
3  [purple] ParseAllSheets  [purple] TRUE
```

Both cells in each row must be purple. `ParseAllSheets: TRUE` is required since you will have multiple sheets.

Other useful metadata to consider:
- `Description` - appears in the app header
- `EnabledForSave: TRUE` - lets users save scenarios
- `CSS` - custom styling

See the **Metadata Reference** section for all options. Only include metadata that differs from defaults.

## Step 3: Create an Interface Sheet

Create a separate sheet (e.g. named `App`) for all Molnify inputs, outputs, and charts. **Do not add colored cells to the original model sheet(s)** - keep the model untouched.

The interface sheet uses the standard 3-column layout:

| Column A (Title) | Column B (Value) | Column C (UI options) |
|-------------------|-------------------|-----------------------|
| Label (no color) | Value or formula (colored) | Options (no color) |

**Connect the interface to the model using formulas:**

- **Inputs (green):** Place the user-facing input on the interface sheet. Then, in the original model sheet, replace the old hardcoded value with a formula that references the green input cell: `=App!B4`
- **Outputs (red):** The red cell's formula simply references the model's result cell: `=Model!D25`

This way the original model's formulas and structure stay intact - the interface sheet is just a thin layer on top.

## Step 4: Apply Colors on the Interface Sheet

Color **only the value cells** (column B). Use the exact standard colors:

| Role | Color | Hex | Where to apply |
|------|--------|-----|----------------|
| Input | Green | `#00B050` | Value cells the user should edit |
| Output | Red | `#FF0000` | Value cells that show calculated results |
| Chart data | Blue | `#0070C0` | Only the numeric data cells (not headers/labels) |
| Metadata | Purple | `#7030A0` | Metadata sheet - both key and value cells |

**Do not color** title cells, UI cells, chart headers, or row labels. Custom shades of green/red/blue will not be recognized - use the exact standard colors from the default Excel palette.

## Step 5: Add UI Options

In column C of the interface sheet, add semicolon-separated options to improve the user experience:

```
     A                  B [COLOUR]                          C
4  Loan Amount         [GREEN]  100000                      slider;min=10000;max=2000000;delta=10000
5  Interest Rate       [GREEN]  0.05                        slider;min=0.01;max=0.15;delta=0.005
6  Term (years)        [GREEN]  20                          slider;min=1;max=40
7
8  Monthly Payment     [RED]    ="€"&TEXT(ROUND(Model!B10,2),"#,##0.00")
9  Total Paid          [RED]    ="€"&TEXT(ROUND(Model!B11,2),"#,##0.00")
```

See the **Inputs Reference** and **Outputs Reference** sections for all available UI options.

## Step 6: Convert Charts

Native Excel charts will **not** carry over. Molnify uses its own charting. Replace them:

1. Identify the data range the original chart used
2. Create a blue-cell chart structure on the interface sheet (see Charts and Tables section):
   - Title cell (no color) - chart name
   - Header row (no color) - series names
   - Label column (no color) - category labels
   - Data cells (blue, `#0070C0`) - formulas referencing the model's data
   - UI cell - chart type, e.g. `barChart;xAxis=Category;yAxis=Value`

## Step 7: Validate

Run the **validate script** to catch common issues:

```bash
molnify_validate.py <converted_file.xlsx>
```

### Understanding the output

The script reports two severity levels:

- **ERRORS** - Problems that will cause the app to malfunction. These must be fixed. Examples: missing ID metadata, missing ParseAllSheets, no metadata sheet.
- **WARNINGS** - Potential issues that may or may not be problems. Review each one, but not all require action. Examples: near-miss colors (may be intentional decorative fills), missing title cells (may be intentional for hidden inputs), unrecognized UI options (may be newly added features).

### Exit codes

| Exit code | Meaning |
|-----------|---------|
| `0` | No errors (warnings may still be present) |
| `1` | One or more errors found |

### Near-miss color warnings

The validator detects cell fills that are close to - but not exactly - a standard Molnify color. These appear as warnings like:

```
WARNING: Sheet1!B5: fill color #00B060 is close to a Molnify color but may not be recognized.
```

This usually means the cell was colored manually or in Google Sheets with a slightly different shade. The fix is to apply the exact standard color (e.g. `#00B050` for inputs).

### Iterative workflow

1. Run `molnify_validate.py <file.xlsx>`
2. Fix all **errors** first
3. Re-run to confirm errors are resolved
4. Review **warnings** - fix genuine issues, ignore false positives
5. Repeat until satisfied

Additionally:
1. **Check the wiring** - verify that inputs on the interface sheet flow into the model, and model results flow back to outputs
2. **Test with known values** - enter the same inputs as the original file and verify outputs match
3. **Remember:** formulas in green (input) cells only run once on load. If a value depends on user input, it must be a red output (or an uncolored intermediate cell in the model)

## Recommended Sheet Structure

```
Workbook:
├── Metadata     (sheet 1 - must be first)
│   └── Purple cells: ID, Name, ParseAllSheets, etc.
├── App          (sheet 2 - the Molnify interface)
│   └── Green inputs, red outputs, blue charts
│   └── Formulas reference Model sheet(s)
└── Model        (sheet 3+ - original spreadsheet, untouched)
    └── Cell A1: "molnifyIgnore" (prevents color misinterpretation)
    └── Original formulas and calculations
    └── Input cells replaced with =App!B4 style references
```

This separation keeps the original model maintainable and makes it easy to change the Molnify interface without breaking calculations.

## Common Conversion Pitfalls

| Problem | Cause | Fix |
|---------|-------|-----|
| Output always shows the initial value | Formula is in a green (input) cell | Move to a red (output) cell |
| Cell shows `#REF!` | Cross-sheet formula references are wrong | Check sheet name and cell address |
| Chart doesn't appear | Header/label cells are colored blue | Only color the data value cells blue |
| App ignores some cells | Custom color shade used | Use exact standard colors (`#00B050`, `#FF0000`, `#0070C0`) |
| Inputs appear in wrong order | Cell placement on interface sheet | Rearrange - Molnify reads left→right, top→bottom |
| Multi-sheet content missing | `ParseAllSheets` not set | Add metadata `ParseAllSheets: TRUE` |
| Intermediate values visible to user | Intermediate cell is colored | Leave intermediate cells uncolored on the model sheet |
| Random cells detected as outputs/inputs | Conditional formatting or incidental colors on model sheets | Add `molnifyIgnore` in cell A1 of each model sheet |
| Dropdown is empty in the app | The source file uses the x14 dataValidation extension (`<x14:dataValidation>`, common in recent Excel/Google Sheets), which Molnify ignores — it reads only standard data validation | Recreate the dropdown as a standard data validation (e.g. via openpyxl) referencing a named range of the list values |

## Minimal Conversion Example

**Original plain Excel** (`Model` sheet - a simple loan calculator):

```
     A              B
1  Loan Amount    100000
2  Rate           0.05
3  Years          20
4  Monthly Pmt    =B1*(B2/12)/(1-(1+B2/12)^(-B3*12))
5  Total Paid     =B4*B3*12
6  Total Interest =B5-B1
```

**After conversion - three sheets:**

`Metadata` sheet (sheet 1):
```
     A                       B
1  [purple] ID              [purple] loan-calculator
2  [purple] Name            [purple] Loan Calculator
3  [purple] ParseAllSheets  [purple] TRUE
```

`App` sheet (sheet 2):
```
     A                  B [COLOUR]                          C
1  Loan Amount         [GREEN]  100000                      slider;min=10000;max=2000000;delta=10000
2  Interest Rate       [GREEN]  0.05                        slider;min=0.01;max=0.15;delta=0.005
3  Term (years)        [GREEN]  20                          slider;min=1;max=40
4
5  Monthly Payment     [RED]    ="€"&TEXT(ROUND(Model!B5,2),"#,##0.00")
6  Total Paid          [RED]    ="€"&TEXT(ROUND(Model!B6,2),"#,##0.00")
7  Total Interest      [RED]    ="€"&TEXT(ROUND(Model!B7,2),"#,##0.00")
```

`Model` sheet (sheet 3 - original, with input cells rewired):
```
     A              B
1  molnifyIgnore
2  Loan Amount    =App!B1
3  Rate           =App!B2
4  Years          =App!B3
5  Monthly Pmt    =B2*(B3/12)/(1-(1+B3/12)^(-B4*12))
6  Total Paid     =B5*B4*12
7  Total Interest =B6-B2
```

Note how:
- `molnifyIgnore` in A1 prevents any colors on this sheet from being interpreted
- Adding `molnifyIgnore` in A1 shifted all content down one row, so formula cell references were updated accordingly (e.g., `=B1*(B2/12)...` became `=B2*(B3/12)...`). When inserting rows programmatically with openpyxl, formula references are **not** auto-adjusted - you must update them manually
- Input cells reference the App sheet; formulas reference the new local positions
- The App sheet is a clean interface layer that maps to/from the model
- Metadata is on its own sheet, kept as the first sheet
