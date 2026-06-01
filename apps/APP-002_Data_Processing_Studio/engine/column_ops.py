"""Column operations — Manager and Transformer."""
import pandas as pd
import numpy as np
from .transform_model import TransformStep


def apply_rename(df: pd.DataFrame, step: TransformStep) -> tuple:
    renames = step.params.get("renames", {})
    valid   = {old: new for old, new in renames.items() if old in df.columns and old != new}
    if not valid:
        return df, "Rename: no changes to apply"
    new_df = df.rename(columns=valid)
    desc = "Renamed: " + ", ".join(f'"{o}" → "{n}"' for o, n in valid.items())
    return new_df, desc


def apply_reorder(df: pd.DataFrame, step: TransformStep) -> tuple:
    order = step.params.get("order", [])
    valid = [c for c in order if c in df.columns]
    rest  = [c for c in df.columns if c not in valid]
    new_df = df[valid + rest]
    return new_df, f"Reordered {len(valid)} columns"


def apply_delete(df: pd.DataFrame, step: TransformStep) -> tuple:
    cols  = step.params.get("columns", [])
    valid = [c for c in cols if c in df.columns]
    if not valid:
        return df, "Delete: no valid columns to remove"
    new_df = df.drop(columns=valid)
    return new_df, f"Deleted: {', '.join(valid)}"


def apply_merge_columns(df: pd.DataFrame, step: TransformStep) -> tuple:
    source_cols  = step.params.get("source_cols", [])
    separator    = step.params.get("separator", " ")
    new_col_name = step.params.get("new_col_name", "Merged")
    drop_sources = step.params.get("drop_sources", False)

    valid = [c for c in source_cols if c in df.columns]
    if len(valid) < 2:
        return df, "Merge: need at least 2 valid source columns"

    new_df = df.copy()
    new_df[new_col_name] = new_df[valid].fillna("").astype(str).apply(
        lambda row: separator.join(v for v in row if v.strip()), axis=1
    )
    if drop_sources:
        new_df = new_df.drop(columns=valid)

    return new_df, f'Merged {", ".join(valid)} → "{new_col_name}" (sep="{separator}")'


def apply_split_column(df: pd.DataFrame, step: TransformStep) -> tuple:
    source_col   = step.params.get("source_col", "")
    delimiter    = step.params.get("delimiter", " ")
    new_col_names = step.params.get("new_col_names", [])
    max_splits   = step.params.get("max_splits", -1)
    drop_source  = step.params.get("drop_source", False)

    if source_col not in df.columns:
        return df, f"Split: column '{source_col}' not found"
    if not new_col_names:
        return df, "Split: no output column names specified"

    split_result = df[source_col].astype(str).str.split(delimiter, n=max_splits, expand=True, regex=False)
    new_df = df.copy()
    for i, name in enumerate(new_col_names):
        if i < split_result.shape[1]:
            new_df[name] = split_result[i].fillna("").astype(str).str.strip()
        else:
            new_df[name] = ""

    if drop_source:
        new_df = new_df.drop(columns=[source_col])

    return new_df, f'Split "{source_col}" on "{delimiter}" → {", ".join(new_col_names)}'


def apply_format_column(df: pd.DataFrame, step: TransformStep) -> tuple:
    column      = step.params.get("column", "")
    format_type = step.params.get("format_type", "")

    if column not in df.columns:
        return df, f"Format: column '{column}' not found"

    new_df = df.copy()

    if format_type == "text_upper":
        new_df[column] = new_df[column].astype(str).str.upper()
    elif format_type == "text_lower":
        new_df[column] = new_df[column].astype(str).str.lower()
    elif format_type == "text_title":
        new_df[column] = new_df[column].astype(str).str.title()
    elif format_type == "text_strip":
        new_df[column] = new_df[column].astype(str).str.strip()
    elif format_type == "prefix_suffix":
        prefix = step.params.get("prefix", "")
        suffix = step.params.get("suffix", "")
        new_df[column] = prefix + new_df[column].fillna("").astype(str) + suffix
    elif format_type == "round_numeric":
        decimals = step.params.get("decimals", 0)
        new_df[column] = pd.to_numeric(new_df[column], errors="coerce").round(int(decimals))
    elif format_type == "to_percentage":
        decimals = step.params.get("decimals", 1)
        numeric = pd.to_numeric(new_df[column], errors="coerce")
        new_df[column] = numeric.round(int(decimals)).astype(str) + "%"
    elif format_type == "date_reformat":
        in_fmt  = step.params.get("date_input_format", "%d/%m/%Y")
        out_fmt = step.params.get("date_output_format", "%d %b %Y")
        import warnings
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            parsed = pd.to_datetime(new_df[column], format=in_fmt, errors="coerce")
        new_df[column] = parsed.dt.strftime(out_fmt)

    return new_df, f'Formatted "{column}": {format_type}'


def apply_create_column(df: pd.DataFrame, step: TransformStep) -> tuple:
    new_col_name  = step.params.get("new_col_name", "New Column")
    creation_type = step.params.get("creation_type", "constant")

    new_df = df.copy()

    if creation_type == "constant":
        new_df[new_col_name] = step.params.get("value", "")
    elif creation_type == "copy":
        src = step.params.get("source_col", "")
        if src in df.columns:
            new_df[new_col_name] = df[src].copy()
        else:
            return df, f"Create: source column '{src}' not found"
    elif creation_type == "math":
        col_a = step.params.get("col_a", "")
        col_b = step.params.get("col_b", "")
        op    = step.params.get("op", "add")
        if col_a not in df.columns or col_b not in df.columns:
            return df, f"Create: one or more math columns not found"
        a = pd.to_numeric(df[col_a], errors="coerce")
        b = pd.to_numeric(df[col_b], errors="coerce")
        if op == "add":          new_df[new_col_name] = (a + b).round(2)
        elif op == "subtract":   new_df[new_col_name] = (a - b).round(2)
        elif op == "multiply":   new_df[new_col_name] = (a * b).round(2)
        elif op == "divide":     new_df[new_col_name] = (a / b.replace(0, np.nan)).round(4)
        elif op == "divide_pct": new_df[new_col_name] = (a / b.replace(0, np.nan) * 100).round(1)

    return new_df, f'Created column "{new_col_name}": {creation_type}'


def apply_fill_missing_value(df: pd.DataFrame, step: TransformStep) -> tuple:
    columns    = step.params.get("columns", [])
    fill_value = step.params.get("fill_value", "")
    valid = [c for c in columns if c in df.columns]
    if not valid:
        return df, "Fill missing: no valid columns"
    new_df = df.copy()
    new_df[valid] = new_df[valid].fillna(fill_value)
    return new_df, f'Filled missing values in {", ".join(valid)} with "{fill_value}"'


def apply_fill_missing_stat(df: pd.DataFrame, step: TransformStep) -> tuple:
    column = step.params.get("column", "")
    stat   = step.params.get("stat", "mean")
    if column not in df.columns:
        return df, f"Fill missing stat: column '{column}' not found"
    new_df = df.copy()
    if stat == "mean":
        val = pd.to_numeric(new_df[column], errors="coerce").mean()
    elif stat == "median":
        val = pd.to_numeric(new_df[column], errors="coerce").median()
    else:  # mode
        mode_result = new_df[column].mode()
        val = mode_result.iloc[0] if not mode_result.empty else ""
    new_df[column] = new_df[column].fillna(val)
    return new_df, f'Filled missing in "{column}" with {stat} ({val})'
