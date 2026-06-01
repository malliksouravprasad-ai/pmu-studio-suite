"""APP-001 Monitoring Builder — entry point."""
import sys
import os

_APP_DIR  = os.path.dirname(os.path.abspath(__file__))
_PMU_ROOT = os.path.dirname(os.path.dirname(_APP_DIR))
for _p in [_PMU_ROOT, _APP_DIR]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

import streamlit as st
from shared import render_registry_browser
from engine import init_state, get_workspace, get_job, has_fields, has_sections

st.set_page_config(
    page_title="Monitoring Builder — OSEPA PMU Tools",
    page_icon="🏗️",
    layout="wide",
)
init_state()

ws  = get_workspace()
job = get_job()

with st.sidebar:
    st.markdown("## 🏗️ Monitoring Builder")
    st.caption("APP-001 · OSEPA PMU Tool Suite")
    st.markdown("---")
    if ws:
        st.success(f"📁 **{ws['name']}**")
        st.caption(f"Project: {ws['project_code']}")
    else:
        st.warning("No workspace selected")

st.markdown("# 🏗️ Monitoring Builder")
st.markdown("**APP-001 · OSEPA PMU Tool Suite**")
st.markdown("---")

st.markdown("""
### What this tool builds

Create a complete monitoring system from scratch — define your data schema,
design the collection form, set validation rules, and configure KPIs — then
export everything as a ready-to-deploy package.

The outputs of this tool feed directly into the other studios:
the Excel template collects data, which APP-002 cleans, APP-003 analyses,
APP-004 visualizes, and APP-005 reports.

---

### Workflow

| Step | Page | What you build |
|------|------|----------------|
| 0 | **Workspace** | Select or create a project workspace |
| 1 | **Schema** | Define data fields — names, types, choices, descriptions |
| 2 | **Form** | Organise fields into form sections |
| 3 | **Validation** | Define rules that validate collected data |
| 4 | **KPIs** | Define indicators and their calculation formulas |
| 5 | **Package** | Generate all outputs and create Google Form |

---

### Outputs

| File | Use in |
|------|--------|
| **data_template.xlsx** | Send to field teams for data collection |
| **data_dictionary.xlsx** | Included in template, also standalone |
| **validation_rules.pmuconfig** | Import into APP-002 to validate collected data |
| **kpi_definitions.pmuconfig** | Import into APP-003 to calculate indicators |
| **form_structure.json** | Reference + input for Google Form creation |
| **Google Form** | Live data collection form (requires Google credentials) |
""")

if has_fields():
    st.markdown("---")
    st.markdown("### Framework Status")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Fields Defined",      len([f for f in job.fields if f.enabled]))
    c2.metric("Form Sections",        len(job.form_def.sections))
    c3.metric("Validation Rules",     len(job.rule_defs))
    c4.metric("KPI Definitions",      len(job.kpi_defs))

st.info("👈 Use the sidebar to navigate between steps.")

st.markdown("---")
ws = get_workspace()
ws_path = ws["path"] if ws else None
render_registry_browser(workspace_path=ws_path, app_id="APP-001")
