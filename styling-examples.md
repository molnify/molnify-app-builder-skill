# Styling Examples

Layout recipes for Molnify apps. Each example includes JavaScript (for DOM rearrangement) and CSS.

See `styling.md` for DOM structure, selector reference, and the CSS Grid escape pattern.
See `design.md` for visual design principles — typography, color, hierarchy, and avoiding generic AI aesthetics. Read it before choosing fonts, colors, or layout direction.

## Reusable CSS Blocks

These blocks appear in most examples below. Copy what you need as a starting point.

**Output card grid override** — replaces Bootstrap's `.row` flex with CSS Grid inside the results panel:
```css
#outputboxpanel { background: transparent; border: none; box-shadow: none; overflow: visible; }
#outputboxpanel .panel-heading { display: none; }
#outputboxpanel .panel-body { padding: 0; }
#outputboxpanel .row {
  display: grid !important;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
  margin: 0;
}
#outputboxpanel .row::before, #outputboxpanel .row::after { display: none; }
#outputboxpanel [class*="col-"] {
  width: auto;
  max-width: none;
  padding: 0;
}
#outputboxpanel .widget { margin-bottom: 0; }
.widget-stats { border-radius: 10px; }
```

**Clean panel styling:**
```css
.panel { border: none; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.08); overflow: hidden; }
.panel-heading { border-radius: 12px 12px 0 0; }
```

**Light panel headers** — use when overriding the default dark headers. Note: `PanelHeaderColor` metadata injects `#molnifyAppBody .panel-heading { background-color: ... !important; }` (specificity 1-1-0). To beat it on specific panels, add `.panel` to the selector for 1-2-0:
```css
#inputpanel.panel .panel-heading { background-color: transparent !important; color: #333 !important; border-bottom: 1px solid #eee; }
#inputpanel .panel-title { color: inherit; }
```

**Strip Bootstrap grid classes** (JS) — the universal escape pattern from `styling.md`:
```javascript
$('#leftColumn, #rightColumn').removeClass(function(i, c) {
  return (c.match(/\bcol-\S+/g) || []).join(' ');
});
$('#boxRow').removeClass('row');
```

---

## Bootstrap-Based Layouts

These use BS3 class swapping — simpler but limited to 12ths.

**Tip:** For a narrower input panel without JavaScript, set `InputPanelSmall: TRUE` in metadata (gives 33%/67% split).

### Full-Width Dashboard with Compact Input Bar

Inputs in a horizontal bar at top, charts and outputs below full-width.

```javascript
JavaScriptAfterLoad:
$('#leftColumn').removeClass('col-md-6 col-md-4').addClass('col-md-12');
$('#rightColumn').removeClass('col-md-6 col-md-8').addClass('col-md-12');
$('#inputpanel .panel-heading').hide();
calculateButton();
```
```css
CSS:
body { background: #f0f2f5; }

/* Compact horizontal inputs */
#inputpanel { background: white; border-radius: 12px; margin-bottom: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.08); }
#inputpanel .panel-body { padding: 15px 20px; }
#inputpanel form { display: flex; flex-wrap: wrap; gap: 20px; align-items: flex-end; }
#inputpanel .form-group { margin: 0; flex: 1; min-width: 200px; }
#inputpanel .control-label { font-size: 12px; }

/* Apply output card grid override and clean panel styling from above */
```

### Full-Width Metrics Above Inputs

Metrics span full width at top, narrow inputs + charts below. Set `InputPanelSmall: TRUE` in metadata for the 33%/67% split — don't re-swap the column classes in JS to get a width Molnify already provides.

```javascript
JavaScriptAfterLoad:
var metricsRow = $('<div class="row"><div class="col-md-12" id="metricsCol"></div></div>');
metricsRow.insertBefore('#boxRow');
$('#outputboxpanel').appendTo('#metricsCol');
calculateButton();
```
```css
CSS:
body { background: #f0f2f5; }

/* Output card grid override with fixed 4-column layout */
#outputboxpanel .row {
  display: grid !important;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin: 0;
}
/* Apply remaining output card overrides and clean panel styling from above */

/* Light input panel heading — use .panel to beat Molnify's PanelHeaderColor specificity */
#inputpanel.panel .panel-heading { background-color: transparent !important; color: #333 !important; border-bottom: 1px solid #e0e0e0; }
#inputpanel .panel-title { color: inherit; }

@media (max-width: 768px) {
  #outputboxpanel .row { grid-template-columns: 1fr; }
}
```

### Hero Metric

Make the first output card span full width with large text.

```javascript
JavaScriptAfterLoad:
$('#outputboxpanel .outputbox:first').addClass('hero-metric');
```
```css
CSS:
/* Adapt the background to your app's palette */
.hero-metric {
  grid-column: 1 / -1;
  background: var(--primary-dark, #1a3a4a) !important;
  color: white;
  padding: 40px !important;
  text-align: center;
  border-radius: 10px;
}
.hero-metric p.outputBoxValue { font-size: 3.5em; font-weight: 700; }
.hero-metric h4.boxName { font-size: 1.2em; opacity: 0.85; }
```

### Centered Single-Column

Good for form-focused apps and reports.

```javascript
JavaScriptAfterLoad:
$('#leftColumn, #rightColumn').removeClass('col-md-4 col-md-6 col-md-8').addClass('col-md-8 col-md-offset-2');
$('#rightColumn').insertAfter('#leftColumn .panel');
```
```css
CSS:
#appHeaderRow { max-width: 66.667%; margin: 0 auto; padding: 0 15px; }
#boxRow { display: block; }
#leftColumn, #rightColumn { float: none; margin: 0 auto 20px; }
```

### Full-Width Charts Above Inputs

Move all chart panels above the input/output area.

```javascript
JavaScriptAfterLoad:
var chartRow = $('<div class="row chart-row"></div>');
var chartCol = $('<div class="col-md-12"></div>');
$('#rightColumn .panel').appendTo(chartCol);
chartCol.appendTo(chartRow);
chartRow.insertBefore('#boxRow');
$('#leftColumn').removeClass('col-md-6 col-md-4').addClass('col-md-12');
$('#rightColumn').removeClass('col-md-6 col-md-8').addClass('col-md-12');
calculateButton();
```

### Horizontal Input Bar (Wizard-Style)

Inputs inline on one row.

```javascript
JavaScriptAfterLoad:
$('#leftColumn').removeClass('col-md-6 col-md-4').addClass('col-md-12');
$('#rightColumn').removeClass('col-md-6 col-md-8').addClass('col-md-12');
$('#inputpanel .panel-heading').hide();
calculateButton();
```
```css
CSS:
#inputpanel form { display: flex; flex-wrap: wrap; gap: 16px; align-items: flex-end; }
#inputpanel .form-group { flex: 0 0 auto; min-width: 150px; margin: 0; }
```

### Kiosk / Presentation Mode

Dark theme, no chrome. Good for wall-mounted dashboards.

```javascript
JavaScriptAfterLoad:
$('#header, #appHeaderRow, #inputpanel .panel-heading').hide();
```
```css
CSS:
.page-header-fixed { padding-top: 0; }
#page-container { background: #1c1f26; }

#molnifyAppHtml .panel { background: #262a33; border: none; border-radius: 10px; }
#molnifyAppHtml .panel .panel-heading { background: #2e3340 !important; color: #c8cdd5 !important; border-radius: 10px 10px 0 0 !important; }
#molnifyAppHtml .control-label, #molnifyAppHtml .input-label { color: #c8cdd5; }
.outputbox .widget-stats { background: #262a33 !important; }
.outputbox h4.boxName { color: #8b919d; }
.outputbox p.outputBoxValue { color: #e8eaed; font-size: 2em; }

/* Chart colors for dark background */
.nvd3 .nv-axis line, .nvd3 .nv-axis path { stroke: #3a3f4b; }
.nvd3 text { fill: #8b919d !important; }

/* Apply output card grid override from above */
```

### Split View with Sticky Inputs

Input panel stays fixed while outputs scroll. Works best with apps that have enough output content (charts, tables) to require scrolling.

```css
CSS:
#leftColumn {
  position: sticky;
  top: 70px;
  height: calc(100vh - 90px);
  overflow-y: auto;
}

/* Light panel headers (see reusable block above) */
#inputpanel.panel .panel-heading { background-color: transparent !important; color: #333 !important; border-bottom: 1px solid #e0e0e0; }
#inputpanel .panel-title { color: inherit; }

/* Apply output card grid override from above */
```

### Borderless / Minimal

All panel chrome stripped. Hierarchy from typography and whitespace only. Inputs use underline style, outputs are large numbers with thin dividers. Chart moves to full width below both columns.

```javascript
JavaScriptAfterLoad:
$('#leftColumn').removeClass('col-md-6 col-md-4').addClass('col-md-5');
$('#rightColumn').removeClass('col-md-6 col-md-8').addClass('col-md-7');
var chartRow = $('<div class="chart-row"></div>');
$('#rightColumn .panel:not(#outputboxpanel)').appendTo(chartRow);
chartRow.insertAfter('#boxRow');
calculateButton();
```
```css
CSS:
body { background: #f7f5f2; }

/* Strip all panel chrome — scoped to app area */
#molnifyAppHtml .panel {
  background: transparent !important; border: none !important;
  box-shadow: none !important; border-radius: 0 !important;
}
#molnifyAppHtml .panel-heading { display: none !important; }
#molnifyAppHtml .panel-body { padding: 0 !important; }

/* Column gap */
#boxRow { padding: 0 24px; }
#leftColumn { padding-right: 32px !important; }
#rightColumn { padding-left: 32px !important; }

/* Header - minimal */
#appHeaderRow { background: transparent; border: none; margin-bottom: 32px; }
h1#appHeader { font-size: 32px; color: #2a2a2a; font-weight: 400; letter-spacing: -0.5px; }

/* Inputs - underline style */
#inputpanel .form-group { margin-bottom: 24px; }
#inputpanel .panel-body { padding-top: 20px !important; }
#inputpanel .control-label, #inputpanel .input-label {
  font-size: 11px; text-transform: uppercase; letter-spacing: 1px;
  color: #8b8178; font-weight: 600; margin-bottom: 8px;
}
#inputpanel .form-control {
  border: none; border-bottom: 1px solid #d4cdc4; border-radius: 0;
  background: transparent; padding: 8px 8px; font-size: 18px; color: #2a2a2a;
  box-shadow: none;
}
#inputpanel .form-control:focus { border-bottom-color: #8b7355; box-shadow: none; }
.btn-primary, .btn-success { background: #8b7355; border: none; border-radius: 4px; }

/* Output metrics - large typography, no cards */
#outputboxpanel .row { display: flex !important; flex-direction: column; }
#outputboxpanel .row::before, #outputboxpanel .row::after { display: none; }
#outputboxpanel [class*="col-"] { width: auto; max-width: none; padding: 0; }
#outputboxpanel .widget { margin-bottom: 0; }
#outputboxpanel .widget-stats {
  background: transparent !important; border-radius: 0;
  border-bottom: 1px solid #e8e2da; padding: 20px 0 !important;
}
#outputboxpanel .widget-stats h4.boxName {
  font-size: 11px; text-transform: uppercase; letter-spacing: 1px;
  color: #8b8178; margin-bottom: 4px;
}
#outputboxpanel .widget-stats p.outputBoxValue { font-size: 36px; color: #2a2a2a; font-weight: 300; }
#outputboxpanel .widget-stats .fa { color: #8b7355; }

/* Chart - full width below columns */
.chart-row { padding: 0 24px; margin-top: 24px; border-top: 1px solid #e8e2da; padding-top: 16px; }

.chart-series0 { color: #8b7355; }
.chart-series1 { color: #d4cdc4; }

@media (max-width: 768px) {
  #leftColumn, #rightColumn { width: 100% !important; padding: 0 16px !important; }
  h1#appHeader { font-size: 24px; }
}
```

### Toolbar + Canvas

Inputs compressed into a dark horizontal toolbar, metrics inline below, one large chart filling the rest. Top banner hidden. Feels like a tool, not a form.

Uses `TopBannerHidden: TRUE` metadata. Select2 dropdowns need explicit dark styling — the dropdown results are appended to `<body>`, not inside the app DOM, so they can't be scoped to `#molnifyAppHtml`.

Outputs don't support `prefix`/`postfix` — use `="$"&TEXT(ROUND(...), "#,##0")` in the formula to include units.

```javascript
JavaScriptAfterLoad:
$('#leftColumn').removeClass('col-md-6 col-md-4').addClass('col-md-12');
$('#rightColumn').removeClass('col-md-6 col-md-8').addClass('col-md-12');
$('#inputpanel .panel-heading').hide();
calculateButton();
```
```css
CSS:
body { background: #09090b; color: #fafafa; margin: 0; }
#appHeaderRow { display: none; }

/* Toolbar input bar */
#inputpanel { background: #18181b !important; border: none; border-radius: 0; border-bottom: 1px solid #27272a; }
#inputpanel .panel-heading { display: none; }
#inputpanel .panel-body { padding: 12px 24px !important; }
#inputpanel form { display: flex; flex-wrap: wrap; gap: 16px; align-items: center; }
#inputpanel .form-group { flex: 0 0 auto; margin: 0; min-width: 250px; }
#inputpanel .form-group > .col-sm-4 { width: 50%; }
#inputpanel .form-group > .col-sm-8 { width: 50%; }
#inputpanel .control-label, #inputpanel .input-label {
  font-size: 10px; text-transform: uppercase; letter-spacing: 0.5px;
  color: #71717a; margin-bottom: 2px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}
#inputpanel .form-control {
  background: #27272a; border: 1px solid #3f3f46; border-radius: 6px;
  color: #fafafa; padding: 6px 12px; font-size: 13px;
}
#inputpanel .form-control:focus { border-color: #a1a1aa; box-shadow: none; }
/* Select2 dark theme — dropdown appended to body, can't scope further */
.select2-dropdown { background: #27272a; border-color: #3f3f46; }
.select2-results__option { color: #fafafa; }
.select2-container--default .select2-results__option--highlighted[aria-selected] { background: #3f3f46; color: #fafafa; }
#inputpanel .select2-container--default .select2-selection--single { background: #27272a; border: 1px solid #3f3f46; border-radius: 6px; }
#inputpanel .select2-container--default .select2-selection--single .select2-selection__rendered { color: #fafafa; }
#inputpanel .select2-container--default .select2-selection--single .select2-selection__arrow b { border-color: #a1a1aa transparent transparent transparent; }
#molnifyAppHtml .btn-primary, #molnifyAppHtml .btn-success { background: #3f3f46; border: 1px solid #52525b; color: #fafafa; border-radius: 6px; font-size: 13px; }

/* Output metrics - horizontal inline bar */
#outputboxpanel { background: #18181b !important; border: none !important; box-shadow: none; border-radius: 0; border-bottom: 1px solid #27272a !important; }
#outputboxpanel .panel-heading { display: none; }
#outputboxpanel .panel-body { padding: 8px 24px !important; }
#outputboxpanel .row { display: flex !important; gap: 32px; margin: 0; }
#outputboxpanel .row::before, #outputboxpanel .row::after { display: none; }
#outputboxpanel [class*="col-"] { width: auto; max-width: none; padding: 0; flex: 0 0 auto; }
#outputboxpanel .widget { margin-bottom: 0; }
#outputboxpanel .widget-stats { background: transparent !important; border-radius: 0; padding: 4px 0 !important; }
#outputboxpanel .widget-stats .stats-icon { display: none; }
#outputboxpanel .widget-stats .stats-info { display: flex; align-items: baseline; gap: 8px; }
#outputboxpanel .widget-stats h4.boxName { font-size: 10px; text-transform: uppercase; letter-spacing: 0.5px; color: #71717a; margin: 0; }
#outputboxpanel .widget-stats p.outputBoxValue { font-size: 18px; color: #fafafa; margin: 0; font-weight: 500; }

/* Canvas - full remaining space for chart */
#rightColumn > .panel { background: #09090b; border: none; border-radius: 0; margin: 0; }
#rightColumn > .panel .panel-heading {
  background: transparent !important; color: #a1a1aa !important;
  border: none; padding: 16px 24px 0;
  font-size: 11px; text-transform: uppercase; letter-spacing: 0.5px;
}
#rightColumn > .panel .panel-body { padding: 0 24px 24px; }
#rightColumn > .panel .chart { min-height: 450px; }

.chart-series0 { color: #22c55e; }
.chart-series1 { color: #3f3f46; }
.nvd3 .nv-axis line, .nvd3 .nv-axis path { stroke: #27272a; }
.nvd3 text { fill: #71717a !important; }

@media (max-width: 768px) {
  #inputpanel form { gap: 8px; }
  #inputpanel .form-group { flex: 1 1 45%; }
}
```

### Small CSS Tweaks

**Cards with shadows and rounded corners:**
```css
.panel { border: none; border-radius: 16px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1), 0 2px 4px -1px rgba(0,0,0,0.06); overflow: hidden; }
.panel-heading { border-radius: 16px 16px 0 0; }
.outputbox { border-radius: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
```

**Responsive mobile-first adjustments:**
```css
@media (max-width: 768px) {
  #leftColumn, #rightColumn { width: 100% !important; padding: 0 10px; }
  .hero-section { padding: 30px 15px; }
}
```

---

## CSS Grid Layouts

These use the universal escape pattern (strip BS3 grid, apply CSS Grid on `#boxRow`). All require the "Strip Bootstrap grid classes" JS from the top of this file.

**Important when using CSS Grid:**
- Charts/tables need explicit `rightColumn` or `leftColumn` UI options — default panel alternation breaks in Grid layouts.
- Call `calculateButton()` at the end of `JavaScriptAfterLoad` — NVD3 charts compute dimensions on render and need a redraw after DOM restructuring.

### Three-Column Layout

Inputs | Charts | Summary metrics. Impossible with BS3 class swapping.

```javascript
JavaScriptAfterLoad:
// Strip BS3 grid (see top of file)
// Create a third column for summary metrics
var summaryCol = $('<div id="summaryColumn"></div>');
$('#outputboxpanel').appendTo(summaryCol);
summaryCol.insertAfter('#rightColumn');
calculateButton();
```
```css
CSS:
body { background: #f8f9fb; }

#boxRow {
  display: grid !important;
  grid-template-columns: 400px 1fr 280px;
  gap: 20px;
  padding: 0 20px;
}
#leftColumn, #rightColumn, #summaryColumn {
  width: auto !important; max-width: none !important;
  float: none !important; padding: 0 !important;
}

/* Inputs - compact sidebar */
#inputpanel { border-radius: 10px; border: 1px solid #e2e5ea; box-shadow: none; }
#inputpanel .panel-heading { background: #f8f9fb !important; color: #374151 !important; font-size: 0.85em; text-transform: uppercase; letter-spacing: 0.5px; }

/* Summary metrics - vertical stack in right column */
#outputboxpanel { background: transparent; border: none; box-shadow: none; }
#outputboxpanel .panel-heading { display: none; }
#outputboxpanel .row { display: flex !important; flex-direction: column; gap: 12px; }
#outputboxpanel [class*="col-"] { width: auto; padding: 0; }
#outputboxpanel .widget-stats { border-radius: 10px; box-shadow: 0 1px 4px rgba(0,0,0,0.06); }

/* Charts + panels - clean styling */
.panel { border: none; border-radius: 10px; box-shadow: 0 1px 4px rgba(0,0,0,0.06); }
.panel-heading { background: white !important; color: #374151 !important; border-bottom: 1px solid #f0f0f0; font-size: 0.85em; text-transform: uppercase; letter-spacing: 0.5px; }

@media (max-width: 1024px) { #boxRow { grid-template-columns: 1fr; } }
```

### Data-Entry Focused

Wide centered form, results below. For forms, surveys, data capture.

```javascript
JavaScriptAfterLoad:
// Strip BS3 grid (see top of file)
calculateButton();
```
```css
CSS:
body { background: #fafbfc; }

#boxRow {
  display: grid !important;
  grid-template-columns: 1fr;
  gap: 24px;
  max-width: 800px;
  margin: 0 auto;
  padding: 0 20px;
}

/* Wide input form */
#inputpanel { border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.06); border: none; }
#inputpanel .panel-heading { display: none; }
#inputpanel .panel-body { padding: 32px; }
#inputpanel .form-group { margin-bottom: 20px; }
#inputpanel .form-group label { font-weight: 600; color: #1f2937; margin-bottom: 6px; }
#inputpanel .form-control { border-radius: 8px; border: 1px solid #d1d5db; padding: 10px 14px; font-size: 15px; }
#inputpanel .form-control:focus { border-color: #475569; box-shadow: 0 0 0 3px rgba(71,85,105,0.1); }

/* Section dividers (when using dividerName on inputs) */
#inputpanel legend[id^="divider-"] {
  background: #edf0f4; margin: 0 -32px 16px; padding: 14px 32px;
  border-bottom: 1px solid #dde1e7; border-top: 1px solid #dde1e7;
  font-weight: 600; font-size: 14px; color: #374151; width: auto;
}
#inputpanel legend[id^="divider-"]:first-of-type {
  margin-top: -32px; border-top: none; border-radius: 12px 12px 0 0;
}

/* Apply output card grid override from top of file */
```

### Tabbed Dark Dashboard

Read-only dashboard, inputs hidden, dark theme.

```javascript
JavaScriptAfterLoad:
// Strip BS3 grid (see top of file)
$('#leftColumn').hide();
var metricsRow = $('<div id="metricsRow"></div>');
$('#outputboxpanel').appendTo(metricsRow);
metricsRow.insertBefore('#boxRow');
calculateButton();
```
```css
CSS:
body { background: #0f172a; color: #e2e8f0; }

#boxRow {
  display: grid !important;
  grid-template-columns: 1fr;
  gap: 20px;
  padding: 0 24px;
}
#leftColumn { display: none; }
#rightColumn { width: auto !important; float: none !important; padding: 0 !important; }

/* Top metrics bar */
#metricsRow { padding: 0 24px 8px; }
#outputboxpanel { background: transparent; border: none; box-shadow: none; overflow: visible; }
#outputboxpanel .panel-heading { display: none; }
#outputboxpanel .panel-body { padding: 0; }
#outputboxpanel .row {
  display: grid !important;
  grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
  gap: 16px; margin: 0;
}
#outputboxpanel .row::before, #outputboxpanel .row::after { display: none; }
#outputboxpanel [class*="col-"] { width: auto; padding: 0; }
#outputboxpanel .widget { margin-bottom: 0; }
#outputboxpanel .widget-stats { background: #1e293b; border-radius: 10px; border: 1px solid #334155; }
#outputboxpanel h4.boxName { color: #94a3b8; }
#outputboxpanel p.outputBoxValue { color: #f1f5f9; }

/* Dark chart panels — scope to #molnifyAppHtml to avoid affecting admin sidebar */
#molnifyAppHtml .panel { background: #1e293b; border: 1px solid #334155; border-radius: 10px; }
#molnifyAppHtml .panel-heading { background: transparent !important; color: #e2e8f0 !important; border-bottom: 1px solid #334155; }

/* Header */
#appHeaderRow { background: #0f172a; border-bottom: 1px solid #1e293b; margin-bottom: 16px; }
h1#appHeader { color: #f1f5f9; }
.btn { background: #334155; color: #e2e8f0; border: 1px solid #475569; }
.btn:hover { background: #475569; }

/* Mobile navbar */
@media (max-width: 768px) { .navbar-header { border-bottom: none !important; } }
```

### Asymmetric Grid

Inputs + 3 metric cards on top row, charts spanning full width below.

```javascript
JavaScriptAfterLoad:
// Strip BS3 grid (see top of file)
// Prepend (not append) so inputs+metrics appear before charts in DOM
$('#leftColumn .panel').add('#outputboxpanel').prependTo('#rightColumn');
$('#leftColumn').hide();
$('#rightColumn').addClass('dashboard-grid');
calculateButton();
```
```css
CSS:
body { background: #f1f5f9; }

.dashboard-grid {
  display: grid !important;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  width: auto !important; float: none !important; padding: 0 20px !important;
}

/* Input panel - 1 column */
.dashboard-grid > #inputpanel { grid-column: span 1; border-radius: 10px; border: none; box-shadow: 0 1px 4px rgba(0,0,0,0.06); }
.dashboard-grid > #inputpanel .panel-heading { display: none; }

/* Metric cards - 3 columns */
.dashboard-grid > #outputboxpanel { grid-column: span 3; background: transparent; border: none; box-shadow: none; overflow: visible; }
#outputboxpanel .panel-heading { display: none; }
#outputboxpanel .panel-body { padding: 0; }
#outputboxpanel .row {
  display: grid !important;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px; margin: 0;
}
#outputboxpanel .row::before, #outputboxpanel .row::after { display: none; }
#outputboxpanel [class*="col-"] { width: auto; padding: 0; }
#outputboxpanel .widget { margin-bottom: 0; }
#outputboxpanel .widget-stats { border-radius: 10px; box-shadow: 0 1px 4px rgba(0,0,0,0.06); }

/* Chart panels - full width */
.dashboard-grid > .panel {
  grid-column: 1 / -1;
  border: none; border-radius: 10px; box-shadow: 0 1px 4px rgba(0,0,0,0.06);
}
.dashboard-grid > .panel .panel-heading { background: white !important; color: #374151 !important; border-bottom: 1px solid #f0f0f0; }

@media (max-width: 900px) {
  .dashboard-grid { grid-template-columns: 1fr; }
  .dashboard-grid > #outputboxpanel { grid-column: span 1; }
  #outputboxpanel .row { grid-template-columns: 1fr; }
}
```
