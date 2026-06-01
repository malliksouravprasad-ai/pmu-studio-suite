"""APP-005 Deliverable Studio — entry point."""
import sys
import os

_APP_DIR  = os.path.dirname(os.path.abspath(__file__))
_PMU_ROOT = os.path.dirname(os.path.dirname(_APP_DIR))
for _p in [_PMU_ROOT, _APP_DIR]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

import streamlit as st
from shared import render_registry_browser
from engine import init_state, get_workspace, get_job, has_data, has_sections

st.set_page_config(
    page_title="Deliverable Studio — OSEPA PMU Tools",
    page_icon="📄",
    layout="wide",
)
init_state()

ws  = get_workspace()
job = get_job()

with st.sidebar:
    st.markdown("## 📄 Deliverable Studio")
    st.caption("APP-005 · OSEPA PMU Tool Suite")
    st.markdown("---")
    if ws:
        st.success(f"📁 **{ws['name']}**")
        st.caption(f"Project: {ws['project_code']}")
    else:
        st.warning("No workspace selected")

st.markdown("# 📄 Deliverable Studio")
st.markdown("**APP-005 · OSEPA PMU Tool Suite**")
st.markdown("---")

st.markdown("""
### What this studio does

Generate polished reporting deliverables from any dataset — narrative reports,
data tables, and highlight summaries — in Excel, Word, PowerPoint, or PDF.

Save report configurations to your workspace and regenerate on updated data
without rebuilding the report structure each time.

---

### Workflow

| Step | Page | What you do |
|------|------|-------------|
| 0 | **Workspace** | Select or create a project workspace |
| 1 | **Upload** | Load your dataset |
| 2 | **Report Details** | Set title, programme, date, and output formats |
| 3 | **Sections** | Add data tables, narrative text, and highlight summaries |
| 4 | **Generate** | Download outputs and save config to workspace |

---

### Outputs

| Format | Contents |
|--------|----------|
| **Excel (.xlsx)** | Formatted report with cover sheet + section sheets |
| **Word (.docx)** | Narrative report with embedded data tables |
| **PowerPoint (.pptx)** | Slide deck with key findings |
| **PDF (.pdf)** | Printable single-document report |
""")

if has_data():
    rc = job.report_config
    st.markdown("---")
    st.markdown("### Report Status")
    c1, c2, c3 = st.columns(3)
    c1.metric("Report Title", rc.report_title[:30] if rc.report_title else "—")
    c2.metric("Sections",     len(rc.sections))
    c3.metric("Formats",      len(rc.selected_formats))

st.info("👈 Use the sidebar to navigate between steps.")

st.markdown("---")
ws = get_workspace()
ws_path = ws["path"] if ws else None
render_registry_browser(workspace_path=ws_path, app_id="APP-005")
