"""
PMU Tools AI Assistant — Claude-powered agentic assistant with password protection.
Admin sets: Anthropic API key + usage password (via Integrations page).
Users enter: usage password only (API key never exposed).
"""
from __future__ import annotations
import json
import streamlit as st

# ── Credential helpers ────────────────────────────────────────────────────────

def _cm():
    from .credentials_manager import _load, _save
    return _load, _save

def get_anthropic_key() -> str | None:
    load, _ = _cm()
    k = load().get("anthropic_api_key")
    if k:
        return k
    try:
        return st.secrets.get("anthropic_api_key") or st.secrets.get("ANTHROPIC_API_KEY")
    except Exception:
        return None

def save_anthropic_key(key: str) -> None:
    load, save = _cm()
    d = load(); d["anthropic_api_key"] = key.strip(); save(d)

def get_ai_password() -> str | None:
    load, _ = _cm()
    return load().get("ai_usage_password") or None

def save_ai_password(pw: str) -> None:
    load, save = _cm()
    d = load(); d["ai_usage_password"] = pw.strip(); save(d)

def ai_available() -> bool:
    return bool(get_anthropic_key())

def ai_password_set() -> bool:
    return bool(get_ai_password())

# ── System prompt ─────────────────────────────────────────────────────────────

SYSTEM_PROMPT = """You are the PMU Tools AI Assistant — built for Project Monitoring Unit (PMU) teams supporting education-sector programmes in India (primarily Odisha).

## Suite Overview
Six apps share one workspace system:

APP-001 Monitoring Builder: Design data collection frameworks. Pages: Workspace → Schema (inline table editor) → Form → Validation → KPIs → Package. Outputs: Excel template, Google Form, validation_config.json, kpi_config.json.

APP-002 Data Processing Studio: Clean, transform, validate raw data. Sources: file/Google Sheet/BigQuery. Pages: Upload → Clean → Transform → Map (fuzzy district matching) → Validate → Generate.

APP-003 Analytics Studio: Aggregate data, calculate KPIs, rank entities, trend analysis. Pages: Upload → Aggregate → KPIs → Analyse → Trends → Generate.

APP-004 Dashboard Studio: KPI cards + charts + tables → Excel dashboard. Pages: Upload → KPIs → Charts → Tables → Layout → Generate.

APP-005 Deliverable Studio: Reports in Excel/Word/PowerPoint/PDF, with district-split option. Pages: Upload → Report Details → Sections → Generate.

APP-006 Workflow Builder: Track implementation stages across districts/schools. Pages: Define → Tracker → Generate.

## UDISE+ Context
UDISE Code: 11-digit unique school identifier. Validation: `^\d{11}$`. Odisha has 30 districts. Key fields: udise_code, district_name, block_name, total_enrolment, attendance_pct. Sections: 1A School Profile, 1B Safety, 2 Physical Facilities, 3 Staff, 4 Students.

## Data Flows
Flow A: Upload CSV/XLSX file | Flow B: Google Sheet URL | Flow C: BigQuery SQL | Flow D: Apps Script aggregation trigger.

## Integrations
Google Workspace, BigQuery, Apps Script — all configurable from the Integrations page without any coding.

## Behaviour
- Be concise and direct. PMU users are busy field officers.
- When asked to DO something (create workspace, add field), use available tools.
- Reference exact page names: "APP-002 → Map tab".
- Use PMU language: district, block, enrolment, ATR, MOM, KPI, pendency.
- Never invent field names — ask if unsure.""".strip()

# ── Tools ─────────────────────────────────────────────────────────────────────

TOOLS = [
    {
        "name": "create_workspace",
        "description": "Create a new project workspace. Use when user asks to create/start a new project.",
        "input_schema": {
            "type": "object",
            "properties": {
                "name":         {"type": "string"},
                "project_code": {"type": "string"},
                "description":  {"type": "string"},
            },
            "required": ["name", "project_code"],
        },
    },
    {
        "name": "list_workspaces",
        "description": "List all existing workspaces.",
        "input_schema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "add_schema_field",
        "description": "Add a data field to the current monitoring framework schema.",
        "input_schema": {
            "type": "object",
            "properties": {
                "label":       {"type": "string"},
                "column_name": {"type": "string"},
                "data_type":   {"type": "string", "enum": ["text","integer","number","code","date","choice","boolean"]},
                "required":    {"type": "boolean"},
                "description": {"type": "string"},
                "choices":     {"type": "string"},
            },
            "required": ["label", "column_name", "data_type"],
        },
    },
    {
        "name": "get_current_schema",
        "description": "Show all fields currently defined in the active monitoring framework.",
        "input_schema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "suggest_validation_rules",
        "description": "Suggest validation rules based on current schema fields.",
        "input_schema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "get_help",
        "description": "Provide detailed step-by-step help for any PMU Tools feature or app.",
        "input_schema": {
            "type": "object",
            "properties": {
                "topic": {"type": "string"},
            },
            "required": ["topic"],
        },
    },
]

# ── Tool execution ────────────────────────────────────────────────────────────

def _execute_tool(name: str, inputs: dict, app_context: dict) -> str:
    if name == "list_workspaces":
        from shared.workspace import list_workspaces
        ws_list = list_workspaces()
        if not ws_list:
            return "No workspaces found."
        lines = ["**Existing workspaces:**"]
        for w in ws_list:
            tag = f" `[{w['user_tag']}]`" if w.get("user_tag") else ""
            lines.append(f"- **{w['name']}** ({w['project_code']}){tag} — {w.get('modified','')}")
        return "\n".join(lines)

    if name == "create_workspace":
        from shared.workspace import create_workspace
        try:
            ws = create_workspace(inputs["name"], inputs["project_code"],
                                  user_tag=app_context.get("user_tag",""),
                                  description=inputs.get("description",""))
            return f"✅ Workspace **{ws['name']}** created (project code: **{ws['project_code']}**). It is now visible in all apps."
        except FileExistsError:
            return f"A workspace named '{inputs['name']}' already exists."
        except Exception as e:
            return f"Could not create workspace: {e}"

    if name == "get_current_schema":
        job = app_context.get("job")
        if not job or not getattr(job, "fields", None):
            return "No fields defined yet in the active monitoring framework."
        lines = [f"**{len(job.fields)} fields:**"]
        for f in job.fields:
            badge = "🔑" if f.is_identifier else ("★" if f.required else "·")
            ch = f" — choices: {', '.join(f.choices[:4])}" if f.choices else ""
            lines.append(f"{badge} **{f.label}** `{f.name}` — {f.data_type}{ch}")
        return "\n".join(lines)

    if name == "add_schema_field":
        try:
            from engine import add_field, FieldDef
            choices = [c.strip() for c in inputs.get("choices","").split(",") if c.strip()]
            add_field(FieldDef(
                name=inputs["column_name"].replace(" ","_"),
                label=inputs["label"],
                data_type=inputs["data_type"],
                required=inputs.get("required", False),
                choices=choices,
                description=inputs.get("description",""),
            ))
            return f"✅ Field **{inputs['label']}** added. Refresh the Schema page to see it in the table."
        except Exception as e:
            return f"Could not add field: {e}"

    if name == "suggest_validation_rules":
        job = app_context.get("job")
        if not job or not getattr(job, "fields", None):
            return "No fields defined. Add schema fields first."
        lines = ["**Suggested rules for your schema:**"]
        for f in job.fields:
            if f.is_identifier:
                lines.append(f"- **{f.label}**: Required (Error) | Pattern — 11 digits if UDISE code")
            elif f.required:
                lines.append(f"- **{f.label}**: Required (Error)")
            if "enrolment" in f.name.lower() or "count" in f.name.lower():
                lines.append(f"- **{f.label}**: Range check 0–10000 (positive integers only)")
            if "pct" in f.name.lower() or "percent" in f.name.lower():
                lines.append(f"- **{f.label}**: Range check 0–100 (percentage bounds)")
            if f.data_type == "date":
                lines.append(f"- **{f.label}**: Type check — must be a valid date")
        return "\n".join(lines)

    if name == "get_help":
        topic = inputs.get("topic","").lower()
        if "app-002" in topic or "process" in topic or "clean" in topic:
            return "**APP-002 Data Processing Studio — workflow:**\n1. Upload → load file, Google Sheet URL, or BigQuery query\n2. Clean → fill nulls, deduplicate, strip whitespace, normalise case\n3. Transform → rename/merge/split columns, create calculations, filter rows\n4. Map → fuzzy-match district/block names to Odisha master list\n5. Validate → required, range, pattern, comparison, dependency rules\n6. Generate → download clean dataset + transformation log + validation report"
        if "fuzz" in topic or "map" in topic or "district" in topic:
            return "**Fuzzy Matching (APP-002 → Map tab):**\nMatches raw district/block names against the Odisha master list. Results: Exact (auto-accepted) → Variant (auto-accepted) → Fuzzy (review suggestion, approve/reject) → Unmatched (assign manually). Threshold slider: 80 = balanced, higher = stricter."
        if "bigquery" in topic or "bq" in topic:
            return "**BigQuery (Integrations tab):**\n1. Paste Service Account JSON in Integrations → Google Workspace tab\n2. Enter Project ID + Dataset ID in Integrations → BigQuery tab\n3. Upload tab → BigQuery tab → browse tables or write SQL\n4. After processing, Generate tab → Push to BigQuery to write results back"
        if "kpi" in topic:
            return "**KPI formulas (APP-003):**\n- Value: use column directly (e.g. avg_attendance = 78.5)\n- Ratio: numerator ÷ denominator (e.g. present / total)\n- Percentage: (numerator ÷ denominator) × 100\nSet target + interpretation (higher/lower is better). Composite score = weighted average."
        if "valid" in topic or "rule" in topic:
            return "**Validation rules (APP-002 → Validate):**\n- Required: column must not be blank\n- Type check: must be numeric / integer / date\n- Range: between min and max (e.g. attendance 0–100)\n- Pattern: UDISE = 11 digits, phone = 10 digits\n- Compare columns: col_a ≤ col_b (e.g. present ≤ enrolled)\n- Dependency: if A is filled, B must also be filled\n- Consistency: sum of parts must equal total"
        if "report" in topic or "app-005" in topic or "deliver" in topic:
            return "**APP-005 Deliverable Studio:**\n1. Upload data (file / Sheet / BigQuery)\n2. Report Details: title, author, formats (Excel / Word / PPT / PDF)\n3. Sections: add Table sections (aggregated data) or Narrative sections (free text)\n4. Generate: download all formats. Enable 'Split by Column' to get one report per district."
        if "workflow" in topic or "app-006" in topic or "atr" in topic or "track" in topic:
            return "**APP-006 Workflow Builder:**\n1. Define: add entity list (districts/schools) and stages (action points)\n2. Tracker: update each entity × stage status (Completed / In Progress / Pending / Overdue)\n3. Generate: download colour-coded tracker + pendency report\nPast due dates auto-upgrade Pending → Overdue."
        return "I can help with: APP-002 data processing, fuzzy matching, BigQuery setup, KPI formulas, validation rules, APP-005 reports, APP-006 workflow tracking. Which would you like details on?"

    return f"Action completed: {name}"

# ── Password gate ─────────────────────────────────────────────────────────────

def _render_password_gate() -> bool:
    """Show password form. Returns True if user is authenticated."""
    if st.session_state.get("ai_auth"):
        return True

    st.markdown("""
    <div class="ai-pw-card">
        <div class="ai-pw-icon">🤖</div>
        <h2 class="ai-pw-title">PMU AI Assistant</h2>
        <p class="ai-pw-sub">Enter the access password provided by your administrator to start using the assistant.</p>
    </div>
    """, unsafe_allow_html=True)

    col_l, col_c, col_r = st.columns([1, 2, 1])
    with col_c:
        with st.form("ai_pw_form", clear_on_submit=True):
            pw = st.text_input("Access Password", type="password",
                               placeholder="Team access password")
            submitted = st.form_submit_button("Unlock AI Assistant",
                                              type="primary", use_container_width=True)
        if submitted:
            correct = get_ai_password()
            if not correct:
                st.error("AI Assistant is not configured. Ask your administrator to set it up via Integrations → AI Assistant.")
            elif pw == correct:
                st.session_state["ai_auth"] = True
                st.rerun()
            else:
                st.error("Incorrect password. Please try again.")

    return False

# ── CSS ───────────────────────────────────────────────────────────────────────

_CSS = """
<style>
/* Chat bubbles */
[data-testid="stChatMessage"] {
    border-radius: 12px !important;
    padding: 14px 18px !important;
    margin-bottom: 6px !important;
    border: 1px solid #E2E8F0 !important;
    background: #FFFFFF !important;
    box-shadow: 0 1px 3px rgba(15,23,42,0.06) !important;
}

/* AI header banner */
.ai-header {
    background: linear-gradient(135deg, #0F172A 0%, #1A2744 50%, #0C2340 100%);
    border-radius: 16px;
    padding: 28px 36px;
    color: white;
    margin-bottom: 24px;
    position: relative;
    overflow: hidden;
    box-shadow: 0 8px 24px rgba(15,23,42,0.25);
}
.ai-header::before {
    content: '';
    position: absolute;
    top: -40px; right: -40px;
    width: 220px; height: 220px;
    background: radial-gradient(circle, rgba(5,150,105,0.18) 0%, transparent 70%);
    border-radius: 50%;
}
.ai-header h1 {
    margin: 0; font-size: 1.6rem; font-weight: 800;
    letter-spacing: -0.02em; position: relative; z-index: 1;
}
.ai-header p {
    margin: 8px 0 0; opacity: 0.72; font-size: 0.875rem;
    position: relative; z-index: 1;
}
.ai-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: rgba(5,150,105,0.2);
    border: 1px solid rgba(5,150,105,0.35);
    color: #6EE7B7;
    border-radius: 999px;
    padding: 4px 14px;
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    margin-top: 14px;
    position: relative; z-index: 1;
}

/* Tool call card */
.tool-card {
    background: #F0FDF9;
    border: 1px solid #A7F3D0;
    border-left: 4px solid #059669;
    border-radius: 8px;
    padding: 10px 16px;
    margin: 8px 0;
    font-size: 0.82rem;
    color: #064E3B;
    font-weight: 500;
}

/* Password gate card */
.ai-pw-card {
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 16px;
    padding: 40px 48px;
    max-width: 440px;
    margin: 64px auto;
    text-align: center;
    box-shadow: 0 8px 24px rgba(15,23,42,0.10);
}
.ai-pw-icon  { font-size: 3rem; margin-bottom: 8px; }
.ai-pw-title { font-size: 1.4rem; font-weight: 800; color: #0F172A; margin: 0 0 8px; }
.ai-pw-sub   { font-size: 0.875rem; color: #64748B; margin: 0 0 28px; line-height: 1.5; }

/* Section label */
.ai-section-label {
    font-size: 0.70rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.09em;
    color: #64748B;
    margin: 16px 0 8px;
}
</style>
"""

# ── Main render ───────────────────────────────────────────────────────────────

def render_ai_assistant(app_name: str = "PMU Tools", app_context: dict = None):
    app_context = app_context or {}
    st.markdown(_CSS, unsafe_allow_html=True)

    # ── Admin setup (no API key yet) ──────────────────────────────────────────
    if not ai_available():
        st.markdown("""
        <div class="ai-header">
            <h1>🤖 AI Assistant — Setup Required</h1>
            <p>Configure the AI Assistant so your team can start using it.</p>
        </div>
        """, unsafe_allow_html=True)

        st.info("**Admin Setup:** Enter your Anthropic API key and set a team access password. Users will only see the password prompt — the API key stays hidden.")

        with st.form("admin_setup_form"):
            st.markdown("##### Step 1 — Anthropic API Key")
            st.caption("Get your key at console.anthropic.com → API Keys")
            api_key = st.text_input("Anthropic API Key", type="password", placeholder="sk-ant-api03-...")
            st.markdown("##### Step 2 — Team Access Password")
            st.caption("This is what your team members will enter to use the AI Assistant")
            pw1 = st.text_input("Set Access Password", type="password", placeholder="e.g. PMU@2026")
            pw2 = st.text_input("Confirm Password",   type="password", placeholder="Re-enter password")

            if st.form_submit_button("💾 Save & Activate AI Assistant", type="primary"):
                errs = []
                if not api_key.strip().startswith("sk-ant-"):
                    errs.append("API key must start with 'sk-ant-'")
                if not pw1.strip():
                    errs.append("Access password cannot be empty")
                elif pw1 != pw2:
                    errs.append("Passwords do not match")
                if errs:
                    for e in errs: st.error(e)
                else:
                    save_anthropic_key(api_key.strip())
                    save_ai_password(pw1.strip())
                    st.success("✅ AI Assistant configured. Users can now access it with the password you set.")
                    st.rerun()
        return

    # ── Password gate ─────────────────────────────────────────────────────────
    if not _render_password_gate():
        return

    # ── Authenticated — main chat UI ──────────────────────────────────────────
    st.markdown(f"""
    <div class="ai-header">
        <h1>🤖 PMU AI Assistant</h1>
        <p>Ask anything about the PMU Studio Suite — or ask me to take an action on your behalf.</p>
        <span class="ai-badge">✦ Powered by Claude &nbsp;·&nbsp; Agentic Mode Active</span>
    </div>
    """, unsafe_allow_html=True)

    # Sidebar controls
    with st.sidebar:
        st.markdown("---")
        st.markdown("**AI Assistant**")
        ws = app_context.get("workspace")
        if ws:
            st.caption(f"Context: **{ws.get('name','')}**")
        if st.button("🗑 Clear Chat", use_container_width=True, key="clear_chat"):
            st.session_state["pmu_chat"] = []
            st.rerun()
        if st.button("🔒 Lock", use_container_width=True, key="lock_ai"):
            st.session_state.pop("ai_auth", None)
            st.session_state["pmu_chat"] = []
            st.rerun()
        st.caption("Admin: update API key or password in **Integrations → AI**.")

    # Init chat
    if "pmu_chat" not in st.session_state:
        st.session_state["pmu_chat"] = []

    # Suggestions (shown only when chat is empty)
    if not st.session_state["pmu_chat"]:
        SUGGESTIONS = [
            ("🏗️", "Create a workspace for UDISE 2026 Odisha"),
            ("📋", "Show my current schema fields"),
            ("➕", "Add the UDISE Code field to my schema"),
            ("🔍", "What validation rules should I add?"),
            ("📊", "How do I generate a district KPI report?"),
            ("🔗", "How do I connect Google Sheets?"),
            ("🔀", "Explain fuzzy matching for district names"),
            ("📄", "How do I create a district-wise split report?"),
        ]
        st.markdown('<div class="ai-section-label">Suggested questions</div>', unsafe_allow_html=True)
        cols = st.columns(2)
        for i, (icon, text) in enumerate(SUGGESTIONS):
            if cols[i % 2].button(f"{icon}  {text}", use_container_width=True, key=f"sug_{i}"):
                st.session_state["pmu_chat"].append({"role": "user", "content": text})
                st.rerun()
        st.markdown("---")

    # Render chat history
    for msg in st.session_state["pmu_chat"]:
        with st.chat_message(msg["role"], avatar="🧑‍💼" if msg["role"]=="user" else "🤖"):
            st.markdown(msg["content"])

    # Input
    if prompt := st.chat_input("Ask a question or request an action, e.g. 'Create a workspace for FLN 2026'"):
        st.session_state["pmu_chat"].append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar="🧑‍💼"):
            st.markdown(prompt)

        with st.chat_message("assistant", avatar="🤖"):
            with st.spinner(""):
                reply = _run_claude(
                    history=st.session_state["pmu_chat"][:-1],
                    user_message=prompt,
                    app_context=app_context,
                )
            st.markdown(reply)

        st.session_state["pmu_chat"].append({"role": "assistant", "content": reply})


def _run_claude(history: list, user_message: str, app_context: dict) -> str:
    try:
        import anthropic
    except ImportError:
        return "`anthropic` package not installed. Redeploy after adding it to requirements.txt."

    key = get_anthropic_key()
    if not key:
        return "API key not configured."

    client = anthropic.Anthropic(api_key=key)

    msgs = []
    for m in history[-20:]:
        if m["role"] in ("user","assistant") and isinstance(m["content"], str):
            msgs.append({"role": m["role"], "content": m["content"]})
    msgs.append({"role": "user", "content": user_message})

    tool_log = []

    for _ in range(5):
        resp = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=2048,
            system=SYSTEM_PROMPT,
            tools=TOOLS,
            messages=msgs,
        )

        text_parts = [b.text for b in resp.content if b.type == "text"]
        tool_uses  = [b for b in resp.content if b.type == "tool_use"]

        if not tool_uses:
            final = "\n".join(text_parts).strip()
            if tool_log:
                actions = "\n".join(f'<div class="tool-card">⚡ {t}</div>' for t in tool_log)
                return f'<div>{actions}</div>\n\n{final}'
            return final

        results = []
        for tu in tool_uses:
            out = _execute_tool(tu.name, tu.input, app_context)
            results.append({"type":"tool_result","tool_use_id":tu.id,"content":out})
            tool_log.append(f"Ran <strong>{tu.name}</strong>")

        msgs.append({"role": "assistant", "content": resp.content})
        msgs.append({"role": "user",      "content": results})

    return "\n".join(text_parts).strip() if text_parts else "Actions completed."
