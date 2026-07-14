# Styling Examples

Layout recipes for Molnify apps. Each example includes JavaScript (for DOM rearrangement) and CSS.

See `styling.md` for DOM structure, selector reference, and the CSS Grid escape pattern.
See `design.md` for visual design principles - typography, color, hierarchy, and avoiding generic AI aesthetics. Read it before choosing fonts, colors, or layout direction.

## Reusable CSS Blocks

These blocks appear in most examples below. Copy what you need as a starting point.

**Output card grid override** - the core `#outputboxpanel` CSS Grid override is in `styling.md` under "Overriding Bootstrap inside panels". The recipes below combine it with this panel-chrome removal so the cards sit directly on the page:
```css
#outputboxpanel { background: transparent; border: none; box-shadow: none; overflow: visible; }
#outputboxpanel .panel-heading { display: none; }
#outputboxpanel .panel-body { padding: 0; }
.widget-stats { border-radius: 10px; }
```

**Clean panel styling:**
```css
.panel { border: none; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.08); overflow: hidden; }
.panel-heading { border-radius: 12px 12px 0 0; }
```

**Light panel headers** - use when overriding the default dark headers. Note: `PanelHeaderColor` metadata injects `#molnifyAppBody .panel-heading { background-color: ... !important; }` (specificity 1-1-0). To beat it on specific panels, add `.panel` to the selector for 1-2-0:
```css
#inputpanel.panel .panel-heading { background-color: transparent !important; color: #333 !important; border-bottom: 1px solid #eee; }
#inputpanel .panel-title { color: inherit; }
```

**Strip Bootstrap grid classes** (JS) - use the universal escape pattern JS from `styling.md` ("Breaking Out of the Bootstrap 3 Grid"). Recipes below reference it as "Strip BS3 grid".

**Stack columns full-width** (JS) - drop the default 50/50 split so the input column spans full width on top and the output/chart column spans full width below, and hide the input-panel heading. Inputs can be arranged horizontally by CSS, but that is not done here:
```javascript
$('#leftColumn').removeClass('col-md-6 col-md-4').addClass('col-md-12');
$('#rightColumn').removeClass('col-md-6 col-md-8').addClass('col-md-12');
$('#inputpanel .panel-heading').hide();
calculateButton();
```

---

## Skins & modifiers

These layer onto any layout below - apply them on top of a base layout's CSS.

### Dark theme

A dark palette that composes onto any layout - drop it into the `CSS` metadata. Use it when the context calls for it (wall display, kiosk, focused tool), not as a default - see `design.md` on avoiding generic dark-glow aesthetics.

Re-theme by editing the `:root` variables (override example below). Tokens live on `:root`, not `#molnifyAppHtml`, so the body-appended widgets (Select2, date/time pickers) can resolve them. Brand teal (`#00acac`) stays literal - other, non-overridden UI uses it, so tokenising it would let elements drift out of sync.

```css
:root {
  --m-bg: #0f172a;          /* page background */
  --m-panel: #1e293b;       /* panels, inputs, popovers, pickers */
  --m-card: #273449;        /* raised output cards */
  --m-control: #334155;     /* control fills, borders, chart lines */
  --m-control-2: #475569;   /* hover / active / highlight, stronger borders */
  --m-text: #e2e8f0;        /* primary text */
  --m-text-strong: #f1f5f9; /* emphasised text */
  --m-text-muted: #94a3b8;  /* labels, secondary, chart text */
  --m-text-faint: #64748b;  /* placeholders, disabled */
  --m-glow: #cbd5e1;        /* people-matrix hover glow */
}

body, #page-container { background: var(--m-bg); color: var(--m-text); }

/* App title (#pAppTitle) defaults to gray - force it light for this dark page + top banner */
#pAppTitle { color: var(--m-text-strong) !important; }
#header { background: var(--m-bg) !important; border-bottom: 1px solid var(--m-control); }

/* Panels */
#molnifyAppHtml .panel { background: var(--m-panel); border: 1px solid var(--m-control); border-radius: 10px; }
#molnifyAppHtml .panel-heading { background: transparent !important; color: var(--m-text) !important; border-bottom: 1px solid var(--m-control); }

/* Tabs (nav-tabs-inverse; the active tab's white background is on the <a>) */
.nav-tabs-inverse > li > a { color: var(--m-text-muted); background: transparent; border: none; }
.nav-tabs-inverse > li > a:hover, .nav-tabs-inverse > li > a:focus { background: var(--m-control); color: var(--m-text-strong); }
.nav-tabs-inverse > li.active > a,
.nav-tabs-inverse > li.active > a:hover,
.nav-tabs-inverse > li.active > a:focus { background: var(--m-panel) !important; color: var(--m-text-strong) !important; border-color: var(--m-control) !important; }
#molnifyAppHtml .tab-content { background: transparent; border: none; }

/* Labels + input-panel section dividers (render as <legend>) */
#molnifyAppHtml .control-label, #molnifyAppHtml .input-label { color: var(--m-text-muted); }
#molnifyAppHtml legend { color: var(--m-text) !important; border-color: var(--m-control); }

/* Output cards - lighter than the panel + a border so the tiles read as distinct */
.outputbox .widget-stats { background: var(--m-card) !important; border: 1px solid var(--m-control); }
.outputbox h4.boxName { color: var(--m-text-muted); }
.outputbox p.outputBoxValue { color: var(--m-text-strong); }
/* Respect a per-output custom color (background=/color= UI) instead of the dark default */
.outputbox .widget-stats[style*="color"] .boxName,
.outputbox .widget-stats[style*="color"] .outputBoxValue,
.outputbox .widget-stats[style*="color"] .stats-icon { color: inherit !important; }

/* People matrix: default figures are inline color:black; recolor those, keep custom colors.
   Hover glow is black by default - make it light. */
#molnifyAppHtml .peopleMatrixRow > .fa[style*="black"] { color: var(--m-text-muted) !important; }
#molnifyAppHtml .peopleMatrixRow > .fa:hover { text-shadow: 0 0 5px var(--m-glow); }

/* Headings inside HTML outputs / infotext: the theme forces h1-h6 dark. Let them inherit. */
#molnifyAppHtml .out-html h1, #molnifyAppHtml .out-html h2, #molnifyAppHtml .out-html h3,
#molnifyAppHtml .out-html h4, #molnifyAppHtml .out-html h5, #molnifyAppHtml .out-html h6,
#molnifyAppHtml .input-simple-layout h1, #molnifyAppHtml .input-simple-layout h2, #molnifyAppHtml .input-simple-layout h3,
#molnifyAppHtml .input-simple-layout h4, #molnifyAppHtml .input-simple-layout h5, #molnifyAppHtml .input-simple-layout h6 { color: inherit; }

/* Buttons */
.btn { background: var(--m-control); color: var(--m-text); border: 1px solid var(--m-control-2); }
/* Copy/clipboard buttons → brand teal (literal, see note above) */
.btn[data-clipboard-action] { background: #00acac !important; border-color: #00acac !important; color: #fff !important; }
.btn[data-clipboard-action]:hover, .btn[data-clipboard-action]:focus { background: #009393 !important; border-color: #009393 !important; color: #fff !important; }

/* Form fields (white-on-white by default) */
#molnifyAppHtml .form-control { background: var(--m-bg); border-color: var(--m-control); color: var(--m-text); }
#molnifyAppHtml .form-control:focus { border-color: var(--m-control-2); box-shadow: none; }
#molnifyAppHtml .form-control::placeholder { color: var(--m-text-faint); }
#molnifyAppHtml .input-group-addon { background: var(--m-panel); border-color: var(--m-control); color: var(--m-text-muted); }

/* Numeric +/- steppers and other default buttons (light grey by default) */
#molnifyAppHtml .btn-default, #molnifyAppHtml .btn-number { background-color: var(--m-control) !important; border-color: var(--m-control-2) !important; color: var(--m-text) !important; }
#molnifyAppHtml .btn-default:hover, #molnifyAppHtml .btn-number:hover { background-color: var(--m-control-2) !important; color: var(--m-text-strong) !important; }

/* Toggle (switchery): on/off colors are set inline by JS - override via the hidden checkbox's
   :checked, with !important. On-state = brand teal. */
#molnifyAppHtml .switchery-options + .switchery { background-color: var(--m-control-2) !important; box-shadow: none !important; border-color: var(--m-control-2) !important; }
#molnifyAppHtml .switchery-options:checked + .switchery { background-color: #00acac !important; box-shadow: none !important; border-color: #00acac !important; }

/* Select2 v4.1 - appended to <body>, can't scope to #molnifyAppHtml. Selected/highlighted use
   modifier classes (not [aria-selected]), and Molnify's style.css uses !important. */
.select2-dropdown { background-color: var(--m-panel) !important; border-color: var(--m-control) !important; }
.select2-container--default .select2-results__option { color: var(--m-text); }
.select2-container--default .select2-results__option--selected { background-color: var(--m-control) !important; color: var(--m-text-strong); }
.select2-container--default .select2-results__option--highlighted.select2-results__option--selectable,
.select2-container--default .select2-results__option--highlighted[aria-selected] { background-color: var(--m-control-2) !important; color: var(--m-text-strong) !important; }
.select2-search__field { color: var(--m-text); background: var(--m-bg); }
.select2-container--default .select2-selection--single { background-color: var(--m-panel) !important; border-color: var(--m-control) !important; }
.select2-container--default .select2-selection--single .select2-selection__rendered { color: var(--m-text) !important; }
.select2-container--default .select2-selection--single .select2-selection__arrow b { border-color: var(--m-text-muted) transparent transparent transparent; }
.select2-container--default .select2-selection--multiple { background-color: var(--m-panel) !important; border-color: var(--m-control) !important; }
.select2-container--default .select2-selection__choice { background-color: var(--m-control) !important; border-color: var(--m-control-2) !important; color: var(--m-text) !important; }
.select2-container--default .select2-selection__choice__display { color: var(--m-text) !important; }
.select2-container--default .select2-selection__choice__remove { color: var(--m-text-muted) !important; }

/* Date picker (bootstrap-datepicker, appended to body) */
.datepicker, .datepicker.dropdown-menu { background: var(--m-panel); border-color: var(--m-control); color: var(--m-text); }
.datepicker table tr td, .datepicker table tr th { color: var(--m-text); }
.datepicker table tr td.day:hover, .datepicker table tr td.focused { background: var(--m-control); }
.datepicker table tr td.active, .datepicker table tr td.active.active,
.datepicker table tr td.active:hover { background: var(--m-control-2) !important; color: var(--m-text-strong); }
.datepicker table tr td.old, .datepicker table tr td.new { color: var(--m-text-faint); }

/* Time picker (bootstrap-timepicker, appended to body) */
.bootstrap-timepicker-widget.dropdown-menu { background: var(--m-panel); border-color: var(--m-control); color: var(--m-text); }
.bootstrap-timepicker-widget table td input { background: var(--m-bg); border: 1px solid var(--m-control); color: var(--m-text); }
.bootstrap-timepicker-widget a { color: var(--m-text-muted); }

/* NVD3 charts - scope text fill to axis + legend only; a blanket `.nvd3 text` would also
   recolor pie/donut slice labels and break their adaptive per-slice contrast. */
.nvd3 .nv-axis line, .nvd3 .nv-axis path { stroke: var(--m-control); }
.nvd3 .nv-axis text, .nvd3 .nv-legend text { fill: var(--m-text-muted) !important; }

/* Waterfall chart is a separate custom SVG (not NVD3): inline-black gridlines/axes + black text */
#molnifyAppHtml svg.molnify_waterfall-chart line { stroke: var(--m-control) !important; }
#molnifyAppHtml svg.molnify_waterfall-chart text { fill: var(--m-text-muted); }
```

**Override example** - a near-black "zinc" palette:
```css
:root {
  --m-bg: #09090b; --m-panel: #18181b; --m-card: #18181b;
  --m-control: #27272a; --m-control-2: #3f3f46;
  --m-text: #fafafa; --m-text-strong: #fff; --m-text-muted: #71717a; --m-text-faint: #52525b;
}
```

### Hero Metric

Make the first output card span full width with large text.

```javascript
JavaScriptAfterLoad:
$('#outputboxpanel .outputbox:first').addClass('hero-metric');
```
```css
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
body { background: #f7f5f2; }

/* Strip all panel chrome - scoped to app area */
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
.btn-primary, #molnifyAppBody .btn-success { background: #8b7355; border: none; border-radius: 4px; }

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

## Bootstrap-Based Layouts

These use BS3 class swapping - simpler but limited to 12ths.

**Tip:** For a narrower input panel without JavaScript, set `InputPanelSmall: TRUE` in metadata (gives 33%/67% split).

### Full-Width Dashboard with Compact Input Bar

Inputs in a horizontal bar at top, charts and outputs below full-width.

```javascript
JavaScriptAfterLoad:
// Stack columns full-width (see reusable block above)
```
```css
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

Metrics span full width at top, narrow inputs + charts below. Set `InputPanelSmall: TRUE` in metadata for the 33%/67% split - don't re-swap the column classes in JS to get a width Molnify already provides.

```javascript
JavaScriptAfterLoad:
var metricsRow = $('<div class="row"><div class="col-md-12" id="metricsCol"></div></div>');
metricsRow.insertBefore('#boxRow');
$('#outputboxpanel').appendTo('#metricsCol');
calculateButton();
```
```css
body { background: #f0f2f5; }

/* Output card grid override with fixed 4-column layout */
#outputboxpanel .row {
  display: grid !important;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin: 0;
}
/* Apply the rest of the grid override from styling.md (::before/::after, [class*="col-"], .widget)
   plus the chrome removal and clean panel styling from above */

/* Light input panel heading - use .panel to beat Molnify's PanelHeaderColor specificity */
#inputpanel.panel .panel-heading { background-color: transparent !important; color: #333 !important; border-bottom: 1px solid #e0e0e0; }
#inputpanel .panel-title { color: inherit; }

@media (max-width: 768px) {
  #outputboxpanel .row { grid-template-columns: 1fr; }
}
```

---

## CSS Grid Layouts

These use the universal escape pattern (strip BS3 grid, apply CSS Grid on `#boxRow`). All require the "Strip BS3 grid" JS, and the "Important when using CSS Grid" checklist in `styling.md` applies (explicit `rightColumn`/`leftColumn` on charts, final `calculateButton()`, don't starve the input column).

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
