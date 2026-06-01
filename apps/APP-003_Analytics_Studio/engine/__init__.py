"""APP-003 Analytics Studio — engine package."""
from .studio_model import AnalyticsStudioJob
from .agg_model import AggConfig, MetricDef, AggJob, AGG_FUNCS, suggest_agg_func
from .analytics_model import (
    RankDef, VarianceDef, TrendDef, AnalyticsJob,
    RANK_MODES, VARIANCE_MODES, TREND_INTERPRETATIONS,
)
from .kpi_engine import KPIDef, calculate_kpis, KPI_FORMULAS, KPI_INTERPRETATIONS
from .state import (
    init_state, reset_state,
    get_workspace, set_workspace, has_workspace,
    get_raw_df, set_raw_df, has_data,
    get_job, set_job,
    add_agg_config, remove_agg_config, get_agg_results, set_agg_results, has_agg_configs,
    add_kpi, remove_kpi, get_kpi_result, set_kpi_result, has_kpis,
    add_ranking, remove_ranking, get_rank_results, set_rank_results, has_rankings,
    add_variance, remove_variance, get_var_results, set_var_results, has_variances,
    add_trend, remove_trend, get_trend_results, set_trend_results, has_trends,
)
from .aggregator import run_all_configs, aggregate_config
from .ranker import rank_entities
from .variance import calc_variance
from .trend import analyze_trend
from .reporter import save_aggregation, save_kpi_report, save_analytics, register_outputs
