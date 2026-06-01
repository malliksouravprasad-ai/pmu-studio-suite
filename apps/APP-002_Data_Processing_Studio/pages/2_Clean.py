"""Page 2 — Data cleaning: missing values, duplicates, text standardization."""
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
    has_data, get_raw_df, add_transform_step, remove_transform_step,
    toggle_transform_step, get_transform_log,
    TransformStep,
)

st.set_page_config(page_title="Clean — Data Processing Studio", page_icon="🧹", layout="wide")
init_state()

ws  = get_workspace()
job = get_job()

with st.sidebar:
    st.markdown("## ⚙️ Data Processing Studio")
    st.caption("APP-002 · OSEPA PMU Tool Suite")
    st.markdown("---")
    if ws:
        st.success(f"📁 **{ws['name']}**")
    else:
        st.warning("No workspace selected")
    steps = [s for s in job.transform_job.steps if s.enabled]
    st.info(f"**{len(steps)}** step(s) in pipeline")
    if st.button("🗑 Reset Studio", use_container_width=True):
        reset_state(); st.rerun()

st.markdown("# 🧹 Clean")
st.caption("Step 2 of 6 — Handle missing values, duplicates, and text quality")
st.markdown("---")

if not has_data():
    st.warning("Please upload a file first (Step 1 — Upload).")
    st.stop()

df   = get_raw_df()
cols = df.columns.tolist()
text_cols = list(df.select_dtypes(exclude="number").columns)

# ── Data quality overview ─────────────────────────────────────────────────────
st.markdown("### Data Quality Overview")
null_counts = df.isnull().sum()
dup_count   = df.duplicated().sum()

m1, m2, m3, m4 = st.columns(4)
m1.metric("Total Rows",       f"{len(df):,}")
m2.metric("Columns with Nulls", int((null_counts > 0).sum()))
m3.metric("Total Null Cells",  f"{int(null_counts.sum()):,}")
m4.metric("Duplicate Rows",   f"{dup_count:,}")

qual_df = pd.DataFrame({
    "Column":     cols,
    "Type":       [str(df[c].dtype) for c in cols],
    "Null Count": [int(null_counts[c]) for c in cols],
    "Null %":     [round(df[c].isna().mean() * 100, 1) for c in cols],
}).query("`Null Count` > 0")

if not qual_df.empty:
    with st.expander("Columns with missing values", expanded=True):
        st.dataframe(qual_df, use_container_width=True, hide_index=True)

st.markdown("---")

# ── Cleaning operations ───────────────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs(["Missing Values", "Duplicates", "Text Standardization"])

with tab1:
    st.markdown("#### Fill Missing Values")
    fill_cols  = st.multiselect("Select column(s)", cols)
    fill_mode  = st.radio("Fill with", ["Constant value", "Mean", "Median", "Mode"], horizontal=True)

    if fill_mode == "Constant value":
        fill_val = st.text_input("Fill value", value="0")
        if st.button("Add: Fill Missing (Constant)", type="primary") and fill_cols:
            add_transform_step(TransformStep(
                op_type="fill_missing_value",
                description=f'Fill nulls in {", ".join(fill_cols)} with "{fill_val}"',
                params={"columns": fill_cols, "fill_value": fill_val},
            ))
            st.success("Step added.")
            st.rerun()
    else:
        stat_map = {"Mean": "mean", "Median": "median", "Mode": "mode"}
        stat = stat_map[fill_mode]
        if st.button(f"Add: Fill Missing ({fill_mode})", type="primary") and fill_cols:
            for col in fill_cols:
                add_transform_step(TransformStep(
                    op_type="fill_missing_stat",
                    description=f'Fill nulls in "{col}" with {stat}',
                    params={"column": col, "stat": stat},
                ))
            st.success(f"{len(fill_cols)} step(s) added.")
            st.rerun()

    st.markdown("#### Drop Rows with Missing Values")
    drop_col = st.selectbox("Drop rows where this column is blank", ["— choose —"] + cols)
    if drop_col != "— choose —":
        if st.button("Add: Drop Blank Rows", type="primary"):
            add_transform_step(TransformStep(
                op_type="remove_blanks",
                description=f'Remove rows where "{drop_col}" is blank',
                params={"column": drop_col},
            ))
            st.success("Step added.")
            st.rerun()

with tab2:
    st.markdown(f"#### Remove Duplicate Rows")
    st.caption(f"Dataset currently has **{dup_count:,}** exact duplicate rows.")
    dup_cols  = st.multiselect("Consider only these columns (blank = all columns)", cols)
    keep_opt  = st.radio("Keep", ["First occurrence", "Last occurrence"], horizontal=True)
    keep_map  = {"First occurrence": "first", "Last occurrence": "last"}

    if st.button("Add: Remove Duplicates", type="primary"):
        add_transform_step(TransformStep(
            op_type="remove_duplicates",
            description=f"Remove duplicates ({keep_opt})" + (f" on {', '.join(dup_cols)}" if dup_cols else ""),
            params={"subset": dup_cols or None, "keep": keep_map[keep_opt]},
        ))
        st.success("Step added.")
        st.rerun()

with tab3:
    st.markdown("#### Strip Whitespace")
    strip_cols = st.multiselect("Columns to strip", text_cols, default=text_cols[:10] if len(text_cols) > 10 else text_cols, key="strip_cols")
    if st.button("Add: Strip Whitespace", type="primary") and strip_cols:
        for col in strip_cols:
            add_transform_step(TransformStep(
                op_type="format_column",
                description=f'Strip whitespace: "{col}"',
                params={"column": col, "format_type": "text_strip"},
            ))
        st.success(f"{len(strip_cols)} step(s) added.")
        st.rerun()

    st.markdown("#### Standardize Case")
    case_cols  = st.multiselect("Columns", text_cols, key="case_cols")
    case_type  = st.radio("Apply", ["UPPERCASE", "lowercase", "Title Case"], horizontal=True)
    case_map   = {"UPPERCASE": "text_upper", "lowercase": "text_lower", "Title Case": "text_title"}
    if st.button("Add: Standardize Case", type="primary") and case_cols:
        for col in case_cols:
            add_transform_step(TransformStep(
                op_type="format_column",
                description=f'Format "{col}": {case_type}',
                params={"column": col, "format_type": case_map[case_type]},
            ))
        st.success(f"{len(case_cols)} step(s) added.")
        st.rerun()

# ── Pipeline view ─────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("### Cleaning Pipeline")
all_steps = job.transform_job.steps
if not all_steps:
    st.info("No steps added yet. Add cleaning operations above.")
else:
    for step in all_steps:
        with st.container(border=True):
            c1, c2, c3 = st.columns([5, 1, 1])
            icon = "✅" if step.enabled else "⏸"
            c1.markdown(f"{icon} `{step.op_type.replace('_', ' ').title()}` — {step.description}")
            with c2:
                if st.button("Toggle", key=f"tog_{step.step_id}", use_container_width=True):
                    toggle_transform_step(step.step_id); st.rerun()
            with c3:
                if st.button("Remove", key=f"rem_{step.step_id}", use_container_width=True):
                    remove_transform_step(step.step_id); st.rerun()
