"""Data models for APP-006 Analytics Builder."""
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from uuid import uuid4


RANK_MODES = {
    "simple":   "Full Ranking — rank all entities by one indicator",
    "top_n":    "Top N — show highest performers only",
    "bottom_n": "Bottom N — show lowest performers (needs attention)",
    "weighted": "Weighted Score — combine multiple indicators with weights",
}

VARIANCE_MODES = {
    "target_vs_achievement": "Target vs Achievement — actual compared to target",
    "period_diff":           "Period Comparison — compare two data columns",
    "growth":                "Growth Rate — percentage change between two periods",
}

TREND_INTERPRETATIONS = {
    "higher_better": "Higher is better (attendance, enrolment, score)",
    "lower_better":  "Lower is better (dropout rate, pendency, errors)",
}


@dataclass
class RankDef:
    rank_id: str = field(default_factory=lambda: uuid4().hex[:8].upper())
    name: str = ""
    entity_col: str = ""
    value_col: str = ""               # for simple / top_n / bottom_n
    rank_mode: str = "simple"
    ascending: bool = False           # False = highest value → Rank 1
    top_n: int = 5
    weight_cols: List[str] = field(default_factory=list)
    weight_values: List[float] = field(default_factory=list)
    normalize: bool = True
    invert_cols: List[str] = field(default_factory=list)  # lower-is-better cols in weighted mode
    enabled: bool = True

    def weight_dict(self) -> Dict[str, float]:
        if len(self.weight_cols) == len(self.weight_values):
            return dict(zip(self.weight_cols, self.weight_values))
        return {}


@dataclass
class VarianceDef:
    var_id: str = field(default_factory=lambda: uuid4().hex[:8].upper())
    name: str = ""
    entity_col: str = ""
    actual_col: str = ""              # for target_vs_achievement
    variance_mode: str = "target_vs_achievement"
    target_col: str = ""             # column with per-entity target values
    target_fixed: Optional[float] = None   # fixed target for all entities
    period_a_col: str = ""           # for period_diff / growth
    period_b_col: str = ""
    enabled: bool = True


@dataclass
class TrendDef:
    trend_id: str = field(default_factory=lambda: uuid4().hex[:8].upper())
    name: str = ""
    entity_col: str = ""
    period_cols: List[str] = field(default_factory=list)   # ordered periods
    value_interpretation: str = "higher_better"
    change_threshold_pct: float = 10.0
    enabled: bool = True


@dataclass
class AnalyticsJob:
    project_code: str = "PMU"
    artifact_id: str = ""
    rankings: List[RankDef] = field(default_factory=list)
    variances: List[VarianceDef] = field(default_factory=list)
    trends: List[TrendDef] = field(default_factory=list)
