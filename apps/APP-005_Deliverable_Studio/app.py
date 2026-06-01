"""APP-005 Deliverable Studio — entry point."""
import sys
import os

_APP_DIR  = os.path.dirname(os.path.abspath(__file__))
_PMU_ROOT = os.path.dirname(os.path.dirname(_APP_DIR))
for _p in [_PMU_ROOT, _APP_DIR]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

import streamlit as st

pg = st.navigation([
    st.Page("pages/0_Workspace.py",       title="Workspace",      icon="📁", default=True),
    st.Page("pages/1_Upload.py",          title="Upload",         icon="📤"),
    st.Page("pages/2_Report_Details.py",  title="Report Details", icon="📝"),
    st.Page("pages/3_Sections.py",        title="Sections",       icon="📄"),
    st.Page("pages/4_Generate.py",        title="Generate",       icon="📥"),
])
pg.run()
