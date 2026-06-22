# Example: Expense Tracker

A database-backed app where users submit expenses that are stored in a table, with autofill to display recent entries and a download action.

## Features
- Input form with expense details
- `addrecord` action to save to database
- `DataTable.0` metadata for schema provisioning
- Autofill to populate a table of recent expenses
- `downloadquery` action to export data

## Cell Layout

### Metadata sheet (sheet 1)

```
     A                          B
1  [purple] ID                [purple] expense-tracker
2  [purple] Name              [purple] Expense Tracker
3  [purple] ParseAllSheets    [purple] TRUE
4  [purple] EnabledForSave    [purple] TRUE
5  [purple] Users             [purple] *@company.com
6  [purple] RecordTableName   [purple] data_expense-tracker_0
7  [purple] DataTable.0       [purple] {"columns":{"category":{"type":"VARCHAR","default":"Food"},"amount":{"type":"DECIMAL","default":"0"},"description":"VARCHAR","expense_date":"VARCHAR","submitted_by":"VARCHAR"}}
8  [purple] autofill.recent_expenses  [purple] SELECT category, amount, expense_date FROM `data_expense-tracker_0` ORDER BY _molnify_timestamp DESC LIMIT 10
9  [purple] JavaScriptAfterLoad  [purple] calculateButton();
```

**Notes:**
- `RecordTableName` must be the full table name including `data_` prefix - it is NOT auto-prefixed.
- `DataTable.0` creates a table named `data_<appId>_0`, so `data_expense-tracker_0`.
- The autofill key is `autofill.recent_expenses` where `recent_expenses` is a named range defined in the Autofill sheet.
- `JavaScriptAfterLoad: calculateButton();` runs a calculation on page load so the autofill table populates immediately - autofill only runs during a calculation, and auto-calc does not fire on initial load on its own.
- The autofill SQL uses backtick-quoted table name (`` `data_expense-tracker_0` ``) because hyphens in SQL are interpreted as subtraction without quoting.
- `expense_date` uses `VARCHAR(20)` rather than `DATE` because date inputs are stored as formatted text strings.
- `category` and `amount` have `default` values matching their input defaults. Molnify only sends inputs the user has modified ("dirty") - if a user submits without changing an input, that column is omitted from the INSERT. Without a DB default, the column would be NULL.

### App sheet (sheet 2)

```
     A                    B                          C
1  Category             [GREEN] Food                dropdown
2  Amount               [GREEN] 0                   min=0;decimals=2;prefix=$
3  Description          [GREEN]                     textarea;placeholder=What was this expense for?
4  Expense Date         [GREEN]                     date
5  Submitted By         [GREEN]                     user.email;hidden
6
7  Recent Expenses      Expenses                    table
8  Category             [BLUE] =Autofill!A2
9  Amount               [BLUE] =Autofill!B2
10 Date                 [BLUE] =Autofill!C2
```

Data validation on B1: list = `Food,Travel,Office,Software,Other`

### Autofill sheet (sheet 3)

```
     A              B              C
1  molnifyIgnore
```

Define a named range `recent_expenses` spanning `Autofill!A2:C11` (10 rows x 3 columns).

### Actions

```
     A                    B
11 [yellow] type         [yellow] addrecord
12 [yellow] title        [yellow] Submit Expense
13 [yellow] successText  [yellow] Expense recorded!
14 [yellow] successCalculate [yellow] TRUE
15
16 [yellow] type         [yellow] downloadquery
17 [yellow] title        [yellow] Download All
18 [yellow] query        [yellow] SELECT * FROM `data_expense-tracker_0` ORDER BY _molnify_timestamp DESC
19 [yellow] format       [yellow] csv
```

## AppBuilder Code

```python
from molnify_builder import AppBuilder

app = AppBuilder("expense-tracker", "Expense Tracker")

# Metadata
app.add_metadata("EnabledForSave", "TRUE")
app.add_metadata("Users", "*@company.com")
app.add_metadata("RecordTableName", "data_expense-tracker_0")
app.add_metadata("DataTable.0",
    '{"columns":{'
    '"category":{"type":"VARCHAR","default":"Food"},'
    '"amount":{"type":"DECIMAL","default":"0"},'
    '"description":"VARCHAR",'
    '"expense_date":"VARCHAR",'
    '"submitted_by":"VARCHAR"}}')
app.add_metadata("autofill.recent_expenses",
    "SELECT category, amount, expense_date "
    "FROM `data_expense-tracker_0` ORDER BY _molnify_timestamp DESC LIMIT 10")
app.add_metadata("JavaScriptAfterLoad", "calculateButton();")

# Inputs
app.add_input("Category", "Food", ui="dropdown")
app.add_input("Amount", 0, ui="min=0;decimals=2;prefix=$")
app.add_input("Description", "", ui="textarea;placeholder=What was this expense for?")
app.add_input("Expense Date", "", ui="date")
app.add_input("Submitted By", "", ui="user.email;hidden")

# Chart (table showing recent expenses via autofill)
app.add_chart("Recent Expenses", "table",
              series={
                  "Category": [f"=Autofill!A{r}" for r in range(2, 12)],
                  "Amount": [f"=Autofill!B{r}" for r in range(2, 12)],
                  "Date": [f"=Autofill!C{r}" for r in range(2, 12)],
              },
              labels=[str(i) for i in range(1, 11)])

# Actions
app.add_action({
    "type": "addrecord",
    "title": "Submit Expense",
    "successText": "Expense recorded!",
    "successCalculate": "TRUE",
})
app.add_action({
    "type": "downloadquery",
    "title": "Download All",
    "query": "SELECT * FROM `data_expense-tracker_0` ORDER BY _molnify_timestamp DESC",
    "format": "csv",
})

# Autofill data sheet + named range "recent_expenses" on Autofill!A2:C11
app.add_model_sheet("Autofill")
app.add_named_range("recent_expenses", "Autofill", "A2:C11")

app.save("expense-tracker.xlsx")
```
