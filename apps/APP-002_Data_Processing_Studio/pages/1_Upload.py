"""Page 1 — Upload data file, load from Google Sheets, or use workspace data source."""
import sys
import os

_APP_DIR  = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_PMU_ROOT = os.path.dirname(os.path.dirname(_APP_DIR))
for _p in [_PMU_ROOT, _APP_DIR]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

import pandas as pd
import streamlit as st
from engine import (
    init_state, reset_state, get_workspace, set_raw_df,
    get_job, set_job, ProcessingJob, has_data,
)
from shared import (
    list_configs, load_config, clone_config,
    credentials_available, read_sheet,
    load_column_metadata, render_column_metadata_panel,
    render_integration_sidebar, render_bq_upload_tab,
)

st.set_page_config(page_title="Upload — Data Processing Studio", page_icon="📤", layout="wide")
init_state()

ws  = get_workspace()
job = get_job()

with st.sidebar:
    st.markdown("## ⚙️ Data Processing Studio")
    st.caption("APP-002 · OSEPA PMU Tool Suite")
    st.markdown("---")
    if ws:
        st.success(f"📁 **{ws['name']}**")
        st.caption(f"Project: {ws['project_code']}")
    else:
        st.warning("No workspace selected")
    if job.source_filename:
        st.info(f"📄 {job.source_filename}")

    # Pipeline overview
    steps = [s for s in job.transform_job.steps if s.enabled]
    maps  = job.mapping_job.column_mappings
    rules = [r for r in job.rule_job.rules if r.enabled]
    if steps or maps or rules:
        st.markdown("---")
        st.markdown("**Pipeline Status**")
        st.markdown(f"- {len(steps)} transform step(s)")
        st.markdown(f"- {len(maps)} mapping column(s)")
        st.markdown(f"- {len(rules)} validation rule(s)")
    if st.button("🗑 Reset Studio", use_container_width=True):
        reset_state(); st.rerun()
    render_integration_sidebar()

st.markdown("# 📤 Upload")
st.caption("Step 1 of 6 — Load your dataset (file, Google Sheet, or workspace data source)")
st.markdown("---")

# ── Saved config loader ───────────────────────────────────────────────────────
if ws:
    saved = list_configs(ws["path"], "APP-002")
    if saved:
        with st.expander("📂 Load / Clone a saved pipeline configuration", expanded=False):
            config_names = list({c["name"] for c in saved})
            col_cfg1, col_cfg2 = st.columns([3, 1])
            chosen = col_cfg1.selectbox("Saved configurations", config_names)
            if col_cfg2.button("Load", type="primary", use_container_width=True):
                data = load_config(ws["path"], "APP-002", chosen)
                loaded_job = ProcessingJob.from_config(data["config"])
                set_job(loaded_job)
                st.success(f"Loaded: **{chosen}** (v{data['version']})"); st.rerun()
            col_cl1, col_cl2 = st.columns([3, 1])
            clone_name = col_cl1.text_input("Clone as", value=f"{chosen} (Copy)", key="clone_name_inp")
            if col_cl2.button("Clone", use_container_width=True):
                clone_config(ws["path"], "APP-002", chosen, clone_name.strip())
                st.success(f"Cloned to **{clone_name.strip()}**.")

# ── Workspace data source picker ──────────────────────────────────────────────
if ws:
    ws_outputs = os.path.join(ws["path"], "outputs")
    ws_sources = os.path.join(ws["path"], "data_sources")
    available_files = []
    for folder in [ws_outputs, ws_sources]:
        if os.path.isdir(folder):
            available_files += [
                os.path.join(folder, f) for f in os.listdir(folder)
                if f.endswith((".csv", ".xlsx"))
            ]
    if available_files:
        with st.expander("📁 Use a workspace data source (output from another app)", expanded=False):
            file_labels = {os.path.basename(p): p for p in available_files}
            sel = st.selectbox("Select file", list(file_labels.keys()))
            if st.button("Load from Workspace", type="primary"):
                fpath = file_labels[sel]
                try:
                    df = pd.read_csv(fpath) if fpath.endswith(".csv") else pd.read_excel(fpath)
                    job.source_filename = sel
                    job.project_code    = ws.get("project_code", "PMU")
                    set_job(job); set_raw_df(df)
                    st.success(f"Loaded **{len(df):,} rows × {len(df.columns)} cols** from `{sel}`")
                    st.rerun()
                except Exception as e:
                    st.error(f"Could not read file: {e}")

# ── Input tabs ────────────────────────────────────────────────────────────────
tab_file, tab_gsheet, tab_bq = st.tabs(["📂 Upload File", "🔗 Google Sheet", "☁ BigQuery"])

with tab_file:
    col_left, col_right = st.columns([2, 1])
    with col_left:
        uploaded = st.file_uploader("Upload data file (CSV or XLSX)", type=["csv", "xlsx"])
    with col_right:
        default_code = ws["project_code"] if ws else (job.project_code or "PMU")
        project_code = st.text_input("Project Code", value=default_code)

    if uploaded:
        try:
            df = pd.read_csv(uploaded) if uploaded.name.endswith(".csv") else pd.read_excel(uploaded)
            job.project_code    = project_code.strip().upper() or "PMU"
            job.source_filename = uploaded.name
            set_job(job); set_raw_df(df)
            st.success(f"Loaded **{len(df):,} rows × {len(df.columns)} columns** from `{uploaded.name}`")
        except Exception as e:
            st.error(f"Could not read file: {e}")

with tab_gsheet:
    if not credentials_available():
        st.info("🔒 Google credentials not configured. Place `credentials.json` in `PMU_Tools/credentials/` to enable.")
    else:
        sheet_url  = st.text_input("Google Sheet URL or ID", placeholder="https://docs.google.com/spreadsheets/d/...")
        sheet_name = st.text_input("Sheet Tab Name", value="Sheet1")
        if st.button("Load from Google Sheets", type="primary") and sheet_url.strip():
            with st.spinner("Reading Google Sheet…"):
                try:
                    df = read_sheet(sheet_url.strip(), sheet_name.strip() or "Sheet1")
                    job.source_filename = f"GSheet: {sheet_url[:40]}…"
                    job.project_code    = (ws["project_code"] if ws else "PMU")
                    set_job(job); set_raw_df(df)
                    st.success(f"Loaded **{len(df):,} rows × {len(df.columns)} cols** from Google Sheet")
                    st.rerun()
                except Exception as e:
                    st.error(f"Could not read sheet: {e}")

with tab_bq:
    def _bq_loaded_002(df, label):
        job.source_filename = label
        job.project_code    = ws.get("project_code", "PMU") if ws else "PMU"
        set_job(job); set_raw_df(df)
    render_bq_upload_tab(_bq_loaded_002)

# ── Preview ───────────────────────────────────────────────────────────────────
if has_data():
    df = st.session_state.get("dps_raw_df")
    st.markdown("---")
    st.success(f"**{job.source_filename}** is loaded — navigate to **Clean** or **Transform** to continue.")

    with st.expander("Preview (first 10 rows)", expanded=True):
        st.dataframe(df.head(10), use_container_width=True)

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Rows",         f"{len(df):,}")
    m2.metric("Columns",      len(df.columns))
    m3.metric("Numeric Cols", len(df.select_dtypes(include="number").columns))
    m4.metric("Text Cols",    len(df.select_dtypes(exclude="number").columns))

    # Show column metadata panel if available from a monitoring framework
    if ws:
        col_meta = load_column_metadata(ws["path"])
        if col_meta:
            render_column_metadata_panel(col_meta, selected_cols=list(df.columns))

    st.markdown("### Column Summary")
    summary = pd.DataFrame({
        "Column":   df.columns.tolist(),
        "Type":     [str(df[c].dtype) for c in df.columns],
        "Non-Null": [df[c].notna().sum() for c in df.columns],
        "Null %":   [round(df[c].isna().mean() * 100, 1) for c in df.columns],
        "Unique":   [df[c].nunique() for c in df.columns],
        "Sample":   [str(df[c].dropna().iloc[0]) if df[c].notna().any() else "—" for c in df.columns],
    })
    st.dataframe(summary, use_container_width=True, hide_index=True)
else:
    st.info("Upload a file, connect a Google Sheet, or select a workspace data source to begin.")
