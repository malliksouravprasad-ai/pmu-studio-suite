"""Page 4 — Ranking and variance analysis."""
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
    add_ranking, remove_ranking, get_rank_results, set_rank_results,
    add_variance, remove_variance, get_var_results, set_var_results,
    RankDef, VarianceDef, RANK_MODES, VARIANCE_MODES,
    rank_entities, calc_variance,
)

st.set_page_config(page_title="Analyse — Analytics Studio", page_icon="📈", layout="wide")
init_state()

ws  = get_workspace()
job = get_job()

with st.sidebar:
    sidebar_brand("Analytics Studio", "APP-003")
    if ws:
        st.success(f"📁 **{ws['name']}**")
    else:
        st.warning("No workspace selected")
    n_rank = len([r for r in job.analytics_job.rankings if r.enabled])
    n_var  = len([v for v in job.analytics_job.variances if v.enabled])
    st.info(f"**{n_rank}** ranking(s) · **{n_var}** variance(s)")
    if st.button("🗑 Reset Studio", use_container_width=True):
        reset_state(); st.rerun()

page_header("Analyse", subtitle="Rank, compare, and score entities", icon="🔬", step=4, total_steps=6)

if not has_data():
    st.warning("Please upload a file first (Step 1 — Upload).")
    st.stop()

df   = get_raw_df()
cols = df.columns.tolist()
num_cols = list(df.select_dtypes(include="number").columns)

tab1, tab2 = st.tabs(["Ranking", "Variance Analysis"])

# ── Tab 1: Ranking ────────────────────────────────────────────────────────────
with tab1:
    with st.expander("➕ Add Ranking", expanded=not job.analytics_job.rankings):
        c1, c2 = st.columns(2)
        r_name = c1.text_input("Ranking name", placeholder="e.g. District Performance")
        r_mode = c2.selectbox("Ranking mode", list(RANK_MODES.keys()), format_func=lambda k: RANK_MODES[k])
        c3, c4 = st.columns(2)
        r_entity = c3.selectbox("Entity column (e.g. District)", ["— choose —"] + cols)
        r_value  = c4.selectbox("Value column", ["— choose —"] + num_cols) if r_mode != "weighted" else None
        r_top_n  = st.number_input("Show top N", min_value=1, value=10) if r_mode in ("top_n", "bottom_n") else 0
        r_asc    = st.checkbox("Ascending (lowest first)", value=False)

        weight_cols = weight_vals = []
        if r_mode == "weighted":
            weight_cols = st.multiselect("Indicator columns", num_cols)
            if weight_cols:
                weight_vals = [st.number_input(f"Weight for {c}", value=1.0, min_value=0.0, key=f"w_{c}")
                               for c in weight_cols]

        if st.button("Add Ranking", type="primary") and r_name.strip() and r_entity != "— choose —":
            rdef = RankDef(
                name=r_name.strip(), entity_col=r_entity,
                value_col=(r_value if r_value != "— choose —" else "") or "",
                rank_mode=r_mode, ascending=r_asc,
                top_n=int(r_top_n) if r_top_n else 5,
                weight_cols=weight_cols, weight_values=weight_vals,
            )
            add_ranking(rdef); st.success("Ranking added."); st.rerun()

    st.markdown("**Defined Rankings**")
    for rdef in job.analytics_job.rankings:
        with st.container(border=True):
            c1, c2 = st.columns([4, 1])
            c1.markdown(f"**{rdef.name}** · `{RANK_MODES[rdef.rank_mode]}` · entity: {rdef.entity_col}")
            if c2.button("Remove", key=f"rrm_{rdef.rank_id}", use_container_width=True):
                remove_ranking(rdef.rank_id); st.rerun()

    if job.analytics_job.rankings:
        if st.button("▶ Run All Rankings", type="primary"):
            results = {}
            for rdef in job.analytics_job.rankings:
                if rdef.enabled:
                    results[rdef.rank_id] = rank_entities(df, rdef)
            set_rank_results(results)
            st.success(f"{len(results)} ranking(s) computed."); st.rerun()

    rank_results = get_rank_results()
    for rdef in job.analytics_job.rankings:
        result_df = rank_results.get(rdef.rank_id)
        if result_df is not None and not result_df.empty:
            with st.expander(f"Results — {rdef.name}", expanded=True):
                st.dataframe(result_df, use_container_width=True, hide_index=True)

# ── Tab 2: Variance ───────────────────────────────────────────────────────────
with tab2:
    with st.expander("➕ Add Variance Analysis", expanded=not job.analytics_job.variances):
        c1, c2 = st.columns(2)
        v_name = c1.text_input("Analysis name", placeholder="e.g. Enrolment vs Target", key="vname")
        v_mode = c2.selectbox("Mode", list(VARIANCE_MODES.keys()), format_func=lambda k: VARIANCE_MODES[k])
        c3 = st.columns(1)[0]
        v_entity = st.selectbox("Entity column", ["— choose —"] + cols, key="ventity")

        if v_mode == "target_vs_achievement":
            c_a, c_b = st.columns(2)
            v_actual = c_a.selectbox("Actual column", ["— choose —"] + num_cols)
            v_target = c_b.selectbox("Target column", ["— choose —"] + num_cols)
            v_p_a = v_p_b = ""
        else:
            c_a, c_b = st.columns(2)
            v_p_a = c_a.selectbox("Period A column", ["— choose —"] + num_cols)
            v_p_b = c_b.selectbox("Period B column", ["— choose —"] + num_cols)
            v_actual = v_target = ""

        if st.button("Add Variance Analysis", type="primary") and v_name.strip() and v_entity != "— choose —":
            vdef = VarianceDef(
                name=v_name.strip(), entity_col=v_entity,
                variance_mode=v_mode,
                actual_col=v_actual if v_actual != "— choose —" else "",
                target_col=v_target if v_target != "— choose —" else "",
                period_a_col=v_p_a if v_p_a != "— choose —" else "",
                period_b_col=v_p_b if v_p_b != "— choose —" else "",
            )
            add_variance(vdef); st.success("Variance analysis added."); st.rerun()

    st.markdown("**Defined Variance Analyses**")
    for vdef in job.analytics_job.variances:
        with st.container(border=True):
            c1, c2 = st.columns([4, 1])
            c1.markdown(f"**{vdef.name}** · `{VARIANCE_MODES[vdef.variance_mode]}` · entity: {vdef.entity_col}")
            if c2.button("Remove", key=f"vrm_{vdef.var_id}", use_container_width=True):
                remove_variance(vdef.var_id); st.rerun()

    if job.analytics_job.variances:
        if st.button("▶ Run All Variance Analyses", type="primary", key="runvar"):
            results = {}
            for vdef in job.analytics_job.variances:
                if vdef.enabled:
                    results[vdef.var_id] = calc_variance(df, vdef)
            set_var_results(results)
            st.success(f"{len(results)} variance analysis(es) computed."); st.rerun()

    var_results = get_var_results()
    for vdef in job.analytics_job.variances:
        result_df = var_results.get(vdef.var_id)
        if result_df is not None and not result_df.empty:
            with st.expander(f"Results — {vdef.name}", expanded=True):
                st.dataframe(result_df, use_container_width=True, hide_index=True)
