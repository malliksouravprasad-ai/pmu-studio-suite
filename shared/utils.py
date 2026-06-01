"""
Shared utility functions used across all PMU applications.
"""
import os
import sys
import logging
from datetime import datetime
from pathlib import Path


def setup_logger(app_name: str) -> logging.Logger:
    logger = logging.getLogger(app_name)
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s", "%Y-%m-%d %H:%M:%S"))
        logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    return logger


def output_path(app_folder: str, filename: str) -> str:
    """Returns absolute path inside the central outputs/ folder, creating it if needed."""
    base = Path(__file__).parent.parent / "outputs" / app_folder
    base.mkdir(parents=True, exist_ok=True)
    return str(base / filename)


def input_path(filename: str) -> str:
    """Returns absolute path inside the central inputs/ folder."""
    return str(Path(__file__).parent.parent / "inputs" / filename)


def timestamp_suffix() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def validate_file_exists(path: str) -> None:
    if not os.path.exists(path):
        raise FileNotFoundError(f"Input file not found: {path}")


def validate_columns(df, required: list[str]) -> list[str]:
    """Returns list of missing column names."""
    return [c for c in required if c not in df.columns]
