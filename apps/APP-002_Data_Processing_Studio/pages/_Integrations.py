"""Integrations settings — Google, BigQuery, Apps Script."""
import sys, os
_APP_DIR  = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_PMU_ROOT = os.path.dirname(os.path.dirname(_APP_DIR))
for _p in [_PMU_ROOT, _APP_DIR]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

import streamlit as st
from shared.theme import page_header, sidebar_brand
from engine import init_state
from shared import render_integrations_page

st.set_page_config(page_title="Integrations — Data Processing Studio", page_icon="🔗", layout="wide")
init_state()

with st.sidebar:
    sidebar_brand("Data Processing Studio", "APP-002")

render_integrations_page()
