# Example: Financial Model (Multi-Sheet)

A multi-sheet app that separates the user interface from the calculation model. Demonstrates the recommended separation pattern for complex spreadsheets.

## Features
- App sheet with inputs and outputs (user-facing)
- Model sheet with all formulas (hidden from user via molnifyIgnore)
- Metadata sheet for configuration
- Shows how inputs flow into the model and outputs flow back

## Architecture

```
Workbook:
├── Metadata     (sheet 1) - purple cells, app config
├── App          (sheet 2) - green inputs, red outputs (user sees this)
└── Model        (sheet 3) - molnifyIgnore, all calculations (hidden)
```

The App sheet is a thin interface layer. Inputs live on App, and the Model sheet reads them via `=App!B2`. Outputs on the App sheet read back from the Model via `=Model!B10`.

## Cell Layout

### Metadata sheet (sheet 1)

```
     A                          B
1  [purple] ID                [purple] financial-model
2  [purple] Name              [purple] Investment Analysis
3  [purple] ParseAllSheets    [purple] TRUE
4  [purple] EnabledForReset   [purple] TRUE
```

### App sheet (sheet 2)

```
     A                       B                               C
1  Initial Investment       [GREEN] 100000                   min=0;decimals=0;prefix=$
2  Annual Return (%)        [GREEN] 8                        slider;min=1;max=30;delta=0.5
3  Years                    [GREEN] 10                       slider;min=1;max=50
4  Annual Contribution      [GREEN] 5000                     min=0;decimals=0;prefix=$
5  Inflation Rate (%)       [GREEN] 2.5                      slider;min=0;max=10;delta=0.5
6
7  Final Value              [RED] =Model!B8                  decimals=0;prefix=$;icon=fa-coins
8  Total Contributions      [RED] =Model!B9                  decimals=0;prefix=$
9  Total Growth             [RED] =Model!B10                 decimals=0;prefix=$
10 Real Return (inflation-adjusted) [RED] =Model!B11         decimals=0;prefix=$
11
12 Growth Over Time         Nominal Value   Real Value       lineChart;yAxis=Value ($);xAxis=Year
13 Year 1                   [BLUE]=Model!C2   [BLUE]=Model!D2
14 Year 2                   [BLUE]=Model!C3   [BLUE]=Model!D3
15 Year 3                   [BLUE]=Model!C4   [BLUE]=Model!D4
16 Year 4                   [BLUE]=Model!C5   [BLUE]=Model!D5
17 Year 5                   [BLUE]=Model!C6   [BLUE]=Model!D6
18 Year 6                   [BLUE]=Model!C7   [BLUE]=Model!D7
19 Year 7                   [BLUE]=Model!C8   [BLUE]=Model!D8
20 Year 8                   [BLUE]=Model!C9   [BLUE]=Model!D9
21 Year 9                   [BLUE]=Model!C10  [BLUE]=Model!D10
22 Year 10                  [BLUE]=Model!C11  [BLUE]=Model!D11
```

### Model sheet (sheet 3)

```
     A                        B                                           C                D
1  molnifyIgnore
2  Rate (monthly)            =App!B2/100
3  Inflation (annual)        =App!B5/100
4  Years                     =App!B3
5  Annual Contribution       =App!B4
6  Initial                   =App!B1
7
8  Final Value               =C11 (last year's nominal value)
9  Total Contributions       =B6+B5*B4
10 Total Growth              =B8-B9
11 Real Return               =D11 (last year's real value)
12
    (Year projection columns)
     C = Nominal value:  C2 = =B6*(1+B2)+B5,  C3 = =C2*(1+B2)+B5,  etc.
     D = Real value:     D2 = =C2/(1+B3)^1,   D3 = =C3/(1+B3)^2,   etc.
```

## AppBuilder Code

```python
from molnify_builder import AppBuilder

app = AppBuilder("financial-model", "Investment Analysis")

app.add_metadata("EnabledForReset", "TRUE")

# Inputs
app.add_input("Initial Investment", 100000, ui="min=0;decimals=0;prefix=$")
app.add_input("Annual Return (%)", 8, ui="slider;min=1;max=30;delta=0.5")
app.add_input("Years", 10, ui="slider;min=1;max=50")
app.add_input("Annual Contribution", 5000, ui="min=0;decimals=0;prefix=$")
app.add_input("Inflation Rate (%)", 2.5, ui="slider;min=0;max=10;delta=0.5")

# Outputs
app.add_output("Final Value", "=Model!B8", ui="decimals=0;prefix=$;icon=fa-coins")
app.add_output("Total Contributions", "=Model!B9", ui="decimals=0;prefix=$")
app.add_output("Total Growth", "=Model!B10", ui="decimals=0;prefix=$")
app.add_output("Real Return (inflation-adjusted)", "=Model!B11", ui="decimals=0;prefix=$")

# Chart
years = 10
app.add_chart("Growth Over Time", "lineChart",
              series={
                  "Nominal Value": [f"=Model!C{i}" for i in range(2, 2 + years)],
                  "Real Value": [f"=Model!D{i}" for i in range(2, 2 + years)],
              },
              labels=[f"Year {i}" for i in range(1, years + 1)],
              ui_extra="yAxis=Value ($);xAxis=Year")

# Model sheet
app.add_model_sheet("Model")

# Parameters (read from App inputs)
app.set_cell("Model!A2", "Annual Rate")
app.set_cell("Model!B2", "=App!B2/100")
app.set_cell("Model!A3", "Inflation Rate")
app.set_cell("Model!B3", "=App!B5/100")
app.set_cell("Model!A4", "Years")
app.set_cell("Model!B4", "=App!B3")
app.set_cell("Model!A5", "Annual Contribution")
app.set_cell("Model!B5", "=App!B4")
app.set_cell("Model!A6", "Initial Investment")
app.set_cell("Model!B6", "=App!B1")

# Year projections (columns C = nominal, D = real)
for yr in range(1, years + 1):
    row = yr + 1
    if yr == 1:
        app.set_cell(f"Model!C{row}", "=B6*(1+B2)+B5")
    else:
        app.set_cell(f"Model!C{row}", f"=C{row - 1}*(1+B2)+B5")
    app.set_cell(f"Model!D{row}", f"=C{row}/(1+B3)^{yr}")

# Summary outputs
app.set_cell("Model!A8", "Final Value")
app.set_cell("Model!B8", f"=C{years + 1}")
app.set_cell("Model!A9", "Total Contributions")
app.set_cell("Model!B9", "=B6+B5*B4")
app.set_cell("Model!A10", "Total Growth")
app.set_cell("Model!B10", "=B8-B9")
app.set_cell("Model!A11", "Real Return")
app.set_cell("Model!B11", f"=D{years + 1}")

app.save("financial-model.xlsx")
```
