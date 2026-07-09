# Advanced Topics

Companion to the main reference. Contains JavaScript runtime details, DOM lifecycle, and tips not covered in the main reference.

---

## Tips & Patterns

### Custom Action Buttons
Create custom buttons using either HTML outputs or `infotext` inputs:

**Two approaches:**
- **HTML output** (`UI: html`) - Button can be dynamic (formula-driven value)
- **Infotext input** (`UI: infotext`) - Button is static (value cannot be a formula)

**Implementation:**
1. Create the actual action with `hidden: True` so the default button doesn't show
2. Give the action a descriptive `name` property
3. Create HTML containing a button that calls `performActionWithName()`:
```html
<a href="javascript:performActionWithName('myActionName');"><button class="btn btn-success">My Button</button></a>
```

**Use cases:**
- Show buttons only on specific tabs (default action buttons appear on all tabs)
- Run JavaScript before/after the action
- Apply custom button styling

### Dynamic Dropdown Lists
Create dependent dropdowns (e.g., category -> subcategory):
1. Create named ranges for each category's options
2. Use INDIRECT formula to select the correct range based on first dropdown
3. Apply data validation using the INDIRECT formula

### Custom Save Scenario Buttons
Instead of using the built-in save button:
1. Create a `scenariosave` action
2. Use formula to auto-generate scenario name (e.g., based on date/user)
3. Style as needed with custom button

### Run JavaScript on Action Success
Use `successJavaScript` to execute JavaScript after an action completes:
```
successJavaScript: alert('Saved as ID: ' + getValueForVariable('recordId'))
```

Legacy alternative: `successHTMLElementContent` with `<script>` tags also works but requires a target element:
```
successHTMLElementId: myElement
successHTMLElementContent: <script>window.myCounter++; setValueForVariable('counter', window.myCounter);</script>
```

### URL Parameters as Variables
Pass values via URL using variables:
1. Create input with `UI: variable=myParam;hidden`
2. Access app with `?myParam=value`
3. The input will be populated with the URL parameter value

### Iframe Communication
Embed Molnify apps within other Molnify apps:
- Use `parent.calculateButton()` from inner app to trigger outer app recalculation
- Use `successHTMLElementContent` to communicate between apps
- JavaScript can access variables across iframes on same domain

---

## Limitations & Workarounds
- **UNIQUE formula** not supported - use workaround formulas (note: doesn't scale well for large datasets, consider database for large data)
- **Limited sliders** - use `range` UI type instead of JavaScript workarounds
- **Complex layouts** - use HTML outputs with custom CSS

## Dynamic UI Strings with Formulas
UI options can be built dynamically using formulas:
```
UI: =E3&";"&"placeholder="&F3
```
This allows settings to be driven by cell values.

## Auto-Refresh Dashboards
Use `calcTimerSeconds` metadata to recalculate automatically at a fixed interval:
```
calcTimerSeconds: 30
```
This calls `calculateButton()` every 30 seconds. Minimum value is 0.5.

## Scenario Name Variable
Access the current scenario name:
```
UI: variable=molnifyCurrentScenario;hidden
```
Use with `oldName` in ScenarioSave action to update existing scenarios.

## Silent HTTP Requests
Use `requestHandler: nomodal` to suppress the loading modal during HTTP actions.

## Expand Comma-Separated Values
Parse comma-separated values into separate cells (useful with `multiple` select):
```
=TRIM(MID(SUBSTITUTE($B$4,",",REPT(" ",LEN($B$4))), (ROW()-7)*LEN($B$4)+1, LEN($B$4)))
```
Copy this formula down for each item position.

---

## DOM Lifecycle & Output Re-rendering

Understanding when Molnify replaces output DOM is critical for any app that uses JavaScript to modify outputs (adding buttons, making cells editable, attaching event handlers, etc.).

### What happens on each calculation

When a calculation runs (via auto-calc, `calculateButton()`, or action with `successCalculate: TRUE`):

1. The backend evaluates all formulas and returns changed values
2. **Tables** (`<table>` elements): The `<thead>` and `<tbody>` innerHTML are **fully replaced** with fresh HTML generated from the new data. All child elements (rows, cells) are new DOM nodes. Any attributes, event handlers, or injected elements you added to table cells are gone.
3. **Output boxes** (text/number outputs): Updated **in-place** - only the `innerHTML` of the individual output element changes, and only if the value actually changed. The parent elements remain.
4. **Charts**: Data is updated and the chart is redrawn via NVD3.
5. `JavaScriptAfterCalc` runs after all updates are applied.

The critical implication for tables: **any DOM modifications you made to `<thead>` or `<tbody>` will be lost on the next calculation** - added columns, event handlers, CSS classes, `contenteditable` attributes, injected buttons - all gone.

### The idempotency rule

Any function that runs in `JavaScriptAfterCalc` and modifies table DOM must be **idempotent** - it must produce the correct result on a freshly rebuilt table.

Since tables are fully rebuilt on each calculation, you don't need cleanup - you're always working with a fresh table. But if you also modify non-table output DOM, that content persists between calculations, so you must handle both cases:

```javascript
JavaScriptAfterCalc:
// Tables: no cleanup needed - thead/tbody are already fresh
$('.out-table tbody tr').each(function() {
  $(this).append('<td class="js-actions-col"><button class="btn btn-xs btn-info">View</button></td>');
});

// Non-table outputs: clean up first since the element persists
$('#my-output .js-badge').remove();
$('#my-output').append('<span class="js-badge">New</span>');
```

### When NOT to enhance table DOM

If your app needs interactive tables (inline editing, row-level action buttons, drag-to-reorder), you are creating **client-side state inside server-owned DOM**. Every calculation cycle will rebuild the table and destroy your state. This leads to cascading bugs: lost edit state, broken event handlers, and missing injected elements.

Instead, use one of these approaches:

| Need | Recommended approach | See |
|------|---------------------|-----|
| View records, click to edit in a form | Master-Detail pattern | `patterns.md` |
| Full inline editing, custom table interactions | Custom frontend (own the entire DOM) | `custom-frontend.md` |
| Simple read-only table with click handlers | `JavaScriptAfterCalc` (safe - table is fresh each time) | Example above |

See the "Choosing a Pattern" section in `patterns.md` for a full decision tree.

---

## Calling setValueForVariable Multiple Times

When `AutoCalcEnabled` is TRUE (the default), `setValueForVariable()` eventually triggers `autoCalc()`, which calls `calculateButton()`. However, for text, number, and textarea inputs, there is a **200ms debounce timer** - rapid sequential calls are batched, and only one calculation runs after the last call.

This means calling `setValueForVariable()` several times in a row (as the Master-Detail pattern does) is fine for text/number inputs:
```javascript
// These are debounced - only one calculation runs ~200ms after the last call
setValueForVariable('name', $cells.eq(1).text().trim());
setValueForVariable('email', $cells.eq(2).text().trim());
setValueForVariable('phone', $cells.eq(3).text().trim());
```

**Exception - dropdowns, checkboxes, and option sets:** These input types call `autoCalc()` immediately (no debounce), so each `setValueForVariable()` triggers a separate calculation. There is no clean workaround for this - each dropdown/checkbox update goes through `autoCalc` which both marks the input as dirty (so the backend sees the change) and triggers `calculateButton()`. If you need to set multiple dropdowns at once and the extra calculations are a problem, consider restructuring the app so that fewer dropdown values need to be set simultaneously.

**Apps with `AutoCalcEnabled: FALSE`:** `setValueForVariable()` never triggers calculation automatically, so you can call it as many times as needed and then call `calculateButton()` once.

---

## JavaScript Execution & Error Handling

### Execution entry points

Molnify has several JavaScript entry points, each with different timing and injection methods:

| Entry point | When it runs | How it's injected |
|-------------|--------------|-------------------|
| `JavaScript` (metadata) | Page load, early - before DOM is fully interactive | `<script>` tag in page |
| `JavaScriptAfterLoad` (metadata) | Page load, late - after DOM init, input setup, and scenario dropdown init | Inline in `$(document).ready()` |
| `JavaScriptAfterCalc` (metadata) | After every calculation - inside `afterCalc()`, after all output values are updated | Embedded in `afterCalc()` function body |
| `jsOnChange` (UI option) | After the specific input/output value changes | If a global function with that name exists, called via `window[name].apply()`. Otherwise, `eval()`. |
| `successHTMLElementContent` (action) | After an action succeeds | Injected via jQuery `.html()`, which **does** execute inline `<script>` tags |

### Error handling

**None of these entry points have try/catch wrappers.** If your JavaScript throws an error:

- The error is logged to the browser console
- Execution of that specific script stops
- The app continues working - UI updates happen *before* JS runs, so the app state is already consistent
- Other entry points are unaffected (e.g., a broken `jsOnChange` on one input won't prevent `JavaScriptAfterCalc` from running)

### Inline `<script>` in HTML outputs

HTML outputs (cells with `UI: html`) are updated via native `innerHTML` assignment, which does **not** execute `<script>` tags. If you need to run JS when an output updates, use `jsOnChange` instead.

The exception is `successHTMLElementContent` in actions - this uses jQuery's `.html()` method, which **does** execute `<script>` tags. This is why the pattern works:
```
successHTMLElementContent: <script>setValueForVariable('status', 'done');</script>
```

### jsOnChange restrictions

The `jsOnChange` value is stored as an HTML `data-jsOnChange` attribute on the DOM element. This means:
- **No semicolons** in the value (use a named function instead)
- **No apostrophes** (use double quotes or a named function)
- For anything beyond a simple expression, define a function in `JavaScript` or `JavaScriptAfterLoad` metadata and reference it by name

```
// Simple - works directly:
jsOnChange=handleAgeChange

// Complex - define function in JavaScript metadata, reference by name:
JavaScript: function handleAgeChange(el) { var v = getValueForVariable('age'); if (v > 120) setValueForVariable('age', 120); }
```

### Debugging tips

1. **Open browser DevTools** - Press F12 (or Cmd+Option+I on Mac), check Console tab for errors
2. **Use `console.log()`** for tracing:
   ```javascript
   JavaScriptAfterCalc: console.log('calc done, val =', getValueForVariable('myVar'));
   ```
3. **Test in the browser console first** - Paste your JS into DevTools to verify it works before embedding in metadata

### Common pitfalls

| Problem | Cause | Fix |
|---------|-------|-----|
| DOM manipulation does nothing | Using `JavaScript` metadata (runs before DOM is ready) | Move to `JavaScriptAfterLoad` |
| Empty string check fails | Empty Molnify cells return `'\u00A0'` (non-breaking space), not `''` | Check `if (val !== '\u00A0')` |
| `getValueForVariable()` returns `undefined` | No input/output has `variable=X` matching that name | Verify `UI: variable=X` is set, check spelling/case |
| `performActionWithName()` silently fails | No action has `name: X` (case-sensitive) | Verify the action's `name` property matches exactly |
| Infinite calc loop (app freezes) | `setValueForVariable()` in `JavaScriptAfterCalc` re-triggers auto-calc | Guard: `if (current !== desired) setValueForVariable(...)` |

---

## Troubleshooting

### Input not showing
- Check if `hidden` is set in UI
- Check conditional display (`showIfVariable`/`showIfValue`) conditions
- Verify the cell color is green (for inputs)

### Action not executing
- Verify all required properties are set
- Check `showIfCell`/`showIfValue` conditions on the action
- Check browser console for JavaScript errors

### Chart not rendering
- Verify ONLY data value cells are colored blue (not headers, labels, or title)
- Verify the chart type is spelled correctly in the UI cell
- Check that data format matches expected structure (title row, then data rows)

### JavaScript can't find table elements
Molnify tables render with `<td>` elements in `<thead>` (not `<th>`) - target `$('.out-table thead td')`. Full table DOM is in `styling.md`.

### Validation not working
- Validation rules are case-sensitive
- Ensure proper syntax (e.g., `>0` not `> 0`)

### Scenarios not saving
- `EnabledForSave` must be TRUE in metadata
- User must be logged in (unless app allows anonymous)
- Check that `scenariosave` action has `newName` property
