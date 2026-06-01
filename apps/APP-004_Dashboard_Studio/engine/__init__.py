"""APP-004 Dashboard Studio — engine package."""
from .studio_model import DashboardStudioJob
from .viz_model import KPIDef, ChartDef, TableDef, DashboardJob, CHART_TYPES, AGG_FUNCS, card_color
from .state import (
    init_state, reset_state,
    get_workspace, set_workspace, has_workspace,
    get_raw_df, set_raw_df, has_data,
    get_job, set_job,
    add_kpi, remove_kpi, has_kpis,
    add_chart, remove_chart, has_charts,
    add_table, remove_table, has_tables,
)
from .kpi_builder import compute_all_kpis, compute_kpi
from .chart_builder import prepare_chart_data, write_chart_to_ws
from .table_builder import build_all_tables, build_table
from .reporter import save_dashboard, save_dashboard_dataset, register_outputs
