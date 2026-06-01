"""
Template Library — discover, register, and load reusable templates.

Covers all template types used across PMU apps:
  excel, word, ppt, form, survey

Templates are indexed in PMU_Tools/templates/template_index.json.
Each app can also have its own local template folder for app-specific forms.
"""
import json
import shutil
from datetime import datetime
from pathlib import Path

_ROOT = Path(__file__).parent.parent
_TEMPLATES_DIR = _ROOT / "templates"
_INDEX_PATH = _TEMPLATES_DIR / "template_index.json"

TEMPLATE_TYPES = ("excel", "word", "ppt", "form", "survey")


# ── Index management ──────────────────────────────────────────────────────────

def _load_index() -> list[dict]:
    if not _INDEX_PATH.exists():
        return []
    with open(_INDEX_PATH, encoding="utf-8") as f:
        return json.load(f)


def _save_index(index: list[dict]):
    _TEMPLATES_DIR.mkdir(parents=True, exist_ok=True)
    with open(_INDEX_PATH, "w", encoding="utf-8") as f:
        json.dump(index, f, indent=2, ensure_ascii=False)


# ── Public API ────────────────────────────────────────────────────────────────

def register_template(
    name: str,
    path: str | Path,
    app_id: str = "SHARED",
    description: str = "",
    template_type: str = "excel",
    tags: list[str] = None,
) -> dict:
    """
    Register a template file in the shared index.

    name:          Human-readable name (e.g. "School Visit Report")
    path:          Absolute path to the template file
    app_id:        Owning app (e.g. "APP-012") or "SHARED" for cross-app use
    template_type: One of excel / word / ppt / form / survey
    """
    index = _load_index()
    entry = {
        "id": _slug(name, app_id),
        "name": name,
        "app_id": app_id,
        "type": template_type,
        "path": str(path),
        "description": description,
        "tags": tags or [],
        "registered": datetime.now().strftime("%Y-%m-%d"),
    }
    index = [e for e in index if e.get("id") != entry["id"]]
    index.append(entry)
    _save_index(index)
    return entry


def list_templates(
    app_id: str = None,
    template_type: str = None,
    tag: str = None,
) -> list[dict]:
    """
    Return templates from the index, optionally filtered.

    list_templates()                    # all templates
    list_templates(app_id="APP-012")    # only PPT Generator templates
    list_templates(template_type="excel")
    list_templates(tag="district")
    """
    entries = _load_index()
    if app_id:
        entries = [e for e in entries if e.get("app_id") in (app_id, "SHARED")]
    if template_type:
        entries = [e for e in entries if e.get("type") == template_type]
    if tag:
        entries = [e for e in entries if tag.lower() in [t.lower() for t in e.get("tags", [])]]
    return entries


def get_template_path(name: str, app_id: str = None) -> Path | None:
    """
    Return the Path to a registered template, or None if not found.
    Verifies the file exists before returning.
    """
    for entry in list_templates(app_id=app_id):
        if entry.get("name") == name:
            p = Path(entry["path"])
            return p if p.exists() else None
    return None


def copy_template(name: str, destination: str | Path, app_id: str = None) -> Path | None:
    """
    Copy a registered template to destination.
    Returns the destination path, or None if template not found.
    """
    src = get_template_path(name, app_id)
    if not src:
        return None
    dest = Path(destination)
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dest)
    return dest


def remove_template(name: str, app_id: str = None):
    """Remove a template entry from the index (does not delete the file)."""
    index = _load_index()
    slug = _slug(name, app_id or "SHARED")
    _save_index([e for e in index if e.get("id") != slug])


# ── Local app template scanning ───────────────────────────────────────────────

def scan_app_templates(app_folder: str | Path) -> list[dict]:
    """
    Scan an app's local templates/ subfolder and return metadata for each file.
    Does NOT register them in the global index.
    """
    folder = Path(app_folder) / "templates"
    if not folder.exists():
        return []
    results = []
    for path in sorted(folder.rglob("*")):
        if path.is_file() and not path.name.startswith("."):
            ext = path.suffix.lower()
            t_type = {"xlsx": "excel", "docx": "word", "pptx": "ppt",
                      "json": "form"}.get(ext.lstrip("."), "other")
            results.append({
                "name": path.stem,
                "file": path.name,
                "type": t_type,
                "path": str(path),
                "size_kb": round(path.stat().st_size / 1024, 1),
            })
    return results


# ── Helpers ───────────────────────────────────────────────────────────────────

def _slug(name: str, app_id: str) -> str:
    return f"{app_id}::{name.lower().replace(' ', '_')}"
