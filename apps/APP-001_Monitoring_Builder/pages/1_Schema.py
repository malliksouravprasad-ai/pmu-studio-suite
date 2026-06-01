"""Page 1 — Schema Builder: inline table field editor."""
import sys, os
_APP_DIR  = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_PMU_ROOT = os.path.dirname(os.path.dirname(_APP_DIR))
for _p in [_PMU_ROOT, _APP_DIR]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

import pandas as pd
import streamlit as st
from shared.theme import page_header, sidebar_brand
from engine import (
    init_state, reset_state, get_workspace, get_job, get_studio_job, set_studio_job,
    add_field, remove_field, update_field, has_fields,
    load_framework_template, FieldDef, FIELD_TYPES,
)

st.set_page_config(page_title="Schema — Monitoring Builder", page_icon="📐", layout="wide")
init_state()

ws  = get_workspace()
job = get_job()

with st.sidebar:
    sidebar_brand("Monitoring Builder", "APP-001")
    if ws:
        st.success(f"📁 **{ws['name']}**")
    else:
        st.warning("No workspace selected")
    st.info(f"**{len(job.fields)}** field(s) defined")
    if st.button("🗑 Reset Builder", use_container_width=True):
        reset_state(); st.rerun()

page_header("Schema", subtitle="Define every field your monitoring system will collect", icon="📐", step=1, total_steps=5)

# ── Framework templates ───────────────────────────────────────────────────────
FRAMEWORK_TEMPLATES = {
    "School Monitoring": {
        "name": "School Monitoring Framework", "entity_type": "School",
        "form_title": "School Monitoring Visit Form",
        "form_description": "Monthly school monitoring data collection",
        "fields": [
            {"name":"udise_code","label":"UDISE Code","data_type":"code","required":True,"is_identifier":True,"choices":[],"description":"11-digit UDISE school code","example":"21340200101","enabled":True,"is_calculated":False},
            {"name":"school_name","label":"School Name","data_type":"text","required":True,"is_identifier":False,"choices":[],"description":"Full name of the school","example":"GOVT MS BARIPADA","enabled":True,"is_calculated":False},
            {"name":"district","label":"District","data_type":"choice","required":True,"is_identifier":False,"choices":[],"description":"District where school is located","example":"","enabled":True,"is_calculated":False},
            {"name":"block","label":"Block","data_type":"choice","required":True,"is_identifier":False,"choices":[],"description":"Block/Mandal","example":"","enabled":True,"is_calculated":False},
            {"name":"school_category","label":"School Category","data_type":"choice","required":True,"is_identifier":False,"choices":["Primary","Upper Primary","Secondary","Higher Secondary"],"description":"","example":"","enabled":True,"is_calculated":False},
            {"name":"total_enrolment","label":"Total Enrolment","data_type":"integer","required":True,"is_identifier":False,"choices":[],"description":"Total students enrolled","example":"350","enabled":True,"is_calculated":False},
            {"name":"boys_enrolment","label":"Boys Enrolment","data_type":"integer","required":False,"is_identifier":False,"choices":[],"description":"","example":"","enabled":True,"is_calculated":False},
            {"name":"girls_enrolment","label":"Girls Enrolment","data_type":"integer","required":False,"is_identifier":False,"choices":[],"description":"","example":"","enabled":True,"is_calculated":False},
            {"name":"teachers_present","label":"Teachers Present","data_type":"integer","required":True,"is_identifier":False,"choices":[],"description":"Number of teachers present on visit day","example":"8","enabled":True,"is_calculated":False},
            {"name":"teachers_sanctioned","label":"Teachers Sanctioned","data_type":"integer","required":True,"is_identifier":False,"choices":[],"description":"Number of sanctioned teaching posts","example":"10","enabled":True,"is_calculated":False},
            {"name":"students_present","label":"Students Present","data_type":"integer","required":True,"is_identifier":False,"choices":[],"description":"Students present on visit day","example":"280","enabled":True,"is_calculated":False},
            {"name":"infrastructure_status","label":"Infrastructure Status","data_type":"choice","required":False,"is_identifier":False,"choices":["Good","Satisfactory","Needs Repair","Poor"],"description":"","example":"","enabled":True,"is_calculated":False},
            {"name":"visit_date","label":"Visit Date","data_type":"date","required":True,"is_identifier":False,"choices":[],"description":"","example":"2026-06-01","enabled":True,"is_calculated":False},
            {"name":"reported_by","label":"Reported By","data_type":"text","required":True,"is_identifier":False,"choices":[],"description":"Name of the monitor","example":"","enabled":True,"is_calculated":False},
            {"name":"remarks","label":"Remarks","data_type":"text","required":False,"is_identifier":False,"choices":[],"description":"Any additional observations","example":"","enabled":True,"is_calculated":False},
        ],
        "sections":[{"title":"School Identification","description":"","field_names":["udise_code","school_name","district","block","school_category"]},{"title":"Enrolment Data","description":"","field_names":["total_enrolment","boys_enrolment","girls_enrolment"]},{"title":"Attendance","description":"","field_names":["teachers_present","teachers_sanctioned","students_present"]},{"title":"Monitoring Details","description":"","field_names":["infrastructure_status","visit_date","reported_by","remarks"]}],
        "rule_defs":[{"rule_id":"r001","name":"UDISE Required","rule_type":"required","column":"udise_code","severity":"error","enabled":True,"params":{}},{"rule_id":"r002","name":"Enrolment Positive","rule_type":"range_check","column":"total_enrolment","severity":"error","enabled":True,"params":{"min":1,"max":5000}}],
        "kpi_defs":[{"kpi_id":"k001","name":"Student Attendance Rate","formula":"percentage","value_col":"","numerator_col":"students_present","denominator_col":"total_enrolment","target":75.0,"target_col":"","weight":2.0,"interpretation":"higher_better","enabled":True},{"kpi_id":"k002","name":"Teacher Attendance Rate","formula":"percentage","value_col":"","numerator_col":"teachers_present","denominator_col":"teachers_sanctioned","target":90.0,"target_col":"","weight":2.0,"interpretation":"higher_better","enabled":True}],
    },
    "District Performance": {
        "name": "District Performance Framework", "entity_type": "District",
        "form_title": "District Monthly Performance Report",
        "form_description": "Monthly district-level performance data",
        "fields": [
            {"name":"district_code","label":"District Code","data_type":"code","required":True,"is_identifier":True,"choices":[],"description":"LGD district code","example":"512","enabled":True,"is_calculated":False},
            {"name":"district_name","label":"District Name","data_type":"text","required":True,"is_identifier":False,"choices":[],"description":"","example":"","enabled":True,"is_calculated":False},
            {"name":"total_schools","label":"Total Schools","data_type":"integer","required":True,"is_identifier":False,"choices":[],"description":"","example":"","enabled":True,"is_calculated":False},
            {"name":"schools_monitored","label":"Schools Monitored","data_type":"integer","required":True,"is_identifier":False,"choices":[],"description":"Schools visited this month","example":"","enabled":True,"is_calculated":False},
            {"name":"total_enrolment","label":"Total Enrolment","data_type":"integer","required":True,"is_identifier":False,"choices":[],"description":"","example":"","enabled":True,"is_calculated":False},
            {"name":"avg_attendance","label":"Avg Attendance %","data_type":"number","required":True,"is_identifier":False,"choices":[],"description":"District-level average attendance","example":"","enabled":True,"is_calculated":False},
            {"name":"report_month","label":"Report Month","data_type":"text","required":True,"is_identifier":False,"choices":[],"description":"YYYY-MM","example":"2026-05","enabled":True,"is_calculated":False},
            {"name":"submitted_by","label":"Submitted By","data_type":"text","required":True,"is_identifier":False,"choices":[],"description":"","example":"","enabled":True,"is_calculated":False},
        ],
        "sections":[{"title":"District Identification","field_names":["district_code","district_name"],"description":""},{"title":"Coverage Data","field_names":["total_schools","schools_monitored","total_enrolment"],"description":""},{"title":"Performance","field_names":["avg_attendance"],"description":""},{"title":"Report Details","field_names":["report_month","submitted_by"],"description":""}],
        "rule_defs":[{"rule_id":"r001","name":"District Code Required","rule_type":"required","column":"district_code","severity":"error","enabled":True,"params":{}}],
        "kpi_defs":[{"kpi_id":"k001","name":"Monitoring Coverage","formula":"percentage","value_col":"","numerator_col":"schools_monitored","denominator_col":"total_schools","target":80.0,"target_col":"","weight":2.0,"interpretation":"higher_better","enabled":True},{"kpi_id":"k002","name":"Average Attendance","formula":"value","value_col":"avg_attendance","numerator_col":"","denominator_col":"","target":75.0,"target_col":"","weight":2.0,"interpretation":"higher_better","enabled":True}],
    },
    "Learning Outcomes": {
        "name": "Learning Outcomes Assessment", "entity_type": "School",
        "form_title": "Learning Outcomes Assessment Form",
        "form_description": "Foundational literacy and numeracy assessment data",
        "fields": [
            {"name":"school_id","label":"School ID","data_type":"code","required":True,"is_identifier":True,"choices":[],"description":"","example":"","enabled":True,"is_calculated":False},
            {"name":"school_name","label":"School Name","data_type":"text","required":True,"is_identifier":False,"choices":[],"description":"","example":"","enabled":True,"is_calculated":False},
            {"name":"district","label":"District","data_type":"text","required":True,"is_identifier":False,"choices":[],"description":"","example":"","enabled":True,"is_calculated":False},
            {"name":"grade","label":"Grade","data_type":"choice","required":True,"is_identifier":False,"choices":["Grade 1","Grade 2","Grade 3","Grade 4","Grade 5"],"description":"","example":"","enabled":True,"is_calculated":False},
            {"name":"students_assessed","label":"Students Assessed","data_type":"integer","required":True,"is_identifier":False,"choices":[],"description":"","example":"","enabled":True,"is_calculated":False},
            {"name":"literacy_level3","label":"Literacy — Paragraph Level","data_type":"integer","required":True,"is_identifier":False,"choices":[],"description":"Students who can read a paragraph","example":"","enabled":True,"is_calculated":False},
            {"name":"numeracy_level2","label":"Numeracy — Operations Level","data_type":"integer","required":True,"is_identifier":False,"choices":[],"description":"Students who can do basic operations","example":"","enabled":True,"is_calculated":False},
            {"name":"assessment_date","label":"Assessment Date","data_type":"date","required":True,"is_identifier":False,"choices":[],"description":"","example":"","enabled":True,"is_calculated":False},
            {"name":"assessed_by","label":"Assessed By","data_type":"text","required":True,"is_identifier":False,"choices":[],"description":"","example":"","enabled":True,"is_calculated":False},
        ],
        "sections":[{"title":"School Details","field_names":["school_id","school_name","district","grade"],"description":""},{"title":"Assessment","field_names":["students_assessed","literacy_level3","numeracy_level2"],"description":""},{"title":"Details","field_names":["assessment_date","assessed_by"],"description":""}],
        "rule_defs":[{"rule_id":"r001","name":"School ID Required","rule_type":"required","column":"school_id","severity":"error","enabled":True,"params":{}}],
        "kpi_defs":[{"kpi_id":"k001","name":"Paragraph Reading Rate","formula":"percentage","value_col":"","numerator_col":"literacy_level3","denominator_col":"students_assessed","target":60.0,"target_col":"","weight":2.0,"interpretation":"higher_better","enabled":True},{"kpi_id":"k002","name":"Basic Numeracy Rate","formula":"percentage","value_col":"","numerator_col":"numeracy_level2","denominator_col":"students_assessed","target":60.0,"target_col":"","weight":2.0,"interpretation":"higher_better","enabled":True}],
    },
}

# ── Template selector ─────────────────────────────────────────────────────────
with st.expander("🚀 Start from a Framework Template", expanded=not has_fields()):
    st.caption("Load a pre-built framework — fields, rules, and KPIs included")
    t_cols = st.columns(len(FRAMEWORK_TEMPLATES))
    for i, (tname, tdata) in enumerate(FRAMEWORK_TEMPLATES.items()):
        with t_cols[i]:
            st.markdown(f"**{tname}**")
            st.caption(f"{tdata['entity_type']} · {len(tdata['fields'])} fields · {len(tdata['kpi_defs'])} KPIs")
            if st.button("Load", key=f"tmpl_{i}", use_container_width=True, type="primary"):
                load_framework_template(tdata)
                st.success(f"Template **{tname}** loaded."); st.rerun()

# ── Quick-add presets ─────────────────────────────────────────────────────────
with st.expander("⚡ Quick-add common fields"):
    st.caption("Click to instantly add a standard field")
    presets = [
        ("UDISE Code","udise_code","code",True,True,[]),
        ("School Name","school_name","text",True,False,[]),
        ("District","district","choice",True,False,[]),
        ("Block","block","choice",False,False,[]),
        ("Total Enrolment","total_enrolment","integer",True,False,[]),
        ("Boys Enrolment","boys_enrolment","integer",False,False,[]),
        ("Girls Enrolment","girls_enrolment","integer",False,False,[]),
        ("Attendance %","attendance_pct","number",False,False,[]),
        ("Visit Date","visit_date","date",True,False,[]),
        ("Reported By","reported_by","text",True,False,[]),
        ("Remarks","remarks","text",False,False,[]),
        ("Verification Status","verified_status","choice",False,False,["Verified","Pending","Rejected"]),
    ]
    existing_names = {f.name for f in job.fields}
    preset_cols = st.columns(6)
    for i, (label, name, dtype, req, is_id, choices) in enumerate(presets):
        if preset_cols[i % 6].button(label, key=f"preset_{name}", use_container_width=True,
                                      disabled=(name in existing_names)):
            add_field(FieldDef(name=name, label=label, data_type=dtype,
                               required=req, is_identifier=is_id, choices=choices))
            st.rerun()

# ── Import from file ──────────────────────────────────────────────────────────
with st.expander("📥 Import schema from Excel / CSV"):
    st.caption("File must have columns: name, label, data_type, required, choices, description")
    imported = st.file_uploader("Upload schema file", type=["csv","xlsx"], key="schema_import")
    if imported:
        try:
            schema_df = pd.read_csv(imported) if imported.name.endswith(".csv") else pd.read_excel(imported)
            st.dataframe(schema_df.head(), use_container_width=True)
            if st.button("Import Fields", type="primary"):
                added = 0
                existing = {f.name for f in job.fields}
                for _, row in schema_df.iterrows():
                    nm = str(row.get("name","")).strip()
                    lb = str(row.get("label", nm)).strip()
                    dt = str(row.get("data_type","text")).strip()
                    if nm and nm not in existing:
                        choices = [c.strip() for c in str(row.get("choices","")).split(",") if c.strip()]
                        add_field(FieldDef(
                            name=nm, label=lb or nm,
                            data_type=dt if dt in FIELD_TYPES else "text",
                            required=str(row.get("required","")).lower() in ("yes","true","1"),
                            choices=choices,
                            description=str(row.get("description","")),
                        ))
                        added += 1
                st.success(f"Imported {added} field(s)."); st.rerun()
        except Exception as e:
            st.error(f"Could not parse file: {e}")

st.markdown("---")

# ── Inline table editor ────────────────────────────────────────────────────────
st.markdown("### Fields")
st.caption("Edit any cell directly. Click **+** in the last row to add a new field. Select a row and press Delete to remove it.")

TYPE_OPTIONS = list(FIELD_TYPES.keys())

def _fields_to_df(fields):
    rows = []
    for f in fields:
        rows.append({
            "Field Label":   f.label,
            "Column Name":   f.name,
            "Type":          f.data_type,
            "Required":      f.required,
            "PK":            f.is_identifier,
            "Choices":       ", ".join(f.choices),
            "Description":   f.description,
            "Example":       f.example,
            "_id":           f.field_id,
        })
    return pd.DataFrame(rows)

def _empty_df():
    return pd.DataFrame(columns=["Field Label","Column Name","Type","Required","PK","Choices","Description","Example","_id"])

if has_fields():
    df_current = _fields_to_df(job.fields)
else:
    df_current = _empty_df()

edited_df = st.data_editor(
    df_current,
    column_config={
        "Field Label":  st.column_config.TextColumn("Field Label *", help="Human-readable name, e.g. School Name", width="medium"),
        "Column Name":  st.column_config.TextColumn("Column Name *", help="No spaces, use underscores, e.g. school_name", width="medium"),
        "Type":         st.column_config.SelectboxColumn("Type", options=TYPE_OPTIONS,
                            help="text / integer / number / code / date / choice / boolean", width="small"),
        "Required":     st.column_config.CheckboxColumn("Req.", width="small"),
        "PK":           st.column_config.CheckboxColumn("PK", help="Primary entity identifier (e.g. UDISE code)", width="small"),
        "Choices":      st.column_config.TextColumn("Choices", help="Comma-separated, for choice/boolean types", width="medium"),
        "Description":  st.column_config.TextColumn("Description", width="large"),
        "Example":      st.column_config.TextColumn("Example", width="medium"),
        "_id":          None,  # hidden — internal ID for update tracking
    },
    num_rows="dynamic",
    use_container_width=True,
    hide_index=True,
    key="field_table",
    column_order=["Field Label","Column Name","Type","Required","PK","Choices","Description","Example"],
)

col_save, col_discard, col_spacer = st.columns([2, 2, 8])

with col_save:
    if st.button("💾 Save All Fields", type="primary", use_container_width=True, key="save_fields"):
        errors = []
        seen_names = set()

        # Validate
        for i, row in edited_df.iterrows():
            label = str(row.get("Field Label","")).strip()
            name  = str(row.get("Column Name","")).strip()
            if not label and not name:
                continue  # blank rows are ignored
            if not label:
                errors.append(f"Row {i+1}: Field Label is required.")
            if not name:
                errors.append(f"Row {i+1}: Column Name is required.")
            elif " " in name:
                errors.append(f"Row {i+1}: Column name '{name}' cannot contain spaces.")
            elif name in seen_names:
                errors.append(f"Row {i+1}: Duplicate column name '{name}'.")
            else:
                seen_names.add(name)

        if errors:
            for e in errors:
                st.error(e)
        else:
            # Build existing field lookup by ID
            existing_by_id = {f.field_id: f for f in job.fields}

            # Clear and rebuild field list
            sj = get_studio_job()
            sj.job.fields = []

            for _, row in edited_df.iterrows():
                label = str(row.get("Field Label","")).strip()
                name  = str(row.get("Column Name","")).strip()
                if not label and not name:
                    continue

                field_id = str(row.get("_id","")).strip()
                choices  = [c.strip() for c in str(row.get("Choices","")).split(",") if c.strip()]
                dtype    = str(row.get("Type","text")).strip()
                if dtype not in FIELD_TYPES:
                    dtype = "text"

                if field_id and field_id in existing_by_id:
                    # Update existing field
                    fld = existing_by_id[field_id]
                    fld.label       = label
                    fld.name        = name
                    fld.data_type   = dtype
                    fld.required    = bool(row.get("Required", False))
                    fld.is_identifier = bool(row.get("PK", False))
                    fld.choices     = choices
                    fld.description = str(row.get("Description","")).strip()
                    fld.example     = str(row.get("Example","")).strip()
                    sj.job.fields.append(fld)
                else:
                    # New field
                    sj.job.fields.append(FieldDef(
                        name=name, label=label, data_type=dtype,
                        required=bool(row.get("Required", False)),
                        is_identifier=bool(row.get("PK", False)),
                        choices=choices,
                        description=str(row.get("Description","")).strip(),
                        example=str(row.get("Example","")).strip(),
                    ))

            set_studio_job(sj)
            st.success(f"✅ {len(sj.job.fields)} field(s) saved.")
            st.rerun()

with col_discard:
    if st.button("↩ Discard Changes", use_container_width=True, key="discard_fields"):
        st.rerun()

# Summary
if has_fields():
    st.caption(
        f"**{len(job.fields)} fields** — "
        f"{sum(1 for f in job.fields if f.required)} required · "
        f"{sum(1 for f in job.fields if f.is_identifier)} identifier(s) · "
        f"{sum(1 for f in job.fields if f.data_type == 'choice')} choice fields"
    )
