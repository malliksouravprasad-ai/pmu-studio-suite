"""APP-001 Monitoring Builder — entry point."""
import sys
import os

_APP_DIR  = os.path.dirname(os.path.abspath(__file__))
_PMU_ROOT = os.path.dirname(os.path.dirname(_APP_DIR))
for _p in [_PMU_ROOT, _APP_DIR]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

import streamlit as st

pg = st.navigation([
    st.Page("pages/0_Workspace.py",  title="Workspace",  icon="📁", default=True),
    st.Page("pages/1_Schema.py",     title="Schema",     icon="📋"),
    st.Page("pages/2_Form.py",       title="Form",       icon="📝"),
    st.Page("pages/3_Validation.py", title="Validation", icon="✅"),
    st.Page("pages/4_KPIs.py",       title="KPIs",       icon="🎯"),
    st.Page("pages/5_Package.py",    title="Package",    icon="📦"),
])
pg.run()
