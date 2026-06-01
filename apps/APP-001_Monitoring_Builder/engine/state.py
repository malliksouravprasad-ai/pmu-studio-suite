"""Session state for APP-001 Monitoring Builder."""
import streamlit as st
from .studio_model import MonitoringStudioJob
from .monitoring_model import FieldDef, FormSection

_WS  = "mb_workspace"
_JOB = "mb_job"


def init_state():
    for k, v in {_WS: None, _JOB: MonitoringStudioJob()}.items():
        if k not in st.session_state:
            st.session_state[k] = v
    try:
        from shared.theme import apply_theme
        apply_theme()
    except Exception:
        pass


def reset_state():
    st.session_state[_WS]  = None
    st.session_state[_JOB] = MonitoringStudioJob()


def get_workspace(): return st.session_state.get(_WS)
def set_workspace(ws): st.session_state[_WS] = ws
def has_workspace(): return get_workspace() is not None

def get_studio_job(): return st.session_state.get(_JOB, MonitoringStudioJob())
def set_studio_job(sj): st.session_state[_JOB] = sj

def get_job():
    return get_studio_job().job


# ── Fields ────────────────────────────────────────────────────────────────────

def add_field(f: FieldDef):
    sj = get_studio_job(); sj.job.fields.append(f); set_studio_job(sj)

def remove_field(field_id: str):
    sj = get_studio_job()
    sj.job.fields = [f for f in sj.job.fields if f.field_id != field_id]
    # Remove from all form sections too
    for s in sj.job.form_def.sections:
        s.field_ids = [fid for fid in s.field_ids if fid != field_id]
    set_studio_job(sj)

def update_field(updated: FieldDef):
    sj = get_studio_job()
    sj.job.fields = [updated if f.field_id == updated.field_id else f for f in sj.job.fields]
    set_studio_job(sj)


# ── Form Sections ─────────────────────────────────────────────────────────────

def add_section(s: FormSection):
    sj = get_studio_job(); sj.job.form_def.sections.append(s); set_studio_job(sj)

def remove_section(section_id: str):
    sj = get_studio_job()
    sj.job.form_def.sections = [s for s in sj.job.form_def.sections if s.section_id != section_id]
    set_studio_job(sj)

def update_section_fields(section_id: str, field_ids: list):
    sj = get_studio_job()
    for s in sj.job.form_def.sections:
        if s.section_id == section_id:
            s.field_ids = field_ids
    set_studio_job(sj)


def move_field_up(field_id: str):
    sj = get_studio_job()
    fields = sj.job.fields
    idx = next((i for i, f in enumerate(fields) if f.field_id == field_id), None)
    if idx and idx > 0:
        fields[idx - 1], fields[idx] = fields[idx], fields[idx - 1]
    set_studio_job(sj)


def move_field_down(field_id: str):
    sj = get_studio_job()
    fields = sj.job.fields
    idx = next((i for i, f in enumerate(fields) if f.field_id == field_id), None)
    if idx is not None and idx < len(fields) - 1:
        fields[idx], fields[idx + 1] = fields[idx + 1], fields[idx]
    set_studio_job(sj)


def move_section_up(section_id: str):
    sj = get_studio_job()
    sections = sj.job.form_def.sections
    idx = next((i for i, s in enumerate(sections) if s.section_id == section_id), None)
    if idx and idx > 0:
        sections[idx - 1], sections[idx] = sections[idx], sections[idx - 1]
    set_studio_job(sj)


def move_section_down(section_id: str):
    sj = get_studio_job()
    sections = sj.job.form_def.sections
    idx = next((i for i, s in enumerate(sections) if s.section_id == section_id), None)
    if idx is not None and idx < len(sections) - 1:
        sections[idx], sections[idx + 1] = sections[idx + 1], sections[idx]
    set_studio_job(sj)


def load_framework_template(template: dict):
    """Replace current job fields, sections, rules, and KPIs from a template dict."""
    from .monitoring_model import FieldDef, FormSection, FormDef
    sj = get_studio_job()
    sj.job.fields = [FieldDef(**f) for f in template.get("fields", [])]
    sj.job.rule_defs = template.get("rule_defs", [])
    sj.job.kpi_defs  = template.get("kpi_defs", [])
    # Rebuild sections referencing new field_ids by position name
    fmap_by_name = {f.name: f.field_id for f in sj.job.fields}
    raw_sections = template.get("sections", [])
    new_sections = []
    for s in raw_sections:
        fids = [fmap_by_name[n] for n in s.get("field_names", []) if n in fmap_by_name]
        new_sections.append(FormSection(title=s["title"], description=s.get("description", ""), field_ids=fids))
    sj.job.form_def = FormDef(title=template.get("form_title", "Data Collection Form"),
                               description=template.get("form_description", ""),
                               sections=new_sections)
    sj.job.monitoring_name = template.get("name", sj.job.monitoring_name)
    sj.job.entity_type     = template.get("entity_type", sj.job.entity_type)
    set_studio_job(sj)


# ── Rules / KPIs / Aggs ───────────────────────────────────────────────────────

def add_rule_def(rule_dict: dict):
    sj = get_studio_job(); sj.job.rule_defs.append(rule_dict); set_studio_job(sj)

def remove_rule_def(rule_id: str):
    sj = get_studio_job()
    sj.job.rule_defs = [r for r in sj.job.rule_defs if r.get("rule_id") != rule_id]
    set_studio_job(sj)

def add_kpi_def(kpi_dict: dict):
    sj = get_studio_job(); sj.job.kpi_defs.append(kpi_dict); set_studio_job(sj)

def remove_kpi_def(kpi_id: str):
    sj = get_studio_job()
    sj.job.kpi_defs = [k for k in sj.job.kpi_defs if k.get("kpi_id") != kpi_id]
    set_studio_job(sj)


# ── Helpers ───────────────────────────────────────────────────────────────────

def has_fields(): return len(get_job().fields) > 0
def has_sections(): return len(get_job().form_def.sections) > 0

def field_map() -> dict:
    """Return {field_id: FieldDef} for quick lookup."""
    return {f.field_id: f for f in get_job().fields}

def enabled_fields():
    return [f for f in get_job().fields if f.enabled and not f.is_calculated]
