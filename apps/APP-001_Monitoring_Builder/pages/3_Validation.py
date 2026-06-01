"""Page 3 — Validation Builder: define data quality rules."""
import sys
import os

_APP_DIR  = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_PMU_ROOT = os.path.dirname(os.path.dirname(_APP_DIR))
for _p in [_PMU_ROOT, _APP_DIR]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

import streamlit as st
from shared.theme import page_header, sidebar_brand
from uuid import uuid4
from engine import (
    init_state, reset_state, get_workspace, get_job, get_studio_job, set_studio_job,
    add_rule_def, remove_rule_def, has_fields, enabled_fields,
)

st.set_page_config(page_title="Validation — Monitoring Builder", page_icon="✅", layout="wide")
init_state()

ws  = get_workspace()
job = get_job()

with st.sidebar:
    sidebar_brand("Monitoring Builder", "APP-001")
    if ws:
        st.success(f"📁 **{ws['name']}**")
    else:
        st.warning("No workspace selected")
    st.info(f"**{len(job.rule_defs)}** rule(s) defined")
    if st.button("🗑 Reset Builder", use_container_width=True):
        reset_state(); st.rerun()

page_header("Validation", subtitle="Define data quality rules for collected submissions", icon="✅", step=3, total_steps=5)

if not has_fields():
    st.warning("Define fields first (Step 1 — Schema)."); st.stop()

e_fields    = enabled_fields()
field_names = [f.name for f in e_fields]
num_fields  = [f.name for f in e_fields if f.data_type in ("number", "integer")]

CHOOSE = "— choose —"

VALIDATION_TYPES = {
    "required":        "Required — field must not be blank",
    "type_check":      "Type Check — validate data type",
    "range_check":     "Range Check — value must be within min/max",
    "pattern_check":   "Format Check — must match a standard format",
    "compare_columns": "Compare Columns — one column vs another",
    "dependency_check":"Dependency — if A has value, B must too",
    "consistency_check":"Consistency — value consistent within group",
}

SEVERITY_LEVELS = ["error", "warning", "info"]
TYPE_OPTIONS    = ["numeric", "positive_numeric", "integer", "date", "text"]

PATTERN_PRESETS = {
    "udise_code":    ("^\\d{11}$",              "UDISE Code (exactly 11 digits)"),
    "phone_number":  ("^[6-9]\\d{9}$",          "Phone Number (10 digits, starts 6-9)"),
    "email":         ("^[\\w.%+-]+@[\\w.-]+\\.\\w{2,}$", "Email Address"),
    "pincode":       ("^\\d{6}$",               "PIN Code (exactly 6 digits)"),
    "year_4digit":   ("^(19|20)\\d{2}$",        "4-Digit Year (1900-2099)"),
    "date_ddmmyyyy": ("^\\d{2}/\\d{2}/\\d{4}$","Date — DD/MM/YYYY"),
    "date_yyyymmdd": ("^\\d{4}-\\d{2}-\\d{2}$","Date — YYYY-MM-DD"),
    "digits_only":   ("^\\d+$",                 "Digits Only (no letters or symbols)"),
    "letters_only":  ("^[A-Za-z\\s]+$",         "Letters Only (no numbers or symbols)"),
    "alphanumeric":  ("^[A-Za-z0-9]+$",         "Alphanumeric (letters and digits only)"),
    "positive_int":  ("^[1-9]\\d*$",            "Positive Integer (no zero, no negatives)"),
    "lgd_code":      ("^\\d{1,6}$",             "LGD Code (1-6 digits)"),
    "aadhaar":       ("^[2-9]\\d{11}$",         "Aadhaar Number (12 digits, starts 2-9)"),
    "custom":        (None,                      "Custom Regex (for advanced users)"),
}

# ── Auto-generate common rules from schema ───────────────────────────────────
with st.expander("⚡ Auto-generate rules from schema", expanded=not job.rule_defs):
    st.caption("Automatically create standard validation rules based on the fields you defined")
    ac1, ac2 = st.columns(2)
    if ac1.button("Generate Required Field Rules", use_container_width=True, type="primary"):
        added = 0
        existing_names = {r.get("name") for r in job.rule_defs}
        for f in e_fields:
            if f.required:
                rule_name = f"Required: {f.label}"
                if rule_name not in existing_names:
                    add_rule_def({
                        "rule_id":   uuid4().hex[:8].upper(),
                        "name":      rule_name,
                        "rule_type": "required",
                        "severity":  "error",
                        "enabled":   True,
                        "params":    {"column": f.name},
                    })
                    added += 1
        if added:
            st.success(f"Added {added} required-field rule(s)."); st.rerun()
        else:
            st.info("All required field rules already exist.")

    if ac2.button("Generate Range Rules (numeric fields)", use_container_width=True):
        added = 0
        existing_names = {r.get("name") for r in job.rule_defs}
        for f in e_fields:
            if f.data_type in ("number", "integer"):
                rule_name = f"Range: {f.label} > 0"
                if rule_name not in existing_names:
                    add_rule_def({
                        "rule_id":   uuid4().hex[:8].upper(),
                        "name":      rule_name,
                        "rule_type": "range_check",
                        "severity":  "warning",
                        "enabled":   True,
                        "params":    {"column": f.name, "min_val": 0.0, "max_val": 999999.0},
                    })
                    added += 1
        if added:
            st.success(f"Added {added} range rule(s)."); st.rerun()
        else:
            st.info("All numeric range rules already exist.")

# ── Add validation rule ───────────────────────────────────────────────────────
st.markdown("### Add Validation Rule")
with st.form("add_rule_form", clear_on_submit=True):
    c1, c2, c3 = st.columns(3)
    rule_name = c1.text_input("Rule Name *", placeholder="e.g. UDISE must be 11 digits")
    rule_type = c2.selectbox("Rule Type", list(VALIDATION_TYPES.keys()),
                              format_func=lambda k: VALIDATION_TYPES[k])
    severity  = c3.selectbox("Severity", SEVERITY_LEVELS)

    params = {}
    rule_preview_text = ""

    if rule_type == "required":
        col_sel = st.selectbox("Column must not be blank", [CHOOSE] + field_names)
        params["column"] = col_sel
        if col_sel != CHOOSE:
            rule_preview_text = f"**Rule preview:** Any row where `{col_sel}` is empty will be flagged as **{severity}**."

    elif rule_type == "type_check":
        ca, cb = st.columns(2)
        params["column"]        = ca.selectbox("Column", [CHOOSE] + field_names)
        params["expected_type"] = cb.selectbox("Expected type", TYPE_OPTIONS,
                                               format_func=lambda t: {
                                                   "numeric": "Number (any)",
                                                   "positive_numeric": "Positive Number (>0)",
                                                   "integer": "Whole Number",
                                                   "date": "Date",
                                                   "text": "Text (any)",
                                               }.get(t, t))

    elif rule_type == "range_check":
        ca, cb, cc = st.columns(3)
        col_sel = ca.selectbox("Numeric column", [CHOOSE] + num_fields)
        min_val = cb.number_input("Minimum", value=0.0)
        max_val = cc.number_input("Maximum", value=100.0)
        params["column"]  = col_sel
        params["min_val"] = min_val
        params["max_val"] = max_val
        if col_sel != CHOOSE:
            rule_preview_text = f"**Rule preview:** `{col_sel}` values outside [{min_val}, {max_val}] will be flagged."

    elif rule_type == "pattern_check":
        ca, cb = st.columns(2)
        col_sel = ca.selectbox("Column", [CHOOSE] + field_names)
        preset  = cb.selectbox("Format", list(PATTERN_PRESETS.keys()),
                                format_func=lambda k: PATTERN_PRESETS[k][1])
        if preset == "custom":
            pattern = st.text_input("Custom regex pattern")
            st.caption("Example: `^\\d{11}$` matches exactly 11 digits.")
        else:
            pattern = PATTERN_PRESETS[preset][0]
            st.info(f"**Format:** {PATTERN_PRESETS[preset][1]}  |  Rows that do NOT match will be flagged.")
        params["column"]  = col_sel
        params["pattern"] = pattern

    elif rule_type == "compare_columns":
        ca, cb, cc = st.columns(3)
        col_a    = ca.selectbox("Column A", [CHOOSE] + field_names)
        operator = cb.selectbox("Must be", ["eq", "neq", "gt", "gte", "lt", "lte"],
                                format_func=lambda k: {"eq": "= equal to", "neq": "not equal to",
                                                        "gt": "> greater than", "gte": ">= greater or equal",
                                                        "lt": "< less than", "lte": "<= less or equal"}[k])
        col_b    = cc.selectbox("Column B", [CHOOSE] + field_names)
        params["col_a"]    = col_a
        params["operator"] = operator
        params["col_b"]    = col_b
        if col_a != CHOOSE and col_b != CHOOSE:
            op_label = {"eq": "equal to", "neq": "not equal to", "gt": "greater than",
                        "gte": "greater or equal to", "lt": "less than", "lte": "less or equal to"}[operator]
            rule_preview_text = f"**Rule preview:** Rows where `{col_a}` is NOT {op_label} `{col_b}` will be flagged."

    elif rule_type == "dependency_check":
        st.info("**Dependency rule:** if the trigger field has any value, the dependent field must also have a value.\n\n"
                "Example: if Visit Date is filled, then Reported By must also be filled.")
        ca, cb = st.columns(2)
        trigger_col   = ca.selectbox("If this field has a value", [CHOOSE] + field_names)
        dependent_col = cb.selectbox("Then this field must also have a value", [CHOOSE] + field_names)
        params["trigger_col"]   = trigger_col
        params["dependent_col"] = dependent_col
        if trigger_col != CHOOSE and dependent_col != CHOOSE:
            rule_preview_text = (
                f"**Rule preview:** If `{trigger_col}` is filled but `{dependent_col}` is blank, "
                f"the row will be flagged."
            )

    elif rule_type == "consistency_check":
        params["group_col"]  = st.selectbox("Group column", [CHOOSE] + field_names)
        params["check_cols"] = st.multiselect("Must be consistent within group", field_names)
        if params.get("group_col") != CHOOSE and params.get("check_cols"):
            rule_preview_text = (
                f"**Rule preview:** Within each `{params['group_col']}` group, "
                f"the columns {', '.join(params['check_cols'])} must have the same value across all rows."
            )

    if rule_preview_text:
        st.info(rule_preview_text)

    if st.form_submit_button("Add Rule", type="primary") and rule_name.strip():
        add_rule_def({
            "rule_id":   uuid4().hex[:8].upper(),
            "name":      rule_name.strip(),
            "rule_type": rule_type,
            "severity":  severity,
            "enabled":   True,
            "params":    params,
        })
        st.success(f"Rule **{rule_name.strip()}** added."); st.rerun()

# ── Rule list ─────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("### Defined Validation Rules")
if not job.rule_defs:
    st.info("No validation rules yet. Use Auto-generate above or add rules manually.")
else:
    for r in job.rule_defs:
        with st.container(border=True):
            c1, c2 = st.columns([5, 1])
            badge  = {"error": "🔴", "warning": "🟡", "info": "🔵"}.get(r.get("severity", "info"), "⚪")
            rule_type_label = VALIDATION_TYPES.get(r.get("rule_type", ""), r.get("rule_type", ""))
            c1.markdown(f"{badge} **{r['name']}** · _{rule_type_label.split(' — ')[0]}_")
            if c2.button("✕", key=f"rm_{r['rule_id']}", use_container_width=True, help="Remove"):
                remove_rule_def(r["rule_id"]); st.rerun()

st.markdown("---")
st.info("💡 These rules will be exported as a **.pmuconfig** on the **Package** page, "
        "importable directly into **APP-002 Data Processing Studio** to validate collected data.")
