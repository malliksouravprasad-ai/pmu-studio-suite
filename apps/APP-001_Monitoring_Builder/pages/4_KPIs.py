"""Page 4 — KPI Builder: define indicators and aggregation configs."""
import sys
import os

_APP_DIR  = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_PMU_ROOT = os.path.dirname(os.path.dirname(_APP_DIR))
for _p in [_PMU_ROOT, _APP_DIR]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

import streamlit as st
from uuid import uuid4
from engine import (
    init_state, reset_state, get_workspace, get_job, get_studio_job, set_studio_job,
    add_kpi_def, remove_kpi_def, has_fields, enabled_fields,
)

st.set_page_config(page_title="KPIs — Monitoring Builder", page_icon="🎯", layout="wide")
init_state()

ws  = get_workspace()
job = get_job()

with st.sidebar:
    st.markdown("## 🏗️ Monitoring Builder")
    st.caption("APP-001 · OSEPA PMU Tool Suite")
    st.markdown("---")
    if ws:
        st.success(f"📁 **{ws['name']}**")
    else:
        st.warning("No workspace selected")
    st.info(f"**{len(job.kpi_defs)}** KPI(s) · **{len(job.agg_defs)}** aggregation(s)")
    if st.button("🗑 Reset Builder", use_container_width=True):
        reset_state(); st.rerun()

st.markdown("# 🎯 KPI Builder")
st.caption("Step 4 of 4 — Define key performance indicators and aggregation configs")
st.markdown("---")

if not has_fields():
    st.warning("Define fields first (Step 1 — Schema)."); st.stop()

e_fields    = enabled_fields()
field_names = [f.name for f in e_fields]
num_fields  = [f.name for f in e_fields if f.data_type in ("number", "integer")]

# ── KPI definitions ───────────────────────────────────────────────────────────
tab1, tab2 = st.tabs(["KPI Definitions", "Aggregation Configs"])

with tab1:
    st.markdown("### Add KPI Definition")
    with st.form("kpi_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        kpi_name    = c1.text_input("KPI Name *", placeholder="e.g. Attendance Rate")
        kpi_formula = c2.selectbox("Formula",
            ["value", "ratio", "percentage"],
            format_func=lambda k: {"value": "Direct value", "ratio": "Ratio (A÷B)",
                                    "percentage": "Percentage (A÷B×100)"}[k])

        if kpi_formula == "value":
            value_col = st.selectbox("Value column", ["— choose —"] + num_fields)
            num_col = den_col = ""
        else:
            ca, cb = st.columns(2)
            num_col   = ca.selectbox("Numerator column", ["— choose —"] + num_fields)
            den_col   = cb.selectbox("Denominator column", ["— choose —"] + num_fields)
            value_col = ""

        # Live formula preview
        _vc = value_col if value_col and value_col != "— choose —" else "value_col"
        _nc = num_col if num_col and num_col != "— choose —" else "numerator"
        _dc = den_col if den_col and den_col != "— choose —" else "denominator"
        _name_preview = kpi_name.strip() or "KPI"
        if kpi_formula == "value":
            st.info(f"**Formula preview:** {_name_preview} = `{_vc}`")
        elif kpi_formula == "ratio":
            st.info(f"**Formula preview:** {_name_preview} = `{_nc}` ÷ `{_dc}`")
        else:
            st.info(f"**Formula preview:** {_name_preview} = (`{_nc}` ÷ `{_dc}`) × 100  →  result in **%**")

        c3, c4, c5 = st.columns(3)
        target_type   = c3.radio("Target", ["Fixed value", "Column"], horizontal=True)
        kpi_weight    = c4.number_input("Weight", min_value=0.1, value=1.0, step=0.1)
        interpretation = c5.selectbox("Interpretation",
            ["higher_better", "lower_better"],
            format_func=lambda k: {"higher_better": "Higher = better", "lower_better": "Lower = better"}[k])

        target_val = target_col_name = None
        if target_type == "Fixed value":
            target_val = st.number_input("Target value", value=100.0)
        else:
            target_col_name = st.selectbox("Target column", ["— choose —"] + num_fields)
            if target_col_name == "— choose —":
                target_col_name = ""

        if st.form_submit_button("Add KPI", type="primary") and kpi_name.strip():
            add_kpi_def({
                "kpi_id":         uuid4().hex[:8].upper(),
                "name":           kpi_name.strip(),
                "formula":        kpi_formula,
                "value_col":      value_col if value_col != "— choose —" else "",
                "numerator_col":  num_col if num_col != "— choose —" else "",
                "denominator_col": den_col if den_col != "— choose —" else "",
                "target":         float(target_val) if target_type == "Fixed value" else None,
                "target_col":     target_col_name or "",
                "weight":         kpi_weight,
                "interpretation": interpretation,
                "enabled":        True,
            })
            st.success(f"KPI **{kpi_name.strip()}** added."); st.rerun()

    st.markdown("### Defined KPIs")
    if not job.kpi_defs:
        st.info("No KPIs defined yet.")
    else:
        for k in job.kpi_defs:
            with st.container(border=True):
                c1, c2 = st.columns([5, 1])
                c1.markdown(f"**{k['name']}** · `{k['formula']}` · weight: {k['weight']} · "
                            f"target: {k.get('target') or k.get('target_col') or '—'}")
                if c2.button("Remove", key=f"rm_{k['kpi_id']}", use_container_width=True):
                    remove_kpi_def(k["kpi_id"]); st.rerun()

with tab2:
    st.markdown("### Add Aggregation Config")
    st.caption("Define how data should be grouped and summarized when analysed in APP-003")

    with st.form("agg_form", clear_on_submit=True):
        agg_name   = st.text_input("Aggregation Name *", placeholder="e.g. District Summary")
        group_cols = st.multiselect("Group By columns", field_names)
        metric_cols = st.multiselect("Metric columns (numeric)", num_fields)
        agg_funcs   = {}
        if metric_cols:
            agg_func_row = st.columns(min(4, len(metric_cols)))
            for i, mc in enumerate(metric_cols):
                agg_funcs[mc] = agg_func_row[i % 4].selectbox(mc, ["sum", "avg", "count", "min", "max"],
                                                                key=f"af_{mc}")
        totals = st.checkbox("Include grand total row", value=True)

        if st.form_submit_button("Add Aggregation", type="primary") and agg_name.strip() and group_cols and metric_cols:
            sj = get_studio_job()
            sj.job.agg_defs.append({
                "config_id":      uuid4().hex[:8].upper(),
                "name":           agg_name.strip(),
                "group_cols":     group_cols,
                "metrics":        [{"metric_id": uuid4().hex[:8].upper(), "source_col": mc,
                                    "agg_func": agg_funcs.get(mc, "sum"), "alias": "", "enabled": True}
                                   for mc in metric_cols],
                "include_totals": totals,
                "hierarchical":   False,
                "sort_by":        "",
                "sort_asc":       False,
            })
            set_studio_job(sj)
            st.success(f"Aggregation **{agg_name.strip()}** added."); st.rerun()

    st.markdown("### Defined Aggregations")
    sj = get_studio_job()
    if not sj.job.agg_defs:
        st.info("No aggregation configs defined yet.")
    else:
        for agg in sj.job.agg_defs:
            with st.container(border=True):
                c1, c2 = st.columns([5, 1])
                c1.markdown(f"**{agg['name']}** · Group: {', '.join(agg['group_cols'])} · "
                            f"{len(agg['metrics'])} metric(s)")
                if c2.button("Remove", key=f"rma_{agg['config_id']}", use_container_width=True):
                    sj.job.agg_defs = [a for a in sj.job.agg_defs if a["config_id"] != agg["config_id"]]
                    set_studio_job(sj); st.rerun()

st.markdown("---")
st.info("💡 KPIs and aggregations are exported as a **.pmuconfig** file on the **Package** page, "
        "importable into **APP-003 Analytics Studio**.")
