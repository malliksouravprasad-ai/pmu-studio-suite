"""
Project Workspace Manager — create, open, and manage project workspaces.

A workspace preserves project memory across sessions: configurations, forms,
data sources, rules, mappings, KPIs, dashboards, deliverables, workflows,
outputs, templates, and a per-project registry.

Workspace root: PMU_Tools/workspaces/<slug>/
"""
import json
import re
import shutil
from datetime import datetime
from pathlib import Path

_WORKSPACES_ROOT = Path(__file__).parent.parent / "workspaces"

WORKSPACE_FOLDERS = [
    "configurations",
    "forms",
    "data_sources",
    "rules",
    "mappings",
    "kpis",
    "dashboards",
    "deliverables",
    "workflows",
    "outputs",
    "templates",
    "registry",
]


# ── Create / Delete ───────────────────────────────────────────────────────────

def create_workspace(
    name: str,
    project_code: str,
    user_tag: str = "",
    description: str = "",
) -> dict:
    """
    Create a new project workspace on disk.

    user_tag: identifies the creator (e.g. 'Malli', 'District_A').
    When provided, the workspace slug includes the tag so two users can create
    workspaces with the same name without collision.

    Returns the workspace metadata dict (including 'path').
    Raises FileExistsError if this user already has a workspace with this name.
    """
    _WORKSPACES_ROOT.mkdir(parents=True, exist_ok=True)
    _tag = slugify(user_tag) if user_tag.strip() else ""
    slug = slugify(f"{name}_{_tag}") if _tag else slugify(name)
    ws_path = _WORKSPACES_ROOT / slug
    if ws_path.exists():
        raise FileExistsError(
            f"Workspace '{name}' already exists"
            + (f" for user '{user_tag}'." if user_tag else ".")
        )

    ws_path.mkdir(parents=True)
    for folder in WORKSPACE_FOLDERS:
        (ws_path / folder).mkdir()

    meta = {
        "name": name,
        "slug": slug,
        "project_code": project_code.upper().strip(),
        "user_tag": user_tag.strip(),
        "description": description,
        "created": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "modified": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "version": 1,
    }
    _write_meta(ws_path, meta)
    meta["path"] = str(ws_path)
    return meta


def delete_workspace(slug: str) -> None:
    """Permanently delete a workspace directory."""
    ws_path = _WORKSPACES_ROOT / slug
    if not ws_path.exists():
        raise FileNotFoundError(f"Workspace '{slug}' not found.")
    shutil.rmtree(ws_path)


# ── Load / List ───────────────────────────────────────────────────────────────

def load_workspace(slug: str) -> dict:
    """
    Load an existing workspace by its slug.
    Returns the metadata dict (including 'path').
    """
    ws_path = _WORKSPACES_ROOT / slug
    if not ws_path.exists():
        raise FileNotFoundError(f"Workspace '{slug}' not found.")
    meta = _read_meta(ws_path)
    meta["path"] = str(ws_path)
    return meta


def list_workspaces() -> list[dict]:
    """
    Return metadata for all existing workspaces, sorted by name.
    Each entry includes a 'path' key.
    """
    _WORKSPACES_ROOT.mkdir(parents=True, exist_ok=True)
    results = []
    for ws_path in sorted(_WORKSPACES_ROOT.iterdir()):
        meta_file = ws_path / "workspace.json"
        if ws_path.is_dir() and meta_file.exists():
            try:
                meta = _read_meta(ws_path)
                meta["path"] = str(ws_path)
                results.append(meta)
            except Exception:
                pass
    return results


# ── Update ────────────────────────────────────────────────────────────────────

def update_workspace(slug: str, **kwargs) -> dict:
    """
    Update any metadata fields of an existing workspace.
    Always updates 'modified' timestamp automatically.
    Returns the updated metadata dict.
    """
    ws_path = _WORKSPACES_ROOT / slug
    if not ws_path.exists():
        raise FileNotFoundError(f"Workspace '{slug}' not found.")
    meta = _read_meta(ws_path)
    for k, v in kwargs.items():
        if k not in ("slug", "created", "path"):  # these are immutable
            meta[k] = v
    meta["modified"] = datetime.now().strftime("%Y-%m-%d %H:%M")
    _write_meta(ws_path, meta)
    meta["path"] = str(ws_path)
    return meta


# ── Path Helpers ──────────────────────────────────────────────────────────────

def workspace_path(slug: str) -> Path:
    """Return the root Path of a workspace."""
    return _WORKSPACES_ROOT / slug


def get_folder(slug: str, folder: str) -> Path:
    """
    Return the Path to a named subfolder within a workspace.
    Creates the folder if it does not exist.
    Folder names: configurations, forms, data_sources, rules, mappings,
                  kpis, dashboards, deliverables, workflows, outputs,
                  templates, registry
    """
    path = _WORKSPACES_ROOT / slug / folder
    path.mkdir(parents=True, exist_ok=True)
    return path


# ── Internals ─────────────────────────────────────────────────────────────────

def slugify(name: str) -> str:
    """Convert a workspace name to a safe directory slug."""
    return re.sub(r"[^a-z0-9]+", "_", name.lower().strip()).strip("_")


def _write_meta(ws_path: Path, meta: dict) -> None:
    with open(ws_path / "workspace.json", "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2, ensure_ascii=False)


def _read_meta(ws_path: Path) -> dict:
    with open(ws_path / "workspace.json", encoding="utf-8") as f:
        return json.load(f)
