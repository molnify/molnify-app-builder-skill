# UX Patterns

Companion to the main reference.

Reusable patterns that combine inputs, outputs, JavaScript, CSS, and actions to create common user experiences. Each pattern includes the app structure, metadata, and code needed.

For visual styling (colors, fonts, CSS Grid layouts, dashboard aesthetics), see `styling.md`.

---

## Choosing a Pattern

Pick the simplest approach that meets the requirement. Each row below is more complex than the one above - only escalate when the simpler option genuinely can't work.

| What the user needs | Pattern | Why |
|---------------------|---------|-----|
| Display calculated results, charts, summaries | Default outputs (no extra JS) | Molnify handles rendering and re-rendering automatically |
| Multi-page form, guided data entry | [Multi-Step Wizard](#multi-step-wizard) | Tabs + JS navigation, stays within default UI |
| Organized form with sections | [Form with Grouped Sections](#form-with-grouped-sections) | CSS-only, no JS needed for basic version |
| Show/hide fields based on a selection | [Conditional Multi-Section Form](#conditional-multi-section-form) | Built-in `showIfVariable`/`showIfValue`, no JS needed |
| Read-only table, click row to edit in a form | [Master-Detail with Database Table](#master-detail-with-database-table) | Table stays server-rendered, editing happens in inputs - works *with* the calc cycle |
| Live formatted preview (invoice, certificate) | [Live Report Preview](#live-report-preview) | HTML output with formula, auto-updates on calc |
| Printable output | [Print-Optimized Layout](#print-optimized-layout) | CSS `@media print` rules only |
| Chart type Molnify doesn't support (radar, polar, heatmap) | [Custom Chart (External Library)](#custom-chart-external-library) | HeadHTML loads library, JS renders into a stable canvas |
| Inline table editing, drag-and-drop, complex table interactions | Headless mode (`Headless: TRUE`) | You need to own the DOM entirely - see `custom-frontend.md` |

### The key question for table-heavy apps

If the app involves a data table with row-level actions, ask: **does the user edit data inside the table, or in a separate form?**

- **Separate form** → Master-Detail pattern. The table is a read-only Molnify output that re-renders safely on each calculation. Editing happens in standard inputs. This is the recommended approach for most CRUD apps.

- **Inside the table** (contenteditable cells, inline dropdowns, edit/save/cancel buttons per row) → Custom frontend. You need full control over the DOM because Molnify will re-render the table on every calculation, destroying your inline editing state, event handlers, and injected elements. See `custom-frontend.md` and the "DOM Lifecycle" section in `advanced-topics.md`.

---

## Multi-Step Wizard

Guide users through a sequence of steps with prev/next navigation and a progress indicator. Good for onboarding flows, multi-page forms, and guided data entry.

**How it works:**
- Group inputs into tabs - set `tab=X` only on the **first input** of each step (each `tab=` creates a new tab; subsequent inputs without `tab=` stay in the current tab)
- Hide the default tab bar with CSS
- Add a custom progress indicator and prev/next buttons via JavaScript
- Track the current step in a hidden variable

**App structure:**
```python
app = AppBuilder("wizard-demo", "Application Form")

# Step 1: Personal info - only first input gets tab=
app.add_input("Full Name", "", ui="tab=Step 1;variable=fullName;placeholder=Enter your name")
app.add_input("Email", "", ui="variable=email;placeholder=email@company.com")
app.add_input("Phone", "", ui="variable=phone;placeholder=+46 70 123 4567")

# Step 2: Details - tab= only on first input
app.add_input("Department", "Engineering", ui="tab=Step 2;dropdown;variable=department")
app.add_input("Start Date", "", ui="date;variable=startDate")
app.add_input("Notes", "", ui="textarea;variable=notes")
# Hidden step tracker - no tab=, stays in Step 2
app.add_input("Step", "0", ui="hidden;variable=wizardStep")

# Step 3: Review (output with formula - recalculates when inputs change)
app.add_output("Review", '="<h4>Please confirm:</h4><p><b>Name:</b> "&B1&"</p><p><b>Email:</b> "&B2&"</p><p><b>Department:</b> "&B4&"</p>"',
               ui="tab=Step 3;html;amongInputs;hideCopy")
```

**Metadata - JavaScript:**
```javascript
JavaScriptAfterLoad:
var $allLinks = $('#inputpanel .nav-tabs a');
var tabNames = [];
var $tabs = $();
$allLinks.each(function() {
  var name = $(this).text().trim();
  if (name && tabNames.indexOf(name) === -1) {
    tabNames.push(name);
    $tabs = $tabs.add($(this));
  }
});
var stepCount = tabNames.length;

// Build progress bar + navigation
var $wizard = $('<div id="wizard-nav"></div>');
var $progress = $('<div class="wizard-progress"></div>');
for (var i = 0; i < stepCount; i++) {
  $progress.append('<div class="wizard-step" data-step="' + i + '"><span class="step-num">' + (i+1) + '</span> ' + tabNames[i] + '</div>');
}
$wizard.append($progress);

var $buttons = $('<div class="wizard-buttons"></div>');
$buttons.append('<button class="btn btn-default" id="wizPrev" onclick="wizardNav(-1)">Previous</button>');
$buttons.append('<button class="btn btn-success" id="wizNext" onclick="wizardNav(1)">Next</button>');
$wizard.append($buttons);

$('#inputpanel .panel-body').prepend($wizard);

// Use window. so inline onclick handlers can find these functions
window.wizardNav = function(dir) {
  var cur = parseInt(getValueForVariable('wizardStep') || '0');
  var next = Math.max(0, Math.min(stepCount - 1, cur + dir));
  if (next !== cur) setValueForVariable('wizardStep', String(next));
};

window.wizardUpdate = function() {
  var cur = parseInt(getValueForVariable('wizardStep') || '0');
  $tabs.eq(cur).click();
  $('.wizard-step').removeClass('active done');
  for (var i = 0; i < cur; i++) $('.wizard-step').eq(i).addClass('done');
  $('.wizard-step').eq(cur).addClass('active');
  $('#wizPrev').css('visibility', cur > 0 ? 'visible' : 'hidden');
  $('#wizNext').text(cur === stepCount - 1 ? 'Submit' : 'Next');
};
wizardUpdate();
```

```javascript
JavaScriptAfterCalc:
if (typeof wizardUpdate === 'function') wizardUpdate();
```

**Metadata - CSS:**
```css
CSS:
/* Hide default tab bar */
#inputpanel .nav-tabs { display: none; }

/* Progress indicator */
.wizard-progress { display: flex; gap: 8px; margin-bottom: 20px; }
.wizard-step {
  flex: 1; padding: 10px 12px; background: #f0f0f0; border-radius: 8px;
  font-size: 13px; color: #999; text-align: center;
}
.wizard-step .step-num {
  display: inline-block; width: 24px; height: 24px; border-radius: 50%;
  background: #ddd; color: #999; text-align: center; line-height: 24px;
  font-weight: 600; margin-right: 4px;
}
.wizard-step.active { background: #e8f4fd; color: #1a73e8; }
.wizard-step.active .step-num { background: #1a73e8; color: white; }
.wizard-step.done { background: #e8f8e8; color: #2e7d32; }
.wizard-step.done .step-num { background: #2e7d32; color: white; }

/* Navigation buttons */
.wizard-buttons { display: flex; justify-content: space-between; margin-top: 20px; padding-top: 16px; border-top: 1px solid #eee; }
.wizard-buttons .btn { min-width: 120px; }
```

**Tips:**
- The review step uses an output (not an input) so it recalculates when inputs change. `amongInputs` places it in the input panel, `hideCopy` removes the copy button
- Use `window.functionName = function(...)` for functions called from inline `onclick` handlers - regular `function` declarations inside `JavaScriptAfterLoad` are not accessible from inline handlers
- Use `$tabs.eq(cur).click()` to switch tabs - `.tab('show')` causes a jQuery error on Molnify's tab links
- Use `css('visibility', ...)` instead of `.toggle()` on the Previous button so the Next button stays right-aligned on step 1
- To add validation before advancing, check values in `wizardNav()` and show an alert if incomplete
- For a final submit action, check if `cur === stepCount - 1` in `wizardNav(1)` and call `performActionWithName('submit')` instead of advancing

---

## Form with Grouped Sections

Organize inputs into visual card groups instead of a flat list. Good for any form with distinct sections (personal details, address, payment, etc.).

**How it works:**
- Use `dividerName=Section Title` on the first input of each group
- Molnify renders dividers as `<legend id="divider-inN">` elements inside the input panel
- CSS transforms these legend elements into card headers and wraps subsequent inputs in card bodies

**App structure:**

Use `dividerName` on the first input of each section:
```
Name        [GREEN] ""           variable=name;dividerName=Personal Details
Email       [GREEN] ""           variable=email;placeholder=email@company.com
Phone       [GREEN] ""           variable=phone

Street      [GREEN] ""           variable=street;dividerName=Address
City        [GREEN] ""           variable=city
Zip Code    [GREEN] ""           variable=zip

Card Number [GREEN] ""           variable=cardNum;dividerName=Payment
Expiry      [GREEN] ""           variable=expiry;date
```

**Metadata - CSS:**
```css
CSS:
body { background: #f5f6fa; }

/* Turn dividers (legend elements) into card headers */
#inputpanel legend[id^="divider-"] {
  background: #f8f9fa;
  margin: 0 -15px;
  padding: 14px 20px;
  border-bottom: 1px solid #e9ecef;
  border-top: 1px solid #e9ecef;
  font-weight: 600;
  font-size: 14px;
  color: #374151;
  text-transform: none;
  width: auto;
}

/* First divider has no top gap */
#inputpanel legend[id^="divider-"]:first-of-type {
  margin-top: -15px;
  border-top: none;
  border-radius: 4px 4px 0 0;
}

/* Spacing between header and first input */
#inputpanel legend[id^="divider-"] + .form-group { margin-top: 10px; }

/* Card-like panel */
#inputpanel {
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.08);
  overflow: hidden;
}
#inputpanel .panel-heading { display: none; }
#inputpanel .form-group { margin-bottom: 14px; }
```

**Side-by-side inputs within a section:**

To place two inputs on one row (e.g., first name + last name), use CSS classes:
```
First Name  [GREEN] ""   variable=firstName;class=half-left;dividerName=Personal Details
Last Name   [GREEN] ""   variable=lastName;class=half-right
```

```css
CSS:
/* Side-by-side input pairs - avoid !important on display so slideToggle works */
#inputpanel .half-left-form-group-class,
#inputpanel .half-right-form-group-class {
  display: inline-block;
  width: 49%;
  vertical-align: top;
}
#inputpanel .half-right-form-group-class { margin-left: 1%; }
```

Note: Molnify appends `-form-group-class` to the `class=` value when applying it to the form group wrapper.

**Collapsible sections:**

Add JavaScript to make section cards collapsible. The callback restores `display: inline-block` on side-by-side inputs after the slide animation (jQuery's `slideToggle` sets `display: block`):
```javascript
JavaScriptAfterLoad:
$('#inputpanel legend[id^="divider-"]').each(function() {
  var $legend = $(this);
  $legend.css('cursor', 'pointer');
  $legend.append(' <i class="fa fa-chevron-up" style="float:right;margin-top:2px"></i>');
  $legend.on('click', function() {
    var $icon = $(this).find('i');
    var $fields = $(this).nextUntil('legend', '.form-group');
    $fields.slideToggle(200, function() {
      var $el = $(this);
      if ($el.is(':visible') && ($el.hasClass('half-left-form-group-class') || $el.hasClass('half-right-form-group-class'))) {
        $el.css('display', 'inline-block');
      }
    });
    $icon.toggleClass('fa-chevron-up fa-chevron-down');
  });
});
```

---

## Master-Detail with Database Table

Show a list of records in a table, click a row to load it into the form for viewing or editing. Good for CRUD apps - order management, contact lists, inventory tracking.

**Simpler alternative:** If you only need a dropdown to pick a record (not a visible table), use a `recorddropdown` or `rowdropdown` input instead. It handles record selection and variable population automatically with no JavaScript. See `database.md` for details.

**How it works:**
- Autofill populates a named range displayed as a Molnify table
- JavaScript adds click handlers to table rows
- Clicking a row sets input variables via `setValueForVariable()`
- A hidden `recordId` variable tracks whether we're creating or editing

**App structure:**
```python
app = AppBuilder("contacts", "Contact Manager")

# Record ID (hidden - set when editing, empty when creating new)
app.add_input("Record ID", "", ui="hidden;variable=recordId")

# Form inputs
app.add_input("Name", "", ui="variable=name;placeholder=Full name;dividerName=Contact Details")
app.add_input("Email", "", ui="variable=email;placeholder=email@company.com")
app.add_input("Phone", "", ui="variable=phone;placeholder=+46 70 123 4567")
app.add_input("Company", "", ui="variable=company;placeholder=Company name")

# Table showing existing records (populated by autofill)
app.add_model_sheet("Autofill")
app.add_named_range("contactList", "Autofill", "A2:E50")

# Save action
app.add_action({
    "type": "addrecord",
    "title": "Save Contact",
    "name": "saveContact",
    "successText": "Contact saved!",
    "successCalculate": "TRUE",
})

# Metadata
app.add_metadata("RecordTableName", "data_contacts_0")
app.add_metadata("DataTable.0", '{"columns":{"name":"VARCHAR","email":"VARCHAR","phone":"VARCHAR","company":"VARCHAR"}}')
app.add_metadata("autofill.contactList", "SELECT recordId, name, email, phone, company FROM `data_contacts_0` ORDER BY recordId DESC LIMIT 50")
app.add_metadata("JavaScriptAfterLoad", "calculateButton();")
```

The table output uses blue cells with formulas that reference the autofill range. Use `IF` to return `""` for empty rows so Molnify auto-hides them:
```python
num_rows = 20
app.add_chart("Contacts", "table",
              series={
                  "Name": [f'=IF(Autofill!B{i}="","",Autofill!B{i})' for i in range(2, 2 + num_rows)],
                  "Email": [f'=IF(Autofill!C{i}="","",Autofill!C{i})' for i in range(2, 2 + num_rows)],
                  "Phone": [f'=IF(Autofill!D{i}="","",Autofill!D{i})' for i in range(2, 2 + num_rows)],
                  "Company": [f'=IF(Autofill!E{i}="","",Autofill!E{i})' for i in range(2, 2 + num_rows)],
              },
              labels=[f'=IF(Autofill!A{i}="","",Autofill!A{i})' for i in range(2, 2 + num_rows)])
```

**Metadata - JavaScript:**
```javascript
JavaScriptAfterCalc:
// Add click handlers to table rows
$('.out-table tbody tr').off('click.master').on('click.master', function() {
  var $cells = $(this).find('td');
  if ($cells.length < 5) return;

  setValueForVariable('recordId', $cells.eq(0).text().trim());
  setValueForVariable('name', $cells.eq(1).text().trim());
  setValueForVariable('email', $cells.eq(2).text().trim());
  setValueForVariable('phone', $cells.eq(3).text().trim());
  setValueForVariable('company', $cells.eq(4).text().trim());

  // Highlight selected row
  $('.out-table tbody tr').removeClass('selected-row');
  $(this).addClass('selected-row');
});
```

```javascript
JavaScriptAfterLoad:
// Add a "New Contact" button to clear the form
var $clearBtn = $('<button class="btn btn-default" style="margin-bottom:15px" onclick="clearForm()"><i class="fa fa-plus"></i> New Contact</button>');
$('#inputpanel .panel-body').prepend($clearBtn);

window.clearForm = function() {
  setValueForVariable('recordId', '');
  setValueForVariable('name', '');
  setValueForVariable('email', '');
  setValueForVariable('phone', '');
  setValueForVariable('company', '');
  $('.out-table tbody tr').removeClass('selected-row');
};
```

**Metadata - CSS:**
```css
CSS:
/* Clickable table rows */
.out-table tbody tr { cursor: pointer; transition: background 0.15s; }
.out-table tbody tr:hover { background: #f0f7ff; }
.out-table tbody tr.selected-row { background: #e3f2fd; font-weight: 500; }

/* Hide the recordId column */
.out-table tr td:first-child { display: none; }
.out-table tr td:first-child + td { border-left: none; }
```

**Tips:**
- The `addrecord` action automatically inserts (if `recordId` is empty) or updates (if `recordId` has a value). Use `idVariable` if your ID column is not named `recordId`.
- Use `successCalculate: TRUE` so the table refreshes after saving
- The "New Contact" button can be replaced with a `resetinputs` action to avoid manual `setValueForVariable` calls
- To add a delete button, create a separate HTTP or SQL action that deletes by `recordId`
- For large datasets, add a search input that filters the autofill query dynamically:
  ```
  autofill.contactList: ="SELECT recordId, name, email, phone, company FROM `data_contacts_0` WHERE name LIKE '%" & B10 & "%' ORDER BY recordId DESC LIMIT 50"
  ```

---

## Live Report Preview

Show a formatted preview of what a report will look like, updating in real-time as the user fills in inputs. Good for invoice builders, quote generators, and certificate creators.

**How it works:**
- An HTML output (`UI: html`) contains a formula that builds a formatted HTML document from input/output values
- The preview updates on every calculation
- Style it to look like a paper document

**App structure:**

The key is an output whose formula concatenates HTML:
```
Preview  [RED]  ="<div class='preview-doc'><h1>Invoice #"&B2&"</h1><p class='date'>"&TEXT(B3,"YYYY-MM-DD")&"</p><hr><p><b>Bill to:</b> "&B4&"</p><p><b>Email:</b> "&B5&"</p><table class='inv-table'><tr><th>Item</th><th>Qty</th><th>Price</th><th>Total</th></tr><tr><td>"&B7&"</td><td>"&B8&"</td><td>"&B9&"</td><td>"&B8*B9&"</td></tr></table><div class='inv-total'><b>Total: $"&TEXT(B8*B9,"#,##0.00")&"</b></div></div>"   html;hideCopy
```

For complex previews, split the formula across helper cells on a model sheet to stay under the 256-character string limit:
```
Model!B1: ="<div class='preview-doc'><h1>Invoice #"&App!B2&"</h1>"
Model!B2: ="<p><b>Bill to:</b> "&App!B4&"</p>"
Model!B3: ="<table class='inv-table'>..."
App output: =Model!B1&Model!B2&Model!B3&"</div>"
```

**Metadata - CSS:**
```css
CSS:
/* Paper document look */
.preview-doc {
  background: white;
  max-width: 700px;
  margin: 0 auto;
  padding: 48px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.12);
  font-family: Georgia, serif;
  line-height: 1.6;
  min-height: 800px;
}
.preview-doc h1 { font-size: 28px; margin: 0 0 4px; }
.preview-doc .date { color: #888; margin: 0 0 20px; }
.preview-doc hr { border: none; border-top: 2px solid #333; margin: 16px 0; }

/* Invoice table */
.inv-table { width: 100%; border-collapse: collapse; margin: 24px 0; }
.inv-table th { background: #f5f5f5; text-align: left; padding: 10px; border-bottom: 2px solid #ddd; }
.inv-table td { padding: 10px; border-bottom: 1px solid #eee; }
.inv-total { text-align: right; font-size: 18px; margin-top: 16px; }

/* Hide the panel chrome around the preview */
.preview-doc-panel .panel-heading { display: none; }
.preview-doc-panel .panel-body { padding: 0; background: #f0f0f0; }
```

Add `class=preview-doc-panel` and `hideCopy` to the HTML output's UI options: `UI: html;hideCopy;class=preview-doc-panel`

**Tips:**
- Use `TEXT()` for number formatting in formulas: `TEXT(B8*B9, "#,##0.00")`
- For a "Generate PDF" button, create a `generatereport` action with an HTML template that reuses the same layout - or use the preview HTML directly
- The preview panel can be placed in the right column (default) or moved above inputs with `JavaScriptAfterLoad`

---

## Conditional Multi-Section Form

Show or hide entire form sections based on a controlling dropdown. Good for insurance applications, multi-type forms, and any scenario where different selections require different inputs.

**How it works:**
- A controlling dropdown input is exposed as a variable
- Subsequent inputs use `showIfVariable` and `showIfValue` to show/hide based on the selection
- `dividerName` creates visual section boundaries
- `resetWhenHidden` resets values to their defaults while a section is hidden (so they are not submitted), but when the section is shown again, inputs regain their previously entered values

**App structure:**
```python
app = AppBuilder("claim-form", "Insurance Claim Form")

# Common fields
app.add_input("Claim Type", "Vehicle", ui="dropdown;variable=claimType;dividerName=Claim Information")
app.add_input("Date of Incident", "", ui="date;variable=incidentDate")
app.add_input("Description", "", ui="textarea;variable=description")

# Vehicle section - only shown when claimType = "Vehicle"
app.add_input("Registration Number", "",
    ui="variable=regNum;dividerName=Vehicle Details;showIfVariable=claimType;showIfValue=Vehicle;resetWhenHidden")
app.add_input("Vehicle Make/Model", "",
    ui="variable=vehicleMake;showIfVariable=claimType;showIfValue=Vehicle;resetWhenHidden")
app.add_input("Damage Location", "Front",
    ui="dropdown;variable=damageLocation;showIfVariable=claimType;showIfValue=Vehicle;resetWhenHidden")

# Property section - only shown when claimType = "Property"
app.add_input("Property Address", "",
    ui="variable=propAddress;dividerName=Property Details;showIfVariable=claimType;showIfValue=Property;resetWhenHidden")
app.add_input("Property Type", "House",
    ui="dropdown;variable=propType;showIfVariable=claimType;showIfValue=Property;resetWhenHidden")
app.add_input("Estimated Damage ($)", 0,
    ui="variable=propDamage;min=0;showIfVariable=claimType;showIfValue=Property;resetWhenHidden")

# Health section - same pattern with showIfValue=Health:
#   Hospital/Clinic (first input carries dividerName=Health Details), Treatment Date (date), Diagnosis (textarea)

# Common fields at the bottom
app.add_input("Upload Evidence", "", ui="fileupload;dividerName=Supporting Documents")
app.add_input("Signature", "", ui="signature;variable=claimSignature")
```

**Key points:**
- Every input in a conditional section needs `showIfVariable=claimType;showIfValue=Vehicle` (or Property, Health)
- Add `resetWhenHidden` so hidden values are reset and not submitted
- The `dividerName` on the first input of each section creates the section header. It is also conditionally hidden when its input is hidden
- Common fields (date, description, uploads, signature) that appear regardless of type do NOT have `showIfVariable`

**Multiple conditions:**

To show a field only when *two* conditions are met (e.g., Vehicle AND damage location is Front), chain conditions on a hidden output:
```
Show front details?  [RED]  =IF(AND(claimType="Vehicle", damageLocation="Front"), "yes", "no")   hidden;variable=showFrontDetails
Front Photo          [GREEN] ""   fileupload;showIfVariable=showFrontDetails;showIfValue=yes;resetWhenHidden
```

**Tips:**
- For dropdowns, set up data validation lists in Excel for each dropdown
- If you have many conditional sections, consider using the multi-step wizard pattern instead - one section per step, with the controlling dropdown on step 1
- Test with `resetWhenHidden` to verify that hidden values are properly cleared before saving

---

## Print-Optimized Layout

Make the app look good when printed directly from the browser (Ctrl+P / Cmd+P). Good for apps where users need a quick printout without generating a formal report.

**How it works:**
- `@media print` CSS rules hide navigation, inputs, and chrome
- Outputs are reformatted for paper
- Page break control ensures clean pagination

**Metadata - CSS:**
```css
CSS:
@media print {
  /* Hide everything except results */
  #header, #topMenu, .navbar, #appHeaderRow,
  #leftColumn, .panel-heading-btn,
  .btn, #scenario-chooser { display: none !important; }

  /* Make output column full width */
  #rightColumn {
    width: 100% !important;
    margin: 0 !important;
    padding: 0 !important;
  }

  /* Remove panel chrome */
  .panel {
    border: none !important;
    box-shadow: none !important;
    break-inside: avoid;
  }
  .panel-heading {
    background: none !important;
    color: #000 !important;
    border-bottom: 2px solid #333 !important;
    padding-left: 0 !important;
  }

  /* Clean table styling */
  .out-table { border-collapse: collapse; width: 100%; }
  .out-table td { border: 1px solid #ccc; padding: 6px 10px; }
  .out-table thead td { background: #f5f5f5 !important; font-weight: bold; }

  /* Output boxes - simple grid */
  .outputbox .widget-stats {
    background: none !important;
    border: 1px solid #ddd;
    color: #000 !important;
  }
  .outputbox .widget-stats * { color: #000 !important; }

  /* Page setup */
  body { background: white !important; font-size: 12pt; }
  @page { margin: 2cm; size: A4; }

  /* Force page breaks before specific panels (use class= UI option) */
  .page-break-before { break-before: page; }
}
```

**Showing print-only content:**

To show content only when printing (e.g., a header with date and company name), hide the output's entire panel on screen and reveal it in print. Note: `class=` is applied to the `.panel-body`, not the outer `.panel`, so use JavaScript to add a hiding class to the parent panel:
```css
CSS:
.print-only { display: none; }
.print-only-panel { display: none; }
@media print {
  .print-only { display: block !important; }
  .print-only-panel { display: block !important; }
}
```

```
Print Header  [RED]  ="<div class='print-only'><h1>Company Report</h1><p>Printed: "&TEXT(TODAY(),"YYYY-MM-DD")&"</p><hr></div>"   html;hideCopy;class=print-header
```

```javascript
JavaScriptAfterLoad:
$('.print-header').closest('.panel').addClass('print-only-panel');
```

**Hiding specific outputs from print:**
```css
CSS:
@media print { .no-print { display: none !important; } }
```

Then on the output: `UI: barChart;class=no-print` - the chart will show on screen but not when printed.

**Tips:**
- Use `break-inside: avoid` on panels to prevent content from splitting across pages
- Use `break-before: page` (via `class=page-break-before`) to force a new page before a section
- Test with browser print preview (Ctrl+P) during development
- For more control over the printed output, use `generatereport` with an HTML template instead - it gives full control over the PDF layout
- The `EnabledForPrint` metadata (TRUE by default) shows a print button in the header that triggers `window.print()`

---

## Custom Chart (External Library)

Render chart types that Molnify doesn't support natively (radar, polar area, heatmap, etc.) using an external library like Chart.js. The chart updates live as inputs change.

**How it works:**
- `HeadHTML` metadata loads the chart library from a CDN
- An HTML output (`UI: html`) provides a panel in the right column - the `class=` UI option identifies it
- `JavaScriptAfterLoad` creates a `<canvas>` as a sibling of `.out-html` (not inside it) and initializes the chart
- `JavaScriptAfterCalc` reads input values via `getValueForVariable()` and updates the chart data

**Why the canvas must be outside `.out-html`:** Molnify re-renders HTML output content on every calculation, replacing the innerHTML of `.out-html`. A canvas inside it would be destroyed and recreated each time, losing the Chart.js instance and causing the chart to re-animate. Placing the canvas as a sibling in the same `.panel-body` keeps it stable across calculations.

**App structure:**
```python
app = AppBuilder("assessment", "Team Assessment")

# Slider inputs - variable= exposes values to JS
app.add_input("Technical Skills", 8, ui="variable=technical;slider;min=1;max=10;delta=1")
app.add_input("Communication", 6, ui="variable=communication;slider;min=1;max=10;delta=1")
app.add_input("Leadership", 5, ui="variable=leadership;slider;min=1;max=10;delta=1")
app.add_input("Problem Solving", 9, ui="variable=problemSolving;slider;min=1;max=10;delta=1")
app.add_input("Creativity", 7, ui="variable=creativity;slider;min=1;max=10;delta=1")
app.add_input("Teamwork", 8, ui="variable=teamwork;slider;min=1;max=10;delta=1")

# HTML output - class= lets JS find the panel; content doesn't matter (hidden by JS)
app.add_output("Skills Radar", " ", ui="html;hideCopy;rightColumn;class=radar-panel")
```

**Metadata:**
```
HeadHTML: <script src="https://cdn.jsdelivr.net/npm/chart.js@4/dist/chart.umd.min.js"></script>
```

**Metadata - JavaScript:**
```javascript
JavaScriptAfterLoad:
var $panelBody = $('.radar-panel').closest('.panel').find('.panel-body');
$panelBody.find('.out-html').hide();
$('<canvas id="radarChart" style="max-height:400px"></canvas>').appendTo($panelBody);

window._radarChart = new Chart(document.getElementById('radarChart'), {
  type: 'radar',
  data: {
    labels: ['Technical', 'Communication', 'Leadership', 'Problem Solving', 'Creativity', 'Teamwork'],
    datasets: [{
      label: 'Score',
      data: [0, 0, 0, 0, 0, 0],
      backgroundColor: 'rgba(51, 65, 85, 0.2)',
      borderColor: '#334155',
      borderWidth: 2,
      pointBackgroundColor: '#1e293b',
      pointBorderColor: '#fff',
      pointRadius: 4
    }]
  },
  options: {
    scales: {
      r: {
        min: 0, max: 10,
        ticks: { stepSize: 2, backdropColor: 'transparent', font: { size: 11 } },
        grid: { color: '#e2e8f0' },
        angleLines: { color: '#e2e8f0' },
        pointLabels: { font: { size: 13 } }
      }
    },
    plugins: { legend: { display: false } },
    animation: { duration: 400 }
  }
});

window.updateRadar = function() {
  if (!window._radarChart) return;
  window._radarChart.data.datasets[0].data = [
    parseFloat(getValueForVariable('technical')) || 0,
    parseFloat(getValueForVariable('communication')) || 0,
    parseFloat(getValueForVariable('leadership')) || 0,
    parseFloat(getValueForVariable('problemSolving')) || 0,
    parseFloat(getValueForVariable('creativity')) || 0,
    parseFloat(getValueForVariable('teamwork')) || 0
  ];
  window._radarChart.update();
};
updateRadar();
```

```javascript
JavaScriptAfterCalc:
updateRadar();
```

**Tips:**
- Define the chart instance and update function in `JavaScriptAfterLoad`, call the update function from `JavaScriptAfterCalc` - don't recreate the chart on each calc
- Use `getValueForVariable()` to read input values in JS - this is the bridge between Molnify's calc cycle and external libraries
- For computed values that aren't direct inputs, use hidden outputs with `variable=` (e.g., `ui="variable=derivedValue;hidden"`) and read them the same way
- The `class=` UI option is applied to `.panel-body`, not the outer `.panel` - use `.closest('.panel').find('.panel-body')` to navigate to the right container
- This technique works with any JS library that renders into a DOM element: Chart.js, D3, Leaflet, Three.js, etc.
