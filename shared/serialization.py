"""
Serialization Engine — artifact ID generation and data serialization.

Every output produced by any PMU app must have a unique artifact ID.
Format: PMU-YYYY-APPCODE-SUBTYPE-NNNNN
"""
import csv
import json
import os
from datetime import datetime
from pathlib import Path

_REGISTRY_PATH = Path(__file__).parent.parent / "registry.csv"


# ── ID Generation ─────────────────────────────────────────────────────────────

def generate_id(app_code: str, subtype: str = "") -> str:
    """
    Generate a unique PMU artifact ID.

    generate_id("FLN", "SURVEY")  →  PMU-2026-FLN-SURVEY-00001
    generate_id("ATR")            →  PMU-2026-ATR-00001
    """
    year = datetime.now().year
    seq = _next_sequence(app_code, year)
    parts = ["PMU", str(year), app_code.upper()]
    if subtype:
        parts.append(subtype.upper())
    parts.append(f"{seq:05d}")
    return "-".join(parts)


def _next_sequence(app_code: str, year: int) -> int:
    if not _REGISTRY_PATH.exists():
        return 1
    with open(_REGISTRY_PATH, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    prefix = f"PMU-{year}-{app_code.upper()}"
    nums = [
        int(r["artifact_id"].split("-")[-1])
        for r in rows
        if r.get("artifact_id", "").startswith(prefix)
        and r["artifact_id"].split("-")[-1].isdigit()
    ]
    return max(nums, default=0) + 1


# ── JSON Serialization ────────────────────────────────────────────────────────

def to_json(data: dict | list, path: str | Path, indent: int = 2) -> str:
    """Write data to a JSON file. Returns the written path."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=indent, ensure_ascii=False, default=str)
    return str(path)


def from_json(path: str | Path) -> dict | list:
    """Load and return a JSON file."""
    with open(path, encoding="utf-8") as f:
        return json.load(f)


# ── CSV Serialization ─────────────────────────────────────────────────────────

def to_csv(data: list[dict], path: str | Path, fieldnames: list[str] = None) -> str:
    """Write a list of dicts to CSV. Returns the written path."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = fieldnames or (list(data[0].keys()) if data else [])
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(data)
    return str(path)


def from_csv(path: str | Path) -> list[dict]:
    """Load a CSV file as a list of dicts."""
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


# ── DataFrame helpers (lazy import) ──────────────────────────────────────────

def df_to_csv(df, path: str | Path) -> str:
    """Write a pandas DataFrame to CSV."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False, encoding="utf-8")
    return str(path)


def df_from_csv(path: str | Path):
    """Read a CSV into a pandas DataFrame."""
    import pandas as pd
    return pd.read_csv(path, dtype=str).fillna("")


def df_to_json(df, path: str | Path) -> str:
    """Write a pandas DataFrame to JSON (records orientation)."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_json(path, orient="records", indent=2, force_ascii=False)
    return str(path)
