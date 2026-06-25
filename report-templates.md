# Report Templates

Companion to the main reference.

**IMPORTANT:** The `{{variable}}` placeholder syntax described below is ONLY for report template files (docx/html/markdown). It does NOT work in Excel cells. Excel cells use standard Excel formulas and cell references (e.g., `=A1`, `=SUM(B2:B10)`).

The `generatereport` action supports multiple template engines. Set the engine via the `engine` property on the action. Templates are managed via the Template Manager in the app sidebar.

| Engine | Template File | Template Syntax / Rendering | Best For |
|--------|---------------|-----------------------------|----------|
| `html` | index.html | Mustache, rendered in a browser engine (full CSS) | Complex layouts, custom styling (default) |
| `markdown` | index.html + .md files | Mustache, rendered in a browser engine (full CSS) | Simple text reports |
| `docx` | index.docx | poi-tl placeholders, converted to PDF | Text-heavy reports, invoices, embedded charts |
| `xlsx` | index.xlsx | Excel formulas, converted to PDF | Spreadsheet reports with formulas |

## Template Data Model (shared)

All engines receive the same data, but consume it differently (see engine-specific sections below).

**Inputs and outputs** - referenced by variable name (if set via `UI: variable=X`) or cell reference (e.g. `Sheet1_B2`):
```
inputs.customerName              Single input value
outputs.totalAmount              Single output value
inputs.Sheet1_B2                 By cell reference (dots replaced with underscores)
```

**Named ranges** - single-cell ranges become scalar properties, multi-row ranges become arrays of objects:
```
namedRanges.companyName          Single named range value
namedRanges.orderItems           Array of {col1: val, col2: val, ...} objects
```

**Charts** - rendered as SVG strings from the app's chart outputs.

**Session context:**
```
molnify.userEmail                Logged-in user's email
molnify.userIP                   User's IP address
molnify.appId                    Application ID
molnify.template                 Template name
```

**File uploads** - inputs with `UI: fileupload` produce an array with `url` and `url_full` properties.

**Multiple select** - inputs with `UI: multiple` produce a semicolon-separated string in the main variable and an `_array` suffix variant with individual values.

## HTML Engine

Uses standard [Mustache](https://mustache.github.io/mustache.5.html) syntax. The template is a full webpage - any HTML, CSS, and JavaScript works. It is rendered by a browser engine, so the output matches what a browser would display.

```html
<h1>Report for {{inputs.customerName}}</h1>

<table>
  {{#namedRanges.orderItems}}
  <tr><td>{{name}}</td><td>{{price}}</td></tr>
  {{/namedRanges.orderItems}}
</table>

<!-- Charts: use triple-braces to avoid HTML escaping -->
{{{charts.myChartVariable}}}

<!-- File uploads -->
{{#inputs.myUpload_array}}
  <img src="{{url_full}}" />
{{/inputs.myUpload_array}}

<!-- Conditionals -->
{{#inputs.showDetails}}
  <p>Details: {{outputs.details}}</p>
{{/inputs.showDetails}}
```

For charts, you can either embed the app's SVG chart directly via `{{{charts.X}}}` (identical look, but zoom/proportions may be off in PDF), or use a JavaScript charting library like Chart.js to render charts from the data.

## Markdown Engine

The template bundle must contain an `index.html` that references markdown files. The markdown route processes the HTML as a wrapper and converts included markdown files. Mustache syntax works in both the HTML wrapper and the markdown files.

## DOCX Engine

Processed by the poi-tl engine - **not** by Mustache. Uses poi-tl placeholder syntax in the Word document.

**Unlike HTML/Markdown templates**, the DOCX engine uses a **flat namespace** - all inputs, outputs, and named ranges are merged into a single map by variable name. Do not prefix with `inputs.` or `outputs.`.

**What variables are available in DOCX templates:**
- Inputs/outputs with `variable=X` → available as `{{X}}`
- Inputs/outputs without a variable → available by cell reference, e.g. `{{Sheet1!B2}}`
- Single-cell named ranges → available by range name, e.g. `{{companyName}}`
- Multi-row named ranges → available as table data via `{{#rangeName}}`
- If names collide, later entries overwrite earlier ones (processing order: inputs → outputs → named ranges)

| Syntax | Purpose | Example |
|--------|---------|---------|
| `{{variable}}` | Insert text value | `{{customerName}}` |
| `{{@variable}}` | Insert image from URL (alt-text method preferred - see below) | `{{@logoUrl}}` |
| `{{#variable}}` | Insert table data (NOT a conditional - see note below) | `{{#orderItems}}` |

- Placeholder text inherits formatting from the template (bold, color, size, font)
- **Automatic image detection:** If a variable's value is a web URL ending in `.png`, `.jpg`, `.jpeg`, `.gif`, `.webp`, or `.svg`, or a data URL (`data:image/png;base64,...`), it is automatically rendered as an image - even with plain `{{variable}}` syntax. If it fails to load, a warning is logged and the value is skipped
- **Preferred: alt-text method.** Insert a placeholder image in the DOCX and set its alt text to `{{variable}}` (without the `@`). poi-tl replaces the image at render time, preserving the placeholder image's size and position. This is preferred over `{{@variable}}` because it gives control over image dimensions/layout, and if the variable is empty or unmatched the placeholder image simply stays instead of crashing
- **Alternative: `{{@variable}}` in text.** Simpler to set up but offers no size control, and **crashes** on empty/invalid values. If you must use `{{@}}`, ensure the variable always has a valid value (e.g., use a hidden output with a fallback transparent 1x1 pixel data URL - see code snippet below)
- Unmatched text placeholders (`{{variable}}`) are **silently removed** (no error, just blank)
- Charts embedded in the template document are automatically updated with app output data

**Table styling via action properties:**

Tables inserted with `{{#tableName}}` can be styled using action properties with dot notation:

| Action Property | Description | Example Value |
|----------------|-------------|---------------|
| `tableName.border.style` | Border style | NONE, SINGLE, THICK, DOUBLE, DOTTED, DASHED, OUTSET, INSET |
| `tableName.border.color` | Border color (CSS format) | `#000000`, `rgb(0,0,0)` |
| `tableName.border.width` | Border width in points | `1` |
| `tableName.header.backgroundcolor` | Header row background | `#333333` |
| `tableName.header.textcolor` | Header row text color | `#FFFFFF` |
| `tableName.header.bold` | Header row bold | `true` |
| `tableName.header.fontfamily` | Header font | `Arial` |
| `tableName.header.fontsize` | Header font size | `12` |
| `tableName.body.*` | All body rows (same sub-properties as header) | |
| `tableName.oddrows.*` | Odd-numbered rows | |
| `tableName.evenrows.*` | Even-numbered rows | |
| `tableName.footer.*` | Footer row | |

**Common pitfalls:**
- poi-tl crashes give **no user-facing feedback** - the "Preparing your file" modal just spins indefinitely. To debug, open browser DevTools → Network tab and inspect the request payload in the `api/execute` call for the generatereport action. The payload shows what data was sent to the template, which helps identify mismatches.
- Test templates with a small dataset first to catch issues early
- Ensure image URLs are accessible from the server (not localhost)
- Malformed placeholders or type mismatches can cause silent failures with no indication of which placeholder is at fault
- **No conditional rendering** - unlike the HTML engine's Mustache `{{#variable}}...{{/variable}}` syntax, `{{#}}` in DOCX only inserts table data. To conditionally show/hide content, use a hidden output that returns the content or an empty string, and reference it with `{{variable}}`
- The `signature` input type stores data in **jSignature base30 format**, not base64 PNG. To use a signature in a DOCX template image, convert it via JavaScript (see snippet below). Use the alt-text method for the image placeholder

**Code snippet - jSignature to data URL conversion:**

Use this in `JavaScriptAfterCalc` or as a `jsOnChange` handler to convert a signature input into a data URL that DOCX templates can render as an image:

```javascript
JavaScriptAfterCalc:
var sigData = getValueForVariable('signatur');
var sigImg = getValueForVariable('signatur_bild');
if (sigData && sigData !== '\u00A0' && sigData !== sigImg) {
  var canvas = document.createElement('canvas');
  canvas.width = 600; canvas.height = 200;
  var ctx = canvas.getContext('2d');
  var img = new Image();
  img.onload = function() {
    ctx.drawImage(img, 0, 0, 600, 200);
    var dataUrl = canvas.toDataURL('image/png');
    if (getValueForVariable('signatur_bild') !== dataUrl) {
      setValueForVariable('signatur_bild', dataUrl);
    }
  };
  // jSignature provides SVG export via getData('svgbase64')
  var svgData = $('.signature [variable="signatur"]').jSignature('getData', 'svgbase64');
  img.src = 'data:image/svg+xml;base64,' + svgData[1];
}
```

This requires two inputs: `signatur` (the signature input, `UI: signature;variable=signatur`) and `signatur_bild` (a hidden input, `UI: hidden;variable=signatur_bild`) that stores the converted data URL for the template.

**Code snippet - transparent 1x1 pixel fallback for empty images:**

When using `{{@variable}}` for optional images, use a hidden output with a fallback formula to prevent crashes on empty values:

```
Formula: =IF(B5="", "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAC0lEQVQI12NgAAIABQABNjN9GQAAAAlwSFlzAAAWJQAAFiUBSVIk8AAAAA0lEQVQI12P4z8BQDwAEgAF/QualIQAAAABJRU5ErkJggg==", B5)
UI: hidden;variable=safeImageUrl
```

Then use `{{safeImageUrl}}` (or the alt-text method with `{{safeImageUrl}}`) in the DOCX template instead of the raw image variable

## XLSX Engine

Processed server-side - **not** by Mustache. No Mustache syntax. Data from the app's **named ranges** is injected into matching named ranges and tables in the template.

**How it works:**
1. Named ranges in the app's Excel file are matched **by name** to named ranges in the template
2. Single-cell named ranges: the value is set directly in the template cell
3. Multi-cell named ranges: skipped (not supported - use tables instead)
4. XSSFTable objects in the template are matched by name to multi-row named range data; tables auto-resize to fit the data
5. All formulas in the template are recalculated after data injection

**Type parsing:** Values starting with `=` are injected as formulas. Booleans, percentages (`"95%"` → `0.95`), and numbers are parsed automatically. Leading-zero strings (e.g. phone numbers) are preserved as text.

**Key limitation:** If no named ranges in the template match the app's named ranges, the generated report is completely static - every report will be identical. Named ranges and tables are the only way data flows from the app to the template.

## PDF Output Notes

**Filenames:** the download filename comes from the action's `fileName` via `Content-Disposition`. Non-ASCII names (e.g. Cyrillic) are not honored - the browser falls back to a generic name like `pdf.pdf`. **Use an ASCII filename.**

**Fonts (HTML engine):** The HTML engine renders a web font loaded via `<link>`/`@font-face` URL, but does **not embed** the font file into the generated PDF. The PDF then depends on the font being available wherever it is opened, and silently falls back when it isn't - dropping glyphs the fallback font lacks, which is a real problem for non-Latin scripts. To make the font travel inside the PDF, **base64-encode the font file and inline it as a `data:` URI in `@font-face`** so it is embedded. It is tedious but reliable, and worth it whenever a specific font or non-Latin glyphs must render correctly. (The DOCX/XLSX engines render through a separate converter and use only fonts installed in the render environment - web fonts do not apply there.)
