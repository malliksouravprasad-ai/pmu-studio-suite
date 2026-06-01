"""Data models for APP-008 Deliverable Builder."""
from dataclasses import dataclass, field
from typing import Dict, List
from uuid import uuid4
import datetime

SECTION_TYPES = {
    "table":      "Data Table — grouped aggregation from the dataset",
    "narrative":  "Narrative — free-text section (observation, context, recommendation)",
    "highlights": "Highlights — top/bottom performers from one column",
}

OUTPUT_FORMATS = {
    "excel": "Excel (.xlsx) — formatted workbook with cover + section sheets",
    "word":  "Word (.docx) — narrative report with tables",
    "ppt":   "PowerPoint (.pptx) — presentation slides",
    "pdf":   "PDF (.pdf) — printable report",
}

AGG_FUNCS = {
    "sum": "sum", "avg": "mean", "count": "count",
    "min": "min", "max": "max", "distinct_count": "nunique",
}


@dataclass
class SectionDef:
    section_id: str = field(default_factory=lambda: uuid4().hex[:8].upper())
    title: str = ""
    section_type: str = "table"     # table | narrative | highlights
    narrative: str = ""             # used for narrative type
    group_cols: List[str] = field(default_factory=list)
    metric_cols: List[str] = field(default_factory=list)
    agg_funcs: Dict[str, str] = field(default_factory=dict)   # col -> "sum"|"avg"|...
    sort_col: str = ""
    sort_asc: bool = False
    top_n: int = 0                  # 0 = all; also used as N for highlights
    include_totals: bool = True
    enabled: bool = True


@dataclass
class ReportConfig:
    project_code: str = "PMU"
    artifact_id: str = ""
    report_title: str = "Programme Report"
    programme: str = ""
    organization: str = "OSEPA"
    author: str = ""
    report_date: str = field(
        default_factory=lambda: datetime.date.today().strftime("%d %B %Y"))
    description: str = ""
    sections: List[SectionDef] = field(default_factory=list)
    selected_formats: List[str] = field(default_factory=lambda: ["excel"])
