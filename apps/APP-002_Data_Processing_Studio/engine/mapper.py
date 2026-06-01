"""Apply approved match decisions to a DataFrame."""
import pandas as pd
from .mapping_model import ColumnMapping, MatchResult, MATCH_STATUSES


def _resolved_value(r: MatchResult) -> tuple:
    """Return (mapped_value, status_label) for a MatchResult."""
    if r.status in ("exact", "variant", "approved"):
        return r.canonical_value, MATCH_STATUSES[r.status]
    if r.status == "manual":
        return r.canonical_value, MATCH_STATUSES["manual"]
    if r.status == "rejected":
        return r.input_value, MATCH_STATUSES["rejected"]
    if r.status == "blank":
        return "", MATCH_STATUSES["blank"]
    # pending or unmatched → keep original
    return r.input_value, MATCH_STATUSES.get(r.status, "Unmatched")


def apply_column_mapping(
    df: pd.DataFrame, cm: ColumnMapping, results: dict
) -> pd.DataFrame:
    """Apply one ColumnMapping to df. Returns modified copy."""
    if cm.source_col not in df.columns:
        return df

    out = df.copy()
    mapped_col  = f"{cm.source_col}_Mapped" if cm.create_new_col else cm.source_col
    status_col  = f"{cm.source_col}_Match_Status"

    def _map_row(val):
        v = str(val).strip() if pd.notna(val) else ""
        r = results.get(v)
        if r is None:
            return val, "No Result"
        mv, sl = _resolved_value(r)
        return mv, sl

    mapped_vals  = []
    status_vals  = []
    for val in out[cm.source_col]:
        mv, sl = _map_row(val)
        mapped_vals.append(mv)
        status_vals.append(sl)

    out[mapped_col] = mapped_vals
    out[status_col] = status_vals
    return out


def apply_all_mappings(
    df: pd.DataFrame,
    column_mappings: list,
    match_results_by_col: dict,
) -> pd.DataFrame:
    """Apply all configured column mappings. Returns final DataFrame."""
    result = df.copy()
    for cm in column_mappings:
        results = match_results_by_col.get(cm.mapping_id, {})
        result = apply_column_mapping(result, cm, results)
    return result


def get_unmatched_df(mapped_df: pd.DataFrame, column_mappings: list) -> pd.DataFrame:
    """Extract rows where any column has Unmatched status."""
    status_cols = [f"{cm.source_col}_Match_Status" for cm in column_mappings
                   if f"{cm.source_col}_Match_Status" in mapped_df.columns]
    if not status_cols:
        return pd.DataFrame()

    unmatched_mask = pd.Series(False, index=mapped_df.index)
    for sc in status_cols:
        unmatched_mask |= mapped_df[sc].str.contains("Unmatched", na=False)

    return mapped_df[unmatched_mask].reset_index(drop=True)
