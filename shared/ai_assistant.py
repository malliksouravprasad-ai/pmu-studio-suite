"""
PMU Tools AI Assistant — Claude-powered agentic assistant.
Answers questions about all 6 apps and can take actions on behalf of the user.
"""
from __future__ import annotations
import json
import streamlit as st

# ── API key management ────────────────────────────────────────────────────────

def get_anthropic_key() -> str | None:
    """Return API key: UI-saved → st.secrets → None."""
    try:
        from .credentials_manager import _load
        k = _load().get("anthropic_api_key")
        if k:
            return k
    except Exception:
        pass
    try:
        return st.secrets.get("anthropic_api_key") or st.secrets.get("ANTHROPIC_API_KEY")
    except Exception:
        return None


def save_anthropic_key(key: str) -> None:
    from .credentials_manager import _load, _save
    data = _load()
    data["anthropic_api_key"] = key.strip()
    _save(data)


def ai_available() -> bool:
    return bool(get_anthropic_key())


# ── System prompt ─────────────────────────────────────────────────────────────

SYSTEM_PROMPT = """
You are the PMU Tools AI Assistant — an expert agentic assistant built for Project Monitoring Unit (PMU) teams supporting education-sector programmes in India (primarily Odisha).

## What you know

### The PMU Studio Suite (6 apps)

**APP-001 — Monitoring Builder**
Purpose: Design a monitoring framework from scratch — define data fields, form structure, validation rules, KPI definitions. Outputs: Excel template, Google Form, validation_config.json, kpi_config.json.
Key pages: Workspace → Schema (define fields with inline table) → Form (section builder) → Validation (add rules) → KPIs (define indicators) → Package (generate all outputs).

**APP-002 — Data Processing Studio**
Purpose: Clean, transform, standardise, and validate raw data from any source.
Data sources: File upload (CSV/XLSX), Google Sheet URL, BigQuery.
Key pages: Upload → Clean (fill missing, dedup, strip whitespace) → Transform (rename/merge/split/calculate columns, filter/sort rows) → Map (fuzzy match district/block names against master lists) → Validate (required, type, range, pattern, comparison, dependency, consistency rules) → Generate (download clean dataset, transformation log, validation report).

**APP-003 — Analytics Studio**
Purpose: Aggregate clean data, calculate KPIs, rank entities, analyse variances and trends.
Key pages: Upload → Aggregate (groupby district/block, sum/avg/count) → KPIs (calculate scores vs targets) → Analyse (rank districts, variance analysis) → Trends (4-period trend, growth matrix) → Generate (KPI report, analytics workbook).

**APP-004 — Dashboard Studio**
Purpose: Build KPI cards, charts, and summary tables → export Excel dashboard.
Key pages: Upload → KPIs (add KPI cards with target status) → Charts (bar/line/area/pie charts) → Tables (aggregated summary tables with totals) → Layout (save/load dashboard layout) → Generate (dashboard Excel + dataset).

**APP-005 — Deliverable Studio**
Purpose: Generate reports in Excel, Word, PowerPoint, and PDF from structured data.
Key pages: Upload → Report Details (title, author, formats) → Sections (table/narrative/highlights sections) → Generate (download all selected formats, with option to split reports by District/Block).

**APP-006 — Workflow Builder**
Purpose: Track implementation progress across entities (districts/schools/blocks) through defined stages.
Key pages: Define (entity list, stage list) → Tracker (update status per entity per stage: Completed/In Progress/Pending/Overdue) → Generate (tracker Excel, pendency report).

### Integrations (in every app → Integrations tab)
- Google Workspace: paste Service Account JSON → connects Google Sheets, Drive, Forms
- BigQuery: enter Project ID + Dataset → load/push large datasets
- Apps Script Aggregator: enter web app URL + secret → trigger automated aggregations on Google Sheets

### Data Input Flows
- Flow A: Upload CSV/XLSX file
- Flow B: Paste Google Sheet URL → loads live data
- Flow C: Connect BigQuery → browse tables or run SQL queries
- Flow D: Trigger Apps Script → aggregate a Google Sheet automatically

### UDISE+ Context
UDISE Code: 11-digit unique school identifier. Field validation: `^\d{11}$`.
District codes follow LGD (Local Government Directory). Odisha has 30 districts.
Key fields: udise_code, district_name, block_name, school_name, total_enrolment, attendance_pct.
Data is collected annually via UDISE+ Data Capture Format (DCF) covering: School Profile (Section 1A), Safety (1B), Expenditure (1C), Physical Facilities (Section 2), Staff (Section 3), Students (Section 4).

### Common PMU Workflows
1. Design framework (APP-001) → Collect via Form → Clean data (APP-002) → Analyse (APP-003) → Dashboard (APP-004) → Report (APP-005)
2. Upload UDISE+ Excel → Clean + validate UDISE codes → Aggregate by district → KPI scorecard → PPT report
3. Track ATR compliance across districts (APP-006) → generate pendency report for review meeting

### Workspace System
All apps share workspaces. Create once → visible everywhere. User Tag field isolates workspaces between team members.
Artifacts saved with PMU IDs: PMU-2026-FLN-REPORT-00001 format.

## Your behaviour

- Be concise and action-oriented. PMU users are busy.
- When the user asks you to DO something (create workspace, add field, etc.), use the available tools — don't just explain how to do it manually.
- When explaining navigation, give exact page names: "Go to APP-002 → Upload → Google Sheet tab".
- Use PMU language: district, block, school, enrolment, attendance, ATR, MOM, KPI, pendency.
- If unsure about a data structure, ask one clarifying question.
- Never make up field names, column names, or values — ask the user if you don't know.
""".strip()


# ── Tool definitions ──────────────────────────────────────────────────────────

TOOLS = [
    {
        "name": "create_workspace",
        "description": "Create a new project workspace. Use when the user asks to create, set up, or start a new project workspace.",
        "input_schema": {
            "type": "object",
            "properties": {
                "name":         {"type": "string", "description": "Workspace name, e.g. FLN_2026_Odisha"},
                "project_code": {"type": "string", "description": "Short project code, e.g. FLN"},
                "description":  {"type": "string", "description": "Optional description"},
            },
            "required": ["name", "project_code"],
        },
    },
    {
        "name": "list_workspaces",
        "description": "List all existing workspaces with their names, project codes, and modification dates.",
        "input_schema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "add_schema_field",
        "description": "Add a new data field to the current monitoring framework schema in APP-001. Use when the user asks to add a field.",
        "input_schema": {
            "type": "object",
            "properties": {
                "label":       {"type": "string", "description": "Human-readable field label, e.g. School Name"},
                "column_name": {"type": "string", "description": "Column name with no spaces, e.g. school_name"},
                "data_type":   {"type": "string", "enum": ["text","integer","number","code","date","choice","boolean"], "description": "Data type"},
                "required":    {"type": "boolean", "description": "Whether this field is mandatory"},
                "description": {"type": "string", "description": "What this field means"},
                "choices":     {"type": "string", "description": "Comma-separated choices for choice/boolean fields"},
            },
            "required": ["label", "column_name", "data_type"],
        },
    },
    {
        "name": "get_current_schema",
        "description": "Get the list of fields currently defined in the active monitoring framework. Use to show the user what fields exist.",
        "input_schema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "get_app_help",
        "description": "Get detailed step-by-step guidance for a specific PMU app or feature.",
        "input_schema": {
            "type": "object",
            "properties": {
                "topic": {"type": "string", "description": "App name or feature, e.g. APP-002, fuzzy matching, BigQuery, Apps Script, validation rules, KPI"},
            },
            "required": ["topic"],
        },
    },
    {
        "name": "suggest_validation_rules",
        "description": "Suggest appropriate validation rules for the current schema fields. Use when the user asks what rules to add.",
        "input_schema": {"type": "object", "properties": {}, "required": []},
    },
]


# ── Tool execution ────────────────────────────────────────────────────────────

def _execute_tool(name: str, inputs: dict, app_context: dict) -> str:
    from shared.workspace import list_workspaces, create_workspace

    if name == "list_workspaces":
        ws_list = list_workspaces()
        if not ws_list:
            return "No workspaces found. Create one first."
        lines = ["**Existing workspaces:**"]
        for w in ws_list:
            lines.append(f"- **{w['name']}** ({w['project_code']}) — modified: {w.get('modified','—')}" +
                        (f" [tag: {w['user_tag']}]" if w.get('user_tag') else ""))
        return "\n".join(lines)

    if name == "create_workspace":
        try:
            ws = create_workspace(
                inputs["name"], inputs["project_code"],
                user_tag=app_context.get("user_tag", ""),
                description=inputs.get("description", ""),
            )
            return f"✅ Workspace **{ws['name']}** created with project code **{ws['project_code']}**. It is now active and accessible in all PMU apps."
        except FileExistsError:
            return f"A workspace named '{inputs['name']}' already exists. Choose a different name or open the existing one."
        except Exception as e:
            return f"Could not create workspace: {e}"

    if name == "get_current_schema":
        job = app_context.get("job")
        if not job or not job.fields:
            return "No fields defined yet in the current monitoring framework."
        lines = [f"**{len(job.fields)} fields defined:**"]
        for f in job.fields:
            badge = "🔑" if f.is_identifier else ("⭐" if f.required else "·")
            lines.append(f"{badge} **{f.label}** (`{f.name}`) — {f.data_type}" +
                        (f" — choices: {', '.join(f.choices[:4])}" if f.choices else ""))
        return "\n".join(lines)

    if name == "add_schema_field":
        from engine import add_field, FieldDef
        label   = inputs["label"]
        colname = inputs["column_name"].replace(" ", "_")
        dtype   = inputs.get("data_type", "text")
        choices = [c.strip() for c in inputs.get("choices","").split(",") if c.strip()]
        try:
            add_field(FieldDef(
                name=colname, label=label, data_type=dtype,
                required=inputs.get("required", False),
                choices=choices,
                description=inputs.get("description", ""),
            ))
            return f"✅ Field **{label}** (`{colname}`, type: `{dtype}`) added to the schema. Go to the Schema page to see it in the table."
        except Exception as e:
            return f"Could not add field: {e}"

    if name == "get_app_help":
        topic = inputs.get("topic","").lower()
        help_map = {
            "app-002": "**APP-002 Data Processing Studio:**\n1. Upload → load CSV/XLSX or paste Google Sheet URL\n2. Clean → fill missing values, remove duplicates, strip whitespace from names\n3. Transform → rename columns, create calculated columns (e.g. attendance %)\n4. Map → standardise district/block names (fuzzy matching against Odisha master list)\n5. Validate → run required, range, pattern, comparison checks\n6. Generate → download clean dataset, transformation log, validation report",
            "fuzzy": "**Fuzzy Matching (APP-002 → Map tab):**\nSelects a column (e.g. District), compares each value against a master list (built-in Odisha districts). Results: Exact (auto-accepted), Variant (auto-accepted), Fuzzy (review each suggestion), Unmatched (assign manually). Threshold controls sensitivity (default 80%).",
            "bigquery": "**BigQuery Setup:**\n1. Go to Integrations tab → BigQuery\n2. Enter your GCP Project ID and Dataset ID\n3. Click Save → Test BigQuery Connection\n4. Once connected: Upload tab → BigQuery tab → browse tables or write SQL",
            "apps script": "**Apps Script Aggregator:**\n1. Go to Integrations tab → Apps Script\n2. Enter Web App URL and Shared Secret\n3. From any Generate tab → Apps Script section → enter source sheet, target sheet, group columns, metric columns\n4. Click Run Aggregator → data is aggregated and written to target sheet automatically",
            "kpi": "**KPI Configuration (APP-003):**\nThree formula types:\n- Value: use a column directly (e.g. avg_attendance)\n- Ratio: numerator ÷ denominator\n- Percentage: (numerator ÷ denominator) × 100\nSet target value and interpretation (higher/lower is better). Composite score = weighted average of all KPIs.",
            "validation": "**Validation Rules (APP-002 → Validate):**\n- Required: column must not be blank\n- Type Check: must be numeric/integer/date\n- Range: numeric column must be between min and max\n- Pattern: text must match format (UDISE = 11 digits, phone = 10 digits)\n- Compare Columns: col_a must be ≤/≥ col_b (e.g. present ≤ total)\n- Dependency: if field A is filled, field B must also be filled\n- Consistency: sum of parts must equal total",
        }
        for key, val in help_map.items():
            if key in topic:
                return val
        return f"I can provide detailed help on: APP-002 processing, fuzzy matching, BigQuery, Apps Script, KPI formulas, validation rules. Which one would you like?"

    if name == "suggest_validation_rules":
        job = app_context.get("job")
        if not job or not job.fields:
            return "No fields defined yet. Add fields first, then I can suggest validation rules."
        suggestions = []
        for f in job.fields:
            if f.is_identifier:
                suggestions.append(f"- **{f.label}**: Required | Pattern check (UDISE: 11 digits if it's a school code)")
            elif f.required:
                suggestions.append(f"- **{f.label}**: Required field rule (severity: Error)")
            if f.data_type == "integer" and "enrolment" in f.name.lower():
                suggestions.append(f"- **{f.label}**: Range check 1–10000 (must be positive)")
            if f.data_type == "number" and "pct" in f.name.lower():
                suggestions.append(f"- **{f.label}**: Range check 0–100 (percentage cannot exceed 100)")
            if f.data_type == "date":
                suggestions.append(f"- **{f.label}**: Type check (must be a valid date)")
        return "**Suggested validation rules based on your schema:**\n" + "\n".join(suggestions) if suggestions else "No specific suggestions — add more fields first."

    return f"Tool '{name}' executed. (No specific output)"


# ── Chat UI ───────────────────────────────────────────────────────────────────

def render_ai_assistant(app_name: str = "PMU Tools", app_context: dict = None):
    """
    Full-page AI assistant chat UI.
    app_context: dict with keys like 'job', 'workspace', 'user_tag' from session state.
    """
    app_context = app_context or {}

    st.markdown("# 🤖 AI Assistant")
    st.caption(f"Powered by Claude · Knows every feature of PMU Tools · Can take actions on your behalf")

    # API key check / setup
    if not ai_available():
        st.warning("AI Assistant is not configured. Enter your Anthropic API key below to enable it.")
        with st.form("api_key_form"):
            key_input = st.text_input("Anthropic API Key", type="password",
                                      placeholder="sk-ant-api03-...")
            st.caption("Get your key at console.anthropic.com → API Keys. Your key is saved securely on the server.")
            if st.form_submit_button("Save API Key", type="primary"):
                if key_input.strip().startswith("sk-ant-"):
                    save_anthropic_key(key_input.strip())
                    st.success("API key saved. Reloading...")
                    st.rerun()
                else:
                    st.error("This does not look like a valid Anthropic API key. It should start with 'sk-ant-'.")
        return

    # Init chat history
    if "pmu_chat" not in st.session_state:
        st.session_state["pmu_chat"] = []

    # Sidebar controls
    with st.sidebar:
        st.markdown("---")
        st.markdown("**AI Assistant**")
        if st.button("🗑 Clear Chat", use_container_width=True, key="clear_chat"):
            st.session_state["pmu_chat"] = []
            st.rerun()
        st.caption("The assistant knows your current workspace and schema.")

    # Suggested prompts (shown when chat is empty)
    if not st.session_state["pmu_chat"]:
        st.markdown("### What can I help you with?")
        suggestions = [
            "Create a workspace for UDISE 2026 Odisha",
            "Add the UDISE Code field to my schema",
            "How do I validate UDISE codes in APP-002?",
            "What validation rules should I add for my school monitoring form?",
            "How do I connect Google Sheets to PMU Tools?",
            "Explain how fuzzy matching works for district names",
            "Show me my current schema fields",
            "How do I generate a district-wise report?",
        ]
        cols = st.columns(2)
        for i, s in enumerate(suggestions):
            if cols[i % 2].button(s, use_container_width=True, key=f"sug_{i}"):
                st.session_state["pmu_chat"].append({"role": "user", "content": s})
                st.rerun()
        st.markdown("---")

    # Display chat history
    for msg in st.session_state["pmu_chat"]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Input
    user_input = st.chat_input("Ask anything about PMU Tools, or say 'Create a workspace for FLN 2026'...")

    if user_input:
        st.session_state["pmu_chat"].append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response_text = _run_claude(
                    messages=st.session_state["pmu_chat"][:-1],
                    user_message=user_input,
                    app_context=app_context,
                )
            st.markdown(response_text)

        st.session_state["pmu_chat"].append({"role": "assistant", "content": response_text})


def _run_claude(messages: list, user_message: str, app_context: dict) -> str:
    """Run Claude with tool use, handle tool calls, return final text."""
    try:
        import anthropic
    except ImportError:
        return "The `anthropic` package is not installed. Run `pip install anthropic` and redeploy."

    key = get_anthropic_key()
    if not key:
        return "API key not configured."

    client = anthropic.Anthropic(api_key=key)

    # Build message history (last 20 turns to stay within context)
    history = []
    for m in messages[-20:]:
        if m["role"] in ("user", "assistant"):
            history.append({"role": m["role"], "content": m["content"]})
    history.append({"role": "user", "content": user_message})

    # Agentic loop — keep going until no more tool calls
    for _ in range(5):  # max 5 tool-call rounds
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=2048,
            system=SYSTEM_PROMPT,
            tools=TOOLS,
            messages=history,
        )

        # Collect text and tool uses from this response
        text_parts   = []
        tool_uses    = []

        for block in response.content:
            if block.type == "text":
                text_parts.append(block.text)
            elif block.type == "tool_use":
                tool_uses.append(block)

        if not tool_uses:
            # No tools called — final answer
            return "\n".join(text_parts).strip() or "(No response)"

        # Execute each tool and collect results
        tool_results = []
        tool_texts   = []
        for tu in tool_uses:
            result = _execute_tool(tu.name, tu.input, app_context)
            tool_results.append({
                "type":        "tool_result",
                "tool_use_id": tu.id,
                "content":     result,
            })
            tool_texts.append(f"[Ran: **{tu.name}**]")

        # Add assistant turn (with tool_use blocks) + tool results to history
        history.append({"role": "assistant", "content": response.content})
        history.append({"role": "user",      "content": tool_results})

        # If assistant also wrote text before calling tools, show it
        if text_parts:
            tool_texts = text_parts + tool_texts

    # Fallback if loop exhausted
    return "\n".join(text_parts).strip() if text_parts else "I ran several actions. Check your workspace and schema for updates."
