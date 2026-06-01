"""Row operations — Filter, Sort, Remove Duplicates, Remove Blanks."""
import pandas as pd
from .transform_model import TransformStep


def apply_filter(df: pd.DataFrame, step: TransformStep) -> tuple:
    conditions = step.params.get("conditions", [])
    logic      = step.params.get("logic", "AND")

    mask = None
    desc_parts = []

    for cond in conditions:
        col = cond.get("column", "")
        op  = cond.get("op", "equals")
        val = str(cond.get("value", ""))

        if col not in df.columns:
            continue

        series = df[col]
        str_series = series.fillna("").astype(str).str.strip()
        num_series = pd.to_numeric(series, errors="coerce")

        if op == "equals":         cond_mask = str_series.str.lower() == val.lower()
        elif op == "not_equals":   cond_mask = str_series.str.lower() != val.lower()
        elif op == "contains":     cond_mask = str_series.str.lower().str.contains(val.lower(), na=False, regex=False)
        elif op == "starts_with":  cond_mask = str_series.str.lower().str.startswith(val.lower())
        elif op == "ends_with":    cond_mask = str_series.str.lower().str.endswith(val.lower())
        elif op == "greater_than": cond_mask = num_series > float(val) if _is_num(val) else pd.Series(False, index=df.index)
        elif op == "less_than":    cond_mask = num_series < float(val) if _is_num(val) else pd.Series(False, index=df.index)
        elif op == "greater_equal":cond_mask = num_series >= float(val) if _is_num(val) else pd.Series(False, index=df.index)
        elif op == "less_equal":   cond_mask = num_series <= float(val) if _is_num(val) else pd.Series(False, index=df.index)
        elif op == "is_blank":     cond_mask = series.isna() | (str_series == "")
        elif op == "is_not_blank": cond_mask = ~(series.isna() | (str_series == ""))
        else:
            continue

        desc_parts.append(f'"{col}" {op.replace("_", " ")} "{val}"')

        if mask is None:
            mask = cond_mask
        elif logic == "AND":
            mask = mask & cond_mask
        else:
            mask = mask | cond_mask

    if mask is None:
        return df, "Filter: no valid conditions"

    before = len(df)
    new_df = df[mask].reset_index(drop=True)
    desc = f"Filter [{logic}]: {', '.join(desc_parts)} → {len(df)} → {len(new_df)} rows"
    return new_df, desc


def apply_sort(df: pd.DataFrame, step: TransformStep) -> tuple:
    sort_by = step.params.get("sort_by", [])
    valid   = [(s["column"], s.get("ascending", True))
               for s in sort_by if s.get("column") in df.columns]
    if not valid:
        return df, "Sort: no valid columns"

    cols, asc = zip(*valid)
    new_df = df.sort_values(by=list(cols), ascending=list(asc)).reset_index(drop=True)
    desc = "Sorted by: " + ", ".join(f'"{c}" {"↑" if a else "↓"}' for c, a in valid)
    return new_df, desc


def apply_remove_duplicates(df: pd.DataFrame, step: TransformStep) -> tuple:
    key_cols = step.params.get("key_cols", [])
    keep     = step.params.get("keep", "first")
    valid    = [c for c in key_cols if c in df.columns]

    if not valid:
        return df, "Remove duplicates: no valid key columns"

    before = len(df)
    new_df = df.drop_duplicates(subset=valid, keep=keep).reset_index(drop=True)
    removed = before - len(new_df)
    return new_df, f"Removed {removed} duplicate rows (key: {', '.join(valid)}, keep={keep})"


def apply_remove_blanks(df: pd.DataFrame, step: TransformStep) -> tuple:
    columns = step.params.get("columns", [])
    mode    = step.params.get("mode", "any")  # any | all
    valid   = [c for c in columns if c in df.columns]

    if not valid:
        return df, "Remove blanks: no valid columns"

    blank_mask = df[valid].isna()
    for c in valid:
        blank_mask[c] = blank_mask[c] | (df[c].astype(str).str.strip() == "")

    remove_mask = blank_mask.any(axis=1) if mode == "any" else blank_mask.all(axis=1)

    before = len(df)
    new_df = df[~remove_mask].reset_index(drop=True)
    removed = before - len(new_df)
    return new_df, f"Removed {removed} rows with blank values in [{mode.upper()}]: {', '.join(valid)}"


def _is_num(s: str) -> bool:
    try:
        float(s)
        return True
    except (ValueError, TypeError):
        return False
