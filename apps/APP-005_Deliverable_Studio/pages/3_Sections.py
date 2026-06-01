"""Page 3 — Define report sections."""
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
    init_state, reset_state, get_workspace, get_job, set_job, has_data, get_raw_df,
    SectionDef, SECTION_TYPES, AGG_FUNCS,
    add_section, remove_section, move_section_up, move_section_down,
    compute_section_data,
)

st.set_page_config(page_title="Sections — Deliverable Studio", page_icon="📑", layout="wide")
init_state()

ws  = get_workspace()
job = get_job()
rc  = job.report_config

with st.sidebar:
    sidebar_brand("Deliverable Studio", "APP-005")
    if ws:
        st.success(f"📁 **{ws['name']}**")
    else:
        st.warning("No workspace selected")
    st.info(f"**{len(rc.sections)}** section(s)")
    if st.button("🗑 Reset Studio", use_container_width=True):
        reset_state(); st.rerun()

page_header("Sections", subtitle="Build and arrange report sections", icon="📑", step=3, total_steps=4)

if not has_data():
    st.warning("Please upload a file first."); st.stop()

df = get_raw_df()
all_cols     = list(df.columns)
numeric_cols = list(df.select_dtypes(include="number").columns)


# ── Auto-narrative helper ─────────────────────────────────────────────────────
def _auto_narrative(df: pd.DataFrame, group_col: str, metric_col: str,
                     title: str, target: float = None) -> str:
    """Generate a plain-English observation narrative from data."""
    if group_col not in df.columns or metric_col not in df.columns:
        return ""
    grp = df.groupby(group_col)[metric_col].mean().sort_values(ascending=False)
    if grp.empty:
        return ""
    best  = grp.index[0];  best_val  = grp.iloc[0]
    worst = grp.index[-1]; worst_val = grp.iloc[-1]
    avg   = grp.mean()
    lines = [
        f"Analysis of **{metric_col}** across **{group_col}** shows an average of {avg:.1f}.",
        f"**{best}** recorded the highest value ({best_val:.1f}), while "
        f"**{worst}** recorded the lowest ({worst_val:.1f}).",
    ]
    if target:
        above = (grp >= target).sum()
        lines.append(f"{above} out of {len(grp)} {group_col}(s) met the target of {target:.1f}.")
    lines.append(f"Further review is recommended for {group_col}(s) below the average.")
    return "\n\n".join(lines)


# ── Existing sections ─────────────────────────────────────────────────────────
if rc.sections:
    st.markdown("### Report Sections (in order)")
    n_sects = len(rc.sections)
    for idx, sdef in enumerate(rc.sections):
        with st.expander(f"**{idx+1}. {sdef.title}** · {SECTION_TYPES.get(sdef.section_type, '')}", expanded=False):
            c1, c2, c3, c4, c5 = st.columns([3, 1, 1, 1, 1])
            if sdef.section_type == "narrative":
                c1.write(sdef.narrative[:120] + "…" if len(sdef.narrative) > 120 else sdef.narrative or "(empty)")
            elif sdef.section_type == "recommendations":
                c1.markdown("_Recommendations section_")
            else:
                c1.markdown(f"Group: **{', '.join(sdef.group_cols)}** · Metrics: **{', '.join(sdef.metric_cols)}**")
            with c2:
                if idx > 0 and st.button("↑", key=f"up_{sdef.section_id}", use_container_width=True, help="Move up"):
                    move_section_up(sdef.section_id); st.rerun()
            with c3:
                if idx < n_sects - 1 and st.button("↓", key=f"dn_{sdef.section_id}", use_container_width=True, help="Move down"):
                    move_section_down(sdef.section_id); st.rerun()
            with c4:
                if sdef.section_type not in ("narrative", "recommendations") and \
                   st.button("Preview", key=f"pv_{sdef.section_id}", use_container_width=True):
                    sd = compute_section_data(df, rc)
                    preview_df = sd.get(sdef.section_id, pd.DataFrame())
                    if not preview_df.empty:
                        st.dataframe(preview_df, use_container_width=True, hide_index=True)
                    else:
                        st.warning("No data.")
            with c5:
                if st.button("✕", key=f"rm_{sdef.section_id}", use_container_width=True, help="Remove"):
                    remove_section(sdef.section_id); st.rerun()
    st.markdown("---")

# ── Add new section ───────────────────────────────────────────────────────────
st.markdown("### Add New Section")

ALL_SECTION_TYPES = {
    **SECTION_TYPES,
    "recommendations": "Recommendations — structured action recommendations",
}

with st.form("section_form", clear_on_submit=True):
    c1, c2 = st.columns(2)
    title    = c1.text_input("Section Title *")
    sec_type = c2.selectbox("Section Type", list(ALL_SECTION_TYPES.keys()),
                             format_func=lambda k: ALL_SECTION_TYPES[k])

    if sec_type == "narrative":
        # Auto-narrative option
        st.markdown("**Narrative Text**")
        auto_group  = st.selectbox("Auto-generate from (Group column)", ["— manual entry —"] + all_cols,
                                    key="auto_grp")
        auto_metric = st.selectbox("Metric column", ["— choose —"] + numeric_cols, key="auto_met")
        auto_target = st.number_input("Target value (optional, 0 = ignore)", min_value=0.0, value=0.0,
                                       key="auto_tgt")
        if auto_group != "— manual entry —" and auto_metric != "— choose —":
            if st.form_submit_button("🤖 Auto-generate Narrative", type="secondary"):
                pass  # handled below at submit
            st.caption("Or enter narrative text manually:")
        narrative = st.text_area("Narrative Text", height=150)
        group_cols  = []; metric_cols = []; agg_funcs = {}
        sort_col    = ""; sort_asc = False; top_n = 0; include_totals = False
        recs = []

    elif sec_type == "recommendations":
        narrative   = ""
        group_cols  = []; metric_cols = []; agg_funcs = {}
        sort_col    = ""; sort_asc = False; top_n = 0; include_totals = False
        st.markdown("**Enter recommendations (one per line)**")
        recs_raw  = st.text_area("Recommendations", height=150,
                                  placeholder="1. Increase teacher deployment in low-performing blocks\n2. …")
        recs = [r.strip() for r in recs_raw.splitlines() if r.strip()]
        auto_group = auto_metric = "— manual entry —"; auto_target = 0.0

    else:
        narrative   = st.text_area("Optional observation (shown above the table)", height=60)
        ca, cb = st.columns(2)
        group_cols  = ca.multiselect("Group By Columns *", all_cols)
        metric_cols = cb.multiselect("Metric Columns *", numeric_cols)
        agg_funcs   = {}
        if metric_cols:
            st.markdown("**Aggregation per metric:**")
            agg_cols = st.columns(min(4, len(metric_cols)))
            for i, mc in enumerate(metric_cols):
                agg_funcs[mc] = agg_cols[i % 4].selectbox(mc, list(AGG_FUNCS.keys()),
                                                            format_func=lambda k: k.upper(), key=f"af_{mc}")
        c5, c6, c7 = st.columns(3)
        sort_col       = c5.selectbox("Sort by", ["(default)"] + numeric_cols)
        sort_asc       = c5.checkbox("Ascending", value=False)
        top_n          = c6.number_input("Top N (0 = all)", min_value=0, value=0, step=5)
        include_totals = c7.checkbox("Include TOTAL row", value=(sec_type == "table"))
        auto_group = auto_metric = "— manual entry —"; auto_target = 0.0; recs = []

    if st.form_submit_button("Add Section", type="primary"):
        err = None
        if not title.strip():
            err = "Title required."
        elif sec_type == "narrative":
            # Auto-generate if columns selected and narrative empty
            if not narrative.strip() and auto_group != "— manual entry —" and auto_metric != "— choose —":
                narrative = _auto_narrative(df, auto_group, auto_metric, title,
                                             target=auto_target if auto_target > 0 else None)
            if not narrative.strip():
                err = "Narrative text required (or select columns for auto-generation)."
        elif sec_type == "recommendations":
            if not recs:
                err = "Add at least one recommendation."
        elif sec_type != "recommendations" and sec_type != "narrative" and (not group_cols or not metric_cols):
            err = "Group and metric columns required."

        if err:
            st.error(err)
        else:
            # Store recommendations as narrative (formatted as a list)
            if sec_type == "recommendations":
                narrative = "\n".join(f"• {r}" for r in recs)
                sec_type_store = "narrative"
            else:
                sec_type_store = sec_type
            add_section(SectionDef(
                title=title.strip(), section_type=sec_type_store, narrative=narrative.strip(),
                group_cols=group_cols, metric_cols=metric_cols, agg_funcs=agg_funcs,
                sort_col=sort_col if sort_col != "(default)" else "",
                sort_asc=sort_asc, top_n=int(top_n), include_totals=include_totals,
            ))
            st.success(f"Section **{title.strip()}** added."); st.rerun()
