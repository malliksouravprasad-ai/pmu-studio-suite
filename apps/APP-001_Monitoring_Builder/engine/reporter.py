"""Output registration for APP-001 Monitoring Builder."""
import os
import sys

_APP_DIR  = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_PMU_ROOT = os.path.dirname(os.path.dirname(_APP_DIR))
for _p in [_PMU_ROOT, _APP_DIR]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

from shared import register

_OUT_DIR = os.path.join(_APP_DIR, "outputs")
os.makedirs(_OUT_DIR, exist_ok=True)


def save_bytes(data: bytes, filename: str, workspace_path: str = None) -> tuple:
    """Write bytes to a file path (workspace or default out dir). Returns (path, bytes)."""
    from pathlib import Path
    import io
    base = (Path(workspace_path) / "outputs") if workspace_path else Path(_OUT_DIR)
    base.mkdir(parents=True, exist_ok=True)
    path = base / filename
    path.write_bytes(data)
    return str(path), io.BytesIO(data)


def register_outputs(
    artifact_id: str, project_code: str,
    template_path: str = None,
    validation_path: str = None,
    kpi_path: str = None,
    form_path: str = None,
) -> None:
    for path, rtype in [
        (template_path,   "Excel Data Template"),
        (validation_path, "Validation Config"),
        (kpi_path,        "KPI Config"),
        (form_path,       "Form Structure"),
    ]:
        if path:
            register(
                artifact_id=artifact_id, app_id="APP-001",
                project=project_code, report_type=rtype,
                output_file=str(path), status="Generated",
            )
