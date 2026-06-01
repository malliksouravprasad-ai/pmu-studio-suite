"""
Enterprise UI theme for PMU Tool Suite.
Call apply_theme() once per page (inside init_state works best).
"""
import streamlit as st

# ── Colour tokens ─────────────────────────────────────────────────────────────
NAVY        = "#0F172A"
NAVY_LIGHT  = "#1E293B"
SLATE       = "#334155"
EMERALD     = "#059669"
EMERALD_DK  = "#047857"
EMERALD_LT  = "#D1FAE5"
AMBER       = "#D97706"
AMBER_LT    = "#FEF3C7"
CRIMSON     = "#DC2626"
CRIMSON_LT  = "#FEE2E2"
SKY         = "#0EA5E9"
SKY_LT      = "#E0F2FE"
BG          = "#F8FAFC"
CARD        = "#FFFFFF"
BORDER      = "#E2E8F0"
TEXT_PRI    = "#0F172A"
TEXT_SEC    = "#64748B"
TEXT_MUTED  = "#94A3B8"

_CSS = """
<style>
/* ── Google Font import ───────────────────────────────────────────────────── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

/* ── Global tokens ────────────────────────────────────────────────────────── */
:root {
  --navy:        #0F172A;
  --navy-light:  #1E293B;
  --slate:       #334155;
  --emerald:     #059669;
  --emerald-dk:  #047857;
  --emerald-lt:  #D1FAE5;
  --amber:       #D97706;
  --amber-lt:    #FEF3C7;
  --crimson:     #DC2626;
  --crimson-lt:  #FEE2E2;
  --sky:         #0EA5E9;
  --sky-lt:      #E0F2FE;
  --bg:          #F8FAFC;
  --card:        #FFFFFF;
  --border:      #E2E8F0;
  --text-pri:    #0F172A;
  --text-sec:    #64748B;
  --text-muted:  #94A3B8;
  --shadow-sm:   0 1px 3px rgba(15,23,42,0.07), 0 1px 2px rgba(15,23,42,0.04);
  --shadow-md:   0 4px 8px rgba(15,23,42,0.08), 0 2px 4px rgba(15,23,42,0.05);
  --shadow-lg:   0 12px 24px rgba(15,23,42,0.10), 0 4px 8px rgba(15,23,42,0.06);
  --radius:      10px;
  --radius-sm:   6px;
  --radius-lg:   16px;
  --transition:  0.18s cubic-bezier(0.4, 0, 0.2, 1);
}

/* ── Base typography & background ─────────────────────────────────────────── */
html, body, [class*="css"] {
    font-family: 'Inter', 'Segoe UI', system-ui, -apple-system, sans-serif !important;
}

.main {
    background-color: var(--bg) !important;
}

.main .block-container {
    padding: 1.75rem 2.25rem 3rem !important;
    max-width: 1380px !important;
}

/* ── Top header bar ───────────────────────────────────────────────────────── */
[data-testid="stHeader"] {
    background: var(--card) !important;
    border-bottom: 1px solid var(--border) !important;
    box-shadow: var(--shadow-sm) !important;
}

/* ── Sidebar ──────────────────────────────────────────────────────────────── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0F172A 0%, #1A2744 60%, #1E293B 100%) !important;
    border-right: 1px solid rgba(255,255,255,0.06) !important;
}

[data-testid="stSidebarContent"] {
    padding-top: 1rem !important;
}

/* All sidebar text → light */
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] div,
[data-testid="stSidebar"] .stMarkdown {
    color: #CBD5E1 !important;
}

[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3,
[data-testid="stSidebar"] strong {
    color: #F1F5F9 !important;
}

/* Sidebar markdown heading */
[data-testid="stSidebar"] .stMarkdown h2 {
    font-size: 1rem !important;
    font-weight: 700 !important;
    letter-spacing: 0.01em !important;
    color: #F8FAFC !important;
    margin-bottom: 0.15rem !important;
}

[data-testid="stSidebar"] .stMarkdown p {
    font-size: 0.72rem !important;
    color: #94A3B8 !important;
}

/* Sidebar horizontal rule */
[data-testid="stSidebar"] hr {
    border-color: rgba(255,255,255,0.10) !important;
    margin: 0.75rem 0 !important;
}

/* Sidebar success / info / warning banners */
[data-testid="stSidebar"] [data-testid="stNotification"],
[data-testid="stSidebar"] .stAlert {
    border-radius: var(--radius-sm) !important;
}

[data-testid="stSidebar"] [data-testid="stNotification"][data-type="success"] {
    background: rgba(5,150,105,0.18) !important;
    border: 1px solid rgba(5,150,105,0.35) !important;
    color: #6EE7B7 !important;
}

[data-testid="stSidebar"] [data-testid="stNotification"][data-type="info"] {
    background: rgba(14,165,233,0.15) !important;
    border: 1px solid rgba(14,165,233,0.30) !important;
    color: #7DD3FC !important;
}

[data-testid="stSidebar"] [data-testid="stNotification"][data-type="warning"] {
    background: rgba(217,119,6,0.18) !important;
    border: 1px solid rgba(217,119,6,0.35) !important;
    color: #FCD34D !important;
}

/* Sidebar buttons */
[data-testid="stSidebar"] .stButton > button {
    background: rgba(255,255,255,0.06) !important;
    border: 1px solid rgba(255,255,255,0.14) !important;
    color: #CBD5E1 !important;
    border-radius: 8px !important;
    font-size: 0.82rem !important;
    font-weight: 500 !important;
    letter-spacing: 0.01em !important;
    transition: all var(--transition) !important;
    width: 100% !important;
}

[data-testid="stSidebar"] .stButton > button:hover {
    background: rgba(5,150,105,0.22) !important;
    border-color: rgba(5,150,105,0.50) !important;
    color: #6EE7B7 !important;
    transform: none !important;
}

/* Nav items in sidebar */
[data-testid="stSidebarNavItems"] {
    padding-top: 0.5rem !important;
}

[data-testid="stSidebarNavLink"] {
    border-radius: 8px !important;
    margin: 1px 4px !important;
    padding: 0.55rem 1rem !important;
    color: #94A3B8 !important;
    font-size: 0.84rem !important;
    font-weight: 500 !important;
    transition: all var(--transition) !important;
}

[data-testid="stSidebarNavLink"]:hover {
    background: rgba(255,255,255,0.08) !important;
    color: #E2E8F0 !important;
}

[data-testid="stSidebarNavLink"][aria-selected="true"],
[data-testid="stSidebarNavLink"][data-active="true"] {
    background: linear-gradient(90deg, rgba(5,150,105,0.28), rgba(5,150,105,0.12)) !important;
    color: #6EE7B7 !important;
    border-left: 3px solid #059669 !important;
    font-weight: 600 !important;
}

/* ── Headings in main content ─────────────────────────────────────────────── */
.main h1 {
    font-size: 1.75rem !important;
    font-weight: 800 !important;
    color: var(--navy) !important;
    letter-spacing: -0.02em !important;
    margin-bottom: 0.25rem !important;
    line-height: 1.2 !important;
}

.main h2 {
    font-size: 1.25rem !important;
    font-weight: 700 !important;
    color: var(--navy) !important;
    letter-spacing: -0.01em !important;
}

.main h3 {
    font-size: 1.05rem !important;
    font-weight: 600 !important;
    color: var(--slate) !important;
}

.main hr {
    border-color: var(--border) !important;
    margin: 1rem 0 !important;
}

/* Caption / muted text */
.main .stCaption,
.main [data-testid="stCaptionContainer"] p,
.main small {
    color: var(--text-sec) !important;
    font-size: 0.78rem !important;
}

/* ── Metrics ──────────────────────────────────────────────────────────────── */
[data-testid="metric-container"] {
    background: var(--card) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius) !important;
    padding: 1.1rem 1.4rem !important;
    box-shadow: var(--shadow-sm) !important;
    transition: box-shadow var(--transition) !important;
}

[data-testid="metric-container"]:hover {
    box-shadow: var(--shadow-md) !important;
}

[data-testid="stMetricLabel"] > div,
[data-testid="stMetricLabel"] p {
    font-size: 0.7rem !important;
    font-weight: 700 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.09em !important;
    color: var(--text-sec) !important;
}

[data-testid="stMetricValue"] > div {
    font-size: 1.85rem !important;
    font-weight: 800 !important;
    color: var(--navy) !important;
    letter-spacing: -0.02em !important;
}

[data-testid="stMetricDelta"] {
    font-size: 0.75rem !important;
    font-weight: 600 !important;
}

/* ── Buttons ──────────────────────────────────────────────────────────────── */
.stButton > button {
    border-radius: 8px !important;
    font-family: 'Inter', system-ui, sans-serif !important;
    font-weight: 500 !important;
    font-size: 0.84rem !important;
    letter-spacing: 0.01em !important;
    transition: all var(--transition) !important;
    border: 1px solid var(--border) !important;
    color: var(--text-pri) !important;
    background: var(--card) !important;
    box-shadow: var(--shadow-sm) !important;
    padding: 0.45rem 1.1rem !important;
}

.stButton > button:hover {
    border-color: #94A3B8 !important;
    box-shadow: var(--shadow-md) !important;
    transform: translateY(-1px) !important;
}

.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, var(--emerald) 0%, var(--emerald-dk) 100%) !important;
    color: #FFFFFF !important;
    border: none !important;
    box-shadow: 0 2px 8px rgba(5,150,105,0.30) !important;
    font-weight: 600 !important;
}

.stButton > button[kind="primary"]:hover {
    box-shadow: 0 4px 16px rgba(5,150,105,0.40) !important;
    transform: translateY(-1px) !important;
    background: linear-gradient(135deg, #0CA678 0%, var(--emerald) 100%) !important;
}

.stButton > button[kind="primary"]:active {
    transform: translateY(0) !important;
    box-shadow: 0 2px 6px rgba(5,150,105,0.30) !important;
}

/* Danger / destructive buttons (contain "Delete", "Remove", "Reset") */
.stButton > button[kind="secondary"]:hover {
    color: var(--text-pri) !important;
}

/* ── Form inputs ──────────────────────────────────────────────────────────── */
[data-testid="stTextInput"] input,
[data-testid="stNumberInput"] input,
[data-testid="stTextArea"] textarea {
    border-radius: var(--radius-sm) !important;
    border: 1px solid var(--border) !important;
    background: var(--card) !important;
    color: var(--text-pri) !important;
    font-family: 'Inter', system-ui, sans-serif !important;
    font-size: 0.875rem !important;
    transition: border-color var(--transition), box-shadow var(--transition) !important;
}

[data-testid="stTextInput"] input:focus,
[data-testid="stNumberInput"] input:focus,
[data-testid="stTextArea"] textarea:focus {
    border-color: var(--emerald) !important;
    box-shadow: 0 0 0 3px rgba(5,150,105,0.12) !important;
    outline: none !important;
}

[data-testid="stTextInput"] label,
[data-testid="stNumberInput"] label,
[data-testid="stTextArea"] label,
[data-testid="stSelectbox"] label,
[data-testid="stMultiSelect"] label,
[data-testid="stRadio"] label,
[data-testid="stCheckbox"] label,
[data-testid="stSlider"] label,
[data-testid="stFileUploader"] label,
[data-testid="stDateInput"] label {
    font-size: 0.80rem !important;
    font-weight: 600 !important;
    color: var(--slate) !important;
    letter-spacing: 0.01em !important;
}

/* Selectbox */
[data-testid="stSelectbox"] > div > div {
    border-radius: var(--radius-sm) !important;
    border: 1px solid var(--border) !important;
    background: var(--card) !important;
    font-size: 0.875rem !important;
}

[data-testid="stSelectbox"] > div > div:focus-within {
    border-color: var(--emerald) !important;
    box-shadow: 0 0 0 3px rgba(5,150,105,0.12) !important;
}

/* ── File uploader ────────────────────────────────────────────────────────── */
[data-testid="stFileUploaderDropzone"] {
    border: 2px dashed var(--border) !important;
    border-radius: var(--radius) !important;
    background: #FAFBFD !important;
    transition: all var(--transition) !important;
}

[data-testid="stFileUploaderDropzone"]:hover {
    border-color: var(--emerald) !important;
    background: rgba(5,150,105,0.03) !important;
}

/* ── Tabs ─────────────────────────────────────────────────────────────────── */
.stTabs [data-baseweb="tab-list"] {
    background: #F1F5F9 !important;
    border-radius: 10px !important;
    padding: 4px !important;
    gap: 2px !important;
    border: 1px solid var(--border) !important;
}

.stTabs [data-baseweb="tab"] {
    border-radius: 8px !important;
    font-size: 0.83rem !important;
    font-weight: 500 !important;
    color: var(--text-sec) !important;
    background: transparent !important;
    padding: 0.5rem 1rem !important;
    transition: all var(--transition) !important;
    border: none !important;
}

.stTabs [data-baseweb="tab"]:hover {
    color: var(--navy) !important;
    background: rgba(255,255,255,0.6) !important;
}

.stTabs [data-baseweb="tab"][aria-selected="true"] {
    background: var(--card) !important;
    color: var(--navy) !important;
    font-weight: 600 !important;
    box-shadow: 0 1px 4px rgba(15,23,42,0.10), 0 1px 2px rgba(15,23,42,0.06) !important;
}

.stTabs [data-baseweb="tab-highlight"] {
    display: none !important;
}

.stTabs [data-baseweb="tab-border"] {
    display: none !important;
}

/* ── Expanders ────────────────────────────────────────────────────────────── */
[data-testid="stExpander"] {
    border: 1px solid var(--border) !important;
    border-radius: var(--radius) !important;
    background: var(--card) !important;
    box-shadow: var(--shadow-sm) !important;
    overflow: hidden !important;
    margin-bottom: 0.5rem !important;
}

[data-testid="stExpander"] summary {
    padding: 0.85rem 1.1rem !important;
    font-weight: 600 !important;
    color: var(--navy) !important;
    font-size: 0.875rem !important;
    background: var(--card) !important;
    border-radius: var(--radius) !important;
    transition: background var(--transition) !important;
}

[data-testid="stExpander"] summary:hover {
    background: #F8FAFC !important;
}

[data-testid="stExpander"][open] summary {
    border-bottom: 1px solid var(--border) !important;
    border-radius: var(--radius) var(--radius) 0 0 !important;
}

/* ── Alert banners ────────────────────────────────────────────────────────── */
[data-testid="stNotification"] {
    border-radius: var(--radius-sm) !important;
    border-width: 1px !important;
    border-style: solid !important;
    font-size: 0.875rem !important;
    font-weight: 450 !important;
}

[data-testid="stNotification"][data-type="success"] {
    background: #F0FDF9 !important;
    border-color: #A7F3D0 !important;
    color: #064E3B !important;
}

[data-testid="stNotification"][data-type="info"] {
    background: #F0F9FF !important;
    border-color: #BAE6FD !important;
    color: #0C4A6E !important;
}

[data-testid="stNotification"][data-type="warning"] {
    background: #FFFBEB !important;
    border-color: #FDE68A !important;
    color: #78350F !important;
}

[data-testid="stNotification"][data-type="error"] {
    background: #FEF2F2 !important;
    border-color: #FECACA !important;
    color: #7F1D1D !important;
}

/* ── Containers with border ───────────────────────────────────────────────── */
[data-testid="stVerticalBlockBorderWrapper"] {
    border: 1px solid var(--border) !important;
    border-radius: var(--radius) !important;
    background: var(--card) !important;
    box-shadow: var(--shadow-sm) !important;
    padding: 0.75rem 1rem !important;
    transition: box-shadow var(--transition) !important;
}

[data-testid="stVerticalBlockBorderWrapper"]:hover {
    box-shadow: var(--shadow-md) !important;
}

/* ── Data editor ──────────────────────────────────────────────────────────── */
[data-testid="stDataEditor"] {
    border: 1px solid var(--border) !important;
    border-radius: var(--radius) !important;
    overflow: hidden !important;
    box-shadow: var(--shadow-sm) !important;
}

/* ── DataFrames ───────────────────────────────────────────────────────────── */
[data-testid="stDataFrame"] {
    border: 1px solid var(--border) !important;
    border-radius: var(--radius) !important;
    overflow: hidden !important;
    box-shadow: var(--shadow-sm) !important;
}

/* ── Form containers ──────────────────────────────────────────────────────── */
[data-testid="stForm"] {
    border: 1px solid var(--border) !important;
    border-radius: var(--radius) !important;
    background: var(--card) !important;
    padding: 1.25rem !important;
    box-shadow: var(--shadow-sm) !important;
}

/* ── Progress bar ─────────────────────────────────────────────────────────── */
[data-testid="stProgressBar"] > div {
    background: linear-gradient(90deg, var(--emerald) 0%, #34D399 100%) !important;
    border-radius: 999px !important;
}

[data-testid="stProgressBar"] {
    background: #E2E8F0 !important;
    border-radius: 999px !important;
    height: 8px !important;
}

/* ── Toggle ───────────────────────────────────────────────────────────────── */
[data-testid="stToggle"] input:checked + div {
    background: var(--emerald) !important;
}

/* ── Spinner ──────────────────────────────────────────────────────────────── */
[data-testid="stSpinner"] {
    color: var(--emerald) !important;
}

/* ── Radio buttons ────────────────────────────────────────────────────────── */
[data-testid="stRadio"] [role="radiogroup"] {
    gap: 0.5rem !important;
}

/* ── Checkbox ─────────────────────────────────────────────────────────────── */
[data-testid="stCheckbox"] input:checked + div {
    background: var(--emerald) !important;
    border-color: var(--emerald) !important;
}

/* ── Scrollbar ────────────────────────────────────────────────────────────── */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: #CBD5E1; border-radius: 999px; }
::-webkit-scrollbar-thumb:hover { background: #94A3B8; }

/* ── Custom PMU components ────────────────────────────────────────────────── */

/* Page header banner */
.pmu-page-header {
    background: linear-gradient(135deg, var(--navy) 0%, #1E3A5F 50%, #0C2340 100%);
    border-radius: var(--radius-lg);
    padding: 1.5rem 2rem;
    margin-bottom: 1.5rem;
    box-shadow: var(--shadow-lg);
    position: relative;
    overflow: hidden;
}

.pmu-page-header::before {
    content: '';
    position: absolute;
    top: -30px; right: -30px;
    width: 200px; height: 200px;
    background: radial-gradient(circle, rgba(5,150,105,0.15) 0%, transparent 70%);
    border-radius: 50%;
}

.pmu-page-header::after {
    content: '';
    position: absolute;
    bottom: -20px; left: 20%;
    width: 150px; height: 150px;
    background: radial-gradient(circle, rgba(14,165,233,0.08) 0%, transparent 70%);
    border-radius: 50%;
}

.pmu-page-header-inner {
    display: flex;
    align-items: center;
    gap: 1.25rem;
    position: relative;
    z-index: 1;
}

.pmu-page-icon {
    font-size: 2.2rem;
    line-height: 1;
    filter: drop-shadow(0 2px 4px rgba(0,0,0,0.3));
}

.pmu-page-title {
    font-size: 1.65rem !important;
    font-weight: 800 !important;
    color: #F8FAFC !important;
    letter-spacing: -0.02em !important;
    margin: 0 !important;
    line-height: 1.1 !important;
}

.pmu-page-subtitle {
    font-size: 0.82rem !important;
    color: #94A3B8 !important;
    margin: 0.2rem 0 0 !important;
    font-weight: 400 !important;
    letter-spacing: 0.01em !important;
}

.pmu-step-badge {
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    background: rgba(5,150,105,0.2);
    border: 1px solid rgba(5,150,105,0.35);
    color: #6EE7B7;
    border-radius: 999px;
    padding: 0.25rem 0.75rem;
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    margin-top: 0.5rem;
}

/* KPI cards */
.pmu-kpi-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
    gap: 1rem;
    margin: 1rem 0;
}

.pmu-kpi-card {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1.25rem 1.5rem;
    box-shadow: var(--shadow-sm);
    transition: box-shadow var(--transition), transform var(--transition);
    position: relative;
    overflow: hidden;
}

.pmu-kpi-card:hover {
    box-shadow: var(--shadow-md);
    transform: translateY(-2px);
}

.pmu-kpi-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    background: linear-gradient(90deg, var(--emerald), #34D399);
    border-radius: var(--radius) var(--radius) 0 0;
}

.pmu-kpi-label {
    font-size: 0.70rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: var(--text-sec);
    margin-bottom: 0.5rem;
}

.pmu-kpi-value {
    font-size: 2rem;
    font-weight: 800;
    color: var(--navy);
    letter-spacing: -0.03em;
    line-height: 1;
}

.pmu-kpi-delta {
    font-size: 0.73rem;
    font-weight: 600;
    margin-top: 0.35rem;
    color: var(--text-muted);
}

.pmu-kpi-card.status-green::before  { background: linear-gradient(90deg, var(--emerald), #34D399); }
.pmu-kpi-card.status-amber::before  { background: linear-gradient(90deg, var(--amber), #FBBF24); }
.pmu-kpi-card.status-red::before    { background: linear-gradient(90deg, var(--crimson), #F87171); }
.pmu-kpi-card.status-blue::before   { background: linear-gradient(90deg, var(--sky), #38BDF8); }
.pmu-kpi-card.status-slate::before  { background: linear-gradient(90deg, var(--slate), #64748B); }

/* Section cards */
.pmu-section-card {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1.5rem;
    margin-bottom: 1rem;
    box-shadow: var(--shadow-sm);
}

.pmu-section-title {
    font-size: 0.85rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.07em;
    color: var(--text-sec);
    padding-bottom: 0.75rem;
    border-bottom: 1px solid var(--border);
    margin-bottom: 1rem;
}

/* Status badges */
.pmu-badge {
    display: inline-flex;
    align-items: center;
    gap: 0.3rem;
    border-radius: 999px;
    padding: 0.2rem 0.65rem;
    font-size: 0.70rem;
    font-weight: 700;
    letter-spacing: 0.04em;
    text-transform: uppercase;
}

.pmu-badge-green  { background: var(--emerald-lt); color: #065F46; }
.pmu-badge-amber  { background: var(--amber-lt);   color: #92400E; }
.pmu-badge-red    { background: var(--crimson-lt);  color: #991B1B; }
.pmu-badge-blue   { background: var(--sky-lt);     color: #075985; }
.pmu-badge-slate  { background: #F1F5F9;           color: #475569; }

/* Step progress bar */
.pmu-step-bar {
    display: flex;
    align-items: center;
    gap: 0;
    margin: 1rem 0 1.5rem;
    position: relative;
}

.pmu-step-bar-track {
    position: absolute;
    top: 50%;
    left: 0; right: 0;
    height: 2px;
    background: var(--border);
    transform: translateY(-50%);
    z-index: 0;
}

.pmu-step-bar-fill {
    position: absolute;
    top: 50%;
    left: 0;
    height: 2px;
    background: linear-gradient(90deg, var(--emerald), #34D399);
    transform: translateY(-50%);
    z-index: 1;
    transition: width 0.4s ease;
}

.pmu-step {
    display: flex;
    flex-direction: column;
    align-items: center;
    position: relative;
    z-index: 2;
    flex: 1;
}

.pmu-step-dot {
    width: 28px; height: 28px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.70rem;
    font-weight: 700;
    border: 2px solid var(--border);
    background: var(--card);
    color: var(--text-muted);
    transition: all var(--transition);
}

.pmu-step-dot.done {
    background: var(--emerald);
    border-color: var(--emerald);
    color: white;
}

.pmu-step-dot.active {
    background: var(--navy);
    border-color: var(--navy);
    color: white;
    box-shadow: 0 0 0 4px rgba(15,23,42,0.15);
}

.pmu-step-label {
    font-size: 0.66rem;
    font-weight: 600;
    color: var(--text-muted);
    margin-top: 0.35rem;
    white-space: nowrap;
    letter-spacing: 0.03em;
    text-transform: uppercase;
}

.pmu-step-label.active {
    color: var(--navy);
    font-weight: 700;
}

.pmu-step-label.done {
    color: var(--emerald);
}

/* Workspace card */
.pmu-workspace-card {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1rem 1.25rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
    box-shadow: var(--shadow-sm);
    transition: all var(--transition);
    margin-bottom: 0.5rem;
}

.pmu-workspace-card:hover {
    border-color: #CBD5E1;
    box-shadow: var(--shadow-md);
    transform: translateY(-1px);
}

.pmu-workspace-card.active {
    border-color: var(--emerald);
    background: #F0FDF9;
    box-shadow: 0 0 0 3px rgba(5,150,105,0.10);
}

/* Toolbar strip */
.pmu-toolbar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0.65rem 1rem;
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: var(--radius-sm);
    margin-bottom: 1rem;
    box-shadow: var(--shadow-sm);
}

/* App branding sidebar header */
.pmu-sidebar-brand {
    display: flex;
    flex-direction: column;
    padding: 0.5rem 0 0.75rem;
    border-bottom: 1px solid rgba(255,255,255,0.08);
    margin-bottom: 0.75rem;
}

.pmu-sidebar-app-name {
    font-size: 1rem !important;
    font-weight: 800 !important;
    color: #F8FAFC !important;
    letter-spacing: -0.01em !important;
    line-height: 1.2 !important;
}

.pmu-sidebar-app-id {
    font-size: 0.68rem !important;
    font-weight: 600 !important;
    color: #059669 !important;
    letter-spacing: 0.08em !important;
    text-transform: uppercase !important;
    margin-top: 0.1rem !important;
}

.pmu-sidebar-app-suite {
    font-size: 0.65rem !important;
    color: #475569 !important;
    margin-top: 0.05rem !important;
    letter-spacing: 0.03em !important;
}

/* Divider with label */
.pmu-divider {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    margin: 1.25rem 0;
    color: var(--text-muted);
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.06em;
    text-transform: uppercase;
}

.pmu-divider::before,
.pmu-divider::after {
    content: '';
    flex: 1;
    height: 1px;
    background: var(--border);
}

/* Empty state */
.pmu-empty {
    text-align: center;
    padding: 3rem 2rem;
    color: var(--text-sec);
}

.pmu-empty-icon { font-size: 3rem; margin-bottom: 0.75rem; }
.pmu-empty-title {
    font-size: 1.1rem;
    font-weight: 700;
    color: var(--navy);
    margin-bottom: 0.4rem;
}
.pmu-empty-body { font-size: 0.875rem; color: var(--text-sec); }

/* ── Loading skeleton pulse ───────────────────────────────────────────────── */
@keyframes skeleton-pulse {
  0%, 100% { opacity: 1; }
  50%       { opacity: 0.5; }
}

.pmu-skeleton {
    background: #E2E8F0;
    border-radius: 4px;
    animation: skeleton-pulse 1.8s ease-in-out infinite;
}

/* ── Responsive tweaks ────────────────────────────────────────────────────── */
@media (max-width: 768px) {
    .main .block-container { padding: 1rem 1rem 2rem !important; }
    .pmu-page-header       { padding: 1rem 1.25rem; }
    .pmu-page-title        { font-size: 1.3rem !important; }
}

</style>
"""


def apply_theme() -> None:
    """Inject enterprise CSS into the current page. Call once per page."""
    st.markdown(_CSS, unsafe_allow_html=True)


# ── Reusable HTML components ──────────────────────────────────────────────────

def page_header(
    title: str,
    subtitle: str = "",
    icon: str = "",
    step: int = 0,
    total_steps: int = 0,
    step_label: str = "",
) -> None:
    """Render a branded page header banner."""
    icon_html = f'<div class="pmu-page-icon">{icon}</div>' if icon else ""
    sub_html  = f'<p class="pmu-page-subtitle">{subtitle}</p>' if subtitle else ""
    step_html = ""
    if step and total_steps:
        lbl = step_label or f"Step {step} of {total_steps}"
        step_html = f'<div class="pmu-step-badge">&#9654; {lbl}</div>'
    st.markdown(f"""
    <div class="pmu-page-header">
        <div class="pmu-page-header-inner">
            {icon_html}
            <div>
                <h1 class="pmu-page-title">{title}</h1>
                {sub_html}
                {step_html}
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def sidebar_brand(app_name: str, app_id: str) -> None:
    """Render the branded sidebar header (call inside `with st.sidebar:`)."""
    st.markdown(f"""
    <div class="pmu-sidebar-brand">
        <div class="pmu-sidebar-app-name">{app_name}</div>
        <div class="pmu-sidebar-app-id">{app_id}</div>
        <div class="pmu-sidebar-app-suite">OSEPA PMU Tool Suite</div>
    </div>
    """, unsafe_allow_html=True)


def kpi_card(
    label: str,
    value: str,
    delta: str = "",
    status: str = "green",   # green | amber | red | blue | slate
    icon: str = "",
) -> str:
    """Return HTML for a KPI card (use inside st.markdown(..., unsafe_allow_html=True))."""
    icon_html  = f'<span style="font-size:1.4rem;margin-bottom:0.5rem;display:block">{icon}</span>' if icon else ""
    delta_html = f'<div class="pmu-kpi-delta">{delta}</div>' if delta else ""
    return f"""
    <div class="pmu-kpi-card status-{status}">
        {icon_html}
        <div class="pmu-kpi-label">{label}</div>
        <div class="pmu-kpi-value">{value}</div>
        {delta_html}
    </div>"""


def kpi_row(cards: list[dict]) -> None:
    """Render a grid of KPI cards. Each dict: {label, value, delta?, status?, icon?}"""
    inner = "".join(kpi_card(**c) for c in cards)
    st.markdown(f'<div class="pmu-kpi-grid">{inner}</div>', unsafe_allow_html=True)


def section_header(title: str) -> None:
    """Render a subtle section divider with label."""
    st.markdown(f"""
    <div class="pmu-divider">{title}</div>
    """, unsafe_allow_html=True)


def badge(text: str, color: str = "slate") -> str:
    """Return a status badge HTML span. color: green|amber|red|blue|slate"""
    return f'<span class="pmu-badge pmu-badge-{color}">{text}</span>'


def empty_state(icon: str, title: str, body: str) -> None:
    """Render an empty-state panel."""
    st.markdown(f"""
    <div class="pmu-empty">
        <div class="pmu-empty-icon">{icon}</div>
        <div class="pmu-empty-title">{title}</div>
        <div class="pmu-empty-body">{body}</div>
    </div>
    """, unsafe_allow_html=True)


def step_progress(steps: list[str], current: int) -> None:
    """
    Render a step progress bar.
    steps  = list of step label strings
    current = 1-based index of active step
    """
    n = len(steps)
    if n == 0:
        return
    pct = ((current - 1) / max(n - 1, 1)) * 100

    dots = ""
    for i, lbl in enumerate(steps, start=1):
        if i < current:
            cls = "done"; dot_inner = "✓"
        elif i == current:
            cls = "active"; dot_inner = str(i)
        else:
            cls = ""; dot_inner = str(i)
        dots += f"""
        <div class="pmu-step">
            <div class="pmu-step-dot {cls}">{dot_inner}</div>
            <div class="pmu-step-label {cls}">{lbl}</div>
        </div>"""

    st.markdown(f"""
    <div class="pmu-step-bar">
        <div class="pmu-step-bar-track"></div>
        <div class="pmu-step-bar-fill" style="width:{pct}%"></div>
        {dots}
    </div>
    """, unsafe_allow_html=True)
