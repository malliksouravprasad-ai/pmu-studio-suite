"""Page 4 — Generate report outputs and save config."""
import sys
import os

_APP_DIR  = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_PMU_ROOT = os.path.dirname(os.path.dirname(_APP_DIR))
for _p in [_PMU_ROOT, _APP_DIR]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

import streamlit as st
from engine import (
    init_state, reset_state, get_workspace, get_job, set_job, has_data, get_raw_df, has_sections,
    generate_all, save_excel_report, save_word_report, save_ppt_report, save_pdf_report,
    register_outputs, OUTPUT_FORMATS,
)
from shared import (
    generate_id, save_config, credentials_available,
    upload_to_drive,
)

st.set_page_config(page_title="Generate — Deliverable Studio", page_icon="📥", layout="wide")
init_state()

ws  = get_workspace()
job = get_job()
rc  = job.report_config

with st.sidebar:
    st.markdown("## 📄 Deliverable Studio")
    st.caption("APP-005 · OSEPA PMU Tool Suite")
    st.markdown("---")
    if ws:
        st.success(f"📁 **{ws['name']}**")
    else:
        st.warning("No workspace selected")
    st.info(f"**{len(rc.sections)}** section(s) · **{len(rc.selected_formats)}** format(s)")
    if st.button("🗑 Reset Studio", use_container_width=True):
        reset_state(); st.rerun()

st.markdown("# 📥 Generate")
st.caption("Step 4 of 3 — Generate report outputs and save configuration")
st.markdown("---")

if not has_data():
    st.warning("Please upload a file first."); st.stop()

df           = get_raw_df()
project_code = rc.project_code or "PMU"
ws_path      = ws["path"] if ws else None

artifact_id = rc.artifact_id or generate_id(project_code, "RPT")
if not rc.artifact_id:
    rc.artifact_id = artifact_id; set_job(job)

st.markdown("### Report Configuration")
c1, c2, c3, c4 = st.columns(4)
c1.metric("Title",    (rc.report_title[:18] + "…") if len(rc.report_title) > 18 else rc.report_title)
c2.metric("Sections", len(rc.sections))
c3.metric("Formats",  len(rc.selected_formats))
c4.metric("Date",     rc.report_date or "—")

if not rc.sections:
    st.warning("Add at least one section first (Step 3 — Sections)."); st.stop()

st.markdown("---")

# ── Save config ───────────────────────────────────────────────────────────────
if ws:
    with st.expander("💾 Save Configuration to Workspace"):
        config_name = st.text_input("Configuration name", value=f"{project_code} Report Config")
        if st.button("Save Configuration"):
            save_config(ws["path"], "APP-005", config_name, job.to_config())
            st.success(f"Configuration **{config_name}** saved.")

st.markdown("---")
st.markdown("### Generate Outputs")
st.info(f"Selected formats: **{', '.join(OUTPUT_FORMATS[f] for f in rc.selected_formats)}**")

# ── Generate all ──────────────────────────────────────────────────────────────
if st.button("📦 Generate All Outputs", type="primary", use_container_width=True):
    generated = {}
    with st.spinner("Generating outputs…"):
        outputs = generate_all(df, rc, ws_path)
    for fmt, (path, buf) in outputs.items():
        generated[fmt] = (path, buf)
    register_outputs(artifact_id, project_code, {k: v[0] for k, v in generated.items()})
    st.success(f"All outputs generated! Artifact: **{artifact_id}**")

    cols = st.columns(len(generated))
    ext_map = {"excel": ("xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"),
               "word":  ("docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"),
               "ppt":   ("pptx", "application/vnd.openxmlformats-officedocument.presentationml.presentation"),
               "pdf":   ("pdf",  "application/pdf")}
    for col, (fmt, (path, buf)) in zip(cols, generated.items()):
        ext, mime = ext_map.get(fmt, ("bin", "application/octet-stream"))
        col.download_button(f"⬇ {OUTPUT_FORMATS[fmt].split(' ')[0]}", buf,
            file_name=os.path.basename(path), mime=mime,
            use_container_width=True, type="primary")

# ── Individual formats ────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("### Or generate individually")
fmt_funcs = {
    "excel": (save_excel_report, "xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"),
    "word":  (save_word_report,  "docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"),
    "ppt":   (save_ppt_report,   "pptx", "application/vnd.openxmlformats-officedocument.presentationml.presentation"),
    "pdf":   (save_pdf_report,   "pdf",  "application/pdf"),
}
cols = st.columns(len(rc.selected_formats))
for col, fmt in zip(cols, rc.selected_formats):
    fn, ext, mime = fmt_funcs.get(fmt, (None, "bin", "application/octet-stream"))
    if fn and col.button(f"Generate {OUTPUT_FORMATS[fmt].split('(')[0].strip()}", use_container_width=True):
        with st.spinner(f"Building {ext}…"):
            path, buf = fn(df, rc, ws_path)
        col.download_button(f"⬇ {ext}", buf, file_name=os.path.basename(path), mime=mime, use_container_width=True)

# ── Google Drive upload ────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("### Upload to Google Drive")
if not credentials_available():
    st.info("🔒 Google credentials not configured. Place `credentials.json` in `PMU_Tools/credentials/` to enable.")
else:
    drive_fmt = st.selectbox("Select format to upload", rc.selected_formats,
                              format_func=lambda f: OUTPUT_FORMATS[f].split("(")[0].strip(),
                              key="del_drive_fmt")
    if ws_path and st.button("☁ Upload to Google Drive", use_container_width=True):
        with st.spinner("Generating and uploading…"):
            try:
                fn, ext, mime = fmt_funcs.get(drive_fmt, (None, "bin", ""))
                if fn:
                    path, _ = fn(df, rc, ws_path)
                    result  = upload_to_drive(path)
                    st.success("Uploaded to Drive!")
                    st.markdown(f"**Drive URL:** {result['web_url']}")
            except Exception as e:
                st.error(f"Upload failed: {e}")
