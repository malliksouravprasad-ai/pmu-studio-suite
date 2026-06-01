"""Page 4 — Lookup and fuzzy mapping against master lists."""
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
    add_column_mapping, remove_column_mapping,
    get_match_results, set_match_results, set_mapped_df,
    ColumnMapping, MAPPING_TYPES,
    run_matching, summarize_matches, apply_all_mappings,
    get_master_list,
)

st.set_page_config(page_title="Map — Data Processing Studio", page_icon="🗺️", layout="wide")
init_state()

ws  = get_workspace()
job = get_job()

with st.sidebar:
    sidebar_brand("Data Processing Studio", "APP-002")
    if ws:
        st.success(f"📁 **{ws['name']}**")
    else:
        st.warning("No workspace selected")
    st.info(f"**{len(job.mapping_job.column_mappings)}** mapping(s) configured")
    if st.button("🗑 Reset Studio", use_container_width=True):
        reset_state(); st.rerun()

page_header("Map", subtitle="Map lookup values and resolve mismatches", icon="🗺️", step=4, total_steps=6)

if not has_data():
    st.warning("Please upload a file first (Step 1 — Upload).")
    st.stop()

df   = get_raw_df()
cols = df.columns.tolist()

BUILT_IN_TYPES = ["district", "block", "yesno"]

# ── Add new mapping ───────────────────────────────────────────────────────────
with st.expander("➕ Add Column Mapping", expanded=len(job.mapping_job.column_mappings) == 0):
    c1, c2 = st.columns(2)
    with c1:
        src_col     = st.selectbox("Column to map", ["— choose —"] + cols)
        map_type    = st.selectbox("Master list type", BUILT_IN_TYPES + ["custom"])
        new_col     = st.checkbox("Create new column ({col}_Mapped)", value=True)
    with c2:
        fuzzy_thr = st.slider("Fuzzy match threshold", 0.5, 1.0, 0.72, 0.01)
        if map_type == "custom":
            custom_input = st.text_area("Custom master list (one value per line)", height=150)
        else:
            custom_input = ""

    if st.button("Add Mapping", type="primary") and src_col != "— choose —":
        if map_type == "custom":
            master_list = [v.strip() for v in custom_input.splitlines() if v.strip()]
            variant_map = {}
        else:
            master_list, variant_map = get_master_list(map_type)

        cm = ColumnMapping(
            source_col     = src_col,
            mapping_type   = map_type,
            master_list    = master_list,
            variant_map    = variant_map,
            fuzzy_threshold = fuzzy_thr,
            create_new_col = new_col,
        )
        add_column_mapping(cm)
        st.success(f"Mapping added for **{src_col}**.")
        st.rerun()

# ── Configured mappings ───────────────────────────────────────────────────────
st.markdown("### Configured Mappings")
col_maps = job.mapping_job.column_mappings
if not col_maps:
    st.info("No mappings configured yet. Add one above.")
    st.stop()

for cm in col_maps:
    with st.container(border=True):
        ch, cb = st.columns([4, 1])
        ch.markdown(f"**{cm.source_col}** → `{cm.mapping_type}` master list · "
                    f"{len(cm.master_list)} canonical values · fuzzy ≥ {cm.fuzzy_threshold}")
        if cb.button("Remove", key=f"rm_{cm.mapping_id}", use_container_width=True):
            remove_column_mapping(cm.mapping_id); st.rerun()

st.markdown("---")

# ── Run matching ──────────────────────────────────────────────────────────────
if st.button("▶ Run Matching on All Columns", type="primary", use_container_width=True):
    all_results = get_match_results()
    with st.spinner("Running matching…"):
        for cm in col_maps:
            if cm.source_col in df.columns:
                results = run_matching(df[cm.source_col], cm)
                all_results[cm.mapping_id] = results
    set_match_results(all_results)
    st.success("Matching complete. Review results below.")
    st.rerun()

# ── Results review ────────────────────────────────────────────────────────────
all_results = get_match_results()
if not all_results:
    st.stop()

for cm in col_maps:
    results = all_results.get(cm.mapping_id, {})
    if not results:
        continue

    summary = summarize_matches(results)
    st.markdown(f"#### {cm.source_col}")
    s1, s2, s3, s4, s5 = st.columns(5)
    s1.metric("Exact",     summary.get("exact", 0))
    s2.metric("Variant",   summary.get("variant", 0))
    s3.metric("Fuzzy",     summary.get("pending", 0))
    s4.metric("Unmatched", summary.get("unmatched", 0))
    s5.metric("Blank",     summary.get("blank", 0))

    # Fuzzy review table
    fuzzy_items = [(v, r) for v, r in results.items() if r.status == "pending"]
    if fuzzy_items:
        with st.expander(f"Review {len(fuzzy_items)} fuzzy match(es) for {cm.source_col}"):
            for val, mr in fuzzy_items:
                row_cols = st.columns([2, 2, 1, 1])
                row_cols[0].markdown(f"**{val}**")
                chosen = row_cols[1].selectbox(
                    "Canonical value",
                    [mr.canonical_value] + [s for s in mr.suggestions if s != mr.canonical_value],
                    key=f"sel_{cm.mapping_id}_{val}",
                )
                if row_cols[2].button("Approve", key=f"app_{cm.mapping_id}_{val}"):
                    results[val].status = "approved"
                    results[val].canonical_value = chosen
                    set_match_results({**all_results, cm.mapping_id: results})
                    st.rerun()
                if row_cols[3].button("Reject", key=f"rej_{cm.mapping_id}_{val}"):
                    results[val].status = "rejected"
                    set_match_results({**all_results, cm.mapping_id: results})
                    st.rerun()

# ── Apply mapping ─────────────────────────────────────────────────────────────
st.markdown("---")
if st.button("✅ Apply All Mappings to Dataset", type="primary", use_container_width=True):
    with st.spinner("Applying mappings…"):
        mapped_df = apply_all_mappings(df, col_maps, all_results)
    set_mapped_df(mapped_df)
    st.success(f"Mappings applied. Dataset now has **{len(mapped_df.columns)}** columns.")
    with st.expander("Preview mapped dataset (first 10 rows)"):
        st.dataframe(mapped_df.head(10), use_container_width=True)
