"""
Package Manager — export, import, clone, and restore .pmupack files.

A .pmupack is a ZIP archive of a complete Project Workspace directory.
It captures forms, rules, mappings, KPI definitions, dashboard layouts,
workflow definitions, templates, configurations, and metadata in one file
that can be moved between machines or shared with other PMU teams.

Usage:
    export_package("teacher_training", Path("exports/"))
    → exports/teacher_training_20260531_143000.pmupack

    import_package(Path("exports/teacher_training_20260531_143000.pmupack"))
    → restores to workspaces/teacher_training/
"""
import json
import shutil
import zipfile
from datetime import datetime
from pathlib import Path

from .workspace import (
    _WORKSPACES_ROOT,
    _read_meta,
    _write_meta,
    slugify,
    WORKSPACE_FOLDERS,
)

PACK_EXT = ".pmupack"


# ── Export ────────────────────────────────────────────────────────────────────

def export_package(slug: str, output_dir: str | Path) -> Path:
    """
    Pack a workspace into a .pmupack file.

    The archive preserves the full workspace folder structure.
    Output filename format: <slug>_YYYYMMDD_HHMMSS.pmupack

    Returns the path to the created file.
    Raises FileNotFoundError if the workspace does not exist.
    """
    ws_path = _WORKSPACES_ROOT / slug
    if not ws_path.exists():
        raise FileNotFoundError(f"Workspace '{slug}' not found.")

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    pack_name = f"{slug}_{stamp}{PACK_EXT}"
    pack_path = output_dir / pack_name

    with zipfile.ZipFile(pack_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for file in sorted(ws_path.rglob("*")):
            if file.is_file():
                zf.write(file, file.relative_to(ws_path))

    return pack_path


# ── Import ────────────────────────────────────────────────────────────────────

def import_package(
    pack_path: str | Path,
    new_name: str = None,
    overwrite: bool = False,
) -> dict:
    """
    Restore a .pmupack file into the workspaces directory.

    If new_name is provided, the workspace is imported under that name.
    If overwrite is True and the slug already exists, it is deleted first.

    Returns the imported workspace metadata dict (including 'path').
    Raises FileExistsError if the target slug exists and overwrite is False.
    Raises ValueError if the pack file does not contain workspace.json.
    """
    pack_path = Path(pack_path)
    if not pack_path.exists():
        raise FileNotFoundError(f"Package file not found: {pack_path}")

    with zipfile.ZipFile(pack_path, "r") as zf:
        try:
            meta = json.loads(zf.read("workspace.json"))
        except KeyError:
            raise ValueError(
                "Invalid .pmupack: workspace.json not found in the archive."
            )

        if new_name:
            meta["name"] = new_name
            meta["slug"] = slugify(new_name)

        slug = meta["slug"]
        ws_path = _WORKSPACES_ROOT / slug

        if ws_path.exists():
            if overwrite:
                shutil.rmtree(ws_path)
            else:
                raise FileExistsError(
                    f"Workspace '{slug}' already exists. "
                    "Use overwrite=True or choose a different name."
                )

        _WORKSPACES_ROOT.mkdir(parents=True, exist_ok=True)
        ws_path.mkdir(parents=True)
        zf.extractall(ws_path)

    # Ensure all standard subfolders exist (in case pack was from older version)
    for folder in WORKSPACE_FOLDERS:
        (ws_path / folder).mkdir(exist_ok=True)

    meta["modified"] = datetime.now().strftime("%Y-%m-%d %H:%M")
    _write_meta(ws_path, meta)
    meta["path"] = str(ws_path)
    return meta


# ── Clone ─────────────────────────────────────────────────────────────────────

def clone_package(slug: str, new_name: str) -> dict:
    """
    Clone an existing workspace into a new workspace.

    Performs a full directory copy. The clone gets a fresh 'created' timestamp
    and version 1. All configurations, rules, templates, etc. are preserved.

    Returns the new workspace metadata dict.
    Raises FileNotFoundError if the source workspace does not exist.
    Raises FileExistsError if the target name is already taken.
    """
    src_path = _WORKSPACES_ROOT / slug
    if not src_path.exists():
        raise FileNotFoundError(f"Workspace '{slug}' not found.")

    new_slug = slugify(new_name)
    dest_path = _WORKSPACES_ROOT / new_slug
    if dest_path.exists():
        raise FileExistsError(f"Workspace '{new_name}' already exists.")

    shutil.copytree(src_path, dest_path)

    meta = _read_meta(dest_path)
    meta["name"] = new_name
    meta["slug"] = new_slug
    meta["created"] = datetime.now().strftime("%Y-%m-%d %H:%M")
    meta["modified"] = datetime.now().strftime("%Y-%m-%d %H:%M")
    meta["version"] = 1
    _write_meta(dest_path, meta)
    meta["path"] = str(dest_path)
    return meta


# ── Inspect ───────────────────────────────────────────────────────────────────

def package_info(pack_path: str | Path) -> dict:
    """
    Read workspace metadata from a .pmupack without extracting it.
    Returns the metadata dict, or {'error': <reason>} if unreadable.
    """
    try:
        with zipfile.ZipFile(pack_path, "r") as zf:
            return json.loads(zf.read("workspace.json"))
    except KeyError:
        return {"error": "Invalid package: workspace.json not found"}
    except Exception as e:
        return {"error": str(e)}


def list_packages(search_dir: str | Path) -> list[dict]:
    """
    Return info for all .pmupack files found in a directory.
    Each entry includes 'file' (path) and the metadata fields from workspace.json.
    """
    search_dir = Path(search_dir)
    results = []
    for pack in sorted(search_dir.glob(f"*{PACK_EXT}")):
        info = package_info(pack)
        info["file"] = str(pack)
        results.append(info)
    return results
