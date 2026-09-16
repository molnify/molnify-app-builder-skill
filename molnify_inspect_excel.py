#!/usr/bin/env python3
"""Inspect an Excel file to plan its conversion into, or changes to, a Molnify app.

Modes (default --overview):
  --overview              Sheets, sizes, Molnify cell counts, and workbook features
  --molnify               Molnify cells by role with their title and UI cells
  --search REGEX          Cell values, formulas and named ranges matching REGEX
  --range REF             Cells in 'Sheet!A1:D20', 'Sheet!B5' or 'Sheet', with full values
  --formulas              Distinct formulas, with filled-down/right copies collapsed
  --deps CELL             What one cell references and what references it
  --dependencies          Workbook-wide input/output/intermediate analysis

Every mode stops printing at MAX_OUTPUT_CHARS and reports what it left out.
"""

import argparse
import bisect
import re
import sys
import warnings
from collections import Counter, defaultdict
from openpyxl import load_workbook
from openpyxl.utils import get_column_letter, column_index_from_string
from openpyxl.worksheet.formula import ArrayFormula, DataTableFormula

from molnify_validate import color_matches_molnify, get_cell_color_hex


MAX_OUTPUT_CHARS = 30_000
SHORT_VALUE_CHARS = 120
RANGE_VALUE_CHARS = 500
MAX_EXCEL_ROWS = 1_048_576
MAX_EXCEL_COLS = 16_384

ROLE_ORDER = ['input', 'output', 'chart', 'action', 'metadata']


class Output:
    """Prints lines until the character budget is spent, then counts what was dropped.

    The budget keeps a reserve so the closing summary always fits.
    """

    def __init__(self, budget=MAX_OUTPUT_CHARS - 1_000):
        self.budget = budget
        self.used = 0
        self.dropped = 0
        self.full = False

    def line(self, text=''):
        if self.full:
            self.dropped += 1
            return
        if self.used + len(text) + 1 > self.budget:
            self.full = True
            self.dropped += 1
            return
        print(text)
        self.used += len(text) + 1

    def finish(self, hint, summary=None):
        if self.dropped:
            print(f"[output limit reached: {self.dropped} more lines not shown. {hint}]")
        if summary:
            print(summary)


def formula_text(value):
    """Return the formula string for a cell value, or None if it is not a formula.

    openpyxl stores array and data-table formulas as objects rather than strings.
    """
    if isinstance(value, ArrayFormula):
        return value.text
    if isinstance(value, DataTableFormula):
        return f"=TABLE({value.r1 or ''},{value.r2 or ''})"
    if isinstance(value, str) and value.startswith('='):
        return value
    return None


def display_value(value):
    """The formula text for formula cells, otherwise the raw value."""
    f = formula_text(value)
    return f if f is not None else value


def short(value, limit=SHORT_VALUE_CHARS):
    """One-line repr of a value, cut to limit with the full length noted."""
    if isinstance(value, str):
        s = value.replace('\r', '').replace('\n', '\\n')
        if len(s) > limit:
            return f'"{s[:limit]}…" ({len(value):,} chars)'
        return f'"{s}"'
    return repr(value) if value is not None else '(empty)'


def cell_role(cell):
    return color_matches_molnify(get_cell_color_hex(cell))


def quote_sheet(name):
    return f"'{name}'" if re.search(r"[^A-Za-z0-9_]", name) else name


def addr(sheet, coord):
    return f"{quote_sheet(sheet)}!{coord}"


def load(path):
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        return load_workbook(path)


# ---------------------------------------------------------------------------
# Formula reference parsing
# ---------------------------------------------------------------------------

_STRING_LITERAL = re.compile(r'"(?:[^"]|"")*"')
_SHEET = r"(?:'((?:[^']|'')+)'|([A-Za-z_][\w.]*))!"
_REF = re.compile(
    r"(?<![\w.$!:'])"
    r"(?:" + _SHEET + r")?"
    r"(?:"
    r"(\$?[A-Z]{1,3}\$?\d+)(?::(\$?[A-Z]{1,3}\$?\d+))?"   # A1 or A1:B2
    r"|(\$?[A-Z]{1,3}):(\$?[A-Z]{1,3})"                   # A:B
    r"|(\$?\d+):(\$?\d+)"                                 # 1:5
    r")"
    r"(?![\w(!])"
)
_NAME_TOKEN = re.compile(r"(?<![\w.$!'\"])([A-Za-z_\\][\w.]*)(?![\w(!])")
_CELL = re.compile(r"\$?([A-Z]{1,3})\$?(\d+)")


def strip_strings(formula):
    return _STRING_LITERAL.sub('""', formula)


def _cell_pos(text):
    m = _CELL.fullmatch(text)
    return column_index_from_string(m.group(1)), int(m.group(2))


def parse_ranges(formula, sheet, names=None):
    """Return the rectangles a formula references as (sheet, c1, r1, c2, r2) tuples.

    Whole columns and rows are bounded to Excel's limits. Named ranges are resolved when
    `names` maps lowercase names to rectangles. Structured table references and
    INDIRECT/OFFSET targets cannot be resolved statically and are not returned.
    """
    body = strip_strings(formula)
    found = []
    for m in _REF.finditer(body):
        ref_sheet = (m.group(1).replace("''", "'") if m.group(1) else m.group(2)) or sheet
        if m.group(3):
            c1, r1 = _cell_pos(m.group(3))
            c2, r2 = _cell_pos(m.group(4)) if m.group(4) else (c1, r1)
        elif m.group(5):
            c1 = column_index_from_string(m.group(5).lstrip('$'))
            c2 = column_index_from_string(m.group(6).lstrip('$'))
            r1, r2 = 1, MAX_EXCEL_ROWS
        else:
            r1, r2 = int(m.group(7).lstrip('$')), int(m.group(8).lstrip('$'))
            c1, c2 = 1, MAX_EXCEL_COLS
        found.append((ref_sheet, min(c1, c2), min(r1, r2), max(c1, c2), max(r1, r2)))
    if names:
        without_refs = _REF.sub(' ', body)
        for m in _NAME_TOKEN.finditer(without_refs):
            found.extend(names.get(m.group(1).lower(), ()))
    return found


def named_ranges(wb):
    """Map lowercase defined names to the rectangles they refer to."""
    result = defaultdict(list)
    scopes = [(None, wb.defined_names)] + [(ws.title, ws.defined_names) for ws in wb.worksheets]
    for scope, names in scopes:
        for name, dn in names.items():
            text = dn.attr_text or ''
            if text.startswith('='):
                text = text[1:]
            for rect in parse_ranges('=' + text, scope or ''):
                if rect[0]:
                    result[name.lower()].append(rect)
    return result


def all_defined_names(wb):
    """Yield (scope, name, reference) for workbook- and sheet-scoped defined names."""
    for name, dn in wb.defined_names.items():
        yield None, name, dn.attr_text
    for ws in wb.worksheets:
        for name, dn in ws.defined_names.items():
            yield ws.title, name, dn.attr_text


def rect_text(rect):
    sheet, c1, r1, c2, r2 = rect
    if r1 == 1 and r2 == MAX_EXCEL_ROWS:
        body = f"{get_column_letter(c1)}:{get_column_letter(c2)}"
    elif c1 == 1 and c2 == MAX_EXCEL_COLS:
        body = f"{r1}:{r2}"
    elif (c1, r1) == (c2, r2):
        body = f"{get_column_letter(c1)}{r1}"
    else:
        body = f"{get_column_letter(c1)}{r1}:{get_column_letter(c2)}{r2}"
    return f"{quote_sheet(sheet)}!{body}"


def relative_form(formula, row, col):
    """Rewrite A1 references relative to (row, col) so filled copies compare equal."""
    parts = re.split(r'("(?:[^"]|"")*")', formula)

    def rel(m):
        col_abs, col_s, row_abs, row_s = m.group(1), m.group(2), m.group(3), m.group(4)
        c = column_index_from_string(col_s)
        r = int(row_s)
        cpart = f"C{c}" if col_abs else f"C[{c - col}]"
        rpart = f"R{r}" if row_abs else f"R[{r - row}]"
        return rpart + cpart

    pattern = re.compile(r"(?<![\w.])(\$?)([A-Z]{1,3})(\$?)(\d+)(?![\w(])")
    return ''.join(p if i % 2 else pattern.sub(rel, p) for i, p in enumerate(parts))


def formula_blocks(cells):
    """Group (row, col, formula) cells into rectangles of identical relative formulas.

    Returns (top-left formula, c1, r1, c2, r2, count) sorted by position.
    """
    by_rel = defaultdict(list)
    for row, col, formula in cells:
        by_rel[relative_form(formula, row, col)].append((row, col, formula))
    blocks = []
    for members in by_rel.values():
        by_col = defaultdict(list)
        for row, col, formula in members:
            by_col[col].append((row, formula))
        runs = []
        for col, items in by_col.items():
            items.sort()
            start, prev, first = items[0][0], items[0][0], items[0][1]
            for row, formula in items[1:]:
                if row != prev + 1:
                    runs.append((start, prev, col, first))
                    start, first = row, formula
                prev = row
            runs.append((start, prev, col, first))
        runs.sort(key=lambda r: (r[0], r[1], r[2]))
        merged = []
        for r1, r2, col, formula in runs:
            last = merged[-1] if merged else None
            if last and (last[0], last[1]) == (r1, r2) and last[3] == col - 1:
                last[3] = col
            else:
                merged.append([r1, r2, col, col, formula])
        for r1, r2, c1, c2, formula in merged:
            blocks.append((formula, c1, r1, c2, r2, (c2 - c1 + 1) * (r2 - r1 + 1)))
    blocks.sort(key=lambda b: (b[2], b[1]))
    return blocks


def block_text(sheet, block):
    formula, c1, r1, c2, r2, count = block
    where = rect_text((sheet, c1, r1, c2, r2))
    copies = f" ({count:,} cells)" if count > 1 else ''
    return f"  {where}{copies}: {short(formula, 300)}"


# ---------------------------------------------------------------------------
# Modes
# ---------------------------------------------------------------------------

def mode_overview(wb, path, out):
    out.line(f"Workbook: {path}")
    names = list(all_defined_names(wb))
    out.line(f"Sheets: {len(wb.sheetnames)} ({len(wb.chartsheets)} chart sheets), "
             f"named ranges: {len(names)}, external links: {len(wb._external_links)}")
    out.line()

    fn_counts = Counter()
    for ws in wb.chartsheets:
        out.line(f"== {ws.title} (chart sheet, {ws.sheet_state})")
    for ws in wb.worksheets:
        cells = formulas = arrays = 0
        roles = Counter()
        for row in ws.iter_rows():
            for cell in row:
                if cell.value is not None:
                    cells += 1
                    f = formula_text(cell.value)
                    if f is not None:
                        formulas += 1
                        arrays += not isinstance(cell.value, str)
                        body = strip_strings(f)
                        fn_counts.update(re.findall(r"_xl(?:fn|udf|ws)\.[\w.]+?(?=\()", body))
                        fn_counts.update(m.upper() for m in re.findall(
                            r"\b(INDIRECT|OFFSET)\s*\(", body, re.IGNORECASE))
                        if re.search(r"\[\d+\]", body):
                            fn_counts['external workbook reference'] += 1
                role = cell_role(cell)
                if role:
                    roles[role] += 1
        state = '' if ws.sheet_state == 'visible' else f", {ws.sheet_state}"
        out.line(f"== {ws.title} ({ws.dimensions}{state})")
        a1 = ws['A1'].value
        if isinstance(a1, str) and 'molnify' in a1.lower():
            out.line(f"  A1: {short(a1)}")
        array_note = f" ({arrays:,} array)" if arrays else ''
        out.line(f"  {cells:,} cells, {formulas:,} formulas{array_note}")
        if roles:
            out.line("  Molnify cells: " + ', '.join(
                f"{roles[r]:,} {r}" for r in ROLE_ORDER if roles[r]))
        features = []
        if ws.merged_cells.ranges:
            features.append(f"{len(ws.merged_cells.ranges)} merged ranges")
        dv = ws.data_validations.dataValidation
        if dv:
            features.append(f"{len(dv)} data validations")
        cf = sum(len(r.rules) for r in ws.conditional_formatting)
        if cf:
            features.append(f"{cf} conditional formats")
        if ws._charts:
            features.append(f"{len(ws._charts)} charts")
        hidden_rows = sum(1 for d in ws.row_dimensions.values() if d.hidden)
        hidden_cols = sum(1 for d in ws.column_dimensions.values() if d.hidden)
        if hidden_rows or hidden_cols:
            features.append(f"hidden: {hidden_rows} rows, {hidden_cols} column groups")
        if features:
            out.line("  " + ', '.join(features))
        for table in ws.tables.values():
            out.line(f"  Excel table {table.displayName} ({table.ref})")
    out.line()

    if fn_counts:
        out.line("Formula features Molnify may not support: " + ', '.join(
            f"{k} ×{v}" for k, v in fn_counts.most_common()))
    if names:
        shown = names[:25]
        out.line(f"Named ranges ({len(names)}"
                 + (", first 25; search to find others" if len(names) > 25 else '') + "):")
        for scope, name, ref in shown:
            prefix = f"[{scope}] " if scope else ''
            out.line(f"  {prefix}{name} = {ref}")
    out.finish("Narrow with --molnify/--formulas --sheet, or --search.")


def _blue_blocks(cells):
    """Group chart cells into 4-connected rectangles' bounding boxes."""
    remaining = set(cells)
    blocks = []
    while remaining:
        stack = [remaining.pop()]
        members = []
        while stack:
            r, c = stack.pop()
            members.append((r, c))
            for n in ((r + 1, c), (r - 1, c), (r, c + 1), (r, c - 1)):
                if n in remaining:
                    remaining.remove(n)
                    stack.append(n)
        rows = [m[0] for m in members]
        cols = [m[1] for m in members]
        blocks.append((min(rows), min(cols), max(rows), max(cols)))
    return sorted(blocks)


def mode_molnify(wb, sheet_filter, out):
    for ws in wb.worksheets:
        if sheet_filter and ws.title != sheet_filter:
            continue
        a1 = ws['A1'].value
        if isinstance(a1, str) and a1.strip().lower() == 'molnifyignore':
            out.line(f"== {ws.title}: skipped (molnifyIgnore in A1)")
            continue
        by_role = defaultdict(list)
        for row in ws.iter_rows():
            for cell in row:
                role = cell_role(cell)
                if role:
                    by_role[role].append(cell)
        if not by_role:
            continue
        note = f" (A1: {short(a1)})" if isinstance(a1, str) and 'molnify' in a1.lower() else ''
        out.line(f"== {ws.title}{note}")

        def v(r, c):
            return ws.cell(row=r, column=c).value if c >= 1 else None

        for role in ('input', 'output'):
            if by_role[role]:
                out.line(f"{role.capitalize()}s:")
            for cell in by_role[role]:
                parts = [f"  {cell.coordinate}", f"title={short(display_value(v(cell.row, cell.column - 1)), 60)}",
                         f"value={short(display_value(cell.value))}"]
                ui = v(cell.row, cell.column + 1)
                if ui is not None:
                    parts.append(f"ui={short(display_value(ui), 200)}")
                if cell.comment:
                    parts.append(f"comment={short(cell.comment.text, 80)}")
                out.line(' '.join(parts))

        if by_role['chart']:
            out.line("Charts/tables:")
        for r1, c1, r2, c2 in _blue_blocks([(c.row, c.column) for c in by_role['chart']]):
            header = r1 - 1
            title = v(header, c1 - 1)
            series = [v(header, c) for c in range(c1, c2 + 1)]
            ui = None
            for c in range(c2 + 1, c2 + 4):
                if v(header, c) is not None:
                    ui = v(header, c)
                    break
            data = rect_text((ws.title, c1, r1, c2, r2)).split('!', 1)[1]
            labels = f"{get_column_letter(c1 - 1)}{r1}:{get_column_letter(c1 - 1)}{r2}" if c1 > 1 else '-'
            out.line(f"  {data} title={short(display_value(title), 60)} ui={short(display_value(ui), 120)} "
                     f"series={[display_value(s) for s in series][:8]} labels={labels}")

        if by_role['action']:
            out.line("Actions:")
        action_cells = sorted(by_role['action'], key=lambda c: (c.column, c.row))
        block = []
        for cell in action_cells + [None]:
            if block and (cell is None or cell.column != block[-1].column or cell.row != block[-1].row + 1):
                pairs = '; '.join(f"{display_value(v(c.row, c.column - 1))}={short(display_value(c.value), 60)}"
                                  for c in block)
                col = block[0].column_letter
                out.line(f"  {col}{block[0].row}:{col}{block[-1].row} {pairs}")
                block = []
            if cell is not None:
                block.append(cell)

        if by_role['metadata']:
            out.line("Metadata:")
        meta = {(c.row, c.column) for c in by_role['metadata']}
        for cell in by_role['metadata']:
            if (cell.row, cell.column - 1) in meta or cell.value is None:
                continue
            value_cell = ws.cell(row=cell.row, column=cell.column + 1)
            out.line(f"  {value_cell.coordinate} key={short(display_value(cell.value), 60)} "
                     f"value={short(display_value(value_cell.value))}")
    out.finish("Use --sheet to narrow, or --range for full values.")


def mode_search(wb, pattern, sheet_filter, out):
    try:
        regex = re.compile(pattern, re.IGNORECASE)
    except re.error as e:
        print(f"Invalid regex: {e}", file=sys.stderr)
        sys.exit(2)
    matches = 0
    for scope, name, ref in all_defined_names(wb):
        if sheet_filter and scope != sheet_filter:
            continue
        if regex.search(name) or regex.search(ref or ''):
            matches += 1
            prefix = f"[{scope}] " if scope else ''
            out.line(f"name {prefix}{name} = {ref}")
    for ws in wb.worksheets:
        if sheet_filter and ws.title != sheet_filter:
            continue
        for row in ws.iter_rows():
            for cell in row:
                if cell.value is None:
                    continue
                text = str(display_value(cell.value))
                m = regex.search(text)
                if not m:
                    continue
                matches += 1
                start = max(0, m.start() - 60)
                end = min(len(text), m.end() + 60)
                snippet = text[start:end].replace('\n', '\\n')
                context = ('…' if start else '') + snippet + ('…' if end < len(text) else '')
                length = f" ({len(text):,} chars)" if len(text) > 200 else ''
                role = cell_role(cell)
                tag = f" [{role}]" if role else ''
                out.line(f"{addr(ws.title, cell.coordinate)}{tag}{length}: {context}")
    out.finish("Refine the regex or add --sheet.", f"{matches} matches")


def _parse_target(wb, ref):
    """Parse 'Sheet!A1:B2', 'Sheet!A1' or 'Sheet' into (worksheet, c1, r1, c2, r2)."""
    m = re.fullmatch(r"(?:'((?:[^']|'')+)'|([^!]+?))(?:!(\$?[A-Z]{1,3}\$?\d+)(?::(\$?[A-Z]{1,3}\$?\d+))?)?", ref.strip())
    if not m:
        raise ValueError(f"Cannot parse reference: {ref}")
    sheet = m.group(1).replace("''", "'") if m.group(1) else m.group(2)
    if sheet not in wb.sheetnames or sheet not in [ws.title for ws in wb.worksheets]:
        raise ValueError(f"No worksheet named {sheet!r}. Sheets: {', '.join(wb.sheetnames)}")
    ws = wb[sheet]
    if not m.group(3):
        return ws, 1, 1, ws.max_column, ws.max_row
    c1, r1 = _cell_pos(m.group(3))
    c2, r2 = _cell_pos(m.group(4)) if m.group(4) else (c1, r1)
    return ws, min(c1, c2), min(r1, r2), max(c1, c2), max(r1, r2)


def mode_range(wb, ref, offset, out):
    ws, c1, r1, c2, r2 = _parse_target(wb, ref)
    single = (c1, r1) == (c2, r2)
    shown = 0
    for row in ws.iter_rows(min_row=r1, max_row=min(r2, ws.max_row), min_col=c1, max_col=min(c2, ws.max_column)):
        for cell in row:
            if cell.value is None and not single:
                continue
            value = display_value(cell.value)
            role = cell_role(cell)
            hexcolor = get_cell_color_hex(cell)
            tags = []
            if role:
                tags.append(role)
            elif hexcolor:
                tags.append(f"fill #{hexcolor}")
            if isinstance(cell.value, (ArrayFormula, DataTableFormula)):
                tags.append(f"array over {cell.value.ref}")
            tag = f" [{', '.join(tags)}]" if tags else ''
            if single and isinstance(value, str):
                budget = MAX_OUTPUT_CHARS - 200
                chunk = value[offset:offset + budget]
                end = offset + len(chunk)
                span = f" (chars {offset:,}-{end:,} of {len(value):,})" if offset or end < len(value) else ''
                print(f"{addr(ws.title, cell.coordinate)}{tag}{span}:")
                print(chunk)
                if end < len(value):
                    print(f"[value continues: rerun with --offset {end}]")
            else:
                text = short(value, RANGE_VALUE_CHARS)
                out.line(f"{cell.coordinate}{tag}: {text}")
            if cell.comment:
                out.line(f"  comment: {short(cell.comment.text, RANGE_VALUE_CHARS)}")
            shown += 1
    summary = None if single else f"{shown} non-empty cells in {rect_text((ws.title, c1, r1, c2, r2))}"
    out.finish("Request a smaller range, or a single cell for its full value.", summary)


def _sheet_formula_cells(ws):
    cells = []
    for row in ws.iter_rows():
        for cell in row:
            f = formula_text(cell.value)
            if f is not None:
                cells.append((cell.row, cell.column, f))
    return cells


def mode_formulas(wb, sheet_filter, out):
    for ws in wb.worksheets:
        if sheet_filter and ws.title != sheet_filter:
            continue
        cells = _sheet_formula_cells(ws)
        if not cells:
            continue
        blocks = formula_blocks(cells)
        out.line(f"== {ws.title}: {len(cells):,} formulas, {len(blocks):,} distinct blocks")
        for block in blocks:
            out.line(block_text(ws.title, block))
    out.finish("Use --sheet to narrow, or --search for specific functions.")


def mode_deps(wb, ref, out):
    ws, c, r, c2, r2 = _parse_target(wb, ref)
    if (c, r) != (c2, r2):
        raise ValueError("--deps takes a single cell, e.g. 'Sheet1!B5'")
    names = named_ranges(wb)
    cell = ws.cell(row=r, column=c)
    target = addr(ws.title, cell.coordinate)
    formula = formula_text(cell.value)
    role = cell_role(cell)
    out.line(f"{target}{' [' + role + ']' if role else ''} = {short(display_value(cell.value), 500)}")

    if formula is not None:
        out.line("References:")
        seen = set()
        for rect in parse_ranges(formula, ws.title, names):
            if rect in seen:
                continue
            seen.add(rect)
            sheet, pc1, pr1, pc2, pr2 = rect
            if (pc1, pr1) == (pc2, pr2) and sheet in wb.sheetnames and sheet in [w.title for w in wb.worksheets]:
                ref_cell = wb[sheet].cell(row=pr1, column=pc1)
                ref_role = cell_role(ref_cell)
                tag = f" [{ref_role}]" if ref_role else ''
                out.line(f"  {rect_text(rect)}{tag} = {short(display_value(ref_cell.value))}")
            else:
                out.line(f"  {rect_text(rect)} (range)")
        dynamic = re.findall(r"\b(INDIRECT|OFFSET)\s*\(", strip_strings(formula), re.IGNORECASE)
        if dynamic:
            out.line(f"  plus dynamic references via {', '.join(sorted(set(d.upper() for d in dynamic)))}")

    out.line("Referenced by:")
    count = 0
    for other in wb.worksheets:
        for row in other.iter_rows():
            for oc in row:
                f = formula_text(oc.value)
                if f is None:
                    continue
                for sheet, rc1, rr1, rc2, rr2 in parse_ranges(f, other.title, names):
                    if sheet == ws.title and rc1 <= c <= rc2 and rr1 <= r <= rr2:
                        count += 1
                        out.line(f"  {addr(other.title, oc.coordinate)} = {short(f, 200)}")
                        break
    out.finish("Search for the cell address to narrow the referencing formulas.",
               f"{count} formulas reference {target}")


class _Coverage:
    """Answers whether a cell lies in any referenced rectangle, per sheet and column."""

    def __init__(self, rects, max_cols):
        spans = defaultdict(list)
        for sheet, c1, r1, c2, r2 in rects:
            for col in range(c1, min(c2, max_cols.get(sheet, 0)) + 1):
                spans[(sheet, col)].append((r1, r2))
        self.starts = {}
        self.ends = {}
        for key, intervals in spans.items():
            intervals.sort()
            merged = []
            for s, e in intervals:
                if merged and s <= merged[-1][1] + 1:
                    merged[-1][1] = max(merged[-1][1], e)
                else:
                    merged.append([s, e])
            self.starts[key] = [m[0] for m in merged]
            self.ends[key] = [m[1] for m in merged]

    def covers(self, sheet, col, row):
        starts = self.starts.get((sheet, col))
        if not starts:
            return False
        i = bisect.bisect_right(starts, row) - 1
        return i >= 0 and row <= self.ends[(sheet, col)][i]


def mode_dependencies(wb, sheet_filter, out):
    names = named_ranges(wb)
    formula_cells = {}
    single_refs = Counter()
    range_refs = Counter()
    for ws in wb.worksheets:
        for row, col, f in _sheet_formula_cells(ws):
            formula_cells[(ws.title, row, col)] = f
            for rect in set(parse_ranges(f, ws.title, names)):
                sheet, c1, r1, c2, r2 = rect
                if (c1, r1) == (c2, r2):
                    single_refs[(sheet, r1, c1)] += 1
                else:
                    range_refs[rect] += 1

    max_cols = {ws.title: ws.max_column for ws in wb.worksheets}
    coverage = _Coverage(list(range_refs), max_cols)
    sheet_ok = (lambda s: s == sheet_filter) if sheet_filter else (lambda s: True)

    out.line("Potential INPUTS (non-formula cells referenced directly by a formula):")
    for (sheet, row, col), n in sorted(single_refs.items(), key=lambda kv: (kv[0][0], kv[0][1], kv[0][2])):
        if not sheet_ok(sheet) or (sheet, row, col) in formula_cells or sheet not in max_cols:
            continue
        cell = wb[sheet].cell(row=row, column=col)
        if cell.value is None:
            continue
        role = cell_role(cell)
        tag = f" [{role}]" if role else ''
        out.line(f"  {addr(sheet, cell.coordinate)}{tag} = {short(cell.value)} ({n} formulas)")

    out.line("Ranges referenced by formulas:")
    for rect, n in sorted(range_refs.items(), key=lambda kv: (kv[0][0], kv[0][2], kv[0][1])):
        if sheet_ok(rect[0]):
            out.line(f"  {rect_text(rect)} ({n} formulas)")

    outputs = defaultdict(list)
    intermediates = defaultdict(list)
    for (sheet, row, col), f in formula_cells.items():
        if not sheet_ok(sheet):
            continue
        referenced = (sheet, row, col) in single_refs or coverage.covers(sheet, col, row)
        (intermediates if referenced else outputs)[sheet].append((row, col, f))

    for label, groups in (("Potential OUTPUTS (formulas nothing references)", outputs),
                          ("Intermediate calculations (formulas other formulas reference)", intermediates)):
        out.line(f"{label}:")
        for sheet in [ws.title for ws in wb.worksheets]:
            for block in formula_blocks(groups.get(sheet, [])):
                out.line(block_text(sheet, block))
    out.finish("Use --sheet to narrow, or --deps for a single cell.")


def main():
    parser = argparse.ArgumentParser(
        description='Inspect an Excel file to plan its conversion into, or changes to, a Molnify app.')
    parser.add_argument('file', help='Excel file to inspect (.xlsx/.xlsm)')
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument('--overview', action='store_true', help='Workbook summary (default)')
    modes.add_argument('--molnify', action='store_true', help='Molnify cells by role')
    modes.add_argument('--search', metavar='REGEX', help='Case-insensitive search of values, formulas, names')
    modes.add_argument('--range', metavar='REF', help="Cells in 'Sheet!A1:D20', 'Sheet!B5' or 'Sheet'")
    modes.add_argument('--formulas', action='store_true', help='Distinct formulas, fill copies collapsed')
    modes.add_argument('--deps', metavar='CELL', help="References to and from one cell, e.g. 'Sheet1!B5'")
    modes.add_argument('--dependencies', action='store_true', help='Workbook-wide dependency analysis')
    parser.add_argument('--sheet', help='Limit --molnify, --search, --formulas or --dependencies to one sheet')
    parser.add_argument('--offset', type=int, default=0, help='Character offset for a single-cell --range')
    args = parser.parse_args()

    wb = load(args.file)
    if args.sheet and args.sheet not in wb.sheetnames:
        print(f"No sheet named {args.sheet!r}. Sheets: {', '.join(wb.sheetnames)}", file=sys.stderr)
        sys.exit(2)
    out = Output()
    try:
        if args.molnify:
            mode_molnify(wb, args.sheet, out)
        elif args.search is not None:
            mode_search(wb, args.search, args.sheet, out)
        elif args.range:
            mode_range(wb, args.range, max(args.offset, 0), out)
        elif args.formulas:
            mode_formulas(wb, args.sheet, out)
        elif args.deps:
            mode_deps(wb, args.deps, out)
        elif args.dependencies:
            mode_dependencies(wb, args.sheet, out)
        else:
            mode_overview(wb, args.file, out)
    except ValueError as e:
        print(str(e), file=sys.stderr)
        sys.exit(2)


if __name__ == '__main__':
    main()
