"""Session state for APP-005 Deliverable Studio."""
import streamlit as st
import pandas as pd
from .studio_model import DeliverableStudioJob
from .deliverable_model import SectionDef

_WS  = "del_workspace"
_RAW = "del_raw_df"
_JOB = "del_job"

def init_state():
    for k, v in {_WS: None, _RAW: None, _JOB: DeliverableStudioJob()}.items():
        if k not in st.session_state:
            st.session_state[k] = v
    try:
        from shared.theme import apply_theme
        apply_theme()
    except Exception:
        pass

def reset_state():
    st.session_state[_WS]  = None
    st.session_state[_RAW] = None
    st.session_state[_JOB] = DeliverableStudioJob()

def get_workspace(): return st.session_state.get(_WS)
def set_workspace(ws): st.session_state[_WS] = ws
def has_workspace(): return get_workspace() is not None

def get_raw_df(): return st.session_state.get(_RAW)
def set_raw_df(df): st.session_state[_RAW] = df
def has_data():
    df = get_raw_df(); return df is not None and len(df) > 0

def get_job(): return st.session_state.get(_JOB, DeliverableStudioJob())
def set_job(job): st.session_state[_JOB] = job

def add_section(s: SectionDef):
    job = get_job(); job.report_config.sections.append(s); set_job(job)

def remove_section(section_id: str):
    job = get_job()
    job.report_config.sections = [s for s in job.report_config.sections if s.section_id != section_id]
    set_job(job)

def move_section_up(section_id: str):
    job = get_job(); sections = job.report_config.sections
    for i, s in enumerate(sections):
        if s.section_id == section_id and i > 0:
            sections[i-1], sections[i] = sections[i], sections[i-1]
            break
    set_job(job)

def move_section_down(section_id: str):
    job = get_job(); sections = job.report_config.sections
    for i, s in enumerate(sections):
        if s.section_id == section_id and i < len(sections) - 1:
            sections[i], sections[i+1] = sections[i+1], sections[i]
            break
    set_job(job)

def has_sections(): return len(get_job().report_config.sections) > 0
