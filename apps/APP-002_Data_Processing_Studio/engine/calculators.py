"""Calculation rule implementations for APP-003 Rule Engine."""
import pandas as pd
import numpy as np
from .rule_model import Rule


def _cmp_series(series: pd.Series, op: str, val: str) -> pd.Series:
    """Return boolean mask for series [op] val (numeric-aware)."""
    numeric = pd.to_numeric(series, errors="coerce")
    try:
        num_val = float(val)
        if op == "eq":   return numeric == num_val
        if op == "neq":  return numeric != num_val
        if op == "gt":   return numeric >  num_val
        if op == "gte":  return numeric >= num_val
        if op == "lt":   return numeric <  num_val
        if op == "lte":  return numeric <= num_val
    except (ValueError, TypeError):
        pass
    # Fall back to string comparison
    str_series = series.fillna("").astype(str).str.strip().str.lower()
    val_lower  = str(val).strip().lower()
    if op == "eq":    return str_series == val_lower
    if op == "neq":   return str_series != val_lower
    if op == "contains": return str_series.str.contains(val_lower, na=False, regex=False)
    return pd.Series(False, index=series.index)


def calc_arithmetic(df: pd.DataFrame, rule: Rule) -> tuple:
    """Create new column: col_a [op] col_b."""
    new_col = rule.params.get("new_col", "Result")
    col_a   = rule.params.get("col_a", "")
    col_b   = rule.params.get("col_b", "")
    op      = rule.params.get("op", "add")

    if col_a not in df.columns or col_b not in df.columns:
        return df, f"Arithmetic skipped: column not found"

    a = pd.to_numeric(df[col_a], errors="coerce")
    b = pd.to_numeric(df[col_b], errors="coerce")
    new_df = df.copy()

    if op == "add":          new_df[new_col] = (a + b).round(2)
    elif op == "subtract":   new_df[new_col] = (a - b).round(2)
    elif op == "multiply":   new_df[new_col] = (a * b).round(2)
    elif op == "divide":     new_df[new_col] = (a / b.replace(0, np.nan)).round(4)
    elif op == "divide_pct": new_df[new_col] = (a / b.replace(0, np.nan) * 100).round(1)

    return new_df, f'Calculated "{new_col}" = {col_a} {op} {col_b}'


def calc_conditional(df: pd.DataFrame, rule: Rule) -> tuple:
    """IF condition THEN then_value ELSE else_value → new column."""
    new_col       = rule.params.get("new_col", "Result")
    cond_col      = rule.params.get("condition_col", "")
    cond_op       = rule.params.get("condition_op", "gte")
    cond_val      = str(rule.params.get("condition_val", ""))
    then_value    = rule.params.get("then_value", "")
    else_value    = rule.params.get("else_value", "")
    then_is_col   = rule.params.get("then_is_column", False)
    else_is_col   = rule.params.get("else_is_column", False)

    if cond_col not in df.columns:
        return df, f"Conditional skipped: '{cond_col}' not found"

    mask   = _cmp_series(df[cond_col], cond_op, cond_val)
    new_df = df.copy()

    if then_is_col and then_value in df.columns:
        then_series = df[then_value]
    else:
        then_series = pd.Series(then_value, index=df.index)

    if else_is_col and else_value in df.columns:
        else_series = df[else_value]
    else:
        else_series = pd.Series(else_value, index=df.index)

    new_df[new_col] = else_series
    new_df.loc[mask, new_col] = then_series[mask] if then_is_col else then_value

    return new_df, (f'Conditional "{new_col}": IF "{cond_col}" {cond_op} "{cond_val}" '
                    f'THEN "{then_value}" ELSE "{else_value}"')


def calc_percentage(df: pd.DataFrame, rule: Rule) -> tuple:
    """(numerator / denominator) × 100 → new column."""
    new_col   = rule.params.get("new_col", "Percentage")
    num_col   = rule.params.get("numerator_col", "")
    den_col   = rule.params.get("denominator_col", "")
    decimals  = int(rule.params.get("round_decimals", 1))

    if num_col not in df.columns or den_col not in df.columns:
        return df, f"Percentage skipped: column not found"

    numerator   = pd.to_numeric(df[num_col], errors="coerce")
    denominator = pd.to_numeric(df[den_col], errors="coerce")
    new_df      = df.copy()
    new_df[new_col] = (numerator / denominator.replace(0, np.nan) * 100).round(decimals)

    return new_df, f'Calculated "{new_col}" = ({num_col} / {den_col}) × 100'


def calc_score(df: pd.DataFrame, rule: Rule) -> tuple:
    """Multi-criterion scoring: sum points for each satisfied criterion."""
    new_col   = rule.params.get("new_col", "Score")
    criteria  = rule.params.get("criteria", [])  # list of {column, op, val, points}
    max_score = rule.params.get("max_score", None)

    if not criteria:
        return df, "Score skipped: no criteria defined"

    new_df = df.copy()
    score  = pd.Series(0.0, index=df.index)

    for crit in criteria:
        col    = crit.get("column", "")
        op     = crit.get("op", "gte")
        val    = str(crit.get("val", ""))
        points = float(crit.get("points", 0))

        if col not in df.columns:
            continue

        mask   = _cmp_series(df[col], op, val)
        score += mask.astype(float) * points

    new_df[new_col] = score.round(1)

    if max_score:
        pct_col = f"{new_col} %"
        new_df[pct_col] = (score / float(max_score) * 100).round(1)

    return new_df, f'Scored "{new_col}" across {len(criteria)} criteria'
