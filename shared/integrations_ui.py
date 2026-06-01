"""
Integrations UI — self-service setup for Google, BigQuery, and Apps Script.
No Docker rebuild or GCP console required after initial deployment.
"""
import json
import streamlit as st


# ── Sidebar status chips ──────────────────────────────────────────────────────

def render_integration_sidebar() -> None:
    from .google_svc     import credentials_available
    from .bigquery_svc   import bq_available, bq_connection_info
    from .appscript_svc  import appscript_available

    st.markdown("---")
    st.markdown("""
    <div style="font-size:0.70rem;font-weight:700;text-transform:uppercase;
                letter-spacing:0.08em;color:#475569;margin-bottom:6px;">
        Integrations
    </div>""", unsafe_allow_html=True)

    def _dot(ok: bool, label: str):
        color = "#059669" if ok else "#94A3B8"
        icon  = "●" if ok else "○"
        st.markdown(
            f'<div style="font-size:0.75rem;color:#CBD5E1;margin:2px 0;">'
            f'<span style="color:{color};font-size:0.6rem;">{icon}</span>&nbsp;{label}</div>',
            unsafe_allow_html=True,
        )

    _dot(credentials_available(), "Google Workspace")

    if bq_available():
        info = bq_connection_info()
        _dot(info["connected"], f"BigQuery ({info.get('project','—')[:12]})" if info["connected"] else "BigQuery — error")
    else:
        _dot(False, "BigQuery")

    _dot(appscript_available(), "Apps Script")


# ── Full integrations setup page ──────────────────────────────────────────────

def render_integrations_page() -> None:
    try:
        from .theme import page_header
        page_header("Integrations Setup",
                    subtitle="Connect Google Workspace, BigQuery, and Apps Script — no coding required",
                    icon="🔗")
    except Exception:
        st.markdown("# ⚙️ Integrations Setup")
        st.caption("Configure all integrations from here — no coding or server access needed.")

    tab_google, tab_bq, tab_appscript, tab_ai, tab_status = st.tabs([
        "🔑 Google Workspace",
        "☁️ BigQuery",
        "📜 Apps Script",
        "🤖 AI Assistant",
        "📊 Status",
    ])

    with tab_google:
        _render_google_tab()

    with tab_bq:
        _render_bigquery_tab()

    with tab_appscript:
        _render_appscript_tab()

    with tab_ai:
        _render_ai_tab()

    with tab_status:
        _render_status_tab()


# ── Google Workspace tab ──────────────────────────────────────────────────────

def _render_google_tab():
    from .credentials_manager import get_google_sa, save_google_sa, clear_google_sa
    from .google_svc import credentials_available

    st.markdown("### Google Workspace Setup")
    st.markdown(
        "This connects PMU Tools to **Google Sheets**, **Google Drive**, and **Google Forms**. "
        "You need a Service Account JSON key from your Google Cloud project."
    )

    # Current status
    sa = get_google_sa()
    if sa:
        st.success(f"✅ Google credentials configured — Project: **{sa.get('project_id')}** | "
                   f"Account: `{sa.get('client_email')}`")
        if st.button("🗑 Remove Google Credentials", key="rm_google"):
            clear_google_sa()
            st.rerun()
        st.markdown("---")

    # How to get the JSON key
    with st.expander("📋 How to get your Service Account JSON key (click to expand)", expanded=not bool(sa)):
        st.markdown("""
**Step 1 — Open Google Cloud Console**
Go to [console.cloud.google.com](https://console.cloud.google.com) and sign in.

**Step 2 — Select your project**
At the top, click the project dropdown and select your project (e.g., `pmu-test-sourav`).

**Step 3 — Create a Service Account**
1. In the left menu, click **IAM & Admin → Service Accounts**
2. Click **+ Create Service Account**
3. Name it `pmu-tools-service`, click **Create and Continue**
4. Set Role to **Editor**, click **Continue**, then **Done**

**Step 4 — Download the JSON key**
1. Click on the service account you just created
2. Go to the **Keys** tab
3. Click **Add Key → Create new key**
4. Select **JSON**, click **Create**
5. A `.json` file downloads to your computer

**Step 5 — Open the JSON file**
Right-click the downloaded file → Open with **Notepad** (or any text editor)
Select all text (Ctrl+A), copy it (Ctrl+C)

**Step 6 — Paste it below**
        """)

    st.markdown("### Paste your Service Account JSON key")
    sa_input = st.text_area(
        "Paste the entire contents of the downloaded JSON file here",
        height=220,
        placeholder='{\n  "type": "service_account",\n  "project_id": "your-project",\n  ...\n}',
        key="sa_json_input",
    )

    col_save, col_test = st.columns([1, 1])

    with col_save:
        if st.button("💾 Save Google Credentials", type="primary", use_container_width=True, key="save_google"):
            if not sa_input.strip():
                st.error("Please paste your JSON key before saving.")
            else:
                try:
                    sa_dict = json.loads(sa_input.strip())
                    required = ["type", "project_id", "private_key", "client_email"]
                    missing  = [k for k in required if k not in sa_dict]
                    if missing:
                        st.error(f"This JSON is missing required fields: {missing}. "
                                 "Make sure you copied the entire file.")
                    elif sa_dict.get("type") != "service_account":
                        st.error("This is not a service account JSON key. "
                                 "Please download the key from IAM → Service Accounts → Keys tab.")
                    else:
                        save_google_sa(sa_dict)
                        st.success(f"✅ Google credentials saved — Project: {sa_dict['project_id']}")
                        st.rerun()
                except json.JSONDecodeError as e:
                    st.error(f"Invalid JSON. Make sure you copied the entire file contents. Error: {e}")

    with col_test:
        if st.button("🔌 Test Connection", use_container_width=True, key="test_google"):
            if credentials_available():
                try:
                    from .google_svc import build_service
                    svc = build_service("sheets", "v4")
                    st.success("✅ Google Sheets API connected successfully.")
                except Exception as exc:
                    st.error(f"Connection failed: {exc}")
            else:
                st.warning("No credentials configured yet.")

    # Share instruction
    if sa:
        st.info(
            f"**Important:** For PMU Tools to read or write a Google Sheet, "
            f"share that sheet with the service account email:\n\n"
            f"`{sa.get('client_email')}`\n\n"
            "Open the Google Sheet → Share → paste this email → set Editor → Done."
        )


# ── BigQuery tab ──────────────────────────────────────────────────────────────

def _render_bigquery_tab():
    from .credentials_manager import get_bigquery_config, save_bigquery_config, clear_bigquery_config, get_google_sa
    from .bigquery_svc import bq_available, bq_connection_info

    st.markdown("### BigQuery Setup")
    st.markdown(
        "BigQuery lets PMU Tools load and query very large datasets (100,000+ rows) "
        "directly from Google Cloud — without downloading them to Excel first."
    )

    # Google SA must be configured first
    if not get_google_sa():
        st.warning("⚠️ Set up Google Workspace credentials first (Google Workspace tab), "
                   "then come back here to configure BigQuery.")
        return

    # Current status
    cfg = get_bigquery_config()
    if cfg and cfg.get("project_id"):
        info = bq_connection_info()
        if info["connected"]:
            st.success(f"✅ BigQuery connected — Project: **{info['project']}** | "
                       f"Default dataset: **{cfg.get('dataset_id', '—')}**")
        else:
            st.error(f"❌ BigQuery not reachable — {info.get('error')}")
        if st.button("🗑 Remove BigQuery Config", key="rm_bq"):
            clear_bigquery_config()
            st.rerun()
        st.markdown("---")

    st.markdown("### Enter your BigQuery details")

    with st.expander("📋 How to find your GCP Project ID and create a dataset", expanded=not bool(cfg)):
        st.markdown("""
**GCP Project ID**
- Go to [console.cloud.google.com](https://console.cloud.google.com)
- Your Project ID appears at the top of the page (e.g., `pmu-test-sourav`)
- It is also in the service account JSON under `"project_id"`

**BigQuery Dataset ID**
- Go to [console.cloud.google.com/bigquery](https://console.cloud.google.com/bigquery)
- In the Explorer panel on the left, click the **three dots ⋮** next to your project name
- Click **Create dataset**
- Set Dataset ID to `pmu_data`, Location to `asia-south1` (Mumbai), click **Create**
- The Dataset ID is what you enter below (e.g., `pmu_data`)
        """)

    c1, c2 = st.columns(2)
    project_id = c1.text_input(
        "GCP Project ID",
        value=cfg.get("project_id", "") if cfg else "",
        placeholder="e.g. pmu-test-sourav",
        key="bq_project",
    )
    dataset_id = c2.text_input(
        "Default Dataset ID",
        value=cfg.get("dataset_id", "pmu_data") if cfg else "pmu_data",
        placeholder="e.g. pmu_data",
        key="bq_dataset",
    )

    col_save, col_test = st.columns([1, 1])

    with col_save:
        if st.button("💾 Save BigQuery Config", type="primary", use_container_width=True, key="save_bq"):
            if not project_id.strip():
                st.error("Project ID is required.")
            else:
                save_bigquery_config(project_id.strip(), dataset_id.strip())
                st.success(f"✅ BigQuery config saved — Project: {project_id}")
                st.rerun()

    with col_test:
        if st.button("🔌 Test BigQuery Connection", use_container_width=True, key="test_bq"):
            if bq_available():
                with st.spinner("Connecting to BigQuery..."):
                    info = bq_connection_info()
                if info["connected"]:
                    st.success(f"✅ BigQuery connected — Project: {info['project']}")
                else:
                    st.error(f"Connection failed: {info.get('error')}\n\n"
                             "Check that the service account has **BigQuery Data Viewer** and "
                             "**BigQuery Job User** roles in GCP IAM.")
            else:
                st.warning("Save your BigQuery config first.")


# ── Apps Script tab ───────────────────────────────────────────────────────────

def _render_appscript_tab():
    from .credentials_manager import get_appscript_config, save_appscript_config, clear_appscript_config
    from .appscript_svc import appscript_available, appscript_ping

    st.markdown("### Apps Script Aggregator Setup")
    st.markdown(
        "The Apps Script Aggregator lets PMU Tools automatically group and sum data "
        "in a Google Sheet — without downloading it. You set it up once; "
        "then any PMU user can trigger aggregations from the Generate tab."
    )

    # Current status
    cfg = get_appscript_config()
    if cfg and cfg.get("web_app_url"):
        st.success(f"✅ Apps Script configured — URL: `{cfg['web_app_url'][:60]}...`")
        if st.button("🗑 Remove Apps Script Config", key="rm_appscript"):
            clear_appscript_config()
            st.rerun()
        st.markdown("---")

    with st.expander("📋 How to deploy the Apps Script web app (click to expand)", expanded=not bool(cfg)):
        st.markdown("""
**Step 1 — Open Google Apps Script**
Go to [script.google.com](https://script.google.com) and click **New project**.

**Step 2 — Paste the aggregator code**
- Delete all existing code in the editor.
- Copy the entire contents of the file `templates/apps_script_aggregator.js` from your PMU Tools project folder.
- Paste it into the Apps Script editor.
- Click **File → Save** and name the project `PMU Aggregator`.

**Step 3 — Set a security password**
- Click the **gear icon ⚙️** (Project Settings) in the left sidebar.
- Scroll to **Script Properties** → click **Add script property**.
- Property name: `PMU_SECRET` | Value: choose any password (e.g., `OsepaPMU@2026`)
- Click **Save**. Note this password — you will enter it below.

**Step 4 — Deploy as Web App**
- Click **Deploy** (top right) → **New deployment**.
- Click the **gear ⚙️** → select **Web app**.
- Set: Execute as = **Me** | Who has access = **Anyone**.
- Click **Deploy** → authorise when prompted → click **Allow**.
- Copy the **Web App URL** (ends in `/exec`).

**Step 5 — Paste the URL and password below.**
        """)

    st.markdown("### Enter your Apps Script details")

    url = st.text_input(
        "Apps Script Web App URL",
        value=cfg.get("web_app_url", "") if cfg else "",
        placeholder="https://script.google.com/macros/s/AKfycby.../exec",
        key="as_url",
    )
    secret = st.text_input(
        "Shared Secret (the PMU_SECRET password you set)",
        value=cfg.get("shared_secret", "") if cfg else "",
        type="password",
        placeholder="e.g. OsepaPMU@2026",
        key="as_secret",
    )

    col_save, col_test = st.columns([1, 1])

    with col_save:
        if st.button("💾 Save Apps Script Config", type="primary", use_container_width=True, key="save_as"):
            if not url.strip():
                st.error("Web App URL is required.")
            elif not url.strip().startswith("https://script.google.com"):
                st.error("This does not look like a valid Apps Script URL. "
                         "It should start with https://script.google.com/macros/s/...")
            else:
                save_appscript_config(url.strip(), secret.strip())
                st.success("✅ Apps Script config saved.")
                st.rerun()

    with col_test:
        if st.button("🔌 Ping Apps Script", use_container_width=True, key="test_as"):
            if appscript_available():
                with st.spinner("Pinging Apps Script..."):
                    try:
                        result = appscript_ping()
                        if result.get("status") == "ok":
                            st.success(f"✅ {result.get('message', 'Apps Script is running.')}")
                        else:
                            st.error(f"Apps Script returned an error: {result.get('error')}\n\n"
                                     "Check that the PMU_SECRET script property matches the password entered above.")
                    except Exception as exc:
                        st.error(f"Could not reach Apps Script: {exc}\n\n"
                                 "Verify the Web App URL is correct and the deployment is active.")
            else:
                st.warning("Save your Apps Script config first.")


# ── AI Assistant tab ─────────────────────────────────────────────────────────

def _render_ai_tab():
    from .ai_assistant import (
        get_anthropic_key, save_anthropic_key,
        get_ai_password, save_ai_password,
        ai_available, ai_password_set,
    )

    st.markdown("### AI Assistant Configuration")
    st.markdown("Configure the Claude-powered AI assistant. Set an API key (admin only) and a team access password.")

    # Current status
    is_ready = ai_available() and ai_password_set()
    if is_ready:
        st.success("✅ AI Assistant is active. Users can access it with the configured password.")
    else:
        st.warning("⚠️ AI Assistant is not fully configured yet.")

    st.markdown("---")

    # API Key section
    st.markdown("#### Anthropic API Key")
    st.caption("Get your key at console.anthropic.com → API Keys. Never share this — it stays hidden from users.")

    current_key = get_anthropic_key()
    key_display = f"`sk-ant-...{current_key[-6:]}`" if current_key else "Not configured"
    st.caption(f"Current key: {key_display}")

    with st.form("ai_key_form"):
        new_key = st.text_input("New API Key", type="password", placeholder="sk-ant-api03-...")
        if st.form_submit_button("💾 Update API Key", type="primary"):
            if not new_key.strip():
                st.error("Key cannot be empty.")
            elif not new_key.strip().startswith("sk-ant-"):
                st.error("Not a valid Anthropic API key. It must start with 'sk-ant-'.")
            else:
                save_anthropic_key(new_key.strip())
                st.success("✅ API key updated.")
                st.rerun()

    st.markdown("---")

    # Password section
    st.markdown("#### Team Access Password")
    st.caption("This is what your team enters to use the AI Assistant. Share it with your PMU team.")

    current_pw = get_ai_password()
    if current_pw:
        st.caption(f"Password is set ({len(current_pw)} characters).")
    else:
        st.caption("No password set yet.")

    with st.form("ai_pw_form"):
        pw1 = st.text_input("New Access Password", type="password", placeholder="e.g. PMU@2026")
        pw2 = st.text_input("Confirm Password",    type="password")
        if st.form_submit_button("💾 Update Password", type="primary"):
            if not pw1.strip():
                st.error("Password cannot be empty.")
            elif pw1 != pw2:
                st.error("Passwords do not match.")
            elif len(pw1.strip()) < 4:
                st.error("Password must be at least 4 characters.")
            else:
                save_ai_password(pw1.strip())
                st.success("✅ Access password updated. Share the new password with your team.")
                st.rerun()

    st.info("**Security:** The API key is stored on the server and never shown to users. Users only enter the access password, which grants them a session-level token to use the assistant.")


# ── Status tab ────────────────────────────────────────────────────────────────

def _render_status_tab():
    from .credentials_manager import integration_summary
    from .google_svc    import credentials_available
    from .bigquery_svc  import bq_available, bq_connection_info
    from .appscript_svc import appscript_available

    st.markdown("### Integration Status")

    summary = integration_summary()

    # Google
    google_ok = credentials_available()
    st.markdown(f"{'✅' if google_ok else '🔴'} **Google Workspace**")
    if google_ok and summary["google"]["configured"]:
        st.caption(f"Project: {summary['google']['project']} | Account: {summary['google']['email']}")
    elif not google_ok:
        st.caption("Not configured — go to Google Workspace tab to set up.")

    st.markdown("---")

    # BigQuery
    bq_ok = bq_available()
    if bq_ok:
        info = bq_connection_info()
        connected = info["connected"]
        st.markdown(f"{'✅' if connected else '⚠️'} **BigQuery**")
        if connected:
            st.caption(f"Project: {info['project']} | Dataset: {summary['bigquery'].get('dataset')}")
        else:
            st.caption(f"Configured but not reachable — {info.get('error')}")
    else:
        st.markdown("🔴 **BigQuery**")
        st.caption("Not configured — go to BigQuery tab to set up.")

    st.markdown("---")

    # Apps Script
    as_ok = appscript_available()
    st.markdown(f"{'✅' if as_ok else '🔴'} **Apps Script Aggregator**")
    if as_ok and summary["apps_script"]["configured"]:
        st.caption(f"URL: {summary['apps_script']['url'][:60]}...")
    elif not as_ok:
        st.caption("Not configured — go to Apps Script tab to set up.")

    st.markdown("---")

    # AI Assistant
    from .ai_assistant import ai_available, ai_password_set
    ai_ok = ai_available() and ai_password_set()
    st.markdown(f"{'✅' if ai_ok else '🔴'} **AI Assistant**")
    if ai_ok:
        st.caption("Active — team can access with the configured password.")
    elif ai_available() and not ai_password_set():
        st.caption("API key set but no access password — go to AI Assistant tab.")
    else:
        st.caption("Not configured — go to AI Assistant tab to set up.")

    st.markdown("---")
    st.markdown("### Quick Test")

    c1, c2, c3 = st.columns(3)

    with c1:
        if st.button("Test Google Sheets", use_container_width=True, key="st_google"):
            if google_ok:
                try:
                    from .google_svc import build_service
                    build_service("sheets", "v4")
                    st.success("✅ Google Sheets OK")
                except Exception as e:
                    st.error(f"Failed: {e}")
            else:
                st.warning("Not configured.")

    with c2:
        if st.button("Test BigQuery", use_container_width=True, key="st_bq"):
            if bq_ok:
                info = bq_connection_info()
                st.success(f"✅ BigQuery OK — {info['project']}") if info["connected"] else st.error(info.get("error"))
            else:
                st.warning("Not configured.")

    with c3:
        if st.button("Ping Apps Script", use_container_width=True, key="st_as"):
            if as_ok:
                from .appscript_svc import appscript_ping
                try:
                    r = appscript_ping()
                    st.success("✅ Apps Script OK") if r.get("status") == "ok" else st.error(r.get("error"))
                except Exception as e:
                    st.error(str(e))
            else:
                st.warning("Not configured.")


# ── BigQuery Upload tab (used on Upload pages) ────────────────────────────────

def render_bq_upload_tab(set_df_callback) -> None:
    from .bigquery_svc import (
        bq_available, bq_connection_info,
        bq_list_datasets, bq_list_tables,
        bq_table_to_df, bq_query,
    )

    if not bq_available():
        st.info("BigQuery is not configured. Go to the **Integrations** page to set it up.")
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
                limit = st.number_input("Row limit (0 = all rows)", min_value=0, value=10000, key="bq_ul_lim")
                if st.button("Load Table", type="primary", key="bq_ul_load"):
                    with st.spinner("Loading from BigQuery..."):
                        df = bq_table_to_df(dataset, table, limit=limit or None)
                    st.success(f"Loaded {len(df):,} rows × {len(df.columns)} columns from BigQuery.")
                    set_df_callback(df, f"BigQuery: {dataset}.{table}")
        except Exception as exc:
            st.error(f"Error listing datasets: {exc}")

    else:
        sql = st.text_area("SQL Query", height=150,
                           placeholder="SELECT district, SUM(enrolment) AS total\nFROM `project.dataset.table`\nGROUP BY district",
                           key="bq_ul_sql")
        if st.button("Run Query", type="primary", key="bq_ul_run"):
            if sql.strip():
                with st.spinner("Running query on BigQuery..."):
                    try:
                        df = bq_query(sql.strip())
                        st.success(f"Query returned {len(df):,} rows × {len(df.columns)} columns.")
                        set_df_callback(df, "BigQuery: custom query")
                    except Exception as exc:
                        st.error(f"Query failed: {exc}")


# ── BigQuery push section (used on Generate pages) ────────────────────────────

def render_bq_push_section(df, artifact_id: str, project_code: str) -> None:
    from .bigquery_svc import bq_available, bq_list_datasets, bq_push_df

    if not bq_available():
        st.info("BigQuery not configured — go to Integrations to set it up.")
        return

    st.markdown("#### Push to BigQuery")
    try:
        datasets = bq_list_datasets()
    except Exception:
        datasets = []

    c1, c2, c3 = st.columns(3)
    dataset = c1.selectbox("Dataset", datasets or ["pmu_data"], key=f"bq_push_ds_{artifact_id}")
    table   = c2.text_input("Table name", value=f"{project_code}_output".lower(), key=f"bq_push_tbl_{artifact_id}")
    mode    = c3.selectbox("Write mode", ["append", "replace"], key=f"bq_push_mode_{artifact_id}")

    if st.button("Push to BigQuery", key=f"bq_push_btn_{artifact_id}"):
        with st.spinner("Writing to BigQuery..."):
            try:
                bq_push_df(df, dataset, table, mode=mode)
                st.success(f"✅ {len(df):,} rows written to `{dataset}.{table}`.")
            except Exception as exc:
                st.error(f"Push failed: {exc}")


# ── Apps Script section (used on Generate pages) ──────────────────────────────

def render_appscript_section() -> None:
    from .appscript_svc import appscript_available, appscript_aggregate

    if not appscript_available():
        st.info("Apps Script not configured — go to Integrations to set it up.")
        return

    st.markdown("#### Apps Script Aggregator")
    src_url = st.text_input("Source sheet URL (raw data)", key="as_src")
    tgt_url = st.text_input("Target sheet URL (aggregated output)", key="as_tgt")
    c1, c2, c3 = st.columns(3)
    group_cols  = c1.text_input("Group-by columns (comma-separated)", placeholder="District,Block", key="as_grp")
    metric_cols = c2.text_input("Metric columns (comma-separated)", placeholder="Enrolment,Score", key="as_met")
    agg_func    = c3.selectbox("Function", ["SUM", "AVERAGE", "COUNT", "MIN", "MAX"], key="as_fn")

    if st.button("Run Aggregator", key="as_run"):
        gc = [c.strip() for c in group_cols.split(",") if c.strip()]
        mc = [c.strip() for c in metric_cols.split(",") if c.strip()]
        if not src_url or not tgt_url or not gc or not mc:
            st.error("Please fill in all fields before running.")
        else:
            with st.spinner("Running aggregation via Apps Script..."):
                try:
                    result = appscript_aggregate(src_url, tgt_url, gc, mc, agg_func)
                    if result.get("status") == "ok":
                        st.success(f"✅ Aggregation complete — {result.get('rows_written', '?')} rows written to target sheet.")
                    else:
                        st.error(f"Aggregation failed: {result.get('error')}")
                except Exception as exc:
                    st.error(f"Error: {exc}")
