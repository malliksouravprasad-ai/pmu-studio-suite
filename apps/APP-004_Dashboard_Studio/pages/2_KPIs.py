"""Page 2 — Define KPI summary cards."""
import sys
import os

_APP_DIR  = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_PMU_ROOT = os.path.dirname(os.path.dirname(_APP_DIR))
for _p in [_PMU_ROOT, _APP_DIR]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

import pandas as pd
import streamlit as st
from engine import (
    init_state, reset_state, get_workspace, get_job, get_raw_df, has_data,
    KPIDef, AGG_FUNCS, add_kpi, remove_kpi, compute_kpi,
)

st.set_page_config(page_title="KPIs — Dashboard Studio", page_icon="🔢", layout="wide")
init_state()

ws  = get_workspace()
job = get_job()

with st.sidebar:
    st.markdown("## 🖥️ Dashboard Studio")
    st.caption("APP-004 · OSEPA PMU Tool Suite")
    st.markdown("---")
    if ws:
        st.success(f"📁 **{ws['name']}**")
    else:
        st.warning("No workspace selected")
    st.info(f"**{len(job.dashboard_job.kpis)}** KPI(s) defined")
    if st.button("🗑 Reset Studio", use_container_width=True):
        reset_state(); st.rerun()

st.markdown("# 🔢 KPI Cards")
st.caption("Step 2 of 6 — Define metric cards for the dashboard header")
st.markdown("---")

if not has_data():
    st.warning("Please upload a file first."); st.stop()

df = get_raw_df()
all_cols     = list(df.columns)
numeric_cols = list(df.select_dtypes(include="number").columns)

if job.dashboard_job.kpis:
    st.markdown("### Current KPI Cards")
    cols = st.columns(min(len(job.dashboard_job.kpis), 4))
    for i, kdef in enumerate(job.dashboard_job.kpis):
        result = compute_kpi(df, kdef)
        with cols[i % 4]:
            status_emoji = {"good": "✅", "warn": "⚠️", "bad": "🔴", "neutral": "🔵"}.get(result.get("status", "neutral"), "🔵")
            st.metric(label=f"{status_emoji} {kdef.title}", value=result.get("formatted", "—"),
                      delta=result.get("change_str") or None)
            if st.button("Remove", key=f"del_{kdef.kpi_id}", use_container_width=True):
                remove_kpi(kdef.kpi_id); st.rerun()
    st.markdown("---")

st.markdown("### Add New KPI Card")
with st.form("kpi_form", clear_on_submit=True):
    c1, c2 = st.columns(2)
    title     = c1.text_input("KPI Title *", placeholder="e.g. Total Students Enrolled")
    source_col = c1.selectbox("Data Column *", numeric_cols or all_cols)
    agg_func   = c1.selectbox("Aggregation", list(AGG_FUNCS.keys()), format_func=lambda k: AGG_FUNCS[k])
    unit       = c2.text_input("Unit (suffix)", placeholder="%, Cr, lakh")
    comp_type  = c2.radio("Compare against", ["None", "Fixed target", "Target column"])
    higher_is_better = c2.checkbox("Higher = better", value=True)

    target_val = None
    target_col = ""
    target_agg = "sum"
    if comp_type == "Fixed target":
        target_val = st.number_input("Target value", value=100.0)
    elif comp_type == "Target column":
        ca, cb = st.columns(2)
        target_col = ca.selectbox("Target column", [c for c in numeric_cols if c != source_col] or numeric_cols)
        target_agg = cb.selectbox("Target aggregation", list(AGG_FUNCS.keys()), format_func=lambda k: AGG_FUNCS[k])

    if st.form_submit_button("Add KPI Card", type="primary"):
        if not title.strip():
            st.error("Title is required.")
        else:
            comp_map = {"None": "none", "Fixed target": "fixed", "Target column": "column"}
            add_kpi(KPIDef(title=title.strip(), source_col=source_col, agg_func=agg_func, unit=unit.strip(),
                           comparison_type=comp_map[comp_type],
                           target_value=float(target_val) if target_val is not None else None,
                           target_col=target_col, target_agg=target_agg, higher_is_better=higher_is_better))
            st.success(f"KPI **{title.strip()}** added."); st.rerun()
