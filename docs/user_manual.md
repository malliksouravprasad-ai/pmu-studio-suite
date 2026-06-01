# PMU Studio Suite — User Manual

**Version:** 2.0 | **Date:** June 2026 | **Suite:** OSEPA PMU Tool Suite

---

## Live Application URLs (UAT)

| App | Name | URL |
|-----|------|-----|
| APP-001 | Monitoring Builder | https://pmu-001-monitoring-builder-4jlqk7zuya-el.a.run.app |
| APP-002 | Data Processing Studio | https://pmu-002-data-processing-studio-4jlqk7zuya-el.a.run.app |
| APP-003 | Analytics Studio | https://pmu-003-analytics-studio-4jlqk7zuya-el.a.run.app |
| APP-004 | Dashboard Studio | https://pmu-004-dashboard-studio-4jlqk7zuya-el.a.run.app |
| APP-005 | Deliverable Studio | https://pmu-005-deliverable-studio-4jlqk7zuya-el.a.run.app |
| APP-006 | Workflow Builder | https://pmu-006-workflow-builder-4jlqk7zuya-el.a.run.app |

> **Before starting:** Enter your name in the **Your Name / User Tag** field on each app's Workspace page. This isolates your workspaces from other users.

---

## About This Manual

This manual covers every function across all 6 PMU Studio applications and all 4 data input flows:

- **Flow A — File Upload:** Direct upload of CSV or Excel files
- **Flow B — Google Sheets & Forms:** Live connection to Google Sheets; data collection via Google Forms
- **Flow C — BigQuery:** Load pre-aggregated data from large datasets stored in Google BigQuery
- **Flow D — Apps Script:** Trigger an automated aggregation of a Google Sheet using a deployed Apps Script web app

Each section describes what to do and what comes out.

---

## Suite Overview

| App | Purpose | Primary Output |
|-----|---------|----------------|
| APP-001 | Monitoring Builder | Build monitoring frameworks, validation rules, KPI configs, Google Forms |
| APP-002 | Data Processing Studio | Clean, transform, standardise, and validate raw datasets |
| APP-003 | Analytics Studio | Aggregate data, compute KPIs, rank entities, analyse trends |
| APP-004 | Dashboard Studio | Build KPI cards, charts, and summary tables for reporting |
| APP-005 | Deliverable Studio | Generate Word, PowerPoint, PDF, and Excel reports |
| APP-006 | Workflow Builder | Track implementation progress across entities and stages |

---

## How Workspaces Work

All apps share a common workspace system.

- A workspace is the container for one project or assignment.
- Create it once in any app — it is visible in all other apps automatically.
- Enter your **User Tag** (name) so your workspaces stay separate from colleagues using the same system.
- Every file generated is saved to the workspace and registered with a unique PMU ID.

---

---

# Data Input Flows

This section explains each of the 4 ways data enters the PMU Studio Suite. Every app that loads data supports all 4 flows.

---

## Flow A — File Upload (CSV / Excel)

**When to use:** You have a file on your computer — downloaded from UDISE+, DISE, MIS, or any offline system.

**Supported file types:** `.csv`, `.xlsx`, `.xls`

**What to do:**
1. Go to the **Upload** tab in any app.
2. Click the **Upload File** tab.
3. Click **Browse** and select your file.
4. Click **Load File**.

**What comes out:**
- A data preview showing the first 20 rows.
- Column summary: total rows, column count, null counts per column, detected data types.

**Best for:** Historical data exports, UDISE+ DCF downloads, offline MIS data, district submission files.

---

## Flow B — Google Sheets & Forms

**When to use:** Data is being collected via Google Forms and is live in a Google Sheet, or the team is collaborating on a shared Sheet.

### B1 — Load from Google Sheet

**What to do:**
1. Go to the **Upload** tab in any app.
2. Click the **Google Sheet** tab.
3. Paste the full Google Sheet URL (the sheet must be either publicly readable or shared with the service account).
4. Click **Load Sheet**.

**What comes out:**
- Live data pulled from the sheet — exactly as it appears at that moment.
- Data preview with row/column summary.
- If the sheet is connected to a Google Form, responses appear as rows in real time.

**Best for:** UDISE+ DCF Google Form responses, survey data, real-time school submission data.

### B2 — Create a Google Form (APP-001 only)

**What to do:**
1. Complete the framework design in APP-001 (Schema + Form sections + Validation rules).
2. In **APP-001 → Package** tab, click **Create Google Form**.
3. The tool creates the form using your field definitions and section structure.
4. The response sheet URL is returned — paste this into APP-002 Upload to pull responses.

**What comes out:**
- A live Google Form with all fields, sections, and required field rules applied.
- A linked Google Sheet that receives all responses automatically.
- The response sheet URL ready to use in APP-002.

### B3 — Push Output to Google Sheet

**What to do:**
1. On the **Generate** tab of any app, look for **Push to Google Drive / Sheet**.
2. Click the button after generating your output.
3. The file is uploaded and a shareable link is returned.

**What comes out:**
- The Excel/report uploaded to Google Drive as a Google Sheet (for tabular outputs).
- A link to share with the team.

**Best for:** Sharing clean datasets with district officers; sharing dashboards with senior management.

---

## Flow C — BigQuery

**When to use:** Your dataset is too large for a spreadsheet (more than 50,000 rows), data lives in a government data warehouse or UDISE+ BigQuery instance, or you need to query across multiple years or states.

**Prerequisite:** Google Cloud credentials must be configured in the **Integrations** page of the app (one-time setup — see Integration Setup at end of this manual).

### C1 — Browse and Load a BigQuery Table

**What to do:**
1. Go to the **Upload** tab.
2. Click the **BigQuery** tab.
3. The connection status shows ✅ Connected (or 🔴 Not Connected — see Integration Setup).
4. Select a **Dataset** from the dropdown.
5. Select a **Table** from the dropdown.
6. To load a sample: set a row limit (e.g., 10,000) and click **Load Table**.
7. To load all rows: leave the limit blank and click **Load Table**.

**What comes out:**
- Data loaded directly from BigQuery into the app.
- The dataset never passes through Google Sheets — it comes directly into the PMU tool.
- Row/column preview same as file upload.

**Best for:** UDISE+ school-level data across all states; multi-year enrolment data; large district survey datasets with 100,000+ rows.

### C2 — Query BigQuery with Custom SQL

**What to do:**
1. Go to **Upload → BigQuery** tab.
2. Click **Custom SQL** mode.
3. Type your SQL query in the text box. Example:
   ```sql
   SELECT district_name, block_name, COUNT(*) AS school_count,
          AVG(enrolment_total) AS avg_enrolment
   FROM udise_dataset.schools_2025
   WHERE state_code = 'OD'
   GROUP BY district_name, block_name
   ```
4. Click **Run Query**.

**What comes out:**
- The query result is loaded as the working dataset.
- Since aggregation happens on BigQuery's servers, even queries over 10 lakh rows return in seconds.
- Row/column preview shown.

**Best for:** Pulling only the relevant columns and districts; pre-aggregating before loading; comparing two years of data in a single query.

### C3 — Push Output Back to BigQuery

**What to do:**
1. After generating outputs (clean data, KPI results, rankings), go to the **Generate** tab.
2. In the **Push to BigQuery** section:
   - Select the target dataset.
   - Enter a table name (or select an existing one).
   - Choose write mode: **Append** (add rows) or **Replace** (overwrite the table).
3. Click **Push**.

**What comes out:**
- Your processed output (e.g., district-level KPI scores) written back to BigQuery.
- Confirmation of rows written.

**Best for:** Building an analytical data warehouse; storing clean UDISE+ data for long-term tracking; feeding Power BI or Looker Studio directly from BigQuery.

---

## Flow D — Apps Script Aggregator

**When to use:** A colleague is maintaining a master Google Sheet that receives data from multiple districts. You want to automatically aggregate that sheet (sum by district, average by block) and write the result to a separate summary sheet — without manually doing it in Excel.

**Prerequisite:** The Apps Script web app must be deployed from your Google account. See Integration Setup at the end of this manual.

### D1 — Trigger an Aggregation via Apps Script

**What to do:**
1. In any app, go to **Generate → Apps Script Aggregator** tab (or open the **Integrations** page).
2. Enter the **Source Sheet URL** — the Google Sheet containing raw data.
3. Enter the **Target Sheet URL** — the Google Sheet where the aggregated result should be written.
4. Select the **Group-by columns** (e.g., District, Block).
5. Select the **Metric columns** to aggregate (e.g., Enrolment, Attendance).
6. Select the **Aggregation function**: SUM / AVERAGE / COUNT / MIN / MAX.
7. Click **Run Aggregator**.

**What comes out:**
- The Apps Script web app reads the source sheet on Google's servers.
- It runs the aggregation (GROUP BY District, SUM of Enrolment, etc.).
- It writes the result directly into the target sheet.
- The PMU tool confirms: "Aggregation complete — N rows written to [Target Sheet URL]."

**Best for:** Nightly rollup of district submission forms; consolidating 30 district sheets into one state-level summary; automating monthly reporting without opening Excel.

### D2 — Schedule Nightly Aggregation (Apps Script only)

**What to do:**
1. In the Apps Script editor (in Google Apps Script, not PMU Tools), run the function `setupNightlyTrigger()`.
2. This creates an automatic trigger: every night at 11 PM, the aggregation runs on its own.

**What comes out:**
- Every morning, the target Google Sheet has fresh aggregated data from the previous day's submissions.
- No manual steps required — the system runs automatically.

**Best for:** State-level UDISE+ data rooms; daily school attendance rollup; automated district compliance tracking.

---

---

# APP-001 — Monitoring Builder

**Purpose:** Design a complete monitoring framework — define data fields, collection form, validation rules, and KPI definitions — then generate all output artefacts.

**Data flows supported:** Flow B (Google Forms creation and output push to Drive)

---

## Use Case 1 — Build a New Monitoring Framework

**Scenario:** A PMU team is starting UDISE+ data collection for 2025-26. They need to define what data to collect, how to validate it, and what KPIs to track.

---

### Step 1 — Create Workspace

**What to do:** Go to **Workspace**, enter a name (e.g., `UDISE_2025_Odisha`) and project code (e.g., `UDISE`). Click **Create Workspace**.

**What comes out:** Active workspace. All outputs will be saved here.

---

### Step 2 — Define the Data Schema

**What to do:**
1. Go to the **Schema** tab.
2. To start from a template: select a template (School Monitoring / District Review / Survey / ATR / KPI Report) and click **Load Template**.
3. To add a field manually: fill in Field Label, Data Type (text / number / date / choice / boolean), Validation Rule, Example Value. Click **Add Field**.
4. To import column names from a file: click **Import from File**, upload a CSV/XLSX, select the column header row.

**What comes out:** A field-by-field data dictionary — the master list of every data point the programme will collect.

---

### Step 3 — Build the Form Structure

**What to do:**
1. Go to **Form** tab.
2. Click **Auto-Generate Sections** to group fields automatically, or create sections manually.
3. Assign fields to sections using the dropdown. Drag to reorder.

**What comes out:** Structured form layout in sections — the sequence in which data collectors will fill in data.

---

### Step 4 — Set Validation Rules

**What to do:**
1. Go to **Validation** tab.
2. Required field rules are auto-generated from the schema.
3. Add range rules (numeric min/max), pattern rules (UDISE code = 11 digits, phone = 10 digits), comparison rules (Actual ≤ Target), dependency rules (if field A is filled, field B must be filled).

**What comes out:** Complete validation rule list — used by APP-002 to automatically check incoming data.

---

### Step 5 — Define KPIs

**What to do:**
1. Go to **KPIs** tab.
2. For each KPI: enter name, select formula (Value / Ratio / Percentage), select numerator and denominator columns, set target, set interpretation (Higher is Better / Lower is Better), set weight.

**What comes out:** KPI definition table — used by APP-003 to calculate and score district performance.

---

### Step 6 — Generate All Outputs

**What to do:**
1. Go to **Package** tab.
2. Click **Generate Package**.
3. **Flow B — Create Google Form:** Click **Create Google Form**. A live form is created matching your schema and sections. The response sheet URL is returned.
4. Download each output file.

**What comes out:**
- `monitoring_template.xlsx` — Excel data entry template
- `validation_config.json` — Validation rules for APP-002
- `kpi_config.json` — KPI definitions for APP-003
- `form_structure.json` — Form layout definition
- Google Form (Flow B) — Ready-to-share data collection form linked to a live Google Sheet

---

---

# APP-002 — Data Processing Studio

**Purpose:** Take raw submitted data and produce a clean, validated, standardised dataset ready for analysis.

**Data flows supported:** Flow A (file upload), Flow B (Google Sheets), Flow C (BigQuery)

---

## Use Case 1 — Clean a UDISE+ Raw Data File (Flow A)

**Scenario:** UDISE+ DCF data has been downloaded as an Excel file. It has missing values, inconsistent district name spellings, and UDISE codes with incorrect digit counts.

---

### Step 1 — Open Workspace and Upload Data

**What to do:**
1. Go to **Workspace**, select the project.
2. Go to **Upload → Upload File** tab.
3. Upload the UDISE+ Excel file.

**What comes out:** Data preview — row count, column names, null counts per column.

---

### Step 2 — Clean the Data

**What to do:**
1. Go to **Clean** tab.
2. Add cleaning steps:
   - Fill missing values (Constant / Mean / Median / Mode)
   - Remove duplicate rows (select key columns: UDISE Code)
   - Strip whitespace from text columns (School Name, District, Block)
   - Standardise text case (UPPERCASE → Title Case)
3. Click **Run Cleaning Pipeline**.

**What comes out:** Cleaned dataset preview. Cleaning log: column, rows changed, before/after values.

---

### Step 3 — Transform the Data

**What to do:**
1. Go to **Transform** tab.
2. Add transform steps:
   - Rename columns to standard names
   - Delete columns not needed for analysis
   - Create calculated columns (e.g., `GER = Enrolled / Population * 100`)
   - Filter rows (e.g., keep only Odisha schools)
   - Sort rows (e.g., by District then School Name)
3. Toggle each step on/off without deleting.
4. Click **Run Transformation Pipeline**.

**What comes out:** Transformed dataset. Transformation log showing every step, rows in/out.

---

### Step 4 — Standardise Names (Fuzzy Matching)

**What to do:**
1. Go to **Map** tab.
2. Select the District column.
3. Choose master list: **District** (built-in Odisha list) or upload a custom reference CSV.
4. Set threshold (default 80).
5. Click **Run Matching**.
6. Review: Exact matches (auto-accepted) → Variant matches (auto-accepted) → Fuzzy matches (review each) → Unmatched (assign manually).
7. Click **Apply Mappings**.

**What comes out:** Standardised district/block names. Match report: original value, matched value, type, confidence score.

---

### Step 5 — Validate the Data

**What to do:**
1. Go to **Validate** tab.
2. Click **Load from Workspace** to load rules from APP-001's `validation_config.json`, or add rules manually:
   - Required: UDISE Code, School Name, District
   - Pattern: UDISE Code must match `^\d{11}$`
   - Range: Attendance % between 0 and 100
   - Type: Enrolment must be a positive integer
3. Click **Run All Validations**.

**What comes out:**
- Summary: total rows, passed, warnings, errors.
- Per-rule results: which rows failed each rule.
- Exception report: every row with its specific issues.

---

### Step 6 — Generate Outputs

**What to do:**
1. Go to **Generate** tab.
2. Click **Run Full Pipeline**.
3. Download clean dataset, transformation log, validation report.
4. **Flow B — Push to Google Sheet:** Click **Push to Google Drive** to upload the clean data as a shared sheet.
5. **Flow C — Push to BigQuery:** Enter dataset and table name, click **Push to BigQuery**.

**What comes out:**
- `clean_dataset.xlsx` — Final validated dataset
- `transformation_log.xlsx` — Complete audit trail of every change
- `validation_report.xlsx` — Exception register with row-level issues

---

## Use Case 2 — Process Live Google Form Responses (Flow B)

**Scenario:** Districts are submitting UDISE+ data via a Google Form. Responses are accumulating in a linked Google Sheet. Process them as they come in.

---

### Step 1 — Connect Google Sheet

**What to do:**
1. Go to **Upload → Google Sheet** tab.
2. Paste the Google Form response sheet URL.
3. Click **Load Sheet**.

**What comes out:** Live data pulled from the sheet — all responses to date.

### Step 2 to 6 — Same as Use Case 1

Run the same cleaning, transformation, matching, validation, and generation steps. Each time you reload the sheet, fresh responses are included.

---

## Use Case 3 — Process Large-Scale UDISE+ Data from BigQuery (Flow C)

**Scenario:** 1.5 lakh school records for all of India are stored in a BigQuery table. You need only Odisha data, pre-aggregated at district level.

---

### Step 1 — Query BigQuery

**What to do:**
1. Go to **Upload → BigQuery** tab.
2. Click **Custom SQL** mode.
3. Enter a query:
   ```sql
   SELECT district_name, block_name,
          COUNT(*) AS total_schools,
          SUM(enrolment_boys + enrolment_girls) AS total_enrolment,
          AVG(attendance_pct) AS avg_attendance
   FROM udise.schools_2025_26
   WHERE state_name = 'Odisha'
   GROUP BY district_name, block_name
   ```
4. Click **Run Query**.

**What comes out:** Pre-aggregated district/block data — only the rows and columns you need. BigQuery does the heavy aggregation on its servers.

### Step 2 — Clean, Validate, and Generate

Run the same pipeline as Use Case 1. The dataset is already aggregated, so cleaning is minimal.

---

---

# APP-003 — Analytics Studio

**Purpose:** Analyse clean datasets — aggregate, compute KPIs, rank entities, identify variances and trends.

**Data flows supported:** Flow A (file upload), Flow B (Google Sheets), Flow C (BigQuery load + push back), Flow D (Apps Script aggregation trigger)

---

## Use Case 1 — District KPI Scorecard from File (Flow A)

**Scenario:** Clean UDISE+ district data is ready. Generate KPI scores and rank all districts.

---

### Step 1 — Upload Data

**What to do:** Go to **Upload → Upload File**, load the clean dataset from workspace or upload a file.

---

### Step 2 — Build Aggregation

**What to do:**
1. Go to **Aggregate** tab.
2. Select group-by columns (e.g., `District`).
3. For each metric column, select aggregation: Sum / Average / Count / Min / Max.
4. Click **Add Aggregation**, then **Run Aggregations**.

**What comes out:** One row per district with all metric aggregations. Grand total row included.

---

### Step 3 — Calculate KPIs

**What to do:**
1. Go to **KPIs** tab.
2. Click **Load KPI Config** from workspace (from APP-001 output) or define manually.
3. Click **Calculate KPIs**.

**What comes out:** Per-district KPI scores, achievement % vs target, weighted composite score, green/amber/red status.

---

### Step 4 — Rank and Analyse

**What to do:**
1. Go to **Analyse** tab.
2. Set ranking mode: All / Top N / Bottom N / Weighted Composite.
3. Add variance analysis: select target column and actual column.
4. Click **Run**.

**What comes out:** Ranked district list. Variance table: target, actual, gap, % achievement.

---

### Step 5 — Trend Analysis

**What to do:**
1. Go to **Trends** tab.
2. Select period columns in order (e.g., Q1, Q2, Q3, Q4 enrolment).
3. Set interpretation (Higher is Better), change threshold (e.g., 5%).
4. Click **Analyse Trends**.

**What comes out:** Per-district trend: value in each period, direction (↑/↓/→), label (Improving / Declining / Stable). Period-by-period growth matrix.

---

### Step 6 — Generate Outputs

**What to do:**
1. Go to **Generate** tab.
2. Click **Generate All**.
3. **Flow C — Push to BigQuery:** Click **Push to BigQuery** to write KPI results back to a BigQuery table.
4. **Flow D — Trigger Apps Script:** Click **Run Apps Script Aggregator** to trigger aggregation of a Google Sheet directly.

**What comes out:**
- `aggregation.xlsx` — District/block aggregated data
- `kpi_report.xlsx` — KPI scores, composite scores, target comparison
- `analytics.xlsx` — Rankings, variances, trends in one workbook

---

## Use Case 2 — Analyse Live Google Sheet Data (Flow B)

**Scenario:** A district submission Google Sheet is being updated daily. Analyse today's data without downloading it.

**What to do:**
1. Go to **Upload → Google Sheet**, paste the sheet URL, click **Load Sheet**.
2. Run aggregation, KPI calculation, and ranking — same as Use Case 1.
3. At end of day, push results back to a summary Google Sheet via **Push to Drive**.

---

## Use Case 3 — Aggregate Directly via Apps Script (Flow D)

**Scenario:** A master Google Sheet collects daily school attendance from 30 districts. You want the nightly district-level summary without opening the app.

**What to do:**
1. Go to **Generate → Apps Script Aggregator** tab.
2. Set source sheet (master attendance sheet), target sheet (district summary), group by District, metric = Attendance Count, function = SUM.
3. Click **Run Aggregator**.

**What comes out:** The target Google Sheet is updated with fresh district totals. No file download or manual aggregation needed.

---

---

# APP-004 — Dashboard Studio

**Purpose:** Build KPI cards, charts, and summary tables — produces an Excel dashboard and dataset ready for reporting.

**Data flows supported:** Flow A (file upload), Flow B (Google Sheets), Flow C (BigQuery)

---

## Use Case 1 — Monthly Review Dashboard from File (Flow A)

**Scenario:** Monthly district review meeting. Build a dashboard Excel with KPI status and district rankings.

---

### Step 1 — Upload Dashboard Data

**What to do:** Go to **Upload → Upload File**, load analytics output or clean dataset. Enter dashboard title and project code.

---

### Step 2 — Add KPI Cards

**What to do:**
1. Go to **KPIs** tab.
2. For each KPI card: enter title, select source column, choose aggregation, enter unit, set target.
3. Click **Add KPI Card**.

**What comes out:** KPI cards with value, target, and status: ✅ On Target / ⚠️ Near Target / 🔴 Below Target.

---

### Step 3 — Add Charts

**What to do:**
1. Go to **Charts** tab, click **Add Chart**.
2. Select chart type (Bar / Line / Area / Pie), X-axis column, Y-axis column, aggregation, sorting.
3. Click **Save Chart**.

**What comes out:** Chart preview in browser. Chart definition saved for Excel output.

---

### Step 4 — Add Summary Tables

**What to do:**
1. Go to **Tables** tab.
2. Select group-by columns, metric columns, aggregation per metric, sorting, Top N, totals row.
3. Click **Add Table**.

**What comes out:** Summary table preview with aggregated district data.

---

### Step 5 — Generate Dashboard

**What to do:**
1. Go to **Generate** tab.
2. Click **Generate Dashboard**.
3. **Flow B — Push to Google Drive:** Click **Push to Drive** to upload as a Google Sheet.

**What comes out:**
- `dashboard.xlsx` — KPI cards, charts, tables in one formatted Excel
- `dashboard_dataset.xlsx` — Raw data behind the dashboard

---

## Use Case 2 — Dashboard from Live Google Sheet (Flow B)

**Scenario:** The analytics team maintains a live district data sheet. Pull it directly into the dashboard without downloading.

**What to do:**
1. Go to **Upload → Google Sheet**, paste the URL, click **Load Sheet**.
2. Build KPI cards, charts, and tables same as Use Case 1.
3. Push dashboard back to Drive when done.

---

## Use Case 3 — Dashboard from BigQuery (Flow C)

**Scenario:** UDISE+ all-India data is in BigQuery. Build a state-level KPI dashboard for Odisha.

**What to do:**
1. Go to **Upload → BigQuery**, write a query selecting Odisha district-level aggregates.
2. Load the result — only the pre-aggregated rows come into the app.
3. Build KPI cards and charts on the loaded data.

**What comes out:** Dashboard built from BigQuery data — handles millions of source rows without performance issues.

---

---

# APP-005 — Deliverable Studio

**Purpose:** Generate formatted reports — Word, PowerPoint, PDF, Excel — from structured data.

**Data flows supported:** Flow A (file upload), Flow B (Google Sheets), Flow C (BigQuery)

---

## Use Case 1 — Generate Quarterly District Report (Flow A)

**Scenario:** Quarterly programme report is due. Data is ready. Generate Word and PowerPoint outputs.

---

### Step 1 — Upload Reporting Data

**What to do:** Go to **Upload → Upload File**, load the clean analytics dataset.

---

### Step 2 — Set Report Details

**What to do:**
1. Go to **Report Details** tab.
2. Fill in: Report Title, Programme Name, Organisation, Author, Date, Description.
3. Select output formats: Excel / Word / PowerPoint / PDF.
4. Click **Save Details**.

**What comes out:** A unique PMU Report ID assigned (e.g., `PMU-2026-UDISE-REPORT-00001`).

---

### Step 3 — Define Report Sections

**What to do:**
1. Go to **Sections** tab, click **Add Section**.
2. For each section select type:
   - **Table** — aggregated data table (select group-by and metric columns)
   - **Narrative** — free-text paragraphs (type the text directly)
   - **Highlights** — top/bottom performers (select column and N)
3. Reorder sections using up/down arrows.

**What comes out:** Section list in report order with live preview.

---

### Step 4 — Generate Reports

**What to do:**
1. Go to **Generate** tab.
2. Click **Generate Reports**.
3. Download each format.

**What comes out:**
- `report.xlsx` — Excel report with one sheet per section
- `report.docx` — Formatted Word document with headings, tables, narrative text
- `report.pptx` — PowerPoint with one slide per section
- `report.pdf` — Print-ready PDF

---

## Use Case 2 — Report from Live Google Sheet (Flow B)

**What to do:**
1. Go to **Upload → Google Sheet**, paste the sheet URL, load.
2. Build sections and generate the report exactly as Use Case 1.
3. Each time you regenerate, the report reflects the latest sheet data.

---

## Use Case 3 — Report from BigQuery (Flow C)

**What to do:**
1. Go to **Upload → BigQuery**, run a query to pull pre-aggregated state/district summary.
2. Load the result and generate reports — handles large-scale UDISE+ or enrolment datasets.

---

## Use Case 4 — Segregated Reports by District

**Scenario:** Generate one separate report per district — one Excel per district, all in one ZIP.

**What to do:**
1. Upload district-level dataset (any flow).
2. In **Generate** tab, enable **Split by Column**.
3. Select the column to split on (e.g., `District`).
4. Click **Generate Segregated Reports**.

**What comes out:**
- One report per unique district value.
- All files bundled as a single ZIP download.

```
district_reports.zip
├── FLN_Report_Khordha.xlsx
├── FLN_Report_Puri.xlsx
├── FLN_Report_Cuttack.xlsx
... (one per district)
```

---

---

# APP-006 — Workflow Builder

**Purpose:** Track implementation progress across entities (districts, schools, blocks) through defined workflow stages.

**Data flows supported:** Flow A (entity list upload), Flow B (output push to Google Sheets)

---

## Use Case 1 — Track ATR Compliance Across Districts

**Scenario:** 30 districts have 6 action points from a review meeting. Track completion.

---

### Step 1 — Open Workspace

**What to do:** Go to **Workspace**, select or create the project workspace.

---

### Step 2 — Define the Workflow

**What to do:**
1. Go to **Define** tab.
2. Enter workflow name (e.g., `Q2 Review ATR`).
3. Select entity type (District / Block / School / Custom).
4. Upload entity list: **Flow A** — upload CSV with entity names in column 1, OR type entities manually.
5. Add stages (e.g., `Submit Utilisation Certificate`, `HM Orientation Completed`, `Data Verified`).
6. Load a template if available (ATR / Review / Training / Implementation).

**What comes out:** Entity list + stage list ready for tracking.

---

### Step 3 — Update Tracking

**What to do:**
1. Go to **Tracker** tab — rows = entities, columns = stages.
2. Click a cell → select status: Completed / In Progress / Pending / Overdue / N/A.
3. Add a remark and click **Save**.
4. Use **Bulk Update** to set the same status across many entities at once.

**What comes out:** Colour-coded matrix: ✅ green / 🔵 blue / ⬜ grey / 🔴 red. Progress % per entity. Live pendency list.

---

### Step 4 — Generate Outputs

**What to do:**
1. Go to **Generate** tab.
2. Click **Generate Tracker**.
3. **Flow B — Push to Google Sheets:** Click **Push to Drive** to upload tracker as a shared sheet.

**What comes out:**
- `tracker.xlsx` — Colour-coded tracking matrix with remarks and progress %
- `pendency_report.xlsx` — All Pending and Overdue items listed by entity
- Google Sheet (Flow B) — Live shared tracker for team collaboration

---

## Use Case 2 — UDISE+ Data Collection Monitoring

**Scenario:** Track which of 30 districts have completed each stage of UDISE+ DCF submission: Data Collected → Validated → Uploaded → Verified.

**What to do:**
1. Create workspace `UDISE_2025_Submission_Track`.
2. Entity type = District, upload 30 district names.
3. Add 4 stages matching the UDISE+ workflow.
4. Update as districts complete each stage.
5. Push the tracker to Google Sheets weekly for state-level review.

---

---

# Integration Setup Guide

This section covers the one-time setup required to enable Flow B (Google Sheets/Forms), Flow C (BigQuery), and Flow D (Apps Script).

---

## Setup 1 — Google Credentials (Flows B and C)

Required for: Loading Google Sheets, creating Google Forms, pushing outputs to Drive, connecting to BigQuery.

**On Streamlit Cloud / Cloud Run:**
1. In the app's **Integrations** page, the Secrets Configuration section shows a `secrets.toml` template.
2. Ask your system administrator to add the following to the app's secrets:

```toml
[gcp_service_account]
type = "service_account"
project_id = "your-gcp-project-id"
private_key_id = "..."
private_key = "-----BEGIN RSA PRIVATE KEY-----\n..."
client_email = "pmu-service@your-project.iam.gserviceaccount.com"
client_id = "..."
```

3. The service account needs these GCP permissions:
   - **Google Sheets API** — for reading/writing sheets
   - **Google Drive API** — for uploading files
   - **BigQuery Data Viewer + Job User** — for querying BigQuery

4. Once secrets are added and the app is redeployed, the **Integrations** page shows ✅ Google Connected and ✅ BigQuery Connected.

---

## Setup 2 — Apps Script Web App (Flow D)

Required for: Triggering automated aggregations on Google Sheets from within the PMU tools.

**Step 1 — Copy the template:**
1. Open Google Apps Script (`script.google.com`).
2. Create a new project.
3. Copy the contents of `templates/apps_script_aggregator.js` (available in the PMU Tools workspace) into the script editor.

**Step 2 — Deploy as Web App:**
1. In Apps Script, click **Deploy → New Deployment**.
2. Select type: **Web App**.
3. Set **Execute as**: Me.
4. Set **Who has access**: Anyone (or Anyone within your organisation).
5. Click **Deploy**.
6. Copy the **Web App URL** (looks like: `https://script.google.com/macros/s/AKfy.../exec`).

**Step 3 — Add URL to PMU Tools:**
1. Go to any app → **Integrations** page.
2. Paste the Web App URL into the **Apps Script Web App URL** field.
3. Click **Test Connection** — the status should show ✅ Connected.

**Step 4 — Nightly Trigger (optional):**
1. In the Apps Script editor, run the function `setupNightlyTrigger()`.
2. This sets a trigger to run the aggregation automatically every night at 11 PM.

---

## Setup 3 — Verifying Integration Status

Go to **Integrations** page in any app. The status chips show:

| Integration | Status Meaning |
|---|---|
| ✅ Google Connected | Sheets, Drive, Forms available |
| ✅ BigQuery Connected | BigQuery queries and writes available |
| ✅ Apps Script Connected | Apps Script aggregator available |
| 🔴 Not Connected | Credentials missing or invalid |

---

---

# Common Operations

## Artifact ID System

Every file generated is assigned a unique ID:
```
PMU-2026-UDISE-REPORT-00001
```
A `registry.csv` in the workspace records: artifact ID, app, date/time, output file, status.

---

## Saving and Loading Configurations

Every app saves configurations automatically. To reuse:
- Click **Save Config**, enter a name (e.g., `UDISE_KPI_v1`).
- Click **Load Config** to restore from the list.
- Click **Export Config** to download a `.pmuconfig` file for sharing.
- Click **Import Config** to load a colleague's config into your workspace.

---

## End-to-End Flow — All 4 Input Methods

```
Data Source
     │
     ├── Flow A: File Upload (CSV/XLSX from UDISE+, MIS, Excel)
     ├── Flow B: Google Sheets (Form responses, live shared sheets)
     ├── Flow C: BigQuery (large-scale, multi-year, server-side aggregation)
     └── Flow D: Apps Script (automated Google Sheet aggregation)
     │
     ▼
APP-002 Data Processing Studio
(Clean → Transform → Map → Validate)
     │
     ▼
APP-003 Analytics Studio
(Aggregate → KPIs → Rank → Trend)
     │
     ├─── APP-004 Dashboard Studio (KPI cards, charts, tables)
     │
     └─── APP-005 Deliverable Studio (Word, PPT, PDF, Excel reports)

APP-001 Monitoring Builder — design phase (creates framework, form, validation config)
APP-006 Workflow Builder — ongoing tracking (runs independently at any time)

Outputs can be pushed back via:
     Flow B → Google Drive / Sheets
     Flow C → BigQuery table
     Flow D → Apps Script → Target Google Sheet
```

---

*PMU Studio Suite — OSEPA | Version 2.0 | June 2026*
