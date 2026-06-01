"""Page 5 — Validation rules and calculation rules."""
import sys
import os

_APP_DIR  = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_PMU_ROOT = os.path.dirname(os.path.dirname(_APP_DIR))
for _p in [_PMU_ROOT, _APP_DIR]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

import re
import pandas as pd
import streamlit as st
from shared.theme import page_header, sidebar_brand
from engine import (
    init_state, reset_state, get_workspace, get_job,
    has_data, get_raw_df, get_mapped_df,
    add_rule, remove_rule, get_rule_results, set_rule_results,
    Rule, VALIDATION_TYPES, CALCULATION_TYPES, SEVERITY_LEVELS,
    COMPARE_OPS, TYPE_OPTIONS, PATTERN_PRESETS, MATH_OPS,
    run_all_rules,
)

st.set_page_config(page_title="Validate — Data Processing Studio", page_icon="✅", layout="wide")
init_state()

ws  = get_workspace()
job = get_job()

with st.sidebar:
    sidebar_brand("Data Processing Studio", "APP-002")
    if ws:
        st.success(f"📁 **{ws['name']}**")
    else:
        st.warning("No workspace selected")
    enabled = [r for r in job.rule_job.rules if r.enabled]
    st.info(f"**{len(enabled)}** rule(s) defined")
    if st.button("🗑 Reset Studio", use_container_width=True):
        reset_state(); st.rerun()

page_header("Validate", subtitle="Run validation rules against the cleaned dataset", icon="✅", step=5, total_steps=6)

if not has_data():
    st.warning("Please upload a file first (Step 1 — Upload).")
    st.stop()

working_df = get_mapped_df() if get_mapped_df() is not None else get_raw_df()
cols     = working_df.columns.tolist()
num_cols = list(working_df.select_dtypes(include="number").columns)

CHOOSE = "— choose —"

tab1, tab2 = st.tabs(["Validation Rules", "Calculation Rules"])

# ── Tab 1: Validation Rules ───────────────────────────────────────────────────
with tab1:
    st.markdown("#### Add Validation Rule")
    c1, c2, c3 = st.columns(3)
    rule_name  = c1.text_input("Rule name", placeholder="e.g. School Name Required")
    rule_type  = c2.selectbox("Rule type", VALIDATION_TYPES)
    severity   = c3.selectbox("Severity", SEVERITY_LEVELS)

    params = {}
    rule_preview_text = ""

    if rule_type == "required":
        col_sel = st.selectbox("Column must not be blank", [CHOOSE] + cols)
        params["column"] = col_sel
        if col_sel != CHOOSE:
            blank_count = working_df[col_sel].isna().sum() + (working_df[col_sel] == "").sum()
            rule_preview_text = f"**Preview:** `{col_sel}` — {blank_count:,} blank value(s) in {len(working_df):,} rows would be flagged."

    elif rule_type == "type_check":
        c_a, c_b = st.columns(2)
        col_sel = c_a.selectbox("Column", [CHOOSE] + cols)
        exp_type = c_b.selectbox("Expected type", TYPE_OPTIONS,
                                  format_func=lambda t: {
                                      "numeric":          "Number (any)",
                                      "positive_numeric": "Positive Number (> 0)",
                                      "integer":          "Whole Number (integer)",
                                      "date":             "Date",
                                      "text":             "Text (any)",
                                  }.get(t, t))
        params["column"] = col_sel
        params["expected_type"] = exp_type

    elif rule_type == "range_check":
        c_a, c_b, c_c = st.columns(3)
        col_sel    = c_a.selectbox("Column", [CHOOSE] + num_cols)
        min_val    = c_b.number_input("Minimum", value=0.0)
        max_val    = c_c.number_input("Maximum", value=100.0)
        params["column"]  = col_sel
        params["min_val"] = min_val
        params["max_val"] = max_val
        if col_sel != CHOOSE:
            out_of_range = ((working_df[col_sel] < min_val) | (working_df[col_sel] > max_val)).sum()
            rule_preview_text = f"**Preview:** {out_of_range:,} rows in `{col_sel}` are outside [{min_val}, {max_val}] and would be flagged."

    elif rule_type == "pattern_check":
        c_a, c_b = st.columns(2)
        col_sel = c_a.selectbox("Column", [CHOOSE] + cols)
        preset  = c_b.selectbox("Format", list(PATTERN_PRESETS.keys()),
                                 format_func=lambda k: PATTERN_PRESETS[k][1])
        if preset == "custom":
            pattern = st.text_input("Custom regex pattern")
            st.caption("Example: `^\\d{11}$` matches exactly 11 digits.  `^[A-Z]+$` matches uppercase letters only.")
        else:
            pattern = PATTERN_PRESETS[preset][0]
            desc    = PATTERN_PRESETS[preset][1]
            st.info(f"**Format:** {desc}  |  Rows that do NOT match this format will be flagged.")
        params["column"]  = col_sel
        params["pattern"] = pattern
        if col_sel != CHOOSE and pattern:
            try:
                rx = re.compile(pattern)
                fail_count = working_df[col_sel].astype(str).apply(
                    lambda v: not rx.match(str(v)) if pd.notna(v) and str(v) not in ("", "nan") else False
                ).sum()
                rule_preview_text = f"**Preview:** {fail_count:,} rows in `{col_sel}` do not match the selected format and would be flagged."
            except re.error:
                rule_preview_text = "Invalid regex pattern — check syntax."

    elif rule_type == "compare_columns":
        c_a, c_op, c_b = st.columns(3)
        col_a    = c_a.selectbox("Column A", [CHOOSE] + cols)
        operator = c_op.selectbox("Must be", list(COMPARE_OPS.keys()), format_func=lambda k: COMPARE_OPS[k])
        col_b    = c_b.selectbox("Column B", [CHOOSE] + cols)
        params["col_a"]    = col_a
        params["operator"] = operator
        params["col_b"]    = col_b
        if col_a != CHOOSE and col_b != CHOOSE:
            rule_preview_text = f"**Rule:** `{col_a}` must be {COMPARE_OPS[operator]} `{col_b}` — rows where this is not true will be flagged."

    elif rule_type == "dependency_check":
        st.info("**Dependency rule:** if the trigger field has any value, the dependent field must also have a value. Example: if Visit Date is filled, Reported By must also be filled.")
        c_a, c_b = st.columns(2)
        trigger_col   = c_a.selectbox("If this column has a value", [CHOOSE] + cols)
        dependent_col = c_b.selectbox("Then this column must also have a value", [CHOOSE] + cols)
        params["trigger_col"]   = trigger_col
        params["dependent_col"] = dependent_col
        if trigger_col != CHOOSE and dependent_col != CHOOSE:
            rule_preview_text = (
                f"**Rule preview:** Rows where `{trigger_col}` is filled but `{dependent_col}` is blank will be flagged.\n\n"
                f"**Sample check:** "
                f"{int((working_df[trigger_col].notna() & (working_df[dependent_col].isna() | (working_df[dependent_col] == ''))).sum()):,} "
                f"such rows found in current dataset."
            )

    elif rule_type == "consistency_check":
        grp_col   = st.selectbox("Group column (e.g. District)", [CHOOSE] + cols)
        chk_cols  = st.multiselect("Values must be consistent within group", cols)
        params["group_col"]  = grp_col
        params["check_cols"] = chk_cols
        if grp_col != CHOOSE and chk_cols:
            rule_preview_text = f"**Rule:** within each `{grp_col}` group, columns {', '.join(chk_cols)} must have consistent values."

    if rule_preview_text:
        st.markdown(rule_preview_text)

    if st.button("Add Validation Rule", type="primary") and rule_name.strip():
        add_rule(Rule(name=rule_name.strip(), rule_type=rule_type, severity=severity, params=params))
        st.success("Rule added."); st.rerun()

# ── Tab 2: Calculation Rules ──────────────────────────────────────────────────
with tab2:
    st.markdown("#### Add Calculation Rule")
    c1, c2 = st.columns(2)
    calc_name = c1.text_input("Rule name", placeholder="e.g. Enrolment Rate")
    calc_type = c2.selectbox("Calculation type", CALCULATION_TYPES,
                              format_func=lambda t: {
                                  "arithmetic":  "Math — column A operation column B",
                                  "conditional": "Conditional — if/then value assignment",
                                  "percentage":  "Percentage — (numerator / denominator) x 100",
                                  "score":       "Weighted Score — combine multiple columns",
                              }.get(t, t))

    calc_params = {}
    if calc_type == "arithmetic":
        c_a, c_op, c_b, c_out = st.columns(4)
        calc_params["col_a"]      = c_a.selectbox("Column A", [CHOOSE] + num_cols)
        calc_params["op"]         = c_op.selectbox("Op", list(MATH_OPS.keys()), format_func=lambda k: MATH_OPS[k])
        calc_params["col_b"]      = c_b.selectbox("Column B", [CHOOSE] + num_cols + ["Constant"])
        calc_params["output_col"] = c_out.text_input("Output column name", value="Result")
        if calc_params["col_b"] == "Constant":
            calc_params["constant_b"] = st.number_input("Constant value", value=1.0)
        # Preview
        a = calc_params.get("col_a", "A")
        b = "constant" if calc_params.get("col_b") == "Constant" else calc_params.get("col_b", "B")
        st.caption(f"Will create column **{calc_params['output_col']}** = `{a}` {MATH_OPS.get(calc_params['op'], '')} `{b}`")

    elif calc_type == "conditional":
        st.info("**Conditional rule:** if a column meets a condition, assign one value; otherwise assign another.")
        c_a, c_op, c_b = st.columns(3)
        calc_params["condition_col"] = c_a.selectbox("If column", [CHOOSE] + cols)
        calc_params["operator"]      = c_op.selectbox("Condition", list(COMPARE_OPS.keys()), format_func=lambda k: COMPARE_OPS[k])
        calc_params["condition_val"] = c_b.text_input("Value to compare")
        c_t, c_f, c_out = st.columns(3)
        calc_params["true_val"]   = c_t.text_input("Then output", value="1")
        calc_params["false_val"]  = c_f.text_input("Else output", value="0")
        calc_params["output_col"] = c_out.text_input("Output column", value="Flag")
        cond_col = calc_params.get("condition_col", "col")
        cond_val = calc_params.get("condition_val", "value")
        op_label = COMPARE_OPS.get(calc_params.get("operator", "eq"), "")
        st.caption(f"Will create **{calc_params['output_col']}** = {calc_params['true_val']} if `{cond_col}` {op_label} `{cond_val}`, else {calc_params['false_val']}")

    elif calc_type == "percentage":
        c_n, c_d, c_out = st.columns(3)
        calc_params["numerator"]   = c_n.selectbox("Numerator column", [CHOOSE] + num_cols)
        calc_params["denominator"] = c_d.selectbox("Denominator column", [CHOOSE] + num_cols)
        calc_params["output_col"]  = c_out.text_input("Output column", value="Percentage")
        n = calc_params.get("numerator", "A"); d = calc_params.get("denominator", "B")
        st.caption(f"Will create **{calc_params['output_col']}** = (`{n}` ÷ `{d}`) × 100")

    elif calc_type == "score":
        calc_params["score_cols"]   = st.multiselect("Columns to score (numeric)", num_cols)
        calc_params["weights"]      = st.text_input("Weights (comma-separated, same order as columns above)", value="1,1,1")
        calc_params["output_col"]   = st.text_input("Score column name", value="Score")
        calc_params["scale"]        = st.number_input("Scale to (0 = no scaling)", value=100.0)

    if st.button("Add Calculation Rule", type="primary") and calc_name.strip():
        add_rule(Rule(name=calc_name.strip(), rule_type=calc_type, severity="info", params=calc_params))
        st.success("Rule added."); st.rerun()

# ── Rule list ─────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("### Configured Rules")
all_rules = job.rule_job.rules
if not all_rules:
    st.info("No rules defined yet. Add rules above to validate data quality.")
else:
    for r in all_rules:
        with st.container(border=True):
            c1, c2, c3 = st.columns([5, 1, 1])
            badge = {"error": "🔴", "warning": "🟡", "info": "🔵"}.get(r.severity, "⚪")
            c1.markdown(f"{badge} **{r.name}** · `{r.rule_type}` · {'✅' if r.enabled else '⏸'}")
            if c2.button("Test", key=f"test_{r.rule_id}", use_container_width=True, help="Test on current data"):
                st.session_state[f"test_result_{r.rule_id}"] = True
            if c3.button("✕", key=f"rm_{r.rule_id}", use_container_width=True, help="Remove"):
                remove_rule(r.rule_id); st.rerun()

            if st.session_state.get(f"test_result_{r.rule_id}"):
                with st.spinner("Testing rule…"):
                    try:
                        _, test_results, test_exc, _ = run_all_rules(working_df, [r])
                        if test_results:
                            rr = test_results[0]
                            status_icon = {"PASS": "🟢", "WARN": "🟡", "FAIL": "🔴"}.get(rr.status, "⚪")
                            st.markdown(f"{status_icon} **{rr.rule_name}** — **{rr.failed:,}** / {rr.total:,} rows failed ({rr.fail_pct:.1f}%)")
                    except Exception as e:
                        st.warning(f"Could not test rule: {e}")

# ── Run rules ─────────────────────────────────────────────────────────────────
st.markdown("---")
if st.button("▶ Run All Rules on Full Dataset", type="primary", use_container_width=True) and all_rules:
    with st.spinner("Running rules…"):
        result_df, val_results, exceptions, calc_log = run_all_rules(working_df, all_rules)
    set_rule_results(val_results, exceptions, calc_log)
    st.success(f"Rules executed. {len(val_results)} validation rule(s), {len(calc_log)} calculation(s).")
    st.rerun()

# ── Results ───────────────────────────────────────────────────────────────────
val_results = get_rule_results()
if val_results:
    st.markdown("### Validation Results")
    pass_count = sum(1 for rr in val_results if rr.status == "PASS")
    fail_count = sum(1 for rr in val_results if rr.status == "FAIL")
    warn_count = sum(1 for rr in val_results if rr.status == "WARN")
    m1, m2, m3 = st.columns(3)
    m1.metric("Rules Passed",  pass_count)
    m2.metric("Rules Failed",  fail_count)
    m3.metric("Rules Warning", warn_count)
    for rr in val_results:
        status_color = {"PASS": "🟢", "WARN": "🟡", "FAIL": "🔴"}.get(rr.status, "⚪")
        st.markdown(f"{status_color} **{rr.rule_name}** — {rr.failed:,}/{rr.total:,} rows failed ({rr.fail_pct:.1f}%)")
