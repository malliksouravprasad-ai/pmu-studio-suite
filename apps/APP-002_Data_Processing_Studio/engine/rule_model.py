"""Data models for APP-003 Rule Engine."""
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from uuid import uuid4

VALIDATION_TYPES = [
    "required", "type_check", "range_check", "pattern_check",
    "compare_columns", "dependency_check", "consistency_check",
]
CALCULATION_TYPES = ["arithmetic", "conditional", "percentage", "score"]
ALL_RULE_TYPES = VALIDATION_TYPES + CALCULATION_TYPES

SEVERITY_LEVELS = ["error", "warning", "info"]

COMPARE_OPS = {
    "eq":  "= equals",
    "neq": "≠ not equal",
    "gt":  "> greater than",
    "gte": "≥ greater or equal",
    "lt":  "< less than",
    "lte": "≤ less or equal",
}

ARITH_OPS = {
    "add":         "A + B",
    "subtract":    "A − B",
    "multiply":    "A × B",
    "divide":      "A ÷ B",
    "divide_pct":  "(A ÷ B) × 100",
}

TYPE_OPTIONS = ["numeric", "positive_numeric", "integer", "date", "text"]

PATTERN_PRESETS = {
    "udise_code":    ("^\\d{11}$",              "UDISE Code (exactly 11 digits)"),
    "phone_number":  ("^[6-9]\\d{9}$",          "Phone Number (10 digits, starts 6-9)"),
    "email":         ("^[\\w.%+-]+@[\\w.-]+\\.\\w{2,}$", "Email Address"),
    "pincode":       ("^\\d{6}$",               "PIN Code (exactly 6 digits)"),
    "year_4digit":   ("^(19|20)\\d{2}$",        "4-Digit Year (1900–2099)"),
    "date_ddmmyyyy": ("^\\d{2}/\\d{2}/\\d{4}$","Date — DD/MM/YYYY"),
    "date_yyyymmdd": ("^\\d{4}-\\d{2}-\\d{2}$","Date — YYYY-MM-DD"),
    "digits_only":   ("^\\d+$",                 "Digits Only (no letters or symbols)"),
    "letters_only":  ("^[A-Za-z\\s]+$",         "Letters Only (no numbers or symbols)"),
    "alphanumeric":  ("^[A-Za-z0-9]+$",         "Alphanumeric (letters and digits only)"),
    "no_special":    ("^[A-Za-z0-9\\s]+$",      "No Special Characters"),
    "positive_int":  ("^[1-9]\\d*$",            "Positive Integer (no zero, no negatives)"),
    "code_6_10":     ("^[A-Z0-9]{6,10}$",       "Alphanumeric Code (6–10 uppercase chars)"),
    "lgd_code":      ("^\\d{1,6}$",             "LGD Code (1–6 digits)"),
    "aadhaar":       ("^[2-9]\\d{11}$",         "Aadhaar Number (12 digits, starts 2-9)"),
    "custom":        (None,                      "Custom Regex (advanced users)"),
}


@dataclass
class Rule:
    rule_id: str = field(default_factory=lambda: uuid4().hex[:8].upper())
    name: str = ""
    rule_type: str = "required"
    severity: str = "error"
    enabled: bool = True
    params: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RuleResult:
    rule_id: str
    rule_name: str
    rule_type: str
    severity: str
    total: int
    passed: int
    failed: int
    fail_pct: float
    status: str               # PASS / FAIL / WARN
    failing_rows: List[int] = field(default_factory=list)
    error_details: List[Dict] = field(default_factory=list)


@dataclass
class RuleJob:
    project_code: str = "PMU"
    filename: str = ""
    artifact_id: str = ""
    rules: List[Rule] = field(default_factory=list)
