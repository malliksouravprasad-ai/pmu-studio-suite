"""Verify all 5 common services load and function correctly."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from shared import (
    # Serialization Engine
    generate_id, to_json, from_json, to_csv, from_csv,
    # Registry Manager
    register, get_entry, update_status, list_entries, registry_summary,
    # Template Library
    register_template, list_templates, scan_app_templates,
    # Google Integration (auth check only — no live call)
    credentials_available,
    # Excel Integration
    PMU_COLORS, create_workbook, style_header_row, style_section_row,
    write_dataframe, auto_width, freeze_header, save_workbook,
    # Utils
    setup_logger, output_path, timestamp_suffix,
)

log = setup_logger("VERIFY")

# ── 1. Serialization Engine ──────────────────────────────────────────────────
log.info("--- Serialization Engine ---")
id1 = generate_id("FLN", "SURVEY")
id2 = generate_id("ATR")
id3 = generate_id("FLN", "SURVEY")
log.info(f"  {id1}")
log.info(f"  {id2}")
log.info(f"  {id3}  (sequence incremented from {id1})")

data = [{"name": "Test", "value": 42}]
json_path = output_path("SHARED_TEST", "test.json")
to_json(data, json_path)
loaded = from_json(json_path)
assert loaded == data, "JSON round-trip failed"
log.info(f"  JSON round-trip OK")

csv_path = output_path("SHARED_TEST", "test.csv")
to_csv(data, csv_path)
loaded_csv = from_csv(csv_path)
assert loaded_csv[0]["name"] == "Test"
log.info(f"  CSV round-trip OK")

# ── 2. Registry Manager ──────────────────────────────────────────────────────
log.info("--- Registry Manager ---")
row = register("APP-TEST", id1, "PROJECT_X", "Survey", "output.xlsx")
row2 = register("APP-TEST", id2, "PROJECT_Y", "Report", "output2.xlsx")
entry = get_entry(id1)
assert entry is not None, "get_entry failed"
log.info(f"  Registered and retrieved: {entry['artifact_id']}")

updated = update_status(id1, "Reviewed")
assert updated
entry_after = get_entry(id1)
assert entry_after["status"] == "Reviewed"
log.info(f"  Status updated: {entry_after['status']}")

filtered = list_entries(app_id="APP-TEST", project="PROJECT_X")
assert len(filtered) >= 1
log.info(f"  Filtered list: {len(filtered)} entry/entries")

summ = registry_summary()
log.info(f"  Registry summary: {summ}")

# ── 3. Template Library ──────────────────────────────────────────────────────
log.info("--- Template Library ---")
import tempfile, pathlib
with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tf:
    dummy_path = tf.name
register_template("Test Template", dummy_path, app_id="APP-TEST",
                  description="Verify template", template_type="excel", tags=["test"])
templates = list_templates(app_id="APP-TEST", template_type="excel")
assert any(t["name"] == "Test Template" for t in templates)
log.info(f"  Registered and listed: {len(templates)} template(s)")

app_folder = os.path.join(os.path.dirname(__file__), "apps", "APP-001_Form_Builder")
scanned = scan_app_templates(app_folder)
log.info(f"  Scanned APP-001 templates: {len(scanned)} file(s)")

# ── 4. Google Integration ────────────────────────────────────────────────────
log.info("--- Google Integration ---")
avail = credentials_available()
log.info(f"  credentials.json present: {avail}")
log.info(f"  (Google API calls skipped — requires credentials.json)")

# ── 5. Excel Integration ─────────────────────────────────────────────────────
log.info("--- Excel Integration ---")
import pandas as pd
wb = create_workbook("Report")
ws = wb.active
style_header_row(ws, ["District", "Schools", "Attendance %", "Status"], row=1,
                 col_widths=[20, 12, 16, 14])
style_section_row(ws, "Region: North", row=2, col_count=4)
df = pd.DataFrame([
    ["Patna", "120", "87.3", "On Track"],
    ["Gaya", "95", "72.1", "At Risk"],
    ["Muzaffarpur", "110", "91.5", "On Track"],
])
write_dataframe(ws, df, start_row=3, alternate_rows=True)
auto_width(ws)
freeze_header(ws)
out = save_workbook(wb, "SHARED_TEST", f"verify_excel_{timestamp_suffix()}.xlsx")
log.info(f"  Excel written: {out}")
log.info(f"  PMU Colors available: {list(PMU_COLORS.keys())}")

log.info("")
log.info("=== ALL 5 COMMON SERVICES VERIFIED ===")

import os
os.remove(dummy_path)
