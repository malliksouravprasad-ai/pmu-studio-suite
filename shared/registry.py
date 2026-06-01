"""
Registry Manager — system-wide tracking log for all generated outputs.

Every app must call register() after producing an output.
The registry is a flat CSV file at PMU_Tools/registry.csv.
All writes are protected by a file lock so concurrent users cannot corrupt it.
"""
import csv
import os
from datetime import datetime
from pathlib import Path

try:
    import filelock as _filelock
    _LOCK_AVAILABLE = True
except ImportError:
    _LOCK_AVAILABLE = False

_REGISTRY_PATH = Path(__file__).parent.parent / "registry.csv"
_LOCK_PATH     = _REGISTRY_PATH.with_suffix(".csv.lock")

FIELDS = [
    "app_id", "artifact_id", "date_generated",
    "project", "report_type", "output_file", "status",
    "source_file", "config_name", "config_version",
]


# ── Core operations ───────────────────────────────────────────────────────────

def register(
    app_id: str,
    artifact_id: str,
    project: str,
    report_type: str,
    output_file: str,
    status: str = "Generated",
    source_file: str = "",
    config_name: str = "",
    config_version: str = "",
) -> dict:
    """Add a new output entry to the registry. Returns the written row."""
    _ensure()
    row = {
        "app_id": app_id,
        "artifact_id": artifact_id,
        "date_generated": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "project": project,
        "report_type": report_type,
        "output_file": str(output_file),
        "status": status,
        "source_file": source_file,
        "config_name": config_name,
        "config_version": str(config_version),
    }
    with _lock():
        with open(_REGISTRY_PATH, "a", newline="", encoding="utf-8") as f:
            csv.DictWriter(f, fieldnames=FIELDS).writerow(row)
    return row


def get_entry(artifact_id: str) -> dict | None:
    """Return a single registry entry by artifact_id, or None."""
    for row in list_entries():
        if row.get("artifact_id") == artifact_id:
            return row
    return None


def update_status(artifact_id: str, new_status: str) -> bool:
    """Update the status of an existing entry. Returns True if found."""
    _ensure()
    rows = list_entries()
    found = False
    for row in rows:
        if row.get("artifact_id") == artifact_id:
            row["status"] = new_status
            found = True
    if found:
        _rewrite(rows)
    return found


def delete_entry(artifact_id: str) -> bool:
    """Remove an entry from the registry. Returns True if found."""
    _ensure()
    rows = list_entries()
    filtered = [r for r in rows if r.get("artifact_id") != artifact_id]
    if len(filtered) < len(rows):
        _rewrite(filtered)
        return True
    return False


# ── Querying ──────────────────────────────────────────────────────────────────

def list_entries(
    app_id: str = None,
    project: str = None,
    status: str = None,
    report_type: str = None,
) -> list[dict]:
    """
    Return registry entries, optionally filtered.
    All filters are case-insensitive partial matches.
    """
    _ensure()
    with open(_REGISTRY_PATH, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    if app_id:
        rows = [r for r in rows if r.get("app_id", "").upper() == app_id.upper()]
    if project:
        rows = [r for r in rows if project.lower() in r.get("project", "").lower()]
    if status:
        rows = [r for r in rows if r.get("status", "").lower() == status.lower()]
    if report_type:
        rows = [r for r in rows if report_type.lower() in r.get("report_type", "").lower()]
    return rows


def summary() -> dict:
    """Return count of entries grouped by app_id."""
    rows = list_entries()
    counts = {}
    for r in rows:
        counts[r.get("app_id", "?")] = counts.get(r.get("app_id", "?"), 0) + 1
    return counts


# ── Internals ─────────────────────────────────────────────────────────────────

def _lock():
    """Return a context manager that serialises registry writes across processes."""
    if _LOCK_AVAILABLE:
        return _filelock.FileLock(str(_LOCK_PATH), timeout=15)
    import contextlib
    return contextlib.nullcontext()


def _ensure():
    if not _REGISTRY_PATH.exists():
        with _lock():
            if not _REGISTRY_PATH.exists():  # double-check inside lock
                with open(_REGISTRY_PATH, "w", newline="", encoding="utf-8") as f:
                    csv.DictWriter(f, fieldnames=FIELDS).writeheader()


def _rewrite(rows: list[dict]):
    with _lock():
        with open(_REGISTRY_PATH, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=FIELDS)
            writer.writeheader()
            writer.writerows(rows)
