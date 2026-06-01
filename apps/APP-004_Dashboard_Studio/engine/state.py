"""Session state for APP-004 Dashboard Studio."""
import streamlit as st
import pandas as pd
from .studio_model import DashboardStudioJob
from .viz_model import KPIDef, ChartDef, TableDef

_WS  = "ds_workspace"
_RAW = "ds_raw_df"
_JOB = "ds_job"

def init_state():
    defaults = {_WS: None, _RAW: None, _JOB: DashboardStudioJob()}
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

def reset_state():
    st.session_state[_WS]  = None
    st.session_state[_RAW] = None
    st.session_state[_JOB] = DashboardStudioJob()

def get_workspace(): return st.session_state.get(_WS)
def set_workspace(ws): st.session_state[_WS] = ws
def has_workspace(): return get_workspace() is not None

def get_raw_df(): return st.session_state.get(_RAW)
def set_raw_df(df): st.session_state[_RAW] = df
def has_data():
    df = get_raw_df(); return df is not None and len(df) > 0

def get_job(): return st.session_state.get(_JOB, DashboardStudioJob())
def set_job(job): st.session_state[_JOB] = job

def add_kpi(kpi: KPIDef):
    job = get_job(); job.dashboard_job.kpis.append(kpi); set_job(job)

def remove_kpi(kpi_id: str):
    job = get_job()
    job.dashboard_job.kpis = [k for k in job.dashboard_job.kpis if k.kpi_id != kpi_id]
    set_job(job)

def add_chart(chart: ChartDef):
    job = get_job(); job.dashboard_job.charts.append(chart); set_job(job)

def remove_chart(chart_id: str):
    job = get_job()
    job.dashboard_job.charts = [c for c in job.dashboard_job.charts if c.chart_id != chart_id]
    set_job(job)

def add_table(table: TableDef):
    job = get_job(); job.dashboard_job.tables.append(table); set_job(job)

def remove_table(table_id: str):
    job = get_job()
    job.dashboard_job.tables = [t for t in job.dashboard_job.tables if t.table_id != table_id]
    set_job(job)

def has_kpis(): return len(get_job().dashboard_job.kpis) > 0
def has_charts(): return len(get_job().dashboard_job.charts) > 0
def has_tables(): return len(get_job().dashboard_job.tables) > 0
