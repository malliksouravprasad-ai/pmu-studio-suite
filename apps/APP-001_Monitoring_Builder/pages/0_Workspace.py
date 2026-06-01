"""Page 0 — Workspace selection for Monitoring Builder."""
import sys
import os

_APP_DIR  = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_PMU_ROOT = os.path.dirname(os.path.dirname(_APP_DIR))
for _p in [_PMU_ROOT, _APP_DIR]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

import streamlit as st
from engine import (
    init_state, get_workspace, set_workspace, reset_state,
    get_studio_job, set_studio_job, MonitoringStudioJob, ENTITY_TYPES,
)
from shared import create_workspace, list_workspaces, load_workspace, delete_workspace, list_configs, load_config

st.set_page_config(page_title="Workspace — Monitoring Builder", page_icon="📁", layout="wide")
init_state()

with st.sidebar:
    st.markdown("## 🏗️ Monitoring Builder")
    st.caption("APP-001 · OSEPA PMU Tool Suite")
    st.markdown("---")
    ws = get_workspace()
    if ws:
        st.success(f"📁 **{ws['name']}**")
    else:
        st.warning("No workspace selected")
    if st.button("🗑 Reset Builder", use_container_width=True):
        reset_state(); st.rerun()

st.markdown("# 📁 Workspace")
st.caption("Step 0 — Select workspace and set monitoring framework metadata")
st.markdown("---")

active_ws = get_workspace()
if active_ws:
    st.success(f"**Active workspace:** {active_ws['name']} · Project: {active_ws['project_code']}")
    if st.button("Close workspace"):
        set_workspace(None); st.rerun()
    st.markdown("---")

# ── Load saved framework ──────────────────────────────────────────────────────
if active_ws:
    saved = list_configs(active_ws["path"], "APP-001")
    if saved:
        with st.expander("📂 Load a saved monitoring framework", expanded=False):
            names  = list({c["name"] for c in saved})
            chosen = st.selectbox("Saved frameworks", names)
            if st.button("Load Framework", type="primary"):
                data = load_config(active_ws["path"], "APP-001", chosen)
                ms   = MonitoringStudioJob.from_config(data["config"])
                ms.workspace_slug = active_ws["slug"]
                set_studio_job(ms)
                st.success(f"Framework **{chosen}** loaded."); st.rerun()

# ── Monitoring framework metadata ─────────────────────────────────────────────
sj  = get_studio_job()
job = sj.job

st.markdown("### Monitoring Framework Metadata")
with st.form("meta_form"):
    c1, c2 = st.columns(2)
    mon_name    = c1.text_input("Monitoring Framework Name *",
                                 value=job.monitoring_name or "School Monitoring Framework",
                                 placeholder="e.g. FLN School Monitoring 2026")
    entity_type = c1.selectbox("Entity Type *", ENTITY_TYPES,
                                index=ENTITY_TYPES.index(job.entity_type) if job.entity_type in ENTITY_TYPES else 0)
    proj_code   = c2.text_input("Project Code", value=job.project_code or (active_ws["project_code"] if active_ws else "PMU"))
    form_title  = c2.text_input("Google Form Title", value=job.form_def.title or mon_name)
    form_desc   = st.text_area("Form Description / Instructions for respondents", value=job.form_def.description, height=80)

    if st.form_submit_button("Save Metadata", type="primary"):
        job.monitoring_name     = mon_name.strip()
        job.entity_type         = entity_type
        job.project_code        = proj_code.strip().upper() or "PMU"
        job.form_def.title      = form_title.strip() or mon_name.strip()
        job.form_def.description = form_desc.strip()
        sj.workspace_slug = active_ws["slug"] if active_ws else ""
        set_studio_job(sj)
        st.success("Metadata saved. Navigate to **Schema** to define fields.")

# ── Create / open workspace ───────────────────────────────────────────────────
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
