"""Streamlit UI components for Google / BigQuery / Apps Script integrations."""
import streamlit as st


# ── Sidebar status ────────────────────────────────────────────────────────────

def render_integration_sidebar() -> None:
    """Compact integration status chips for app sidebars."""
    from .google_svc    import credentials_available
    from .bigquery_svc  import bq_available, bq_connection_info
    from .appscript_svc import appscript_available

    st.markdown("---")
    st.markdown("**Integrations**")
    st.caption("✅ Google" if credentials_available() else "🔴 Google — not configured")

    if bq_available():
        info = bq_connection_info()
        label = f"✅ BigQuery ({info.get('project', '')})" if info["connected"] \
                else f"⚠️ BigQuery — {str(info.get('error', ''))[:28]}"
        st.caption(label)
    else:
        st.caption("🔴 BigQuery — not configured")

    st.caption("✅ Apps Script" if appscript_available() else "🔴 Apps Script — not configured")


# ── BigQuery upload tab ───────────────────────────────────────────────────────

def render_bq_upload_tab(set_df_callback) -> None:
    """
    BigQuery data source tab for Upload pages.
    set_df_callback(df, source_label) is called when the user loads data.
    """
    from .bigquery_svc import (
        bq_available, bq_connection_info,
        bq_list_datasets, bq_list_tables,
        bq_table_to_df, bq_query,
    )

    if not bq_available():
        st.info("BigQuery is not configured. Add `[gcp_service_account]` and `[bigquery]` to your Streamlit secrets.")
        with st.expander("How to configure BigQuery"):
            st.code("""
# .streamlit/secrets.toml
[gcp_service_account]
type         = "service_account"
project_id   = "your-project"
private_key  = "-----BEGIN RSA PRIVATE KEY-----\\n...\\n-----END RSA PRIVATE KEY-----\\n"
client_email = "service@your-project.iam.gserviceaccount.com"
# ... (all fields from your service account JSON key)

[bigquery]
project_id = "your-project"
dataset_id = "pmu_data"
            """, language="toml")
        return

    info = bq_connection_info()
    if not info["connected"]:
        st.error(f"BigQuery connection failed: {info.get('error')}")
        return

    st.success(f"Connected — project: **{info['project']}**")
    mode = st.radio("Load mode", ["Browse table", "Custom SQL query"], horizontal=True, key="bq_ul_mode")

    if mode == "Browse table":
        try:
            datasets = bq_list_datasets()
            if not datasets:
                st.warning("No datasets found in this project.")
                return
            c1, c2 = st.columns(2)
            dataset = c1.selectbox("Dataset", datasets, key="bq_ul_ds")
            tables  = bq_list_tables(dataset) if dataset else []
            table   = c2.selectbox("Table", tables, key="bq_ul_tbl") if tables else None

            if table:
                limit = st.number_input(
                    "Row limit (0 = all rows — use with caution for large tables)",
                    min_value=0, value=10000, step=1000, key="bq_ul_limit",
                )
                pb1, pb2 = st.columns(2)
                if pb1.button("Preview (5 rows)", use_container_width=True, key="bq_ul_prev"):
                    with st.spinner("Fetching preview…"):
                        try:
                            st.dataframe(bq_table_to_df(dataset, table, limit=5), use_container_width=True)
                            st.caption(f"Full load: {limit:,} rows" if limit else "Full load — no row limit set")
                        except Exception as exc:
                            st.error(f"Preview error: {exc}")

                if pb2.button("Load from BigQuery", type="primary", use_container_width=True, key="bq_ul_load"):
                    with st.spinner(f"Loading `{dataset}.{table}`…"):
                        try:
                            df = bq_table_to_df(dataset, table, limit=limit if limit > 0 else None)
                            set_df_callback(df, f"BigQuery: {dataset}.{table}")
                            st.success(f"Loaded **{len(df):,} rows × {len(df.columns)} cols**")
                            st.rerun()
                        except Exception as exc:
                            st.error(f"Load failed: {exc}")
        except Exception as exc:
            st.error(f"BigQuery error: {exc}")

    else:
        sql = st.text_area(
            "SQL Query",
            value="SELECT * FROM `project.dataset.table` LIMIT 1000",
            height=120, key="bq_ul_sql",
        )
        if st.button("Run Query", type="primary", use_container_width=True, key="bq_ul_run"):
            with st.spinner("Running query on BigQuery…"):
                try:
                    df = bq_query(sql)
                    set_df_callback(df, "BigQuery: Custom SQL")
                    st.success(f"Loaded **{len(df):,} rows × {len(df.columns)} cols**")
                    st.rerun()
                except Exception as exc:
                    st.error(f"Query failed: {exc}")


# ── BigQuery push (Generate pages) ────────────────────────────────────────────

def render_bq_push_section(df, artifact_id: str, project_code: str) -> None:
    """Render BigQuery push section on Generate pages."""
    from .bigquery_svc import bq_available, bq_list_datasets, bq_push_df

    if not bq_available():
        st.info("BigQuery not configured — add `[gcp_service_account]` and `[bigquery]` to secrets to enable.")
        return

    try:
        datasets = bq_list_datasets()
        bq_ds    = st.selectbox("Target Dataset", datasets, key=f"bq_ps_ds_{artifact_id}")
        bq_tbl   = st.text_input("Target Table Name", value=f"{project_code.lower()}_output",
                                  key=f"bq_ps_tbl_{artifact_id}")
        bq_mode  = st.radio("Write mode", ["append", "replace"], horizontal=True,
                             key=f"bq_ps_mode_{artifact_id}")
        if st.button("☁ Push to BigQuery", use_container_width=True, key=f"bq_ps_btn_{artifact_id}"):
            with st.spinner(f"Writing {len(df):,} rows to `{bq_ds}.{bq_tbl}`…"):
                bq_push_df(df, bq_ds, bq_tbl, mode=bq_mode)
            st.success(f"Written to `{bq_ds}.{bq_tbl}` ({bq_mode} mode).")
    except Exception as exc:
        st.error(f"BigQuery push failed: {exc}")


# ── Apps Script trigger (Generate pages) ──────────────────────────────────────

def render_appscript_section() -> None:
    """Render Apps Script aggregator trigger on Generate pages."""
    from .appscript_svc import appscript_available, appscript_aggregate, appscript_ping

    if not appscript_available():
        st.info("Apps Script not configured — add `[apps_script]` to secrets to enable.")
        with st.expander("Setup guide"):
            st.markdown("""
1. Open [script.google.com](https://script.google.com) → New Project
2. Paste the contents of `templates/apps_script_aggregator.js`
3. **Project Settings → Script Properties** → Add: `PMU_SECRET = your-token`
4. **Deploy → New deployment → Web App** (Execute as: Me · Access: Anyone)
5. Copy the Web App URL, then add to `secrets.toml`:

```toml
[apps_script]
web_app_url   = "https://script.google.com/macros/s/.../exec"
shared_secret = "your-pmu-secret-token"
```
            """)
        return

    src_url  = st.text_input("Source Sheet URL (raw data)",          key="as_src_url")
    tgt_url  = st.text_input("Target Sheet URL (aggregated output)", key="as_tgt_url")
    c1, c2   = st.columns(2)
    grp_str  = c1.text_input("Group-by columns (comma-separated)", value="District,Block", key="as_grp")
    met_str  = c2.text_input("Metric columns (comma-separated)",   key="as_met")
    agg_func = st.selectbox("Aggregation", ["SUM", "AVERAGE", "COUNT", "MIN", "MAX"], key="as_fn")

    b1, b2 = st.columns(2)
    if b1.button("▶ Trigger Aggregation Now", type="primary", use_container_width=True, key="as_trig"):
        group_cols  = [c.strip() for c in grp_str.split(",")  if c.strip()]
        metric_cols = [c.strip() for c in met_str.split(",")  if c.strip()]
        if not src_url.strip() or not tgt_url.strip():
            st.warning("Both Source and Target Sheet URLs are required.")
        elif not metric_cols:
            st.warning("Enter at least one metric column.")
        else:
            with st.spinner("Calling Apps Script aggregator…"):
                try:
                    result = appscript_aggregate(src_url.strip(), tgt_url.strip(),
                                                 group_cols, metric_cols, agg_func)
                    if result.get("status") == "ok":
                        st.success(f"Complete — {result.get('rows_written', 0)} rows written to target sheet.")
                    else:
                        st.error(f"Aggregation failed: {result.get('error', 'Unknown error')}")
                except Exception as exc:
                    st.error(f"Error: {exc}")

    if b2.button("Ping Apps Script", use_container_width=True, key="as_ping"):
        with st.spinner("Pinging…"):
            try:
                r = appscript_ping()
                st.success(r.get("message", "Apps Script is live."))
            except Exception as exc:
                st.error(f"Ping failed: {exc}")


# ── Full integrations settings page ──────────────────────────────────────────

def render_integrations_page() -> None:
    """Full integrations page — call from each app's _Integrations.py."""
    from .google_svc    import credentials_available
    from .bigquery_svc  import bq_available, bq_connection_info, bq_list_datasets
    from .appscript_svc import appscript_available, appscript_status

    st.markdown("# 🔗 Integrations")
    st.caption("Google account · BigQuery · Apps Script — status and setup guide")
    st.markdown("---")

    # ── Google ────────────────────────────────────────────────────────────────
    st.markdown("### Google Workspace")
    st.caption("Enables: Google Sheets · Google Drive · Google Forms across all apps")
    if credentials_available():
        st.success("Google credentials are active. Sheets, Drive, and Forms are available.")
    else:
        st.warning("Google credentials not configured.")
        st.markdown("""
Add `[gcp_service_account]` to `.streamlit/secrets.toml`:

```toml
[gcp_service_account]
type                        = "service_account"
project_id                  = "your-gcp-project"
private_key_id              = "..."
private_key                 = "-----BEGIN RSA PRIVATE KEY-----\\nMIIE...\\n-----END RSA PRIVATE KEY-----\\n"
client_email                = "pmu-service@your-project.iam.gserviceaccount.com"
client_id                   = "..."
auth_uri                    = "https://accounts.google.com/o/oauth2/auth"
token_uri                   = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url        = "https://www.googleapis.com/robot/v1/metadata/x509/..."
```
        """)

    st.markdown("---")

    # ── BigQuery ──────────────────────────────────────────────────────────────
    st.markdown("### BigQuery")
    st.caption("Enables: load tables directly, run SQL queries, push outputs back — handles 5 lakh+ rows")
    if bq_available():
        info = bq_connection_info()
        if info["connected"]:
            st.success(f"Connected — project: **{info['project']}**")
            try:
                datasets = bq_list_datasets()
                st.markdown(f"Available datasets: `{'`, `'.join(datasets[:15])}`")
            except Exception as exc:
                st.warning(f"Could not list datasets: {exc}")
        else:
            st.error(f"Configured but connection failed: {info.get('error')}")
    else:
        st.warning("BigQuery not configured.")
        st.markdown("""
Same service account as Google — just add BigQuery roles in IAM:

```toml
[bigquery]
project_id = "your-gcp-project"
dataset_id = "pmu_data"
```

**Required IAM roles:** BigQuery Data Viewer · BigQuery Job User · BigQuery Data Editor
        """)

    st.markdown("---")

    # ── Apps Script ───────────────────────────────────────────────────────────
    st.markdown("### Apps Script Aggregator")
    st.caption("Enables: nightly Google Sheets aggregation triggered from any Generate page")
    info = appscript_status()
    if info["connected"]:
        st.success(f"Configured: `{info['url'][:65]}…`")
    else:
        st.warning("Apps Script not configured.")
        st.markdown("""
**Setup steps:**
1. Open [script.google.com](https://script.google.com) → New Project
2. Paste contents of `templates/apps_script_aggregator.js` (in your PMU_Tools folder)
3. **Project Settings → Script Properties** → Add: `PMU_SECRET = your-secret-token`
4. **Deploy → New deployment → Web App**
   Execute as: **Me** · Who has access: **Anyone**
5. Add to `secrets.toml`:

```toml
[apps_script]
web_app_url   = "https://script.google.com/macros/s/.../exec"
shared_secret = "your-secret-token"
```

For nightly scheduling: run `setupNightlyTrigger()` once from inside the Apps Script editor.
        """)

    st.markdown("---")

    # ── Complete secrets template ─────────────────────────────────────────────
    st.markdown("### Complete `secrets.toml` Template")
    st.caption("Place at `PMU_Tools/.streamlit/secrets.toml` (local) or paste into Streamlit Cloud App Settings → Secrets")
    st.code("""
[gcp_service_account]
type                        = "service_account"
project_id                  = "your-gcp-project"
private_key_id              = "abc123..."
private_key                 = "-----BEGIN RSA PRIVATE KEY-----\\nMIIE...\\n-----END RSA PRIVATE KEY-----\\n"
client_email                = "pmu-service@your-project.iam.gserviceaccount.com"
client_id                   = "123456789"
auth_uri                    = "https://accounts.google.com/o/oauth2/auth"
token_uri                   = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url        = "https://www.googleapis.com/robot/v1/metadata/x509/..."

[bigquery]
project_id = "your-gcp-project"
dataset_id = "pmu_data"

[apps_script]
web_app_url   = "https://script.google.com/macros/s/AKfycbx.../exec"
shared_secret = "your-pmu-secret-token"
    """, language="toml")
