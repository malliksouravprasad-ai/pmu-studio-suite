"""APP-002 Data Processing Studio — engine package."""
from .studio_model import ProcessingJob
from .transform_model import TransformStep, TransformJob, FORMAT_TYPES, MATH_OPS, FILTER_OPS
from .rule_model import Rule, RuleJob, RuleResult, VALIDATION_TYPES, CALCULATION_TYPES, SEVERITY_LEVELS, COMPARE_OPS, TYPE_OPTIONS, PATTERN_PRESETS
from .mapping_model import ColumnMapping, MappingJob, MatchResult, MAPPING_TYPES, MATCH_STATUSES
from .state import (
    init_state, reset_state,
    get_workspace, set_workspace, has_workspace,
    get_raw_df, set_raw_df, has_data, get_working_df,
    get_job, set_job,
    get_transform_log, set_transform_log,
    add_transform_step, remove_transform_step, toggle_transform_step, has_transform_steps,
    move_transform_step_up, move_transform_step_down,
    get_rule_results, set_rule_results, get_exceptions, get_calc_log, has_rule_results,
    add_rule, remove_rule, has_rules,
    get_match_results, set_match_results, get_mapped_df, set_mapped_df,
    add_column_mapping, remove_column_mapping, has_mappings,
)
from .transform_executor import apply_all
from .rule_executor import run_all_rules, split_valid_invalid
from .matcher import run_matching, summarize_matches
from .mapper import apply_all_mappings, apply_column_mapping, get_unmatched_df
from .master_lists import get_master_list
from .reporter import (
    save_clean_dataset, save_transform_log,
    save_validation_report, register_outputs,
)
