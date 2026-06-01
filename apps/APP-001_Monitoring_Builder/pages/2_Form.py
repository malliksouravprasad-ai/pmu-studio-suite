"""Page 2 — Form Builder: organise fields into sections."""
import sys
import os

_APP_DIR  = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_PMU_ROOT = os.path.dirname(os.path.dirname(_APP_DIR))
for _p in [_PMU_ROOT, _APP_DIR]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

import streamlit as st
from shared.theme import page_header, sidebar_brand
from engine import (
    init_state, reset_state, get_workspace, get_job, get_studio_job, set_studio_job,
    add_section, remove_section, update_section_fields, has_fields, has_sections,
    move_section_up, move_section_down,
    FormSection, field_map, enabled_fields,
)

st.set_page_config(page_title="Form — Monitoring Builder", page_icon="📝", layout="wide")
init_state()

ws  = get_workspace()
job = get_job()

with st.sidebar:
    sidebar_brand("Monitoring Builder", "APP-001")
    if ws:
        st.success(f"📁 **{ws['name']}**")
    else:
        st.warning("No workspace selected")
    st.info(f"**{len(job.form_def.sections)}** section(s)")
    if st.button("🗑 Reset Builder", use_container_width=True):
        reset_state(); st.rerun()

page_header("Form Builder", subtitle="Organise fields into sections for your data collection form", icon="📝", step=2, total_steps=5)

if not has_fields():
    st.warning("Define fields first (Step 1 — Schema)."); st.stop()

fmap    = field_map()
e_fields = enabled_fields()

# ── Form metadata quick-edit ──────────────────────────────────────────────────
with st.expander("✏ Edit Form Title & Description"):
    sj = get_studio_job()
    with st.form("form_meta"):
        title = st.text_input("Form Title", value=sj.job.form_def.title)
        desc  = st.text_area("Form Description", value=sj.job.form_def.description, height=70)
        if st.form_submit_button("Save"):
            sj.job.form_def.title       = title.strip()
            sj.job.form_def.description = desc.strip()
            set_studio_job(sj); st.success("Saved."); st.rerun()

# ── Auto-generate sections ────────────────────────────────────────────────────
if not has_sections() and has_fields():
    if st.button("⚡ Auto-generate one section with all fields"):
        add_section(FormSection(
            title="Data Collection",
            description="",
            field_ids=[f.field_id for f in e_fields],
        ))
        st.rerun()

# ── Add section ───────────────────────────────────────────────────────────────
with st.expander("➕ Add Section", expanded=not has_sections()):
    with st.form("add_section_form", clear_on_submit=True):
        s_title = st.text_input("Section Title *", placeholder="e.g. School Identification")
        s_desc  = st.text_input("Section Description (shown to respondents)", placeholder="optional")
        field_options = [f.field_id for f in e_fields]
        field_labels  = {f.field_id: f"{f.label or f.name}" for f in e_fields}
        # Fields not yet assigned to any section
        assigned = {fid for s in job.form_def.sections for fid in s.field_ids}
        unassigned = [fid for fid in field_options if fid not in assigned]
        s_fields = st.multiselect(
            "Fields in this section",
            field_options,
            default=unassigned,
            format_func=lambda fid: field_labels.get(fid, fid),
        )
        if st.form_submit_button("Add Section", type="primary"):
            if not s_title.strip():
                st.error("Section title required.")
            else:
                add_section(FormSection(title=s_title.strip(), description=s_desc.strip(), field_ids=s_fields))
                st.success(f"Section **{s_title.strip()}** added."); st.rerun()

# ── Section list ──────────────────────────────────────────────────────────────
st.markdown("### Form Sections")
if not job.form_def.sections:
    st.info("No sections yet. Add one above.")
else:
    covered_fields = set()
    n_sections = len(job.form_def.sections)
    for idx, section in enumerate(job.form_def.sections):
        with st.container(border=True):
            c1, c2, c3, c4 = st.columns([4, 1, 1, 1])
            c1.markdown(f"**{idx+1}. {section.title}**")
            if section.description:
                c1.caption(section.description)
            fields_in_section = [fmap[fid] for fid in section.field_ids if fid in fmap]
            covered_fields.update(section.field_ids)
            if fields_in_section:
                c1.caption(f"Fields ({len(fields_in_section)}): " +
                           ", ".join(f.label or f.name for f in fields_in_section))
            else:
                c1.warning("No fields assigned to this section.")

            with c2:
                if idx > 0 and st.button("↑", key=f"up_{section.section_id}", use_container_width=True, help="Move up"):
                    move_section_up(section.section_id); st.rerun()
            with c3:
                if idx < n_sections - 1 and st.button("↓", key=f"dn_{section.section_id}", use_container_width=True, help="Move down"):
                    move_section_down(section.section_id); st.rerun()
            with c4:
                if st.button("✕", key=f"rs_{section.section_id}", use_container_width=True, help="Remove"):
                    remove_section(section.section_id); st.rerun()

            # Edit field assignment
            with st.expander("Edit fields in this section"):
                current_fids = section.field_ids
                new_fids = st.multiselect(
                    "Fields",
                    [f.field_id for f in e_fields],
                    default=current_fids,
                    format_func=lambda fid: fmap[fid].label or fmap[fid].name if fid in fmap else fid,
                    key=f"ef_{section.section_id}",
                )
                if st.button("Update", key=f"upd_{section.section_id}", use_container_width=True):
                    update_section_fields(section.section_id, new_fids); st.rerun()

    # Show unassigned fields
    unassigned = [f for f in e_fields if f.field_id not in covered_fields]
    if unassigned:
        st.warning(f"**{len(unassigned)} field(s) not yet assigned to any section:** " +
                   ", ".join(f.label or f.name for f in unassigned))

# ── Form preview ──────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("### Form Preview")
st.caption(f"**{job.form_def.title}**")
if job.form_def.description:
    st.caption(job.form_def.description)
for section in job.form_def.sections:
    if not section.enabled:
        continue
    st.markdown(f"**── {section.title} ──**")
    for fid in section.field_ids:
        fld = fmap.get(fid)
        if fld:
            req = "\\*" if fld.required else ""
            type_hint = f" ({', '.join(fld.choices[:3])}{'…' if len(fld.choices) > 3 else ''})" if fld.choices else ""
            st.markdown(f"  • {fld.label or fld.name}{req}{type_hint}")
