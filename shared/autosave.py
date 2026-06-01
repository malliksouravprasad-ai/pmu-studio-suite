"""
Auto-save utility — saves the current studio job to workspace on each page load
when a workspace is active and auto-save is enabled.

Usage in any Streamlit page:
    from shared import autosave_job
    autosave_job(ws, job, "APP-002", "Auto-saved pipeline")
"""
import json
import os
from datetime import datetime
from pathlib import Path


def autosave_job(workspace: dict, job_config: dict, app_id: str, config_name: str = None) -> bool:
    """
    Save job config to workspace as an auto-save entry.

    workspace:   workspace metadata dict (must have 'path' key).
    job_config:  the result of job.to_config() — a serializable dict.
    app_id:      e.g. 'APP-002'.
    config_name: optional display name; defaults to 'Auto-save YYYY-MM-DD HH:MM'.

    Returns True if save succeeded, False if skipped (no workspace).
    """
    if not workspace or not workspace.get("path"):
        return False

    config_name = config_name or f"Auto-save {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    autosave_dir = Path(workspace["path"]) / "configurations" / app_id / "autosave"
    autosave_dir.mkdir(parents=True, exist_ok=True)

    payload = {
        "app_id":    app_id,
        "name":      config_name,
        "slug":      "autosave",
        "version":   "auto",
        "saved":     datetime.now().isoformat(),
        "config":    job_config,
    }
    target = autosave_dir / "latest.json"
    target.write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")
    return True


def load_autosave(workspace: dict, app_id: str) -> dict | None:
    """
    Load the most recent auto-save for an app, or None if not found.
    Returns the full payload dict (with 'config', 'saved', etc.).
    """
    if not workspace or not workspace.get("path"):
        return None
    target = Path(workspace["path"]) / "configurations" / app_id / "autosave" / "latest.json"
    if not target.exists():
        return None
    try:
        return json.loads(target.read_text(encoding="utf-8"))
    except Exception:
        return None


def render_autosave_controls(ws: dict, app_id: str, job, key_prefix: str = ""):
    """
    Render auto-save toggle + restore banner in Streamlit.
    Call this from any app page sidebar after init_state().

    ws:         result of get_workspace()
    app_id:     e.g. 'APP-002'
    job:        the current studio job (must have .to_config())
    key_prefix: prefix for session state keys to avoid collisions

    Returns True if auto-save is active (caller may want to save on their own actions too).
    """
    import streamlit as st

    if not ws:
        return False

    # Auto-save toggle
    autosave_key = f"{key_prefix}_autosave_enabled"
    if autosave_key not in st.session_state:
        st.session_state[autosave_key] = True

    enabled = st.sidebar.checkbox("Auto-save to workspace", value=st.session_state[autosave_key],
                                   key=f"{key_prefix}_autosave_cb",
                                   help="Automatically saves your current configuration to workspace on each page load.")
    st.session_state[autosave_key] = enabled

    if enabled:
        try:
            autosave_job(ws, job.to_config(), app_id)
        except Exception:
            pass

    # Restore banner
    saved = load_autosave(ws, app_id)
    if saved:
        saved_time = saved.get("saved", "unknown time")
        restore_key = f"{key_prefix}_autosave_dismissed"
        if not st.session_state.get(restore_key):
            with st.sidebar:
                st.info(f"Auto-save: {saved_time[:16]}")

    return enabled
