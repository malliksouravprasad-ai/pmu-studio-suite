"""APP-002 Data Processing Studio — entry point."""
import sys
import os

_APP_DIR  = os.path.dirname(os.path.abspath(__file__))
_PMU_ROOT = os.path.dirname(os.path.dirname(_APP_DIR))
for _p in [_PMU_ROOT, _APP_DIR]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

import streamlit as st
from engine import init_state, get_workspace, get_job, has_data, has_transform_steps, has_rules, has_mappings
from shared import render_registry_browser

st.set_page_config(
    page_title="Data Processing Studio — OSEPA PMU Tools",
    page_icon="⚙️",
    layout="wide",
)
init_state()

ws  = get_workspace()
job = get_job()

with st.sidebar:
    st.markdown("## ⚙️ Data Processing Studio")
    st.caption("APP-002 · OSEPA PMU Tool Suite")
    st.markdown("---")
    if ws:
        st.success(f"📁 **{ws['name']}**")
        st.caption(f"Project: {ws['project_code']}")
    else:
        st.warning("No workspace selected")
        st.caption("Open the **Workspace** page to begin")

st.markdown("# ⚙️ Data Processing Studio")
st.markdown("**APP-002 · OSEPA PMU Tool Suite**")
st.markdown("---")

st.markdown("""
### What this studio does

Prepare any dataset for analysis in one place — clean, transform, map, and validate
without switching between multiple tools.

Every operation is configuration-driven and saved to your project workspace so you
can reload and rerun the same pipeline on the next data drop.

---

### Workflow

| Step | Page | What you do |
|------|------|-------------|
| 0 | **Workspace** | Select or create a project workspace |
| 1 | **Upload** | Load your CSV or XLSX file (or reload a saved config) |
| 2 | **Clean** | Handle missing values, duplicates, and text standardization |
| 3 | **Transform** | Rename, reorder, merge, split, format, and create columns |
| 4 | **Map** | Apply lookup and fuzzy mapping against master lists |
| 5 | **Validate** | Define and run validation and calculation rules |
| 6 | **Generate** | Apply everything, save config to workspace, download outputs |

---

### Outputs

| File | Contents |
|------|----------|
| **clean_dataset.xlsx** | Final processed dataset |
| **transformation_log.xlsx** | Step-by-step audit trail |
| **validation_report.xlsx** | Rule results + exceptions + valid/invalid split |
""")

# Pipeline status
if has_data() or has_transform_steps() or has_rules() or has_mappings():
    st.markdown("---")
    st.markdown("### Current Pipeline Status")
    c1, c2, c3, c4 = st.columns(4)
    df = job.transform_job
    c1.metric("File Loaded", "Yes" if has_data() else "No")
    c2.metric("Transform Steps", len([s for s in job.transform_job.steps if s.enabled]))
    c3.metric("Mapping Columns", len(job.mapping_job.column_mappings))
    c4.metric("Validation Rules", len([r for r in job.rule_job.rules if r.enabled]))

st.info("👈 Use the sidebar to navigate between steps.")

st.markdown("---")
ws_path = ws["path"] if ws else None
render_registry_browser(workspace_path=ws_path, app_id="APP-002")
