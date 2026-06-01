"""Page 6 — Generate all analytics outputs and save config."""
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
    has_data, get_raw_df,
    get_agg_results, set_agg_results, has_agg_configs,
    get_kpi_result, set_kpi_result, has_kpis,
    get_rank_results, set_rank_results,
    get_var_results, set_var_results,
    get_trend_results, set_trend_results,
    run_all_configs, calculate_kpis, rank_entities, calc_variance, analyze_trend,
    save_aggregation, save_kpi_report, save_analytics, register_outputs,
)
from shared import (
    generate_id, save_config, clone_config, list_configs,
    credentials_available, clear_and_write, upload_to_drive, create_spreadsheet,
)

st.set_page_config(page_title="Generate — Analytics Studio", page_icon="📥", layout="wide")
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
    st.info(f"**{len(job.agg_job.configs)}** agg · **{len([k for k in job.kpi_defs if k.enabled])}** KPI · "
            f"**{len([r for r in job.analytics_job.rankings if r.enabled])}** rank")
    if st.button("🗑 Reset Studio", use_container_width=True):
        reset_state(); st.rerun()

st.markdown("# 📥 Generate")
st.caption("Step 6 of 6 — Run everything, save config, download outputs")
st.markdown("---")

if not has_data():
    st.warning("Please upload a file first (Step 1 — Upload).")
    st.stop()

df           = get_raw_df()
project_code = job.project_code or "PMU"
ws_path      = ws["path"] if ws else None

artifact_id = job.artifact_id or generate_id(project_code, "ANL")
if not job.artifact_id:
    job.artifact_id = artifact_id; set_job(job)

# ── Pipeline Summary ──────────────────────────────────────────────────────────
st.markdown("### Analysis Pipeline")
c1, c2, c3, c4 = st.columns(4)
c1.metric("Aggregations",     len(job.agg_job.configs))
c2.metric("KPIs",             len([k for k in job.kpi_defs if k.enabled]))
c3.metric("Rankings",         len([r for r in job.analytics_job.rankings if r.enabled]))
c4.metric("Trend Analyses",   len([t for t in job.analytics_job.trends if t.enabled]))

st.markdown("---")

# ── Run All ───────────────────────────────────────────────────────────────────
if st.button("▶ Run Full Analysis", type="primary", use_container_width=True):
    with st.spinner("Running aggregations…"):
        if job.agg_job.configs:
            set_agg_results(run_all_configs(df, job.agg_job.configs))

    with st.spinner("Calculating KPIs…"):
        if job.kpi_defs:
            set_kpi_result(calculate_kpis(df, job.kpi_defs))

    with st.spinner("Running rankings…"):
        r_res = {r.rank_id: rank_entities(df, r) for r in job.analytics_job.rankings if r.enabled}
        set_rank_results(r_res)

    with st.spinner("Running variance analyses…"):
        v_res = {v.var_id: calc_variance(df, v) for v in job.analytics_job.variances if v.enabled}
        set_var_results(v_res)

    with st.spinner("Running trend analyses…"):
        t_res = {t.trend_id: analyze_trend(df, t) for t in job.analytics_job.trends if t.enabled}
        set_trend_results(t_res)

    st.success("Full analysis complete."); st.rerun()

# ── Results preview ───────────────────────────────────────────────────────────
agg_results   = get_agg_results()
kpi_result    = get_kpi_result()
rank_results  = get_rank_results()
var_results   = get_var_results()
trend_results = get_trend_results()

if any([agg_results, kpi_result, rank_results, var_results, trend_results]):
    if kpi_result:
        kpi_df, _ = kpi_result
        if "Composite Score" in kpi_df.columns:
            st.metric("Mean Composite Score", f"{kpi_df['Composite Score'].mean():.2f}")

    st.markdown("---")

    # ── Save / Clone config ───────────────────────────────────────────────────
    if ws:
        st.markdown("### Save Configuration")
        config_name = st.text_input("Configuration name", value=f"{project_code} Analysis")
        cc1, cc2 = st.columns(2)
        if cc1.button("💾 Save to Workspace", use_container_width=True):
            save_config(ws["path"], "APP-003", config_name, job.to_config())
            st.success(f"Configuration **{config_name}** saved.")
        saved = list_configs(ws["path"], "APP-003")
        if saved:
            clone_from = cc2.selectbox("Clone from", list({c["name"] for c in saved}),
                                       key="anl_clone_from", label_visibility="collapsed")
            if cc2.button("📋 Clone Config", use_container_width=True):
                clone_config(ws["path"], "APP-003", clone_from, f"{clone_from} (Copy)")
                st.success(f"Cloned **{clone_from}**.")

    st.markdown("---")
    st.markdown("### Download Outputs")
    d1, d2, d3 = st.columns(3)

    with d1:
        if agg_results:
            agg_named = {cfg.name: agg_results[cfg.config_id]
                         for cfg in job.agg_job.configs if cfg.config_id in agg_results}
            if st.button("📊 Generate aggregation.xlsx", use_container_width=True, type="primary"):
                path, buf = save_aggregation(agg_named, project_code, artifact_id, ws_path)
                st.download_button("⬇ aggregation.xlsx", buf, file_name=os.path.basename(path),
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True)

    with d2:
        if kpi_result:
            kpi_df, kpi_summary = kpi_result
            if st.button("🎯 Generate kpi_report.xlsx", use_container_width=True, type="primary"):
                path, buf = save_kpi_report(kpi_df, kpi_summary, project_code, artifact_id, ws_path)
                st.download_button("⬇ kpi_report.xlsx", buf, file_name=os.path.basename(path),
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True)

    with d3:
        if rank_results or var_results or trend_results:
            r_named = {r.name: rank_results[r.rank_id] for r in job.analytics_job.rankings if r.rank_id in rank_results}
            v_named = {v.name: var_results[v.var_id] for v in job.analytics_job.variances if v.var_id in var_results}
            t_named = {t.name: trend_results[t.trend_id] for t in job.analytics_job.trends if t.trend_id in trend_results}
            if st.button("📈 Generate analytics.xlsx", use_container_width=True, type="primary"):
                path, buf = save_analytics(r_named, v_named, t_named, project_code, artifact_id, ws_path)
                st.download_button("⬇ analytics.xlsx", buf, file_name=os.path.basename(path),
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True)

    st.markdown("---")
    if st.button("📦 Generate All Outputs", use_container_width=True):
        agg_named = {cfg.name: agg_results[cfg.config_id] for cfg in job.agg_job.configs if cfg.config_id in agg_results}
        r_named   = {r.name: rank_results[r.rank_id] for r in job.analytics_job.rankings if r.rank_id in rank_results}
        v_named   = {v.name: var_results[v.var_id] for v in job.analytics_job.variances if v.var_id in var_results}
        t_named   = {t.name: trend_results[t.trend_id] for t in job.analytics_job.trends if t.trend_id in trend_results}

        agg_path = agg_buf = kpi_path = kpi_buf = anl_path = anl_buf = None
        if agg_named:
            agg_path, agg_buf = save_aggregation(agg_named, project_code, artifact_id, ws_path)
        if kpi_result:
            kpi_df, kpi_summary = kpi_result
            kpi_path, kpi_buf = save_kpi_report(kpi_df, kpi_summary, project_code, artifact_id, ws_path)
        if r_named or v_named or t_named:
            anl_path, anl_buf = save_analytics(r_named, v_named, t_named, project_code, artifact_id, ws_path)

        register_outputs(artifact_id, project_code, agg_path, kpi_path, anl_path)
        st.success(f"All outputs generated! Artifact: **{artifact_id}**")

        b1, b2, b3 = st.columns(3)
        if agg_buf:
            b1.download_button("⬇ aggregation.xlsx", agg_buf, file_name=os.path.basename(agg_path),
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True, type="primary")
        if kpi_buf:
            b2.download_button("⬇ kpi_report.xlsx", kpi_buf, file_name=os.path.basename(kpi_path),
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True, type="primary")
        if anl_buf:
            b3.download_button("⬇ analytics.xlsx", anl_buf, file_name=os.path.basename(anl_path),
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True, type="primary")
    # ── Google Sheets + Drive output ──────────────────────────────────────────
    st.markdown("---")
    st.markdown("### Push to Google Sheets / Drive")
    if not credentials_available():
        st.info("🔒 Google credentials not configured.")
    else:
        gs1, gs2 = st.columns(2)
        with gs1:
            st.markdown("**Write KPI results to Google Sheets**")
            sheet_url_out = st.text_input("Sheet URL (blank = create new)", key="anl_sheet_out")
            if kpi_result and st.button("📊 Write KPI Report to Sheet", use_container_width=True):
                with st.spinner("Writing…"):
                    try:
                        import pandas as pd
                        kpi_df, kpi_summary = kpi_result
                        if sheet_url_out.strip():
                            clear_and_write(sheet_url_out.strip(), "KPI Report", kpi_df)
                            st.success("Written to sheet.")
                        else:
                            meta = create_spreadsheet(f"{artifact_id} — KPI Report")
                            clear_and_write(meta["sheet_id"], "KPI Report", kpi_df)
                            st.success("New Google Sheet created!")
                            st.code(meta["sheet_url"])
                    except Exception as e:
                        st.error(f"Error: {e}")
        with gs2:
            st.markdown("**Upload KPI report to Google Drive**")
            if kpi_result and ws_path and st.button("☁ Upload kpi_report to Drive", use_container_width=True):
                with st.spinner("Uploading…"):
                    try:
                        kpi_df, kpi_summary = kpi_result
                        path, _ = save_kpi_report(kpi_df, kpi_summary, project_code, artifact_id, ws_path)
                        result = upload_to_drive(path)
                        st.success("Uploaded!"); st.markdown(f"**Drive URL:** {result['web_url']}")
                    except Exception as e:
                        st.error(f"Upload failed: {e}")

    # ── Inter-app pass ────────────────────────────────────────────────────────
    if ws and kpi_result:
        st.markdown("---")
        st.markdown("### Pass Output to Next App")
        st.caption("Save KPI dataset to workspace so APP-004/APP-005 can pick it up directly.")
        if st.button("📤 Pass to Dashboard Studio (APP-004)", type="primary", use_container_width=True):
            with st.spinner("Saving to workspace data_sources…"):
                ds_folder = os.path.join(ws["path"], "data_sources")
                os.makedirs(ds_folder, exist_ok=True)
                kpi_df, _ = kpi_result
                out_path = os.path.join(ds_folder, f"{artifact_id}_kpi_dataset.xlsx")
                kpi_df.to_excel(out_path, index=False)
                st.success("Saved to workspace `data_sources/`. Open APP-004 and select this file from workspace sources.")

else:
    st.info("Click **Run Full Analysis** above to compute all results before downloading.")
