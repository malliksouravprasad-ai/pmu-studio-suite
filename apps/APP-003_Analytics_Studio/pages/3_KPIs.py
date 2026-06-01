"""Page 3 — KPI Engine: define KPIs, set targets, compute scores."""
import sys
import os

_APP_DIR  = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_PMU_ROOT = os.path.dirname(os.path.dirname(_APP_DIR))
for _p in [_PMU_ROOT, _APP_DIR]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

import pandas as pd
import streamlit as st
from shared import list_configs, load_config, clone_config
from engine import (
    init_state, reset_state, get_workspace, get_job,
    has_data, get_raw_df,
    add_kpi, remove_kpi, get_kpi_result, set_kpi_result,
    KPIDef, KPI_FORMULAS, KPI_INTERPRETATIONS,
    calculate_kpis,
)

st.set_page_config(page_title="KPIs — Analytics Studio", page_icon="🎯", layout="wide")
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
    enabled_kpis = [k for k in job.kpi_defs if k.enabled]
    st.info(f"**{len(enabled_kpis)}** KPI(s) defined")
    if st.button("🗑 Reset Studio", use_container_width=True):
        reset_state(); st.rerun()

st.markdown("# 🎯 KPIs")
st.caption("Step 3 of 6 — Define KPIs, set targets, and compute weighted scores")
st.markdown("---")

if not has_data():
    st.warning("Please upload a file first (Step 1 — Upload).")
    st.stop()

df   = get_raw_df()
cols = df.columns.tolist()
num_cols = list(df.select_dtypes(include="number").columns)

# ── KPI Quick-start Templates ─────────────────────────────────────────────────
KPI_TEMPLATES = {
    "School Attendance": [
        {"name": "Student Attendance Rate", "formula": "percentage", "num": "students_present", "den": "total_enrolment", "target": 75.0, "weight": 2.0, "interp": "higher_better"},
        {"name": "Teacher Attendance Rate", "formula": "percentage", "num": "teachers_present", "den": "teachers_sanctioned", "target": 90.0, "weight": 2.0, "interp": "higher_better"},
    ],
    "Monitoring Coverage": [
        {"name": "Monitoring Coverage %", "formula": "percentage", "num": "schools_monitored", "den": "total_schools", "target": 80.0, "weight": 2.0, "interp": "higher_better"},
        {"name": "Average Attendance", "formula": "value", "val": "avg_attendance", "target": 75.0, "weight": 1.0, "interp": "higher_better"},
    ],
    "Learning Outcomes": [
        {"name": "Paragraph Reading Rate", "formula": "percentage", "num": "literacy_level3", "den": "students_assessed", "target": 60.0, "weight": 2.0, "interp": "higher_better"},
        {"name": "Basic Numeracy Rate", "formula": "percentage", "num": "numeracy_level2", "den": "students_assessed", "target": 60.0, "weight": 2.0, "interp": "higher_better"},
    ],
}

with st.expander("🚀 Load KPI Template", expanded=False):
    st.caption("Pre-populate KPIs from a standard monitoring template")
    tmpl_sel = st.selectbox("Template", list(KPI_TEMPLATES.keys()))
    if st.button("Load Template KPIs", type="primary"):
        from uuid import uuid4
        for k in KPI_TEMPLATES[tmpl_sel]:
            kpi = KPIDef(
                name=k["name"], formula=k["formula"],
                value_col=k.get("val", ""), numerator_col=k.get("num", ""),
                denominator_col=k.get("den", ""),
                target=k["target"], target_col="",
                weight=k["weight"], interpretation=k["interp"],
            )
            add_kpi(kpi)
        st.success(f"Loaded {len(KPI_TEMPLATES[tmpl_sel])} KPIs from **{tmpl_sel}** template."); st.rerun()

# ── Define KPI ────────────────────────────────────────────────────────────────
with st.expander("➕ Define New KPI", expanded=len(job.kpi_defs) == 0):
    c1, c2 = st.columns(2)
    kpi_name    = c1.text_input("KPI Name", placeholder="e.g. Attendance Rate")
    kpi_formula = c2.selectbox("Formula", list(KPI_FORMULAS.keys()), format_func=lambda k: KPI_FORMULAS[k])

    if kpi_formula == "value":
        value_col = st.selectbox("Value column", ["— choose —"] + num_cols)
        num_col = den_col = ""
    else:
        c_a, c_b = st.columns(2)
        num_col   = c_a.selectbox("Numerator column", ["— choose —"] + num_cols)
        den_col   = c_b.selectbox("Denominator column", ["— choose —"] + num_cols)
        value_col = ""

    # Live formula preview
    _n = kpi_name.strip() or "KPI"
    _vc = value_col if value_col and value_col != "— choose —" else "value_col"
    _nc = num_col if num_col and num_col != "— choose —" else "numerator"
    _dc = den_col if den_col and den_col != "— choose —" else "denominator"
    if kpi_formula == "value":
        st.info(f"**Formula:** {_n} = `{_vc}`")
    elif kpi_formula == "ratio":
        st.info(f"**Formula:** {_n} = `{_nc}` ÷ `{_dc}`")
    else:
        st.info(f"**Formula:** {_n} = (`{_nc}` ÷ `{_dc}`) × 100  →  result in **%**")

    c1, c2, c3 = st.columns(3)
    target_type = c1.radio("Target type", ["Fixed value", "Column"], horizontal=True)
    kpi_weight  = c2.number_input("Weight", min_value=0.01, value=1.0, step=0.1)
    interpretation = c3.selectbox("Interpretation", list(KPI_INTERPRETATIONS.keys()),
                                   format_func=lambda k: KPI_INTERPRETATIONS[k])

    target_val = target_col = None
    if target_type == "Fixed value":
        target_val = st.number_input("Target value", value=100.0)
    else:
        target_col = st.selectbox("Target column", ["— choose —"] + num_cols)
        if target_col == "— choose —":
            target_col = ""

    if st.button("Add KPI", type="primary") and kpi_name.strip():
        kpi = KPIDef(
            name           = kpi_name.strip(),
            formula        = kpi_formula,
            value_col      = value_col if value_col != "— choose —" else "",
            numerator_col  = num_col if num_col != "— choose —" else "",
            denominator_col = den_col if den_col != "— choose —" else "",
            target         = float(target_val) if target_type == "Fixed value" else None,
            target_col     = target_col or "",
            weight         = kpi_weight,
            interpretation = interpretation,
        )
        add_kpi(kpi)
        st.success(f"KPI **{kpi_name}** added."); st.rerun()

# ── KPI list ──────────────────────────────────────────────────────────────────
st.markdown("### Defined KPIs")
if not job.kpi_defs:
    st.info("No KPIs defined yet. Add one above.")
    st.stop()

total_weight = sum(k.weight for k in job.kpi_defs if k.enabled)
for kpi in job.kpi_defs:
    share = round(kpi.weight / total_weight * 100, 1) if total_weight > 0 else 0
    with st.container(border=True):
        c1, c2 = st.columns([5, 1])
        c1.markdown(f"**{kpi.name}** · `{kpi.formula}` · "
                    f"Target: {kpi.target or kpi.target_col or '—'} · "
                    f"Weight: {kpi.weight} ({share}%) · "
                    f"{KPI_INTERPRETATIONS.get(kpi.interpretation, kpi.interpretation)}")
        if c2.button("Remove", key=f"rm_{kpi.kpi_id}", use_container_width=True):
            remove_kpi(kpi.kpi_id); st.rerun()

# ── Calculate ─────────────────────────────────────────────────────────────────
st.markdown("---")
if st.button("▶ Calculate KPIs & Scores", type="primary", use_container_width=True):
    with st.spinner("Calculating KPIs…"):
        kpi_df, kpi_summary = calculate_kpis(df, job.kpi_defs)
    set_kpi_result((kpi_df, kpi_summary))
    st.success(f"Calculated {len(job.kpi_defs)} KPI(s)."); st.rerun()

# ── Results ───────────────────────────────────────────────────────────────────
kpi_result = get_kpi_result()
if kpi_result:
    kpi_df, kpi_summary = kpi_result
    st.markdown("### KPI Results")

    if kpi_summary:
        st.markdown("#### Summary Table")
        st.dataframe(pd.DataFrame(kpi_summary), use_container_width=True, hide_index=True)

    if "Composite Score" in kpi_df.columns:
        st.markdown(f"**Overall mean composite score: {kpi_df['Composite Score'].mean():.2f}**")

    kpi_preview_cols = [c for c in kpi_df.columns if c not in df.columns or c in
                        [k.name for k in job.kpi_defs]]
    with st.expander("Preview KPI dataset (first 20 rows)", expanded=True):
        st.dataframe(kpi_df.head(20), use_container_width=True)
