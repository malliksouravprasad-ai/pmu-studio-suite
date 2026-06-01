"""APP-006 Workflow Builder — entry point."""
import sys
import os

_APP_DIR  = os.path.dirname(os.path.abspath(__file__))
_PMU_ROOT = os.path.dirname(os.path.dirname(_APP_DIR))
for _p in [_PMU_ROOT, _APP_DIR]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

import streamlit as st
from shared import render_registry_browser
from engine import init_state, get_workspace, get_workflow_job, has_stages, has_entities, workflow_summary

st.set_page_config(
    page_title="Workflow Builder — OSEPA PMU Tools",
    page_icon="🔄",
    layout="wide",
)
init_state()

ws = get_workspace()
wj = get_workflow_job()

with st.sidebar:
    st.markdown("## 🔄 Workflow Builder")
    st.caption("APP-006 · OSEPA PMU Tool Suite")
    st.markdown("---")
    if ws:
        st.success(f"📁 **{ws['name']}**")
        st.caption(f"Project: {ws['project_code']}")
    else:
        st.warning("No workspace selected")

st.markdown("# 🔄 Workflow Builder")
st.markdown("**APP-006 · OSEPA PMU Tool Suite**")
st.markdown("---")

st.markdown("""
### What this tool does

Create reusable tracking systems for any PMU workflow — data collection rounds,
action-taken registers, compliance trackers, review cycles, and issue registers.

Define entities and stages once, save to workspace, and reload for each reporting cycle.

---

### Workflow

| Step | Page | What you do |
|------|------|-------------|
| 0 | **Workspace** | Select or create a project workspace |
| 1 | **Define** | Name the workflow, set entity type, add entities and stages |
| 2 | **Tracker** | Update status for each entity × stage combination |
| 3 | **Generate** | Download tracker workbook and save config to workspace |

---

### Outputs

| File | Contents |
|------|----------|
| **tracker.xlsx** | Status matrix + pendency report + progress summary |
| **workflow_definition.xlsx** | Entity list + stage definitions |
""")

if has_stages() and has_entities():
    progress = workflow_summary(wj)
    st.markdown("---")
    st.markdown("### Workflow Status")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Workflow",  wj.workflow_name[:20])
    c2.metric("Entities",  len(wj.entities))
    c3.metric("Stages",    len(wj.stages))
    c4.metric("Completed", f"{progress.get('completed_pct', 0):.0f}%")

st.info("👈 Use the sidebar to navigate between steps.")

st.markdown("---")
ws = get_workspace()
ws_path = ws["path"] if ws else None
render_registry_browser(workspace_path=ws_path, app_id="APP-006")
