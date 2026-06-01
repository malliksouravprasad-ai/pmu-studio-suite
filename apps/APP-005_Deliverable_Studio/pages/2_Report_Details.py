"""Page 2 — Report metadata and output format selection."""
import sys
import os

_APP_DIR  = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_PMU_ROOT = os.path.dirname(os.path.dirname(_APP_DIR))
for _p in [_PMU_ROOT, _APP_DIR]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

import datetime
import streamlit as st
from engine import (
    init_state, reset_state, get_workspace, get_job, set_job, has_data,
    OUTPUT_FORMATS,
)

st.set_page_config(page_title="Report Details — Deliverable Studio", page_icon="📝", layout="wide")
init_state()

ws  = get_workspace()
job = get_job()
rc  = job.report_config

with st.sidebar:
    st.markdown("## 📄 Deliverable Studio")
    st.caption("APP-005 · OSEPA PMU Tool Suite")
    st.markdown("---")
    if ws:
        st.success(f"📁 **{ws['name']}**")
    else:
        st.warning("No workspace selected")
    if rc.report_title:
        st.info(f"**{rc.report_title}**")
    if st.button("🗑 Reset Studio", use_container_width=True):
        reset_state(); st.rerun()

st.markdown("# 📝 Report Details")
st.caption("Step 2 of 3 — Set report title, metadata, and output formats")
st.markdown("---")

with st.form("report_details_form"):
    c1, c2 = st.columns(2)
    report_title = c1.text_input("Report Title *", value=rc.report_title or "Programme Report")
    programme    = c1.text_input("Programme / Project", value=rc.programme)
    organization = c1.text_input("Organisation", value=rc.organization or "OSEPA")
    author       = c2.text_input("Prepared by", value=rc.author)
    report_date  = c2.text_input("Report Date", value=rc.report_date or datetime.date.today().strftime("%d %B %Y"))
    project_code = c2.text_input("Project Code", value=rc.project_code or (ws["project_code"] if ws else "PMU"))
    description  = st.text_area("Description / Executive Summary", value=rc.description, height=100)
    selected_formats = st.multiselect(
        "Output formats",
        list(OUTPUT_FORMATS.keys()),
        default=rc.selected_formats or ["excel"],
        format_func=lambda k: OUTPUT_FORMATS[k],
    )

    if st.form_submit_button("Save Report Details", type="primary"):
        rc.report_title     = report_title.strip()
        rc.programme        = programme.strip()
        rc.organization     = organization.strip()
        rc.author           = author.strip()
        rc.report_date      = report_date.strip()
        rc.project_code     = project_code.strip().upper() or "PMU"
        rc.description      = description.strip()
        rc.selected_formats = selected_formats or ["excel"]
        set_job(job)
        st.success("Report details saved. Proceed to **Sections**.")

st.markdown("---")
m1, m2, m3, m4 = st.columns(4)
m1.metric("Title",    rc.report_title[:20] + "…" if len(rc.report_title) > 20 else rc.report_title)
m2.metric("Org",      rc.organization or "—")
m3.metric("Date",     rc.report_date or "—")
m4.metric("Formats",  ", ".join(rc.selected_formats) if rc.selected_formats else "—")
