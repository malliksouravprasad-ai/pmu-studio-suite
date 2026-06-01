"""Data models for APP-009 Workflow Builder."""
from dataclasses import dataclass, field
from typing import List
from uuid import uuid4

STATUSES = ["Pending", "In Progress", "Completed", "Overdue", "N/A"]

STATUS_COLORS = {
    "Completed":   "#C6EFCE",
    "In Progress": "#FFEB9C",
    "Pending":     "#F2F2F2",
    "Overdue":     "#FFC7CE",
    "N/A":         "#D9D9D9",
}

STATUS_EXCEL_FILLS = {
    "Completed":   "C6EFCE",
    "In Progress": "FFEB9C",
    "Pending":     "F2F2F2",
    "Overdue":     "FFC7CE",
    "N/A":         "D9D9D9",
}

ENTITY_TYPES = ["District", "Block", "School", "Village", "Person", "Team", "Other"]


@dataclass
class StageDef:
    stage_id: str = field(default_factory=lambda: uuid4().hex[:8].upper())
    name: str = ""
    sequence: int = 1
    description: str = ""
    due_date: str = ""     # "YYYY-MM-DD" or empty
    enabled: bool = True


@dataclass
class TrackingEntry:
    entity: str = ""
    stage_id: str = ""
    status: str = "Pending"
    updated_on: str = ""
    remarks: str = ""


@dataclass
class WorkflowJob:
    project_code: str = "PMU"
    artifact_id: str = ""
    workflow_name: str = "Data Collection Workflow"
    entity_type: str = "District"
    entities: List[str] = field(default_factory=list)
    stages: List[StageDef] = field(default_factory=list)
    tracking: List[TrackingEntry] = field(default_factory=list)
