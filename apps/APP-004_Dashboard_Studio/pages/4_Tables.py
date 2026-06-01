"""Page 4 — Define summary tables."""
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
    TableDef, AGG_FUNCS, add_table, remove_table, build_table,
)

st.set_page_config(page_title="Tables — Dashboard Studio", page_icon="📋", layout="wide")
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
    st.info(f"**{len(job.dashboard_job.tables)}** table(s) defined")
    if st.button("🗑 Reset Studio", use_container_width=True):
        reset_state(); st.rerun()

st.markdown("# 📋 Tables")
st.caption("Step 4 of 6 — Define summary tables for the dashboard")
st.markdown("---")

if not has_data():
    st.warning("Please upload a file first."); st.stop()

df = get_raw_df()
all_cols     = list(df.columns)
numeric_cols = list(df.select_dtypes(include="number").columns)
cat_cols     = list(df.select_dtypes(exclude="number").columns)

if job.dashboard_job.tables:
    st.markdown("### Defined Tables")
    for tdef in job.dashboard_job.tables:
        with st.expander(f"**{tdef.title}**", expanded=False):
            c1, c2 = st.columns([4, 1])
            c1.markdown(f"Group: **{', '.join(tdef.group_cols)}** · "
                        f"Metrics: **{', '.join(tdef.metric_cols)}**")
            with c2:
                if st.button("Remove", key=f"del_{tdef.table_id}", use_container_width=True):
                    remove_table(tdef.table_id); st.rerun()
                if st.button("Preview", key=f"prev_{tdef.table_id}", use_container_width=True):
                    preview = build_table(df, tdef)
                    if not preview.empty:
                        st.dataframe(preview, use_container_width=True, hide_index=True)
    st.markdown("---")

st.markdown("### Add New Table")
with st.form("table_form", clear_on_submit=True):
    title       = st.text_input("Table Title *")
    group_cols  = st.multiselect("Group by column(s) *", cat_cols + all_cols)
    metric_cols = st.multiselect("Metric column(s) *", numeric_cols)
    agg_funcs   = {}
    for mc in metric_cols:
        agg_funcs[mc] = st.selectbox(f"Aggregation for `{mc}`", list(AGG_FUNCS.keys()),
                                      format_func=lambda k: AGG_FUNCS[k], key=f"agg_{mc}")

    c1, c2, c3 = st.columns(3)
    sort_col = c1.selectbox("Sort by", ["(default)"] + metric_cols)
    sort_asc = c1.checkbox("Sort ascending", value=False)
    top_n    = c2.number_input("Top N (0 = all)", min_value=0, value=0)
    totals   = c3.checkbox("Include totals row", value=True)

    if st.form_submit_button("Add Table", type="primary"):
        if not title.strip() or not group_cols or not metric_cols:
            st.error("Title, group columns, and metric columns are required.")
        else:
            add_table(TableDef(
                title=title.strip(), group_cols=group_cols, metric_cols=metric_cols,
                agg_funcs=agg_funcs, top_n=int(top_n),
                sort_col=sort_col if sort_col != "(default)" else "",
                sort_asc=sort_asc, include_totals=totals,
            ))
            st.success(f"Table **{title.strip()}** added."); st.rerun()
