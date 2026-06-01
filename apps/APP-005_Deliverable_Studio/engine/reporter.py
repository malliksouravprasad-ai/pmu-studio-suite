"""Orchestrator for APP-008 Deliverable Builder."""
import os
import sys
from typing import Dict, Tuple
import pandas as pd

_APP_DIR  = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_PMU_ROOT = os.path.dirname(os.path.dirname(_APP_DIR))
for _p in [_PMU_ROOT, _APP_DIR]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

from shared import register
from .deliverable_model import ReportConfig, SectionDef, AGG_FUNCS
from .excel_report import save_excel_report
from .word_report  import save_word_report
from .ppt_report   import save_ppt_report
from .pdf_report   import save_pdf_report

_OUT_DIR = os.path.join(_PMU_ROOT, "outputs", "APP-008_Deliverable_Builder")
os.makedirs(_OUT_DIR, exist_ok=True)

_PANDAS_FUNC = {
    "sum": "sum", "avg": "mean", "count": "count",
    "min": "min", "max": "max", "distinct_count": "nunique",
}


def compute_section_data(df: pd.DataFrame, config: ReportConfig) -> Dict[str, pd.DataFrame]:
    """Return {section_id: DataFrame} for all enabled non-narrative sections."""
    result = {}
    for sdef in config.sections:
        if not sdef.enabled or sdef.section_type == "narrative":
            result[sdef.section_id] = pd.DataFrame()
            continue
        result[sdef.section_id] = _compute_one(df, sdef)
    return result


def _compute_one(df: pd.DataFrame, sdef: SectionDef) -> pd.DataFrame:
    """Aggregate df according to SectionDef."""
    group_cols  = [c for c in sdef.group_cols  if c in df.columns]
    metric_cols = [c for c in sdef.metric_cols if c in df.columns]

    if not group_cols or not metric_cols:
        return pd.DataFrame()

    # Highlights: top N by first metric
    if sdef.section_type == "highlights":
        agg_spec = {c: _PANDAS_FUNC.get(sdef.agg_funcs.get(c, "sum"), "sum")
                    for c in metric_cols}
        result = df.groupby(group_cols, as_index=False).agg(agg_spec)
        for c in metric_cols:
            result[c] = pd.to_numeric(result[c], errors="coerce").round(2)
        sort_c = sdef.sort_col if sdef.sort_col in result.columns else metric_cols[0]
        result = result.sort_values(sort_c, ascending=sdef.sort_asc).reset_index(drop=True)
        if sdef.top_n > 0:
            result = result.head(sdef.top_n)
        return result

    # Standard table
    agg_spec = {c: _PANDAS_FUNC.get(sdef.agg_funcs.get(c, "sum"), "sum")
                for c in metric_cols}
    result = df.groupby(group_cols, as_index=False).agg(agg_spec)
    for c in metric_cols:
        result[c] = pd.to_numeric(result[c], errors="coerce").round(2)

    sort_c = sdef.sort_col if sdef.sort_col in result.columns else ""
    if sort_c:
        result = result.sort_values(sort_c, ascending=sdef.sort_asc)

    if sdef.top_n > 0:
        result = result.head(sdef.top_n)

    result = result.reset_index(drop=True)

    if sdef.include_totals and group_cols:
        total_row = {gc: ("TOTAL" if i == 0 else "") for i, gc in enumerate(group_cols)}
        for c in metric_cols:
            func = sdef.agg_funcs.get(c, "sum")
            s = pd.to_numeric(df[c], errors="coerce")
            total_row[c] = round(float({
                "sum": s.sum, "avg": s.mean, "count": lambda: df[c].notna().sum(),
                "min": s.min, "max": s.max, "distinct_count": lambda: df[c].nunique(),
            }.get(func, s.sum)()), 2)
        result = pd.concat([result, pd.DataFrame([total_row])], ignore_index=True)

    return result


def generate_all(
    df: pd.DataFrame,
    section_data: Dict[str, pd.DataFrame],
    config: ReportConfig,
    artifact_id: str,
) -> Dict[str, Tuple[str, object]]:
    """Generate all selected output formats. Returns {format: (fname, buf)}."""
    outputs = {}

    if "excel" in config.selected_formats:
        fname, buf = save_excel_report(section_data, config, artifact_id)
        path = _save_to_disk(buf, fname)
        outputs["excel"] = (fname, buf, path)

    if "word" in config.selected_formats:
        fname, buf = save_word_report(section_data, config, artifact_id)
        path = _save_to_disk(buf, fname)
        outputs["word"] = (fname, buf, path)

    if "ppt" in config.selected_formats:
        fname, buf = save_ppt_report(section_data, config, artifact_id)
        path = _save_to_disk(buf, fname)
        outputs["ppt"] = (fname, buf, path)

    if "pdf" in config.selected_formats:
        fname, buf = save_pdf_report(section_data, config, artifact_id)
        path = _save_to_disk(buf, fname)
        outputs["pdf"] = (fname, buf, path)

    return outputs


def _save_to_disk(buf, fname: str) -> str:
    buf.seek(0)
    path = os.path.join(_OUT_DIR, fname)
    with open(path, "wb") as f:
        f.write(buf.read())
    buf.seek(0)
    return path


def register_outputs(artifact_id, project_code, outputs: dict):
    mime_map = {
        "excel": "Excel Report", "word": "Word Report",
        "ppt": "PowerPoint", "pdf": "PDF Report",
    }
    for fmt, (fname, buf, path) in outputs.items():
        register(
            artifact_id=artifact_id,
            app_id="APP-008",
            project=project_code,
            report_type=mime_map.get(fmt, fmt),
            output_file=str(path),
            status="Generated",
        )
