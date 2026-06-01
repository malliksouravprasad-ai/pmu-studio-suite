"""Page 2 — Tracking matrix: update entity × stage statuses."""
import sys
import os

_APP_DIR  = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_PMU_ROOT = os.path.dirname(os.path.dirname(_APP_DIR))
for _p in [_PMU_ROOT, _APP_DIR]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

import streamlit as st
import pandas as pd
from engine import (
    init_state, reset_state, get_workspace, get_job, set_job, get_workflow_job,
    has_entities, has_stages, update_tracking, STATUSES,
    get_tracking_matrix, style_matrix, compute_progress, get_pendency_list,
    workflow_summary,
)

st.set_page_config(page_title="Tracker — Workflow Builder", page_icon="📊", layout="wide")
init_state()

ws  = get_workspace()
job = get_job()
wj  = get_workflow_job()

with st.sidebar:
    st.markdown("## 🔄 Workflow Builder")
    st.caption("APP-006 · OSEPA PMU Tool Suite")
    st.markdown("---")
    if ws:
        st.success(f"📁 **{ws['name']}**")
    else:
        st.warning("No workspace selected")
    total = len(wj.entities) * len(wj.stages)
    done  = sum(1 for t in wj.tracking if t.status == "Completed")
    st.info(f"**{done}** / {total} entries completed")
    if st.button("🗑 Reset Builder", use_container_width=True):
        reset_state(); st.rerun()

st.markdown("# 📊 Tracker")
st.caption("Step 2 of 2 — Update entity × stage statuses")
st.markdown("---")

if not has_entities():
    st.warning("Please add entities first (Step 1 — Define)."); st.stop()
if not has_stages():
    st.warning("Please define stages first (Step 1 — Define)."); st.stop()

summary   = workflow_summary(wj)
matrix_df = get_tracking_matrix(wj)

# ── Progress summary ──────────────────────────────────────────────────────────
m1, m2, m3, m4 = st.columns(4)
m1.metric("Entities",      len(wj.entities))
m2.metric("Stages",        len(wj.stages))
m3.metric("Completed",     f"{summary['completed_pct']:.0f}%")
m4.metric("Pending/Overdue", summary["pending_count"])

# ── Tracking matrix ───────────────────────────────────────────────────────────
st.markdown("### Tracking Matrix")
st.caption("🟢 Completed  🟡 In Progress  ⬜ Pending  🔴 Overdue  ⬛ N/A")

if not matrix_df.empty:
    try:
        styled = style_matrix(matrix_df, wj.entity_type)
        st.dataframe(styled, use_container_width=True, height=min(600, 50 + 35 * len(wj.entities)))
    except Exception:
        st.dataframe(matrix_df, use_container_width=True)
else:
    st.info("No data yet.")

st.markdown("---")

# ── Update status ─────────────────────────────────────────────────────────────
with st.expander("✏ Update Status", expanded=True):
    with st.form("update_form", clear_on_submit=True):
        c1, c2, c3, c4 = st.columns([2, 2, 1, 2])
        entity     = c1.selectbox(wj.entity_type, wj.entities)
        stage_name = c2.selectbox("Stage", [s.name for s in sorted(wj.stages, key=lambda s: s.sequence)])
        new_status = c3.selectbox("Status", STATUSES)
        remarks    = c4.text_input("Remarks (optional)")
        if st.form_submit_button("Update", type="primary"):
            stage = next((s for s in wj.stages if s.name == stage_name), None)
            if stage:
                update_tracking(entity, stage.stage_id, new_status, remarks)
                st.success(f"Updated: {entity} / {stage_name} → **{new_status}**"); st.rerun()

# ── Bulk update ───────────────────────────────────────────────────────────────
with st.expander("🔁 Bulk Update"):
    bc1, bc2, bc3 = st.columns(3)
    bulk_entities = bc1.multiselect("Entities", wj.entities)
    bulk_stages   = bc2.multiselect("Stages",   [s.name for s in wj.stages])
    bulk_status   = bc3.selectbox("Set status to", STATUSES)
    if st.button("Apply Bulk Update", type="primary") and bulk_entities and bulk_stages:
        stage_map = {s.name: s.stage_id for s in wj.stages}
        for ent in bulk_entities:
            for sname in bulk_stages:
                if sname in stage_map:
                    update_tracking(ent, stage_map[sname], bulk_status)
        st.success(f"Updated {len(bulk_entities) * len(bulk_stages)} entries to **{bulk_status}**."); st.rerun()

# ── Pendency list ─────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("### Pendency List")
pendency_df = get_pendency_list(wj)
if not pendency_df.empty:
    st.dataframe(pendency_df, use_container_width=True, hide_index=True)
else:
    st.success("No pending or overdue items.")
