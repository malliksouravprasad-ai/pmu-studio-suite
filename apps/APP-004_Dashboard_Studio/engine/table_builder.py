"""Summary table builder for APP-007."""
import pandas as pd
from .viz_model import TableDef

_PANDAS_FUNC = {
    "sum": "sum", "avg": "mean", "count": "count",
    "min": "min", "max": "max", "distinct_count": "nunique",
}


def build_table(df: pd.DataFrame, tdef: TableDef) -> pd.DataFrame:
    """Aggregate df per TableDef. Returns formatted DataFrame with optional TOTAL row."""
    group_cols = [c for c in tdef.group_cols if c in df.columns]
    metric_cols = [c for c in tdef.metric_cols if c in df.columns]

    if not group_cols or not metric_cols:
        return pd.DataFrame()

    agg_spec = {c: _PANDAS_FUNC.get(tdef.agg_funcs.get(c, "sum"), "sum")
                for c in metric_cols}
    result = df.groupby(group_cols, as_index=False).agg(agg_spec)

    for c in metric_cols:
        result[c] = pd.to_numeric(result[c], errors="coerce").round(2)

    sort_col = tdef.sort_col if tdef.sort_col in result.columns else ""
    if sort_col:
        result = result.sort_values(sort_col, ascending=tdef.sort_asc)

    if tdef.top_n > 0:
        result = result.head(tdef.top_n)

    result = result.reset_index(drop=True)

    if tdef.include_totals:
        total_row = {gc: ("TOTAL" if i == 0 else "") for i, gc in enumerate(group_cols)}
        for c in metric_cols:
            func = tdef.agg_funcs.get(c, "sum")
            s = pd.to_numeric(df[c], errors="coerce")
            if func == "sum":            total_row[c] = round(float(s.sum()), 2)
            elif func == "avg":          total_row[c] = round(float(s.mean()), 2)
            elif func == "count":        total_row[c] = int(df[c].notna().sum())
            elif func == "min":          total_row[c] = round(float(s.min()), 2)
            elif func == "max":          total_row[c] = round(float(s.max()), 2)
            elif func == "distinct_count": total_row[c] = int(df[c].nunique())
            else:                        total_row[c] = round(float(s.sum()), 2)
        result = pd.concat([result, pd.DataFrame([total_row])], ignore_index=True)

    return result


def build_all_tables(df: pd.DataFrame, tables: list) -> dict:
    """Returns {table_id: DataFrame}."""
    return {t.table_id: build_table(df, t) for t in tables if t.enabled}
