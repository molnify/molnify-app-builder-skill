# Example: Sales Dashboard

A multi-chart dashboard with conditional display, CSS styling, and multiple chart types.

## Features
- Bar chart for revenue by region
- Line chart for monthly trend
- Pie chart for product mix
- Conditional chart display based on dropdown
- Custom CSS for dashboard layout

## Cell Layout

### Metadata sheet (sheet 1)

```
     A                          B
1  [purple] ID                [purple] sales-dashboard
2  [purple] Name              [purple] Sales Dashboard
3  [purple] ParseAllSheets    [purple] TRUE
4  [purple] AutoCalcEnabled   [purple] TRUE
5  [purple] TopBannerHidden   [purple] TRUE
6  [purple] CSS               [purple] .panel-heading{background:#2c3e50!important} .panel-title{color:#ecf0f1!important} #boxRow{padding:20px} .chart-container{min-height:400px}
```

### App sheet (sheet 2)

```
     A                    B                          C
1  View                 [GREEN] All                 dropdown;variable=viewMode
2  Year                 [GREEN] 2025                dropdown
3
4  Total Revenue        [RED] ="$"&TEXT(ROUND(Model!B2,0),"#,##0")   icon=fa-usd
5  Growth               [RED] =TEXT(Model!B3,"0.0")&"%"
6
7  Revenue by Region    EMEA         APAC         Americas       barChart;stacked;showValues
8  Q1                   [BLUE]=Model!C2  [BLUE]=Model!D2  [BLUE]=Model!E2
9  Q2                   [BLUE]=Model!C3  [BLUE]=Model!D3  [BLUE]=Model!E3
10 Q3                   [BLUE]=Model!C4  [BLUE]=Model!D4  [BLUE]=Model!E4
11 Q4                   [BLUE]=Model!C5  [BLUE]=Model!D5  [BLUE]=Model!E5
12
13 Monthly Trend        Revenue      Target       lineChart;yAxis=Revenue ($);showIfVariable=viewMode;showIfValue=All
14 Jan                  [BLUE]=Model!F2   [BLUE]=Model!G2
15 Feb                  [BLUE]=Model!F3   [BLUE]=Model!G3
16 Mar                  [BLUE]=Model!F4   [BLUE]=Model!G4
17 Apr                  [BLUE]=Model!F5   [BLUE]=Model!G5
18 May                  [BLUE]=Model!F6   [BLUE]=Model!G6
19 Jun                  [BLUE]=Model!F7   [BLUE]=Model!G7
20
21 Product Mix          Share        pieChart;showIfVariable=viewMode;showIfValue=All
22 Enterprise           [BLUE]=Model!H2
23 SMB                  [BLUE]=Model!H3
24 Consumer             [BLUE]=Model!H4
```

Data validation on B1: list = `All,Regional,Summary`
Data validation on B2: list = `2023,2024,2025`

### Model sheet (sheet 3)

```
     A              B
1  molnifyIgnore
2  Total Revenue  =SUM(C2:E5)
3  Growth         12.5
```

(Plus data columns C-H with regional, monthly, and product data)

## AppBuilder Code

```python
from molnify_builder import AppBuilder

app = AppBuilder("sales-dashboard", "Sales Dashboard")

# Styling metadata
app.add_metadata("AutoCalcEnabled", "TRUE")
app.add_metadata("TopBannerHidden", "TRUE")
app.add_metadata("CSS",
    ".panel-heading{background:#2c3e50!important} "
    ".panel-title{color:#ecf0f1!important} "
    "#boxRow{padding:20px} "
    ".chart-container{min-height:400px}")

# Inputs
app.add_input("View", "All", ui="dropdown;variable=viewMode")
app.add_input("Year", "2025", ui="dropdown")

# Summary outputs - units baked into the formula; prefix/postfix are input-only and do nothing here.
app.add_output("Total Revenue", '="$"&TEXT(ROUND(Model!B2,0),"#,##0")', ui="icon=fa-usd")
app.add_output("Growth", '=TEXT(Model!B3,"0.0")&"%"')

# Revenue by region chart
app.add_chart("Revenue by Region", "barChart",
              series={
                  "EMEA": ["=Model!C2", "=Model!C3", "=Model!C4", "=Model!C5"],
                  "APAC": ["=Model!D2", "=Model!D3", "=Model!D4", "=Model!D5"],
                  "Americas": ["=Model!E2", "=Model!E3", "=Model!E4", "=Model!E5"],
              },
              labels=["Q1", "Q2", "Q3", "Q4"],
              ui_extra="stacked;showValues")

# Monthly trend chart (conditional display)
app.add_chart("Monthly Trend", "lineChart",
              series={
                  "Revenue": ["=Model!F2", "=Model!F3", "=Model!F4",
                              "=Model!F5", "=Model!F6", "=Model!F7"],
                  "Target": ["=Model!G2", "=Model!G3", "=Model!G4",
                             "=Model!G5", "=Model!G6", "=Model!G7"],
              },
              labels=["Jan", "Feb", "Mar", "Apr", "May", "Jun"],
              ui_extra="yAxis=Revenue ($)")

# Product mix pie chart
app.add_chart("Product Mix", "pieChart",
              series={"Share": ["=Model!H2", "=Model!H3", "=Model!H4"]},
              labels=["Enterprise", "SMB", "Consumer"])

# Model sheet with sample data
app.add_model_sheet("Model")
app.set_cell("Model!A2", "Total Revenue")
app.set_cell("Model!B2", "=SUM(C2:E5)")
app.set_cell("Model!A3", "Growth")
app.set_cell("Model!B3", 12.5)

# Regional data (Q1-Q4 x 3 regions)
for i, vals in enumerate([(200, 150, 300), (220, 170, 320),
                           (210, 180, 310), (240, 200, 350)], start=2):
    app.set_cell(f"Model!C{i}", vals[0] * 1000)
    app.set_cell(f"Model!D{i}", vals[1] * 1000)
    app.set_cell(f"Model!E{i}", vals[2] * 1000)

# Monthly data
for i, (rev, target) in enumerate([(180, 200), (195, 200), (210, 210),
                                    (225, 210), (240, 220), (250, 220)], start=2):
    app.set_cell(f"Model!F{i}", rev * 1000)
    app.set_cell(f"Model!G{i}", target * 1000)

# Product mix
app.set_cell("Model!H2", 0.55)
app.set_cell("Model!H3", 0.30)
app.set_cell("Model!H4", 0.15)

app.save("sales-dashboard.xlsx")
```
