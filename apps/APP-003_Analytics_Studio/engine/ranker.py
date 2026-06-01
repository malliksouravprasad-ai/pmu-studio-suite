"""Ranking engine for APP-006."""
import pandas as pd
from .analytics_model import RankDef


def rank_entities(df: pd.DataFrame, rdef: RankDef) -> pd.DataFrame:
    if rdef.rank_mode == "weighted":
        return _rank_weighted(df, rdef)
    return _rank_single(df, rdef)


def _rank_single(df: pd.DataFrame, rdef: RankDef) -> pd.DataFrame:
    ec, vc = rdef.entity_col, rdef.value_col
    if ec not in df.columns or vc not in df.columns:
        return pd.DataFrame()

    result = df[[ec, vc]].copy()
    result[vc] = pd.to_numeric(result[vc], errors="coerce")
    result = result.dropna(subset=[vc])
    result = result.groupby(ec, as_index=False)[vc].mean()
    result[vc] = result[vc].round(2)

    # bottom_n shows the worst performers → sort in opposite direction
    asc = (not rdef.ascending) if rdef.rank_mode == "bottom_n" else rdef.ascending
    result = result.sort_values(vc, ascending=asc).reset_index(drop=True)
    result.insert(0, "Rank", range(1, len(result) + 1))

    if rdef.rank_mode in ("top_n", "bottom_n"):
        result = result.head(rdef.top_n).reset_index(drop=True)
        result["Rank"] = range(1, len(result) + 1)

    q75 = result[vc].quantile(0.75)
    q25 = result[vc].quantile(0.25)
    result["Band"] = result[vc].apply(
        lambda v: "High" if v >= q75 else ("Low" if v < q25 else "Medium"))

    return result


def _rank_weighted(df: pd.DataFrame, rdef: RankDef) -> pd.DataFrame:
    ec = rdef.entity_col
    weights = rdef.weight_dict()
    if not weights or ec not in df.columns:
        return pd.DataFrame()

    metric_cols = [c for c in weights if c in df.columns]
    if not metric_cols:
        return pd.DataFrame()

    result = df[[ec] + metric_cols].copy()
    result = result.groupby(ec, as_index=False)[metric_cols].mean()

    if rdef.normalize:
        for col in metric_cols:
            s = pd.to_numeric(result[col], errors="coerce")
            lo, hi = s.min(), s.max()
            if hi > lo:
                result[col] = ((s - lo) / (hi - lo) * 100).round(2)
            else:
                result[col] = 100.0
            # invert for lower-is-better columns
            if col in rdef.invert_cols:
                result[col] = (100 - result[col]).round(2)

    total_w = sum(weights.get(c, 0) for c in metric_cols)
    result["Composite Score"] = 0.0
    for col in metric_cols:
        w = weights.get(col, 0) / total_w if total_w > 0 else 0
        result["Composite Score"] += pd.to_numeric(result[col], errors="coerce").fillna(0) * w
    result["Composite Score"] = result["Composite Score"].round(2)

    result = result.sort_values("Composite Score", ascending=False).reset_index(drop=True)
    result.insert(0, "Rank", range(1, len(result) + 1))
    return result
