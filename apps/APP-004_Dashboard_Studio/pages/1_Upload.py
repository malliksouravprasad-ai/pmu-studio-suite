"""Page 1 — Upload data file."""
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
from engine import init_state, reset_state, get_workspace, get_job, set_job, set_raw_df, get_raw_df, has_data, DashboardStudioJob
from shared import (
    list_configs, load_config, credentials_available, read_sheet,
    render_integration_sidebar, render_bq_upload_tab,
)

st.set_page_config(page_title="Upload — Dashboard Studio", page_icon="📤", layout="wide")
init_state()

ws  = get_workspace()
job = get_job()

with st.sidebar:
    sidebar_brand("Dashboard Studio", "APP-004")
    if ws:
        st.success(f"📁 **{ws['name']}**")
    else:
        st.warning("No workspace selected")
    if job.source_filename:
        st.info(f"📄 {job.source_filename}")
    if st.button("🗑 Reset Studio", use_container_width=True):
        reset_state(); st.rerun()
    render_integration_sidebar()

page_header("Upload", subtitle="Load your dataset — CSV, Excel, Google Sheet, or BigQuery", icon="📤", step=1, total_steps=6)

if ws:
    saved = list_configs(ws["path"], "APP-004")
    if saved:
        with st.expander("📂 Load a saved dashboard layout", expanded=False):
            config_names = list({c["name"] for c in saved})
            chosen = st.selectbox("Saved layouts", config_names)
            if st.button("Load Layout", type="primary"):
                data = load_config(ws["path"], "APP-004", chosen)
                set_job(DashboardStudioJob.from_config(data["config"]))
                st.success(f"Layout **{chosen}** loaded."); st.rerun()

# ── Workspace data source picker ──────────────────────────────────────────────
if ws:
    ws_outputs  = os.path.join(ws["path"], "outputs")
    ws_sources  = os.path.join(ws["path"], "data_sources")
    avail_files = []
    for folder in [ws_outputs, ws_sources]:
        if os.path.isdir(folder):
            avail_files += [os.path.join(folder, f) for f in os.listdir(folder)
                            if f.endswith((".csv", ".xlsx"))]
    if avail_files:
        with st.expander("📁 Use a workspace data source (from APP-002 / APP-003)", expanded=False):
            file_labels = {os.path.basename(p): p for p in avail_files}
            sel = st.selectbox("Select file", list(file_labels.keys()), key="dsh_ws_sel")
            if st.button("Load from Workspace", type="primary", key="dsh_ws_load"):
                fpath = file_labels[sel]
                try:
                    df_ws = pd.read_csv(fpath) if fpath.endswith(".csv") else pd.read_excel(fpath)
                    job.source_filename = sel
                    job.project_code    = ws.get("project_code", "PMU")
                    set_job(job); set_raw_df(df_ws)
                    st.success(f"Loaded **{len(df_ws):,} rows × {len(df_ws.columns)} cols** from `{sel}`")
                    st.rerun()
                except Exception as e:
                    st.error(f"Could not read: {e}")

default_code    = ws["project_code"] if ws else (job.project_code or "PMU")
project_code    = st.text_input("Project Code", value=default_code, key="dsh_proj_code")
dashboard_title = st.text_input("Dashboard Title", value=job.dashboard_job.dashboard_title, key="dsh_title")

tab_file, tab_gsheet, tab_bq = st.tabs(["📂 Upload File", "🔗 Google Sheet", "☁ BigQuery"])

with tab_file:
    uploaded = st.file_uploader("Upload CSV or XLSX", type=["csv", "xlsx"], key="dsh_file_up")
    if uploaded:
        try:
            df = pd.read_csv(uploaded) if uploaded.name.endswith(".csv") else pd.read_excel(uploaded)
            job.project_code    = project_code.strip().upper() or "PMU"
            job.source_filename = uploaded.name
            job.dashboard_job.project_code    = job.project_code
            job.dashboard_job.dashboard_title = dashboard_title.strip() or "PMU Dashboard"
            set_job(job); set_raw_df(df)
            st.success(f"Loaded **{len(df):,} rows × {len(df.columns)} cols**")
            st.rerun()
        except Exception as e:
            st.error(f"Could not read file: {e}")

with tab_gsheet:
    if not credentials_available():
        st.info("🔒 Google credentials not configured.")
    else:
        gs_url  = st.text_input("Google Sheet URL or ID", key="dsh_gs_url")
        gs_name = st.text_input("Sheet Tab Name", value="Sheet1", key="dsh_gs_name")
        if st.button("Load from Google Sheets", type="primary", key="dsh_gs_btn") and gs_url.strip():
            with st.spinner("Reading Google Sheet…"):
                try:
                    df = read_sheet(gs_url.strip(), gs_name.strip() or "Sheet1")
                    job.source_filename = f"GSheet: {gs_url[:40]}…"
                    job.project_code    = project_code.strip().upper() or "PMU"
                    job.dashboard_job.project_code    = job.project_code
                    job.dashboard_job.dashboard_title = dashboard_title.strip() or "PMU Dashboard"
                    set_job(job); set_raw_df(df)
                    st.success(f"Loaded **{len(df):,} rows × {len(df.columns)} cols**")
                    st.rerun()
                except Exception as e:
                    st.error(f"Could not read sheet: {e}")

with tab_bq:
    def _bq_loaded_004(df, label):
        job.source_filename = label
        job.project_code    = project_code.strip().upper() or "PMU"
        job.dashboard_job.project_code    = job.project_code
        job.dashboard_job.dashboard_title = dashboard_title.strip() or "PMU Dashboard"
        set_job(job); set_raw_df(df)
    render_bq_upload_tab(_bq_loaded_004)

if not has_data():
    st.info("Upload a CSV/XLSX, connect a Google Sheet, or load from BigQuery to begin.")
    st.stop()

df = get_raw_df()
st.success(f"**{job.source_filename}** loaded — navigate to **KPIs** or **Charts** to continue.")
with st.expander("Preview (first 10 rows)", expanded=True):
    st.dataframe(df.head(10), use_container_width=True)

m1, m2, m3 = st.columns(3)
m1.metric("Rows",    f"{len(df):,}")
m2.metric("Columns", len(df.columns))
m3.metric("Numeric", len(df.select_dtypes(include="number").columns))
