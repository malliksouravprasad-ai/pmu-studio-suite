"""Page 1 — Schema Builder: define data fields (data dictionary)."""
import sys
import os

_APP_DIR  = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_PMU_ROOT = os.path.dirname(os.path.dirname(_APP_DIR))
for _p in [_PMU_ROOT, _APP_DIR]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

import pandas as pd
import streamlit as st
from engine import (
    init_state, reset_state, get_workspace, get_job, get_studio_job, set_studio_job,
    add_field, remove_field, update_field, has_fields,
    move_field_up, move_field_down, load_framework_template,
    FieldDef, FIELD_TYPES,
)

st.set_page_config(page_title="Schema — Monitoring Builder", page_icon="📐", layout="wide")
init_state()

ws  = get_workspace()
job = get_job()

with st.sidebar:
    st.markdown("## 🏗️ Monitoring Builder")
    st.caption("APP-001 · OSEPA PMU Tool Suite")
    st.markdown("---")
    if ws:
        st.success(f"📁 **{ws['name']}**")
    else:
        st.warning("No workspace selected")
    st.info(f"**{len(job.fields)}** field(s) defined")
    if st.button("🗑 Reset Builder", use_container_width=True):
        reset_state(); st.rerun()

st.markdown("# 📐 Schema")
st.caption("Step 1 of 4 — Define the data fields your monitoring system will collect")
st.markdown("---")

# ── Framework Templates ────────────────────────────────────────────────────────
FRAMEWORK_TEMPLATES = {
    "School Monitoring": {
        "name": "School Monitoring Framework",
        "entity_type": "School",
        "form_title": "School Monitoring Visit Form",
        "form_description": "Monthly school monitoring data collection",
        "fields": [
            {"name": "udise_code",        "label": "UDISE Code",           "data_type": "code",    "required": True,  "is_identifier": True,  "choices": [], "description": "11-digit UDISE school code", "example": "21340200101", "enabled": True, "is_calculated": False},
            {"name": "school_name",       "label": "School Name",          "data_type": "text",    "required": True,  "is_identifier": False, "choices": [], "description": "Full name of the school", "example": "GOVT MS BARIPADA", "enabled": True, "is_calculated": False},
            {"name": "district",          "label": "District",             "data_type": "choice",  "required": True,  "is_identifier": False, "choices": [], "description": "District where school is located", "example": "", "enabled": True, "is_calculated": False},
            {"name": "block",             "label": "Block",                "data_type": "choice",  "required": True,  "is_identifier": False, "choices": [], "description": "Block/Mandal", "example": "", "enabled": True, "is_calculated": False},
            {"name": "school_category",   "label": "School Category",      "data_type": "choice",  "required": True,  "is_identifier": False, "choices": ["Primary", "Upper Primary", "Secondary", "Higher Secondary"], "description": "", "example": "", "enabled": True, "is_calculated": False},
            {"name": "total_enrolment",   "label": "Total Enrolment",      "data_type": "integer", "required": True,  "is_identifier": False, "choices": [], "description": "Total students enrolled", "example": "350", "enabled": True, "is_calculated": False},
            {"name": "boys_enrolment",    "label": "Boys Enrolment",       "data_type": "integer", "required": False, "is_identifier": False, "choices": [], "description": "", "example": "", "enabled": True, "is_calculated": False},
            {"name": "girls_enrolment",   "label": "Girls Enrolment",      "data_type": "integer", "required": False, "is_identifier": False, "choices": [], "description": "", "example": "", "enabled": True, "is_calculated": False},
            {"name": "teachers_present",  "label": "Teachers Present",     "data_type": "integer", "required": True,  "is_identifier": False, "choices": [], "description": "Number of teachers present on visit day", "example": "8", "enabled": True, "is_calculated": False},
            {"name": "teachers_sanctioned","label": "Teachers Sanctioned",  "data_type": "integer", "required": True,  "is_identifier": False, "choices": [], "description": "Number of sanctioned teaching posts", "example": "10", "enabled": True, "is_calculated": False},
            {"name": "students_present",  "label": "Students Present",     "data_type": "integer", "required": True,  "is_identifier": False, "choices": [], "description": "Students present on visit day", "example": "280", "enabled": True, "is_calculated": False},
            {"name": "infrastructure_status", "label": "Infrastructure Status", "data_type": "choice", "required": False, "is_identifier": False, "choices": ["Good", "Satisfactory", "Needs Repair", "Poor"], "description": "", "example": "", "enabled": True, "is_calculated": False},
            {"name": "visit_date",        "label": "Visit Date",           "data_type": "date",    "required": True,  "is_identifier": False, "choices": [], "description": "", "example": "2026-06-01", "enabled": True, "is_calculated": False},
            {"name": "reported_by",       "label": "Reported By",          "data_type": "text",    "required": True,  "is_identifier": False, "choices": [], "description": "Name of the monitor", "example": "", "enabled": True, "is_calculated": False},
            {"name": "remarks",           "label": "Remarks",              "data_type": "text",    "required": False, "is_identifier": False, "choices": [], "description": "Any additional observations", "example": "", "enabled": True, "is_calculated": False},
        ],
        "sections": [
            {"title": "School Identification", "description": "Basic school details", "field_names": ["udise_code", "school_name", "district", "block", "school_category"]},
            {"title": "Enrolment Data", "description": "Student enrolment figures", "field_names": ["total_enrolment", "boys_enrolment", "girls_enrolment"]},
            {"title": "Attendance", "description": "Attendance on visit day", "field_names": ["teachers_present", "teachers_sanctioned", "students_present"]},
            {"title": "Monitoring Details", "description": "Visit and infrastructure", "field_names": ["infrastructure_status", "visit_date", "reported_by", "remarks"]},
        ],
        "rule_defs": [
            {"rule_id": "r001", "name": "UDISE Required", "rule_type": "required", "column": "udise_code", "severity": "error", "enabled": True, "params": {}},
            {"rule_id": "r002", "name": "Enrolment Positive", "rule_type": "range_check", "column": "total_enrolment", "severity": "error", "enabled": True, "params": {"min": 1, "max": 5000}},
            {"rule_id": "r003", "name": "Attendance Positive", "rule_type": "range_check", "column": "students_present", "severity": "warning", "enabled": True, "params": {"min": 0, "max": 5000}},
        ],
        "kpi_defs": [
            {"kpi_id": "k001", "name": "Student Attendance Rate", "formula": "percentage", "value_col": "", "numerator_col": "students_present", "denominator_col": "total_enrolment", "target": 75.0, "target_col": "", "weight": 2.0, "interpretation": "higher_better", "enabled": True},
            {"kpi_id": "k002", "name": "Teacher Attendance Rate", "formula": "percentage", "value_col": "", "numerator_col": "teachers_present", "denominator_col": "teachers_sanctioned", "target": 90.0, "target_col": "", "weight": 2.0, "interpretation": "higher_better", "enabled": True},
            {"kpi_id": "k003", "name": "Girls Enrolment Share", "formula": "percentage", "value_col": "", "numerator_col": "girls_enrolment", "denominator_col": "total_enrolment", "target": 50.0, "target_col": "", "weight": 1.0, "interpretation": "higher_better", "enabled": True},
        ],
    },
    "District Performance": {
        "name": "District Performance Framework",
        "entity_type": "District",
        "form_title": "District Monthly Performance Report",
        "form_description": "Monthly district-level performance data",
        "fields": [
            {"name": "district_code",   "label": "District Code",          "data_type": "code",    "required": True,  "is_identifier": True,  "choices": [], "description": "LGD district code", "example": "512", "enabled": True, "is_calculated": False},
            {"name": "district_name",   "label": "District Name",          "data_type": "text",    "required": True,  "is_identifier": False, "choices": [], "description": "", "example": "", "enabled": True, "is_calculated": False},
            {"name": "state",           "label": "State",                  "data_type": "text",    "required": True,  "is_identifier": False, "choices": [], "description": "", "example": "", "enabled": True, "is_calculated": False},
            {"name": "total_schools",   "label": "Total Schools",          "data_type": "integer", "required": True,  "is_identifier": False, "choices": [], "description": "", "example": "", "enabled": True, "is_calculated": False},
            {"name": "schools_monitored","label": "Schools Monitored",     "data_type": "integer", "required": True,  "is_identifier": False, "choices": [], "description": "Schools visited this month", "example": "", "enabled": True, "is_calculated": False},
            {"name": "total_enrolment", "label": "Total Enrolment",        "data_type": "integer", "required": True,  "is_identifier": False, "choices": [], "description": "", "example": "", "enabled": True, "is_calculated": False},
            {"name": "avg_attendance",  "label": "Avg Attendance %",       "data_type": "number",  "required": True,  "is_identifier": False, "choices": [], "description": "District-level average attendance", "example": "", "enabled": True, "is_calculated": False},
            {"name": "infrastructure_good","label": "Schools — Good Infrastructure","data_type": "integer","required": False,"is_identifier": False,"choices": [],"description": "","example": "","enabled": True,"is_calculated": False},
            {"name": "report_month",    "label": "Report Month",           "data_type": "text",    "required": True,  "is_identifier": False, "choices": [], "description": "YYYY-MM", "example": "2026-05", "enabled": True, "is_calculated": False},
            {"name": "submitted_by",    "label": "Submitted By",           "data_type": "text",    "required": True,  "is_identifier": False, "choices": [], "description": "", "example": "", "enabled": True, "is_calculated": False},
        ],
        "sections": [
            {"title": "District Identification", "field_names": ["district_code", "district_name", "state"], "description": ""},
            {"title": "Coverage Data", "field_names": ["total_schools", "schools_monitored", "total_enrolment"], "description": ""},
            {"title": "Performance Indicators", "field_names": ["avg_attendance", "infrastructure_good"], "description": ""},
            {"title": "Report Details", "field_names": ["report_month", "submitted_by"], "description": ""},
        ],
        "rule_defs": [
            {"rule_id": "r001", "name": "District Code Required", "rule_type": "required", "column": "district_code", "severity": "error", "enabled": True, "params": {}},
            {"rule_id": "r002", "name": "Monitoring Coverage Valid", "rule_type": "range_check", "column": "schools_monitored", "severity": "error", "enabled": True, "params": {"min": 0, "max": 10000}},
        ],
        "kpi_defs": [
            {"kpi_id": "k001", "name": "Monitoring Coverage", "formula": "percentage", "value_col": "", "numerator_col": "schools_monitored", "denominator_col": "total_schools", "target": 80.0, "target_col": "", "weight": 2.0, "interpretation": "higher_better", "enabled": True},
            {"kpi_id": "k002", "name": "Average Attendance", "formula": "value", "value_col": "avg_attendance", "numerator_col": "", "denominator_col": "", "target": 75.0, "target_col": "", "weight": 2.0, "interpretation": "higher_better", "enabled": True},
        ],
    },
    "Teacher Attendance": {
        "name": "Teacher Attendance Monitoring",
        "entity_type": "School",
        "form_title": "Teacher Attendance Register",
        "form_description": "Daily teacher attendance data collection",
        "fields": [
            {"name": "school_id",        "label": "School ID",             "data_type": "code",    "required": True,  "is_identifier": True,  "choices": [], "description": "", "example": "", "enabled": True, "is_calculated": False},
            {"name": "school_name",      "label": "School Name",           "data_type": "text",    "required": True,  "is_identifier": False, "choices": [], "description": "", "example": "", "enabled": True, "is_calculated": False},
            {"name": "district",         "label": "District",              "data_type": "text",    "required": True,  "is_identifier": False, "choices": [], "description": "", "example": "", "enabled": True, "is_calculated": False},
            {"name": "date",             "label": "Date",                  "data_type": "date",    "required": True,  "is_identifier": False, "choices": [], "description": "Attendance date", "example": "", "enabled": True, "is_calculated": False},
            {"name": "total_teachers",   "label": "Total Teachers",        "data_type": "integer", "required": True,  "is_identifier": False, "choices": [], "description": "Total teachers on rolls", "example": "", "enabled": True, "is_calculated": False},
            {"name": "teachers_present", "label": "Teachers Present",      "data_type": "integer", "required": True,  "is_identifier": False, "choices": [], "description": "", "example": "", "enabled": True, "is_calculated": False},
            {"name": "teachers_on_leave","label": "Teachers on Leave",     "data_type": "integer", "required": False, "is_identifier": False, "choices": [], "description": "", "example": "", "enabled": True, "is_calculated": False},
            {"name": "head_teacher_present","label": "Head Teacher Present","data_type": "boolean","required": True,  "is_identifier": False, "choices": ["Yes", "No"], "description": "", "example": "", "enabled": True, "is_calculated": False},
            {"name": "reason_absent",    "label": "Reason for Absence",    "data_type": "text",    "required": False, "is_identifier": False, "choices": [], "description": "If any teacher absent without leave", "example": "", "enabled": True, "is_calculated": False},
            {"name": "verified_by",      "label": "Verified By",           "data_type": "text",    "required": True,  "is_identifier": False, "choices": [], "description": "", "example": "", "enabled": True, "is_calculated": False},
        ],
        "sections": [
            {"title": "School Details", "field_names": ["school_id", "school_name", "district"], "description": ""},
            {"title": "Attendance Record", "field_names": ["date", "total_teachers", "teachers_present", "teachers_on_leave", "head_teacher_present"], "description": ""},
            {"title": "Remarks", "field_names": ["reason_absent", "verified_by"], "description": ""},
        ],
        "rule_defs": [
            {"rule_id": "r001", "name": "School ID Required", "rule_type": "required", "column": "school_id", "severity": "error", "enabled": True, "params": {}},
            {"rule_id": "r002", "name": "Present Cannot Exceed Total", "rule_type": "compare_columns", "column": "teachers_present", "severity": "error", "enabled": True, "params": {"compare_col": "total_teachers", "operator": "<="}},
        ],
        "kpi_defs": [
            {"kpi_id": "k001", "name": "Teacher Attendance Rate", "formula": "percentage", "value_col": "", "numerator_col": "teachers_present", "denominator_col": "total_teachers", "target": 90.0, "target_col": "", "weight": 1.0, "interpretation": "higher_better", "enabled": True},
        ],
    },
    "Infrastructure Assessment": {
        "name": "Infrastructure Assessment Framework",
        "entity_type": "School",
        "form_title": "School Infrastructure Assessment",
        "form_description": "Annual infrastructure condition survey",
        "fields": [
            {"name": "school_id",        "label": "School ID",             "data_type": "code",    "required": True,  "is_identifier": True,  "choices": [], "description": "", "example": "", "enabled": True, "is_calculated": False},
            {"name": "school_name",      "label": "School Name",           "data_type": "text",    "required": True,  "is_identifier": False, "choices": [], "description": "", "example": "", "enabled": True, "is_calculated": False},
            {"name": "district",         "label": "District",              "data_type": "text",    "required": True,  "is_identifier": False, "choices": [], "description": "", "example": "", "enabled": True, "is_calculated": False},
            {"name": "classrooms_total", "label": "Total Classrooms",      "data_type": "integer", "required": True,  "is_identifier": False, "choices": [], "description": "", "example": "", "enabled": True, "is_calculated": False},
            {"name": "classrooms_good",  "label": "Classrooms in Good Condition","data_type": "integer","required": True,"is_identifier": False,"choices": [],"description": "","example": "","enabled": True,"is_calculated": False},
            {"name": "toilets_boys",     "label": "Boys Toilets",          "data_type": "integer", "required": True,  "is_identifier": False, "choices": [], "description": "", "example": "", "enabled": True, "is_calculated": False},
            {"name": "toilets_girls",    "label": "Girls Toilets",         "data_type": "integer", "required": True,  "is_identifier": False, "choices": [], "description": "", "example": "", "enabled": True, "is_calculated": False},
            {"name": "drinking_water",   "label": "Drinking Water Available","data_type": "boolean","required": True, "is_identifier": False, "choices": ["Yes", "No"], "description": "", "example": "", "enabled": True, "is_calculated": False},
            {"name": "electricity",      "label": "Electricity Connection", "data_type": "boolean","required": True,  "is_identifier": False, "choices": ["Yes", "No"], "description": "", "example": "", "enabled": True, "is_calculated": False},
            {"name": "boundary_wall",    "label": "Boundary Wall",         "data_type": "choice",  "required": False, "is_identifier": False, "choices": ["Complete", "Partial", "None"], "description": "", "example": "", "enabled": True, "is_calculated": False},
            {"name": "ramp_available",   "label": "Ramp for Disabled",     "data_type": "boolean", "required": False, "is_identifier": False, "choices": ["Yes", "No"], "description": "", "example": "", "enabled": True, "is_calculated": False},
            {"name": "assessment_date",  "label": "Assessment Date",       "data_type": "date",    "required": True,  "is_identifier": False, "choices": [], "description": "", "example": "", "enabled": True, "is_calculated": False},
            {"name": "assessed_by",      "label": "Assessed By",           "data_type": "text",    "required": True,  "is_identifier": False, "choices": [], "description": "", "example": "", "enabled": True, "is_calculated": False},
        ],
        "sections": [
            {"title": "School Details", "field_names": ["school_id", "school_name", "district"], "description": ""},
            {"title": "Classrooms", "field_names": ["classrooms_total", "classrooms_good"], "description": ""},
            {"title": "Sanitation & Utilities", "field_names": ["toilets_boys", "toilets_girls", "drinking_water", "electricity"], "description": ""},
            {"title": "Other Infrastructure", "field_names": ["boundary_wall", "ramp_available"], "description": ""},
            {"title": "Assessment Details", "field_names": ["assessment_date", "assessed_by"], "description": ""},
        ],
        "rule_defs": [
            {"rule_id": "r001", "name": "School ID Required", "rule_type": "required", "column": "school_id", "severity": "error", "enabled": True, "params": {}},
            {"rule_id": "r002", "name": "Good Classrooms Cannot Exceed Total", "rule_type": "compare_columns", "column": "classrooms_good", "severity": "error", "enabled": True, "params": {"compare_col": "classrooms_total", "operator": "<="}},
        ],
        "kpi_defs": [
            {"kpi_id": "k001", "name": "Classroom Condition Score", "formula": "percentage", "value_col": "", "numerator_col": "classrooms_good", "denominator_col": "classrooms_total", "target": 80.0, "target_col": "", "weight": 2.0, "interpretation": "higher_better", "enabled": True},
        ],
    },
    "Learning Outcomes": {
        "name": "Learning Outcomes Assessment",
        "entity_type": "School",
        "form_title": "Learning Outcomes Assessment Form",
        "form_description": "Foundational literacy and numeracy assessment data",
        "fields": [
            {"name": "school_id",        "label": "School ID",             "data_type": "code",    "required": True,  "is_identifier": True,  "choices": [], "description": "", "example": "", "enabled": True, "is_calculated": False},
            {"name": "school_name",      "label": "School Name",           "data_type": "text",    "required": True,  "is_identifier": False, "choices": [], "description": "", "example": "", "enabled": True, "is_calculated": False},
            {"name": "district",         "label": "District",              "data_type": "text",    "required": True,  "is_identifier": False, "choices": [], "description": "", "example": "", "enabled": True, "is_calculated": False},
            {"name": "grade",            "label": "Grade",                 "data_type": "choice",  "required": True,  "is_identifier": False, "choices": ["Grade 1", "Grade 2", "Grade 3", "Grade 4", "Grade 5"], "description": "", "example": "", "enabled": True, "is_calculated": False},
            {"name": "students_assessed","label": "Students Assessed",     "data_type": "integer", "required": True,  "is_identifier": False, "choices": [], "description": "", "example": "", "enabled": True, "is_calculated": False},
            {"name": "literacy_level1",  "label": "Literacy — Level 1 (Letters)","data_type": "integer","required": True,"is_identifier": False,"choices": [],"description": "Students who can identify letters","example": "","enabled": True,"is_calculated": False},
            {"name": "literacy_level2",  "label": "Literacy — Level 2 (Words)", "data_type": "integer","required": True,"is_identifier": False,"choices": [],"description": "Students who can read words","example": "","enabled": True,"is_calculated": False},
            {"name": "literacy_level3",  "label": "Literacy — Level 3 (Paragraph)","data_type": "integer","required": True,"is_identifier": False,"choices": [],"description": "Students who can read a paragraph","example": "","enabled": True,"is_calculated": False},
            {"name": "numeracy_level1",  "label": "Numeracy — Level 1 (Numbers)","data_type": "integer","required": True,"is_identifier": False,"choices": [],"description": "Students who recognise numbers","example": "","enabled": True,"is_calculated": False},
            {"name": "numeracy_level2",  "label": "Numeracy — Level 2 (Operations)","data_type": "integer","required": True,"is_identifier": False,"choices": [],"description": "Students who can do basic operations","example": "","enabled": True,"is_calculated": False},
            {"name": "assessment_date",  "label": "Assessment Date",       "data_type": "date",    "required": True,  "is_identifier": False, "choices": [], "description": "", "example": "", "enabled": True, "is_calculated": False},
            {"name": "assessed_by",      "label": "Assessed By",           "data_type": "text",    "required": True,  "is_identifier": False, "choices": [], "description": "", "example": "", "enabled": True, "is_calculated": False},
        ],
        "sections": [
            {"title": "School Details", "field_names": ["school_id", "school_name", "district", "grade"], "description": ""},
            {"title": "Literacy Assessment", "field_names": ["students_assessed", "literacy_level1", "literacy_level2", "literacy_level3"], "description": ""},
            {"title": "Numeracy Assessment", "field_names": ["numeracy_level1", "numeracy_level2"], "description": ""},
            {"title": "Assessment Details", "field_names": ["assessment_date", "assessed_by"], "description": ""},
        ],
        "rule_defs": [
            {"rule_id": "r001", "name": "School ID Required", "rule_type": "required", "column": "school_id", "severity": "error", "enabled": True, "params": {}},
            {"rule_id": "r002", "name": "Literacy L3 Cannot Exceed Assessed", "rule_type": "compare_columns", "column": "literacy_level3", "severity": "error", "enabled": True, "params": {"compare_col": "students_assessed", "operator": "<="}},
        ],
        "kpi_defs": [
            {"kpi_id": "k001", "name": "Paragraph Reading Rate", "formula": "percentage", "value_col": "", "numerator_col": "literacy_level3", "denominator_col": "students_assessed", "target": 60.0, "target_col": "", "weight": 2.0, "interpretation": "higher_better", "enabled": True},
            {"kpi_id": "k002", "name": "Basic Numeracy Rate", "formula": "percentage", "value_col": "", "numerator_col": "numeracy_level2", "denominator_col": "students_assessed", "target": 60.0, "target_col": "", "weight": 2.0, "interpretation": "higher_better", "enabled": True},
        ],
    },
}

with st.expander("🚀 Start from a Framework Template", expanded=not has_fields()):
    st.caption("Load a pre-built monitoring framework — all fields, validation rules, and KPIs included")
    t_cols = st.columns(len(FRAMEWORK_TEMPLATES))
    for i, (tname, tdata) in enumerate(FRAMEWORK_TEMPLATES.items()):
        entity = tdata["entity_type"]
        n_fields = len(tdata["fields"])
        n_kpis   = len(tdata["kpi_defs"])
        with t_cols[i]:
            st.markdown(f"**{tname}**")
            st.caption(f"{entity} · {n_fields} fields · {n_kpis} KPIs")
            if st.button(f"Load", key=f"tmpl_{i}", use_container_width=True, type="primary"):
                load_framework_template(tdata)
                st.success(f"Template **{tname}** loaded."); st.rerun()

st.markdown("---")

# ── Quick-add common fields ───────────────────────────────────────────────────
with st.expander("⚡ Quick-add common fields", expanded=False):
    st.caption("Click to add individual standard monitoring fields")
    preset_cols = st.columns(4)
    presets = [
        ("UDISE Code",       "udise_code",       "code",    True,  True,  []),
        ("School Name",      "school_name",       "text",    True,  False, []),
        ("District",         "district",          "choice",  True,  False, []),
        ("Block",            "block",             "choice",  False, False, []),
        ("Total Enrolment",  "total_enrolment",   "integer", True,  False, []),
        ("Boys Enrolment",   "boys_enrolment",    "integer", False, False, []),
        ("Girls Enrolment",  "girls_enrolment",   "integer", False, False, []),
        ("Attendance %",     "attendance_pct",    "number",  False, False, []),
        ("Visit Date",       "visit_date",        "date",    True,  False, []),
        ("Reported By",      "reported_by",       "text",    True,  False, []),
        ("Remarks",          "remarks",           "text",    False, False, []),
        ("Verification Status", "verified_status","choice",  False, False, ["Verified", "Pending", "Rejected"]),
    ]
    existing_names = {f.name for f in job.fields}
    for i, (label, name, dtype, req, is_id, choices) in enumerate(presets):
        if preset_cols[i % 4].button(label, key=f"preset_{name}", use_container_width=True,
                                      disabled=(name in existing_names)):
            add_field(FieldDef(name=name, label=label, data_type=dtype,
                               required=req, is_identifier=is_id, choices=choices))
            st.rerun()

# ── Add field manually ────────────────────────────────────────────────────────
st.markdown("### Add Field")
with st.form("add_field_form", clear_on_submit=True):
    c1, c2 = st.columns(2)
    f_label    = c1.text_input("Field Label *", placeholder="e.g. School Name")
    f_name     = c1.text_input("Column Name *", placeholder="e.g. school_name (no spaces)")
    f_type     = c2.selectbox("Data Type", list(FIELD_TYPES.keys()), format_func=lambda k: FIELD_TYPES[k])
    f_required = c2.checkbox("Required field")
    f_id_field = c2.checkbox("Primary entity identifier (e.g., school code)")

    f_choices  = ""
    if f_type in ("choice", "boolean"):
        if f_type == "boolean":
            f_choices = "Yes, No"
        else:
            f_choices = st.text_input("Choices (comma-separated)", placeholder="e.g. Cuttack, Khordha, Puri")

    c3, c4 = st.columns(2)
    f_desc    = c3.text_input("Description", placeholder="What this field means")
    f_example = c4.text_input("Example value", placeholder="e.g. 12345678901")

    if st.form_submit_button("Add Field", type="primary"):
        if not f_label.strip() or not f_name.strip():
            st.error("Label and column name are required.")
        elif " " in f_name.strip():
            st.error("Column name cannot contain spaces — use underscores.")
        elif f_name.strip() in {f.name for f in job.fields}:
            st.error(f"A field named '{f_name.strip()}' already exists.")
        else:
            choices = [c.strip() for c in f_choices.split(",") if c.strip()] if f_choices else []
            add_field(FieldDef(
                name=f_name.strip(), label=f_label.strip(), data_type=f_type,
                required=f_required, is_identifier=f_id_field,
                choices=choices, description=f_desc.strip(), example=f_example.strip(),
            ))
            st.success(f"Field **{f_label.strip()}** added."); st.rerun()

# ── Import from Excel ─────────────────────────────────────────────────────────
with st.expander("📥 Import schema from Excel/CSV"):
    st.caption("Upload a file with columns: name, label, data_type, required, choices, description")
    imported = st.file_uploader("Upload schema file", type=["csv", "xlsx"], key="schema_import")
    if imported:
        try:
            schema_df = pd.read_csv(imported) if imported.name.endswith(".csv") else pd.read_excel(imported)
            st.dataframe(schema_df.head(), use_container_width=True)
            if st.button("Import Fields"):
                added = 0
                existing_names = {f.name for f in job.fields}
                for _, row in schema_df.iterrows():
                    nm = str(row.get("name", "")).strip()
                    lb = str(row.get("label", nm)).strip()
                    dt = str(row.get("data_type", "text")).strip()
                    if nm and nm not in existing_names:
                        choices = [c.strip() for c in str(row.get("choices", "")).split(",") if c.strip()]
                        add_field(FieldDef(
                            name=nm, label=lb or nm,
                            data_type=dt if dt in FIELD_TYPES else "text",
                            required=str(row.get("required", "")).lower() in ("yes", "true", "1"),
                            choices=choices,
                            description=str(row.get("description", "")),
                        ))
                        added += 1
                st.success(f"Imported {added} field(s)."); st.rerun()
        except Exception as e:
            st.error(f"Could not parse file: {e}")

# ── Field table ───────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("### Defined Fields")
if not job.fields:
    st.info("No fields defined yet. Load a template above or add fields using the form.")
else:
    n_fields = len(job.fields)
    for idx, fld in enumerate(job.fields):
        with st.container(border=True):
            c1, c2, c3, c4, c5 = st.columns([5, 1, 1, 1, 1])
            badge = "🔑" if fld.is_identifier else ("⭐" if fld.required else "○")
            c1.markdown(f"{badge} **{fld.label}** `{fld.name}` — `{fld.data_type}`"
                        + (f" — choices: {', '.join(fld.choices[:4])}" if fld.choices else ""))
            if fld.description:
                c1.caption(fld.description)
            with c2:
                if idx > 0 and st.button("↑", key=f"up_{fld.field_id}", use_container_width=True,
                                          help="Move up"):
                    move_field_up(fld.field_id); st.rerun()
            with c3:
                if idx < n_fields - 1 and st.button("↓", key=f"dn_{fld.field_id}", use_container_width=True,
                                                      help="Move down"):
                    move_field_down(fld.field_id); st.rerun()
            with c4:
                if st.button("Edit", key=f"ed_{fld.field_id}", use_container_width=True):
                    st.session_state[f"edit_{fld.field_id}"] = True
            with c5:
                if st.button("✕", key=f"rm_{fld.field_id}", use_container_width=True, help="Remove"):
                    remove_field(fld.field_id); st.rerun()

            if st.session_state.get(f"edit_{fld.field_id}"):
                with st.form(f"edit_form_{fld.field_id}"):
                    ec1, ec2 = st.columns(2)
                    new_label = ec1.text_input("Label", value=fld.label)
                    new_desc  = ec2.text_input("Description", value=fld.description)
                    new_choices = st.text_input("Choices (comma-separated)", value=", ".join(fld.choices))
                    new_req   = st.checkbox("Required", value=fld.required)
                    new_id    = st.checkbox("Primary identifier", value=fld.is_identifier)
                    if st.form_submit_button("Save Changes"):
                        fld.label       = new_label.strip()
                        fld.description = new_desc.strip()
                        fld.choices     = [c.strip() for c in new_choices.split(",") if c.strip()]
                        fld.required    = new_req
                        fld.is_identifier = new_id
                        update_field(fld)
                        st.session_state.pop(f"edit_{fld.field_id}", None)
                        st.rerun()

    st.markdown(f"**{len(job.fields)} field(s) defined** — "
                f"{sum(1 for f in job.fields if f.required)} required, "
                f"{sum(1 for f in job.fields if f.is_identifier)} identifier(s)")
