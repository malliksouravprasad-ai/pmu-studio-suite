"""
Column Metadata Layer — shared column alias / label store.

Decouples display labels from physical column names so that renaming
a column label does not break downstream pipeline configurations.

Usage:
    from shared import save_column_metadata, load_column_metadata, resolve_label

    # Save metadata when generating output:
    meta = {
        "school_name":    {"label": "School Name",    "type": "text",    "unit": ""},
        "total_enrolment":{"label": "Total Enrolment","type": "integer", "unit": "students"},
    }
    save_column_metadata(workspace_path, artifact_id, meta)

    # Load in any downstream app:
    meta = load_column_metadata(workspace_path, artifact_id)
    label = resolve_label(meta, "total_enrolment")  # -> "Total Enrolment"
"""
import json
from pathlib import Path


def save_column_metadata(workspace_path: str, artifact_id: str, metadata: dict) -> Path:
    """
    Save column metadata for an artifact to workspace/data_sources/<artifact_id>_metadata.json.

    metadata format:
    {
        "column_name": {
            "label":       "Human Readable Label",
            "type":        "text | integer | number | date | choice | boolean",
            "unit":        "",
            "description": "",
        },
        ...
    }
    """
    folder = Path(workspace_path) / "data_sources"
    folder.mkdir(parents=True, exist_ok=True)
    target = folder / f"{artifact_id}_metadata.json"
    target.write_text(json.dumps(metadata, indent=2, ensure_ascii=False), encoding="utf-8")
    return target


def load_column_metadata(workspace_path: str, artifact_id: str = None) -> dict:
    """
    Load column metadata from workspace. If artifact_id is None, loads the most
    recently saved metadata file.
    Returns empty dict if none found.
    """
    folder = Path(workspace_path) / "data_sources"
    if not folder.exists():
        return {}

    if artifact_id:
        target = folder / f"{artifact_id}_metadata.json"
        if target.exists():
            try:
                return json.loads(target.read_text(encoding="utf-8"))
            except Exception:
                return {}
        return {}

    # Load most recent metadata file
    candidates = sorted(folder.glob("*_metadata.json"), key=lambda p: p.stat().st_mtime, reverse=True)
    if candidates:
        try:
            return json.loads(candidates[0].read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def resolve_label(metadata: dict, column_name: str) -> str:
    """Return the human label for a column, falling back to the column name."""
    return metadata.get(column_name, {}).get("label", column_name)


def resolve_type(metadata: dict, column_name: str) -> str:
    """Return the declared type for a column, falling back to 'text'."""
    return metadata.get(column_name, {}).get("type", "text")


def metadata_from_monitoring_job(job) -> dict:
    """
    Build a column metadata dict from a MonitoringJob's field definitions.
    Called from APP-001 when generating output files.
    """
    return {
        f.name: {
            "label":       f.label or f.name,
            "type":        f.data_type,
            "unit":        "",
            "description": f.description,
            "required":    f.required,
            "choices":     f.choices,
        }
        for f in job.fields
        if f.enabled
    }


def render_column_metadata_panel(metadata: dict, selected_cols: list = None):
    """
    Render a column metadata reference panel in Streamlit.
    Shows labels, types, and descriptions for selected columns (or all if None).
    """
    import streamlit as st
    import pandas as pd

    if not metadata:
        return

    cols_to_show = selected_cols if selected_cols else list(metadata.keys())
    rows = []
    for col in cols_to_show:
        if col in metadata:
            m = metadata[col]
            rows.append({
                "Column":      col,
                "Label":       m.get("label", col),
                "Type":        m.get("type", "text"),
                "Required":    "Yes" if m.get("required") else "",
                "Description": m.get("description", ""),
            })
    if rows:
        with st.expander("📖 Column Reference (labels and types)"):
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
