"""Page 6 — Apply pipeline, save config to workspace, download outputs."""
import sys
import os

_APP_DIR  = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_PMU_ROOT = os.path.dirname(os.path.dirname(_APP_DIR))
for _p in [_PMU_ROOT, _APP_DIR]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

import streamlit as st
from engine import (
    init_state, reset_state, get_workspace, get_job, set_job,
    has_data, get_raw_df, get_mapped_df, get_working_df,
    has_transform_steps, has_rules, has_mappings, has_rule_results,
    get_transform_log, set_transform_log,
    get_rule_results, set_rule_results,
    get_exceptions, get_calc_log,
    get_match_results, set_mapped_df,
    apply_all, run_all_rules, apply_all_mappings,
    save_clean_dataset, save_transform_log, save_validation_report, register_outputs,
)
from shared import (
    generate_id, save_config, clone_config, list_configs, export_config,
    credentials_available, clear_and_write, upload_to_drive, create_spreadsheet,
    render_autosave_controls, save_column_metadata, load_column_metadata,
)

st.set_page_config(page_title="Generate — Data Processing Studio", page_icon="📥", layout="wide")
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
    steps   = [s for s in job.transform_job.steps if s.enabled]
    rules   = [r for r in job.rule_job.rules if r.enabled]
    maps    = job.mapping_job.column_mappings
    st.info(f"**{len(steps)}** transform · **{len(maps)}** map · **{len(rules)}** validate")
    if st.button("🗑 Reset Studio", use_container_width=True):
        reset_state(); st.rerun()
    render_autosave_controls(ws, "APP-002", job, key_prefix="dps")

st.markdown("# 📥 Generate")
st.caption("Step 6 of 6 — Apply pipeline, save configuration, download outputs")
st.markdown("---")

if not has_data():
    st.warning("Please upload a file first (Step 1 — Upload).")
    st.stop()

df           = get_raw_df()
project_code = job.project_code or "PMU"
ws_path      = ws["path"] if ws else None

artifact_id = job.artifact_id or generate_id(project_code, "DPS")
if not job.artifact_id:
    job.artifact_id = artifact_id
    set_job(job)

# ── Pipeline Summary ──────────────────────────────────────────────────────────
st.markdown("### Pipeline Summary")
c1, c2, c3, c4 = st.columns(4)
c1.metric("Source File",      job.source_filename or "—")
c2.metric("Transform Steps",  len(steps))
c3.metric("Mapping Columns",  len(maps))
c4.metric("Validation Rules", len(rules))

if steps:
    with st.expander("Transform steps"):
        for i, s in enumerate(steps, 1):
            st.markdown(f"**{i}.** `{s.op_type.replace('_', ' ').title()}` — {s.description}")

if maps:
    with st.expander("Mapping columns"):
        for m in maps:
            st.markdown(f"- **{m.source_col}** → `{m.mapping_type}` (fuzzy ≥ {m.fuzzy_threshold})")

if rules:
    with st.expander("Validation rules"):
        for r in rules:
            st.markdown(f"- **{r.name}** · `{r.rule_type}` · {r.severity}")

st.markdown("---")

# ── Apply Pipeline ────────────────────────────────────────────────────────────
if st.button("▶ Apply Full Pipeline & Preview", type="primary", use_container_width=True):
    with st.spinner("Applying transforms…"):
        transformed_df, log = apply_all(df, job.transform_job.steps)
    set_transform_log(log)

    if maps:
        with st.spinner("Applying mappings…"):
            match_results = get_match_results()
            if not match_results:
                from engine import run_matching
                for cm in maps:
                    if cm.source_col in transformed_df.columns:
                        match_results[cm.mapping_id] = run_matching(transformed_df[cm.source_col], cm)
            mapped_df = apply_all_mappings(transformed_df, maps, match_results)
        set_mapped_df(mapped_df)
    else:
        set_mapped_df(transformed_df)

    final_df = get_mapped_df()

    if rules:
        with st.spinner("Running validation rules…"):
            result_df, val_results, exceptions, calc_log = run_all_rules(final_df, rules)
        set_rule_results(val_results, exceptions, calc_log)
    else:
        result_df = final_df

    st.success(f"Pipeline complete. Output: **{len(result_df):,} rows × {len(result_df.columns)} columns**")
    st.rerun()

# ── Preview ───────────────────────────────────────────────────────────────────
final_df    = get_mapped_df() or df
log         = get_transform_log()
val_results = get_rule_results()
exceptions  = get_exceptions()
calc_log    = get_calc_log()

if final_df is not None and len(get_transform_log()) > 0 or get_mapped_df() is not None:
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Original Rows",  f"{len(df):,}")
    m2.metric("Output Rows",    f"{len(final_df):,}", delta=f"{len(final_df)-len(df):,}")
    m3.metric("Original Cols",  len(df.columns))
    m4.metric("Output Cols",    len(final_df.columns), delta=len(final_df.columns)-len(df.columns))

    if val_results:
        total_fail = sum(rr.failed for rr in val_results)
        st.metric("Validation Exceptions", f"{total_fail:,} rows")

    with st.expander("Preview output (first 20 rows)", expanded=True):
        st.dataframe(final_df.head(20), use_container_width=True)

    st.markdown("---")

    # ── Save / Clone / Export config ──────────────────────────────────────────
    if ws:
        st.markdown("### Save Configuration")
        config_name = st.text_input("Configuration name", value=f"{project_code} Pipeline")
        cfg_c1, cfg_c2, cfg_c3 = st.columns(3)
        if cfg_c1.button("💾 Save to Workspace", use_container_width=True):
            save_config(ws["path"], "APP-002", config_name, job.to_config())
            st.success(f"Configuration **{config_name}** saved.")
        saved = list_configs(ws["path"], "APP-002")
        if saved:
            clone_names = list({c["name"] for c in saved})
            clone_from  = cfg_c2.selectbox("Clone from", clone_names, key="dps_clone_from", label_visibility="collapsed")
            if cfg_c2.button("📋 Clone Config", use_container_width=True):
                clone_config(ws["path"], "APP-002", clone_from, f"{clone_from} (Copy)")
                st.success(f"Cloned **{clone_from}**.")
        if cfg_c3.button("⬇ Export .pmuconfig", use_container_width=True):
            try:
                import json, io
                export_bytes = json.dumps({"app_id": "APP-002", "config": job.to_config()}, indent=2).encode()
                st.download_button("Download .pmuconfig", io.BytesIO(export_bytes),
                    file_name=f"{artifact_id}_pipeline.pmuconfig", mime="application/json",
                    use_container_width=True)
            except Exception as e:
                st.error(f"Export failed: {e}")

    st.markdown("---")

    # ── Generate outputs ──────────────────────────────────────────────────────
    st.markdown("### Download Outputs")
    g1, g2, g3 = st.columns(3)

    with g1:
        if st.button("📊 Generate Clean Dataset", use_container_width=True, type="primary"):
            with st.spinner("Building…"):
                path, buf = save_clean_dataset(final_df, project_code, artifact_id, ws_path)
            st.download_button("⬇ clean_dataset.xlsx", buf,
                file_name=os.path.basename(path),
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True)

    with g2:
        if log and st.button("📋 Generate Transformation Log", use_container_width=True):
            with st.spinner("Building…"):
                path, buf = save_transform_log(log, project_code, artifact_id, ws_path)
            st.download_button("⬇ transformation_log.xlsx", buf,
                file_name=os.path.basename(path),
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True)

    with g3:
        if val_results and st.button("✅ Generate Validation Report", use_container_width=True):
            from engine import run_all_rules
            with st.spinner("Building…"):
                result_df, vr, exc, cl = run_all_rules(final_df, rules)
                path, buf = save_validation_report(result_df, vr, exc, cl, project_code, artifact_id, ws_path)
            st.download_button("⬇ validation_report.xlsx", buf,
                file_name=os.path.basename(path),
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True)

    st.markdown("---")
    if st.button("📦 Generate All Outputs", use_container_width=True):
        with st.spinner("Generating all outputs…"):
            clean_path, clean_buf = save_clean_dataset(final_df, project_code, artifact_id, ws_path)
            log_path = log_buf = None
            if log:
                log_path, log_buf = save_transform_log(log, project_code, artifact_id, ws_path)
            val_path = val_buf = None
            if val_results:
                from engine import run_all_rules
                result_df, vr, exc, cl = run_all_rules(final_df, rules)
                val_path, val_buf = save_validation_report(result_df, vr, exc, cl, project_code, artifact_id, ws_path)
            register_outputs(
                artifact_id, project_code, clean_path, log_path, val_path,
                source_file=job.source_filename or "",
                config_name="",
                config_version="",
            )
            if ws_path:
                col_meta = {c: {"label": c, "type": "text", "unit": "", "description": ""}
                            for c in final_df.columns}
                existing_meta = load_column_metadata(ws_path)
                col_meta.update(existing_meta)
                save_column_metadata(ws_path, artifact_id, col_meta)

        st.success(f"All outputs generated! Artifact: **{artifact_id}**")
        d1, d2, d3 = st.columns(3)
        with d1:
            st.download_button("⬇ clean_dataset.xlsx", clean_buf,
                file_name=os.path.basename(clean_path),
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True, type="primary")
        with d2:
            if log_buf:
                st.download_button("⬇ transformation_log.xlsx", log_buf,
                    file_name=os.path.basename(log_path),
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True)
        with d3:
            if val_buf:
                st.download_button("⬇ validation_report.xlsx", val_buf,
                    file_name=os.path.basename(val_path),
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True)
    # ── Google Sheets output ──────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("### Push to Google Sheets / Drive")
    if not credentials_available():
        st.info("🔒 Google credentials not configured. Place `credentials.json` in `PMU_Tools/credentials/` to enable.")
    else:
        gs1, gs2 = st.columns(2)
        with gs1:
            st.markdown("**Write to Google Sheets**")
            sheet_url_out = st.text_input("Sheet URL or ID (leave blank to create new)", key="dps_sheet_out")
            sheet_tab     = st.text_input("Tab name", value="Clean Data", key="dps_tab_out")
            if st.button("📊 Write to Google Sheet", use_container_width=True):
                with st.spinner("Writing to Google Sheets…"):
                    try:
                        if sheet_url_out.strip():
                            clear_and_write(sheet_url_out.strip(), sheet_tab.strip() or "Clean Data", final_df)
                            st.success(f"Data written to sheet tab **{sheet_tab}**.")
                        else:
                            meta = create_spreadsheet(f"{artifact_id} — Clean Data")
                            clear_and_write(meta["sheet_id"], "Clean Data", final_df)
                            st.success("New Google Sheet created!")
                            st.markdown(f"**URL:** {meta['sheet_url']}")
                            st.code(meta["sheet_url"])
                    except Exception as e:
                        st.error(f"Could not write to Google Sheets: {e}")
        with gs2:
            st.markdown("**Upload to Google Drive**")
            if ws_path and final_df is not None:
                if st.button("☁ Upload clean_dataset to Drive", use_container_width=True):
                    with st.spinner("Uploading…"):
                        try:
                            path, _ = save_clean_dataset(final_df, project_code, artifact_id, ws_path)
                            result = upload_to_drive(path)
                            st.success("Uploaded to Drive!")
                            st.markdown(f"**Drive URL:** {result['web_url']}")
                        except Exception as e:
                            st.error(f"Upload failed: {e}")
            else:
                st.info("Apply pipeline first and ensure a workspace is active.")

    # ── Inter-app pipeline pass ───────────────────────────────────────────────
    if ws:
        st.markdown("---")
        st.markdown("### Pass Output to Next App")
        st.caption("Save processed dataset to workspace so APP-003/APP-004/APP-005 can pick it up directly.")
        if st.button("📤 Pass to Analytics Studio (APP-003)", type="primary", use_container_width=True):
            with st.spinner("Saving to workspace data_sources…"):
                import shutil
                ds_folder = os.path.join(ws["path"], "data_sources")
                os.makedirs(ds_folder, exist_ok=True)
                out_path = os.path.join(ds_folder, f"{artifact_id}_clean_dataset.xlsx")
                final_df.to_excel(out_path, index=False)
                st.success(f"Saved to workspace `data_sources/`. Open APP-003 and select this file from workspace sources.")

else:
    st.info("Click **Apply Full Pipeline & Preview** to run the complete pipeline and unlock downloads.")
