"""Page 0 — Workspace selection for Workflow Builder."""
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

st.set_page_config(page_title="Workspace — Workflow Builder", page_icon="📁", layout="wide")
init_state()

with st.sidebar:
    st.markdown("## 🔄 Workflow Builder")
    st.caption("APP-006 · OSEPA PMU Tool Suite")
    st.markdown("---")
    ws = get_workspace()
    if ws:
        st.success(f"📁 **{ws['name']}**")
    else:
        st.warning("No workspace selected")
    if st.button("🗑 Reset Builder", use_container_width=True):
        reset_state(); st.rerun()

st.markdown("# 📁 Workspace")
st.caption("Step 0 — Select or create a project workspace")
st.markdown("---")

_col_tag, _col_clr = st.columns([3, 1])
_user_tag = _col_tag.text_input("Your Name / User Tag",
    value=st.session_state.get("pmu_user_tag", ""),
    placeholder="e.g. Malli, District_A, Team_FLN", key="ws_tag_006")
st.session_state["pmu_user_tag"] = _user_tag.strip()
if _col_clr.button("Clear", key="ws_clr_006", use_container_width=True):
    st.session_state["pmu_user_tag"] = ""; st.rerun()
st.caption("Your workspaces are isolated from other users by this tag.")
st.markdown("---")

active_ws = get_workspace()
if active_ws:
    _lbl = f"**Active workspace:** {active_ws['name']}"
    if active_ws.get("user_tag"):
        _lbl += f" [{active_ws['user_tag']}]"
    st.success(_lbl + f"  ·  Project: {active_ws['project_code']}")
    if st.button("Close workspace"):
        set_workspace(None); st.rerun()
    st.markdown("---")

with st.expander("➕ Create New Workspace", expanded=(active_ws is None)):
    c1, c2 = st.columns(2)
    new_name = c1.text_input("Workspace Name")
    new_code = c2.text_input("Project Code", max_chars=10)
    _tag_display = st.session_state.get("pmu_user_tag", "")
    if _tag_display:
        st.info(f"Will be created under user tag: **{_tag_display}**")
    if st.button("Create Workspace", type="primary"):
        if not new_name.strip() or not new_code.strip():
            st.error("Name and project code are required.")
        else:
            try:
                set_workspace(create_workspace(new_name.strip(), new_code.strip(), user_tag=_tag_display))
                st.rerun()
            except FileExistsError as _e:
                st.error(str(_e))

st.markdown("### Existing Workspaces")
_all_ws   = list_workspaces()
_cur_tag  = st.session_state.get("pmu_user_tag", "")
_show_all = st.toggle("Show all users' workspaces", value=False, key="ws_all_006")
_ws_list  = _all_ws if (_show_all or not _cur_tag) else [w for w in _all_ws if w.get("user_tag", "") == _cur_tag]
for ws_meta in _ws_list:
    is_active = active_ws and active_ws.get("slug") == ws_meta["slug"]
    with st.container(border=True):
        c1, c2, c3 = st.columns([3, 1, 1])
        _label = f"📁 **{ws_meta['name']}**"
        if ws_meta.get("user_tag"):
            _label += f"  `{ws_meta['user_tag']}`"
        c1.markdown(_label + (" ✅" if is_active else ""))
        c1.caption(f"Project: {ws_meta['project_code']}  |  Modified: {ws_meta.get('modified', '—')}")
        with c2:
            if not is_active and st.button("Open", key=f"o_{ws_meta['slug']}", use_container_width=True):
                set_workspace(load_workspace(ws_meta["slug"])); st.rerun()
        with c3:
            if not is_active and st.button("🗑", key=f"d_{ws_meta['slug']}", use_container_width=True):
                delete_workspace(ws_meta["slug"]); st.rerun()
