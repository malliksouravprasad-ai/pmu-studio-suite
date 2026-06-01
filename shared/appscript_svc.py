"""Apps Script webhook connector for PMU Tool Suite."""
import requests


def appscript_available() -> bool:
    """True if Apps Script web app URL is configured in st.secrets."""
    try:
        import streamlit as st
        return "apps_script" in st.secrets and "web_app_url" in st.secrets["apps_script"]
    except Exception:
        return False


def appscript_status() -> dict:
    """Return {connected, url, error}."""
    if not appscript_available():
        return {"connected": False, "url": None, "error": "Not configured in secrets.toml"}
    import streamlit as st
    return {"connected": True, "url": st.secrets["apps_script"]["web_app_url"], "error": None}


def _call(action: str, payload: dict) -> dict:
    import streamlit as st
    url    = st.secrets["apps_script"]["web_app_url"]
    secret = str(st.secrets["apps_script"].get("shared_secret", ""))
    resp   = requests.post(
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
    """
    Trigger the Apps Script aggregator.
    Returns {status, rows_written, timestamp} or {status, error}.
    """
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
