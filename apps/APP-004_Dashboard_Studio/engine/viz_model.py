"""Data models for APP-007 Visualization Builder."""
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from uuid import uuid4


CHART_TYPES = {
    "column": "Column Chart — vertical bars (category comparison)",
    "bar":    "Bar Chart — horizontal bars (long labels / rankings)",
    "line":   "Line Chart — trend and time-series",
    "area":   "Area Chart — cumulative trend",
    "pie":    "Pie Chart — share / proportion (single metric only)",
}

AGG_FUNCS = {
    "sum":            "SUM — Total",
    "avg":            "AVERAGE — Mean",
    "count":          "COUNT — Number of records",
    "min":            "MIN — Minimum",
    "max":            "MAX — Maximum",
    "distinct_count": "DISTINCT COUNT — Unique values",
}

_CARD_COLORS = [
    "1F3864",  # navy
    "375623",  # dark green
    "7B2C2C",  # maroon
    "2D6A7A",  # teal
    "7F4E22",  # dark orange
    "4C3B6E",  # purple
]

STATUS_COLORS = {
    "good":    "375623",
    "warn":    "7F6000",
    "bad":     "C00000",
    "neutral": "1F3864",
}


def card_color(index: int, status: str = "neutral") -> str:
    if status != "neutral":
        return STATUS_COLORS.get(status, _CARD_COLORS[0])
    return _CARD_COLORS[index % len(_CARD_COLORS)]


@dataclass
class KPIDef:
    kpi_id: str = field(default_factory=lambda: uuid4().hex[:8].upper())
    title: str = ""
    source_col: str = ""
    agg_func: str = "sum"
    unit: str = ""                    # suffix like "%", " Cr", " lakh"
    comparison_type: str = "none"    # "none" | "fixed" | "column"
    target_value: Optional[float] = None
    target_col: str = ""
    target_agg: str = "sum"
    higher_is_better: bool = True
    enabled: bool = True


@dataclass
class ChartDef:
    chart_id: str = field(default_factory=lambda: uuid4().hex[:8].upper())
    title: str = ""
    chart_type: str = "column"       # column | bar | line | area | pie
    x_col: str = ""
    y_cols: List[str] = field(default_factory=list)
    agg_func: str = "sum"
    top_n: int = 0                   # 0 = no limit
    sort_col: str = ""
    sort_asc: bool = False
    stacked: bool = False
    enabled: bool = True


@dataclass
class TableDef:
    table_id: str = field(default_factory=lambda: uuid4().hex[:8].upper())
    title: str = ""
    group_cols: List[str] = field(default_factory=list)
    metric_cols: List[str] = field(default_factory=list)
    agg_funcs: Dict[str, str] = field(default_factory=dict)  # col -> func
    top_n: int = 0
    sort_col: str = ""
    sort_asc: bool = False
    include_totals: bool = True
    enabled: bool = True


@dataclass
class DashboardJob:
    project_code: str = "PMU"
    artifact_id: str = ""
    dashboard_title: str = "PMU Dashboard"
    kpis: List[KPIDef] = field(default_factory=list)
    charts: List[ChartDef] = field(default_factory=list)
    tables: List[TableDef] = field(default_factory=list)
