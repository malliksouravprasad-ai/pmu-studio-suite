"""AI Assistant page — Deliverable Studio."""
import sys, os
_APP_DIR  = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_PMU_ROOT = os.path.dirname(os.path.dirname(_APP_DIR))
for _p in [_PMU_ROOT, _APP_DIR]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

import streamlit as st
from shared.theme import page_header, sidebar_brand
from engine import init_state, get_workspace, get_job
from shared.ai_assistant import render_ai_assistant

st.set_page_config(page_title="AI Assistant — Deliverable Studio", page_icon="🤖", layout="wide")
init_state()

with st.sidebar:
    sidebar_brand("Deliverable Studio", "APP-005")
    ws = get_workspace()
    if ws:
        st.success(f"📁 **{ws['name']}")
    else:
        st.warning("No workspace selected")

# Pass current workspace and job context so the assistant can act on them
try:
    job = get_job()
except Exception:
    job = None

render_ai_assistant(
    app_name="Deliverable Studio",
    app_context={
        "app_id":    "APP-005",
        "workspace": get_workspace(),
        "job":       job,
        "user_tag":  st.session_state.get("pmu_user_tag", ""),
    },
)
