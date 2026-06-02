"""APP-006 Workflow Builder — entry point."""
import sys
import os

_APP_DIR  = os.path.dirname(os.path.abspath(__file__))
_PMU_ROOT = os.path.dirname(os.path.dirname(_APP_DIR))
for _p in [_PMU_ROOT, _APP_DIR]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

import streamlit as st

pg = st.navigation([
    st.Page("pages/0_Workspace.py", title="Workspace", icon="📁", default=True),
    st.Page("pages/1_Define.py",    title="Define",    icon="📝"),
    st.Page("pages/2_Tracker.py",   title="Tracker",   icon="📊"),
    st.Page("pages/3_Generate.py",    title="Generate",     icon="📥"),
    st.Page("pages/_Integrations.py", title="Integrations", icon="🔗"),
    st.Page("pages/_AI_Assistant.py",  title="AI Assistant", icon="🤖"),
    st.Page("pages/_Usage.py",       title="Usage Monitor",  icon="📊"),
])
pg.run()


