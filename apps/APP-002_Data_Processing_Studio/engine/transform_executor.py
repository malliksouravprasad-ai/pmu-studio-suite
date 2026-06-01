"""Execute a list of TransformSteps against a DataFrame."""
import pandas as pd
from .transform_model import TransformStep
from .column_ops import (
    apply_rename, apply_reorder, apply_delete,
    apply_merge_columns, apply_split_column,
    apply_format_column, apply_create_column,
    apply_fill_missing_value, apply_fill_missing_stat,
)
from .row_ops import (
    apply_filter, apply_sort,
    apply_remove_duplicates, apply_remove_blanks,
)

_DISPATCH = {
    "rename":               apply_rename,
    "reorder":              apply_reorder,
    "delete":               apply_delete,
    "merge_columns":        apply_merge_columns,
    "split_column":         apply_split_column,
    "format_column":        apply_format_column,
    "create_column":        apply_create_column,
    "filter":               apply_filter,
    "sort":                 apply_sort,
    "remove_duplicates":    apply_remove_duplicates,
    "remove_blanks":        apply_remove_blanks,
    "fill_missing_value":   apply_fill_missing_value,
    "fill_missing_stat":    apply_fill_missing_stat,
}


def apply_all(df: pd.DataFrame, steps: list) -> tuple:
    """
    Apply all enabled steps in sequence.
    Returns (transformed_df, log_entries).
    """
    current  = df.copy()
    log      = []
    step_num = 0

    for step in steps:
        if not step.enabled:
            continue

        step_num += 1
        rows_before = len(current)
        cols_before = len(current.columns)

        fn = _DISPATCH.get(step.op_type)
        if fn is None:
            desc = f"Unknown operation: {step.op_type}"
        else:
            try:
                current, desc = fn(current, step)
            except Exception as e:
                desc = f"ERROR in {step.op_type}: {e}"

        log.append({
            "Step":         step_num,
            "Operation":    step.op_type.replace("_", " ").title(),
            "Description":  desc,
            "Rows Before":  rows_before,
            "Rows After":   len(current),
            "Rows Changed": rows_before - len(current),
            "Cols Before":  cols_before,
            "Cols After":   len(current.columns),
        })

    return current, log
