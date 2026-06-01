"""Apps Script webhook connector — credentials from UI (credentials_manager) or st.secrets fallback."""
import requests


def _get_config() -> tuple[str, str] | tuple[None, None]:
    """
    Return (web_app_url, shared_secret) from the best available source.
    Priority: UI-saved → st.secrets → None
    """
    # Priority 1 — UI-saved via Integrations page
    try:
        from .credentials_manager import get_appscript_config
        cfg = get_appscript_config()
        if cfg and cfg.get("web_app_url"):
            return cfg["web_app_url"], cfg.get("shared_secret", "")
    except Exception:
        pass

    # Priority 2 — st.secrets / secrets.toml
    try:
        import streamlit as st
        if "apps_script" in st.secrets and st.secrets["apps_script"].get("web_app_url"):
            return (
                str(st.secrets["apps_script"]["web_app_url"]),
                str(st.secrets["apps_script"].get("shared_secret", "")),
            )
    except Exception:
        pass

    return None, None


def appscript_available() -> bool:
    """True if Apps Script web app URL is configured from any source."""
    url, _ = _get_config()
    return bool(url)


def appscript_status() -> dict:
    """Return {connected, url, error}."""
    url, _ = _get_config()
    if not url:
        return {"connected": False, "url": None, "error": "Not configured. Use Integrations page to set up Apps Script."}
    return {"connected": True, "url": url, "error": None}


def _call(action: str, payload: dict) -> dict:
    url, secret = _get_config()
    if not url:
        return {"status": "error", "error": "Apps Script not configured."}
    resp = requests.post(
        url,
        json={"action": action, "secret": secret, **payload},
        timeout=120,
    )
    resp.raise_for_status()
    return resp.json()


def appscript_aggregate(
    source_sheet_url: str,
    target_sheet_url: str,
    group_cols: list,
    metric_cols: list,
    agg_func: str = "SUM",
) -> dict:
    """Trigger the Apps Script aggregator. Returns {status, rows_written, timestamp}."""
    return _call("aggregate", {
        "source_url":  source_sheet_url,
        "target_url":  target_sheet_url,
        "group_cols":  group_cols,
        "metric_cols": metric_cols,
        "agg_func":    agg_func.upper(),
    })


def appscript_ping() -> dict:
    """Ping the Apps Script web app to verify it is live."""
    return _call("ping", {})
