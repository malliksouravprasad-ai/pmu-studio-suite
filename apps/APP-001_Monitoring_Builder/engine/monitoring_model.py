"""
Data models for APP-001 Monitoring Builder.

A MonitoringJob captures everything needed to stand up a data collection
and monitoring system — schema, form, validation rules, KPI definitions,
and aggregation configs — in a single serializable object.
"""
from dataclasses import dataclass, field
from typing import List, Optional
from uuid import uuid4

# ── Field (Schema) ────────────────────────────────────────────────────────────

FIELD_TYPES = {
    "text":    "Text — free text",
    "number":  "Number — decimal value",
    "integer": "Integer — whole number",
    "date":    "Date — calendar date",
    "choice":  "Choice — select from list",
    "boolean": "Yes/No — binary response",
    "email":   "Email — email address",
    "code":    "Code — ID / reference code (e.g., UDISE)",
}

# Google Forms question type for each field type
FIELD_TO_QUESTION_TYPE = {
    "text":    "short_text",
    "number":  "number",
    "integer": "number",
    "date":    "date",
    "choice":  "single_choice",
    "boolean": "single_choice",
    "email":   "short_text",
    "code":    "short_text",
}


@dataclass
class FieldDef:
    field_id:     str          = field(default_factory=lambda: uuid4().hex[:8].upper())
    name:         str          = ""    # machine name — used as column header in data
    label:        str          = ""    # human-readable label shown in form/dictionary
    data_type:    str          = "text"
    required:     bool         = False
    choices:      List[str]    = field(default_factory=list)
    description:  str          = ""    # what this field means / how to fill it
    example:      str          = ""    # example value
    is_identifier: bool        = False # primary entity key (e.g., school_code)
    is_calculated: bool        = False # derived — not collected from respondent
    enabled:      bool         = True

    def question_type(self) -> str:
        return FIELD_TO_QUESTION_TYPE.get(self.data_type, "short_text")


# ── Form ──────────────────────────────────────────────────────────────────────

@dataclass
class FormSection:
    section_id:  str       = field(default_factory=lambda: uuid4().hex[:8].upper())
    title:       str       = ""
    description: str       = ""
    field_ids:   List[str] = field(default_factory=list)
    enabled:     bool      = True


@dataclass
class FormDef:
    title:       str              = "Data Collection Form"
    description: str              = ""
    sections:    List[FormSection] = field(default_factory=list)


# ── Monitoring Job (top-level container) ───────────────────────────────────────

@dataclass
class MonitoringJob:
    workspace_slug:   str           = ""
    project_code:     str           = "PMU"
    monitoring_name:  str           = "Monitoring Framework"
    entity_type:      str           = "School"     # School | District | Block | Teacher | Other
    entity_field:     str           = ""           # field_id of the primary entity identifier

    # Schema
    fields:           List[FieldDef]    = field(default_factory=list)

    # Form structure
    form_def:         FormDef           = field(default_factory=FormDef)

    # Validation rules (as dicts matching APP-002's Rule dataclass schema)
    rule_defs:        List[dict]        = field(default_factory=list)

    # KPI definitions (as dicts matching APP-003's KPIDef schema)
    kpi_defs:         List[dict]        = field(default_factory=list)

    # Aggregation definitions (as dicts matching APP-003's AggConfig schema)
    agg_defs:         List[dict]        = field(default_factory=list)


ENTITY_TYPES = ["School", "District", "Block", "Village", "Teacher", "Student", "Other"]
