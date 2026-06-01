# PMU Tool Suite — Setup Guide

**Version:** 1.0  
**Maintained by:** PMU Team  
**Applies to:** All apps in the OSEPA PMU Tool Suite

---

## 1. What Is the PMU Tool Suite?

The PMU Tool Suite is a collection of standalone productivity applications built for Project Monitoring Unit (PMU) staff. Each application takes a data file as input, processes it, and produces a ready-to-use output — reports, dashboards, forms, presentations, or registers.

No database. No server. No login system. Each app runs locally on your computer and produces files you can immediately open in Excel, Word, PowerPoint, or Google Sheets.

---

## 2. System Requirements

| Requirement | Minimum |
|---|---|
| Operating System | Windows 10 or Windows 11 |
| Python | Version 3.10 or higher (3.14 recommended) |
| RAM | 4 GB |
| Disk Space | 2 GB free |
| Internet | Required only for Google integration features |
| Browser | Chrome, Edge, or Firefox (for Streamlit apps) |

Python is already set up if you are working within the PMU Tools project folder. Verify by opening Command Prompt and typing: `python --version`

---

## 3. Folder Structure

After setup, your PMU Tools folder looks like this:

```
PMU_Tools/
├── .venv/              Python environment (do not modify)
├── credentials/        Google login credentials (set up once)
├── shared/             Common services used by all apps
├── apps/
│   ├── APP-001_Form_Builder/
│   ├── APP-002_Data_Cleaner/
│   └── ... (more apps)
├── templates/          Shared Excel, Word, PPT templates
├── inputs/             Drop your raw data files here
├── outputs/            All generated files appear here
├── registry.csv        Automatic log of every output produced
└── requirements.txt    List of required Python packages
```

---

## 4. First-Time Installation

### Step 1 — Open the PMU Tools folder

Navigate to the folder where PMU Tools is saved on your computer.

### Step 2 — Check that the virtual environment exists

Look for a folder named `.venv` inside PMU_Tools. If it exists, setup is done — skip to Step 4.

### Step 3 — Create the environment (if .venv is missing)

Open Command Prompt in the PMU_Tools folder and run:

```
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt
```

This installs all required packages. It takes 2–3 minutes on first run.

### Step 4 — Verify installation

Run the verification script to confirm everything works:

```
.venv\Scripts\python verify_shared.py
```

You should see: `=== ALL 5 COMMON SERVICES VERIFIED ===`

---

## 5. Google Integration Setup (Optional)

Google integration allows apps to read data from Google Sheets and publish forms, reports, or datasets directly to Google Drive.

**You only need to do this once. All 14 apps share the same credentials.**

### Step 1 — Create a Google Cloud Project

1. Go to: [https://console.cloud.google.com](https://console.cloud.google.com)
2. Sign in with the Google account that will own your forms and sheets
3. Click **New Project** → Name it `PMU Tools` → Click **Create**

### Step 2 — Enable APIs

In your new project:
1. Go to **APIs & Services → Library**
2. Search for and enable each of the following:
   - **Google Forms API**
   - **Google Sheets API**
   - **Google Drive API**

### Step 3 — Create Credentials

1. Go to **APIs & Services → Credentials**
2. Click **Create Credentials → OAuth 2.0 Client ID**
3. Application type: **Desktop App**
4. Name: `PMU Tools`
5. Click **Create**
6. Click **Download JSON**

### Step 4 — Place the credentials file

1. Rename the downloaded file to: `credentials.json`
2. Copy it to: `PMU_Tools/credentials/credentials.json`

### Step 5 — First login

The first time any app uses a Google feature, a browser window will open asking you to sign in. Sign in with the same Google account used in Step 1. After signing in, a `token.json` file is saved automatically in the credentials folder. You will not be asked again.

> **Security note:** Do not share `credentials.json` or `token.json` with others. These files give full access to your Google account.

---

## 6. Launching an App

Each app has a `run.bat` file. Double-click it to launch the app.

The app opens in your web browser at: `http://localhost:8501`

To stop the app, close the Command Prompt window that opened.

**Manual launch (alternative):**
```
cd apps\APP-001_Form_Builder
..\..\..\.venv\Scripts\streamlit run app.py
```

---

## 7. Understanding Outputs

All outputs are saved in: `PMU_Tools/outputs/<app-folder>/`

Every output has a **unique Artifact ID** in the format:

```
PMU-2026-FLN-SURVEY-00001
PMU-2026-ADM-REPORT-00005
PMU-2026-ATR-00012
```

The ID is printed on screen and recorded in the registry when the output is generated.

---

## 8. The Registry (registry.csv)

Every time an app generates an output, it automatically records the event in `PMU_Tools/registry.csv`.

The registry is a simple Excel/CSV file you can open and filter. It contains:

| Column | Description |
|---|---|
| app_id | Which app produced the output (e.g. APP-001) |
| artifact_id | Unique ID of the output |
| date_generated | Date and time |
| project | Project name or code |
| report_type | What kind of output (Form, Report, Dictionary, etc.) |
| output_file | Full path to the generated file |
| status | Generated / Reviewed / Submitted / Archived |

You can update the **status** column manually in Excel to track review and submission.

---

## 9. Adding New Templates

To add a shared template (Excel, Word, PPT):

1. Place your template file in: `PMU_Tools/templates/excel/` (or `word/` or `ppt/`)
2. Register it so apps can find it:

```python
from shared import register_template
register_template(
    name="District Monthly Report Template",
    path="templates/excel/district_monthly_report.xlsx",
    app_id="SHARED",
    template_type="excel",
    tags=["district", "monthly", "report"]
)
```

---

## 10. Troubleshooting

| Problem | Solution |
|---|---|
| App does not open | Check that `.venv` exists. Re-run `pip install -r requirements.txt` |
| "Module not found" error | Make sure you are running Python from `.venv\Scripts\python.exe` |
| Google login fails | Delete `credentials/token.json` and try again |
| Output file not saved | Check that the `outputs/` folder exists and is not read-only |
| Registry not updating | Ensure `registry.csv` is not open in Excel while the app is running |
| Browser does not open | Manually go to `http://localhost:8501` in your browser |

---

## 11. Getting Help

- Raise issues with the PMU tool team via the project tracking sheet
- Each app has its own **User Guide** in the app folder
- The registry tracks all outputs — check it before rerunning an app

---

*PMU Tool Suite · OSEPA · Document version 1.0*
