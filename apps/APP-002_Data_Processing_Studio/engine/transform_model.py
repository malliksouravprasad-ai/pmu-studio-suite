"""Data models for APP-002 Transformation Builder."""
from dataclasses import dataclass, field
from typing import Any, Dict, List
from uuid import uuid4

# Column Manager ops
COL_MANAGER_OPS = ["rename", "reorder", "delete"]

# Column Transformer ops
COL_TRANSFORM_OPS = ["merge_columns", "split_column", "format_column", "create_column"]

# Row ops
ROW_OPS = ["filter", "sort", "remove_duplicates", "remove_blanks"]

ALL_OPS = COL_MANAGER_OPS + COL_TRANSFORM_OPS + ROW_OPS

FORMAT_TYPES = {
    "text_upper":     "Text → UPPERCASE",
    "text_lower":     "Text → lowercase",
    "text_title":     "Text → Title Case",
    "text_strip":     "Strip leading/trailing spaces",
    "prefix_suffix":  "Add prefix / suffix",
    "round_numeric":  "Round to N decimals",
    "to_percentage":  "Format as percentage (value × 100% string)",
    "date_reformat":  "Reformat date string",
}

MATH_OPS = {
    "add":         "A + B",
    "subtract":    "A − B",
    "multiply":    "A × B",
    "divide":      "A ÷ B",
    "divide_pct":  "(A ÷ B) × 100",
}

FILTER_OPS = {
    "equals":        "= equals",
    "not_equals":    "≠ not equals",
    "contains":      "contains",
    "starts_with":   "starts with",
    "ends_with":     "ends with",
    "greater_than":  "> greater than",
    "less_than":     "< less than",
    "greater_equal": "≥ greater or equal",
    "less_equal":    "≤ less or equal",
    "is_blank":      "is blank",
    "is_not_blank":  "is not blank",
}


@dataclass
class TransformStep:
    step_id: str = field(default_factory=lambda: uuid4().hex[:8].upper())
    op_type: str = ""
    description: str = ""
    params: Dict[str, Any] = field(default_factory=dict)
    enabled: bool = True


@dataclass
class TransformJob:
    project_code: str = "PMU"
    filename: str = ""
    artifact_id: str = ""
    steps: List[TransformStep] = field(default_factory=list)
