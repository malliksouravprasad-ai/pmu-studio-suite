"""
Generates unique artifact IDs in PMU-YYYY-TYPE-SUBTYPE-NNNNN format.
"""
import csv
import os
from datetime import datetime

REGISTRY_PATH = os.path.join(os.path.dirname(__file__), "..", "registry.csv")


def _next_sequence(app_code: str, year: int) -> int:
    if not os.path.exists(REGISTRY_PATH):
        return 1
    with open(REGISTRY_PATH, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    matches = [
        int(r["artifact_id"].split("-")[-1])
        for r in rows
        if r.get("artifact_id", "").startswith(f"PMU-{year}-{app_code}")
    ]
    return max(matches, default=0) + 1


def generate_id(app_code: str, subtype: str = "") -> str:
    """
    app_code: e.g. 'FLN', 'ADM', 'ATR'
    subtype:  e.g. 'SURVEY', 'REPORT', 'MOM'  (optional)
    """
    year = datetime.now().year
    seq = _next_sequence(app_code, year)
    parts = ["PMU", str(year), app_code]
    if subtype:
        parts.append(subtype.upper())
    parts.append(f"{seq:05d}")
    return "-".join(parts)
