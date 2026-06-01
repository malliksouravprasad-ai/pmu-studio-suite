"""APP-004 Dashboard Studio — entry point."""
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
    st.Page("pages/1_Upload.py",    title="Upload",    icon="📤"),
    st.Page("pages/2_KPIs.py",      title="KPIs",      icon="🎯"),
    st.Page("pages/3_Charts.py",    title="Charts",    icon="📊"),
    st.Page("pages/4_Tables.py",    title="Tables",    icon="📋"),
    st.Page("pages/5_Layout.py",    title="Layout",    icon="🖼️"),
    st.Page("pages/6_Generate.py",    title="Generate",     icon="📥"),
    st.Page("pages/_Integrations.py", title="Integrations", icon="🔗"),
])
pg.run()
