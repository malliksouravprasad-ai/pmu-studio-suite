"""Page 6 — Generate dashboard Excel outputs."""
import sys
import os

_APP_DIR  = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_PMU_ROOT = os.path.dirname(os.path.dirname(_APP_DIR))
for _p in [_PMU_ROOT, _APP_DIR]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

import io
import zipfile
import streamlit as st
from engine import (
    init_state, reset_state, get_workspace, get_job, set_job,
    has_data, get_raw_df, has_kpis, has_charts, has_tables,
    save_dashboard, save_dashboard_dataset, register_outputs,
)
from shared import (
    generate_id, save_config, credentials_available,
    render_integration_sidebar, render_bq_push_section, render_appscript_section,
    clear_and_write, upload_to_drive, create_spreadsheet,
)

st.set_page_config(page_title="Generate — Dashboard Studio", page_icon="📥", layout="wide")
init_state()

ws  = get_workspace()
job = get_job()
dj  = job.dashboard_job

with st.sidebar:
    st.markdown("## 🖥️ Dashboard Studio")
    st.caption("APP-004 · OSEPA PMU Tool Suite")
    st.markdown("---")
    if ws:
        st.success(f"📁 **{ws['name']}**")
    else:
        st.warning("No workspace selected")
    st.info(f"**{len(dj.kpis)}** KPI · **{len(dj.charts)}** chart · **{len(dj.tables)}** table")
    if st.button("🗑 Reset Studio", use_container_width=True):
        reset_state(); st.rerun()
    render_integration_sidebar()

st.markdown("# 📥 Generate")
st.caption("Step 6 of 6 — Download dashboard Excel workbook")
st.markdown("---")

if not has_data():
    st.warning("Please upload a file first."); st.stop()

df           = get_raw_df()
project_code = job.project_code or "PMU"
ws_path      = ws["path"] if ws else None

artifact_id = dj.artifact_id or generate_id(project_code, "DSH")
if not dj.artifact_id:
    dj.artifact_id = artifact_id
    set_job(job)

st.markdown("### Dashboard Configuration")
c1, c2, c3 = st.columns(3)
c1.metric("KPI Cards", len(dj.kpis))
c2.metric("Charts",    len(dj.charts))
c3.metric("Tables",    len(dj.tables))

if not (dj.kpis or dj.charts or dj.tables):
    st.warning("Nothing to generate. Add KPIs, charts, or tables first.")
    st.stop()

st.markdown("---")

# ── Generate dashboard ────────────────────────────────────────────────────────
col1, col2 = st.columns(2)

with col1:
    if st.button("📊 Generate dashboard.xlsx", type="primary", use_container_width=True):
        with st.spinner("Building dashboard workbook…"):
            path, buf = save_dashboard(df, dj, ws_path)
        st.download_button("⬇ dashboard.xlsx", buf,
            file_name=os.path.basename(path),
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True, type="primary")
        st.success(f"Artifact: {artifact_id}")

with col2:
    if st.button("📋 Generate dashboard_dataset.xlsx", use_container_width=True):
        with st.spinner("Building dataset…"):
            path, buf = save_dashboard_dataset(df, dj, ws_path)
        st.download_button("⬇ dashboard_dataset.xlsx", buf,
            file_name=os.path.basename(path),
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True)

st.markdown("---")
if st.button("📦 Generate All Outputs", use_container_width=True):
    with st.spinner("Generating all outputs…"):
        dash_path, dash_buf  = save_dashboard(df, dj, ws_path)
        data_path, data_buf  = save_dashboard_dataset(df, dj, ws_path)
        register_outputs(artifact_id, project_code, dash_path, data_path)

    st.success(f"All outputs generated! Artifact: **{artifact_id}**")
    d1, d2 = st.columns(2)
    d1.download_button("⬇ dashboard.xlsx", dash_buf,
        file_name=os.path.basename(dash_path),
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True, type="primary")
    d2.download_button("⬇ dashboard_dataset.xlsx", data_buf,
        file_name=os.path.basename(data_path),
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True)

# ── Segregated Excel by Column ───────────────────────────────────────────────
st.markdown("---")
st.markdown("### Segregated Excel by Column")
st.caption(
    "Generate one Excel file per unique value in a column "
    "(e.g. one file per District). All files download as a ZIP."
)

_seg_col = st.selectbox("Split by column", df.columns.tolist(), key="dsh_seg_col")
_seg_vals = sorted(df[_seg_col].dropna().unique().tolist()) if _seg_col else []
st.caption(f"**{len(_seg_vals)}** unique value(s) in **{_seg_col}**")

if _seg_vals and st.button(
    f"📂 Generate {len(_seg_vals)} Segregated File(s)", use_container_width=True, key="dsh_seg_btn"
):
    import pandas as _pd
    _zip = io.BytesIO()
    _errs = []
    with st.spinner(f"Building {len(_seg_vals)} file(s)…"):
        with zipfile.ZipFile(_zip, "w", zipfile.ZIP_DEFLATED) as _zf:
            for _v in _seg_vals:
                try:
                    _sub = df[df[_seg_col] == _v].copy()
                    if _sub.empty:
                        continue
                    _out = io.BytesIO()
                    with _pd.ExcelWriter(_out, engine="openpyxl") as _ew:
                        _sub.to_excel(_ew, index=False, sheet_name="Data")
                    _safe = (
                        str(_v).replace("/", "_").replace("\\", "_").replace(":", "_")
                    )
                    _zf.writestr(f"dashboard_{_safe}.xlsx", _out.getvalue())
                except Exception as _e:
                    _errs.append(f"{_v}: {_e}")
    _zip.seek(0)
    _zfname = f"segregated_{_seg_col}_{artifact_id}.zip"
    st.download_button(
        f"⬇ {_zfname}", _zip, file_name=_zfname,
        mime="application/zip", use_container_width=True, type="primary",
        key="dsh_seg_dl",
    )
    if _errs:
        with st.expander(f"{len(_errs)} error(s)"):
            for _e in _errs:
                st.warning(_e)
    st.success(f"ZIP ready — {len(_seg_vals) - len(_errs)} file(s) generated.")

# ── Google Sheets + Drive ─────────────────────────────────────────────────────
st.markdown("---")
st.markdown("### Push to Google Sheets / Drive")
if not credentials_available():
    st.info("🔒 Google credentials not configured.")
else:
    gs1, gs2 = st.columns(2)
    with gs1:
        sheet_url_dash = st.text_input("Sheet URL (blank = create new)", key="dsh_sheet_out")
        if st.button("📊 Write Dataset to Google Sheet", use_container_width=True):
            with st.spinner("Writing…"):
                try:
                    if sheet_url_dash.strip():
                        clear_and_write(sheet_url_dash.strip(), "Dashboard Data", df)
                        st.success("Written to sheet.")
                    else:
                        meta = create_spreadsheet(f"{artifact_id} — Dashboard Data")
                        clear_and_write(meta["sheet_id"], "Dashboard Data", df)
                        st.success("New sheet created!")
                        st.code(meta["sheet_url"])
                except Exception as e:
                    st.error(f"Error: {e}")
    with gs2:
        if ws_path and st.button("☁ Upload dashboard.xlsx to Drive", use_container_width=True):
            with st.spinner("Uploading…"):
                try:
                    path, _ = save_dashboard(df, dj, ws_path)
                    result  = upload_to_drive(path)
                    st.success("Uploaded!"); st.markdown(f"**Drive URL:** {result['web_url']}")
                except Exception as e:
                    st.error(f"Upload failed: {e}")

# ── Inter-app pass ────────────────────────────────────────────────────────────
if ws:
    st.markdown("---")
    st.markdown("### Pass Output to Next App")
    if st.button("📤 Pass dataset to Deliverable Studio (APP-005)", type="primary", use_container_width=True):
        ds_folder = os.path.join(ws["path"], "data_sources")
        os.makedirs(ds_folder, exist_ok=True)
        out_path = os.path.join(ds_folder, f"{artifact_id}_dashboard_data.xlsx")
        df.to_excel(out_path, index=False)
        st.success("Saved to workspace `data_sources/`. Open APP-005 and select this file.")

# ── BigQuery & Apps Script ────────────────────────────────────────────────────
st.markdown("---")
st.markdown("### Push to BigQuery / Trigger Aggregator")
_tab_bq4, _tab_as4 = st.tabs(["☁ Push to BigQuery", "📜 Apps Script Aggregator"])
with _tab_bq4:
    render_bq_push_section(df, artifact_id, project_code)
with _tab_as4:
    render_appscript_section()
