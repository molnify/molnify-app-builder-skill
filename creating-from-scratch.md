# Creating a Molnify App from Scratch

Companion to the main reference in `CLAUDE.md`.

This guide walks through building a new Molnify app without an existing Excel file. For converting an existing spreadsheet, see `converting-excel.md`.

## Step 1: Define Your App

Before writing code, clarify:
- **Inputs** - What does the user provide? (numbers, text, dates, selections)
- **Outputs** - What results should the app display?
- **Actions** - Should the app send emails, save data, call APIs?
- **Charts** - Does the app need visualizations?

## Step 2: Choose Your Approach

### AppBuilder (Recommended)

The `molnify_builder.py` module handles cell colors, layout, and metadata automatically. Use this when building apps programmatically.

#### Cell Layout and Row Tracking

AppBuilder places all items on the **App** sheet in column **B**, starting at **row 1**. Every `add_input()` and `add_output()` call returns the row number where the cell is placed. **Use these return values to build formulas instead of manually counting rows:**

```
Row 1:  Input 1    → App!B1
Row 2:  Input 2    → App!B2
...
Row N:  Input N    → App!BN
Row N+1: (blank separator)
Row N+2: Output 1  → App!B(N+2)
Row N+3: Output 2  → App!B(N+3)
...
```

**The blank separator row is only added if there are both inputs and outputs.** Charts and actions follow after additional separator rows.

```python
from molnify_builder import AppBuilder

app = AppBuilder("bmi-calculator", "BMI Calculator")

# add_input returns the row number — use it in formulas
row_weight = app.add_input("Weight (kg)", 70, ui="slider;min=30;max=200")
row_height = app.add_input("Height (cm)", 170, ui="slider;min=100;max=220")

# Use returned rows — no manual counting needed
row_bmi = app.add_output("BMI", f"=App!B{row_weight}/(App!B{row_height}/100)^2", ui="decimals=1")
app.add_output("Category", f'=IF(App!B{row_bmi}<18.5,"Underweight",IF(App!B{row_bmi}<25,"Normal",IF(App!B{row_bmi}<30,"Overweight","Obese")))')

# Metadata
app.add_metadata("EnabledForReset", "TRUE")

app.save("bmi-calculator.xlsx")
```

#### Dropdown Inputs

Pass an `options` list to `add_input()` to create a dropdown with data validation automatically:

```python
app.add_input("Status", "Active", options=["Active", "Inactive", "Pending"])
app.add_input("Priority", "Medium", options=["Low", "Medium", "High", "Critical"])
```

This creates a hidden `_Options` sheet with named ranges and data validation — no manual openpyxl post-processing needed. The `dropdown` UI type is added automatically.

#### Interleaving Outputs Among Inputs

Use `among_inputs=True` to place an HTML output between inputs in the input panel, at the current position in the item sequence:

```python
app.add_input("Name", "", ui="variable=name;tab=Step 1")
app.add_input("Email", "", ui="variable=email")

# This output appears in the input panel between email and department
app.add_output("Preview", '="<p>Hello, "&App!B1&"</p>"',
               ui="html;hideCopy", among_inputs=True)

app.add_input("Department", "", ui="tab=Step 2;dropdown",
              options=["Engineering", "Sales", "Marketing"])
```

Without `among_inputs=True`, outputs are placed after all inputs (in the right column by default).

### Raw openpyxl

Use raw openpyxl when you need fine-grained control over cell placement, formulas, or non-standard layouts. See `python.md` for color conventions and examples.

## Step 3: Full AppBuilder Example

This builds a complete app with inputs, outputs, a chart, and an email action:

```python
from molnify_builder import AppBuilder

app = AppBuilder("sales-forecast", "Sales Forecast Tool")

# Inputs — use returned rows in output formulas
row_rev = app.add_input("Base Revenue", 100000, ui="min=0;decimals=0;prefix=$")
row_growth = app.add_input("Growth Rate (%)", 10, ui="slider;min=-50;max=100;delta=5")
row_years = app.add_input("Years", 5, ui="slider;min=1;max=20")
row_email = app.add_input("Recipient Email", "", ui="placeholder=email@company.com")

# Outputs — reference inputs by row variable
R, G, Y = f"App!B{row_rev}", f"App!B{row_growth}", f"App!B{row_years}"
app.add_output("Year 1 Revenue", f"={R}*(1+{G}/100)", ui="decimals=0;prefix=$")
app.add_output("Final Year Revenue", f"={R}*(1+{G}/100)^{Y}", ui="decimals=0;prefix=$")
app.add_output("Total Revenue", f"=IF({G}=0,{R}*{Y},{R}*((1+{G}/100)^{Y}-1)/({G}/100))", ui="decimals=0;prefix=$")

# Chart
app.add_chart("Revenue Projection", "lineChart",
              series={"Projected Revenue": [f"={R}*(1+{G}/100)^{i}" for i in range(1, 6)]},
              labels=["Year 1", "Year 2", "Year 3", "Year 4", "Year 5"],
              ui_extra="yAxis=Revenue ($);xAxis=Year")

# Email action
app.add_action({
    "type": "email",
    "title": "Email Report",
    "to": f"=App!B{row_email}",
    "subject": "Sales Forecast Results",
    "contentHTML": f'="<h2>Sales Forecast</h2><p>Base: "&{R}&", Growth: "&{G}&"%</p>"',
    "successText": "Report sent!",
})

app.save("sales-forecast.xlsx")
```

## Step 4: Model Sheets

Use model sheets when your app needs intermediate calculations that should not be visible to the user. Use `set_cell()` to populate them - it accepts `"SheetName!CellRef"` addresses:

```python
from molnify_builder import AppBuilder

app = AppBuilder("loan-calc", "Loan Calculator")

# Inputs - B1, B2, B3
app.add_input("Loan Amount", 100000, ui="slider;min=10000;max=2000000;delta=10000")
app.add_input("Interest Rate", 0.05, ui="slider;min=0.01;max=0.15;delta=0.005")
app.add_input("Term (years)", 20, ui="slider;min=1;max=40")

# Outputs - B5, B6, B7 (blank row 4); reference the model sheet
app.add_output("Monthly Payment", "=Model!B3", ui="decimals=2;prefix=$")
app.add_output("Total Paid", "=Model!B4", ui="decimals=2;prefix=$")
app.add_output("Total Interest", "=Model!B5", ui="decimals=2;prefix=$")

# Model sheet for intermediate calculations
# App inputs: Loan Amount=App!B1, Interest Rate=App!B2, Term=App!B3
app.add_model_sheet("Model")
app.set_cell("Model!A2", "Monthly Rate")
app.set_cell("Model!B2", "=App!B2/12")
app.set_cell("Model!A3", "Monthly Payment")
app.set_cell("Model!B3", "=App!B1*(B2)/(1-(1+B2)^(-App!B3*12))")
app.set_cell("Model!A4", "Total Paid")
app.set_cell("Model!B4", "=B3*App!B3*12")
app.set_cell("Model!A5", "Total Interest")
app.set_cell("Model!B5", "=B4-App!B1")

app.save("loan-calc.xlsx")
```

Key points:
- `add_model_sheet()` creates a sheet with `molnifyIgnore` in A1
- `set_cell()` writes to any sheet by address (e.g. `"Model!B2"`)
- `add_named_range(name, sheet, range)` defines a named range for autofill or report templates
- AppBuilder auto-adds `ParseAllSheets: TRUE` (always needed since Metadata and App are separate sheets)
- Keep all visible UI on the App sheet; keep calculations on model sheets

## Step 5: Validate

Always validate before uploading:

```bash
validate.py my-app.xlsx
```

This checks for missing metadata, incorrect colors, layout issues, unsupported functions, and more. Fix all **errors** (the app won't work correctly with errors). **Warnings** are advisory - review but not always actionable.

## Step 6: Style the App

The default layout is a basic 50/50 two-column Bootstrap panel. You should customize it for a professional look.

- **Colors and fonts** - Use metadata properties: `TopBannerColor`, `PanelHeaderColor`, `ButtonColor`, `HeaderFont`, `BodyFont`, etc.
- **CSS** - Add a `CSS` metadata entry for full control over layout, spacing, and component styling.
- **JavaScript layout changes** - Use `JavaScriptAfterLoad` for DOM manipulation (reordering panels, moving elements).

See **`styling.md`** for detailed recipes including modern dashboard layouts, compact input bars, kiosk mode, and responsive designs.

## Step 7: Upload

Upload your app at:

```
https://app.molnify.com/#ajax/createApp
```

Requirements:
- You must be logged in
- Select your `.xlsx` file and upload
- The app ID (from metadata) determines the URL: `app.molnify.com/app/<id>`
- Uploading with the same ID **replaces** the existing app
- There is no API for uploading - it must be done through the web interface
