"""Page 3 — Define charts."""
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
    init_state, reset_state, get_workspace, get_job, get_raw_df, has_data,
    ChartDef, CHART_TYPES, AGG_FUNCS,
    add_chart, remove_chart, prepare_chart_data,
)

st.set_page_config(page_title="Charts — Dashboard Studio", page_icon="📈", layout="wide")
init_state()

ws  = get_workspace()
job = get_job()

with st.sidebar:
    sidebar_brand("Dashboard Studio", "APP-004")
    if ws:
        st.success(f"📁 **{ws['name']}**")
    else:
        st.warning("No workspace selected")
    st.info(f"**{len(job.dashboard_job.charts)}** chart(s) defined")
    if st.button("🗑 Reset Studio", use_container_width=True):
        reset_state(); st.rerun()

page_header("Charts", subtitle="Configure visualisations for your dashboard", icon="📊", step=3, total_steps=6)

if not has_data():
    st.warning("Please upload a file first."); st.stop()

df = get_raw_df()
all_cols     = list(df.columns)
numeric_cols = list(df.select_dtypes(include="number").columns)
cat_cols     = list(df.select_dtypes(exclude="number").columns)

if job.dashboard_job.charts:
    st.markdown("### Defined Charts")
    for cdef in job.dashboard_job.charts:
        with st.expander(f"**{cdef.title}** · {cdef.chart_type.title()}", expanded=False):
            c1, c2 = st.columns([4, 1])
            c1.markdown(f"X: **{cdef.x_col}** · Y: **{', '.join(cdef.y_cols)}** · {AGG_FUNCS.get(cdef.agg_func, '')}")
            with c2:
                if st.button("Remove", key=f"del_{cdef.chart_id}", use_container_width=True):
                    remove_chart(cdef.chart_id); st.rerun()
                if st.button("Preview", key=f"prev_{cdef.chart_id}", use_container_width=True):
                    st.session_state[f"show_prev_{cdef.chart_id}"] = True

            if st.session_state.get(f"show_prev_{cdef.chart_id}"):
                preview_df = prepare_chart_data(df, cdef)
                if not preview_df.empty and cdef.y_cols:
                    st.caption(f"**{cdef.title}** — data preview")
                    try:
                        plot_df = preview_df.set_index(cdef.x_col)[cdef.y_cols]
                        if cdef.chart_type in ("bar", "column"):
                            st.bar_chart(plot_df)
                        elif cdef.chart_type == "line":
                            st.line_chart(plot_df)
                        elif cdef.chart_type == "area":
                            st.area_chart(plot_df)
                        else:
                            st.dataframe(preview_df, use_container_width=True, hide_index=True)
                    except Exception:
                        st.dataframe(preview_df, use_container_width=True, hide_index=True)
    st.markdown("---")

st.markdown("### Add New Chart")
with st.form("chart_form", clear_on_submit=True):
    c1, c2 = st.columns(2)
    title      = c1.text_input("Chart Title *")
    chart_type = c1.selectbox("Chart Type", list(CHART_TYPES.keys()), format_func=lambda k: CHART_TYPES[k])
    x_col      = c2.selectbox("X-Axis / Category Column", (cat_cols + numeric_cols) or all_cols)
    agg_func   = c2.selectbox("Aggregation", list(AGG_FUNCS.keys()), format_func=lambda k: AGG_FUNCS[k])

    pie_note = " (first column only for pie)" if chart_type == "pie" else ""
    y_cols = st.multiselect(f"Y-Axis Column(s){pie_note}", numeric_cols)

    c3, c4, c5 = st.columns(3)
    sort_col = c3.selectbox("Sort by", ["(default)"] + numeric_cols)
    sort_asc = c3.checkbox("Sort ascending", value=False)
    top_n    = c4.number_input("Top N (0 = all)", min_value=0, value=0, step=5)
    stacked  = c5.checkbox("Stacked", value=False)

    if st.form_submit_button("Add Chart", type="primary"):
        if not title.strip() or not y_cols:
            st.error("Title and at least one Y column are required.")
        else:
            add_chart(ChartDef(
                title=title.strip(), chart_type=chart_type, x_col=x_col, y_cols=y_cols,
                agg_func=agg_func, top_n=int(top_n),
                sort_col=sort_col if sort_col != "(default)" else "",
                sort_asc=sort_asc, stacked=stacked,
            ))
            st.success(f"Chart **{title.strip()}** added."); st.rerun()
