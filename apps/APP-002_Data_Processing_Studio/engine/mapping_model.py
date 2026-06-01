"""Data models for APP-004 Lookup & Mapping Engine."""
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from uuid import uuid4

MAPPING_TYPES = ["district", "block", "school", "custom"]

MATCH_STATUSES = {
    "exact":     "Exact Match",
    "variant":   "Variant Match",
    "approved":  "Fuzzy — Approved",
    "rejected":  "Rejected (original kept)",
    "manual":    "Manual Override",
    "unmatched": "Unmatched",
    "pending":   "Pending Review",
    "blank":     "Blank Value",
}


@dataclass
class MatchResult:
    input_value: str
    canonical_value: str      # best candidate or user-chosen value
    match_type: str           # exact / variant / fuzzy / unmatched
    confidence: float         # 0.0 – 1.0
    suggestions: List[str] = field(default_factory=list)
    status: str = "pending"   # exact/variant (auto) | pending/approved/rejected/manual/unmatched


@dataclass
class ColumnMapping:
    mapping_id: str = field(default_factory=lambda: uuid4().hex[:8].upper())
    source_col: str = ""
    mapping_type: str = "district"
    master_list: List[str] = field(default_factory=list)
    variant_map: Dict[str, str] = field(default_factory=dict)   # {lowercase_alias: canonical}
    fuzzy_threshold: float = 0.72
    create_new_col: bool = True    # True = {col}_Mapped; False = overwrite original


@dataclass
class MappingJob:
    project_code: str = "PMU"
    filename: str = ""
    artifact_id: str = ""
    column_mappings: List[ColumnMapping] = field(default_factory=list)
