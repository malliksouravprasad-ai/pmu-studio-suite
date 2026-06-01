"""APP-003 Analytics Studio — entry point."""
import sys
import os

_APP_DIR  = os.path.dirname(os.path.abspath(__file__))
_PMU_ROOT = os.path.dirname(os.path.dirname(_APP_DIR))
for _p in [_PMU_ROOT, _APP_DIR]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

import streamlit as st
from shared import render_registry_browser
from engine import init_state, get_workspace, get_job, has_data, has_agg_configs, has_kpis, has_rankings

st.set_page_config(
    page_title="Analytics Studio — OSEPA PMU Tools",
    page_icon="📊",
    layout="wide",
)
init_state()

ws  = get_workspace()
job = get_job()

with st.sidebar:
    st.markdown("## 📊 Analytics Studio")
    st.caption("APP-003 · OSEPA PMU Tool Suite")
    st.markdown("---")
    if ws:
        st.success(f"📁 **{ws['name']}**")
        st.caption(f"Project: {ws['project_code']}")
    else:
        st.warning("No workspace selected")
        st.caption("Open the **Workspace** page to begin")

st.markdown("# 📊 Analytics Studio")
st.markdown("**APP-003 · OSEPA PMU Tool Suite**")
st.markdown("---")

st.markdown("""
### What this studio does

Generate insights from any dataset — aggregate by grouping, define and score KPIs,
rank entities, analyse variance against targets, and track trends across periods.

All analysis definitions are saved to your workspace so you can reload and rerun
on updated data without redefining anything.

---

### Workflow

| Step | Page | What you do |
|------|------|-------------|
| 0 | **Workspace** | Select or create a project workspace |
| 1 | **Upload** | Load your dataset (or reload a saved config) |
| 2 | **Aggregate** | Group by columns and compute totals, averages, counts |
| 3 | **KPIs** | Define KPIs with targets and weights — get composite scores |
| 4 | **Analyse** | Rank entities, compare against targets, detect variance |
| 5 | **Trends** | Track indicator movement across reporting periods |
| 6 | **Generate** | Download all outputs and save config to workspace |

---

### Outputs

| File | Contents |
|------|----------|
| **aggregation.xlsx** | One sheet per aggregation config |
| **kpi_report.xlsx** | KPI summary + scored dataset |
| **analytics.xlsx** | Rankings + variance + trend analysis |
""")

if has_data():
    st.markdown("---")
    st.markdown("### Pipeline Status")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Aggregations", len(job.agg_job.configs))
    c2.metric("KPIs",         len([k for k in job.kpi_defs if k.enabled]))
    c3.metric("Rankings",     len([r for r in job.analytics_job.rankings if r.enabled]))
    c4.metric("Variances",    len([v for v in job.analytics_job.variances if v.enabled]))

st.info("👈 Use the sidebar to navigate between steps.")

st.markdown("---")
ws = get_workspace()
ws_path = ws["path"] if ws else None
render_registry_browser(workspace_path=ws_path, app_id="APP-003")
