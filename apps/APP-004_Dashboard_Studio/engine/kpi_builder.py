"""KPI computation engine for APP-007."""
from typing import Any, Dict, List
import pandas as pd
from .viz_model import KPIDef

_PANDAS_FUNC = {
    "sum": "sum", "avg": "mean", "count": "count",
    "min": "min", "max": "max", "distinct_count": "nunique",
}


def _agg(series: pd.Series, func: str) -> float:
    s = pd.to_numeric(series, errors="coerce")
    if func == "sum":            return round(float(s.sum()), 2)
    if func == "avg":            return round(float(s.mean()), 2) if s.notna().any() else 0.0
    if func == "count":          return float(int(series.notna().sum()))
    if func == "min":            return round(float(s.min()), 2)
    if func == "max":            return round(float(s.max()), 2)
    if func == "distinct_count": return float(int(series.nunique()))
    return round(float(s.sum()), 2)


def _fmt(value, unit: str) -> str:
    unit = unit or ""
    if value is None:
        return "—"
    if isinstance(value, (int, float)):
        v = float(value)
        if v >= 10_000_000:
            return f"{v/10_000_000:.1f} Cr{unit}"
        if v >= 100_000:
            return f"{v/100_000:.1f} L{unit}"
        if v != int(v):
            return f"{v:,.1f}{unit}"
        return f"{int(v):,}{unit}"
    return f"{value}{unit}"


def compute_kpi(df: pd.DataFrame, kdef: KPIDef) -> Dict[str, Any]:
    if kdef.source_col not in df.columns:
        return {"value": None, "target": None, "change": None,
                "status": "neutral", "formatted": "—",
                "title": kdef.title, "unit": kdef.unit}

    value = _agg(df[kdef.source_col], kdef.agg_func)

    target = None
    if kdef.comparison_type == "fixed" and kdef.target_value is not None:
        target = float(kdef.target_value)
    elif kdef.comparison_type == "column" and kdef.target_col in df.columns:
        target = _agg(df[kdef.target_col], kdef.target_agg)

    change = None
    status = "neutral"
    if target is not None:
        if target != 0:
            change = round((value - target) / abs(target) * 100, 1)
        if kdef.higher_is_better:
            status = "good" if value >= target else ("warn" if value >= target * 0.8 else "bad")
        else:
            status = "good" if value <= target else ("warn" if value <= target * 1.2 else "bad")

    return {
        "value": value,
        "target": target,
        "change": change,
        "status": status,
        "formatted": _fmt(value, kdef.unit),
        "target_fmt": _fmt(target, kdef.unit) if target is not None else None,
        "change_str": (f"+{change}%" if change and change > 0 else f"{change}%") if change is not None else "",
        "title": kdef.title,
        "unit": kdef.unit,
        "kpi_id": kdef.kpi_id,
    }


def compute_all_kpis(df: pd.DataFrame, kpis: List[KPIDef]) -> List[Dict[str, Any]]:
    return [compute_kpi(df, k) for k in kpis if k.enabled]
