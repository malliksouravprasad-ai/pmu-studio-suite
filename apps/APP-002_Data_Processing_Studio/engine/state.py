"""Unified session state for APP-002 Data Processing Studio."""
import streamlit as st
import pandas as pd
from .studio_model import ProcessingJob
from .transform_model import TransformStep
from .rule_model import Rule
from .mapping_model import ColumnMapping

# All keys prefixed "dps_" to avoid collisions with other apps
_WS     = "dps_workspace"      # workspace metadata dict
_RAW    = "dps_raw_df"         # original uploaded DataFrame
_JOB    = "dps_job"            # ProcessingJob
_TR_LOG = "dps_transform_log"  # list of transform log entry dicts
_RR     = "dps_rule_results"   # list of RuleResult
_EXCEP  = "dps_exceptions"     # list of exception detail dicts
_CALC_L = "dps_calc_log"       # list of calc-rule log entries
_MTCH   = "dps_match_results"  # {mapping_id: {value_str: MatchResult}}
_MAPPED = "dps_mapped_df"      # DataFrame after mapping applied


def init_state():
    defaults = {
        _WS:     None,
        _RAW:    None,
        _JOB:    ProcessingJob(),
        _TR_LOG: [],
        _RR:     None,
        _EXCEP:  [],
        _CALC_L: [],
        _MTCH:   {},
        _MAPPED: None,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v
    try:
        from shared.theme import apply_theme
        apply_theme()
    except Exception:
        pass


def reset_state():
    st.session_state[_WS]     = None
    st.session_state[_RAW]    = None
    st.session_state[_JOB]    = ProcessingJob()
    st.session_state[_TR_LOG] = []
    st.session_state[_RR]     = None
    st.session_state[_EXCEP]  = []
    st.session_state[_CALC_L] = []
    st.session_state[_MTCH]   = {}
    st.session_state[_MAPPED] = None


def _clear_results():
    st.session_state[_TR_LOG] = []
    st.session_state[_RR]     = None
    st.session_state[_EXCEP]  = []
    st.session_state[_CALC_L] = []
    st.session_state[_MAPPED] = None


# ── Workspace ─────────────────────────────────────────────────────────────────

def get_workspace() -> dict | None:
    return st.session_state.get(_WS)

def set_workspace(ws: dict):
    st.session_state[_WS] = ws


# ── Raw Data ──────────────────────────────────────────────────────────────────

def get_raw_df() -> pd.DataFrame | None:
    return st.session_state.get(_RAW)

def set_raw_df(df: pd.DataFrame):
    st.session_state[_RAW] = df
    _clear_results()


# ── Processing Job ────────────────────────────────────────────────────────────

def get_job() -> ProcessingJob:
    return st.session_state.get(_JOB, ProcessingJob())

def set_job(job: ProcessingJob):
    st.session_state[_JOB] = job


# ── Transform ─────────────────────────────────────────────────────────────────

def get_transform_log() -> list:
    return st.session_state.get(_TR_LOG, [])

def set_transform_log(log: list):
    st.session_state[_TR_LOG] = log

def add_transform_step(step: TransformStep):
    job = get_job()
    job.transform_job.steps.append(step)
    set_job(job)
    st.session_state[_TR_LOG] = []

def remove_transform_step(step_id: str):
    job = get_job()
    job.transform_job.steps = [s for s in job.transform_job.steps if s.step_id != step_id]
    set_job(job)
    st.session_state[_TR_LOG] = []

def toggle_transform_step(step_id: str):
    job = get_job()
    for s in job.transform_job.steps:
        if s.step_id == step_id:
            s.enabled = not s.enabled
    set_job(job)
    st.session_state[_TR_LOG] = []


def move_transform_step_up(step_id: str):
    job = get_job()
    steps = job.transform_job.steps
    idx = next((i for i, s in enumerate(steps) if s.step_id == step_id), None)
    if idx and idx > 0:
        steps[idx - 1], steps[idx] = steps[idx], steps[idx - 1]
    set_job(job)
    st.session_state[_TR_LOG] = []


def move_transform_step_down(step_id: str):
    job = get_job()
    steps = job.transform_job.steps
    idx = next((i for i, s in enumerate(steps) if s.step_id == step_id), None)
    if idx is not None and idx < len(steps) - 1:
        steps[idx], steps[idx + 1] = steps[idx + 1], steps[idx]
    set_job(job)
    st.session_state[_TR_LOG] = []


# ── Rules ─────────────────────────────────────────────────────────────────────

def get_rule_results():
    return st.session_state.get(_RR)

def set_rule_results(results, exceptions, calc_log):
    st.session_state[_RR]     = results
    st.session_state[_EXCEP]  = exceptions
    st.session_state[_CALC_L] = calc_log

def get_exceptions() -> list:
    return st.session_state.get(_EXCEP, [])

def get_calc_log() -> list:
    return st.session_state.get(_CALC_L, [])

def add_rule(rule: Rule):
    job = get_job()
    job.rule_job.rules.append(rule)
    set_job(job)
    st.session_state[_RR] = None

def remove_rule(rule_id: str):
    job = get_job()
    job.rule_job.rules = [r for r in job.rule_job.rules if r.rule_id != rule_id]
    set_job(job)
    st.session_state[_RR] = None


# ── Mapping ───────────────────────────────────────────────────────────────────

def get_match_results() -> dict:
    return st.session_state.get(_MTCH, {})

def set_match_results(results: dict):
    st.session_state[_MTCH] = results

def get_mapped_df() -> pd.DataFrame | None:
    return st.session_state.get(_MAPPED)

def set_mapped_df(df: pd.DataFrame):
    st.session_state[_MAPPED] = df

def add_column_mapping(cm: ColumnMapping):
    job = get_job()
    job.mapping_job.column_mappings = [
        c for c in job.mapping_job.column_mappings if c.source_col != cm.source_col
    ]
    job.mapping_job.column_mappings.append(cm)
    set_job(job)
    results = get_match_results()
    results.pop(cm.mapping_id, None)
    set_match_results(results)
    st.session_state[_MAPPED] = None

def remove_column_mapping(mapping_id: str):
    job = get_job()
    job.mapping_job.column_mappings = [
        c for c in job.mapping_job.column_mappings if c.mapping_id != mapping_id
    ]
    set_job(job)
    results = get_match_results()
    results.pop(mapping_id, None)
    set_match_results(results)
    st.session_state[_MAPPED] = None


# ── Derived helpers ───────────────────────────────────────────────────────────

def has_workspace() -> bool:
    return get_workspace() is not None

def has_data() -> bool:
    df = get_raw_df()
    return df is not None and len(df) > 0

def has_transform_steps() -> bool:
    return len([s for s in get_job().transform_job.steps if s.enabled]) > 0

def has_rules() -> bool:
    return len([r for r in get_job().rule_job.rules if r.enabled]) > 0

def has_mappings() -> bool:
    return len(get_job().mapping_job.column_mappings) > 0

def has_rule_results() -> bool:
    return get_rule_results() is not None

def get_working_df() -> pd.DataFrame | None:
    """Mapped df if mapping was applied, else raw df."""
    return get_mapped_df() or get_raw_df()
