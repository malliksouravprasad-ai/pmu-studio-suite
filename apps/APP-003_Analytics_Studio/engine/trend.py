"""Trend analysis engine for APP-006."""
import pandas as pd
import numpy as np
from .analytics_model import TrendDef


def analyze_trend(df: pd.DataFrame, tdef: TrendDef) -> dict:
    """Returns {"main": DataFrame, "growth_matrix": DataFrame}."""
    ec = tdef.entity_col
    period_cols = [c for c in tdef.period_cols if c in df.columns]

    if not period_cols or ec not in df.columns:
        return {"main": pd.DataFrame(), "growth_matrix": pd.DataFrame()}

    result = df[[ec] + period_cols].copy()
    result = result.groupby(ec, as_index=False)[period_cols].mean()
    for c in period_cols:
        result[c] = pd.to_numeric(result[c], errors="coerce").round(2)

    if len(period_cols) >= 2:
        first, last = period_cols[0], period_cols[-1]
        result["Overall Change"] = (result[last] - result[first]).round(2)
        result["Overall Change %"] = (
            (result[last] - result[first]) / result[first].replace(0, float("nan")) * 100
        ).round(1)

        def _dir(row):
            vals = [row[c] for c in period_cols if pd.notna(row[c])]
            if len(vals) < 2:
                return "Insufficient Data"
            slope = float(np.polyfit(range(len(vals)), vals, 1)[0])
            if abs(slope) < 1e-9:
                return "Stable"
            improving = slope > 0
            if tdef.value_interpretation == "lower_better":
                improving = not improving
            return "Improving" if improving else "Declining"

        result["Trend"] = result.apply(_dir, axis=1)

        threshold = tdef.change_threshold_pct

        def _alert(row):
            pct = row.get("Overall Change %")
            if pd.isna(pct):
                return "—"
            gain = pct >= threshold
            drop = pct <= -threshold
            if tdef.value_interpretation == "lower_better":
                gain, drop = drop, gain
            if gain:  return "Significant Gain"
            if drop:  return "Significant Drop"
            return "Stable"

        result["Alert"] = result.apply(_alert, axis=1)
        result = result.sort_values("Overall Change %", ascending=False).reset_index(drop=True)

    gdf = _growth_matrix(result, ec, period_cols)
    return {"main": result, "growth_matrix": gdf}


def _growth_matrix(result: pd.DataFrame, ec: str, period_cols: list) -> pd.DataFrame:
    if len(period_cols) < 2:
        return pd.DataFrame()
    gdf = result[[ec]].copy().reset_index(drop=True)
    for i in range(1, len(period_cols)):
        prev, curr = period_cols[i - 1], period_cols[i]
        col_name = f"{prev}->{curr} %"
        ps = result[prev]
        cs = result[curr]
        gdf[col_name] = ((cs - ps) / ps.replace(0, float("nan")) * 100).round(1)
    return gdf
