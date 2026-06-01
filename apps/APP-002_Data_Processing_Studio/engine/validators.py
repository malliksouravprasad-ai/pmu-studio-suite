"""Validation rule implementations for APP-003 Rule Engine."""
import re
import pandas as pd
import numpy as np
from .rule_model import Rule, RuleResult, PATTERN_PRESETS


def _make_result(rule: Rule, total: int, failing_rows: list, details: list) -> RuleResult:
    passed  = total - len(failing_rows)
    failed  = len(failing_rows)
    pct     = round(failed / total * 100, 1) if total > 0 else 0.0
    status  = "PASS" if failed == 0 else ("WARN" if rule.severity == "warning" else "FAIL")
    return RuleResult(
        rule_id=rule.rule_id, rule_name=rule.name, rule_type=rule.rule_type,
        severity=rule.severity, total=total, passed=passed, failed=failed,
        fail_pct=pct, status=status, failing_rows=failing_rows, error_details=details,
    )


def _is_blank(series: pd.Series) -> pd.Series:
    return series.isna() | series.astype(str).str.strip().str.lower().isin(["", "nan", "none", "n/a"])


def _detail(row_idx, col, val, msg) -> dict:
    return {"Row #": row_idx + 2, "Column": col, "Value": str(val)[:80], "Message": msg}


# ── Field Validation ──────────────────────────────────────────────────────────

def check_required(df: pd.DataFrame, rule: Rule) -> tuple:
    columns  = rule.params.get("columns", [])
    failing  = []
    details  = []
    for col in columns:
        if col not in df.columns:
            continue
        blank_mask = _is_blank(df[col])
        for idx in df.index[blank_mask]:
            if idx not in failing:
                failing.append(idx)
            details.append(_detail(idx, col, "", f"'{col}' is required but blank"))
    return _make_result(rule, len(df), failing, details), details


def check_type(df: pd.DataFrame, rule: Rule) -> tuple:
    column   = rule.params.get("column", "")
    exp_type = rule.params.get("expected_type", "numeric")
    if column not in df.columns:
        return _make_result(rule, len(df), [], []), []

    series  = df[column]
    failing = []
    details = []

    for idx, val in series.items():
        if pd.isna(val):
            continue  # nulls caught by required check
        ok = True
        if exp_type == "numeric":
            try: float(str(val))
            except ValueError: ok = False
        elif exp_type == "positive_numeric":
            try:
                v = float(str(val))
                if v < 0: ok = False
            except ValueError: ok = False
        elif exp_type == "integer":
            try:
                v = float(str(val))
                if v != int(v): ok = False
            except ValueError: ok = False
        elif exp_type == "date":
            try:
                pd.to_datetime(str(val), dayfirst=True)
            except Exception: ok = False

        if not ok:
            failing.append(idx)
            details.append(_detail(idx, column, val, f"Expected {exp_type}, got: '{val}'"))

    return _make_result(rule, len(df), failing, details), details


def check_range(df: pd.DataFrame, rule: Rule) -> tuple:
    column  = rule.params.get("column", "")
    min_val = rule.params.get("min_val")
    max_val = rule.params.get("max_val")
    if column not in df.columns:
        return _make_result(rule, len(df), [], []), []

    numeric = pd.to_numeric(df[column], errors="coerce")
    failing = []
    details = []

    for idx, val in numeric.items():
        if pd.isna(val):
            continue
        if min_val is not None and val < float(min_val):
            failing.append(idx)
            details.append(_detail(idx, column, val, f"{val} < min ({min_val})"))
        elif max_val is not None and val > float(max_val):
            failing.append(idx)
            details.append(_detail(idx, column, val, f"{val} > max ({max_val})"))

    return _make_result(rule, len(df), failing, details), details


def check_pattern(df: pd.DataFrame, rule: Rule) -> tuple:
    column       = rule.params.get("column", "")
    preset       = rule.params.get("pattern_preset", "custom")
    custom_regex = rule.params.get("custom_regex", "")

    if column not in df.columns:
        return _make_result(rule, len(df), [], []), []

    if preset in PATTERN_PRESETS and preset != "custom":
        regex = PATTERN_PRESETS[preset][0]
    else:
        regex = custom_regex

    if not regex:
        return _make_result(rule, len(df), [], []), []

    try:
        compiled = re.compile(regex)
    except re.error as e:
        return _make_result(rule, len(df), [], []), []

    def _to_str(x):
        # Excel often reads numeric codes (UDISE, phone, etc.) as floats.
        # Convert integer-valued floats (e.g. 21105110402.0) to plain int strings
        # so that regex patterns like ^\d{11}$ match correctly.
        try:
            f = float(x)
            if f == int(f) and abs(f) < 1e15:
                return str(int(f))
        except (ValueError, TypeError, OverflowError):
            pass
        return str(x).strip()

    series  = df[column].dropna().apply(_to_str)
    failing = []
    details = []

    for idx, val in series.items():
        if val.lower() in ("nan", "none", "n/a", ""):
            continue
        if not compiled.match(val):
            failing.append(idx)
            details.append(_detail(idx, column, val, f"Does not match pattern '{preset}': '{val}'"))

    return _make_result(rule, len(df), failing, details), details


# ── Cross-Field Validation ────────────────────────────────────────────────────

def _cmp(a, op: str, b) -> bool:
    try:
        a, b = float(a), float(b)
    except (ValueError, TypeError):
        a, b = str(a), str(b)
    if op == "eq":  return a == b
    if op == "neq": return a != b
    if op == "gt":  return a >  b
    if op == "gte": return a >= b
    if op == "lt":  return a <  b
    if op == "lte": return a <= b
    return False


def check_compare_columns(df: pd.DataFrame, rule: Rule) -> tuple:
    col_a = rule.params.get("col_a", "")
    col_b = rule.params.get("col_b", "")
    op    = rule.params.get("op", "gte")
    msg   = rule.params.get("message", f"{col_a} {op} {col_b}")

    if col_a not in df.columns or col_b not in df.columns:
        return _make_result(rule, len(df), [], []), []

    num_a = pd.to_numeric(df[col_a], errors="coerce")
    num_b = pd.to_numeric(df[col_b], errors="coerce")
    failing = []
    details = []

    for idx in df.index:
        a, b = num_a.loc[idx], num_b.loc[idx]
        if pd.isna(a) or pd.isna(b):
            continue
        if not _cmp(a, op, b):
            failing.append(idx)
            details.append(_detail(idx, f"{col_a} vs {col_b}", f"{a} vs {b}", msg))

    return _make_result(rule, len(df), failing, details), details


def check_dependency(df: pd.DataFrame, rule: Rule) -> tuple:
    if_col   = rule.params.get("if_col", "")
    if_op    = rule.params.get("if_op", "is_not_blank")
    if_val   = rule.params.get("if_val", "")
    then_col = rule.params.get("then_col", "")

    if if_col not in df.columns or then_col not in df.columns:
        return _make_result(rule, len(df), [], []), []

    failing = []
    details = []

    for idx, row in df.iterrows():
        a_val = row[if_col]
        # Evaluate the IF condition
        if if_op == "is_not_blank":
            condition_met = not (pd.isna(a_val) or str(a_val).strip() == "")
        elif if_op == "is_blank":
            condition_met = pd.isna(a_val) or str(a_val).strip() == ""
        elif if_op == "equals":
            condition_met = str(a_val).strip().lower() == str(if_val).strip().lower()
        elif if_op == "not_equals":
            condition_met = str(a_val).strip().lower() != str(if_val).strip().lower()
        else:
            condition_met = False

        if condition_met:
            b_val = row[then_col]
            if pd.isna(b_val) or str(b_val).strip() in ("", "nan", "none", "n/a"):
                failing.append(idx)
                details.append(_detail(idx, then_col, "",
                    f"'{then_col}' must not be blank when '{if_col}' {if_op} '{if_val}'"))

    return _make_result(rule, len(df), failing, details), details


def check_consistency(df: pd.DataFrame, rule: Rule) -> tuple:
    addend_cols = rule.params.get("addend_cols", [])
    sum_col     = rule.params.get("sum_col", "")
    tolerance   = float(rule.params.get("tolerance", 0))

    valid_addends = [c for c in addend_cols if c in df.columns]
    if not valid_addends or sum_col not in df.columns:
        return _make_result(rule, len(df), [], []), []

    num_addends = df[valid_addends].apply(pd.to_numeric, errors="coerce").sum(axis=1)
    num_sum     = pd.to_numeric(df[sum_col], errors="coerce")
    failing     = []
    details     = []

    for idx in df.index:
        expected = num_addends.loc[idx]
        actual   = num_sum.loc[idx]
        if pd.isna(expected) or pd.isna(actual):
            continue
        if abs(expected - actual) > tolerance:
            failing.append(idx)
            details.append(_detail(idx, sum_col, actual,
                f"Expected {expected:.2f} (sum of {'+'.join(valid_addends)}), "
                f"got {actual:.2f} (diff={abs(expected-actual):.2f})"))

    return _make_result(rule, len(df), failing, details), details
