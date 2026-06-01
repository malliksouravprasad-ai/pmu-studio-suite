"""Usage & Billing Monitor — Deliverable Studio."""
import sys, os
_APP_DIR  = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_PMU_ROOT = os.path.dirname(os.path.dirname(_APP_DIR))
for _p in [_PMU_ROOT, _APP_DIR]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

import streamlit as st
from shared.theme import page_header, sidebar_brand
from engine import init_state, get_workspace
from shared.usage_monitor import render_usage_dashboard

st.set_page_config(page_title="Usage Monitor — Deliverable Studio", page_icon="📊", layout="wide")
init_state()

with st.sidebar:
    sidebar_brand("Deliverable Studio", "APP-005")
    ws = get_workspace()
    if ws:
        st.success(f"📁 **{ws['name']}")
    else:
        st.warning("No workspace selected")

render_usage_dashboard()
