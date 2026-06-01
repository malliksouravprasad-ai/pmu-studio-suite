"""Page 0 — Select or create a project workspace."""
import sys
import os

_APP_DIR  = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_PMU_ROOT = os.path.dirname(os.path.dirname(_APP_DIR))
for _p in [_PMU_ROOT, _APP_DIR]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

import streamlit as st
from engine import init_state, get_workspace, set_workspace, reset_state
from shared import create_workspace, list_workspaces, load_workspace, delete_workspace, list_all_configs

st.set_page_config(page_title="Workspace — Analytics Studio", page_icon="📁", layout="wide")
init_state()

with st.sidebar:
    st.markdown("## 📊 Analytics Studio")
    st.caption("APP-003 · OSEPA PMU Tool Suite")
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
    new_name = c1.text_input("Workspace Name", placeholder="e.g. FLN Data Analysis 2026")
    new_code = c2.text_input("Project Code", placeholder="e.g. FLN", max_chars=10)
    new_desc = st.text_area("Description (optional)", height=70)
    if st.button("Create Workspace", type="primary"):
        if not new_name.strip() or not new_code.strip():
            st.error("Name and project code are required.")
        else:
            try:
                ws_meta = create_workspace(new_name.strip(), new_code.strip(), new_desc.strip())
                set_workspace(ws_meta); st.rerun()
            except FileExistsError:
                st.error(f"A workspace named '{new_name}' already exists.")

st.markdown("### Existing Workspaces")
workspaces = list_workspaces()
if not workspaces:
    st.info("No workspaces yet. Create one above.")
else:
    for ws_meta in workspaces:
        is_active = active_ws and active_ws.get("slug") == ws_meta["slug"]
        with st.container(border=True):
            c1, c2, c3 = st.columns([3, 1, 1])
            label = f"📁 **{ws_meta['name']}**" + (" ✅" if is_active else "")
            c1.markdown(label)
            c1.caption(f"Project: {ws_meta['project_code']}  |  Modified: {ws_meta.get('modified', '—')}")
            configs = list_all_configs(ws_meta["path"])
            total = sum(len(v) for v in configs.values())
            if total:
                c1.caption(f"💾 {total} saved configuration(s)")
            with c2:
                if not is_active and st.button("Open", key=f"o_{ws_meta['slug']}", use_container_width=True):
                    set_workspace(load_workspace(ws_meta["slug"])); st.rerun()
            with c3:
                if not is_active and st.button("🗑", key=f"d_{ws_meta['slug']}", use_container_width=True):
                    delete_workspace(ws_meta["slug"]); st.rerun()
