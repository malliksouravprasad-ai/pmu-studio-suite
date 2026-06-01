"""Data models for APP-005 Aggregation Builder."""
from dataclasses import dataclass, field
from typing import List
from uuid import uuid4

AGG_FUNCS = {
    "sum":          "SUM — Total",
    "count":        "COUNT — Non-blank rows",
    "avg":          "AVERAGE — Mean value",
    "min":          "MIN — Minimum value",
    "max":          "MAX — Maximum value",
    "distinct_count": "DISTINCT COUNT — Unique values",
}

# Keywords used to suggest a default aggregation function for a column
_SUM_KEYWORDS  = ["enrol", "student", "school", "teacher", "total", "count",
                   "num", "no.", "number", "boys", "girls", "staff", "attend"]
_AVG_KEYWORDS  = ["rate", "pct", "percent", "ratio", "score", "avg",
                   "mean", "attendance", "achievement"]


def suggest_agg_func(col_name: str) -> str:
    lower = col_name.lower()
    if any(kw in lower for kw in _AVG_KEYWORDS):
        return "avg"
    return "sum"


@dataclass
class MetricDef:
    metric_id: str = field(default_factory=lambda: uuid4().hex[:8].upper())
    source_col: str = ""
    agg_func: str = "sum"
    alias: str = ""
    enabled: bool = True

    def effective_alias(self) -> str:
        if self.alias.strip():
            return self.alias.strip()
        labels = {"sum": "Total", "count": "Count", "avg": "Avg",
                  "min": "Min", "max": "Max", "distinct_count": "Unique"}
        return f"{self.source_col} ({labels.get(self.agg_func, self.agg_func)})"


@dataclass
class AggConfig:
    config_id: str = field(default_factory=lambda: uuid4().hex[:8].upper())
    name: str = ""
    group_cols: List[str] = field(default_factory=list)
    metrics: List[MetricDef] = field(default_factory=list)
    include_totals: bool = True
    hierarchical: bool = False   # generate one sheet per grouping level
    sort_by: str = ""
    sort_asc: bool = False


@dataclass
class AggJob:
    project_code: str = "PMU"
    filename: str = ""
    artifact_id: str = ""
    configs: List[AggConfig] = field(default_factory=list)
