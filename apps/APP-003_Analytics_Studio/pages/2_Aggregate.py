"""Page 2 — Aggregation builder: define groupings and metrics."""
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
    init_state, reset_state, get_workspace, get_job,
    has_data, get_raw_df,
    add_agg_config, remove_agg_config, get_agg_results, set_agg_results,
    AggConfig, MetricDef, AGG_FUNCS, suggest_agg_func,
    run_all_configs,
)

st.set_page_config(page_title="Aggregate — Analytics Studio", page_icon="🔢", layout="wide")
init_state()

ws  = get_workspace()
job = get_job()

with st.sidebar:
    st.markdown("## 📊 Analytics Studio")
    st.caption("APP-003 · OSEPA PMU Tool Suite")
    st.markdown("---")
    if ws:
        st.success(f"📁 **{ws['name']}**")
    else:
        st.warning("No workspace selected")
    st.info(f"**{len(job.agg_job.configs)}** aggregation(s) defined")
    if st.button("🗑 Reset Studio", use_container_width=True):
        reset_state(); st.rerun()

st.markdown("# 🔢 Aggregate")
st.caption("Step 2 of 6 — Group data and compute summary metrics")
st.markdown("---")

if not has_data():
    st.warning("Please upload a file first (Step 1 — Upload).")
    st.stop()

df   = get_raw_df()
cols = df.columns.tolist()
num_cols = list(df.select_dtypes(include="number").columns)

# ── Define new aggregation ────────────────────────────────────────────────────
with st.expander("➕ Define New Aggregation", expanded=len(job.agg_job.configs) == 0):
    agg_name   = st.text_input("Aggregation name", placeholder="e.g. District Summary")
    group_cols = st.multiselect("Group by (rows become unique combinations)", cols)
    st.markdown("**Metrics to compute:**")

    metrics    = []
    metric_cols = st.multiselect("Select columns to aggregate", num_cols)
    for mc in metric_cols:
        c_fn, c_alias = st.columns([2, 2])
        fn    = c_fn.selectbox(f"`{mc}` — function", list(AGG_FUNCS.keys()),
                               index=list(AGG_FUNCS.keys()).index(suggest_agg_func(mc)),
                               format_func=lambda k: AGG_FUNCS[k], key=f"fn_{mc}")
        alias = c_alias.text_input(f"Column label", key=f"alias_{mc}")
        metrics.append(MetricDef(source_col=mc, agg_func=fn, alias=alias))

    c1, c2 = st.columns(2)
    include_totals = c1.checkbox("Include grand totals row", value=True)
    sort_by    = c2.selectbox("Sort result by", ["— none —"] + [m.effective_alias() for m in metrics if metrics])
    sort_asc   = c2.checkbox("Ascending", value=False)

    if st.button("Add Aggregation", type="primary") and agg_name.strip() and group_cols and metrics:
        cfg = AggConfig(
            name=agg_name.strip(), group_cols=group_cols, metrics=metrics,
            include_totals=include_totals,
            sort_by=sort_by if sort_by != "— none —" else "",
            sort_asc=sort_asc,
        )
        add_agg_config(cfg)
        st.success(f"Aggregation **{agg_name}** added."); st.rerun()

# ── Configured aggregations ───────────────────────────────────────────────────
st.markdown("### Configured Aggregations")
if not job.agg_job.configs:
    st.info("No aggregations defined yet. Add one above.")
    st.stop()

for cfg in job.agg_job.configs:
    with st.container(border=True):
        c1, c2 = st.columns([4, 1])
        c1.markdown(f"**{cfg.name}** · Group: {', '.join(cfg.group_cols)} · "
                    f"{len(cfg.metrics)} metric(s)")
        if c2.button("Remove", key=f"rm_{cfg.config_id}", use_container_width=True):
            remove_agg_config(cfg.config_id); st.rerun()

# ── Run ───────────────────────────────────────────────────────────────────────
st.markdown("---")
if st.button("▶ Run All Aggregations", type="primary", use_container_width=True):
    with st.spinner("Aggregating…"):
        results = run_all_configs(df, job.agg_job.configs)
    set_agg_results(results)
    st.success(f"Done. {len(results)} aggregation(s) computed."); st.rerun()

# ── Results preview ───────────────────────────────────────────────────────────
agg_results = get_agg_results()
if agg_results:
    for cfg in job.agg_job.configs:
        result_df = agg_results.get(cfg.config_id)
        if result_df is not None and not result_df.empty:
            st.markdown(f"#### {cfg.name}")
            m1, m2 = st.columns(2)
            m1.metric("Result Rows", len(result_df))
            m2.metric("Result Columns", len(result_df.columns))
            with st.expander(f"Preview — {cfg.name}", expanded=True):
                st.dataframe(result_df, use_container_width=True, hide_index=True)
