"""Page 3 — Data transformation: rename, merge, split, format, filter, sort."""
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
    add_transform_step, remove_transform_step, toggle_transform_step,
    move_transform_step_up, move_transform_step_down,
    TransformStep, FORMAT_TYPES, MATH_OPS, FILTER_OPS,
)

st.set_page_config(page_title="Transform — Data Processing Studio", page_icon="🔧", layout="wide")
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
    enabled = [s for s in job.transform_job.steps if s.enabled]
    st.info(f"**{len(enabled)}** step(s) in pipeline")
    if st.button("🗑 Reset Studio", use_container_width=True):
        reset_state(); st.rerun()

st.markdown("# 🔧 Transform")
st.caption("Step 3 of 6 — Reshape columns and rows")
st.markdown("---")

if not has_data():
    st.warning("Please upload a file first (Step 1 — Upload).")
    st.stop()

df   = get_raw_df()
cols = df.columns.tolist()
num_cols  = list(df.select_dtypes(include="number").columns)
text_cols = list(df.select_dtypes(exclude="number").columns)

tab1, tab2, tab3 = st.tabs(["Column Manager", "Column Transformer", "Row Operations"])

# ── Tab 1: Column Manager ─────────────────────────────────────────────────────
with tab1:
    st.markdown("#### Rename Columns")
    rename_from = st.selectbox("Column to rename", ["— choose —"] + cols, key="ren_from")
    rename_to   = st.text_input("New name", key="ren_to")
    if st.button("Add: Rename", type="primary") and rename_from != "— choose —" and rename_to.strip():
        add_transform_step(TransformStep(
            op_type="rename",
            description=f'"{rename_from}" → "{rename_to.strip()}"',
            params={"renames": {rename_from: rename_to.strip()}},
        ))
        st.success("Step added."); st.rerun()

    st.markdown("---")
    st.markdown("#### Reorder Columns")
    reorder_sel = st.multiselect("Set column order (unselected columns appended at end)", cols, default=cols, key="reorder_sel")
    if st.button("Add: Reorder", type="primary") and reorder_sel:
        add_transform_step(TransformStep(
            op_type="reorder",
            description=f"Reorder: {', '.join(reorder_sel[:5])}{'...' if len(reorder_sel) > 5 else ''}",
            params={"order": reorder_sel},
        ))
        st.success("Step added."); st.rerun()

    st.markdown("---")
    st.markdown("#### Delete Columns")
    del_cols = st.multiselect("Columns to delete", cols, key="del_cols")
    if st.button("Add: Delete Columns", type="primary") and del_cols:
        add_transform_step(TransformStep(
            op_type="delete",
            description=f"Delete: {', '.join(del_cols)}",
            params={"columns": del_cols},
        ))
        st.success("Step added."); st.rerun()

# ── Tab 2: Column Transformer ─────────────────────────────────────────────────
with tab2:
    sub = st.selectbox("Operation", ["Merge Columns", "Split Column", "Format Column", "Create Column"])

    if sub == "Merge Columns":
        src_cols  = st.multiselect("Source columns (in order)", cols)
        sep       = st.text_input("Separator", value=" ")
        new_name  = st.text_input("New column name", value="Merged")
        drop_src  = st.checkbox("Drop source columns after merge")
        if st.button("Add: Merge Columns", type="primary") and len(src_cols) >= 2:
            add_transform_step(TransformStep(
                op_type="merge_columns",
                description=f'Merge {", ".join(src_cols)} → "{new_name}"',
                params={"source_cols": src_cols, "separator": sep, "new_col_name": new_name, "drop_sources": drop_src},
            ))
            st.success("Step added."); st.rerun()

    elif sub == "Split Column":
        src_col    = st.selectbox("Column to split", ["— choose —"] + cols)
        delimiter  = st.text_input("Delimiter", value=" ")
        new_names  = st.text_input("Output column names (comma-separated)", value="Part1,Part2")
        drop_src   = st.checkbox("Drop source column after split")
        if st.button("Add: Split Column", type="primary") and src_col != "— choose —":
            name_list = [n.strip() for n in new_names.split(",") if n.strip()]
            add_transform_step(TransformStep(
                op_type="split_column",
                description=f'Split "{src_col}" on "{delimiter}" → {", ".join(name_list)}',
                params={"source_col": src_col, "delimiter": delimiter, "new_col_names": name_list, "drop_source": drop_src},
            ))
            st.success("Step added."); st.rerun()

    elif sub == "Format Column":
        fmt_col  = st.selectbox("Column", ["— choose —"] + cols)
        fmt_type = st.selectbox("Format", list(FORMAT_TYPES.keys()), format_func=lambda k: FORMAT_TYPES[k])
        extra_params = {}
        if fmt_type == "prefix_suffix":
            extra_params["prefix"] = st.text_input("Prefix", value="")
            extra_params["suffix"] = st.text_input("Suffix", value="")
        elif fmt_type == "round_numeric":
            extra_params["decimals"] = st.number_input("Decimal places", min_value=0, max_value=10, value=2)
        elif fmt_type == "date_reformat":
            extra_params["date_input_format"]  = st.text_input("Input format",  value="%d/%m/%Y")
            extra_params["date_output_format"] = st.text_input("Output format", value="%d %b %Y")
        if st.button("Add: Format Column", type="primary") and fmt_col != "— choose —":
            add_transform_step(TransformStep(
                op_type="format_column",
                description=f'Format "{fmt_col}": {FORMAT_TYPES[fmt_type]}',
                params={"column": fmt_col, "format_type": fmt_type, **extra_params},
            ))
            st.success("Step added."); st.rerun()

    elif sub == "Create Column":
        new_col_name = st.text_input("New column name", value="New Column")
        create_type  = st.radio("Create from", ["Constant value", "Copy column", "Math formula"], horizontal=True)
        extra_params = {"creation_type": "constant", "new_col_name": new_col_name}
        if create_type == "Constant value":
            extra_params["value"] = st.text_input("Constant value", value="")
        elif create_type == "Copy column":
            extra_params["creation_type"] = "copy"
            extra_params["source_col"]    = st.selectbox("Source column", ["— choose —"] + cols)
        elif create_type == "Math formula":
            extra_params["creation_type"] = "math"
            c_a, c_b, c_op = st.columns(3)
            extra_params["col_a"] = c_a.selectbox("Column A", ["— choose —"] + num_cols)
            extra_params["op"]    = c_op.selectbox("Operation", list(MATH_OPS.keys()), format_func=lambda k: MATH_OPS[k])
            extra_params["col_b"] = c_b.selectbox("Column B", ["— choose —"] + num_cols)
        if st.button("Add: Create Column", type="primary") and new_col_name.strip():
            add_transform_step(TransformStep(
                op_type="create_column",
                description=f'Create "{new_col_name}": {create_type}',
                params=extra_params,
            ))
            st.success("Step added."); st.rerun()

# ── Tab 3: Row Operations ─────────────────────────────────────────────────────
with tab3:
    row_op = st.selectbox("Operation", ["Filter Rows", "Sort Rows"])

    if row_op == "Filter Rows":
        f_col  = st.selectbox("Filter column", ["— choose —"] + cols)
        f_op   = st.selectbox("Condition", list(FILTER_OPS.keys()), format_func=lambda k: FILTER_OPS[k])
        f_val  = "" if f_op in ("is_blank", "is_not_blank") else st.text_input("Value")
        if st.button("Add: Filter Rows", type="primary") and f_col != "— choose —":
            desc = f'Keep rows where "{f_col}" {FILTER_OPS[f_op]}'
            if f_val:
                desc += f' "{f_val}"'
            add_transform_step(TransformStep(
                op_type="filter",
                description=desc,
                params={"column": f_col, "operator": f_op, "value": f_val},
            ))
            st.success("Step added."); st.rerun()

    elif row_op == "Sort Rows":
        s_cols  = st.multiselect("Sort by column(s)", cols)
        s_order = st.radio("Order", ["Ascending", "Descending"], horizontal=True)
        if st.button("Add: Sort Rows", type="primary") and s_cols:
            add_transform_step(TransformStep(
                op_type="sort",
                description=f"Sort by {', '.join(s_cols)} ({s_order})",
                params={"columns": s_cols, "ascending": s_order == "Ascending"},
            ))
            st.success("Step added."); st.rerun()

# ── Pipeline view ─────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("### Transformation Pipeline")
all_steps = job.transform_job.steps
if not all_steps:
    st.info("No steps yet. Add operations above.")
else:
    n_steps = len(all_steps)
    for i, step in enumerate(all_steps):
        with st.container(border=True):
            c1, c2, c3, c4, c5 = st.columns([5, 1, 1, 1, 1])
            icon = "✅" if step.enabled else "⏸"
            c1.markdown(f"**{i+1}.** {icon} `{step.op_type.replace('_', ' ').title()}` — {step.description}")
            with c2:
                if i > 0 and st.button("↑", key=f"up_{step.step_id}", use_container_width=True, help="Move up"):
                    move_transform_step_up(step.step_id); st.rerun()
            with c3:
                if i < n_steps - 1 and st.button("↓", key=f"dn_{step.step_id}", use_container_width=True, help="Move down"):
                    move_transform_step_down(step.step_id); st.rerun()
            with c4:
                if st.button("⏸" if step.enabled else "▶", key=f"tog_{step.step_id}", use_container_width=True,
                             help="Toggle on/off"):
                    toggle_transform_step(step.step_id); st.rerun()
            with c5:
                if st.button("✕", key=f"rem_{step.step_id}", use_container_width=True, help="Remove"):
                    remove_transform_step(step.step_id); st.rerun()

    enabled_count = sum(1 for s in all_steps if s.enabled)
    st.caption(f"**{n_steps} step(s) total** — {enabled_count} enabled, {n_steps - enabled_count} paused")
