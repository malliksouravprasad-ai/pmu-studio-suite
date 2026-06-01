"""Aggregation engine for APP-005."""
import pandas as pd
import numpy as np
from .agg_model import AggConfig, MetricDef

_PANDAS_FUNC = {
    "sum":   "sum",
    "count": "count",
    "avg":   "mean",
    "min":   "min",
    "max":   "max",
    "distinct_count": "nunique",
}


def _col_total(df: pd.DataFrame, m: MetricDef):
    """Compute the grand-total value for a metric across the whole DataFrame."""
    series = pd.to_numeric(df[m.source_col], errors="coerce") if m.agg_func != "distinct_count" \
        else df[m.source_col]
    if m.agg_func == "sum":           return round(float(series.sum()), 2)
    if m.agg_func == "count":         return int(df[m.source_col].notna().sum())
    if m.agg_func == "avg":           return round(float(series.mean()), 2) if series.notna().any() else None
    if m.agg_func == "min":           return series.min()
    if m.agg_func == "max":           return series.max()
    if m.agg_func == "distinct_count":return int(df[m.source_col].nunique())
    return None


def _run_groupby(
    df: pd.DataFrame,
    group_cols: list,
    metrics: list,
    include_totals: bool,
    sort_by: str,
    sort_asc: bool,
) -> pd.DataFrame:
    """Run groupby aggregation and return result DataFrame."""
    enabled = [m for m in metrics if m.enabled and m.source_col in df.columns]
    if not enabled:
        return pd.DataFrame()

    if not group_cols:
        # State-level: single totals row
        row = {}
        for m in enabled:
            row[m.effective_alias()] = _col_total(df, m)
        return pd.DataFrame([row])

    # Build pandas agg spec
    agg_spec = {}
    for m in enabled:
        pf = _PANDAS_FUNC.get(m.agg_func, "sum")
        agg_spec[m.effective_alias()] = pd.NamedAgg(column=m.source_col, aggfunc=pf)

    result = (
        df.groupby(group_cols, observed=True, dropna=False)
          .agg(**agg_spec)
          .reset_index()
    )

    # Round averages
    for m in enabled:
        if m.agg_func == "avg":
            alias = m.effective_alias()
            if alias in result.columns:
                result[alias] = result[alias].round(2)

    # Sort before adding totals row
    if sort_by and sort_by in result.columns:
        numeric_sort = pd.to_numeric(result[sort_by], errors="coerce")
        result = result.iloc[numeric_sort.sort_values(ascending=sort_asc).index]
        result = result.reset_index(drop=True)

    # Totals row
    if include_totals:
        total_row = {gc: "TOTAL" for gc in group_cols}
        for m in enabled:
            total_row[m.effective_alias()] = _col_total(df, m)
        result = pd.concat([result, pd.DataFrame([total_row])], ignore_index=True)

    return result


def aggregate_config(df: pd.DataFrame, config: AggConfig) -> dict:
    """
    Run one AggConfig against df.
    Returns {sheet_name: DataFrame}.
    Hierarchical mode produces one DataFrame per grouping level.
    """
    results = {}
    metrics = [m for m in config.metrics if m.enabled]

    if config.hierarchical and len(config.group_cols) >= 2:
        # Level 0: State totals (no grouping)
        results["State Total"] = _run_groupby(
            df, [], metrics, False, "", False)

        # Level 1..N: progressively more group columns
        for i in range(1, len(config.group_cols) + 1):
            level_cols = config.group_cols[:i]
            level_name = " > ".join(level_cols)
            results[level_name] = _run_groupby(
                df, level_cols, metrics,
                config.include_totals, config.sort_by, config.sort_asc)
    else:
        results[config.name or "Summary"] = _run_groupby(
            df, config.group_cols, metrics,
            config.include_totals, config.sort_by, config.sort_asc)

    return results


def run_all_configs(df: pd.DataFrame, configs: list) -> dict:
    """Run all AggConfig objects. Returns {config_id: {sheet_name: DataFrame}}."""
    all_results = {}
    for config in configs:
        all_results[config.config_id] = aggregate_config(df, config)
    return all_results


def compute_stats(result_df: pd.DataFrame, group_cols: list, metrics: list) -> dict:
    """Compute descriptive stats for an aggregation result (excluding TOTAL row)."""
    if result_df.empty:
        return {}
    first_gc = group_cols[0] if group_cols and group_cols[0] in result_df.columns else None
    if first_gc:
        mask = result_df[first_gc].astype(str) != "TOTAL"
        data = result_df[mask]
    else:
        data = result_df

    stats = {"group_count": len(data)}
    for m in metrics:
        alias = m.effective_alias()
        if alias not in data.columns:
            continue
        numeric = pd.to_numeric(data[alias], errors="coerce").dropna()
        if len(numeric) == 0:
            continue
        top_group    = str(data.loc[numeric.idxmax(), first_gc]) if first_gc else "—"
        bottom_group = str(data.loc[numeric.idxmin(), first_gc]) if first_gc else "—"
        stats[alias] = {
            "min": round(float(numeric.min()), 2),
            "max": round(float(numeric.max()), 2),
            "mean": round(float(numeric.mean()), 2),
            "top_group":    top_group,
            "bottom_group": bottom_group,
        }
    return stats
