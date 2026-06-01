# PMU Studio Suite — Integration Setup Guide

**Version:** 1.0 | **Date:** June 2026

This guide walks through the complete, one-time setup for all three integrations available in PMU Tools:

1. **Google Workspace** — Google Sheets, Google Drive, Google Forms
2. **BigQuery** — Load and push large datasets from Google Cloud
3. **Apps Script Aggregator** — Trigger automated aggregations on Google Sheets

Once configured, the **Integrations** page of any PMU app shows:
- ✅ Google Connected
- ✅ BigQuery Connected
- ✅ Apps Script Connected

---

# PART 1 — Google Workspace Setup

This covers the foundational setup. BigQuery also requires this to be done first.

---

## Step 1 — Create a Google Cloud Project

1. Open your browser and go to: **console.cloud.google.com**
2. Sign in with your Google Workspace account (the one your organisation uses).
3. At the top of the page, click the **project dropdown** (it may say "Select a project" or show an existing project name).
4. Click **New Project**.
5. In the **Project Name** field, type: `pmu-tools`
6. Leave the **Organisation** as your organisation's domain.
7. Click **Create**.
8. Wait 10–15 seconds. The project is created and you are taken to the project dashboard.
9. Note your **Project ID** — it appears under the project name (e.g., `pmu-tools-2026`). You will need this later.

---

## Step 2 — Enable the Required APIs

You need to enable 4 APIs. Do this one at a time.

**Enable Google Sheets API:**
1. In the top search bar, type: `Google Sheets API`
2. Click the result titled **Google Sheets API** (from Google).
3. Click **Enable**.
4. Wait for the page to confirm "API enabled".

**Enable Google Drive API:**
1. In the top search bar, type: `Google Drive API`
2. Click **Google Drive API**.
3. Click **Enable**.

**Enable Google Forms API:**
1. In the top search bar, type: `Google Forms API`
2. Click **Google Forms API**.
3. Click **Enable**.

**Enable BigQuery API** (needed for Part 2):
1. In the top search bar, type: `BigQuery API`
2. Click **BigQuery API**.
3. Click **Enable**.

---

## Step 3 — Create a Service Account

A Service Account is like a "robot user" that PMU Tools uses to access Google services on your behalf.

1. In the left sidebar, click **IAM & Admin → Service Accounts**.
2. Click **+ Create Service Account** at the top.
3. Fill in:
   - **Service account name:** `pmu-tools-service`
   - **Service account ID:** (auto-filled as `pmu-tools-service`)
   - **Description:** PMU Tools service account for Sheets, Drive, BigQuery
4. Click **Create and Continue**.
5. In the **Grant this service account access to project** step:
   - Click the **Role** dropdown.
   - Search for and select: **BigQuery Data Viewer**
   - Click **+ Add Another Role**
   - Search for and select: **BigQuery Job User**
   - Click **+ Add Another Role**
   - Search for and select: **Editor** (this covers Sheets and Drive)
6. Click **Continue**.
7. Click **Done**.

You will see your new service account listed. Note the **email address** — it looks like:
`pmu-tools-service@pmu-tools-2026.iam.gserviceaccount.com`

---

## Step 4 — Download the Service Account Key (JSON File)

1. On the Service Accounts list, click on **pmu-tools-service** (the one you just created).
2. Click the **Keys** tab.
3. Click **Add Key → Create new key**.
4. Select **JSON** format.
5. Click **Create**.
6. A JSON file is automatically downloaded to your computer. It will be named something like `pmu-tools-2026-abc123.json`.
7. Open this file with Notepad or any text editor. It looks like:

```json
{
  "type": "service_account",
  "project_id": "pmu-tools-2026",
  "private_key_id": "abc123...",
  "private_key": "-----BEGIN RSA PRIVATE KEY-----\nMIIE...\n-----END RSA PRIVATE KEY-----\n",
  "client_email": "pmu-tools-service@pmu-tools-2026.iam.gserviceaccount.com",
  "client_id": "123456789",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  ...
}
```

**Keep this file safe. It gives access to your Google project.**

---

## Step 5 — Add Credentials to PMU Tools (Streamlit Secrets)

This is how PMU Tools on Cloud Run reads your Google credentials securely.

1. Go to: **console.cloud.google.com/run**
2. Click on the Cloud Run service for one of your PMU apps (e.g., `pmu-001-monitoring-builder`).
3. Click **Edit & Deploy New Revision**.
4. Scroll down to **Variables & Secrets**.
5. Click **+ Add Variable** for each entry below — but for PMU Tools, the preferred method is using Streamlit's secrets system.

**Streamlit secrets method (recommended):**

If you deployed using the `deploy_cloudrun.ps1` script, your apps use Streamlit's built-in secrets. To configure:

1. In your project folder, open (or create) the file:
   `C:\Users\malli\OneDrive\Documents\Claude\Projects\PMU_Tools\.streamlit\secrets.toml`

2. Copy the content below and fill in your actual values from the JSON file:

```toml
[gcp_service_account]
type                        = "service_account"
project_id                  = "pmu-tools-2026"
private_key_id              = "paste_private_key_id_from_json"
private_key                 = "-----BEGIN RSA PRIVATE KEY-----\nMIIE...paste full key here...\n-----END RSA PRIVATE KEY-----\n"
client_email                = "pmu-tools-service@pmu-tools-2026.iam.gserviceaccount.com"
client_id                   = "paste_client_id_from_json"
auth_uri                    = "https://accounts.google.com/o/oauth2/auth"
token_uri                   = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url        = "paste_client_x509_cert_url_from_json"

[bigquery]
project_id = "pmu-tools-2026"
dataset_id = "pmu_data"

[apps_script]
web_app_url   = ""
shared_secret = ""
```

3. **Important — the private key:** Copy the entire `private_key` value from the JSON file. It includes `\n` characters. Paste it exactly as-is between the quotes in secrets.toml.

4. Save the file.

---

## Step 6 — Redeploy to Apply the Secrets

After saving `secrets.toml`, redeploy the apps so the new credentials take effect:

```powershell
cd "C:\Users\malli\OneDrive\Documents\Claude\Projects\PMU_Tools"
.\deploy_cloudrun.ps1 -Project "pmu-tools-2026"
```

The deployment takes 10–15 minutes. After it completes, open any app and go to the **Integrations** page. The status chips should show:

✅ Google Connected

---

## Step 7 — Share Google Sheets with the Service Account

For PMU Tools to read or write a specific Google Sheet, the sheet must be shared with the service account email.

**For every Google Sheet you want to use with PMU Tools:**
1. Open the Google Sheet.
2. Click the **Share** button (top right).
3. In the **Add people and groups** field, paste the service account email:
   `pmu-tools-service@pmu-tools-2026.iam.gserviceaccount.com`
4. Set permission to **Editor** (if you want the tool to write back) or **Viewer** (read-only).
5. Click **Share**.

You do not need to notify the service account — it is not a real person.

---

---

# PART 2 — BigQuery Setup

BigQuery is used to load very large datasets (50,000+ rows) or to push processed results into a data warehouse for long-term analysis.

**Prerequisite:** Part 1 must be completed first (APIs enabled, service account created, credentials in secrets.toml).

---

## Step 1 — Open BigQuery

1. Go to: **console.cloud.google.com/bigquery**
2. Make sure your project (`pmu-tools-2026`) is selected in the top dropdown.
3. You will see the BigQuery console with an **Explorer** panel on the left.

---

## Step 2 — Create a Dataset

A Dataset in BigQuery is like a folder that holds your tables.

1. In the **Explorer** panel, click on your project name (`pmu-tools-2026`).
2. Click the **three dots (⋮)** that appear next to the project name.
3. Click **Create dataset**.
4. Fill in:
   - **Dataset ID:** `pmu_data`
   - **Data location:** `asia-south1` (Mumbai — closest to Odisha)
   - Leave other settings as default.
5. Click **Create dataset**.

The dataset `pmu_data` now appears in the Explorer panel under your project.

---

## Step 3 — Upload a Table to BigQuery (Optional — if you have existing data)

If you have a CSV file with UDISE+ or MIS data that you want to store in BigQuery:

1. Click on `pmu_data` in the Explorer panel.
2. Click **+ Create table** (top right of the main panel).
3. Under **Create table from:** select **Upload**.
4. Click **Browse** and select your CSV file.
5. Set the **Table name** (e.g., `udise_2025_odisha`).
6. Under **Schema**, select **Auto detect** — BigQuery will figure out column types.
7. Click **Create table**.

BigQuery processes the file and creates the table. For a 100,000-row CSV, this takes about 30 seconds.

---

## Step 4 — Verify BigQuery Access from PMU Tools

1. Open any PMU app (e.g., APP-003 Analytics Studio).
2. Go to **Upload → BigQuery** tab.
3. The status should show: ✅ **Connected — project: pmu-tools-2026**
4. Select your dataset (`pmu_data`) from the dropdown.
5. Select a table.
6. Set a row limit (e.g., 1000) and click **Load Table**.

If you see an error, check:
- The service account has **BigQuery Data Viewer** and **BigQuery Job User** roles (Step 3 of Part 1).
- The `[bigquery]` section in `secrets.toml` has the correct `project_id`.

---

## Step 5 — Grant BigQuery Access to Existing Datasets (if the data is in another project)

If your UDISE+ or government data is in a different GCP project's BigQuery:

1. In the other project's BigQuery, open the dataset.
2. Click **Share dataset** (or **Permissions**).
3. Add the service account email (`pmu-tools-service@pmu-tools-2026.iam.gserviceaccount.com`) with **BigQuery Data Viewer** role.
4. In `secrets.toml`, update `[bigquery] project_id` to the project that holds the data.

---

---

# PART 3 — Apps Script Aggregator Setup

The Apps Script Aggregator lets you trigger an automated rollup of any Google Sheet — grouping rows by district/block and summing metrics — without opening Excel or the PMU app.

---

## Step 1 — Open Google Apps Script

1. Go to: **script.google.com**
2. Sign in with your Google Workspace account.
3. Click **New project** (top left).
4. A new script editor opens with a blank `Code.gs` file.

---

## Step 2 — Paste the Aggregator Code

1. In the script editor, select all existing text (Ctrl+A) and delete it.
2. Open the file:
   `C:\Users\malli\OneDrive\Documents\Claude\Projects\PMU_Tools\templates\apps_script_aggregator.js`
3. Copy all of its contents (Ctrl+A, Ctrl+C).
4. Paste into the script editor (Ctrl+V).
5. Click **File → Save project** (or Ctrl+S).
6. Name the project: `PMU Aggregator`.
7. Click **Rename**.

---

## Step 3 — Set the Security Secret

The Apps Script web app uses a shared secret to prevent unauthorised access. You choose this — it can be any password you like.

1. In the script editor, click **Project Settings** (the gear icon ⚙️ in the left sidebar).
2. Scroll down to **Script Properties**.
3. Click **Add script property**.
4. Set:
   - **Property:** `PMU_SECRET`
   - **Value:** (choose a password, e.g., `OsepaPMU@2026`)
5. Click **Save script properties**.

Note this password — you will add it to `secrets.toml` in Step 5.

---

## Step 4 — Configure the Nightly Aggregation (Optional)

If you want the aggregator to run automatically every night, configure the source and target sheet URLs in the code first.

1. In the script editor, find the function `runNightlyAggregation()` (near the bottom of the file).
2. Replace the placeholder URLs:
   ```javascript
   source_url:  "PASTE_YOUR_RAW_DATA_SHEET_URL_HERE",
   target_url:  "PASTE_YOUR_AGGREGATED_OUTPUT_SHEET_URL_HERE",
   group_cols:  ["District", "Block"],
   metric_cols: ["Enrolment", "Attendance", "Score"],
   agg_func:    "SUM",
   ```
   with your actual sheet URLs and column names. Example:
   ```javascript
   source_url:  "https://docs.google.com/spreadsheets/d/1ABC.../edit",
   target_url:  "https://docs.google.com/spreadsheets/d/1XYZ.../edit",
   group_cols:  ["District_Name", "Block_Name"],
   metric_cols: ["Total_Enrolment", "Attendance_Count", "FLN_Score"],
   agg_func:    "SUM",
   ```
3. Click **Save** (Ctrl+S).

---

## Step 5 — Deploy as a Web App

This is the key step — it creates a public URL that PMU Tools calls to trigger aggregations.

1. In the script editor, click **Deploy** (top right) → **New deployment**.
2. Click the **gear icon ⚙️** next to "Select type" and choose **Web app**.
3. Fill in the deployment settings:
   - **Description:** PMU Aggregator v1
   - **Execute as:** Me (your Google account)
   - **Who has access:** Anyone
4. Click **Deploy**.
5. Google will ask you to **Authorise access** — click **Authorise** and sign in with your Google account.
6. Review the permissions Google is asking for (access to Sheets, Drive) and click **Allow**.
7. After authorisation, you see a screen with:
   - **Deployment ID:** (a long string)
   - **Web app URL:** `https://script.google.com/macros/s/AKfycby.../exec`
8. **Copy the Web App URL.** This is what PMU Tools will call.

---

## Step 6 — Add the Web App URL to PMU Tools Secrets

1. Open the file:
   `C:\Users\malli\OneDrive\Documents\Claude\Projects\PMU_Tools\.streamlit\secrets.toml`

2. Find the `[apps_script]` section and fill in:

```toml
[apps_script]
web_app_url   = "https://script.google.com/macros/s/AKfycby.../exec"
shared_secret = "OsepaPMU@2026"
```

Replace:
- `web_app_url` with the URL you copied in Step 5.
- `shared_secret` with the password you set in Step 3 (`PMU_SECRET`).

3. Save the file.

---

## Step 7 — Redeploy PMU Tools to Apply the Secret

```powershell
cd "C:\Users\malli\OneDrive\Documents\Claude\Projects\PMU_Tools"
.\deploy_cloudrun.ps1 -Project "pmu-tools-2026"
```

After deployment, open any PMU app → **Integrations** page. The status should show:

✅ Apps Script Connected

---

## Step 8 — Test the Aggregator

1. In any PMU app, go to the **Integrations** page.
2. Find the **Apps Script Aggregator** section.
3. Click **Ping** — the response should say: `PMU Aggregator is running.`
4. To test a real aggregation:
   - Paste a source Google Sheet URL (must be shared with the service account).
   - Paste a target Google Sheet URL (must be shared with Editor access).
   - Select group-by columns and metric columns.
   - Click **Run Aggregator**.
5. Open the target sheet — it should have aggregated data written to it.

---

## Step 9 — Set Up Nightly Trigger (Optional)

If you configured `runNightlyAggregation()` in Step 4:

1. In the Apps Script editor, click the **Run** button (▶️) next to `setupNightlyTrigger`.
2. Wait for the execution log to show:
   `Nightly aggregation trigger created — runs at 1:00 AM daily.`
3. To verify the trigger was created: click **Triggers** (clock icon ⏰ in left sidebar).
4. You should see one trigger: `runNightlyAggregation` → Time-based → Day timer → 1am to 2am.

Every night at 1 AM, the aggregator automatically reads the source sheet, groups by district/block, sums the metrics, and writes the result to the target sheet — with no manual action needed.

---

---

# Verification Checklist

After completing all three parts, verify the setup:

| Check | Where to verify | Expected result |
|-------|----------------|-----------------|
| Google credentials added | `.streamlit/secrets.toml` | `[gcp_service_account]` section is filled |
| BigQuery config added | `.streamlit/secrets.toml` | `[bigquery]` section has project_id and dataset_id |
| Apps Script URL added | `.streamlit/secrets.toml` | `[apps_script]` section has web_app_url and shared_secret |
| Apps deployed | PowerShell deploy command | All 6 apps redeployed successfully |
| Google connected | Any app → Integrations page | ✅ Google Connected |
| BigQuery connected | Any app → Integrations page | ✅ BigQuery Connected |
| Apps Script connected | Any app → Integrations page | ✅ Apps Script Connected |
| Sheet readable | APP-002 → Upload → Google Sheet | Sheet loads without error |
| BigQuery queryable | APP-003 → Upload → BigQuery | Datasets and tables visible |
| Aggregator working | Any app → Integrations → Ping | "PMU Aggregator is running." |

---

# Troubleshooting

## "Google Not Connected"

**Cause:** `[gcp_service_account]` is missing or has a typo.

**Fix:**
1. Open `secrets.toml` and check every field is filled.
2. Check the `private_key` value — it must include the full key including `\n` characters and the `-----BEGIN` / `-----END` lines.
3. Redeploy.

---

## "BigQuery Not Connected"

**Cause:** BigQuery API not enabled, or service account lacks BigQuery roles.

**Fix:**
1. In GCP console → APIs → confirm **BigQuery API** shows "Enabled".
2. In IAM → confirm the service account has **BigQuery Data Viewer** and **BigQuery Job User** roles.
3. Confirm `[bigquery] project_id` in `secrets.toml` matches your GCP project ID exactly.

---

## "Apps Script Not Connected" or "Unauthorized"

**Cause:** The `shared_secret` in `secrets.toml` does not match the `PMU_SECRET` property set in Apps Script.

**Fix:**
1. In Apps Script editor → Project Settings → Script Properties → check the value of `PMU_SECRET`.
2. In `secrets.toml` → `[apps_script]` → make sure `shared_secret` matches exactly (case-sensitive).
3. Redeploy PMU Tools.

---

## "Permission denied" when reading a Google Sheet

**Cause:** The sheet was not shared with the service account email.

**Fix:**
1. Open the Google Sheet.
2. Click **Share** → add `pmu-tools-service@pmu-tools-2026.iam.gserviceaccount.com` as Editor.
3. Retry in the PMU app.

---

## Apps Script "openByUrl" error

**Cause:** The source or target Google Sheet URL was not shared with the service account.

**Fix:** Share both the source sheet and the target sheet with the service account email as Editor.

---

*PMU Studio Suite — OSEPA | Integration Setup Guide v1.0 | June 2026*
