"""Unified session state for APP-003 Analytics Studio."""
import streamlit as st
import pandas as pd
from .studio_model import AnalyticsStudioJob
from .agg_model import AggConfig, MetricDef
from .analytics_model import RankDef, VarianceDef, TrendDef
from .kpi_engine import KPIDef

# "as_" prefix = Analytics Studio
_WS      = "as_workspace"
_RAW     = "as_raw_df"
_JOB     = "as_job"
_AGG_RES = "as_agg_results"   # {config_id: DataFrame}
_KPI_RES = "as_kpi_result"    # (result_df, kpi_summary) or None
_RANK_RES = "as_rank_results"  # {rank_id: DataFrame}
_VAR_RES  = "as_var_results"   # {var_id: DataFrame}
_TREND_RES = "as_trend_results" # {trend_id: DataFrame}


def init_state():
    defaults = {
        _WS:       None,
        _RAW:      None,
        _JOB:      AnalyticsStudioJob(),
        _AGG_RES:  {},
        _KPI_RES:  None,
        _RANK_RES: {},
        _VAR_RES:  {},
        _TREND_RES: {},
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


def reset_state():
    st.session_state[_WS]       = None
    st.session_state[_RAW]      = None
    st.session_state[_JOB]      = AnalyticsStudioJob()
    st.session_state[_AGG_RES]  = {}
    st.session_state[_KPI_RES]  = None
    st.session_state[_RANK_RES] = {}
    st.session_state[_VAR_RES]  = {}
    st.session_state[_TREND_RES] = {}


# ── Workspace ─────────────────────────────────────────────────────────────────
def get_workspace(): return st.session_state.get(_WS)
def set_workspace(ws): st.session_state[_WS] = ws
def has_workspace(): return get_workspace() is not None

# ── Data ──────────────────────────────────────────────────────────────────────
def get_raw_df(): return st.session_state.get(_RAW)
def set_raw_df(df):
    st.session_state[_RAW] = df
    st.session_state[_AGG_RES] = {}
    st.session_state[_KPI_RES] = None
    st.session_state[_RANK_RES] = {}
    st.session_state[_VAR_RES] = {}
    st.session_state[_TREND_RES] = {}
def has_data():
    df = get_raw_df(); return df is not None and len(df) > 0

# ── Job ───────────────────────────────────────────────────────────────────────
def get_job(): return st.session_state.get(_JOB, AnalyticsStudioJob())
def set_job(job): st.session_state[_JOB] = job

# ── Aggregation ───────────────────────────────────────────────────────────────
def add_agg_config(cfg: AggConfig):
    job = get_job(); job.agg_job.configs.append(cfg); set_job(job)
    st.session_state[_AGG_RES] = {}

def remove_agg_config(config_id: str):
    job = get_job()
    job.agg_job.configs = [c for c in job.agg_job.configs if c.config_id != config_id]
    set_job(job)
    results = st.session_state.get(_AGG_RES, {})
    results.pop(config_id, None)
    st.session_state[_AGG_RES] = results

def get_agg_results(): return st.session_state.get(_AGG_RES, {})
def set_agg_results(r): st.session_state[_AGG_RES] = r

# ── KPI ───────────────────────────────────────────────────────────────────────
def add_kpi(kpi: KPIDef):
    job = get_job(); job.kpi_defs.append(kpi); set_job(job)
    st.session_state[_KPI_RES] = None

def remove_kpi(kpi_id: str):
    job = get_job()
    job.kpi_defs = [k for k in job.kpi_defs if k.kpi_id != kpi_id]
    set_job(job); st.session_state[_KPI_RES] = None

def get_kpi_result(): return st.session_state.get(_KPI_RES)
def set_kpi_result(r): st.session_state[_KPI_RES] = r

# ── Analytics ─────────────────────────────────────────────────────────────────
def add_ranking(r: RankDef):
    job = get_job(); job.analytics_job.rankings.append(r); set_job(job)
    st.session_state[_RANK_RES] = {}

def remove_ranking(rank_id: str):
    job = get_job()
    job.analytics_job.rankings = [r for r in job.analytics_job.rankings if r.rank_id != rank_id]
    set_job(job)

def add_variance(v: VarianceDef):
    job = get_job(); job.analytics_job.variances.append(v); set_job(job)
    st.session_state[_VAR_RES] = {}

def remove_variance(var_id: str):
    job = get_job()
    job.analytics_job.variances = [v for v in job.analytics_job.variances if v.var_id != var_id]
    set_job(job)

def add_trend(t: TrendDef):
    job = get_job(); job.analytics_job.trends.append(t); set_job(job)
    st.session_state[_TREND_RES] = {}

def remove_trend(trend_id: str):
    job = get_job()
    job.analytics_job.trends = [t for t in job.analytics_job.trends if t.trend_id != trend_id]
    set_job(job)

def get_rank_results(): return st.session_state.get(_RANK_RES, {})
def set_rank_results(r): st.session_state[_RANK_RES] = r
def get_var_results(): return st.session_state.get(_VAR_RES, {})
def set_var_results(r): st.session_state[_VAR_RES] = r
def get_trend_results(): return st.session_state.get(_TREND_RES, {})
def set_trend_results(r): st.session_state[_TREND_RES] = r

def has_agg_configs(): return len(get_job().agg_job.configs) > 0
def has_kpis(): return len([k for k in get_job().kpi_defs if k.enabled]) > 0
def has_rankings(): return len([r for r in get_job().analytics_job.rankings if r.enabled]) > 0
def has_variances(): return len([v for v in get_job().analytics_job.variances if v.enabled]) > 0
def has_trends(): return len([t for t in get_job().analytics_job.trends if t.enabled]) > 0
