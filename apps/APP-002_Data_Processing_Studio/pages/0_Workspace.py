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
from shared import (
    create_workspace, list_workspaces, load_workspace, delete_workspace,
    list_configs, list_all_configs,
)

st.set_page_config(page_title="Workspace — Data Processing Studio", page_icon="📁", layout="wide")
init_state()

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚙️ Data Processing Studio")
    st.caption("APP-002 · OSEPA PMU Tool Suite")
    st.markdown("---")
    ws = get_workspace()
    if ws:
        st.success(f"📁 **{ws['name']}**")
        st.caption(f"Project: {ws['project_code']}")
        if ws.get("user_tag"):
            st.caption(f"User: {ws['user_tag']}")
    else:
        st.warning("No workspace selected")
    if st.button("🗑 Reset Studio", use_container_width=True):
        reset_state(); st.rerun()

# ── Main ──────────────────────────────────────────────────────────────────────
st.markdown("# 📁 Workspace")
st.caption("Step 0 — Select or create a project workspace")
st.markdown("---")

# ── Session user tag ──────────────────────────────────────────────────────────
st.markdown("### Your User Tag")
st.caption("Enter your name or team identifier so your workspaces are kept separate from other users.")
_col_tag, _col_reset = st.columns([3, 1])
_stored_tag = st.session_state.get("pmu_user_tag", "")
_user_tag   = _col_tag.text_input(
    "Your Name / Tag",
    value=_stored_tag,
    placeholder="e.g. Malli, District_A, Team_FLN",
    key="ws_user_tag_input",
)
st.session_state["pmu_user_tag"] = _user_tag.strip()
if _col_reset.button("Clear tag", use_container_width=True):
    st.session_state["pmu_user_tag"] = ""
    st.rerun()

st.markdown("---")

active_ws = get_workspace()
if active_ws:
    st.success(f"**Active workspace:** {active_ws['name']}"
               + (f" [{active_ws['user_tag']}]" if active_ws.get("user_tag") else "")
               + f"  ·  Project: {active_ws['project_code']}")
    if st.button("Close workspace (keep data)", use_container_width=False):
        set_workspace(None); st.rerun()
    st.markdown("---")

# ── Create New Workspace ──────────────────────────────────────────────────────
with st.expander("➕ Create New Workspace", expanded=(active_ws is None)):
    col1, col2 = st.columns(2)
    with col1:
        new_name = st.text_input("Workspace Name", placeholder="e.g. Teacher Training Monitoring 2026")
    with col2:
        new_code = st.text_input("Project Code", placeholder="e.g. TTM", max_chars=10)
    new_desc = st.text_area("Description (optional)", height=80)

    _tag_display = st.session_state.get("pmu_user_tag", "")
    if _tag_display:
        st.info(f"This workspace will be created under user tag: **{_tag_display}**")
    else:
        st.warning("Set your User Tag above so this workspace is isolated to you.")

    if st.button("Create Workspace", type="primary"):
        if not new_name.strip():
            st.error("Workspace name is required.")
        elif not new_code.strip():
            st.error("Project code is required.")
        else:
            try:
                ws_meta = create_workspace(
                    new_name.strip(), new_code.strip(),
                    user_tag=_tag_display,
                    description=new_desc.strip(),
                )
                set_workspace(ws_meta)
                st.success(f"Workspace **{new_name}** created and activated.")
                st.rerun()
            except FileExistsError as _e:
                st.error(str(_e))

# ── Existing Workspaces ───────────────────────────────────────────────────────
st.markdown("### Existing Workspaces")
_current_tag  = st.session_state.get("pmu_user_tag", "")
_all_ws       = list_workspaces()
_show_all     = st.toggle("Show all users' workspaces", value=False, key="ws_show_all")

if _current_tag and not _show_all:
    workspaces = [w for w in _all_ws if w.get("user_tag", "") == _current_tag]
    if not workspaces and _all_ws:
        st.caption(f"No workspaces found for tag **{_current_tag}**. Toggle 'Show all' to see others.")
else:
    workspaces = _all_ws

if not workspaces:
    st.info("No workspaces yet. Create one above to begin.")
else:
    for ws_meta in workspaces:
        is_active = active_ws and active_ws.get("slug") == ws_meta["slug"]

        with st.container(border=True):
            c1, c2, c3 = st.columns([3, 1, 1])
            with c1:
                label = f"📁 **{ws_meta['name']}**"
                if ws_meta.get("user_tag"):
                    label += f"  `{ws_meta['user_tag']}`"
                if is_active:
                    label += " ✅"
                st.markdown(label)
                st.caption(
                    f"Project: {ws_meta['project_code']}  |  "
                    f"Created: {ws_meta.get('created', '—')}  |  "
                    f"Modified: {ws_meta.get('modified', '—')}"
                )
                if ws_meta.get("description"):
                    st.caption(ws_meta["description"])
                configs     = list_all_configs(ws_meta["path"])
                total_cfgs  = sum(len(v) for v in configs.values())
                if total_cfgs:
                    st.caption(f"💾 {total_cfgs} saved configuration(s)")

            with c2:
                if not is_active:
                    if st.button("Open", key=f"open_{ws_meta['slug']}", use_container_width=True):
                        loaded = load_workspace(ws_meta["slug"])
                        set_workspace(loaded)
                        st.rerun()
                else:
                    st.markdown("*(active)*")

            with c3:
                if not is_active:
                    if st.button("🗑 Delete", key=f"del_{ws_meta['slug']}", use_container_width=True):
                        delete_workspace(ws_meta["slug"])
                        st.rerun()
