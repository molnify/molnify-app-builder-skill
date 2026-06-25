# Database

Companion to the main reference.

## Table Setup

### Data Manager (Manual)
1. Set `ID` in metadata (required to keep table access after updates)
2. Access Data Manager from app sidebar or My Applications page
3. Create tables with "Create New Table" button
4. Tables auto-include: `_molnify_user_ip`, `_molnify_user_email`, `_molnify_application_id`, `_molnify_timestamp`

### Declarative Table Provisioning (DataTable Metadata)

Database tables can be created and managed declaratively via purple metadata cells. Tables are provisioned automatically on app upload - no Data Manager login required.

**Metadata key:** `DataTable.N` where N is 0-31 (maps to table `data_<appId>_N`)

**Value:** JSON object describing the table schema:

```json
{
  "columns": {
    "name": "VARCHAR",
    "email": {"type": "VARCHAR", "default": "unknown", "nullable": false},
    "amount": "DECIMAL",
    "created_at": {"type": "TIMESTAMP", "default": "CURRENT_TIMESTAMP"}
  },
  "indexes": {
    "idx_email": "email",
    "idx_compound": "col1,col2"
  },
  "access": ["other-app-id"]
}
```

**Columns** - keys are column names, values are either:
- A string: just the MySQL type
- An object with: `type` (required), `default`, `nullable` (default true), `autoIncrement` (default false)
- Use bare type names only (e.g. `DECIMAL`, not `DECIMAL(10,2)`). Default lengths are applied automatically: VARCHAR(255), CHAR(255), BINARY(255), VARBINARY(255), DECIMAL(10,2). Parameterized types are rejected by the backend.
- TIMESTAMP/DATETIME require an explicit `default` (e.g. `"CURRENT_TIMESTAMP"`)
- TEXT, TINYTEXT, MEDIUMTEXT, BLOB, TINYBLOB, MEDIUMBLOB, and JSON types cannot have a `default` value
- System columns (recordId, _molnify_*) are created automatically - do not declare them

Valid column types (these are MySQL types - do NOT use generic names like "STRING" or "NUMBER"):
| Category | Types |
|----------|-------|
| Text | `VARCHAR`, `TEXT`, `TINYTEXT`, `MEDIUMTEXT`, `CHAR` |
| Integer | `INT`, `TINYINT`, `SMALLINT`, `MEDIUMINT`, `BIGINT` (also with `UNSIGNED`) |
| Decimal | `DECIMAL`, `DOUBLE`, `FLOAT`, `REAL` |
| Boolean | `BOOL` (alias for TINYINT) |
| Date/Time | `DATETIME`, `TIMESTAMP` (require default), `DATE`, `TIME`, `YEAR` |
| Binary | `BLOB`, `TINYBLOB`, `MEDIUMBLOB`, `VARBINARY`, `BINARY` |
| Other | `JSON`, `SET`, `ENUM` |

Blocked types: `LONGTEXT`, `LONGBLOB`, and any type starting with `LONG`.

**Indexes** - keys are index names, values are comma-separated column names. Use `"primary"` as the index name to set a custom primary key (recordId will no longer be primary in that case).

**Access** - array of other app IDs to grant table access to. The uploader must be a superuser of each target app.

**Schema sync behavior:**
- The uploaded schema is the source of truth for declared tables
- Columns not in the schema (except system columns) are dropped
- New columns are added, type changes are applied
- Undeclared tables (not referenced by any DataTable.N) are never touched
- An empty value or `{}` drops the table if it exists

**Example - simple contacts app:**
```
DataTable.0  →  {"columns": {"name": "VARCHAR", "email": "VARCHAR", "phone": "VARCHAR", "notes": "TEXT"}}
```
This creates table `data_<appId>_0` with the four columns plus system columns.

---

## Writing Data

Use `insertrow` or `addrecord` actions to write to database tables. See the Actions Reference for full details.

### Unmodified inputs are not sent

Molnify's frontend only sends inputs the user has actually changed ("dirty" inputs) to the backend. If a user submits a form without modifying an input, that column is **not included** in the INSERT statement. This means:

- Database columns that correspond to inputs with default values **must** have a `DEFAULT` in the schema, or be `nullable`
- Otherwise the INSERT fails (NOT NULL violation) or the column silently stores NULL
- This applies to both `addrecord` and `insertrow` actions

**Example:** An input defaults to `"Food"` but the user never touches it - the backend never receives `"Food"`, so the `category` column must have `DEFAULT 'Food'` or allow NULL.

When using `DataTable.N`, set defaults explicitly:
```json
{"columns": {"category": {"type": "VARCHAR", "default": "Food"}}}
```

### Table name convention

Always use the full table name including `data_` prefix in all contexts: `RecordTableName` metadata, `insertrow.tablename`, autofill SQL, and `downloadquery` SQL. Tables created by `DataTable.N` are named `data_<appId>_N` (e.g., `data_my-app_0`).

The `insertrow` action auto-adds `data_` if missing, but the other contexts do not. To avoid confusion, always include it.

### Date inputs and database storage

Date inputs (with `UI: date`) are stored as **formatted text strings**, not as SQL date types or Excel serial numbers. When writing date values to a database:

- Use `VARCHAR` column type, not `DATE` or `DATETIME`
- The value is stored as the formatted string (e.g., `"2024-03-15"`)
- If you need date sorting/filtering in SQL, you can use `STR_TO_DATE()` in queries

---

## Reading Data

### Autofill

Populate named ranges with data from database queries at calculation time. Autofill is configured via purple metadata cells.

**Setup:**
1. Define a **named range** in Excel (e.g., `clients` spanning `Sheet1!A1:B10`)
2. Add a purple metadata cell with key `autofill.clients`
3. Set the metadata value to a SQL query:
```
autofill.clients: SELECT name, id FROM `data_my-app_clients`
```

**How it works:**
- When the app calculates, the named range is **cleared first** (removes stale data from previous calculations), then the SQL query runs and fills it row by row, column by column
- Autofills execute **before** all other calculations, so outputs and formulas can reference the populated data
- If the query returns fewer rows than the range, remaining cells stay empty (they were cleared). **Note:** these "empty" cells hold the value `""` (empty string), so `COUNTA` will count them. Use `COUNTIF(range,"<>")` instead
- If the query returns more rows than the range, extra rows are silently skipped
- All query results are retrieved as strings. Values that look numeric (including comma-decimal like `"1,5"` → `1.5`) are stored as numbers; everything else is stored as text

**Using autofilled data:**
The populated named range can be used in:
- Data validation lists (for dynamic dropdowns)
- `VLOOKUP`, `INDEX`/`MATCH` formulas
- Table displays
- Any formula that references the named range

**Dynamic queries with formulas:**
The metadata value can be an Excel formula that builds the SQL dynamically:
```
autofill.items: ="SELECT name, price FROM data_my-app_items WHERE category = '" & B5 & "'"
```

**Constraints:**
- **`@variable` syntax is not supported** - unlike database dropdown `filter` options, autofill SQL does not resolve `@variable` placeholders. Use a formula to build dynamic SQL instead (see example above)
- Database tables created by `DataTable.N` are named `data_<appId>_N` (e.g., `data_my-app_0`)
- Only tables belonging to the app's ID are accessible (unless granted via `access` in DataTable). The backend validates table access before executing the query - unauthorized tables produce an error
- If the app ID contains hyphens, you must backtick-quote the table name in SQL: `` SELECT * FROM `data_my-app_0` `` - otherwise MySQL interprets the hyphen as subtraction
- If the query returns zero rows or fails to parse, the range stays cleared with no error shown to the user
- Queries are **read-only** and the backend does not allow multiple statements in a single query, so SQL injection from user input in dynamic queries is not a practical concern

**Autofill requires a calculation to populate.** Autofill data (SQL queries and API calls) is only executed during a calculation cycle. Although `AutoCalcEnabled` is TRUE by default, auto-calc only triggers when an input *changes* - it does not run on initial page load unless something triggers a calculation (e.g., inputs with `user.email` or other user context variables that set a value on load). This means apps that rely solely on autofill will appear empty until the user changes an input or manually clicks Calculate.

To fix this, add a `JavaScriptAfterLoad` metadata entry that triggers a calculation on load:
```
JavaScriptAfterLoad: calculateButton();
```

### Database Dropdowns

Database dropdowns populate a Select2 dropdown from a database table. When the user selects a row, mapped columns are automatically written into app input variables.

There are two types. Both share these options:

| UI Option | Description | Default |
|-----------|-------------|---------|
| `display` | Column name or `&`-concatenation expression to show in the dropdown | ID column |
| `filter` | SQL WHERE clause with `@variable` references for dynamic filtering | - |
| `orderBy` | SQL ORDER BY clause | `_molnify_timestamp DESC` (if column exists) |
| `maxRows` | Maximum rows returned | 1000 |

#### RecordDropdown (`UI: recorddropdown`)

Loads rows from the app's configured record table (`RecordTableName` metadata) - uses the shared options above. When a row is selected, all table columns that match an app input variable name are automatically populated. Access control is enforced via `RecordTableAccessColumn` metadata - users only see rows where their email matches the access column value.

```
UI: recorddropdown;display=customerName&' ('&city&')'
```

#### RowDropdown (`UI: rowdropdown`)

Loads rows from any specified database table. Shared options above, plus:

| UI Option | Description | Default |
|-----------|-------------|---------|
| `tableName` | Table to query (the `data_` prefix is added automatically if missing) | (required) |
| `idVariable` | Column to use as the row ID | "recordId" |
| `map` | Explicit column-to-variable mapping: `col1->var1,col2->var2` | - |

When a row is selected, mapped columns are set on the corresponding input variables.

```
UI: rowdropdown;tableName=data_my-app_0;idVariable=custId;display=firstName&' '&lastName;map=firstName->custFirst,lastName->custLast;filter=country=@selectedCountry
```

#### Display expressions

The `display` option supports Excel-style `&` concatenation, which is converted to SQL `CONCAT()`:
- `firstName&' '&lastName` becomes `CONCAT(firstName,' ',lastName)`
- SQL functions are also supported: `firstName&' '&COALESCE(middleName,'')&' '&lastName`

#### Filter with @variables

The `filter` option supports `@variableName` placeholders that are resolved from current input values (parameterized, not interpolated - safe from SQL injection):
```
filter=status=@selectedStatus AND region=@selectedRegion
```

### Download Query Action

Use `downloadquery` actions to export query results as CSV or JSON files. See the Actions Reference for details.
