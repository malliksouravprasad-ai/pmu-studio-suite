"""Page 3 — Generate tracker outputs and save workflow config."""
import sys
import os

_APP_DIR  = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_PMU_ROOT = os.path.dirname(os.path.dirname(_APP_DIR))
for _p in [_PMU_ROOT, _APP_DIR]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

import streamlit as st
from engine import (
    init_state, reset_state, get_workspace, get_job, set_job, get_workflow_job,
    has_stages, has_entities,
    save_tracker, save_workflow_definition, register_outputs,
    workflow_summary,
)
from shared import (
    generate_id, save_config, clone_config, list_configs,
    credentials_available, clear_and_write, create_spreadsheet, upload_to_drive,
    render_integration_sidebar, render_appscript_section,
)

st.set_page_config(page_title="Generate — Workflow Builder", page_icon="📥", layout="wide")
init_state()

ws  = get_workspace()
job = get_job()
wj  = get_workflow_job()

with st.sidebar:
    st.markdown("## 🔄 Workflow Builder")
    st.caption("APP-006 · OSEPA PMU Tool Suite")
    st.markdown("---")
    if ws:
        st.success(f"📁 **{ws['name']}**")
    else:
        st.warning("No workspace selected")
    summary = workflow_summary(wj) if has_stages() and has_entities() else {"completed_pct": 0}
    st.info(f"**{summary['completed_pct']:.0f}%** complete")
    if st.button("🗑 Reset Builder", use_container_width=True):
        reset_state(); st.rerun()
    render_integration_sidebar()

st.markdown("# 📥 Generate")
st.caption("Step 3 of 2 — Download tracker outputs and save workflow definition")
st.markdown("---")

if not has_entities() or not has_stages():
    st.warning("Please define entities and stages first (Step 1 — Define)."); st.stop()

project_code = wj.project_code or "PMU"
ws_path      = ws["path"] if ws else None

artifact_id = wj.artifact_id or generate_id(project_code, "WFL")
if not wj.artifact_id:
    wj.artifact_id = artifact_id; set_job(job)

# ── Summary ───────────────────────────────────────────────────────────────────
st.markdown("### Workflow Summary")
c1, c2, c3, c4 = st.columns(4)
c1.metric("Workflow",    wj.workflow_name[:18])
c2.metric("Entities",   len(wj.entities))
c3.metric("Stages",     len(wj.stages))
c4.metric("Completed",  f"{workflow_summary(wj)['completed_pct']:.0f}%")

st.markdown("---")

# ── Save / Clone config ───────────────────────────────────────────────────────
if ws:
    st.markdown("### Save Workflow Definition")
    config_name = st.text_input("Configuration name", value=wj.workflow_name)
    wf_c1, wf_c2 = st.columns(2)
    if wf_c1.button("💾 Save to Workspace", use_container_width=True):
        save_config(ws["path"], "APP-006", config_name, job.to_config())
        st.success(f"Workflow **{config_name}** saved.")
    saved = list_configs(ws["path"], "APP-006")
    if saved:
        clone_from = st.selectbox("Clone from", list({c["name"] for c in saved}),
                                   key="wf_clone_from", label_visibility="collapsed")
        if wf_c2.button("📋 Clone Workflow", use_container_width=True):
            clone_config(ws["path"], "APP-006", clone_from, f"{clone_from} (Copy)")
            st.success(f"Cloned **{clone_from}**.")

st.markdown("---")

# ── Generate outputs ──────────────────────────────────────────────────────────
st.markdown("### Download Outputs")
d1, d2 = st.columns(2)

with d1:
    if st.button("📊 Generate tracker.xlsx", type="primary", use_container_width=True):
        with st.spinner("Building tracker…"):
            path, buf = save_tracker(wj, ws_path)
        st.download_button("⬇ tracker.xlsx", buf,
            file_name=os.path.basename(path),
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True, type="primary")

with d2:
    if st.button("📋 Generate workflow_definition.xlsx", use_container_width=True):
        with st.spinner("Building definition…"):
            path, buf = save_workflow_definition(wj, ws_path)
        st.download_button("⬇ workflow_definition.xlsx", buf,
            file_name=os.path.basename(path),
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True)

st.markdown("---")
if st.button("📦 Generate All Outputs", use_container_width=True):
    with st.spinner("Generating all outputs…"):
        t_path, t_buf = save_tracker(wj, ws_path)
        d_path, d_buf = save_workflow_definition(wj, ws_path)
        register_outputs(artifact_id, project_code, t_path, d_path)
    st.success(f"All outputs generated! Artifact: **{artifact_id}**")
    b1, b2 = st.columns(2)
    b1.download_button("⬇ tracker.xlsx", t_buf, file_name=os.path.basename(t_path),
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True, type="primary")
    b2.download_button("⬇ workflow_definition.xlsx", d_buf, file_name=os.path.basename(d_path),
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True)

# ── Google Sheets + Drive ─────────────────────────────────────────────────────
st.markdown("---")
st.markdown("### Push to Google Sheets / Drive")
if not credentials_available():
    st.info("🔒 Google credentials not configured.")
else:
    gs1, gs2 = st.columns(2)
    with gs1:
        sheet_url_wf = st.text_input("Sheet URL (blank = create new)", key="wf_sheet_out")
        if st.button("📊 Write Tracker to Google Sheet", use_container_width=True):
            with st.spinner("Writing…"):
                try:
                    import pandas as pd
                    from engine import get_tracking_matrix
                    matrix_df = get_tracking_matrix(wj)
                    if sheet_url_wf.strip():
                        clear_and_write(sheet_url_wf.strip(), "Tracker", matrix_df)
                        st.success("Written to sheet.")
                    else:
                        meta = create_spreadsheet(f"{artifact_id} — Tracker")
                        clear_and_write(meta["sheet_id"], "Tracker", matrix_df)
                        st.success("New sheet created!"); st.code(meta["sheet_url"])
                except Exception as e:
                    st.error(f"Error: {e}")
    with gs2:
        if ws_path and st.button("☁ Upload tracker to Drive", use_container_width=True):
            with st.spinner("Uploading…"):
                try:
                    t_path, _ = save_tracker(wj, ws_path)
                    result    = upload_to_drive(t_path)
                    st.success("Uploaded!"); st.markdown(f"**Drive URL:** {result['web_url']}")
                except Exception as e:
                    st.error(f"Upload failed: {e}")

# ── Apps Script ───────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("### Apps Script Aggregator")
render_appscript_section()
