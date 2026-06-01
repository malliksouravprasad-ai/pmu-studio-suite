"""Tracking analytics engine for APP-009."""
import datetime
from typing import Dict
import pandas as pd

from .workflow_model import WorkflowJob, STATUS_COLORS


def _resolve_status(status: str, due_date: str) -> str:
    """Auto-upgrade Pending/In Progress to Overdue if past due date."""
    if due_date and status in ("Pending", "In Progress"):
        today = datetime.date.today().isoformat()
        if today > due_date:
            return "Overdue"
    return status


def get_tracking_matrix(job: WorkflowJob) -> pd.DataFrame:
    """Return entity × stage matrix with status values."""
    stages = sorted([s for s in job.stages if s.enabled], key=lambda s: s.sequence)
    if not stages or not job.entities:
        return pd.DataFrame()

    lookup: Dict = {(e.entity, e.stage_id): e for e in job.tracking}

    rows = []
    for entity in job.entities:
        row = {job.entity_type: entity}
        for stage in stages:
            entry = lookup.get((entity, stage.stage_id))
            raw_status = entry.status if entry else "Pending"
            row[stage.name] = _resolve_status(raw_status, stage.due_date)
        rows.append(row)

    return pd.DataFrame(rows)


def compute_progress(job: WorkflowJob) -> pd.DataFrame:
    """Per-stage completion statistics."""
    stages = sorted([s for s in job.stages if s.enabled], key=lambda s: s.sequence)
    if not stages or not job.entities:
        return pd.DataFrame()

    matrix = get_tracking_matrix(job)
    records = []
    for stage in stages:
        if stage.name not in matrix.columns:
            continue
        col = matrix[stage.name]
        total       = len(col)
        completed   = int((col == "Completed").sum())
        in_progress = int((col == "In Progress").sum())
        pending     = int((col == "Pending").sum())
        overdue     = int((col == "Overdue").sum())
        na          = int((col == "N/A").sum())
        active      = total - na
        pct         = round(completed / active * 100, 1) if active > 0 else 0.0
        records.append({
            "Seq":          stage.sequence,
            "Stage":        stage.name,
            "Due Date":     stage.due_date or "—",
            "Total":        total,
            "Completed":    completed,
            "In Progress":  in_progress,
            "Pending":      pending,
            "Overdue":      overdue,
            "N/A":          na,
            "Completion %": pct,
        })
    return pd.DataFrame(records)


def get_pendency_list(job: WorkflowJob) -> pd.DataFrame:
    """Entities with Pending / In Progress / Overdue stages."""
    stages = sorted([s for s in job.stages if s.enabled], key=lambda s: s.sequence)
    lookup: Dict = {(e.entity, e.stage_id): e for e in job.tracking}
    today = datetime.date.today()
    records = []

    for entity in job.entities:
        for stage in stages:
            entry = lookup.get((entity, stage.stage_id))
            raw_status = entry.status if entry else "Pending"
            status = _resolve_status(raw_status, stage.due_date)

            if status not in ("Pending", "In Progress", "Overdue"):
                continue

            days_overdue: object = ""
            if stage.due_date:
                try:
                    due = datetime.date.fromisoformat(stage.due_date)
                    if today > due:
                        days_overdue = (today - due).days
                except ValueError:
                    pass

            records.append({
                job.entity_type: entity,
                "Stage":         stage.name,
                "Status":        status,
                "Due Date":      stage.due_date or "—",
                "Days Overdue":  days_overdue,
                "Remarks":       entry.remarks if entry else "",
            })

    df = pd.DataFrame(records) if records else pd.DataFrame()
    if not df.empty and "Status" in df.columns:
        order = {"Overdue": 0, "In Progress": 1, "Pending": 2}
        df["_sort"] = df["Status"].map(order).fillna(3)
        df = df.sort_values("_sort").drop(columns="_sort").reset_index(drop=True)
    return df


def style_matrix(matrix_df: pd.DataFrame, entity_type: str) -> object:
    """Return a pandas Styler with color-coded status cells."""
    stage_cols = [c for c in matrix_df.columns if c != entity_type]

    def _color(val):
        return f"background-color: {STATUS_COLORS.get(val, '#FFFFFF')}"

    try:
        return matrix_df.style.map(_color, subset=stage_cols)
    except AttributeError:
        # pandas < 2.1 uses applymap
        return matrix_df.style.applymap(_color, subset=stage_cols)
