"""
KPI Engine — define, calculate, and score KPIs.

Supports three formula types:
  value       — use a column directly as the KPI value
  ratio       — numerator / denominator
  percentage  — (numerator / denominator) × 100

Each KPI can have a target (fixed or column-based). Achievement and
weighted scores are computed automatically.
"""
import dataclasses
from dataclasses import dataclass, field
from typing import Optional
from uuid import uuid4

import numpy as np
import pandas as pd


KPI_FORMULAS = {
    "value":      "Direct value — use column as-is",
    "ratio":      "Ratio — numerator ÷ denominator",
    "percentage": "Percentage — (numerator ÷ denominator) × 100",
}

KPI_INTERPRETATIONS = {
    "higher_better": "Higher is better (attendance, enrolment, score)",
    "lower_better":  "Lower is better (dropout rate, pendency, errors)",
}


@dataclass
class KPIDef:
    kpi_id:           str   = field(default_factory=lambda: uuid4().hex[:8].upper())
    name:             str   = ""
    formula:          str   = "value"         # value | ratio | percentage
    value_col:        str   = ""
    numerator_col:    str   = ""
    denominator_col:  str   = ""
    target:           Optional[float] = None  # fixed target for all rows
    target_col:       str   = ""              # per-row target column
    weight:           float = 1.0
    interpretation:   str   = "higher_better"
    enabled:          bool  = True


# ── Core calculation ──────────────────────────────────────────────────────────

def _kpi_raw_value(df: pd.DataFrame, kpi: KPIDef) -> pd.Series:
    if kpi.formula == "value" and kpi.value_col in df.columns:
        return pd.to_numeric(df[kpi.value_col], errors="coerce")
    if kpi.formula in ("ratio", "percentage"):
        num = pd.to_numeric(df.get(kpi.numerator_col, pd.Series(dtype=float)), errors="coerce")
        den = pd.to_numeric(df.get(kpi.denominator_col, pd.Series(dtype=float)), errors="coerce")
        ratio = num / den.replace(0, np.nan)
        return (ratio * 100).round(2) if kpi.formula == "percentage" else ratio.round(4)
    return pd.Series([np.nan] * len(df), index=df.index)


def _achievement(values: pd.Series, kpi: KPIDef, df: pd.DataFrame) -> pd.Series:
    if kpi.target_col and kpi.target_col in df.columns:
        target = pd.to_numeric(df[kpi.target_col], errors="coerce")
    elif kpi.target is not None:
        target = pd.Series([float(kpi.target)] * len(df), index=df.index)
    else:
        return pd.Series([np.nan] * len(df), index=df.index)
    return (values / target.replace(0, np.nan) * 100).round(2)


def _score(achievement: pd.Series, kpi: KPIDef) -> pd.Series:
    bounded = achievement.clip(0, 200)
    if kpi.interpretation == "lower_better":
        normalized = (200 - bounded).clip(0, 100)
    else:
        normalized = bounded.clip(0, 100)
    return (normalized * kpi.weight).round(3)


def calculate_kpis(df: pd.DataFrame, kpi_defs: list) -> tuple:
    """
    Calculate all enabled KPIs against df.

    Returns:
        result_df   — original df with KPI value, achievement%, and score columns appended
        kpi_summary — list of per-KPI stat dicts (for reporting)
    """
    enabled       = [k for k in kpi_defs if k.enabled]
    result_df     = df.copy()
    kpi_summary   = []
    weighted_cols = []
    total_weight  = sum(k.weight for k in enabled) or 1.0

    for kpi in enabled:
        values  = _kpi_raw_value(df, kpi)
        ach     = _achievement(values, kpi, df)
        score   = _score(ach, kpi)

        v_col   = kpi.name
        a_col   = f"{kpi.name} Achievement%"
        s_col   = f"{kpi.name} Score"

        result_df[v_col] = values
        result_df[a_col] = ach
        result_df[s_col] = score
        weighted_cols.append((s_col, kpi.weight))

        kpi_summary.append({
            "KPI":                kpi.name,
            "Formula":            kpi.formula,
            "Interpretation":     KPI_INTERPRETATIONS.get(kpi.interpretation, kpi.interpretation),
            "Target":             kpi.target if kpi.target is not None else (kpi.target_col or "—"),
            "Weight":             kpi.weight,
            "Mean Value":         round(float(values.mean()), 3) if values.notna().any() else "—",
            "Mean Achievement%":  round(float(ach.mean()), 2) if ach.notna().any() else "—",
        })

    if weighted_cols:
        composite = sum(result_df[sc] * w for sc, w in weighted_cols) / total_weight
        result_df["Composite Score"] = composite.round(2)

    return result_df, kpi_summary
