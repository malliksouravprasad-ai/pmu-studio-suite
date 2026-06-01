"""Rule execution engine for APP-003."""
import pandas as pd
from .rule_model import Rule, RuleResult, CALCULATION_TYPES
from .validators import (
    check_required, check_type, check_range, check_pattern,
    check_compare_columns, check_dependency, check_consistency,
)
from .calculators import calc_arithmetic, calc_conditional, calc_percentage, calc_score

_VAL_DISPATCH = {
    "required":          check_required,
    "type_check":        check_type,
    "range_check":       check_range,
    "pattern_check":     check_pattern,
    "compare_columns":   check_compare_columns,
    "dependency_check":  check_dependency,
    "consistency_check": check_consistency,
}

_CALC_DISPATCH = {
    "arithmetic":   calc_arithmetic,
    "conditional":  calc_conditional,
    "percentage":   calc_percentage,
    "score":        calc_score,
}


def run_all_rules(df: pd.DataFrame, rules: list) -> tuple:
    """
    Apply all enabled rules in order.
    Calculation rules modify the DataFrame; validation rules audit it.

    Returns:
        result_df       — original df + any calculated columns
        val_results     — list of RuleResult for validation rules
        all_exceptions  — flat list of exception detail dicts
        calc_log        — list of (rule_name, description) for calc rules
    """
    result_df      = df.copy()
    val_results    = []
    all_exceptions = []
    calc_log       = []

    for rule in rules:
        if not rule.enabled:
            continue

        if rule.rule_type in CALCULATION_TYPES:
            fn = _CALC_DISPATCH.get(rule.rule_type)
            if fn:
                result_df, desc = fn(result_df, rule)
                calc_log.append({"Rule": rule.name, "Type": rule.rule_type, "Description": desc})
        else:
            fn = _VAL_DISPATCH.get(rule.rule_type)
            if fn:
                rr, details = fn(result_df, rule)
                val_results.append(rr)
                all_exceptions.extend([{**d, "Rule": rule.name, "Severity": rule.severity}
                                       for d in details])

    # Add validation status column
    error_rules = [rr for rr in val_results if rr.severity == "error"]
    warn_rules  = [rr for rr in val_results if rr.severity == "warning"]

    fail_rows = set()
    warn_rows = set()
    for rr in error_rules:
        fail_rows.update(rr.failing_rows)
    for rr in warn_rules:
        warn_rows.update(rr.failing_rows) if rr.failing_rows else None

    result_df["_Validation_Status"] = "Valid"
    result_df.loc[list(warn_rows - fail_rows), "_Validation_Status"] = "Warning"
    result_df.loc[list(fail_rows),             "_Validation_Status"] = "Invalid"

    return result_df, val_results, all_exceptions, calc_log


def split_valid_invalid(result_df: pd.DataFrame) -> tuple:
    """Split the result_df into valid and invalid sub-DataFrames."""
    if "_Validation_Status" not in result_df.columns:
        return result_df, pd.DataFrame()
    valid   = result_df[result_df["_Validation_Status"] == "Valid"].drop(
        columns=["_Validation_Status"])
    invalid = result_df[result_df["_Validation_Status"] != "Valid"]
    return valid, invalid
