# App Styling Guide

Companion to the main reference in `CLAUDE.md`.

## Constraints

- Molnify uses Bootstrap 3 with a fixed DOM structure — you override, not replace
- Fonts come from Google Fonts (loaded via `HeaderFont`/`BodyFont` metadata)
- CSS is injected via the `CSS` metadata cell — one big block, no separate files
- Layout restructuring requires `JavaScriptAfterLoad` for DOM manipulation
- The default 50/50 two-column split is a starting point, not a constraint — if a user asks for a "modern", "dashboard", or "professional" design, assume layout changes are needed

## HTML DOM Structure

Understanding the DOM structure helps write effective CSS. Here's the layout:

```
#content                          <- Main content container
├── #appHeaderRow                 <- Header row with app title and buttons
│   ├── .appHeaderLeft            <- App title (h1#appHeader)
│   └── #appMenu                  <- Scenario selector, action buttons
│       └── .appHeaderGroup       <- Button groups (save, print, reset, etc.)
│
└── #boxRow                       <- Main content row
    ├── #leftColumn               <- Input panel (col-md-6 or col-md-4 if InputPanelSmall)
    │   └── #inputpanel.panel     <- Panel container
    │       ├── .panel-heading    <- "Inputs" title + collapse buttons
    │       │   └── .nav-tabs     <- Tab navigation (if tabs defined)
    │       └── .panel-body
    │           └── .tab-content  <- Tab containers
    │               └── .tab-pane <- Individual tab
    │                   └── .form-group <- Each input
    │                       ├── label.control-label  <- Input title
    │                       └── .input-group         <- Input control
    │
    └── #rightColumn              <- Output panel (col-md-6 or col-md-8)
        ├── #outputboxpanel.panel <- Scalar outputs ("Results" box)
        │   └── .panel-body
        │       └── .outputbox    <- Individual output value
        │
        └── .panel                <- Chart/table/HTML panels
            ├── .panel-heading    <- Output title
            └── .panel-body
                └── .chart / .out-table-div / .out-html
```

### Component DOM Details

**Scalar output box** (`.outputbox` inside `#outputboxpanel`):
```
.col-sm-4.outputbox
└── .widget.widget-stats           <- Card container (inline style for custom bg/color)
    ├── .stats-icon                <- Icon (if UI has icon=fa-*)
    │   └── i.fa.fa-*
    ├── .stats-info
    │   ├── h4.boxName             <- Output title
    │   └── p.outputBoxValue       <- Value display
    │       attrs: cell, id, variable, data-rawValue, data-boxDecimals, data-jsOnChange
    └── .stats-link                <- Tooltip/details (if cell has comment)
```

**Table output** (inside `.panel-body`):
```
.out-table-div
└── table.out-table.table          <- Standard HTML table
    attrs: id, cell, variable, data-outputSize, data-outputValue, data-outputName,
           data-outputDecimals, data-jsOnChange
    ├── thead
    │   └── tr
    │       └── td, td, td, ...    <- NOTE: <td>, NOT <th>
    └── tbody
        └── tr
            └── td, td, td, ...
```

**Chart output** (inside `.panel-body`):
```
.chart                             <- Chart container div
    attrs: id, cell, variable, chartType, chartProps,
           data-outputSize, data-outputValue, data-outputName,
           data-outputXAxisTitle, data-outputYAxisTitle,
           data-outputChartDecimals, data-outputChartStacked,
           data-isHorizontal, data-outputShowValues,
           data-outputNoGridLines, data-jsOnChange
    └── svg.nvd3-svg               <- NVD3-rendered SVG
        └── g.nv-wrap
            ├── g.nv-x.nv-axis     <- X axis
            ├── g.nv-y.nv-axis     <- Y axis
            ├── g.nv-legendWrap    <- Legend
            └── g.nv-*Wrap         <- Data (nv-barsWrap, nv-linesWrap, etc.)
```

**HTML panel output** (inside `.panel-body`):
```
.out-html                          <- Container div
    attrs: id, cell, variable, data-jsOnChange
    └── (raw HTML content inserted directly - no extra wrappers)
```

**Panel wrapper** (wraps charts, tables, and HTML outputs):
```
.panel.panel-inverse.panel-no-rounded-corner
├── .panel-heading
│   ├── .panel-heading-btn         <- Download/collapse/expand buttons
│   │   ├── a.btn.btn-success      <- Download button (charts only)
│   │   ├── a.btn-collapse         <- Collapse (fa-minus)
│   │   └── a.btn-expand           <- Expand (fa-expand)
│   └── h4.panel-title             <- Output name
└── .panel-body
    └── (chart / table / html content)
```

**Input form group** (inside `#inputpanel .panel-body`):
```
.form-group                        <- One per input
    (optional extra classes: .<cssClass>-form-group-class, .<variable>-form-group-variable)
├── label.col-sm-4.control-label   <- Title (hidden if noTitle)
│   ├── span.input-label           <- Label text
│   └── span.btn.btn-tour          <- Tooltip icon (if cell has comment)
└── .col-sm-8                      <- Input container (col-sm-12 if noTitle)
    └── (input element - varies by type)
```

**Input types and their elements:**
| UI Type | Element | Key Classes |
|---------|---------|-------------|
| text/number | `input.form-control.inputElement` | `.input-group` wrapper, `.input-group-btn` for +/- buttons, `.input-group-addon` for prefix/postfix |
| slider | `input.inputElement.ionRangeSlider` | Rendered by Ion.RangeSlider library |
| dropdown/select | `select.form-control.inputElement.select2` | Rendered by Select2 library |
| date | `input.form-control.inputElement.dateString` | `.input-group.date` wrapper, Bootstrap Datepicker |
| time | `input.form-control.inputElement.timeString` | `.input-group.date.bootstrap-timepicker` wrapper |
| textarea | `textarea.form-control.inputElement.autoExpand` | Auto-expanding rows |
| boolean (TRUE/FALSE) | `input.inputElement.switchery-options[type=checkbox]` | `.molnify-switch` on form-group |
| infotext | `div.inputElement.infotext` | Contains `.input-simple-layout` |
| signature | `div.inputElement.signature` | Rendered by signature pad library |
| fileupload | `div.fileUpload` | Custom upload widget |

**Common attributes on all input elements:**
- `id="in<N>"` - sequential index
- `cell="<SheetName>!<CellRef>"` - source cell
- `variable="<name>"` - variable name (if set)
- `data-jsOnChange="<handler>"` - change callback
- `data-reset-when-hidden="true"` - reset on conditional hide

## Targeting Specific Panels

**Panel IDs are unreliable.** `#outputpanel-N` and `#chartpanel-N` IDs are assigned dynamically and their numbering can change when you add/remove outputs. Use the `class=` UI option instead:

```javascript
// Reliable - uses your custom class (UI: barChart;class=revenue-chart)
var panel = $('.revenue-chart').closest('.panel');

// Fragile - breaks when panels are reordered
var panel = $('#outputpanel-2');
```

## Default Color Scheme

Understanding the defaults helps avoid contrast issues. The app uses Bootstrap's `panel-inverse` style with dark headers and white text.

| Element | Default Background | Default Text |
|---------|-------------------|--------------|
| Top banner | `#242a30` (dark gray) | White |
| Panel headers | `#242a30` (dark gray) | White |
| Panel body | `#fff` (white) | `#333` (dark) |
| Output boxes (.bg-green) | `#00acac` (teal) | White |
| Success buttons (.btn-success) | `#00acac` (teal) | White |
| Default buttons (.btn-default) | `#b6c2c9` (gray-blue) | White |

**Key insight:** Panel headers and buttons have **white text** by default. The metadata color properties only change the background, not the text color.

**Common mistake - white text on light background:**
```
PanelHeaderColor: #f0f0f0    ❌ Light background + white text = invisible!
ButtonColor: #e0e0e0         ❌ Light background + white text = invisible!
```

**Solutions:**

1. **Use dark backgrounds** that work with white text:
```
PanelHeaderColor: #2c3e50    ✓ Dark background + white text = readable
SuccessButtonColor: #27ae60  ✓ Dark green + white text = readable
```

2. **Override text color via CSS** when using light backgrounds:
```
PanelHeaderColor: #f5f5f5
CSS: .panel-heading { color: #333 !important; }
```

3. **For output boxes**, light backgrounds need dark text:
```
OutputBoxBackgroundColor: #f8f9fa
CSS: .bg-green { color: #333 !important; }
```

## Styling Best Practices

**1. Use metadata color properties first:**
```
TopBannerColor: #2d3e50
HeaderTextColor: #333333
PanelHeaderColor: #34495e
ButtonColor: #3498db
SuccessButtonColor: #27ae60
OutputBoxBackgroundColor: #00acac
```

**2. Add custom CSS for fine-tuning:**
```css
CSS:
/* Rounded corners on panels */
.panel { border-radius: 8px; overflow: hidden; }

/* Larger input labels */
.control-label { font-size: 14px; font-weight: 600; }

/* Custom output box styling */
.outputbox {
  border-left: 4px solid #3498db;
  background: linear-gradient(to right, #f8f9fa, #ffffff);
}

/* Hide panel borders */
.panel { border: none; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
```

**3. Responsive adjustments:**
```css
CSS:
/* Stack columns on mobile */
@media (max-width: 768px) {
  #leftColumn, #rightColumn { width: 100%; }
  .outputbox { margin-bottom: 10px; }
}
```

**4. Chart colors (via hidden divs):**
Chart series colors are controlled by `.chart-series0` through `.chart-series39`:
```css
CSS:
.chart-series0 { color: #3498db; }
.chart-series1 { color: #e74c3c; }
.chart-series2 { color: #2ecc71; }
.chart-series3 { color: #f39c12; }
```

## Common Styling Recipes

**Clean modern look:**
```css
CSS:
body { background: #f5f6fa; }
.panel { border: none; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.08); }
.panel-heading { border-radius: 12px 12px 0 0; }
.form-control { border-radius: 6px; }
.btn { border-radius: 6px; }
```

**Compact dense layout:**
```css
CSS:
.form-group { margin-bottom: 8px; }
.panel-body { padding: 10px; }
.control-label { font-size: 12px; }
.form-control { height: 32px; font-size: 13px; }
```

**Hide elements:**
```css
CSS:
#appHeaderRow { display: none; }           /* Hide entire header */
.panel-heading-btn { display: none; }      /* Hide collapse buttons */
#scenario-chooser { display: none; }       /* Hide scenario dropdown */
.btn.buttonMargin { display: none; }       /* Hide copy buttons */
```

**Caution:** `display:none` on output elements (`.outputBoxValue`, `.out-table`, `.out-html`, `.chart`) prevents Molnify from populating their values. To reposition outputs, use DOM moves (`.appendTo()`, `.insertBefore()`) rather than hiding and showing. If you need a value without displaying it, use `position: absolute; left: -9999px` or a hidden output with `getValueForVariable()`.

**Custom fonts (with metadata):**
```
HeaderFont: Playfair Display
BodyFont: Source Sans 3
```
These load from Google Fonts automatically.

## Included CSS & JavaScript Libraries

Molnify apps automatically include these libraries - you can use their classes and functions directly:

**CSS Frameworks:**
| Library | Version | What It Provides |
|---------|---------|------------------|
| Bootstrap 3 | 3.x | Grid system, panels, buttons, forms, modals |
| Font Awesome | 4.x | Icon classes (e.g., `fa fa-check`, `fa fa-spinner`) |
| animate.css | - | CSS animations (e.g., `animated fadeIn`) |

**UI Component Libraries:**
| Library | Used For |
|---------|----------|
| ionRangeSlider | Slider inputs |
| bootstrap-select | Enhanced dropdowns |
| bootstrap-datepicker | Date picker inputs |
| bootstrap-timepicker | Time picker inputs |
| Switchery | Toggle switches |
| lightbox | Image lightbox overlays |

**Charting & Visualization:**
| Library | What It Provides |
|---------|------------------|
| D3.js | Data manipulation, SVG rendering |
| NVD3 | Chart components built on D3 |
| jVectorMap | Geographic map visualizations |

**JavaScript:**
| Library | What It Provides |
|---------|------------------|
| jQuery | DOM manipulation, AJAX, event handling |
| Bootstrap JS | Modal, dropdown, tab, collapse components |
| Parsley.js | Form validation |

**Using these in custom CSS/JavaScript:**
```css
/* Font Awesome icons in CSS */
.status-ok::before { content: "\f00c"; font-family: FontAwesome; }

/* animate.css classes */
.panel { animation: fadeIn 0.3s; }

/* Use Bootstrap classes directly in HTML outputs */
/* <div class="col-md-6">Content</div> */
```

```javascript
// jQuery is available as $ and jQuery
$('#myElement').fadeIn();

// Bootstrap components
$('#myModal').modal('show');

// D3.js for custom visualizations
d3.select('#chart').append('svg');
```

## Customizing Layout with JavaScript

The default Molnify layout is a fixed two-column structure. Use the `JavaScriptAfterLoad` metadata to rearrange elements with jQuery:

**Move an output panel above the inputs** (use `class=` UI option on the output, e.g. `UI: html;class=summary`):
```javascript
JavaScriptAfterLoad: $('.summary').closest('.panel').insertBefore('#inputpanel');
```

**Move a chart into the input column** (use `class=` UI option, e.g. `UI: barChart;class=sidebar-chart`):
```javascript
JavaScriptAfterLoad: $('.sidebar-chart').closest('.panel').appendTo('#leftColumn');
```

**Create a full-width section above both columns** (use `class=` UI option, e.g. `UI: html;class=hero-output`):
```javascript
JavaScriptAfterLoad:
var fullWidth = $('<div class="col-md-12"></div>');
$('.hero-output').closest('.panel').appendTo(fullWidth);
fullWidth.insertBefore('#leftColumn');
```

**Hide the input panel entirely:**
```javascript
JavaScriptAfterLoad: $('#leftColumn').hide(); $('#rightColumn').removeClass('col-md-6').addClass('col-md-12');
```

See the "HTML DOM Structure" section above for all selectors.

**Tips:**
- Use `JavaScriptAfterLoad` (not `JavaScript`) to ensure DOM elements exist
- Test on mobile viewports - moved elements may stack differently
- Combine with CSS for responsive adjustments

## Breaking Out of the Bootstrap 3 Grid

Molnify uses Bootstrap 3, which forces a 12-column grid with `col-md-*` classes. The existing recipes often swap these classes (e.g. `col-md-6` → `col-md-3`), but you're still locked into 12ths. For full layout control, **strip the BS3 grid entirely and use CSS Grid on `#boxRow`:**

### The universal escape pattern

This JS+CSS combo removes all BS3 grid constraints from the main layout. Use it as a starting point for any custom layout:

```javascript
JavaScriptAfterLoad:
// Strip all Bootstrap grid classes from the two main columns
$('#leftColumn, #rightColumn').removeClass(function(i, classes) {
  return (classes.match(/\bcol-\S+/g) || []).join(' ');
});
// Also strip from #boxRow itself
$('#boxRow').removeClass(function(i, classes) {
  return (classes.match(/\brow\b/g) || []).join(' ');
});
```
```css
CSS:
/* Replace Bootstrap grid with CSS Grid */
#boxRow {
  display: grid !important;
  gap: 24px;
  padding: 0 20px;
  /* Define your layout here - change this per app.
     Keep the input column at least as wide as InputPanelSmall (~33%).
     minmax() sets a hard floor so the inputs never collapse. */
  grid-template-columns: minmax(360px, 33%) 1fr;
}

/* Remove all Bootstrap column artifacts */
#leftColumn, #rightColumn {
  width: auto !important;
  max-width: none !important;
  float: none !important;
  padding: 0 !important;
  position: static !important;
}
```

**Important when using CSS Grid:**
- **Don't starve the input column.** Treat the built-in `InputPanelSmall` width (33% of `#boxRow`) as the floor — do not render inputs narrower than that. Prefer `minmax(360px, 33%) 1fr` over a fixed pixel sidebar. When in doubt, just set `InputPanelSmall: TRUE` in metadata instead of rebuilding the grid.
- **Charts/tables need `rightColumn` or `leftColumn` UI options** — Molnify's default panel alternation between columns doesn't work reliably in CSS Grid layouts. Explicitly set `UI: barChart;rightColumn` (or `leftColumn`) on every chart and table to ensure correct placement.
- **Don't combine `leftColumn`/`rightColumn` hints with manual re-parenting.** Those hints split panels across `#leftColumn` and `#rightColumn`, so a recipe that re-parents only `#leftColumn .panel` (like the asymmetric-grid example) grabs just half of them and scrambles document order. Pick one approach: either let the hints place panels, **or** drop the hints, give each panel its own `class=`, and re-parent *every* panel into the grid in an explicit, deterministic order.
- **Call `calculateButton()` at the end of `JavaScriptAfterLoad`** — NVD3 charts compute their dimensions on render. If DOM restructuring changes container sizes, charts may draw with zero width or stale dimensions. A final `calculateButton()` forces a redraw with correct dimensions.

Once you've applied this pattern, `grid-template-columns` controls everything. Some examples:

| Layout | `grid-template-columns` |
|--------|------------------------|
| Narrow sidebar + wide content | `minmax(360px, 33%) 1fr` |
| Equal split | `1fr 1fr` |
| Three columns | `minmax(360px, 30%) 1fr 300px` |
| Inputs hidden, full-width content | `0 1fr` (plus `#leftColumn { display: none; }`) |
| Stacked (mobile-style) | `1fr` (single column) |

### Overriding Bootstrap inside panels

The same BS3 grid problem exists inside output panels, where `.row` and `.col-sm-*` constrain output cards. Override these separately:

```css
/* Output cards - replace BS3 grid with CSS Grid */
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
```

### Actual DOM structure for outputs
```
#outputboxpanel.panel
└── .panel-body
    └── form
        └── .row                    <- Bootstrap flex here!
            └── .col-sm-4.outputbox <- Bootstrap widths here!
                └── .widget-stats   <- The actual card
```

Always check which element has the Bootstrap classes and target accordingly.

## Layout Examples

Complete layout recipes are in **`styling-examples.md`**. Each includes JavaScript and CSS.

| Example | Description | Approach |
|---------|-------------|----------|
| Full-width dashboard | Horizontal input bar at top, charts below | BS3 class swap |
| Full-width metrics above inputs | Metrics span full width, narrow inputs + charts below | BS3 class swap |
| Hero metric | First output card large and full-width | CSS addition |
| Centered single-column | Form-focused, narrow centered layout | BS3 class swap |
| Full-width charts above inputs | Charts moved above the input/output area | BS3 class swap |
| Horizontal input bar | Inputs inline on one row | BS3 + Flexbox |
| Kiosk mode | Dark theme, no chrome | CSS only |
| Sticky inputs | Input panel stays fixed while scrolling | CSS only |
| Three-column layout | Inputs \| Charts \| Summary metrics | CSS Grid escape |
| Data-entry focused | Wide centered form, results below | CSS Grid escape |
| Tabbed dark dashboard | No inputs, dark theme, metrics + charts | CSS Grid escape |
| Asymmetric grid | Inputs + metric cards top row, charts full-width below | CSS Grid escape |
