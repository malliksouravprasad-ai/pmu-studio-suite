"""Page 1 — Define workflow: name, entities, and stages."""
import sys
import os

_APP_DIR  = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_PMU_ROOT = os.path.dirname(os.path.dirname(_APP_DIR))
for _p in [_PMU_ROOT, _APP_DIR]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

import streamlit as st
from shared.theme import page_header, sidebar_brand
from engine import (
    init_state, reset_state, get_workspace, get_job, set_job, get_workflow_job,
    add_stage, remove_stage, move_stage_up, move_stage_down,
    has_stages, has_entities,
    StageDef, ENTITY_TYPES, WorkflowStudioJob,
)
from shared import list_configs, load_config

st.set_page_config(page_title="Define — Workflow Builder", page_icon="📋", layout="wide")
init_state()

ws  = get_workspace()
job = get_job()
wj  = job.workflow_job

with st.sidebar:
    sidebar_brand("Workflow Builder", "APP-006")
    if ws:
        st.success(f"📁 **{ws['name']}**")
    else:
        st.warning("No workspace selected")
    st.info(f"**{len(wj.entities)}** entit. · **{len(wj.stages)}** stage(s)")
    if st.button("🗑 Reset Builder", use_container_width=True):
        reset_state(); st.rerun()

page_header("1 Define", icon="📄")

# ── Workflow Templates ─────────────────────────────────────────────────────────
WORKFLOW_TEMPLATES = {
    "Monthly Data Collection Round": {
        "workflow_name": "Monthly Data Collection Round",
        "entity_type": "School",
        "stages": [
            {"name": "Form Distribution",       "description": "Distribute collection forms to field team",       "due_date": ""},
            {"name": "Data Collection",          "description": "Field team collects data from entities",           "due_date": ""},
            {"name": "Data Submission",          "description": "Submitted data received at headquarters",          "due_date": ""},
            {"name": "Data Validation",          "description": "Data quality check and error correction",          "due_date": ""},
            {"name": "Analysis & Report",        "description": "Analysis completed and report generated",          "due_date": ""},
        ],
    },
    "Quarterly Review Cycle": {
        "workflow_name": "Quarterly Review Cycle",
        "entity_type": "District",
        "stages": [
            {"name": "Data Consolidation",       "description": "District data consolidated",                       "due_date": ""},
            {"name": "Internal Review",          "description": "District team reviews performance",                "due_date": ""},
            {"name": "State Review Meeting",     "description": "State-level review meeting held",                  "due_date": ""},
            {"name": "Action Points Issued",     "description": "Review action points formally communicated",       "due_date": ""},
            {"name": "Compliance Report",        "description": "District submits compliance / action taken report","due_date": ""},
        ],
    },
    "ATR (Action Taken Register)": {
        "workflow_name": "Action Taken Register",
        "entity_type": "District",
        "stages": [
            {"name": "Action Point Received",    "description": "Action point formally received",                   "due_date": ""},
            {"name": "Action Plan Submitted",    "description": "Entity submits remediation plan",                  "due_date": ""},
            {"name": "Action Implemented",       "description": "Remediation action completed",                     "due_date": ""},
            {"name": "Evidence Submitted",       "description": "Evidence of completion submitted",                 "due_date": ""},
            {"name": "Verification Complete",    "description": "PMU verifies and closes the action point",         "due_date": ""},
        ],
    },
    "School Visit Compliance": {
        "workflow_name": "School Visit Compliance Tracker",
        "entity_type": "School",
        "stages": [
            {"name": "Visit Scheduled",          "description": "Visit date assigned in plan",                      "due_date": ""},
            {"name": "Visit Conducted",          "description": "Field visit completed",                            "due_date": ""},
            {"name": "Report Submitted",         "description": "Visit report submitted to PMU",                    "due_date": ""},
            {"name": "Data Entered",             "description": "Data entered into MIS/system",                     "due_date": ""},
        ],
    },
    "Training Programme": {
        "workflow_name": "Training Programme Tracker",
        "entity_type": "Block",
        "stages": [
            {"name": "Nomination Received",      "description": "Training nominations received from block",         "due_date": ""},
            {"name": "Attendance Confirmed",     "description": "Participants confirmed and attendance taken",       "due_date": ""},
            {"name": "Training Completed",       "description": "Training session conducted",                       "due_date": ""},
            {"name": "Assessment Done",          "description": "Post-training assessment completed",               "due_date": ""},
            {"name": "Certificate Issued",       "description": "Completion certificate issued",                    "due_date": ""},
        ],
    },
}

with st.expander("🚀 Start from a Workflow Template", expanded=not has_stages()):
    st.caption("Load a pre-built workflow — stages pre-configured, ready for your entity list")
    tmpl_cols = st.columns(len(WORKFLOW_TEMPLATES))
    for i, (tname, tdata) in enumerate(WORKFLOW_TEMPLATES.items()):
        with tmpl_cols[i]:
            st.markdown(f"**{tname}**")
            st.caption(f"{tdata['entity_type']} · {len(tdata['stages'])} stages")
            if st.button("Load", key=f"wtmpl_{i}", use_container_width=True, type="primary"):
                wj.workflow_name = tdata["workflow_name"]
                wj.entity_type   = tdata["entity_type"]
                wj.stages        = [StageDef(name=s["name"], description=s["description"],
                                             sequence=j+1, due_date=s["due_date"])
                                    for j, s in enumerate(tdata["stages"])]
                set_job(job)
                st.success(f"Template **{tname}** loaded."); st.rerun()

st.markdown("---")

# ── Load saved workflow ───────────────────────────────────────────────────────
if ws:
    saved = list_configs(ws["path"], "APP-006")
    if saved:
        with st.expander("📂 Load a saved workflow definition", expanded=False):
            names  = list({c["name"] for c in saved})
            chosen = st.selectbox("Saved workflows", names)
            if st.button("Load Workflow", type="primary"):
                data = load_config(ws["path"], "APP-006", chosen)
                set_job(WorkflowStudioJob.from_config(data["config"]))
                st.success(f"Loaded: **{chosen}**"); st.rerun()

# ── Workflow metadata ─────────────────────────────────────────────────────────
st.markdown("### Workflow Metadata")
with st.form("meta_form"):
    c1, c2, c3 = st.columns(3)
    wf_name     = c1.text_input("Workflow Name *", value=wj.workflow_name)
    entity_type = c2.selectbox("Entity Type *", ENTITY_TYPES,
                                index=ENTITY_TYPES.index(wj.entity_type) if wj.entity_type in ENTITY_TYPES else 0)
    proj_code   = c3.text_input("Project Code", value=wj.project_code)
    if st.form_submit_button("Update Metadata", type="primary"):
        wj.workflow_name = wf_name.strip()
        wj.entity_type   = entity_type
        wj.project_code  = proj_code.strip().upper() or "PMU"
        set_job(job)
        st.success("Metadata updated.")

st.markdown("---")

# ── Entities ──────────────────────────────────────────────────────────────────
st.markdown(f"### {wj.entity_type} List")
col_a, col_b = st.columns([2, 1])
with col_a:
    entity_input = st.text_area(
        f"Enter {wj.entity_type} names (one per line)",
        value="\n".join(wj.entities),
        height=200,
        help="Type or paste entity names — one per line.",
    )
with col_b:
    st.markdown("**Quick add from CSV/XLSX column**")
    uploaded = st.file_uploader("Upload file", type=["csv", "xlsx"], label_visibility="collapsed")
    if uploaded:
        import pandas as pd
        df = pd.read_csv(uploaded) if uploaded.name.endswith(".csv") else pd.read_excel(uploaded)
        col_sel = st.selectbox("Column to use as entities", df.columns.tolist())
        if st.button("Import Entities"):
            new_entities = df[col_sel].dropna().astype(str).str.strip().unique().tolist()
            wj.entities = sorted(set(wj.entities + new_entities))
            set_job(job); st.success(f"Imported {len(new_entities)} entities."); st.rerun()

if st.button("Save Entity List", type="primary"):
    entities = [e.strip() for e in entity_input.splitlines() if e.strip()]
    wj.entities = entities
    set_job(job)
    st.success(f"**{len(entities)}** entities saved.")
    st.rerun()

if wj.entities:
    st.caption(f"**{len(wj.entities)}** entities: {', '.join(wj.entities[:5])}" +
               (f"… (+{len(wj.entities)-5} more)" if len(wj.entities) > 5 else ""))

st.markdown("---")

# ── Stages ────────────────────────────────────────────────────────────────────
st.markdown("### Workflow Stages")
n_stages = len(wj.stages)
for idx, stage in enumerate(wj.stages):
    with st.container(border=True):
        c1, c2, c3, c4 = st.columns([4, 1, 1, 1])
        c1.markdown(f"**{idx+1}.** {stage.name}" + (f" — due {stage.due_date}" if stage.due_date else ""))
        if stage.description:
            c1.caption(stage.description)
        with c2:
            if idx > 0 and st.button("↑", key=f"up_{stage.stage_id}", use_container_width=True, help="Move up"):
                move_stage_up(stage.stage_id); st.rerun()
        with c3:
            if idx < n_stages - 1 and st.button("↓", key=f"dn_{stage.stage_id}", use_container_width=True, help="Move down"):
                move_stage_down(stage.stage_id); st.rerun()
        with c4:
            if st.button("✕", key=f"rs_{stage.stage_id}", use_container_width=True, help="Remove"):
                remove_stage(stage.stage_id); st.rerun()

st.markdown("#### Add Stage")
with st.form("add_stage_form", clear_on_submit=True):
    c1, c2, c3 = st.columns([2, 1, 1])
    stage_name = c1.text_input("Stage Name *", placeholder="e.g. Data Collection")
    stage_desc = c2.text_input("Description (optional)")
    stage_due  = c3.text_input("Due Date (YYYY-MM-DD)", placeholder="optional")
    if st.form_submit_button("Add Stage", type="primary") and stage_name.strip():
        seq = len(wj.stages) + 1
        add_stage(StageDef(name=stage_name.strip(), sequence=seq,
                           description=stage_desc.strip(), due_date=stage_due.strip()))
        st.success(f"Stage **{stage_name.strip()}** added."); st.rerun()
