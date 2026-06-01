"""Page 5 — Layout Builder: save, load, and manage dashboard layouts."""
import sys
import os

_APP_DIR  = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_PMU_ROOT = os.path.dirname(os.path.dirname(_APP_DIR))
for _p in [_PMU_ROOT, _APP_DIR]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

import streamlit as st
from shared.theme import page_header, sidebar_brand
from engine import (
    init_state, reset_state, get_workspace, get_job, set_job, has_data,
    DashboardStudioJob,
)
from shared import save_config, load_config, list_configs, delete_config, clone_config

st.set_page_config(page_title="Layout — Dashboard Studio", page_icon="🗂️", layout="wide")
init_state()

ws  = get_workspace()
job = get_job()

with st.sidebar:
    sidebar_brand("Dashboard Studio", "APP-004")
    if ws:
        st.success(f"📁 **{ws['name']}**")
    else:
        st.warning("No workspace selected")
    dj = job.dashboard_job
    st.info(f"**{len(dj.kpis)}** KPI · **{len(dj.charts)}** chart · **{len(dj.tables)}** table")
    if st.button("🗑 Reset Studio", use_container_width=True):
        reset_state(); st.rerun()

page_header("Layout", subtitle="Design the dashboard layout and export", icon="🎨", step=5, total_steps=6)

if not ws:
    st.warning("A workspace is required to save and manage layouts. Open one on the **Workspace** page.")
    st.stop()

# ── Save current layout ───────────────────────────────────────────────────────
st.markdown("### Save Current Layout")
dj = job.dashboard_job
st.info(f"Current layout: **{len(dj.kpis)}** KPI card(s) · **{len(dj.charts)}** chart(s) · **{len(dj.tables)}** table(s)")

with st.form("save_layout_form"):
    layout_name = st.text_input("Layout name", value=job.layout_name or "Dashboard Layout")
    if st.form_submit_button("💾 Save Layout to Workspace", type="primary"):
        if not layout_name.strip():
            st.error("Layout name is required.")
        else:
            job.layout_name = layout_name.strip()
            set_job(job)
            save_config(ws["path"], "APP-004", layout_name.strip(), job.to_config())
            st.success(f"Layout **{layout_name.strip()}** saved to workspace.")

st.markdown("---")

# ── Saved layouts ─────────────────────────────────────────────────────────────
st.markdown("### Saved Layouts")
saved = list_configs(ws["path"], "APP-004")

if not saved:
    st.info("No layouts saved yet. Use the form above to save the current layout.")
else:
    # Group by name, show latest version
    by_name = {}
    for c in saved:
        by_name.setdefault(c["name"], []).append(c)

    for name, versions in by_name.items():
        latest = max(versions, key=lambda c: c["version"])
        with st.container(border=True):
            c1, c2, c3, c4 = st.columns([3, 1, 1, 1])
            cfg_data = latest.get("config", {})
            n_kpi    = len(cfg_data.get("kpis", []))
            n_chart  = len(cfg_data.get("charts", []))
            n_table  = len(cfg_data.get("tables", []))
            c1.markdown(f"**{name}** (v{latest['version']} · saved {latest['saved']})")
            c1.caption(f"{n_kpi} KPI · {n_chart} chart · {n_table} table")

            with c2:
                if st.button("Load", key=f"load_{name}", use_container_width=True, type="primary"):
                    loaded = load_config(ws["path"], "APP-004", name)
                    set_job(DashboardStudioJob.from_config(loaded["config"]))
                    st.success(f"Layout **{name}** loaded."); st.rerun()

            with c3:
                clone_name = st.text_input("Clone as", key=f"cn_{name}", label_visibility="collapsed",
                                            placeholder="new name")
                if st.button("Clone", key=f"cl_{name}", use_container_width=True):
                    if clone_name.strip():
                        clone_config(ws["path"], "APP-004", name, clone_name.strip())
                        st.success(f"Cloned as **{clone_name.strip()}**."); st.rerun()

            with c4:
                if st.button("🗑 Delete", key=f"del_{name}", use_container_width=True):
                    delete_config(ws["path"], "APP-004", name)
                    st.success(f"Layout **{name}** deleted."); st.rerun()

    # Version history
    with st.expander("Version history"):
        for c in sorted(saved, key=lambda c: (c["name"], -c["version"])):
            st.caption(f"**{c['name']}** v{c['version']} — saved {c['saved']}")
