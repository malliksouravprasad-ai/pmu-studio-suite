"""Variance analysis engine for APP-006."""
import pandas as pd
from .analytics_model import VarianceDef


def calc_variance(df: pd.DataFrame, vdef: VarianceDef) -> pd.DataFrame:
    if vdef.variance_mode == "target_vs_achievement":
        return _target_vs_achievement(df, vdef)
    if vdef.variance_mode == "period_diff":
        return _period_diff(df, vdef)
    if vdef.variance_mode == "growth":
        return _growth_rate(df, vdef)
    return pd.DataFrame()


def _target_vs_achievement(df: pd.DataFrame, vdef: VarianceDef) -> pd.DataFrame:
    ec, ac = vdef.entity_col, vdef.actual_col
    if ec not in df.columns or ac not in df.columns:
        return pd.DataFrame()

    if vdef.target_col and vdef.target_col in df.columns:
        result = df[[ec, ac, vdef.target_col]].copy()
        result[ac] = pd.to_numeric(result[ac], errors="coerce")
        result[vdef.target_col] = pd.to_numeric(result[vdef.target_col], errors="coerce")
        result = result.groupby(ec, as_index=False).agg({ac: "mean", vdef.target_col: "mean"})
        result = result.rename(columns={ac: "Actual", vdef.target_col: "Target"})
    elif vdef.target_fixed is not None:
        result = df[[ec, ac]].copy()
        result[ac] = pd.to_numeric(result[ac], errors="coerce")
        result = result.groupby(ec, as_index=False).agg({ac: "mean"})
        result = result.rename(columns={ac: "Actual"})
        result["Target"] = float(vdef.target_fixed)
    else:
        return pd.DataFrame()

    result["Actual"] = result["Actual"].round(2)
    result["Target"] = result["Target"].round(2)
    result["Gap"] = (result["Actual"] - result["Target"]).round(2)
    result["Achievement %"] = (
        result["Actual"] / result["Target"].replace(0, float("nan")) * 100
    ).round(1)

    def _status(pct):
        if pd.isna(pct):  return "N/A"
        if pct >= 100:    return "On Target"
        if pct >= 80:     return "Near Target"
        if pct >= 60:     return "Below Target"
        return "Critical"

    result["Status"] = result["Achievement %"].apply(_status)
    result = result.sort_values("Achievement %", ascending=False).reset_index(drop=True)
    result.insert(0, "Rank", range(1, len(result) + 1))
    return result


def _period_diff(df: pd.DataFrame, vdef: VarianceDef) -> pd.DataFrame:
    ec, ca, cb = vdef.entity_col, vdef.period_a_col, vdef.period_b_col
    if not all(c in df.columns for c in [ec, ca, cb]):
        return pd.DataFrame()

    result = df[[ec, ca, cb]].copy()
    result[ca] = pd.to_numeric(result[ca], errors="coerce")
    result[cb] = pd.to_numeric(result[cb], errors="coerce")
    result = result.groupby(ec, as_index=False).agg({ca: "mean", cb: "mean"})
    result[ca] = result[ca].round(2)
    result[cb] = result[cb].round(2)
    result["Absolute Change"] = (result[cb] - result[ca]).round(2)
    result["Change %"] = (
        (result[cb] - result[ca]) / result[ca].replace(0, float("nan")) * 100
    ).round(1)
    result["Direction"] = result["Absolute Change"].apply(
        lambda x: "Improved" if x > 0 else ("Declined" if x < 0 else "No Change"))
    return result.sort_values("Change %", ascending=False).reset_index(drop=True)


def _growth_rate(df: pd.DataFrame, vdef: VarianceDef) -> pd.DataFrame:
    ec, ca, cb = vdef.entity_col, vdef.period_a_col, vdef.period_b_col
    if not all(c in df.columns for c in [ec, ca, cb]):
        return pd.DataFrame()

    result = df[[ec, ca, cb]].copy()
    result[ca] = pd.to_numeric(result[ca], errors="coerce")
    result[cb] = pd.to_numeric(result[cb], errors="coerce")
    result = result.groupby(ec, as_index=False).agg({ca: "mean", cb: "mean"})
    result["Growth Rate %"] = (
        (result[cb] - result[ca]) / result[ca].replace(0, float("nan")) * 100
    ).round(1)
    result["Absolute Growth"] = (result[cb] - result[ca]).round(2)
    result["Status"] = result["Growth Rate %"].apply(
        lambda x: "Positive" if (pd.notna(x) and x > 0)
                  else ("Negative" if (pd.notna(x) and x < 0) else "Flat"))
    return result.sort_values("Growth Rate %", ascending=False).reset_index(drop=True)
