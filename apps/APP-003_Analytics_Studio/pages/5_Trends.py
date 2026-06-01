"""Page 5 — Trend analysis across reporting periods."""
import sys
import os

_APP_DIR  = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_PMU_ROOT = os.path.dirname(os.path.dirname(_APP_DIR))
for _p in [_PMU_ROOT, _APP_DIR]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

import pandas as pd
import streamlit as st
from shared.theme import page_header, sidebar_brand
from engine import (
    init_state, reset_state, get_workspace, get_job,
    has_data, get_raw_df,
    add_trend, remove_trend, get_trend_results, set_trend_results,
    TrendDef, TREND_INTERPRETATIONS,
    analyze_trend,
)

st.set_page_config(page_title="Trends — Analytics Studio", page_icon="📉", layout="wide")
init_state()

ws  = get_workspace()
job = get_job()

with st.sidebar:
    sidebar_brand("Analytics Studio", "APP-003")
    if ws:
        st.success(f"📁 **{ws['name']}**")
    else:
        st.warning("No workspace selected")
    n_trends = len([t for t in job.analytics_job.trends if t.enabled])
    st.info(f"**{n_trends}** trend(s) defined")
    if st.button("🗑 Reset Studio", use_container_width=True):
        reset_state(); st.rerun()

page_header("Trends", subtitle="Track changes over time with trend analysis", icon="📈", step=5, total_steps=6)

if not has_data():
    st.warning("Please upload a file first (Step 1 — Upload).")
    st.stop()

df   = get_raw_df()
cols = df.columns.tolist()

# ── Define trend ──────────────────────────────────────────────────────────────
with st.expander("➕ Add Trend Analysis", expanded=not job.analytics_job.trends):
    c1, c2 = st.columns(2)
    t_name   = c1.text_input("Trend name", placeholder="e.g. Attendance Trend 2023-2026")
    t_entity = c2.selectbox("Entity column", ["— choose —"] + cols)

    t_periods = st.multiselect(
        "Period columns (select in chronological order)",
        cols,
        help="Each column represents one reporting period (e.g. Q1, Q2, Q3).",
    )

    c3, c4 = st.columns(2)
    t_interp    = c3.selectbox("Interpretation", list(TREND_INTERPRETATIONS.keys()),
                                format_func=lambda k: TREND_INTERPRETATIONS[k])
    t_threshold = c4.number_input("Change threshold %", min_value=0.0, value=10.0,
                                   help="Changes below this % are considered stable.")

    if st.button("Add Trend Analysis", type="primary") and t_name.strip() and t_entity != "— choose —" and len(t_periods) >= 2:
        tdef = TrendDef(
            name=t_name.strip(), entity_col=t_entity,
            period_cols=t_periods, value_interpretation=t_interp,
            change_threshold_pct=t_threshold,
        )
        add_trend(tdef); st.success("Trend analysis added."); st.rerun()
    elif st.session_state.get("_trend_btn_clicked") and len(t_periods) < 2:
        st.warning("Select at least 2 period columns.")

# ── Defined trends ────────────────────────────────────────────────────────────
st.markdown("### Defined Trends")
if not job.analytics_job.trends:
    st.info("No trend analyses defined yet. Add one above.")
    st.stop()

for tdef in job.analytics_job.trends:
    with st.container(border=True):
        c1, c2 = st.columns([4, 1])
        c1.markdown(f"**{tdef.name}** · entity: {tdef.entity_col} · "
                    f"periods: {', '.join(tdef.period_cols)}")
        if c2.button("Remove", key=f"trm_{tdef.trend_id}", use_container_width=True):
            remove_trend(tdef.trend_id); st.rerun()

# ── Run ───────────────────────────────────────────────────────────────────────
st.markdown("---")
if st.button("▶ Run All Trend Analyses", type="primary", use_container_width=True):
    results = {}
    with st.spinner("Analysing trends…"):
        for tdef in job.analytics_job.trends:
            if tdef.enabled:
                results[tdef.trend_id] = analyze_trend(df, tdef)
    set_trend_results(results)
    st.success(f"{len(results)} trend analysis(es) computed."); st.rerun()

# ── Results ───────────────────────────────────────────────────────────────────
trend_results = get_trend_results()
for tdef in job.analytics_job.trends:
    result_df = trend_results.get(tdef.trend_id)
    if result_df is not None and not result_df.empty:
        with st.expander(f"Results — {tdef.name}", expanded=True):
            st.dataframe(result_df, use_container_width=True, hide_index=True)
