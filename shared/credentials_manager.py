"""
Credentials Manager — saves and reads integration credentials
from /pmu/config/integrations.json inside the container.

Priority order for every service:
  1. UI-saved credentials (this file)        — set by admin in Integrations page
  2. st.secrets / secrets.toml               — baked into Docker image as fallback
  3. Local credentials.json                  — for local development only
"""
import json
from pathlib import Path

_CONFIG_DIR  = Path(__file__).parent.parent / "config"
_CREDS_FILE  = _CONFIG_DIR / "integrations.json"


# ── Internal helpers ──────────────────────────────────────────────────────────

def _load() -> dict:
    if _CREDS_FILE.exists():
        try:
            return json.loads(_CREDS_FILE.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def _save(data: dict) -> None:
    _CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    _CREDS_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


# ── Google / Service Account ──────────────────────────────────────────────────

def get_google_sa() -> dict | None:
    """Return saved service account dict, or None if not configured via UI."""
    return _load().get("google_sa")


def save_google_sa(sa_dict: dict) -> None:
    data = _load()
    data["google_sa"] = sa_dict
    _save(data)


def clear_google_sa() -> None:
    data = _load()
    data.pop("google_sa", None)
    _save(data)


# ── BigQuery ──────────────────────────────────────────────────────────────────

def get_bigquery_config() -> dict | None:
    return _load().get("bigquery")


def save_bigquery_config(project_id: str, dataset_id: str) -> None:
    data = _load()
    data["bigquery"] = {"project_id": project_id.strip(), "dataset_id": dataset_id.strip()}
    _save(data)


def clear_bigquery_config() -> None:
    data = _load()
    data.pop("bigquery", None)
    _save(data)


# ── Apps Script ───────────────────────────────────────────────────────────────

def get_appscript_config() -> dict | None:
    return _load().get("apps_script")


def save_appscript_config(url: str, secret: str) -> None:
    data = _load()
    data["apps_script"] = {"web_app_url": url.strip(), "shared_secret": secret.strip()}
    _save(data)


def clear_appscript_config() -> None:
    data = _load()
    data.pop("apps_script", None)
    _save(data)


# ── Utility ───────────────────────────────────────────────────────────────────

def integration_summary() -> dict:
    """Return current configuration status for all integrations."""
    data = _load()
    sa  = data.get("google_sa", {})
    bq  = data.get("bigquery", {})
    asc = data.get("apps_script", {})
    return {
        "google": {
            "configured": bool(sa),
            "project":    sa.get("project_id"),
            "email":      sa.get("client_email"),
        },
        "bigquery": {
            "configured": bool(bq.get("project_id")),
            "project":    bq.get("project_id"),
            "dataset":    bq.get("dataset_id"),
        },
        "apps_script": {
            "configured": bool(asc.get("web_app_url")),
            "url":        asc.get("web_app_url"),
        },
    }
