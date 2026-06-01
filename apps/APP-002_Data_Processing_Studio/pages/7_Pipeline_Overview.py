"""Page 7 — Pipeline Overview: see the complete processing pipeline in one view and run a sample preview."""
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
    has_data, get_raw_df, get_mapped_df,
    apply_all, run_all_rules, apply_all_mappings,
    get_match_results, set_mapped_df,
)

st.set_page_config(page_title="Pipeline Overview — Data Processing Studio", page_icon="🔀", layout="wide")
init_state()

ws  = get_workspace()
job = get_job()

with st.sidebar:
    sidebar_brand("Data Processing Studio", "APP-002")
    if ws:
        st.success(f"📁 **{ws['name']}**")
    else:
        st.warning("No workspace selected")
    if st.button("🗑 Reset Studio", use_container_width=True):
        reset_state(); st.rerun()

page_header("Pipeline Overview", subtitle="End-to-end view of the processing pipeline", icon="🔭", step=7, total_steps=7)

df = get_raw_df()
steps = [s for s in job.transform_job.steps if s.enabled]
maps  = job.mapping_job.column_mappings
rules = [r for r in job.rule_job.rules if r.enabled]

# ── Visual pipeline flow ──────────────────────────────────────────────────────
st.markdown("### Pipeline Flow")

STAGES = [
    ("📥 Input",      job.source_filename or "No file loaded",   bool(df is not None)),
    ("🧹 Clean",      "Missing values · Duplicates · Standardize","always_done"),
    ("🔧 Transform",  f"{len(steps)} step(s) configured",         len(steps) > 0),
    ("🗺 Map",        f"{len(maps)} mapping(s) configured",       len(maps) > 0),
    ("✅ Validate",   f"{len(rules)} rule(s) configured",          len(rules) > 0),
    ("📥 Output",     "Clean dataset · Log · Report",             df is not None),
]

cols = st.columns(len(STAGES))
for col, (icon_label, detail, active) in zip(cols, STAGES):
    if active == "always_done":
        bg   = "#e8f4fd"
        icon = "🔵"
    elif active:
        bg   = "#e8f5e9"
        icon = "🟢"
    else:
        bg   = "#f5f5f5"
        icon = "⚪"
    with col:
        st.markdown(f"""
<div style="background:{bg};padding:12px;border-radius:8px;text-align:center;border:1px solid #ddd;">
<b>{icon} {icon_label.split(' ', 1)[1] if ' ' in icon_label else icon_label}</b><br>
<small>{detail}</small>
</div>""", unsafe_allow_html=True)

st.markdown("---")

# ── Stage details ─────────────────────────────────────────────────────────────
col_l, col_r = st.columns(2)

with col_l:
    # Transform steps
    st.markdown("### 🔧 Transform Steps")
    if not job.transform_job.steps:
        st.info("No transform steps configured. Add steps on the Transform page.")
    else:
        for i, s in enumerate(job.transform_job.steps):
            icon = "✅" if s.enabled else "⏸"
            st.markdown(f"**{i+1}.** {icon} `{s.op_type.replace('_', ' ').title()}` — {s.description}")

    st.markdown("### 🗺 Mapping Columns")
    if not maps:
        st.info("No mapping columns configured. Add mappings on the Map page.")
    else:
        for m in maps:
            st.markdown(f"- **{m.source_col}** → `{m.mapping_type}` (fuzzy ≥ {m.fuzzy_threshold})")

with col_r:
    # Validation rules
    st.markdown("### ✅ Validation Rules")
    if not [r for r in job.rule_job.rules if r.enabled]:
        st.info("No validation rules configured. Add rules on the Validate page.")
    else:
        for r in job.rule_job.rules:
            if r.enabled:
                badge = {"error": "🔴", "warning": "🟡", "info": "🔵"}.get(r.severity, "⚪")
                st.markdown(f"{badge} **{r.name}** · `{r.rule_type}`")

    # Calculation rules
    calc_rules = [r for r in job.rule_job.rules if r.rule_type in ("arithmetic", "conditional", "percentage", "score")]
    if calc_rules:
        st.markdown("### 🔢 Calculation Rules")
        for r in calc_rules:
            st.markdown(f"🔵 **{r.name}** · `{r.rule_type}`")

st.markdown("---")

# ── Sample Preview ────────────────────────────────────────────────────────────
st.markdown("### Sample Preview")
st.caption("Run the full pipeline on the first 20 rows to see the output before downloading")

if df is None:
    st.warning("Upload a file first (Step 1 — Upload) to enable sample preview.")
else:
    sample_n = st.slider("Sample size (rows)", min_value=5, max_value=100, value=20, step=5)

    if st.button("▶ Run Sample Preview", type="primary", use_container_width=True):
        sample_df = df.head(sample_n).copy()

        with st.spinner("Applying transforms to sample…"):
            if steps:
                sample_df, tr_log = apply_all(sample_df, job.transform_job.steps)
            else:
                tr_log = []

        if maps:
            with st.spinner("Applying mappings to sample…"):
                match_results = get_match_results()
                from engine import run_matching
                sample_match = {}
                for cm in maps:
                    if cm.source_col in sample_df.columns:
                        sample_match[cm.mapping_id] = run_matching(sample_df[cm.source_col], cm)
                sample_df = apply_all_mappings(sample_df, maps, sample_match)

        if rules:
            with st.spinner("Running validation rules on sample…"):
                sample_df, sample_results, sample_exc, _ = run_all_rules(sample_df, rules)

        st.success(f"Sample complete — **{len(sample_df)} rows × {len(sample_df.columns)} columns**")

        # Show shape delta
        orig_sample = df.head(sample_n)
        dm1, dm2, dm3, dm4 = st.columns(4)
        dm1.metric("Input Rows",   len(orig_sample))
        dm2.metric("Output Rows",  len(sample_df), delta=len(sample_df) - len(orig_sample))
        dm3.metric("Input Cols",   len(orig_sample.columns))
        dm4.metric("Output Cols",  len(sample_df.columns), delta=len(sample_df.columns) - len(orig_sample.columns))

        if rules:
            total_flags = sum(getattr(rr, "failed", 0) for rr in sample_results)
            st.metric("Validation Flags (sample)", total_flags)

        with st.expander("Sample output (first rows)", expanded=True):
            st.dataframe(sample_df, use_container_width=True)

        if tr_log:
            with st.expander("Transform log"):
                for entry in tr_log:
                    st.caption(f"- {entry.get('description', '')}")

    st.info("If the sample preview looks correct, go to **Generate** (Step 6) to run on the full dataset and download outputs.")
