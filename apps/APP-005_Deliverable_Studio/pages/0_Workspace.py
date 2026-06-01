"""Page 0 — Workspace selection for Deliverable Studio."""
import sys
import os

_APP_DIR  = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_PMU_ROOT = os.path.dirname(os.path.dirname(_APP_DIR))
for _p in [_PMU_ROOT, _APP_DIR]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

import streamlit as st
from engine import init_state, get_workspace, set_workspace, reset_state
from shared import create_workspace, list_workspaces, load_workspace, delete_workspace

st.set_page_config(page_title="Workspace — Deliverable Studio", page_icon="📁", layout="wide")
init_state()

with st.sidebar:
    st.markdown("## 📄 Deliverable Studio")
    st.caption("APP-005 · OSEPA PMU Tool Suite")
    st.markdown("---")
    ws = get_workspace()
    if ws:
        st.success(f"📁 **{ws['name']}**")
    else:
        st.warning("No workspace selected")
    if st.button("🗑 Reset Studio", use_container_width=True):
        reset_state(); st.rerun()

st.markdown("# 📁 Workspace")
st.caption("Step 0 — Select or create a project workspace")
st.markdown("---")

active_ws = get_workspace()
if active_ws:
    st.success(f"**Active workspace:** {active_ws['name']} · Project: {active_ws['project_code']}")
    if st.button("Close workspace"):
        set_workspace(None); st.rerun()
    st.markdown("---")

with st.expander("➕ Create New Workspace", expanded=(active_ws is None)):
    c1, c2 = st.columns(2)
    new_name = c1.text_input("Workspace Name")
    new_code = c2.text_input("Project Code", max_chars=10)
    if st.button("Create Workspace", type="primary"):
        if not new_name.strip() or not new_code.strip():
            st.error("Name and project code are required.")
        else:
            try:
                set_workspace(create_workspace(new_name.strip(), new_code.strip()))
                st.rerun()
            except FileExistsError:
                st.error(f"A workspace named '{new_name}' already exists.")

st.markdown("### Existing Workspaces")
for ws_meta in list_workspaces():
    is_active = active_ws and active_ws.get("slug") == ws_meta["slug"]
    with st.container(border=True):
        c1, c2, c3 = st.columns([3, 1, 1])
        c1.markdown(f"📁 **{ws_meta['name']}**" + (" ✅" if is_active else ""))
        c1.caption(f"Project: {ws_meta['project_code']}  |  Modified: {ws_meta.get('modified', '—')}")
        with c2:
            if not is_active and st.button("Open", key=f"o_{ws_meta['slug']}", use_container_width=True):
                set_workspace(load_workspace(ws_meta["slug"])); st.rerun()
        with c3:
            if not is_active and st.button("🗑", key=f"d_{ws_meta['slug']}", use_container_width=True):
                delete_workspace(ws_meta["slug"]); st.rerun()
