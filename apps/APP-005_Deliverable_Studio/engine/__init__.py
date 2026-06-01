"""APP-005 Deliverable Studio — engine package."""
from .studio_model import DeliverableStudioJob
from .deliverable_model import ReportConfig, SectionDef, SECTION_TYPES, OUTPUT_FORMATS, AGG_FUNCS
from .state import (
    init_state, reset_state,
    get_workspace, set_workspace, has_workspace,
    get_raw_df, set_raw_df, has_data,
    get_job, set_job,
    add_section, remove_section, move_section_up, move_section_down, has_sections,
)
from .reporter import (
    compute_section_data, generate_all,
    save_excel_report, save_word_report, save_ppt_report, save_pdf_report,
    register_outputs,
)
