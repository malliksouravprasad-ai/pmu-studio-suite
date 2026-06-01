"""Page 5 — Package Builder: generate all outputs and create Google Form."""
import sys
import os

_APP_DIR  = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_PMU_ROOT = os.path.dirname(os.path.dirname(_APP_DIR))
for _p in [_PMU_ROOT, _APP_DIR]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

import io
import streamlit as st
from engine import (
    init_state, reset_state, get_workspace, get_job, get_studio_job, set_studio_job,
    has_fields, has_sections,
    build_excel_template, build_validation_config, build_kpi_config, build_form_structure,
    create_google_form, save_bytes, register_outputs,
)
from shared import (
    generate_id, save_config, clone_config, list_configs,
    credentials_available, export_package, register_template,
    create_spreadsheet, clear_and_write, share_file,
    save_column_metadata, metadata_from_monitoring_job,
)

st.set_page_config(page_title="Package — Monitoring Builder", page_icon="📦", layout="wide")
init_state()

ws  = get_workspace()
job = get_job()
sj  = get_studio_job()

with st.sidebar:
    st.markdown("## 🏗️ Monitoring Builder")
    st.caption("APP-001 · OSEPA PMU Tool Suite")
    st.markdown("---")
    if ws:
        st.success(f"📁 **{ws['name']}**")
    else:
        st.warning("No workspace selected")
    st.info(f"**{len(job.fields)}** fields · **{len(job.rule_defs)}** rules · **{len(job.kpi_defs)}** KPIs")
    if st.button("🗑 Reset Builder", use_container_width=True):
        reset_state(); st.rerun()

st.markdown("# 📦 Package Builder")
st.caption("Generate monitoring framework outputs — Excel template, validation rules, KPI configs, Google Form")
st.markdown("---")

if not has_fields():
    st.warning("Define fields first (Step 1 — Schema)."); st.stop()

project_code = job.project_code or "PMU"
ws_path      = ws["path"] if ws else None

artifact_id = generate_id(project_code, "MON")

# ── Summary ───────────────────────────────────────────────────────────────────
st.markdown("### Monitoring Framework Summary")
c1, c2, c3, c4 = st.columns(4)
c1.metric("Fields",            len([f for f in job.fields if f.enabled]))
c2.metric("Form Sections",     len(job.form_def.sections))
c3.metric("Validation Rules",  len(job.rule_defs))
c4.metric("KPI Definitions",   len(job.kpi_defs))

st.markdown(f"**Framework:** {job.monitoring_name}  |  **Entity:** {job.entity_type}  |  **Project:** {project_code}")

# ── Save / Clone / Template ───────────────────────────────────────────────────
if ws:
    with st.expander("💾 Save / Clone Framework Configuration"):
        config_name = st.text_input("Configuration name", value=job.monitoring_name)
        sc1, sc2, sc3 = st.columns(3)

        if sc1.button("💾 Save to Workspace", use_container_width=True):
            sj.workspace_slug = ws["slug"]
            set_studio_job(sj)
            save_config(ws["path"], "APP-001", config_name, sj.to_config())
            st.success(f"Framework **{config_name}** saved to workspace.")

        saved = list_configs(ws["path"], "APP-001")
        if saved:
            clone_names = list({c["name"] for c in saved})
            clone_from  = st.selectbox("Clone from saved framework", clone_names, key="clone_from")
            if sc2.button("📋 Clone Framework", use_container_width=True):
                new_name = f"{clone_from} (Copy)"
                clone_config(ws["path"], "APP-001", clone_from, new_name)
                st.success(f"Cloned to **{new_name}**.")

        if sc3.button("📌 Save as Reusable Template", use_container_width=True):
            try:
                import json, tempfile
                config_bytes = json.dumps(sj.to_config(), indent=2).encode()
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pmuconfig") as tmp:
                    tmp.write(config_bytes)
                    tmp_path = tmp.name
                register_template("APP-001", config_name, tmp_path)
                st.success(f"Template **{config_name}** registered in template library.")
            except Exception as e:
                st.error(f"Could not register template: {e}")

st.markdown("---")
st.markdown("### Generate Outputs")

out1, out2, out3, out4 = st.columns(4)

# ── Excel Data Template ───────────────────────────────────────────────────────
with out1:
    st.markdown("#### 📊 Excel Template")
    st.caption("Empty data collection workbook with headers, dropdowns, and data dictionary")
    if st.button("Generate", key="gen_tmpl", use_container_width=True, type="primary"):
        with st.spinner("Building Excel template…"):
            buf = build_excel_template(job)
        fname = f"{artifact_id}_data_template.xlsx"
        if ws_path:
            path, buf = save_bytes(buf.getvalue(), fname, ws_path)
            register_outputs(artifact_id, project_code, template_path=path)
        st.download_button("⬇ data_template.xlsx", buf,
            file_name=fname,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True)

# ── Validation Config ─────────────────────────────────────────────────────────
with out2:
    st.markdown("#### ✅ Validation Config")
    st.caption("Import into APP-002 Data Processing Studio to auto-validate collected data")
    if st.button("Generate", key="gen_val", use_container_width=True, type="primary"):
        with st.spinner("Building validation config…"):
            val_bytes = build_validation_config(job)
        fname = f"{artifact_id}_validation_rules.pmuconfig"
        if ws_path:
            path, _ = save_bytes(val_bytes, fname, ws_path)
            register_outputs(artifact_id, project_code, validation_path=path)
        st.download_button("⬇ validation_rules.pmuconfig", io.BytesIO(val_bytes),
            file_name=fname, mime="application/json", use_container_width=True)

# ── KPI Config ────────────────────────────────────────────────────────────────
with out3:
    st.markdown("#### 🎯 KPI Config")
    st.caption("Import into APP-003 Analytics Studio to calculate KPIs automatically")
    if st.button("Generate", key="gen_kpi", use_container_width=True, type="primary"):
        with st.spinner("Building KPI config…"):
            kpi_bytes = build_kpi_config(job)
        fname = f"{artifact_id}_kpi_definitions.pmuconfig"
        if ws_path:
            path, _ = save_bytes(kpi_bytes, fname, ws_path)
            register_outputs(artifact_id, project_code, kpi_path=path)
        st.download_button("⬇ kpi_definitions.pmuconfig", io.BytesIO(kpi_bytes),
            file_name=fname, mime="application/json", use_container_width=True)

# ── Form Structure JSON ───────────────────────────────────────────────────────
with out4:
    st.markdown("#### 📄 Form Structure")
    st.caption("JSON describing the complete form — used to create Google Form")
    if st.button("Generate", key="gen_form", use_container_width=True, type="primary"):
        with st.spinner("Building form structure…"):
            form_bytes = build_form_structure(job)
        fname = f"{artifact_id}_form_structure.json"
        if ws_path:
            path, _ = save_bytes(form_bytes, fname, ws_path)
            register_outputs(artifact_id, project_code, form_path=path)
        st.download_button("⬇ form_structure.json", io.BytesIO(form_bytes),
            file_name=fname, mime="application/json", use_container_width=True)

# ── Generate All ──────────────────────────────────────────────────────────────
st.markdown("---")
if st.button("📦 Generate All Outputs", use_container_width=True):
    with st.spinner("Generating all outputs…"):
        tmpl_buf  = build_excel_template(job)
        val_bytes = build_validation_config(job)
        kpi_bytes = build_kpi_config(job)
        frm_bytes = build_form_structure(job)

    tmpl_path = val_path = kpi_path = frm_path = None
    if ws_path:
        tmpl_path, _ = save_bytes(tmpl_buf.getvalue(), f"{artifact_id}_data_template.xlsx", ws_path)
        val_path,  _ = save_bytes(val_bytes, f"{artifact_id}_validation_rules.pmuconfig", ws_path)
        kpi_path,  _ = save_bytes(kpi_bytes, f"{artifact_id}_kpi_definitions.pmuconfig", ws_path)
        frm_path,  _ = save_bytes(frm_bytes, f"{artifact_id}_form_structure.json", ws_path)
        register_outputs(artifact_id, project_code, tmpl_path, val_path, kpi_path, frm_path)

    # Save column metadata so downstream apps can resolve labels
    if ws_path:
        meta = metadata_from_monitoring_job(job)
        save_column_metadata(ws_path, artifact_id, meta)

    st.success(f"All outputs generated! Artifact: **{artifact_id}**")
    b1, b2, b3, b4 = st.columns(4)
    b1.download_button("⬇ data_template.xlsx", tmpl_buf,
        file_name=f"{artifact_id}_data_template.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True, type="primary")
    b2.download_button("⬇ validation_rules.pmuconfig", io.BytesIO(val_bytes),
        file_name=f"{artifact_id}_validation_rules.pmuconfig",
        mime="application/json", use_container_width=True)
    b3.download_button("⬇ kpi_definitions.pmuconfig", io.BytesIO(kpi_bytes),
        file_name=f"{artifact_id}_kpi_definitions.pmuconfig",
        mime="application/json", use_container_width=True)
    b4.download_button("⬇ form_structure.json", io.BytesIO(frm_bytes),
        file_name=f"{artifact_id}_form_structure.json",
        mime="application/json", use_container_width=True)

# ── Google Form Creation ──────────────────────────────────────────────────────
st.markdown("---")
st.markdown("### Create Google Form")

if not has_sections():
    st.warning("Assign fields to form sections (Step 2 — Form) before creating a Google Form.")
else:
    google_available = credentials_available()
    if google_available:
        st.success("✅ Google credentials detected. Ready to create Google Form and Sheets.")
        gf1, gf2 = st.columns(2)
        if gf1.button("🔗 Create Google Form", type="primary", use_container_width=True):
            with st.spinner("Creating Google Form…"):
                try:
                    form_meta = create_google_form(job)
                    st.session_state["mb_form_meta"] = form_meta
                    st.success("Google Form created!")
                    st.markdown(f"**Edit URL:** {form_meta['edit_url']}")
                    st.markdown(f"**Responder URL:** {form_meta['responder_url']}")
                    st.code(form_meta["responder_url"])
                except Exception as e:
                    st.error(f"Could not create Google Form: {e}")

        if gf2.button("📊 Create Google Sheet (Data Template)", use_container_width=True):
            with st.spinner("Creating Google Sheet…"):
                try:
                    import pandas as pd
                    sheet_title = f"{job.monitoring_name} — Data Collection"
                    sheet_meta  = create_spreadsheet(sheet_title)
                    # Write headers matching enabled fields
                    headers_df = pd.DataFrame(columns=[f.name for f in job.fields if f.enabled])
                    clear_and_write(sheet_meta["sheet_id"], "Sheet1", headers_df)
                    share_file(sheet_meta["sheet_id"])
                    st.success("Google Sheet created!")
                    st.markdown(f"**Sheet URL:** {sheet_meta['sheet_url']}")
                    st.code(sheet_meta["sheet_url"])
                    st.caption("Sheet headers match your schema fields. Share with data collectors.")
                except Exception as e:
                    st.error(f"Could not create Google Sheet: {e}")
    else:
        st.info("🔒 Google credentials not configured. "
                "Place `credentials.json` in `PMU_Tools/credentials/` to enable Google Form and Sheet creation.\n\n"
                "You can still download the **Form Structure JSON** and **Excel Template** above.")

# ── Workspace Package ─────────────────────────────────────────────────────────
if ws:
    st.markdown("---")
    st.markdown("### Export Workspace as .pmupack")
    st.caption("Bundle the entire workspace (configs, outputs, templates) into a portable package file.")
    import tempfile
    if st.button("📦 Export Workspace Package"):
        with st.spinner("Packaging workspace…"):
            with tempfile.TemporaryDirectory() as tmp:
                pack_path = export_package(ws["slug"], tmp)
                pack_bytes = pack_path.read_bytes()
        st.download_button("⬇ Download .pmupack", io.BytesIO(pack_bytes),
            file_name=pack_path.name, mime="application/zip", use_container_width=True)
