---
name: molnify-app-builder
description: "Build, convert, validate, and style Molnify apps: spreadsheet-driven web applications where Excel or Google Sheets formulas drive the logic and colored cells define inputs, outputs, charts, and actions. Use when creating a Molnify app from scratch, converting an existing spreadsheet into one, validating or styling an app, or answering questions about how Molnify apps work."
license: Apache-2.0
metadata:
  version: 1.0.14
---

# Molnify App Development Guide

This is the primary reference for building Molnify applications.

## Overview

Molnify apps are **spreadsheet-driven calculation applications**. You design your app in Excel or Google Sheets, where:
- **Green cells** = Inputs (user-provided parameters)
- **Red cells** = Outputs (calculated results)
- **Blue cells** = Charts and Tables (aggregated data visualizations)
- **Yellow cells** = Actions (automated operations like email, HTTP calls)
- **Purple cells** = Metadata (app settings and configuration)

The spreadsheet formulas perform all calculations. Molnify renders the UI and handles user interaction.

Molnify reads the Excel file **left to right, top to bottom**. The order cells appear determines the order in the app UI.

### Cell Structure

**Inputs, Outputs, Charts** require **three consecutive cells**:
1. **Title cell** - The label shown to users
2. **Value cell** (colored) - The actual value/formula
3. **UI cell** - Configuration options (can be empty)

**Metadata** requires **two consecutive cells, both colored purple**:
1. **Key cell** (purple) - The metadata property name (e.g., "Name", "ID")
2. **Value cell** (purple) - The metadata value

**Actions** require **pairs of cells per property, value cell colored yellow**:
1. **Key cell** (no color) - The property name (e.g., "type", "to", "subject")
2. **Value cell** (yellow) - The property value

Each action is a contiguous block of these pairs, separated from other actions by a blank row.

### Quick Start

Most common patterns at a glance:

| Task | How |
|------|-----|
| Create a new app from scratch | Use `AppBuilder` - see `creating-from-scratch.md` |
| Convert an existing Excel file | Follow `converting-excel.md` step-by-step |
| Add an input | Green cell (`#00B050`), title left, UI options right |
| Add an output | Red cell (`#FF0000`), formula referencing model or inputs |
| Add a chart | Blue data cells (`#0070C0`), headers/labels uncolored |
| Add an action | Yellow cell pairs (`#FFFF00`), key left, value right |
| Add metadata | Purple cell pairs (`#7030A0`), first sheet only |
| Style the app | CSS metadata + `styling.md` recipes |

**Workflow:** Define → Build (AppBuilder or openpyxl) → Validate → Deploy

### Best Practices

1. **Always set the `ID` metadata** - This gives your app a stable URL and ensures you keep access to database tables when updating the app. Without an ID, Molnify auto-generates one, and updating creates a copy instead of replacing.

2. **Only include metadata that differs from defaults** - Do not add metadata cells for values that match the default. This keeps your spreadsheet clean and easier to maintain. For example, don't include `AutoCalcEnabled: TRUE` since TRUE is already the default.

3. **Metadata must be on the first sheet** - All purple metadata cells must be placed on the first sheet of your workbook. Metadata on other sheets will be ignored.

4. **Set `ParseAllSheets: TRUE` for multi-sheet apps** - By default, Molnify only parses the first sheet. If your app has inputs, outputs, actions, charts or metadata on multiple sheets, you must set the metadata `ParseAllSheets` to `TRUE`. AppBuilder always adds this automatically.

5. **Use `molnifyIgnore` to exclude sheets from color interpretation** - Place the text `molnifyIgnore` in cell A1 of any sheet that should not be scanned for Molnify components. If A1 already contains data, insert a new row at the top first. This is essential for sheets containing raw data models, lookup tables, or any content with conditional formatting or incidental cell colors that could be misinterpreted as inputs/outputs.

6. **Ensure text is readable on its background** - When customizing colors (buttons, panels, headers), always verify sufficient contrast between text and background. Light text on light backgrounds or dark text on dark backgrounds makes the app unusable.

7. **Display numbers at a sensible scale and precision** - Raw formula results are rarely display-ready: they carry excessive decimals (`33.333333333`) *and* often an awkward magnitude. Two separate decisions:
   - **Precision:** Round to what the reader can act on. ~3-4 significant figures is plenty for most displays. Use Excel's `ROUND()` in the formula, or the `decimals=N` UI option (and `axisDecimals=N` for chart axes - long axis tick labels are a common readability killer).
   - **Magnitude:** If values run in the thousands or millions, scale the unit instead of printing every digit. `124 500 SEK` reads better as `124.5 tSEK`, and `8 300 000 SEK` as `8.3 MSEK`. Divide by 1000/1e6 in the formula (or use the `multiplier` UI option) and state the scaled unit in the title - e.g. title "Revenue (tSEK)" rather than a 7-digit axis. Keep the chosen unit consistent across related outputs and a chart's whole axis.
   - **Rule of thumb:** before finalizing, ask "at this scale, is this number easy to read at a glance?" An axis labelled `0, 25000, 50000, 75000` should usually be `0, 25, 50, 75` with a "tSEK" axis title. This applies to scalar outputs, table cells, and chart axes alike.

8. **Verify formulas after adding or removing cells** - When inserting or deleting rows/columns, Excel formulas may shift or break. Always verify that all formulas still reference the correct cells after structural changes. This is especially critical when working programmatically (e.g., with openpyxl) where automatic reference adjustment doesn't occur.

9. **Keep strings in formulas under 256 characters** - Excel automatically inserts `_LONGTEXT` references when strings exceed 256 characters, but Molnify does not support `_LONGTEXT`. Split long strings using `&` or `CONCATENATE()`:
   ```
   ❌ ="This is a very long string that exceeds 256 characters..."
   ✓ ="This is a very long string that"&" has been split into chunks"&" each under 256 characters"
   ```

10. **Keep calculations in the spreadsheet, not in JavaScript** - Molnify's strength is that business logic lives in Excel formulas. Avoid offloading calculations, conditional logic, or data transformations to JavaScript. JS should be reserved for UI manipulation (DOM changes, styling, event handling), not for computing values that formulas can handle. This keeps the app auditable, testable, and maintainable.

11. **COUNTA counts empty strings from autofill** - When autofill populates a named range, cells that receive no data are cleared but hold the value `""` (empty string). `COUNTA` counts these as non-empty. Use `COUNTIF(range,"<>")` or `SUMPRODUCT((range<>"")*1)` instead to count only cells with actual data.

12. **Design with intent, not with effects** - Every app should look like it was designed for its purpose, not generated from a template. Pick a color palette that fits the domain. Choose fonts with character. Avoid generic AI-generated aesthetics: purple gradients on white, uniform rounded corners and card shadows on every element, pulsing animations, gradient text, emoji placeholders, and staggered fade-up animations. Left-aligned content is easier to scan than centered. Vary visual weight instead of making everything look the same. If it looks like every other AI-generated dashboard, it needs a point of view.

13. **Validate the *assembled* string when building formulas in code** - Concatenating formula text in Python (especially adjacent f-strings) easily produces a stray `""` that Excel reads as an *escaped quote*, swallowing every following `&` operator and string into one literal. A corrupted formula doesn't just fail its own cell: on load Excel runs "file level validation and repair" and **strips the entire formula table for that sheet** rather than dropping the one bad formula - so the app can render with every formula gone. Adjacent pieces like `f'="<div>…"'` + `f'"&"<h2>…"'` concatenate to `="<div>…""&"<h2>…"`, where the `""` is misread. After building a formula programmatically, `print`/`assert` the final string and confirm the double-quotes are balanced and every `"&"` is a real operator, not buried inside a literal. `molnify_validate.py` flags formulas with an odd number of double-quotes, which catches the common form of this bug.

### CSS & DOM Quick Reference

The rendered DOM does NOT match the spreadsheet - inputs are wrapped in third-party widgets and the selectors differ. `styling.md` has the full DOM tree, selector reference, default color scheme, chart-series colors, the Select2 / Font Awesome / custom-header gotchas, CSS Grid layouts, and dashboard recipes.

### Companion Guides

Alongside this reference, companion guides cover specific needs: `creating-from-scratch.md`, `converting-excel.md`, `styling.md`, `styling-examples.md`, `design.md`, `patterns.md`, `database.md`, `report-templates.md`, `custom-frontend.md`, `advanced-topics.md`, `python.md`, and `examples/`. See `local-instructions.md` for an index of what each covers and when to reach for it, plus local setup and deployment.

### Choosing Your UI Approach

| What you want | Approach | Guide |
|---------------|----------|-------|
| Colors, fonts, spacing | CSS metadata + the CSS & DOM quick ref above | `design.md` |
| Rearranged layout, dashboard, CSS Grid | CSS + `JavaScriptAfterLoad` | `styling.md` |
| Wizard, master-detail, conditional sections | Standard Molnify features | `patterns.md` |
| Fully custom DOM | Headless mode (`Headless: TRUE`) | `custom-frontend.md` |

**Many "modern" or "professional" requests are met by the second row** - restyling and rearranging the default UI is usually the quickest path. When a design needs a layout or interaction the default UI can't express, a custom (headless) frontend is a fully supported tool - reach for it whenever it fits the goal.

---

## Inputs Reference

**IMPORTANT: Input formulas are only calculated once when the app opens.** They are NOT recalculated during app use. This means:
- Inputs with formulas act as static default values
- Any cell that depends on user input (intermediate calculations, derived values) **must be an output (red cell)**, not an input
- Only outputs are recalculated when users change values

### Basic Properties
| Property | Description |
|----------|-------------|
| `cell` | Excel cell reference (e.g., `Sheet1!B2`) |
| `name` | Display label for the input |
| `value` | Current/default value |
| `validation` | Validation rules |
| `UI` | UI-specific options (semicolon-separated) |
| `details` | Tooltip text (from cell comment) |

### Input Types (UI Options)

#### Text & Numeric Inputs
| UI Type | Description | Example |
|---------|-------------|---------|
| (default) | Standard text/number field | `UI: ""` |
| `textarea` | Multi-line text input | `UI: textarea` |
| `nobuttons` | Numeric without +/- buttons | `UI: nobuttons` |

#### Sliders & Ranges
| UI Type | Description | Example |
|---------|-------------|---------|
| `slider` | Single-handle slider | `UI: slider;min=0;max=100` |
| `range` | Dual-handle range slider | `UI: range;min=0;max=100` |
| `delta=N` | Increment step between slider ticks | `UI: slider;min=0;max=100;delta=10` |
| `gridNum=N` | Number of ticks on slider grid | `UI: slider;min=0;max=100;gridNum=5` |

#### Dropdowns & Selection
| UI Type | Description | Example |
|---------|-------------|---------|
| `dropdown` | Dropdown from data validation list | `UI: dropdown` |
| `select` | Same as dropdown | `UI: select` |
| `multiple` | Multi-select dropdown | `UI: multiple` |
| `recorddropdown` | Dropdown populated from the app's record table | `UI: recorddropdown;display=customerName` |
| `rowdropdown` | Dropdown populated from any database table | `UI: rowdropdown;tableName=data_my-app_0;display=name;map=name->custName` |

To create a dropdown: create a named range with the list values, add Data Validation to the input cell referencing that range, and set `UI: dropdown`.

**Database dropdowns (`recorddropdown` and `rowdropdown`)** load options from a database table via AJAX. See `database.md` for full configuration.

#### Date & Time
| UI Type | Description | Example |
|---------|-------------|---------|
| `date` | Date picker | `UI: date` |
| `time` | Time picker | `UI: time` |

#### Special Inputs
| UI Type | Description | Example |
|---------|-------------|---------|
| `fileupload` | File upload | `UI: fileupload;maxFiles=3;acceptedFileTypes=.pdf,.jpg` |
| `signature` | Signature capture | `UI: signature` |
| `barcode` | Barcode/QR scanner | `UI: barcode` |
| `infotext` | Read-only info display (can contain HTML) | `UI: infotext` |
| `longinfotext` | Long read-only info (can contain HTML) | `UI: longinfotext` |

**Boolean toggle buttons:** Inputs with boolean values (`True` or `False`) automatically render as clickable toggle buttons instead of text fields.

### Numeric Display Options
| Option | Description | Example |
|--------|-------------|---------|
| `min=N` | Minimum allowed value | `UI: min=0` |
| `max=N` | Maximum allowed value | `UI: max=100` |
| `delta=N` | Increment step for +/- buttons and slider ticks | `UI: delta=0.5` |
| `multiplier=N` | Display multiplier | `UI: multiplier=100` (shows 0.5 as 50) |
| `prefix=X` | Display prefix (inputs only) | `UI: prefix=$` |
| `postfix=X` | Display suffix (inputs only) | `UI: postfix=%` |
| `decimals=N` | Number of decimal places | `UI: decimals=2` |
| `placeholder=X` | Placeholder text | `UI: placeholder=Enter value...` |
| `regEx=X` | Regex pattern for validation | `UI: regEx=^[A-Z]{2}[0-9]{4}$` |

### Layout & Display Options
| Option | Description | Example |
|--------|-------------|---------|
| `hidden` | Hide the input | `UI: hidden` |
| `noTitle` | Hide the label | `UI: noTitle` |
| `class=X` | Custom CSS class - applied to `.panel-body`, not the outer `.panel`. For inputs, Molnify appends `-form-group-class` (e.g., `class=half-left` → `.half-left-form-group-class`) | `UI: class=my-custom-class` |
| `dividerName=X` | Add section divider above | `UI: dividerName=Personal Details` |
| `tab=X` | Start a new tab - all following inputs are placed in this tab until the next `tab=`. Only set on the **first** input of each tab, not on every input. | `UI: tab=Advanced` |

### Conditional Display
Show/hide inputs and outputs based on variable values:
| Option | Description | Example |
|--------|-------------|---------|
| `showIfVariable=X` | Variable name to check | `UI: showIfVariable=myVar` |
| `showIfValue=X` | Show if variable equals value | `UI: showIfVariable=myVar;showIfValue=Yes` |
| `showIfValueNot=X` | Show if variable NOT equals value | `UI: showIfVariable=myVar;showIfValueNot=No` |
| `resetWhenHidden` | Reset value to default while hidden (prevents submission of stale data). Previously entered values reappear when the input is shown again. | `UI: showIfVariable=myVar;showIfValue=Yes;resetWhenHidden` |

To use conditional display, first expose the controlling input or output as a variable with `variable=X`, then reference it in dependent inputs.

### User Context Variables
Automatically populate inputs with data from the user's session. These are set in the input's **UI cell** and are populated once when the app loads (before the first calculation). Not related to database autofill (`autofill.*` metadata).

| Variable | Value | Notes |
|----------|-------|-------|
| `user.email` | Logged-in user's email | Preferred over `user` |
| `user` | User's email (or identification number if available) | Legacy alias - use `user.email` for clarity |
| `user.ip` | User's IP address | |
| `superuser` | `"true"` or `"false"` | String, not boolean - compare with `="true"` in formulas |
| `manager` | `"true"` or `"false"` | String, not boolean - compare with `="true"` in formulas |
| `currentRealm` | Current realm name | Only meaningful when `Realms` metadata is set |
| `tag1` through `tag10` | Custom per-user data fields | **Requires `DBUsers: TRUE`** - these fields are managed via the sidebar user interface |

Example: `UI: user.email` auto-fills with the user's email.
Example: `UI: user.email;hidden` auto-fills and hides the input (common for tracking who submitted).

### JavaScript Integration
| Option | Description | Example |
|--------|-------------|---------|
| `variable=X` | Expose value to JavaScript (ASCII only - no ö, ä, å) | `UI: variable=myInput` |
| `jsOnChange=X` | Call JS function on change | `UI: jsOnChange=handleInputChange` |

---

## Outputs Reference

### Basic Properties
Same as inputs: `cell`, `name`, `value`, `UI`, `details`

### Output Display Options
| Option | Description | Example |
|--------|-------------|---------|
| `icon=X` | Font Awesome 4.7.0 icon (FA5/6 names won't render) | `UI: icon=fa-line-chart` |
| `background=X` | Background color | `UI: background=#f0f0f0` |
| `color=X` | Text color | `UI: color=#333333` |
| `amongInputs` | Show in input panel (html outputs only). **Tab placement depends on physical row order** - see note below. | `UI: amongInputs` |
| `hidden` | Hide the output | `UI: hidden` |
| `hideCopy` | Hide copy button (html outputs only) | `UI: hideCopy` |
| `leftColumn` | Force into left column (works on html, charts, tables, peopleMatrix) | `UI: leftColumn` |
| `rightColumn` | Force into right column (works on html, charts, tables, peopleMatrix). Without this, panels alternate between columns. **Required when using CSS Grid on `#boxRow`** - the default alternation logic doesn't apply in Grid layouts. | `UI: rightColumn` |
| `panelHidden` | Panel collapsed by default | `UI: panelHidden` |
| `dividerName=X` | Section divider above output (requires amongInputs) | `UI: dividerName=Revenue and profit` |
| `peopleMatrix` | People/team matrix visualization | `UI: peopleMatrix;columns=5;rows=3` |

**`amongInputs` and tabs:** Molnify assigns items to tabs based on physical row order in the spreadsheet. An `amongInputs` output with `tab=X` will only join an existing tab created by inputs if it appears **between those input rows** in the spreadsheet. If the output is placed after all inputs (e.g., because AppBuilder writes inputs first, then outputs), `tab=X` creates a **new, separate tab** instead of joining the existing one. To place an `amongInputs` output inside an input tab, it must be physically interleaved among the inputs in the spreadsheet. Use `app.add_output(..., among_inputs=True)` in AppBuilder to achieve this.

### Charts and Tables Structure

Charts and tables use **blue cells** for data values only.

**CRITICAL: Only the numeric/data value cells are colored blue. Everything else has NO color:**
- Chart title cell - NO color
- Column headers (series names) - NO color
- Row labels (category names) - NO color
- UI configuration cell - NO color

**Example - multi-series (single-series is the same with one data column; pie/donut use one column too):**
```
|     | A              | B          | C          | D          | E          |
|-----|----------------|------------|------------|------------|------------|
| 1   | Sales Trend    | Product A  | Product B  | Product C  | lineChart  |  <- NO color (all headers)
| 2   | Q1             | [BLUE]100  | [BLUE]150  | [BLUE]80   |            |  <- A2 no color, B2:D2 BLUE
| 3   | Q2             | [BLUE]120  | [BLUE]140  | [BLUE]95   |            |  <- A3 no color, B3:D3 BLUE
| 4   | Q3             | [BLUE]110  | [BLUE]160  | [BLUE]100  |            |  <- A4 no color, B4:D4 BLUE
```

**Key rules:**
- Data cell color: RGB 0,112,192 / hex #0070C0
- Rows where ALL values are empty (`""`) are hidden automatically
- Series (columns) where ALL values are empty are hidden automatically
- For pie/donut charts, series with all zeros are also hidden
- Column titles (row 1) become legend/series names
- Row labels (column A) become x-axis categories

### Chart Types

| Chart Type | Description | Example |
|------------|-------------|---------|
| `barChart` | Vertical bar chart | `UI: barChart` |
| `lineChart` | Line chart | `UI: lineChart` |
| `pieChart` | Pie chart (single column) | `UI: pieChart` |
| `donutChart` | Donut chart (single column) | `UI: donutChart` |
| `waterfallChart` | Waterfall chart | `UI: waterfallChart` |
| `scatterChart` | Scatter plot | `UI: scatterChart` |
| `geoChart` | Geographic map | `UI: geoChart;map=world_mill` |
| `lineBarChart` | Combined line/bar (first series = bars, rest = lines) | `UI: lineBarChart` |
| `table` | Data table | `UI: table` |

### Chart Options
| Option | Description | Example |
|--------|-------------|---------|
| `stacked` | Stacked bars (default off) | `UI: barChart;stacked` |
| `horizontal` | Horizontal bars | `UI: barChart;horizontal` |
| `showValues` | Show values on top of bars | `UI: barChart;showValues` |
| `xAxis=X` | X-axis title | `UI: lineChart;xAxis=Time` |
| `yAxis=X` | Y-axis title | `UI: lineChart;yAxis=Value` |
| `yAxisTicks=N` | Number of Y-axis ticks | `UI: lineChart;yAxisTicks=5` |
| `decimals=N` | Decimals for values displayed on chart | `UI: barChart;decimals=2` |
| `axisDecimals=N` | Decimals on axis labels | `UI: axisDecimals=1` |
| `noGridLines` | Hide grid lines | `UI: lineChart;noGridLines` |
| `steps` | Step interpolation for lines | `UI: lineChart;steps` |
| `atLeast=N` | Y-axis must include this value | `UI: barChart;atLeast=0` |
| `atLeastSync` | Sync Y-axis range for dual Y-axes (lineBarChart) | `UI: lineBarChart;atLeastSync` |
| `centerZero` | Center zero on Y-axis (negative values mirror positive) | `UI: barChart;centerZero` |
| `hideMaxMin` | Hide max/min labels on Y-axis | `UI: lineChart;hideMaxMin` |
| `staggerLabels` | Stagger X-axis labels (auto-enabled if >3 values) | `UI: barChart;staggerLabels` |
| `noWordWrap` | Disable label word wrap (horizontal bars only) | `UI: barChart;horizontal;noWordWrap` |
| `noControls` | Hide legend and stacked/grouped toggle | `UI: barChart;noControls` |
| `noGroupedStackedControls` | Hide only stacked/grouped toggle | `UI: barChart;noGroupedStackedControls` |
| `map=X` | Map name for geoChart | `UI: geoChart;map=world_mill` |
| `class=X` | Custom CSS class - applied to `.panel-body`, not the outer `.panel`. Use `$('.my-class').closest('.panel')` in JS to target the outer panel. | `UI: barChart;class=revenue-chart` |

**Scatter chart specific:**
- Column headers must use these reserved names: `x`, `y`, and optionally `series`, `size`, `shape`
- `atLeast` takes four comma-separated values: `xMin,xMax,yMin,yMax`

**Waterfall chart specific:** Use value `e` in a data cell to mark it as a subtotal row (sums all values above)

### Chart Series Styling
Style individual series:
```
UI: lineChart;series1.color=#FF0000;series2.color=#00FF00;series1.strokewidth=3;series2.dashedline;series1.showarea
```

| Property | Description |
|----------|-------------|
| `seriesN.color=X` | Series color (hex or name) |
| `seriesN.strokewidth=N` | Line thickness |
| `seriesN.dashedline` | Dashed line style |
| `seriesN.showarea` | Fill area under line |

### HTML Panels
Display custom HTML:
```
UI: html
```
The cell value should contain HTML content.

---

## Actions Reference

Actions are automated operations triggered by button clicks. Each action is defined in yellow cells in the spreadsheet. Action property values are regular cell values - they can be formulas that reference inputs/outputs, and are evaluated during calculation before the action runs.

### Common Action Properties
| Property | Description |
|----------|-------------|
| `type` | Action type (required) |
| `title` | Button label |
| `name` | Internal name (used by `performActionWithName()`) |
| `hidden` | TRUE to hide button |
| `cssClass` | Custom CSS class |
| `showIfCell` | Conditional display cell |
| `showIfValue` | Show if cell equals value |
| `showIfValueNot` | Show if cell NOT equals value |
| `skip` | TRUE to skip execution (returns success without running) |
| `skipMessage` | Message to return when action is skipped |

### Success Handling Properties
These properties control what happens in the UI after an action completes successfully:
| Property | Description |
|----------|-------------|
| `successText` | Message displayed in the action modal |
| `successUrl` | Redirects the entire page (including parent if in iframe) to this URL |
| `successFrameUrl` | Redirects only the current frame to this URL (stays within iframe) |
| `successNewTabURL` | Shows an "Open in new tab" button in the modal that opens this URL |
| `successCalculate` | TRUE to trigger app recalculation after the action |
| `successRefreshScenarioList` | TRUE to reload the scenario dropdown list |
| `successHTMLElementId` | DOM element ID to update (used with successHTMLElementContent) |
| `successHTMLElementContent` | HTML injected into the element; modal is hidden automatically. Can include `<script>` tags for JS execution |
| `successSilent` | TRUE to hide modal immediately with no message |
| `successJavaScript` | JavaScript code to execute after the action succeeds (runs via `eval`) |

If none of these are set, a default success message is shown and the modal stays open until the user closes it.

**Using `successHTMLElementId`:** This property injects HTML into an existing DOM element after the action succeeds. The target element must already exist in the page. To create a target element, add an `infotext` input with the desired `id` as an HTML attribute:
```
# Create target element using an infotext input
app.add_input("", '<div id="actionResult"></div>', ui="infotext;noTitle;hidden")

# Reference it in the action
app.add_action({
    "type": "addrecord",
    "successHTMLElementId": "actionResult",
    "successHTMLElementContent": '<div class="alert alert-success">Saved!</div>',
})
```
**Do NOT use existing page element IDs** like `content`, `app`, `boxRow`, or `inputpanel` - injecting HTML into these will destroy the page layout. Always create a dedicated target element.

### Action Types

#### Email Action (`type: email`)
Send emails via Mailjet.
| Property | Description | Default |
|----------|-------------|---------|
| `to` | Recipient email(s), comma or semicolon separated | (required) |
| `from` | Sender display name | "Molnify sender" |
| `email` | Sender email address | "no-reply@molnify.com" |
| `subject` | Email subject | "Email from an app on Molnify!" |
| `content` | Plain text body | - |
| `contentHTML` | HTML body (overrides `content` if both set) | - |

Either `content` or `contentHTML` should be provided. If neither is set, a default placeholder message is sent. Default success message: "Email sent!"

**No template substitution:** The `content` and `contentHTML` values are sent as-is. There is no `{{variable}}` substitution for email actions. To include dynamic values, make the action property a **formula** that concatenates HTML with cell references:
```
contentHTML: ="<h1>Your BMI: "&App!B4&"</h1><p>Category: "&App!B5&"</p>"
```

**Limitations:** No CC/BCC, no attachments, no reply-to address. Recipients are split on `,` and `;` without trimming whitespace - use `"a@x.com,b@x.com"` not `"a@x.com, b@x.com"`.

#### HTTP Action (`type: http`)
Make HTTP requests to external APIs.
| Property | Description | Default |
|----------|-------------|---------|
| `url` | Endpoint URL | (required) |
| `method` | HTTP method (GET, POST, PUT, etc.) | "POST" |
| `payload` | Request body (overridden if `autoPayload` produces data) | "OK" |
| `autoPayload` | Auto-generate JSON payload: `inputs`, `outputs`, or `all` | - |
| `token` | Authorization token (added to Authorization header) | - |
| `authorizationType` | Auth scheme prefix for token | "Token" |
| `contentType` | Content-Type header | "application/json" |
| `responseVariable` | Variable to store the response body in | "httpresponse" |

**Response handling:** Only HTTP 200 and 201 are treated as success - other 2xx codes (202, 204, etc.) are treated as failures. The response body is set on the input matching `responseVariable` (default `httpresponse`), allowing you to parse it with `FILTERJSON()`. Newlines are stripped from the response body.

**`autoPayload` details:** Generates a JSON object using **cell references** as keys (e.g. `{"Sheet1!B2": "value"}`), not variable names. `inputs` includes all input cells, `outputs` includes all output cells, `all` includes both. If the generated JSON is empty, the original `payload` value is used instead.

**Request details:**
- `Accept` header is always `application/json` (not configurable)
- `User-Agent` is set to `Molnify-HTTP-Connector/1.1`
- Connect timeout: 5 seconds, read timeout: 12 seconds
- No automatic redirect following (3xx responses are treated as failures)

Default success message: "All received. Thank you!"

#### Scenario Save Action (`type: scenariosave`)
Save current input values as a named scenario.
| Property | Description | Default |
|----------|-------------|---------|
| `newName` | Scenario name | (required) |
| `oldName` | Previous name to delete (for rename operations) | - |
| `private` | TRUE for private scenario, FALSE for public | "true" |
| `allowOverwrite` | TRUE to allow others to overwrite this scenario | "false" |
| `overwriteCurrentScenario` | TRUE to update the currently loaded scenario | "false" |

Use with `successRefreshScenarioList: TRUE` to update the scenario dropdown after saving.

#### Generate Report Action (`type: generatereport`)
Generate PDF reports from templates. Runs asynchronously. The template syntax depends on the `engine` - HTML/markdown use Mustache, DOCX uses poi-tl, XLSX uses named ranges. See `report-templates.md` for details.

| Property | Description | Default |
|----------|-------------|---------|
| `template` | Template name (created via Template Manager) | "template" |
| `engine` | Conversion engine: `html`, `markdown`, `docx`, `xlsx` | "html" |
| `fileName` | Output PDF filename (.pdf added automatically) | "{appId}-molnify.pdf" |
| `suppressDownload` | TRUE to not auto-download the file | "false" |
| `to` | Email recipient (sends email with report link) | - |
| `content` | Plain text email body (use `{{urlToReport}}` placeholder) | - |
| `contentHTML` | HTML email body (use `{{urlToReport}}` placeholder) | - |
| `saveIp` | FALSE to not save user IP in metadata | "true" |

**PDF rendering properties:**

| Property | Description | Default |
|----------|-------------|---------|
| `landscape` | TRUE for landscape orientation | "false" |
| `paperSize` | Paper size: LETTER, LEGAL, TABLOID, LEDGER, A0-A6 | "LETTER" |
| `cssPageSize` | TRUE to use CSS `@page` size instead of `paperSize` | "false" |
| `margin` | Default margin for all sides (inches) | "0.5" |
| `marginTop`, `marginBottom`, `marginLeft`, `marginRight` | Override individual margins | uses `margin` |
| `waitDelay` | Milliseconds to wait before PDF conversion (for JS rendering) | "0" |
| `waitForExpression` | JavaScript expression that must return truthy before conversion | - |
| `pageRanges` | Page ranges to include (e.g., "1-3,5") | all pages |
| `includeBackground` | TRUE to print background graphics/colors | "false" |
| `mediaType` | CSS media type: `screen` or `print` | "print" |
| `performanceMode` | TRUE to skip rendering delay | "false" |

Shows "Preparing your file" in the modal while generating. Once ready, the file downloads automatically. Use `suppressDownload: TRUE` to skip the download while still emailing the report link via the `to`/`content`/`contentHTML` options. If no `content`/`contentHTML` is set but `to` is provided, the email body is just the report URL.

#### Generate File Action (`type: generatefile`)
Generate Excel or PDF files from XLSX templates. Runs asynchronously. **Prefer `generatereport`** for most use cases - `generatefile` is only needed when you want the output as an `.xlsx` file (not PDF) or need workbook password protection.
| Property | Description | Default |
|----------|-------------|---------|
| `template` | XLSX template filename | (required) |
| `format` | Output format: `pdf` or `xlsx` | "pdf" |
| `fileName` | Output filename | "{appId}-molnify.{format}" |
| `landscape` | TRUE for landscape orientation (PDF only) | "false" |
| `overwriteFormatting` | TRUE to apply template formatting to output | "true" |
| `protectWorkbook` | TRUE to password-protect the Excel output | "false" |
| `workbookPassword` | Password for workbook protection | - |

Shows "Preparing your file" in the modal while generating. Once ready, the file downloads automatically.

#### Database Actions

**Insert/Update Record (`type: addrecord`)**
Insert or update a record in the application's configured record table.
| Property | Description | Default |
|----------|-------------|---------|
| `saveIp` | TRUE to save user IP address | "true" |
| `recordTableName` | Override the app's default record table for this action | app's `RecordTableName` metadata |
| `idVariable` | Variable that holds/receives the record ID | app's `RecordTableIdVariable` metadata, or `"recordId"` |

Requires `RecordTableName` metadata (or `recordTableName` action option) to be set to the full table name including the `data_` prefix (e.g., `data_my-app_0`). Maps input/output variables to database columns. If the ID variable has a value, updates that record; otherwise creates a new record. The new/updated record ID is automatically set on the input matching `idVariable`.

**Important:** Only modified ("dirty") inputs are sent. Columns for unmodified inputs need `DEFAULT` values or must be nullable. See `database.md` for details.

**Insert SQL Row (`type: insertrow`)**
Insert or update a row in a specific database table with explicit column mapping.
| Property | Description | Default |
|----------|-------------|---------|
| `tablename` | Target table name (include `data_` prefix for consistency) | (required) |
| `.{columnname}` | Column value (prefix column name with `.`) | - |
| `k.{columnname}` | Primary key column (prefix with `k.` for upsert) | - |
| `idVariable` | Variable that receives the inserted/updated row ID | - |
| `saveIp` | TRUE to save user IP address | "true" |

Uses INSERT ... ON DUPLICATE KEY UPDATE for upsert behavior. Automatically adds `_molnify_user_email`, `_molnify_application_id`, `_molnify_user_ip` columns.

**Important:** Only modified ("dirty") inputs are sent. Columns for unmodified inputs need `DEFAULT` values or must be nullable. See `database.md` for details.

#### Download Query Action (`type: downloadquery`)
Download SQL query results as a file.
| Property | Description | Default |
|----------|-------------|---------|
| `query` | SQL SELECT query to execute | (required) |
| `format` | Output format: `csv` or `json` | "csv" |

Shows "Preparing your file" in the modal, then downloads automatically. CSV files use semicolon delimiter and include UTF-8 BOM. Filename format: `YYYYMMDD-HHmm-{appId}.{format}`.

#### E-Sign Action (`type: createesign`)
Create e-signature request via Zigned. Runs asynchronously.
| Property | Description | Default |
|----------|-------------|---------|
| `template` | Template name (created via Template Manager) | (required) |
| `provider` | E-sign provider (only "zigned" supported) | (required) |
| `fileName` | Output PDF filename | "{appId}-molnify.pdf" |
| `attachments` | Comma-separated URLs of files to attach | - |
| `saveIp` | TRUE to save user IP in metadata | "true" |

#### Reset Inputs Action (`type: resetinputs`)
Reset input variables to specified values or their spreadsheet defaults.
| Property | Description | Default |
|----------|-------------|---------|
| `.{variableName}` | Value to reset to (prefix variable name with `.`). Empty = use spreadsheet default. | - |

If no `.{variableName}` properties are specified, all inputs that have a `variable` are reset to their spreadsheet defaults. Otherwise, only the listed variables are reset.

Example:
```
type: resetinputs
title: Reset Form
.name: Default Name
.age:
```
Resets `name` to `"Default Name"` and `age` to its spreadsheet default value. Inputs without a `variable` UI option are not affected.

#### Multiple Action (`type: multiple`)
Execute several actions in sequence with a single button click.
| Property | Description |
|----------|-------------|
| `1`, `2`, `3`, ... | Name of the sub-action at each step (references another action's `name` property) |

Number sub-actions starting from 1. Each references another action by its `name` property. Sub-actions run in numeric order and **execution stops immediately if any sub-action fails** - later sub-actions do not run.

Success handling properties (`successText`, `successUrl`, etc.) set on the multiple action take precedence over those from sub-actions.

**Do not wrap `aiprompt` or `http` actions inside `multiple` if you need their response.** The `multiple` wrapper consumes the `responsevalue` field - the AI or HTTP response becomes inaccessible. Use `skip` formulas on the action directly for conditional execution, and chain follow-up work via `successJavaScript` instead.

Example - define a `scenariosave` action named `saveStep` and an `email` action named `emailStep`, both with `hidden: TRUE`. Then create the visible button:
```
type: multiple
title: Save & Email
1: saveStep
2: emailStep
successText: Saved and emailed!
```

#### AI Prompt Action (`type: aiprompt`)
Send a prompt to an AI model (Google Gemini) and store the response in a variable.

**Prerequisites:** Before using this action, the app uploader must: (1) be granted access to the AI model, (2) have created a token pool, and (3) have assigned the app to the token pool. All of this is managed in the AI Manager.

| Property | Description | Default |
|----------|-------------|---------|
| `model` | Model identifier: `gemini-flash` or `gemini-pro` | (required) |
| `prompt` | The prompt text to send to the AI model | (required) |
| `maxOutputTokens` | Maximum tokens in the response | 1024 |
| `thinkingBudget` | Token budget for model reasoning (must be > 0 for `gemini-pro`) | 0 |
| `responseSchema` | JSON schema to enforce structured response format | - |
| `responseVariable` | Variable name to store the AI response in | "aipromptresponse" |

**Models:**

| Model | Best For |
|-------|----------|
| `gemini-flash` | Fast responses, summarization, extraction, real-time use |
| `gemini-pro` | Complex analysis, long-form generation, planning, reasoning-heavy tasks |

`gemini-pro` requires `thinkingBudget` > 0 and consumes more tokens per request than `gemini-flash`.

**Response handling:** The AI response text is set on the input matching `responseVariable` (default `aipromptresponse`), allowing you to display it or parse it with `FILTERJSON()`. If `responseSchema` is provided, the response is constrained to valid JSON matching the schema - use `FILTERJSON()` on the response variable's cell to extract individual fields from it.

**Token quota:** Each execution consumes tokens from the app's assigned token pool. If the pool is exhausted, the action returns an error.

**Dynamic prompts:** Like all action properties, `prompt` can be a formula that references inputs/outputs:
```
prompt: ="Summarize the following text in "&B2&" words: "&B3
```

**Structured output with `responseSchema`:** Provide a JSON schema to get predictable, parseable responses. Use `FILTERJSON()` on the response variable's cell to extract fields from the JSON response:
```
type: aiprompt
model: gemini-flash
prompt: ="Classify this feedback as positive, negative, or neutral: "&B2
responseSchema: {"type":"object","properties":{"sentiment":{"type":"string","enum":["positive","negative","neutral"]},"confidence":{"type":"number"}},"required":["sentiment","confidence"]}
responseVariable: classification
maxOutputTokens: 256
```
If `classification` is in cell B10, use `=FILTERJSON(B10, "sentiment")` and `=FILTERJSON(B10, "confidence")` in output cells to extract the values.

**Example - simple text generation:**
```
type: aiprompt
title: Generate Summary
model: gemini-flash
prompt: ="Write a 3-sentence summary of: "&B2
responseVariable: summary
successSilent: TRUE
successCalculate: TRUE
```

---

## Metadata Reference

Metadata cells (purple) configure application-wide settings.

### Application Identity
| Property | Description |
|----------|-------------|
| `Name` | Application name (shown in header and page title) |
| `Author` | Author name (shown in app info modal) |
| `Website` | Website URL |
| `Version` | Version string |
| `Description` | App description (shown in app info modal) |
| `Reference` | Reference/documentation URL (shows reference button if set) |

### Panel Customization
| Property | Default | Description |
|----------|---------|-------------|
| `InputPanelTitle` | "Inputs" | Input section title |
| `OutputPanelTitle` | "Results" | Output section title |
| `CalculateTitle` | "Calculate" | Calculate button text |
| `CopyTitle` | - | Copy button text |
| `SaveTitle` | - | Save button text |

### Feature Toggles
| Property | Default | Description |
|----------|---------|-------------|
| `AutoCalcEnabled` | TRUE | Auto-calculate on input change. When FALSE, no calculation runs automatically - not on load, not on input change; you must trigger calculation yourself (e.g. `calculateButton()` in `JavaScriptAfterLoad` for the initial calc). **Avoid disabling unless truly required** - disabling as a performance optimization breaks the expected UX and introduces subtle bugs. |
| `EnabledForCalculate` | TRUE | Show calculate button (only visible when AutoCalc is FALSE) |
| `EnabledForSave` | FALSE | Enable scenario saving (shows save/delete/share buttons) |
| `EnabledForReset` | FALSE | Show reset button |
| `EnabledForPrint` | TRUE | Show print button |
| `EnabledForUpdate` | FALSE | Show update button (allows anyone to re-upload/update the app) |
| `EnabledForLogOut` | FALSE | Show logout button (only visible when user is signed in) |
| `EnabledForDynamicTitles` | TRUE | Recalculate input/output titles on each calculation |
| `CookieConsentPopup` | FALSE | Show cookie consent dialog on app load |
| `Headless` | FALSE | Serve a minimal page instead of the full UI. Provides `window.molnify` bootstrap object, `MolnifySDK`, and empty `<div id="app">`. Only `JavaScript` metadata runs (not `JavaScriptAfterLoad`/`JavaScriptAfterCalc`). See `custom-frontend.md`. |

### User Management
| Property | Description |
|----------|-------------|
| `Users` | Comma-separated emails or domains (`*@company.com`) to restrict access. If not set, app is public. |
| `SuperUsers` | Comma-separated emails with elevated permissions (can manage users and managers) |
| `Managers` | Comma-separated emails who can manage regular users and view all scenarios |
| `Realms` | Comma-separated realm names (e.g., "Europe,Asia,Americas") - creates a realm selector dropdown |
| `DBUsers` | TRUE to manage users via the sidebar interface instead of metadata |

**Note:** `Users`, `SuperUsers`, and `Managers` can also reference a cell range (e.g., `users!A2:A200`) instead of a comma-separated list.

### Styling
| Property | Description |
|----------|-------------|
| `CSS` | Complete custom CSS |
| `additionalCSS` | CSS appended after the main `CSS` value. Use when a template provides base CSS and you want to extend it without replacing it. Also useful when CSS exceeds a single cell's 32,767-character limit - split across `CSS` and `additionalCSS`. |
| `TopBannerColor` | Top banner color. Paints the **top banner** (`#header`, the fixed full-width bar above the app), via `#molnifyAppBody .container-fluid`. This is a different element from `#appHeaderRow` (the app title bar inside `#content`) - it does not color that. |
| `HeaderTextColor` | Colors the **app title** at the top of the content area (`h1#appHeader`/`#pAppTitle`, via `#molnifyAppBody h1`) - not the top banner (a logo, no text). The title sits on the page background, light by default, so keep it **dark**; only go light for a dark-background app. |
| `PanelHeaderColor` | Panel header color |
| `ButtonColor` | Default button color |
| `ButtonActiveColor` | Selected button color |
| `SuccessButtonColor` | Success/action button color |
| `ExpandButtonColor` | Expand button color |
| `CollapseButtonColor` | Collapse button color |
| `OutputBoxBackgroundColor` | Output box background |
| `ChartDownloadBackgroundColor` | Background color for downloaded chart images |
| `ToggleActiveColor` | Active state color for boolean toggle buttons |
| `BackgroundImageURL` | Background image URL for the app |
| `LogoURL` | Custom logo URL (replaces "Molnify" text in top banner) |
| `FaviconURL` | Custom favicon URL (browser tab icon, should be .ico or small .png) |
| `AppleTouchIconURL` | Apple touch icon URL (for iOS home screen, typically 180x180 .png) |
| `HeaderFont` | Header font family (Google Fonts name, e.g., "Roboto") |
| `BodyFont` | Body font family (Google Fonts name) |

### Slider Styling
| Property | Description |
|----------|-------------|
| `SliderMinAndMaxBackgroundColor` | Min/max label background |
| `SliderMinAndMaxTextColor` | Min/max label text color |
| `SliderCurrentValueBackgroundColor` | Current value background |
| `SliderCurrentValueTextColor` | Current value text color |

### Scenarios Configuration
| Property | Default | Description |
|----------|---------|-------------|
| `ScenarioTerm` | "Scenario" | Custom term (e.g., "Order", "Quote", "Case") - affects all UI labels |
| `RealmTerm` | "Realm" | Custom term for realm (e.g., "Region", "Department") |
| `ScenarioNameVariable` | - | Variable whose value becomes the default scenario name in save dialog |
| `ScenarioSavePrivate` | FALSE | TRUE to save scenarios as private by default |
| `ScenarioLockOption` | FALSE | TRUE to show lock icon for scenarios where overwrite is disabled |
| `ScenarioSharedUsersCell` | - | Cell containing comma-separated emails to share scenarios with |
| `RecordTableName` | - | Database table name for record storage (used with `addrecord` action) |
| `RecordTableIdVariable` | "recordId" | Column name used as the record ID in the record table. Overrideable per-action with `idVariable`. |
| `RecordTableAccessColumn` | - | Column name for row-level access control |
| `DataTable.N` | - | Declarative DB table schema (JSON). N=0-31 maps to `data_<appId>_N`. See [Data Persistence](#data-persistence). |

### JavaScript Integration
| Property | When it runs | Description |
|----------|--------------|-------------|
| `JavaScript` | Page load (early) | Custom JS code, runs before app is fully interactive |
| `additionalJavaScript` | Page load (early) | JavaScript appended after the main `JavaScript` value. Use when a template provides base JS and you want to extend it, or when JS exceeds a single cell's 32,767-character limit - split across `JavaScript` and `additionalJavaScript`. |
| `JavaScriptAfterLoad` | Page load (late) | JS to run after app fully loads and initial calculation completes |
| `JavaScriptAfterCalc` | Every calculation | JS to run after each calculation (including initial load) |

#### Available JavaScript Functions
| Function | Description |
|----------|-------------|
| `setValueForVariable(name, value)` | Set a variable's value (**triggers auto-calc if `AutoCalcEnabled: TRUE`** - see warning below) |
| `getValueForVariable(name)` | Get a variable's current value |
| `performActionWithName(name)` | Trigger an action by its name |
| `calculateButton()` | Trigger app recalculation |
| `getValueForURLParam(name)` | Get a URL query parameter value |

**WARNING - `setValueForVariable` and auto-calc loops:**
When `AutoCalcEnabled: TRUE` (the default), calling `setValueForVariable()` triggers a recalculation. If you call it inside `JavaScriptAfterCalc`, this creates an infinite loop: calc → afterCalc → setValue → calc → afterCalc → ... Always guard with a value comparison:
```javascript
JavaScriptAfterCalc:
var current = getValueForVariable('myVar');
var desired = computeNewValue();
if (current !== desired) setValueForVariable('myVar', desired);
```

Example - Auto-run action on load:
```javascript
JavaScriptAfterLoad: performActionWithName('loadData');
```

Example - Store parsed value:
```javascript
function saveToken() {
  let tok = getValueForVariable('token');
  if (tok !== '\u00A0') setValueForVariable('storedToken', tok);
}
```

### API & Security
| Property | Description |
|----------|-------------|
| `IpRanges` | Comma-separated IP ranges to restrict access (e.g., "192.168.1.0/24,10.0.0.0/8") |
| `TokenAuthentication` | Token authentication config |

### Custom Tooltips
| Property | Description |
|----------|-------------|
| `CustomInfoTooltip` | Info button tooltip |
| `CustomReferenceTooltip` | Reference button tooltip |
| `CustomUpdateTooltip` | Update button tooltip |
| `CustomSaveTooltip` | Save button tooltip |
| `CustomPrintTooltip` | Print button tooltip |
| `CustomResetTooltip` | Reset button tooltip |
| `CustomLogoutTooltip` | Logout button tooltip |
| `CustomDownloadDataTooltip` | Download button tooltip |
| `CustomDeleteTooltip` | Delete button tooltip |

### Advanced Options
| Property | Default | Description |
|----------|---------|-------------|
| `TopBannerHidden` | FALSE | TRUE to hide the top navigation banner |
| `HeaderHidden` | FALSE | TRUE to hide the app header row |
| `InputPanelSmall` | FALSE | TRUE for narrower input panel (33% width instead of 50%) |
| `InputPanelFixed` | FALSE | TRUE to keep input panel fixed while scrolling |
| `PanelsFixed` | FALSE | TRUE to keep both panels fixed while scrolling |
| `OutputBoxPanelHidden` | FALSE | TRUE to collapse output panel by default |
| `OnlyAppNameInPageTitle` | FALSE | TRUE for page title "AppName" instead of "AppName - Molnify" |
| `ClearClipboardAtReset` | FALSE | TRUE to clear copied values when reset button clicked |
| `ClearClipboardAtCalc` | FALSE | TRUE to clear copied values on each calculation |
| `CustomLogOutURL` | - | URL to redirect to after user logs out |
| `HeadHTML` | - | Raw HTML injected into `<head>` - use for CDN `<script>` or `<link>` tags |
| `Template` | - | Apply a built-in template |
| `OnlyIncludeSheet` | - | Only parse the named sheet (ignores all other sheets) |
| `calcTimerSeconds` | - | Auto-recalculate every N seconds (minimum 0.5). Sets up `setInterval(calculateButton, N*1000)`. |

---

## Validation Rules

Validation is specified in the validation property of inputs.

### Numeric Validation
| Rule | Description |
|------|-------------|
| `>N` | Greater than N |
| `>=N` | Greater than or equal to N |
| `<N` | Less than N |
| `<=N` | Less than or equal to N |
| `=N` | Equals N |

### Text Validation
| Rule | Description |
|------|-------------|
| `notEmpty` | Cannot be empty |

### Custom Validation
Use `var=variableName` to store validation dropdown options in a JavaScript variable.


---

*This is v1.0.14 of the skill, published 2026-07-22. Installed copies are version-pinned; to update to the latest release, re-run `npx skills add https://app.molnify.com` (see `README.md`).*
