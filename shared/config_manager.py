"""
Configuration Manager — save, load, clone, version, export, and import
app configurations within a Project Workspace.

Configs are stored as JSON files inside the workspace's configurations/
subfolder, organized by app:

  <workspace>/configurations/<APP_ID>/<slug>_v<N>.json

Each file contains the full configuration payload plus metadata so that
any version can be retrieved and compared.
"""
import json
import re
from datetime import datetime
from pathlib import Path


# ── Save / Load ───────────────────────────────────────────────────────────────

def save_config(
    workspace_path: str | Path,
    app_id: str,
    name: str,
    config: dict,
) -> Path:
    """
    Save a configuration to the workspace.

    If a configuration with the same name already exists, a new version is
    created (version number incremented). Existing versions are never
    overwritten.

    Returns the path to the saved .json file.
    """
    folder = _config_folder(workspace_path, app_id)
    slug = _slugify(name)

    existing = list_configs(workspace_path, app_id)
    same_name = [c for c in existing if c.get("name") == name]
    version = (max(c["version"] for c in same_name) + 1) if same_name else 1

    payload = {
        "app_id": app_id,
        "name": name,
        "slug": slug,
        "version": version,
        "saved": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "config": config,
    }
    path = folder / f"{slug}_v{version}.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False, default=str)
    return path


def load_config(
    workspace_path: str | Path,
    app_id: str,
    name: str,
    version: int = None,
) -> dict:
    """
    Load a configuration by name (and optionally version).

    If version is None, the latest version is returned.
    Returns the full payload dict including 'config', 'version', 'saved'.
    Raises FileNotFoundError if the configuration does not exist.
    """
    candidates = [
        c for c in list_configs(workspace_path, app_id)
        if c.get("name") == name
    ]
    if not candidates:
        raise FileNotFoundError(
            f"No configuration named '{name}' for {app_id} in this workspace."
        )
    if version is not None:
        candidates = [c for c in candidates if c.get("version") == version]
        if not candidates:
            raise FileNotFoundError(
                f"Version {version} of '{name}' not found for {app_id}."
            )
    return max(candidates, key=lambda c: c["version"])


def load_config_by_file(config_file: str | Path) -> dict:
    """Load a configuration directly from a file path."""
    with open(config_file, encoding="utf-8") as f:
        return json.load(f)


# ── List / Delete ─────────────────────────────────────────────────────────────

def list_configs(workspace_path: str | Path, app_id: str) -> list[dict]:
    """
    Return all saved configurations for an app, sorted by name then version.
    Each entry is the full payload dict.
    """
    folder = _config_folder(workspace_path, app_id)
    configs = []
    for path in sorted(folder.glob("*.json")):
        try:
            with open(path, encoding="utf-8") as f:
                configs.append(json.load(f))
        except Exception:
            pass
    return configs


def list_all_configs(workspace_path: str | Path) -> dict[str, list[dict]]:
    """
    Return all saved configurations across all apps in this workspace.
    Returns a dict keyed by app_id.
    """
    configs_root = Path(workspace_path) / "configurations"
    if not configs_root.exists():
        return {}
    result = {}
    for app_folder in sorted(configs_root.iterdir()):
        if app_folder.is_dir():
            result[app_folder.name] = list_configs(workspace_path, app_folder.name)
    return result


def delete_config(
    workspace_path: str | Path,
    app_id: str,
    name: str,
    version: int = None,
) -> int:
    """
    Delete a configuration by name (and optionally a specific version).
    If version is None, all versions of that name are deleted.
    Returns the count of files deleted.
    """
    folder = _config_folder(workspace_path, app_id)
    slug = _slugify(name)
    count = 0
    for path in folder.glob(f"{slug}_v*.json"):
        if version is None:
            path.unlink()
            count += 1
        else:
            try:
                with open(path, encoding="utf-8") as f:
                    data = json.load(f)
                if data.get("version") == version:
                    path.unlink()
                    count += 1
            except Exception:
                pass
    return count


# ── Clone ─────────────────────────────────────────────────────────────────────

def clone_config(
    workspace_path: str | Path,
    app_id: str,
    source_name: str,
    new_name: str,
) -> Path:
    """
    Clone the latest version of a configuration under a new name.
    Returns the path to the new config file.
    """
    source = load_config(workspace_path, app_id, source_name)
    return save_config(workspace_path, app_id, new_name, source["config"])


# ── Export / Import ───────────────────────────────────────────────────────────

def export_config(
    workspace_path: str | Path,
    app_id: str,
    name: str,
    export_dir: str | Path,
    version: int = None,
) -> Path:
    """
    Export a configuration to a standalone .pmuconfig file.
    The .pmuconfig is a plain JSON file that can be shared and re-imported.
    Returns the path to the exported file.
    """
    config = load_config(workspace_path, app_id, name, version)
    export_dir = Path(export_dir)
    export_dir.mkdir(parents=True, exist_ok=True)
    slug = _slugify(name)
    out_path = export_dir / f"{app_id}_{slug}_v{config['version']}.pmuconfig"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False, default=str)
    return out_path


def import_config(
    workspace_path: str | Path,
    config_file: str | Path,
    override_name: str = None,
) -> Path:
    """
    Import a .pmuconfig (or any JSON config file) into the workspace.
    If override_name is given, the config is saved under that name.
    Returns the path to the saved config file.
    """
    with open(config_file, encoding="utf-8") as f:
        data = json.load(f)
    app_id = data.get("app_id", "UNKNOWN")
    name = override_name or data.get("name", "Imported Config")
    config = data.get("config", data)
    return save_config(workspace_path, app_id, name, config)


# ── Internals ─────────────────────────────────────────────────────────────────

def _config_folder(workspace_path: str | Path, app_id: str) -> Path:
    folder = Path(workspace_path) / "configurations" / app_id
    folder.mkdir(parents=True, exist_ok=True)
    return folder


def _slugify(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", name.lower().strip()).strip("_")
