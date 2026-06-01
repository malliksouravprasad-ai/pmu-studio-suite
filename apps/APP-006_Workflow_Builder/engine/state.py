"""Session state for APP-006 Workflow Builder."""
import streamlit as st
from .studio_model import WorkflowStudioJob
from .workflow_model import StageDef, TrackingEntry

_WS  = "wf_workspace"
_JOB = "wf_job"

def init_state():
    for k, v in {_WS: None, _JOB: WorkflowStudioJob()}.items():
        if k not in st.session_state:
            st.session_state[k] = v

def reset_state():
    st.session_state[_WS]  = None
    st.session_state[_JOB] = WorkflowStudioJob()

def get_workspace(): return st.session_state.get(_WS)
def set_workspace(ws): st.session_state[_WS] = ws
def has_workspace(): return get_workspace() is not None

def get_job(): return st.session_state.get(_JOB, WorkflowStudioJob())
def set_job(job): st.session_state[_JOB] = job

def get_workflow_job():
    return get_job().workflow_job

def add_stage(s: StageDef):
    job = get_job(); job.workflow_job.stages.append(s); set_job(job)

def remove_stage(stage_id: str):
    job = get_job()
    job.workflow_job.stages = [s for s in job.workflow_job.stages if s.stage_id != stage_id]
    # Remove tracking entries for this stage too
    job.workflow_job.tracking = [t for t in job.workflow_job.tracking if t.stage_id != stage_id]
    set_job(job)

def update_tracking(entity: str, stage_id: str, status: str, remarks: str = ""):
    import datetime
    job = get_job(); wj = job.workflow_job
    for t in wj.tracking:
        if t.entity == entity and t.stage_id == stage_id:
            t.status     = status
            t.remarks    = remarks
            t.updated_on = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
            set_job(job)
            return
    wj.tracking.append(TrackingEntry(
        entity=entity, stage_id=stage_id, status=status, remarks=remarks,
        updated_on=datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
    ))
    set_job(job)

def move_stage_up(stage_id: str):
    job = get_job(); stages = job.workflow_job.stages
    idx = next((i for i, s in enumerate(stages) if s.stage_id == stage_id), None)
    if idx and idx > 0:
        stages[idx - 1], stages[idx] = stages[idx], stages[idx - 1]
    set_job(job)


def move_stage_down(stage_id: str):
    job = get_job(); stages = job.workflow_job.stages
    idx = next((i for i, s in enumerate(stages) if s.stage_id == stage_id), None)
    if idx is not None and idx < len(stages) - 1:
        stages[idx], stages[idx + 1] = stages[idx + 1], stages[idx]
    set_job(job)


def has_stages(): return len(get_workflow_job().stages) > 0
def has_entities(): return len(get_workflow_job().entities) > 0

def workflow_summary(wj) -> dict:
    """Compute overall summary metrics from the per-stage progress DataFrame."""
    from .tracker_engine import compute_progress
    df = compute_progress(wj)
    if df.empty:
        return {"completed_pct": 0.0, "pending_count": 0, "overdue_count": 0}
    total     = df["Total"].sum()
    completed = df["Completed"].sum()
    pending   = int(df["Pending"].sum() + df["In Progress"].sum())
    overdue   = int(df["Overdue"].sum())
    return {
        "completed_pct":  round(completed / total * 100, 1) if total > 0 else 0.0,
        "pending_count":  pending,
        "overdue_count":  overdue,
        "progress_df":    df,
    }
