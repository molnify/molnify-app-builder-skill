# Custom Frontend (Headless Molnify)

Companion to the main reference.

Replace Molnify's default UI with a fully custom DOM while keeping the backend calculation engine, actions, and authentication.

**When to use this:**
- Building a game, interactive visualization, or drag-and-drop interface
- Creating a mobile-optimized UI that doesn't fit the form paradigm
- White-labeling where the app must look nothing like Molnify
- Embedding Molnify calculations into a larger single-page app

**When NOT to use this:**
- If you just want a different layout → use CSS/JS to restyle the existing DOM (see `styling.md`)
- If you want a few custom components → use HTML outputs with `amongInputs`
- If you want custom buttons or navigation → see the wizard and grouped sections patterns in `patterns.md`

**Key principle:** The JavaScript is only the UI layer. All business logic, calculations, validation, and data transformations belong in the spreadsheet. Send input values to the backend via `MolnifySDK.calculate()` and read results from the response — do not reimplement formulas in JS. This keeps the spreadsheet as the single source of truth and means the app works identically whether served via headless mode or the default UI.

---

## How It Works

Set `Headless: TRUE` metadata. Molnify serves a minimal page instead of the full UI - no Bootstrap, no jQuery, no framework JavaScript. Just your code.

1. The same `/app/<id>` URL works - headless routing is automatic
2. A `window.molnify` bootstrap object is injected with all app data
3. `MolnifySDK` (a lightweight fetch-based client) is loaded
4. Your `JavaScript` metadata runs
5. Your code builds the UI and calls `MolnifySDK.calculate()` / `MolnifySDK.execute()`

The backend doesn't care what the frontend looks like. It receives cell values, calculates, and returns results.

---

## What You Get

- **`window.molnify`** - bootstrap object with `appId`, `calcUrl`, `dateModified`, `inputs`, `outputs`, `actions`
- **`MolnifySDK`** - lightweight client library with debounced, queued API calls using native `fetch()`
- **`<div id="app">`** - empty container for your custom UI
- **`JavaScript` metadata** - your custom code, runs after the SDK loads
- **`CSS` metadata** - injected as `<style>` in `<head>`
- **`HeadHTML` metadata** - raw HTML in `<head>` for external libraries
- **Google Fonts** - auto-loaded if `HeaderFont` or `BodyFont` is set
- **Google Tag Manager** - included with same consent logic as standard mode

## What You Don't Get

No Bootstrap CSS/JS, no jQuery, no Font Awesome, no NVD3, no ionRangeSlider, no switchery, no datepicker, no parsley, no select2, no sidebar, no header, no footer, no modals, no scenario management, no `extractInputs()`, no `autoCalc()`, no `performCalcRequest()`.

Only `JavaScript` metadata runs - **not** `JavaScriptAfterLoad` or `JavaScriptAfterCalc` (there is no framework calc cycle).

---

## `window.molnify` Bootstrap Object

Automatically injected. Contains everything a custom frontend needs:

```javascript
window.molnify = {
  appId: "my-app",
  calcUrl: "https://prod.compute.molnify.com",
  dateModified: "1709715500000",
  inputs: [
    { cell: "App!B1", name: "Weight", value: "80", variable: "weight", ui: "variable=weight" },
    { cell: "App!B2", name: "Height", value: "175", variable: "height", ui: "variable=height" }
  ],
  outputs: [
    { cell: "App!B4", name: "BMI", value: "26.1", variable: "bmi", ui: "variable=bmi" }
  ],
  actions: [
    { index: 0, title: "Send Email", name: "send-email", hidden: false }
  ]
};
```

Also available in standard (non-headless) apps.

---

## MolnifySDK API

| Method | Description |
|--------|-------------|
| `MolnifySDK.calculate(changes)` | Debounced (120ms), queued. Returns `Promise` resolving to response data. |
| `MolnifySDK.execute(nameOrIndex, changes)` | Execute an action by name (string) or index (number). Optional `changes` array. |
| `MolnifySDK.getVariable(name)` | Look up input/output by variable name. Returns `{cell, value, name, ui}` or `undefined`. |
| `MolnifySDK.getCellForVariable(name)` | Shorthand returning just the cell reference string. |
| `MolnifySDK.getAllVariables()` | Returns `{varName: {cell, value, ...}, ...}` map. |
| `MolnifySDK.searchDropdown(cell, query, changes)` | Search a database dropdown. Returns `Promise<[{id, text}]>`. |
| `MolnifySDK.getDropdownRowData(cell, rowId, changes)` | Fetch full row data for a selected dropdown row. Optional `changes` for filter resolution. Returns `Promise<{row, idColumn, map}>`. |
| `MolnifySDK.uploadFile(file)` | Upload a `File` object to Molnify storage. Returns `Promise<{url, urlFull}>`. |

Also available in standard (non-headless) apps.

### Dropdown Methods

For apps with `recorddropdown` or `rowdropdown` inputs, the SDK provides methods to search and select rows without the default Select2 UI.

**`searchDropdown(cell, query, changes)`** — Search for matching rows.
- `cell` — cell reference of the dropdown input (e.g., `"Sheet1!B5"`)
- `query` — search string (default `""` returns all rows up to `maxRows`)
- `changes` — `[{variable, value}, ...]` for `@variable` filter resolution (optional)

```javascript
MolnifySDK.searchDropdown('App!B3', 'Swe').then(function(items) {
  // items = [{id: "42", text: "Sweden"}, {id: "17", text: "Swiss"}]
  items.forEach(function(item) { console.log(item.id, item.text); });
});
```

**`getDropdownRowData(cell, rowId, changes)`** — Fetch the full row after selection.
- `cell` — same cell reference used in `searchDropdown`
- `rowId` — the `id` from a search result item
- `changes` — `[{variable, value}, ...]` for `@variable` filter resolution (optional)

Returns `{row, idColumn, map}` where:
- `row` — `{columnName: value}` for all columns in the selected row
- `idColumn` — the ID column name (e.g., `"recordId"` or custom `idVariable`)
- `map` — explicit column-to-variable mapping string if configured (e.g., `"name->custName,email->custEmail"`), or absent for auto-mapping

```javascript
MolnifySDK.getDropdownRowData('App!B3', '42').then(function(data) {
  console.log(data.row.name);      // "Sweden"
  console.log(data.idColumn);      // "recordId"
  // Apply values to your UI manually — the SDK does not auto-set variables
});
```

### File Upload

**`uploadFile(file)`** — Upload a file to Molnify storage.
- `file` — a `File` object (from `<input type="file">` or drag-and-drop)

Returns `{url, urlFull}` where `url` is the storage URL and `urlFull` is the full-size URL (for images, includes the `__full_` variant).

```javascript
var input = document.querySelector('input[type="file"]');
input.addEventListener('change', function() {
  MolnifySDK.uploadFile(input.files[0]).then(function(result) {
    // Set the file URL as the cell value for a fileupload input
    return MolnifySDK.calculate([{cell: 'App!B5', value: result.url}]);
  });
});
```

---

## API Endpoints

### POST `/api/calculate`

Send changed input values, receive calculated output values.

**Request:**
```json
{
  "applicationID": "my-app",
  "requestID": "1709715600000",
  "dateModified": "1709715500000",
  "changes": [
    { "cell": "App!B1", "value": "42" },
    { "cell": "App!B2", "value": "hello" }
  ]
}
```

**Response:**
```json
{
  "applicationID": "my-app",
  "requestID": "1709715600000",
  "dateModified": "1709715500000",
  "changes": [
    { "cell": "App!B4", "value": "84", "name": "Result" },
    { "cell": "App!B5", "value": "<div>html content</div>" }
  ],
  "charts": [
    { "cell": "App!B7", "valueObject": { "...": "chart data" } }
  ],
  "errors": {}
}
```

**Key details:**
- Only send inputs that changed ("dirty") - not all inputs
- Values are always strings, even numbers (`"42"` not `42`)
- `requestID` must be unique per request - use `String(Date.now())`
- `dateModified` is **required** - available as `window.molnify.dateModified`. The backend rejects requests with a missing `dateModified`.
- `userToken` is **not required** - auth is cookie-based. The backend extracts the user from the session JWT cookie automatically.

### POST `/api/execute`

Run an action. Same payload as `/api/calculate`, plus `actionId` (a 0-based integer index) and an optional `currentScenarioID`.

**Key details:**
- `actionId` is a 0-based integer index - use `MolnifySDK.execute(nameOrIndex)` to avoid dealing with indices
- All current input values should be sent in `changes` so the backend can evaluate action property formulas before executing

### POST `/api/dropdown_rows`

Search a database dropdown for matching rows.

**Request:**
```json
{
  "appId": "my-app",
  "cell": "Sheet1!B5",
  "q": "search term",
  "changes": [
    { "variable": "country", "value": "Sweden" }
  ]
}
```

**Response:**
```json
{
  "status": "ok",
  "items": [
    { "id": "42", "text": "Acme Corp (Sweden)" },
    { "id": "17", "text": "Beta Inc (Sweden)" }
  ]
}
```

**Key details:**
- `changes` uses `variable`/`value` keys (not `cell`/`value` like calculate) — these resolve `@variable` placeholders in the dropdown's `filter` option
- `q` is the search term — matched against the `display` column via SQL `LIKE`
- Returns up to `maxRows` results (default 1000)

### POST `/api/dropdown_row_data`

Fetch full row data for a selected dropdown row.

**Request:**
```json
{
  "appId": "my-app",
  "cell": "Sheet1!B5",
  "rowId": "42"
}
```

**Response:**
```json
{
  "status": "ok",
  "row": { "name": "Acme Corp", "country": "Sweden", "email": "info@acme.com" },
  "idColumn": "recordId",
  "map": "name->custName,country->custCountry"
}
```

**Key details:**
- `map` is only present when the dropdown has an explicit `map` UI option — otherwise the default UI auto-maps column names to variable names
- `idColumn` reflects the `idVariable` setting (default `"recordId"`)

---

## `HeadHTML` Metadata

Inject raw HTML into the `<head>` of the page. Use it for external CDN libraries:

```
HeadHTML: <script src="https://cdn.jsdelivr.net/npm/chart.js"></script><link rel="stylesheet" href="https://cdn.example.com/styles.css">
```

Also available in standard (non-headless) apps.

---

## Complete Example

A BMI calculator with a fully custom UI.

**Spreadsheet metadata:**
```
ID: custom-bmi
Name: BMI Calculator
Headless: TRUE
```

**Spreadsheet (AppBuilder):**
```python
from molnify_builder import AppBuilder

app = AppBuilder("custom-bmi", "BMI Calculator")
app.add_input("Weight (kg)", 80, ui="variable=weight")
app.add_input("Height (cm)", 175, ui="variable=height")
app.add_output("BMI", "=ROUND(B1/(B2/100)^2,1)", ui="variable=bmi")
app.add_output("Category", '=IF(B4<18.5,"Underweight",IF(B4<25,"Normal",IF(B4<30,"Overweight","Obese")))', ui="variable=category")
app.add_metadata("Headless", "TRUE")
```

**JavaScript metadata:**
```javascript
var weightCell = MolnifySDK.getCellForVariable('weight');
var heightCell = MolnifySDK.getCellForVariable('height');

document.getElementById('app').innerHTML =
  '<div style="max-width:400px;margin:60px auto;font-family:system-ui;text-align:center">' +
    '<h1 style="font-size:48px;margin:0">BMI</h1>' +
    '<p style="color:#888">Slide to calculate</p>' +
    '<div style="margin:30px 0">' +
      '<label>Weight: <span id="w-val">80</span> kg</label><br>' +
      '<input type="range" id="w" min="30" max="200" value="80" style="width:100%">' +
    '</div>' +
    '<div style="margin:30px 0">' +
      '<label>Height: <span id="h-val">175</span> cm</label><br>' +
      '<input type="range" id="h" min="100" max="220" value="175" style="width:100%">' +
    '</div>' +
    '<div id="result" style="font-size:64px;font-weight:700;margin:20px 0">-</div>' +
    '<div id="cat" style="font-size:20px;color:#666">-</div>' +
  '</div>';

// Build cell-to-variable lookup for response handling
var cellToVar = {};
var allVars = MolnifySDK.getAllVariables();
for (var name in allVars) {
  cellToVar[allVars[name].cell] = name;
}

function recalc() {
  var w = document.getElementById('w').value;
  var h = document.getElementById('h').value;
  document.getElementById('w-val').textContent = w;
  document.getElementById('h-val').textContent = h;

  MolnifySDK.calculate([
    { cell: weightCell, value: w },
    { cell: heightCell, value: h }
  ]).then(function(data) {
    data.changes.forEach(function(c) {
      var v = cellToVar[c.cell];
      if (v === 'bmi') document.getElementById('result').textContent = c.value;
      if (v === 'category') document.getElementById('cat').textContent = c.value;
    });
  });
}

document.getElementById('w').addEventListener('input', recalc);
document.getElementById('h').addEventListener('input', recalc);
recalc();
```

---

## Metadata That Works in Headless Mode

| Metadata | Effect |
|----------|--------|
| `Headless` | Enables headless mode |
| `JavaScript` | Runs after SDK loads (your app code goes here) |
| `additionalJavaScript` | Appended after `JavaScript` (see tip below) |
| `CSS` | Injected as `<style>` in `<head>` |
| `additionalCSS` | Appended after `CSS` (see tip below) |
| `HeadHTML` | Raw HTML in `<head>` (CDN scripts, stylesheets) |
| `HeaderFont` / `BodyFont` | Google Fonts auto-loaded |
| `FaviconURL` | Custom favicon |
| `AppleTouchIconURL` | Custom Apple touch icon |
| `OnlyAppNameInPageTitle` | Controls page `<title>` format |
| `Users` / `SuperUsers` / `Managers` / `Realms` | Authentication and access control |
| `TokenAuthentication` | Token-based auth |
| `IpRanges` | IP-based access control |
| `CookieConsentPopup` | Cookie consent |

**Splitting large JavaScript or CSS across cells:** Excel cells have a 32,767-character limit. Custom frontends often exceed this. Use `additionalJavaScript` and `additionalCSS` to split content across two metadata cells — the values are concatenated at load time. For example, put your core framework code in `JavaScript` and your app-specific logic in `additionalJavaScript`. The same approach works in standard (non-headless) apps when templates provide base CSS/JS and individual apps need to extend it.

**Not used in headless mode:** `JavaScriptAfterLoad`, `JavaScriptAfterCalc`, `AutoCalcEnabled`, `EnabledForCalculate`, `EnabledForSave`, `EnabledForReset`, `EnabledForPrint`, `TopBannerHidden`, `HeaderHidden`, `InputPanelSmall`, `InputPanelFixed`, `PanelsFixed`, `OutputBoxPanelHidden`, color metadata (`TopBannerColor`, `ButtonColor`, `PanelHeaderColor`, etc.), `ScenarioTerm`, `Template`, and other UI-specific settings.

---

## Things to Watch Out For

**Response `changes` may not include `variable`.**
The calculate response returns `{cell, value, name}` - the `variable` field may or may not be present. Build a lookup map from `MolnifySDK.getAllVariables()` to translate cell references back to variable names.

**Charts require special handling.**
Chart data comes back in `data.charts[].valueObject`, not in `data.changes`. Parse the valueObject and render with a JS charting library (Chart.js, D3, etc.).

**Actions need all current values.**
When executing an action, send ALL current input values in `changes` - not just the dirty ones. Action property formulas (like `to: =B5` for email recipient) need the full input state to evaluate correctly. This differs from calculate, where you only send changed values.

**Autofill works, but getting the data to the frontend requires hidden outputs.**
Autofill runs server-side during `MolnifySDK.calculate()`, so named ranges are populated normally. However, the calculate response only returns output cell values - not raw named range contents. To access autofill data in your frontend, create hidden outputs that read from the named range (e.g. using `INDEX`, `TEXTJOIN`, or concatenation formulas) and expose them via `variable=`. Parse the output values in your JavaScript.

**Scenarios are not supported in headless mode.**
The scenario load/save/share UI is part of the standard frontend and there is no public API for it. If your app needs to persist user state, use database tables with `addrecord`/`insertrow` actions instead.

**`dateModified` changes on re-upload.**
The `window.molnify.dateModified` value is always fresh - no need to extract it manually. But be aware that the backend validates it and rejects stale values.

**Action responses (`aiprompt`, `http`) return data at `responsevalue`, not in `changes`.**
When executing an `aiprompt` or `http` action via `MolnifySDK.execute()`, the response body is at `resp.responsevalue` (top-level), not in `resp.changes[]`. The standard UI handles this automatically via `responseVariable`, but in headless mode you must read it explicitly:
```javascript
MolnifySDK.execute('analyzeData').then(function(resp) {
  var result = JSON.parse(resp.responsevalue);
  // Use result...
});
```

**Do not wrap `aiprompt` or `http` inside a `multiple` action if you need the response.**
The `multiple` wrapper consumes the `responsevalue` field, making it inaccessible to the caller — execute the action directly instead (see the Actions Reference for `skip`/`successJavaScript`).

**Dropdown options are not accessible via MolnifySDK.**
`MolnifySDK.getVariable()` and `MolnifySDK.getAllVariables()` return `{cell, name, value, variable, ui}` but NOT the options list for dropdowns. In headless mode, to populate dropdown UIs you must either inline the options in your JavaScript bundle, or create a hidden output that reads the options from a named range and expose it via `variable=`.
