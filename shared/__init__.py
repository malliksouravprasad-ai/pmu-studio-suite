# ── Serialization Engine ──────────────────────────────────────────────────────
from .serialization import (
    generate_id,
    to_json, from_json,
    to_csv, from_csv,
    df_to_csv, df_from_csv, df_to_json,
)

# ── Registry Manager ──────────────────────────────────────────────────────────
from .registry import (
    register,
    get_entry,
    update_status,
    delete_entry,
    list_entries,
    summary as registry_summary,
)

# ── Template Library ──────────────────────────────────────────────────────────
from .template_lib import (
    register_template,
    list_templates,
    get_template_path,
    copy_template,
    remove_template,
    scan_app_templates,
)

# ── Google Integration ────────────────────────────────────────────────────────
from .google_svc import (
    credentials_available,
    get_credentials,
    build_service,
    read_sheet,
    append_rows,
    clear_and_write,
    create_spreadsheet,
    upload_to_drive,
    share_file,
    get_file_link,
    create_form,
    add_form_items,
    get_form,
    get_form_responses,
)

# ── Excel Integration ─────────────────────────────────────────────────────────
from .excel_svc import (
    PMU_COLORS,
    create_workbook,
    add_sheet,
    style_title_row,
    style_header_row,
    style_section_row,
    style_data_row,
    set_cell,
    write_dataframe,
    auto_width,
    freeze_header,
    set_col_width,
    read_excel,
    load_wb,
    save_workbook,
    save_to_path,
)

# ── General Utilities ─────────────────────────────────────────────────────────
from .utils import (
    setup_logger,
    output_path,
    input_path,
    timestamp_suffix,
    validate_file_exists,
    validate_columns,
)

# ── Project Workspace Manager ─────────────────────────────────────────────────
from .workspace import (
    create_workspace,
    load_workspace,
    list_workspaces,
    update_workspace,
    delete_workspace,
    workspace_path,
    get_folder,
    slugify as workspace_slugify,
    WORKSPACE_FOLDERS,
)

# ── Configuration Manager ─────────────────────────────────────────────────────
from .config_manager import (
    save_config,
    load_config,
    load_config_by_file,
    list_configs,
    list_all_configs,
    clone_config,
    delete_config,
    export_config,
    import_config,
)

# ── Package Manager ───────────────────────────────────────────────────────────
from .package_manager import (
    export_package,
    import_package,
    clone_package,
    package_info,
    list_packages,
)

# ── Registry Browser ──────────────────────────────────────────────────────────
from .registry_browser import render_registry_browser

# ── Auto-save ─────────────────────────────────────────────────────────────────
from .autosave import autosave_job, load_autosave, render_autosave_controls

# ── Column Metadata Layer ─────────────────────────────────────────────────────
from .column_metadata import (
    save_column_metadata,
    load_column_metadata,
    resolve_label,
    resolve_type,
    metadata_from_monitoring_job,
    render_column_metadata_panel,
)
