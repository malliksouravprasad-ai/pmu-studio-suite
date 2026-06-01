# PMU Studio Suite — User Manual

**Version:** 1.1 | **Date:** June 2026 | **Suite:** OSEPA PMU Tool Suite

---

## Live Application URLs (UAT)

Use these links to access the live applications hosted on Google Cloud Run for User Acceptance Testing:

| App | Name | UAT URL |
|-----|------|---------|
| APP-001 | Monitoring Builder | https://pmu-001-monitoring-builder-4jlqk7zuya-el.a.run.app |
| APP-002 | Data Processing Studio | https://pmu-002-data-processing-studio-4jlqk7zuya-el.a.run.app |
| APP-003 | Analytics Studio | https://pmu-003-analytics-studio-4jlqk7zuya-el.a.run.app |
| APP-004 | Dashboard Studio | https://pmu-004-dashboard-studio-4jlqk7zuya-el.a.run.app |
| APP-005 | Deliverable Studio | https://pmu-005-deliverable-studio-4jlqk7zuya-el.a.run.app |
| APP-006 | Workflow Builder | https://pmu-006-workflow-builder-4jlqk7zuya-el.a.run.app |

> **Before starting UAT:** Enter your name in the **Your Name / User Tag** field on each app's Workspace page. This keeps your workspaces separate from other testers.

---

## About This Manual

This manual covers every function available across all 6 PMU Studio applications.

Each section describes:
- **What to do** — the actions the user takes
- **What comes out** — the deliverable or result

---

## Suite Overview

| App | Purpose | Primary Output |
|-----|---------|----------------|
| APP-001 Monitoring Builder | Build monitoring frameworks and data collection tools | Excel template, validation config, Google Form |
| APP-002 Data Processing Studio | Clean, transform, and validate raw datasets | Clean dataset, transformation log, validation report |
| APP-003 Analytics Studio | Aggregate data, compute KPIs, rank districts/blocks | KPI report, analytics workbook, trend analysis |
| APP-004 Dashboard Studio | Build dashboard-ready data views with KPI cards and charts | Dashboard Excel, dataset |
| APP-005 Deliverable Studio | Generate formatted reports in Word, PowerPoint, PDF, Excel | Report in multiple formats |
| APP-006 Workflow Builder | Track implementation progress across entities and stages | Tracker Excel, pendency report |

---

## How Workspaces Work

All apps use a **Workspace** as the container for a project or assignment.

- A workspace stores your data, configurations, and outputs in one folder.
- Once you create a workspace in any app, it is available across all apps.
- You never lose your work between sessions — everything saves automatically to the workspace.

---

---

# APP-001 — Monitoring Builder

**Purpose:** Design a complete monitoring framework for a programme — define what data to collect, how to validate it, what KPIs to track, and generate the collection tool.

---

## Use Case 1 — Build a New Monitoring Framework from Scratch

**Scenario:** A PMU team is starting a new programme and needs to define what data will be collected from districts/blocks, what the form will look like, and what quality checks will apply.

---

### Step 1 — Open or Create a Workspace

**What to do:**
1. Go to the **Workspace** tab.
2. Type a workspace name (e.g., `FLN_Programme_2026`).
3. Type a project code (e.g., `FLN`).
4. Click **Create Workspace**.

**What comes out:**
- A named workspace is created and set as active.
- All subsequent work in this session will be saved to this workspace.

---

### Step 2 — Define the Data Schema

**What to do:**
1. Go to the **Schema** tab.
2. To start from a template: select one of the 5 built-in templates (School Monitoring, District Review, Survey, ATR Tracker, KPI Report) and click **Load Template**.
3. To add a field manually: fill in Field Label, select Data Type (text/number/date/choice/boolean), add a Validation Rule, and add an Example Value. Click **Add Field**.
4. To import from an existing Excel/CSV: click **Import from File**, upload the file, and select the column that contains field names.
5. To edit or delete a field: use the table controls next to each row.

**What comes out:**
- A field-by-field data dictionary showing: Field Label, Data Type, Required (yes/no), Validation Rule, Example.
- This becomes the master list of all data points the programme will collect.

---

### Step 3 — Build the Form Structure

**What to do:**
1. Go to the **Form** tab.
2. To auto-generate sections: click **Auto-Generate Sections** — the tool groups fields by type.
3. To create a section manually: type a section title (e.g., `School Information`) and click **Add Section**.
4. For each section: select which fields belong to it from the dropdown and click **Assign Fields**.
5. Review the form preview showing sections and their fields.

**What comes out:**
- A structured form layout showing sections in sequence with assigned fields.
- This is the logical order in which data collectors will fill in the form.

---

### Step 4 — Set Validation Rules

**What to do:**
1. Go to the **Validation** tab.
2. Required field rules are auto-generated from your schema — review them.
3. To add a range rule: select a numeric column, set minimum and maximum values, set severity (Error/Warning/Info), and click **Add Rule**.
4. To add a pattern rule: select a text column, enter a regex or format pattern, and click **Add Rule**.
5. To add a comparison rule: select two columns, choose the operator (greater than, equal to, etc.), and click **Add Rule**.

**What comes out:**
- A complete validation rule list showing: Rule Type, Column(s), Parameters, Severity.
- This rule set will be used by APP-002 to check incoming data automatically.

---

### Step 5 — Define KPIs

**What to do:**
1. Go to the **KPIs** tab.
2. To add a KPI: type the KPI name, select the formula type (Value / Ratio / Percentage), select the numerator column, select the denominator column (if applicable), set a target value, and set interpretation (Higher is Better / Lower is Better).
3. Set the weight for each KPI (used in composite score calculations).
4. In the **Aggregation Config** section: define how data should be grouped (e.g., by District) and which metrics to aggregate.

**What comes out:**
- A KPI summary table: KPI name, formula, target, weight, interpretation.
- An aggregation configuration that tells analytics tools how to roll up the data.

---

### Step 6 — Generate All Outputs

**What to do:**
1. Go to the **Package** tab.
2. Review the framework summary (field count, rule count, KPI count).
3. Click **Generate Package**.
4. To create a Google Form: click **Create Google Form** (requires Google credentials).
5. Click each **Download** button to save the output files.

**What comes out:**
- `monitoring_template.xlsx` — Excel data entry template with field headers and dropdowns.
- `validation_config.json` — Validation rules in machine-readable format (used by APP-002).
- `kpi_config.json` — KPI definitions (used by APP-003).
- `form_structure.json` — Form layout definition.
- Google Form (if created) — Ready-to-share data collection form linked to a Google Sheet.
- A workspace `.pmupack` export bundling all artifacts.

---

## Use Case 2 — Adapt an Existing Framework

**Scenario:** A framework was built last quarter. This quarter the programme has added 3 new indicators.

**What to do:**
1. Open the workspace used last quarter.
2. In **Schema**: add the 3 new fields.
3. In **Validation**: add rules for the new fields.
4. In **KPIs**: add the 3 new KPI definitions.
5. In **Package**: re-generate. The tool creates a new version automatically (v2).

**What comes out:**
- Updated output files saved alongside the previous version.
- No previous work is lost — versions are preserved in the workspace.

---

---

# APP-002 — Data Processing Studio

**Purpose:** Take raw data submitted by districts/schools and produce a clean, validated, standardised dataset ready for analysis.

---

## Use Case 1 — Clean and Validate a Raw Submission

**Scenario:** 200 rows of data have been submitted via Google Sheets or Excel. The data has missing values, spelling variations for district names, and some invalid entries.

---

### Step 1 — Open Workspace

**What to do:**
1. Go to **Workspace**, select the project workspace.

**What comes out:**
- Workspace is active. Any outputs saved here will be accessible in APP-003 and APP-004.

---

### Step 2 — Upload the Raw Data

**What to do:**
1. Go to the **Upload** tab.
2. To upload a file: click **Upload File** and select your CSV or XLSX.
3. To connect a Google Sheet: paste the sheet URL and click **Load Sheet**.
4. To use data already in the workspace: click **Load from Workspace** and select the file.

**What comes out:**
- A data preview showing the first rows of the file.
- Column statistics: row count, column count, missing value counts per column.

---

### Step 3 — Clean the Data

**What to do:**
1. Go to the **Clean** tab.
2. To handle missing values: select the column, choose a fill method (Constant value / Mean / Median / Mode), enter the fill value if constant, and click **Add Step**.
3. To remove duplicates: select the columns to check for duplicates and click **Add Step**.
4. To standardise text case: select a text column, choose (UPPER / lower / Title Case) and click **Add Step**.
5. To remove leading/trailing whitespace: select columns and click **Add Step**.
6. Click **Run Cleaning Pipeline** to apply all steps.

**What comes out:**
- A cleaned dataset preview.
- A cleaning log showing: step name, column affected, rows changed, before/after counts.

---

### Step 4 — Transform the Data

**What to do:**
1. Go to the **Transform** tab.
2. To rename a column: select the column, type the new name, click **Add Step**.
3. To delete columns: select columns to remove, click **Add Step**.
4. To merge two columns: select the columns, enter a separator (e.g., ` - `), name the new column, click **Add Step**.
5. To create a calculated column: enter a formula (e.g., `col_a / col_b * 100`), name the result column, click **Add Step**.
6. To filter rows: select a column, choose operator (equals / greater than / contains / is not empty), enter value, click **Add Step**.
7. To sort rows: select a column, choose ascending or descending, click **Add Step**.
8. Use the toggle switches to enable/disable individual steps without deleting them.
9. Click **Run Transformation Pipeline**.

**What comes out:**
- Transformed dataset preview.
- A transformation log listing every step applied and the row/column counts after each step.

---

### Step 5 — Standardise Names (Fuzzy Matching)

**What to do:**
1. Go to the **Map** tab.
2. Select the column to standardise (e.g., District Name).
3. Choose a master list: **Built-in** (District / Block / Yes-No) or **Custom** (upload your own reference list CSV).
4. Set the matching threshold (default 80 — lower finds more matches, higher is more precise).
5. Click **Run Matching**.
6. Review results by category:
   - **Exact matches** — automatically accepted.
   - **Variant matches** — common spelling variants, auto-accepted.
   - **Fuzzy matches** — review each suggestion and approve or reject.
   - **Unmatched** — entries with no match found; assign manually.
7. Click **Apply Mappings**.

**What comes out:**
- A matched dataset with standardised names replacing raw entries.
- A match report showing: original value, matched value, match type, confidence score.

---

### Step 6 — Validate the Data

**What to do:**
1. Go to the **Validate** tab.
2. To load validation rules from APP-001: click **Load from Workspace** and select the `validation_config.json`.
3. To add a manual rule: select rule type (Required / Type Check / Range / Pattern / Comparison / Dependency / Consistency), configure parameters, click **Add Rule**.
4. Click **Test Rule** on any rule to preview failures before running all.
5. Click **Run All Validations**.

**What comes out:**
- A validation summary: total rows, pass count, warning count, error count.
- A per-rule result showing which rows failed each rule.
- An exception report listing every row with issues and the rules they violated.

---

### Step 7 — Generate Final Clean Dataset

**What to do:**
1. Go to the **Generate** tab.
2. Review the pipeline summary (stages, steps count, rows in/out).
3. Click **Run Full Pipeline** to apply all stages in sequence.
4. Click **Download Clean Dataset** (XLSX).
5. Click **Download Transformation Log** (XLSX).
6. Click **Download Validation Report** (XLSX).
7. To push to Google Drive/Sheets: click **Push to Google Drive**.

**What comes out:**
- `clean_dataset.xlsx` — The final cleaned and validated dataset.
- `transformation_log.xlsx` — Complete record of every change applied to the data.
- `validation_report.xlsx` — Full exception register with row-level issues.
- Google Sheet (if pushed) — Live sheet with clean data for team review.

---

### Step 8 — Review Full Pipeline (Optional)

**What to do:**
1. Go to **Pipeline Overview**.
2. Select a sample size (5 to 100 rows).
3. Click **Run Sample**.

**What comes out:**
- A visual flow diagram showing: Upload → Clean → Transform → Map → Validate → Output.
- Stage-by-stage statistics: rows in, rows out, columns in, columns out.
- A preview of the final output sample.

---

---

# APP-003 — Analytics Studio

**Purpose:** Analyse clean datasets — aggregate by district/block, calculate KPIs, rank entities, analyse variances and trends.

---

## Use Case 1 — Generate District-Level KPI Report

**Scenario:** Clean data is available for 30 districts. Generate KPI scores, rank districts, and identify underperformers.

---

### Step 1 — Upload Data

**What to do:**
1. Go to **Workspace**, select the project.
2. Go to **Upload**, load the clean dataset from the workspace or upload a file.

**What comes out:**
- Data preview with row/column summary.

---

### Step 2 — Build Aggregation

**What to do:**
1. Go to the **Aggregate** tab.
2. Select group-by columns (e.g., `District`, `Block`).
3. For each metric column, select the aggregation function: Sum / Average / Count / Min / Max.
4. Click **Add Aggregation**.
5. Click **Run Aggregations**.

**What comes out:**
- An aggregated table: one row per district/block showing all metric aggregations.
- Row counts per group.

---

### Step 3 — Calculate KPIs

**What to do:**
1. Go to the **KPIs** tab.
2. To load KPI definitions from APP-001: click **Load KPI Config** from workspace.
3. To define a KPI manually: enter name, select formula type (Value / Ratio / Percentage), select numerator/denominator columns, set target, set weight.
4. Click **Calculate KPIs**.

**What comes out:**
- A KPI results table showing each entity's score on each KPI vs target.
- A weighted composite score for each entity.
- Colour indicators (green/amber/red) based on target achievement.

---

### Step 4 — Rank and Analyse

**What to do:**
1. Go to the **Analyse** tab.
2. Select the entity column (e.g., `District`).
3. Select the value column (e.g., composite KPI score).
4. Choose ranking mode: All / Top N / Bottom N / Weighted Score.
5. Click **Run Ranking**.
6. To add a variance analysis: select a target column and an achievement column, click **Add Variance Analysis**, then **Run**.

**What comes out:**
- A ranked list of all entities (e.g., District 1 ranked 1st, District 2 ranked 2nd).
- A variance table: target vs achievement, absolute variance, percentage variance.

---

### Step 5 — Trend Analysis

**What to do:**
1. Go to the **Trends** tab.
2. Select the entity column.
3. Select the period columns in chronological order (e.g., `April`, `May`, `June`).
4. Set interpretation (Higher is Better / Lower is Better).
5. Set the change threshold percentage (e.g., 5% change = significant).
6. Click **Analyse Trends**.

**What comes out:**
- A trend table per entity showing: value in each period, direction (↑/↓/→), trend label (Improving / Declining / Stable).

---

### Step 6 — Generate Analytics Outputs

**What to do:**
1. Go to **Generate**.
2. Review the analysis summary (aggregations done, KPIs calculated, rankings run).
3. Click **Generate All**.
4. Download each file or push to Google Drive.

**What comes out:**
- `aggregation.xlsx` — District/block level aggregated data.
- `kpi_report.xlsx` — KPI scores, composite scores, target comparison.
- `analytics.xlsx` — Complete workbook with rankings, variances, trends.
- Google Sheets (if pushed) — All three sheets in one Google Workbook.

---

---

# APP-004 — Dashboard Studio

**Purpose:** Build a structured dashboard view with KPI cards, charts, and summary tables — produces an Excel dashboard workbook ready for reporting.

---

## Use Case 1 — Build a Monthly Review Dashboard

**Scenario:** Monthly district review is coming up. Build a dashboard Excel showing KPI status, a bar chart of district scores, and a summary table.

---

### Step 1 — Upload Dashboard Data

**What to do:**
1. Go to **Workspace**, select the project.
2. Go to **Upload**, load the analytics output or clean dataset.
3. Enter a dashboard title (e.g., `Monthly Review — June 2026`) and project code.

**What comes out:**
- Data loaded and confirmed with row/column count.

---

### Step 2 — Add KPI Cards

**What to do:**
1. Go to the **KPIs** tab.
2. For each KPI card: enter a title (e.g., `Enrolment Rate`), select the source column, choose aggregation (Sum / Average / Count), enter the unit (%, number, etc.), and set a target if applicable.
3. Click **Add KPI Card**.
4. Review the KPI card preview showing value, target, and status icon (✅ on target / ⚠️ near target / 🔴 below target / 🔵 no target).

**What comes out:**
- A set of KPI cards displaying current values with status indicators.

---

### Step 3 — Add Charts

**What to do:**
1. Go to the **Charts** tab.
2. Click **Add Chart**.
3. Select chart type: Bar / Line / Area / Pie.
4. Select the X-axis column (e.g., `District`).
5. Select the Y-axis column (e.g., `Composite Score`).
6. Choose aggregation for the Y-axis.
7. Set sorting (none / ascending / descending) and whether to stack (for multi-series).
8. Click **Save Chart** — a preview appears.

**What comes out:**
- A chart preview rendered in the browser.
- Chart definition saved for inclusion in the output Excel.

---

### Step 4 — Add Summary Tables

**What to do:**
1. Go to the **Tables** tab.
2. Select group-by columns (e.g., `District`).
3. For each metric: select the column and aggregation function.
4. Set sorting column and direction.
5. Set Top N (e.g., show top 10 districts only) if required.
6. Enable **Include Totals Row** if needed.
7. Click **Add Table**.

**What comes out:**
- A summary table preview with aggregated district data.

---

### Step 5 — Save Dashboard Layout

**What to do:**
1. Go to the **Layout** tab.
2. Enter a layout name (e.g., `June_Review_Dashboard`).
3. Click **Save Layout**.
4. To reuse in future: open the workspace and click **Load Layout**.

**What comes out:**
- Layout saved with version number.
- Layout list showing all saved versions with date.

---

### Step 6 — Generate Dashboard

**What to do:**
1. Go to **Generate**.
2. Review the component summary (KPI cards count, charts count, tables count).
3. Click **Generate Dashboard**.
4. Download or push to Drive.

**What comes out:**
- `dashboard.xlsx` — Formatted Excel with KPI cards sheet, one sheet per chart, one sheet per table.
- `dashboard_dataset.xlsx` — Underlying data powering the dashboard.
- Google Sheets (if pushed) — All sheets uploaded to Drive.

---

---

# APP-005 — Deliverable Studio

**Purpose:** Generate formatted reports in multiple output formats — Word, PowerPoint, PDF, Excel — from structured data.

---

## Use Case 1 — Generate a District Programme Report

**Scenario:** Quarterly report on programme performance is due. Data is available. Generate a Word document and a PowerPoint summary.

---

### Step 1 — Upload Reporting Data

**What to do:**
1. Go to **Workspace**, select the project.
2. Go to **Upload**, load the final analytics dataset or clean dataset.

**What comes out:**
- Data loaded with row/column preview.

---

### Step 2 — Set Report Details

**What to do:**
1. Go to **Report Details**.
2. Fill in: Report Title, Programme Name, Organisation, Author Name, Report Date, Description/Scope.
3. Select output formats: tick the boxes for Excel / Word / PowerPoint / PDF.
4. Click **Save Details**.

**What comes out:**
- Report metadata summary showing all details confirmed.
- A unique PMU Report ID is assigned (format: `PMU-2026-FLN-REPORT-00001`).

---

### Step 3 — Define Report Sections

**What to do:**
1. Go to the **Sections** tab.
2. Click **Add Section**.
3. For each section:
   - Select section type: **Narrative** (auto-written text from data) / **Table** (summary table) / **Recommendations** (bullet point list).
   - For Narrative sections: select the group column and metric columns — the tool auto-generates descriptive text.
   - For Table sections: select group-by and metric columns.
   - For Recommendations sections: type each recommendation manually.
4. Use the move up/down arrows to reorder sections.
5. Click **Preview Section** to see how it will look in the report.

**What comes out:**
- A section list in the order they will appear in the final report.
- A live preview of each section's content.

---

### Step 4 — Generate Report Outputs

**What to do:**
1. Go to **Generate**.
2. Review the report outline (sections listed in order).
3. Click **Generate Reports**.
4. Click the download button for each format selected.

**What comes out:**
- `report.xlsx` — Structured Excel report with one sheet per section.
- `report.docx` — Formatted Word document with narrative text, tables, and section headings.
- `report.pptx` — PowerPoint presentation with one slide per section.
- `report.pdf` — PDF version of the report.
- Google Drive upload (if pushed) — All files saved to a Drive folder.

---

## Use Case 2 — Generate Segregated Reports by District

> **Note:** This feature is planned for the next update. Currently the tool generates one consolidated report for all districts. The upcoming "Split by Column" feature will allow the user to select a filter column (e.g., District) and automatically generate one separate Excel/Word/PPT report per district, bundled as a ZIP download. This is confirmed as a priority addition.

---

---

# APP-006 — Workflow Builder

**Purpose:** Track implementation progress of a programme across multiple entities (districts, schools, blocks) through defined workflow stages.

---

## Use Case 1 — Track ATR Compliance Across Districts

**Scenario:** 25 districts have been given 6 action points from a review meeting. Track which districts have completed which action points.

---

### Step 1 — Open Workspace

**What to do:**
1. Go to **Workspace**, select or create the project workspace.

---

### Step 2 — Define the Workflow

**What to do:**
1. Go to the **Define** tab.
2. Enter the workflow name (e.g., `Q2 Review ATR Tracker`).
3. Select entity type (District / Block / School / Custom).
4. To enter entities manually: type each entity name and click **Add Entity**.
5. To upload an entity list: upload a CSV with entity names in the first column.
6. To add a stage (action point): type the stage name (e.g., `Submit Utilisation Certificate`) and click **Add Stage**.
7. To load a workflow template (ATR / Review / Implementation / Training): click **Load Template**.
8. Use the up/down arrows to reorder stages.

**What comes out:**
- An entity list (e.g., 25 district names).
- A stage list (e.g., 6 action points in sequence).

---

### Step 3 — Update Tracking Status

**What to do:**
1. Go to the **Tracker** tab.
2. The tracking matrix is displayed: rows = entities, columns = stages.
3. To update a single cell: click on the cell, select status (Completed / In Progress / Pending / Overdue / N/A), add a remark, click **Save**.
4. To update in bulk: select multiple entities, select a stage, set the status, click **Bulk Update**.
5. To filter the matrix: use the status filter to show only Overdue or Pending entries.

**What comes out:**
- A colour-coded tracking matrix: green (Completed), blue (In Progress), grey (Pending), red (Overdue).
- A progress percentage per entity (e.g., District A: 4/6 = 67% complete).
- A live pendency list showing all Pending and Overdue items.

---

### Step 4 — Generate Tracker Outputs

**What to do:**
1. Go to **Generate**.
2. Review the summary (total entities, stages, completion rate).
3. Click **Generate Tracker**.
4. Download the files.

**What comes out:**
- `tracker.xlsx` — Full tracking matrix with colour coding, remarks, and progress percentages.
- `workflow_definition.xlsx` — Workflow metadata (entity list, stage definitions, sequence).
- Pendency report section showing all incomplete items by entity.
- Google Sheets (if pushed) — Live tracker in Drive for team collaboration.

---

## Use Case 2 — Track School Inspection Progress

**Scenario:** 150 schools need to be inspected across 3 stages: Pre-visit checklist, Visit completed, Report submitted.

**What to do:**
1. Create workspace `School_Inspections_Q2`.
2. In **Define**: entity type = School. Upload CSV with 150 school names. Add 3 stages.
3. As inspections complete: update status in **Tracker** individually or in bulk.
4. In **Generate**: download `tracker.xlsx` weekly for review meetings.

**What comes out:**
- Weekly tracker showing exactly which schools are at which stage.
- Completion rates updated in real time.

---

---

# Common Operations Across All Apps

## Saving and Loading Configurations

Every app automatically saves your configuration at each step.

**To save a named configuration:**
- Look for the **Save Config** button (available on most tabs).
- Enter a name (e.g., `FLN_Framework_v1`).
- Click Save.

**To reload a previous configuration:**
- Click **Load Config**.
- Select from the list of saved versions.
- The tool restores the full state.

**To export a configuration for sharing:**
- Click **Export Config** → downloads a `.pmuconfig` file.
- Share this file with a colleague.
- They import it into their workspace using **Import Config**.

---

## Registry and Output Tracking

Every file generated by any app is assigned a unique ID in the format:

```
PMU-2026-FLN-REPORT-00001
```

A `registry.csv` file in the workspace records:
- The artifact ID
- The app that generated it
- The date and time
- The output file name
- The status

This provides a complete audit trail of all deliverables generated.

---

## Google Drive Integration

Any output file can be pushed to Google Drive directly from the Generate tab.

**Requirements:** Google credentials must be configured in the workspace (one-time setup).

**What to do:**
1. Click **Push to Google Drive** on the Generate tab.
2. Select the destination folder.
3. Click **Upload**.

**What comes out:**
- File uploaded to Drive.
- A shareable link returned in the app.

---

## Typical End-to-End Workflow

```
APP-001             APP-002              APP-003             APP-004
Build Framework  →  Clean Raw Data  →   Analyse & KPIs  →  Build Dashboard
(Excel template,    (Clean dataset,      (KPI report,       (Dashboard Excel,
 validation rules,   transformation log,  rankings,           charts, tables)
 Google Form)        validation report)   trend analysis)

                                                                    ↓
                                                              APP-005
                                                         Generate Report
                                                         (Word, PPT, PDF, Excel)
```

APP-006 runs independently at any time to track workflow and ATR compliance.

---

## Upcoming Feature — Segregated Reports by District/Block

The following feature is confirmed for the next development sprint:

**What it will do:** On the Generate tab in APP-003, APP-004, and APP-005, a new option will allow:

1. Select a filter column (e.g., `District` or `Block`).
2. The tool loops through every unique value in that column.
3. One separate Excel (or Word / PPT) is generated per district/block.
4. All files are bundled into a single ZIP file for download.

**Example output for 30 districts:**
```
district_reports.zip
├── FLN_Report_District_A.xlsx
├── FLN_Report_District_B.xlsx
├── FLN_Report_District_C.xlsx
... (one per district)
```

This removes the manual effort of filtering and saving one file per district.

---

*PMU Studio Suite — OSEPA | Built for PMU productivity*
