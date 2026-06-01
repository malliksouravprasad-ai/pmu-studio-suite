"""APP-004 Dashboard Studio — entry point."""
import sys
import os

_APP_DIR  = os.path.dirname(os.path.abspath(__file__))
_PMU_ROOT = os.path.dirname(os.path.dirname(_APP_DIR))
for _p in [_PMU_ROOT, _APP_DIR]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

import streamlit as st
from shared import render_registry_browser
from engine import init_state, get_workspace, get_job, has_data, has_kpis, has_charts, has_tables

st.set_page_config(
    page_title="Dashboard Studio — OSEPA PMU Tools",
    page_icon="🖥️",
    layout="wide",
)
init_state()

ws  = get_workspace()
job = get_job()

with st.sidebar:
    st.markdown("## 🖥️ Dashboard Studio")
    st.caption("APP-004 · OSEPA PMU Tool Suite")
    st.markdown("---")
    if ws:
        st.success(f"📁 **{ws['name']}**")
        st.caption(f"Project: {ws['project_code']}")
    else:
        st.warning("No workspace selected")

st.markdown("# 🖥️ Dashboard Studio")
st.markdown("**APP-004 · OSEPA PMU Tool Suite**")
st.markdown("---")

st.markdown("""
### What this studio does

Build dashboard-ready Excel outputs from any dataset — KPI summary cards,
charts, and summary tables — saved as reusable layouts inside your workspace.

Load a saved layout on a new data drop and regenerate the dashboard in one click.

---

### Workflow

| Step | Page | What you do |
|------|------|-------------|
| 0 | **Workspace** | Select or create a project workspace |
| 1 | **Upload** | Load your dataset |
| 2 | **KPIs** | Define KPI summary cards with targets |
| 3 | **Charts** | Configure column, bar, line, pie charts |
| 4 | **Tables** | Build grouped summary tables |
| 5 | **Layout** | Save and manage dashboard layouts |
| 6 | **Generate** | Download dashboard.xlsx + dataset |

---

### Outputs

| File | Contents |
|------|----------|
| **dashboard.xlsx** | KPI cards + charts + summary tables |
| **dashboard_dataset.xlsx** | Aggregated data used in the dashboard |
""")

if has_data():
    st.markdown("---")
    st.markdown("### Dashboard Status")
    c1, c2, c3 = st.columns(3)
    c1.metric("KPI Cards", len(job.dashboard_job.kpis))
    c2.metric("Charts",    len(job.dashboard_job.charts))
    c3.metric("Tables",    len(job.dashboard_job.tables))

st.info("👈 Use the sidebar to navigate between steps.")

st.markdown("---")
ws = get_workspace()
ws_path = ws["path"] if ws else None
render_registry_browser(workspace_path=ws_path, app_id="APP-004")
