"""APP-005 Deliverable Studio â€” entry point."""
import sys
import os

_APP_DIR  = os.path.dirname(os.path.abspath(__file__))
_PMU_ROOT = os.path.dirname(os.path.dirname(_APP_DIR))
for _p in [_PMU_ROOT, _APP_DIR]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

import streamlit as st

pg = st.navigation([
    st.Page("pages/0_Workspace.py",       title="Workspace",      icon="ðŸ“", default=True),
    st.Page("pages/1_Upload.py",          title="Upload",         icon="ðŸ“¤"),
    st.Page("pages/2_Report_Details.py",  title="Report Details", icon="ðŸ“"),
    st.Page("pages/3_Sections.py",        title="Sections",       icon="ðŸ“„"),
    st.Page("pages/4_Generate.py",        title="Generate",       icon="ðŸ“¥"),
    st.Page("pages/_Integrations.py",     title="Integrations",   icon="ðŸ”—"),
    st.Page("pages/_AI_Assistant.py",  title="AI Assistant", icon="🤖"),
    st.Page("pages/_Usage.py",       title="Usage Monitor",  icon="📊"),
])
pg.run()


