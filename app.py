"""SpendStory — AI-assisted student finance dashboard.

Refined visual direction: Soft neutral canvas, crisp white surfaces, Manrope typography,
restrained mint and lime accents, charcoal contrast, and exact reference illustrated cursor.
"""

from __future__ import annotations

from datetime import date, datetime
import html
import json
import os
from pathlib import Path

import pandas as pd
import streamlit as st

from src.analytics import (
    calculate_budget_comparisons,
    calculate_cumulative_trend,
    calculate_monthly_summary,
    calculate_multi_month_comparison,
    export_transactions_to_csv,
    format_inr,
)
from src.categorizer import DEFAULT_CONFIDENCE_THRESHOLD, get_default_categorizer
from src.cursor_assets import (
    ARROW_DATA_URI,
    HAND_DATA_URI,
    get_cursor_css,
    get_cursor_follower_html,
)
from src.dashboard_charts import render_donut, render_monthly, render_trend
from src.storage import Database, ImportResult
from src.transactions import (
    ALLOWED_EXPENSE_CATEGORIES,
    Transaction,
    compute_fingerprint,
    parse_amount_to_paise,
    parse_transactions_csv,
)


# -----------------------------------------------------------------------------
# Configuration & Theme Setup
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="SpendStory — Student Finance Dashboard",
    page_icon="💳",
    layout="wide",
    initial_sidebar_state="auto",
)

# Custom Scoped CSS matching the refined visual design brief:
# Neutral #F4F4F6 canvas, white #FFFFFF rounded cards, subtle #E3E4E8 borders,
# Manrope typography, charcoal #202126 controls, and restrained mint #78A98E accents.
SPENDSTORY_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&display=swap');

/* Root styling and Neutral Canvas backdrop */
.stApp {
    background: #F4F4F6 !important;
    font-family: 'Manrope', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
    color: #191A1F;
}

/* Zero out height for the invisible cursor follower component */
iframe[height="0"], [data-testid="stCustomComponentV1"]:has(iframe[height="0"]) {
    display: none !important;
    height: 0 !important;
    margin: 0 !important;
    padding: 0 !important;
}

/* Sidebar styling: Clean white surface with subtle neutral border */
[data-testid="stSidebar"] {
    background-color: #FFFFFF !important;
    border-right: 1px solid #E3E4E8 !important;
    padding-top: 0 !important;
}

[data-testid="stSidebar"] .block-container {
    background-color: transparent !important;
    border: none !important;
    box-shadow: none !important;
    padding: 16px 14px !important;
    margin-top: 0 !important;
}

/* SpendStory brand header in sidebar */
.spendstory-logo {
    display: flex;
    align-items: center;
    gap: 10px;
    height: 52px;
    font-size: 18px;
    font-weight: 800;
    color: #191A1F;
    letter-spacing: -0.4px;
    border-bottom: 1px solid #E3E4E8;
    margin-bottom: 10px;
    padding-left: 2px;
}

.spendstory-logo .logo-dot {
    width: 9px;
    height: 9px;
    border-radius: 50%;
    background-color: #78A98E;
    display: inline-block;
    box-shadow: 0 0 0 3px #CFE4D8;
}

/* Sidebar Navigation Items */
[data-testid="stSidebar"] .stRadio [role="radiogroup"] {
    gap: 4px !important;
}

[data-testid="stSidebar"] .stRadio label {
    font-size: 13px !important;
    font-weight: 500 !important;
    color: #747781 !important;
    padding: 9px 12px !important;
    border-radius: 8px !important;
    width: 100%;
    transition: all 0.15s ease !important;
}

[data-testid="stSidebar"] .stRadio label:hover {
    background-color: #F4F4F6 !important;
    color: #191A1F !important;
}

[data-testid="stSidebar"] .stRadio label:has(input:checked) {
    background: #ECEEF1 !important;
    color: #202126 !important;
    font-weight: 600 !important;
}

[data-testid="stSidebar"] .stRadio label:focus-within {
    outline: 2px solid #202126;
    outline-offset: 2px;
}

[data-testid="stRadioOption"] > div > div:first-child {
    display: none;
}

[data-testid="stSidebar"] .stRadio label p {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 13px;
    white-space: nowrap;
    margin: 0;
}

[data-testid="stSidebar"] .stRadio label p::before {
    content: '';
    flex: 0 0 16px;
    height: 16px;
    background: currentColor;
    mask: var(--nav-icon) center / contain no-repeat;
    -webkit-mask: var(--nav-icon) center / contain no-repeat;
}

[data-testid="stSidebar"] .stRadio [role="radiogroup"] > :nth-child(1) {
    --nav-icon: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='black' stroke-width='1.8'%3E%3Ccircle cx='12' cy='12' r='9'/%3E%3Cpath d='m12 12 4-4M7 15a6 6 0 0 1 6-9m4 4a6 6 0 0 1 0 5'/%3E%3C/svg%3E");
}
[data-testid="stSidebar"] .stRadio [role="radiogroup"] > :nth-child(2) {
    --nav-icon: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='black' stroke-width='1.8'%3E%3Crect x='3' y='5' width='18' height='14' rx='2'/%3E%3Cpath d='M3 9h18m-14 5h4'/%3E%3C/svg%3E");
}
[data-testid="stSidebar"] .stRadio [role="radiogroup"] > :nth-child(3) {
    --nav-icon: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='black' stroke-width='1.8'%3E%3Cpath d='M4 8h16v12H4zM7 8V4h10v4M9 13h6m-6 3h4'/%3E%3C/svg%3E");
}
[data-testid="stSidebar"] .stRadio [role="radiogroup"] > :nth-child(4) {
    --nav-icon: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='black' stroke-width='1.8'%3E%3Cpath d='M3 5h9l9 9-7 7-9-9z'/%3E%3Ccircle cx='8' cy='9' r='1'/%3E%3C/svg%3E");
}
[data-testid="stSidebar"] .stRadio [role="radiogroup"] > :nth-child(5) {
    --nav-icon: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='black' stroke-width='1.8'%3E%3Cpath d='M4 4v16h16M8 16v-4m5 4V8m5 8V5'/%3E%3C/svg%3E");
}

/* Top Toolbar */
.view-title {
    font-size: 19px;
    font-weight: 700;
    color: #191A1F;
    letter-spacing: -0.4px;
    margin: 0;
}

.st-key-dashboard_toolbar {
    padding: 10px 0;
    border-bottom: 1px solid #E3E4E8;
}

@media (min-width: 901px) {
  [data-testid="stLayoutWrapper"]:has(> .st-key-dashboard_toolbar) {
    position: sticky;
    top: 0;
    z-index: 5;
    background: #FFFFFF;
  }
}

.st-key-dashboard_toolbar button {
    min-height: 34px;
    padding: 4px 12px;
}

/* Greeting Section */
.greeting-header {
    font-size: 22px;
    font-weight: 700;
    color: #191A1F;
    letter-spacing: -0.5px;
    margin-bottom: 2px;
}

.greeting-subtext {
    font-size: 13px;
    color: #747781;
    font-weight: 400;
    margin-bottom: 16px;
}

/* Four Financial Summary KPI Cards */
.metric-card {
    background-color: #FFFFFF;
    border: 1px solid #E3E4E8;
    border-radius: 14px;
    padding: 16px 18px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    min-height: 114px;
    box-shadow: 0 1px 3px rgba(25, 26, 31, 0.03);
    transition: transform 0.15s ease, box-shadow 0.15s ease, border-color 0.15s ease;
}

.metric-card:hover {
    transform: translateY(-1px);
    border-color: #CBD5E1;
    box-shadow: 0 6px 16px rgba(25, 26, 31, 0.05);
}

.metric-label {
    font-size: 12px;
    font-weight: 600;
    color: #747781;
    text-transform: uppercase;
    letter-spacing: 0.4px;
}

.metric-figure {
    font-size: clamp(20px, 1.8vw, 26px);
    font-weight: 700;
    color: #191A1F;
    letter-spacing: -0.6px;
    font-variant-numeric: tabular-nums;
    margin: 6px 0 3px 0;
}

.metric-badge {
    font-size: 11px;
    font-weight: 500;
    color: #747781;
    display: flex;
    align-items: center;
    gap: 4px;
    border-top: 1px solid #E3E4E8;
    padding-top: 6px;
}

.metric-badge.green {
    color: #2B6E4F;
    font-weight: 600;
}

.metric-badge.red {
    color: #C96F69;
    font-weight: 600;
}

.metric-badge.charcoal {
    color: #202126;
    font-weight: 600;
}

.metric-badge.secondary {
    color: #747781;
    font-weight: 400;
}

/* Chart panel headings */
.panel-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 12px;
}

.panel-title {
    font-size: 14px;
    font-weight: 700;
    color: #191A1F;
    letter-spacing: -0.2px;
    margin: 0;
}

.trend-surplus {
    line-height: 1.2;
    margin-top: 4px;
    color: #191A1F;
    font-size: 24px;
    font-weight: 750;
    letter-spacing: -.6px;
    font-variant-numeric: tabular-nums;
}

.chart-period {
    color: #747781;
    font-size: 11px;
    text-align: right;
}

/* Four Main Chart Panels */
:is(.st-key-dashboard_trend, .st-key-dashboard_breakdown, .st-key-dashboard_budgets, .st-key-dashboard_comparison) {
    background: #FFFFFF !important;
    border: 1px solid #E3E4E8 !important;
    border-radius: 14px !important;
    padding: 16px !important;
    box-shadow: 0 1px 3px rgba(25, 26, 31, 0.02) !important;
}

@media (min-width: 901px) {
  .st-key-dashboard_trend, .st-key-dashboard_breakdown { min-height: 314px; }
  .st-key-dashboard_budgets, .st-key-dashboard_comparison { min-height: 275px; }
}

/* Category Budget Row in Overview */
.budget-preview {
    display: grid;
    gap: 8px;
}

.budget-preview-item {
    padding: 8px 12px;
    background: #F8F9FA;
    border: 1px solid #ECEEF1;
    border-radius: 8px;
}

.budget-preview-label {
    display: flex;
    align-items: center;
    gap: 8px;
    color: #191A1F;
    font-size: 12px;
    font-weight: 600;
}

.budget-preview-label small {
    margin-left: auto;
    text-align: right;
    font-size: 11px;
    font-variant-numeric: tabular-nums;
}

.budget-dot {
    display: inline-grid;
    place-items: center;
    flex: 0 0 18px;
    height: 18px;
    border-radius: 50%;
    color: white;
    font-size: 10px;
    font-weight: 700;
}

.budget-progress-track {
    width: 100%;
    height: 5px;
    background-color: #ECEEF1;
    border-radius: 999px;
    overflow: hidden;
    margin-top: 5px;
}

.budget-progress-fill {
    height: 100%;
    border-radius: 999px;
    transition: width 0.3s ease;
}

/* Badges */
.badge-confirmed {
    background-color: #EBF5F0;
    color: #2B6E4F;
    border: 1px solid #CFE4D8;
    padding: 2px 7px;
    border-radius: 4px;
    font-size: 11px;
    font-weight: 600;
}

.badge-review {
    background-color: #FEF8EC;
    color: #D4A451;
    border: 1px solid #F9E7BE;
    padding: 2px 7px;
    border-radius: 4px;
    font-size: 11px;
    font-weight: 600;
}

.badge-overbudget {
    background-color: #FDF2F2;
    color: #C96F69;
    border: 1px solid #F5D3D1;
    padding: 2px 7px;
    border-radius: 4px;
    font-size: 11px;
    font-weight: 600;
}

/* Streamlit Button Refinements */
.stButton > button {
    border-radius: 8px !important;
    font-weight: 600 !important;
    font-size: 13px !important;
    transition: all 0.15s ease !important;
}

.stButton > button[kind="primary"] {
    background: #202126 !important;
    border: 1px solid #202126 !important;
    color: #FFFFFF !important;
    box-shadow: 0 2px 6px rgba(32, 33, 38, 0.12) !important;
}

.stButton > button[kind="primary"]:hover {
    background: #33363F !important;
    border-color: #33363F !important;
    box-shadow: 0 4px 12px rgba(32, 33, 38, 0.18) !important;
    transform: translateY(-1px);
}

.stButton > button[kind="secondary"] {
    background: #FFFFFF !important;
    border: 1px solid #E3E4E8 !important;
    color: #191A1F !important;
}

.stButton > button[kind="secondary"]:hover {
    background: #F4F4F6 !important;
    border-color: #CBD5E1 !important;
    color: #191A1F !important;
}

.sample-label {
    display: inline-block;
    color: #202126;
    background: #ECEEF1;
    border: 1px solid #E3E4E8;
    border-radius: 6px;
    padding: 3px 8px;
    font-size: .78rem;
    font-weight: 600;
}

.review-reason {
    background: #F8F9FA;
    color: #202126;
    border-inline-start: 3px solid #D4A451;
    border-radius: 6px;
    padding: 10px 14px;
    font-size: 13px;
    margin: 8px 0;
}

.st-key-holdout_explorer {
    background: #FFFFFF;
    border: 1px solid #E3E4E8;
    border-radius: 12px;
    padding: 16px;
}

.st-key-budget_editor {
    background: #FFFFFF;
    border: 1px solid #E3E4E8;
    border-radius: 12px;
    padding: 16px;
}

.st-key-budget_editor [data-testid="stHorizontalBlock"]:has([data-testid="stSlider"]) {
    padding: 8px 0;
    border-bottom: 1px solid #E3E4E8;
}

.budget-summary {
    background: #FFFFFF;
    border: 1px solid #E3E4E8;
    border-radius: 12px;
    padding: 16px 18px;
    margin-bottom: 10px;
}

.budget-summary-head {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 8px;
    flex-wrap: wrap;
}

.budget-summary-head h3 {
    margin: 0;
    padding: 0;
    font-size: 15px;
    font-weight: 700;
    color: #191A1F;
}

.budget-status {
    padding: 4px 10px;
    border-radius: 6px;
    background: #ECEEF1;
    color: #202126;
    font-size: 11px;
    font-weight: 700;
}

.budget-summary.over .budget-status {
    background: #FDF2F2;
    color: #C96F69;
    border: 1px solid #F5D3D1;
}

.budget-summary.on-track .budget-status {
    background: #EBF5F0;
    color: #2B6E4F;
    border: 1px solid #CFE4D8;
}

.budget-amounts, .budget-note {
    margin-top: 6px;
    color: #747781;
    font-size: 13px;
    font-variant-numeric: tabular-nums;
}

.budget-usage {
    display: grid;
    grid-template-columns: 1fr auto;
    align-items: center;
    gap: 12px;
    margin-top: 10px;
    color: #747781;
    font-size: 12px;
    font-variant-numeric: tabular-nums;
}

.budget-summary .budget-progress-track {
    height: 6px;
    border-radius: 999px;
    background: #ECEEF1;
}

.budget-summary .budget-progress-fill {
    height: 100%;
    border-radius: inherit;
    background: #78A98E;
}

.budget-summary.over .budget-progress-fill {
    background: #C96F69;
}

.evaluation-results {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(min(100%, 150px), 1fr));
    gap: 12px;
    margin: 12px 0;
}

.evaluation-result {
    padding: 14px;
    border-radius: 10px;
    background: #FFFFFF;
    border: 1px solid #E3E4E8;
    color: #191A1F;
}

.evaluation-result strong {
    display: block;
    font-size: 26px;
    font-weight: 700;
    font-variant-numeric: tabular-nums;
    color: #202126;
    margin-bottom: 2px;
}

/* Streamlit 1.66 App Frame */
@media (min-width: 901px) {
  [data-testid="stHeader"] { display: none !important; }
  [data-testid="stAppViewContainer"] {
    --frame-gutter: clamp(16px, 2vw, 36px);
    --frame-top: clamp(14px, 2vh, 24px);
    --rail: clamp(210px, 16vw, 250px);
    margin: var(--frame-top) auto !important;
    height: calc(100dvh - 2 * var(--frame-top)) !important;
    min-height: 0 !important;
    width: calc(100% - 2 * var(--frame-gutter)) !important;
    border: 1px solid #E3E4E8;
    border-radius: 20px;
    overflow: hidden;
    background: #FFFFFF !important;
    box-shadow: 0 4px 24px rgba(25, 26, 31, 0.05);
  }
  [data-testid="stSidebar"] {
    width: var(--rail) !important;
    min-width: var(--rail) !important;
    max-width: var(--rail) !important;
  }
  [data-testid="stSidebar"] > div:first-child { width: var(--rail) !important; }
  [data-testid="stSidebarHeader"] { display: none !important; }
  [data-testid="stSidebar"] [data-testid="stSidebarContent"],
  [data-testid="stSidebar"] [data-testid="stSidebarUserContent"] {
    height: 100% !important;
    min-height: 0 !important;
  }
  [data-testid="stMain"] {
    height: calc(100dvh - 2 * var(--frame-top) - 2px) !important;
    min-height: 0 !important;
    overflow-y: auto !important;
    background: #FFFFFF !important;
  }
  [data-testid="stSidebar"] [data-testid="stVerticalBlock"]:has(> [data-testid="stElementContainer"] .sidebar-spacer) {
    min-height: calc(100dvh - 2 * var(--frame-top) - 16px);
  }
}

[data-testid="stToolbar"], [data-testid="stAppDeployButton"] { display: none !important; }
[data-testid="stMain"] { background: #FFFFFF !important; }
[data-testid="stMainBlockContainer"] { max-width: none !important; padding: 0 16px 20px !important; }
[data-testid="stSidebar"] [data-testid="stSidebarContent"] { padding: 0 !important; }
[data-testid="stSidebar"] [data-testid="stSidebarUserContent"] { padding: 0 12px 14px !important; min-height: 100%; }
[data-testid="stSidebar"] [data-testid="stSidebarUserContent"] > [data-testid="stVerticalBlock"] { min-height: 100%; }
[data-testid="stSidebar"] [data-testid="stVerticalBlock"] > [data-testid="stElementContainer"]:has(.sidebar-spacer) { flex: 1; min-height: 12px; }
[data-testid="stSidebar"] [data-testid="stVerticalBlock"] { gap: .55rem !important; }
[data-testid="stMain"] [data-testid="stVerticalBlock"] { gap: .65rem; }
[data-testid="stMain"] [data-testid="stHorizontalBlock"] { gap: 12px; }

/* Ledger & Table Styling */
.ledger-header {
  font-size: 11px;
  font-weight: 700;
  color: #747781;
  text-transform: uppercase;
  letter-spacing: 0.6px;
  padding: 8px 10px;
  border-bottom: 1px solid #E3E4E8;
  margin-bottom: 6px;
}

.ledger-row {
  background: #FFFFFF;
  border: 1px solid #E3E4E8;
  border-radius: 10px;
  padding: 10px 14px;
  margin-bottom: 6px;
  transition: all 0.15s ease;
}

.ledger-row:hover {
  border-color: #CBD5E1;
  box-shadow: 0 4px 12px rgba(25, 26, 31, 0.04);
}

@media (prefers-reduced-motion: reduce) {
  .budget-progress-fill, .metric-card, .metric-figure, .stButton > button, .ledger-row {
    animation: none !important;
    transition: none !important;
  }
}

@media (max-width: 900px) {
  [data-testid="stMain"] { background: #FFFFFF !important; }
  [data-testid="stMainBlockContainer"] { padding: 56px 12px 24px !important; }
  [data-testid="stHeader"] {
    height: 48px !important;
    min-height: 48px !important;
    background: #FFFFFF !important;
    pointer-events: none;
  }
  [data-testid="stHeader"] button { pointer-events: auto; }
  [data-testid="stToolbar"] { display: flex !important; }
  [data-testid="stMain"] [data-testid="stHorizontalBlock"] { gap: 10px; }
}

@media (max-width: 640px) {
  .st-key-dashboard_metrics [data-testid="stHorizontalBlock"],
  .st-key-dashboard_toolbar [data-testid="stHorizontalBlock"] {
    display: grid !important;
    grid-template-columns: repeat(2, minmax(0,1fr));
  }
  .st-key-dashboard_metrics [data-testid="stColumn"],
  .st-key-dashboard_toolbar [data-testid="stColumn"] {
    width: 100% !important;
    min-width: 0 !important;
  }
  .st-key-dashboard_toolbar [data-testid="stColumn"]:first-child { grid-column: 1 / -1; }
  .metric-card { min-height: 100px; padding: 12px; }
  .metric-figure { font-size: 19px; }
}
</style>
"""
st.html(SPENDSTORY_CSS)


# -----------------------------------------------------------------------------
# Database & State Initialization
# -----------------------------------------------------------------------------
@st.cache_resource
def get_database(path: str) -> Database:
    return Database(path)


DEMO_CSV = Path("data/demo/transactions.csv")
DEMO_MONTH = "2026-11"
HOSTED_DEMO = os.environ.get("SPENDSTORY_DEMO") == "1"
if HOSTED_DEMO:
    # Keep each visitor's demo edits in their own Streamlit session.
    if "demo_db" not in st.session_state:
        demo_db = Database(":memory:")
        demo_db.load_demo_data(DEMO_CSV)
        st.session_state.demo_db = demo_db
    db = st.session_state.demo_db
else:
    db = get_database(os.environ.get("FINANCE_DB_PATH", "storage/finance.db"))
categorizer = get_default_categorizer()

NAV_OPTIONS = ("Overview", "Transactions", "Budgets", "Category Review", "Model Evaluation")
ledger_months = db.get_available_months()
available_months = ledger_months or ["2026-10", "2026-11"]

# Direct query params initialize widgets; session state owns updates
query_nav = st.query_params.get("nav")
query_month = st.query_params.get("month")

st.session_state.setdefault("active_nav", query_nav if query_nav in NAV_OPTIONS else "Overview")
default_month = DEMO_MONTH if HOSTED_DEMO and DEMO_MONTH in available_months else available_months[0]
st.session_state.setdefault("selected_month", query_month if query_month in available_months else default_month)
st.session_state.setdefault("search_query", "")
st.session_state.setdefault("tx_type_filter", "All")
st.session_state.setdefault("tx_cat_filter", "All")
st.session_state.setdefault("tx_review_filter", "All")
st.session_state.setdefault("custom_cursor_enabled", True)

if st.session_state.selected_month not in available_months:
    st.session_state.selected_month = available_months[0]


def open_search_results() -> None:
    if st.session_state.search_query.strip():
        st.session_state.active_nav = "Transactions"


def open_budgets() -> None:
    st.session_state.active_nav = "Budgets"


def close_budget_editor() -> None:
    st.session_state.budget_editor_month = None


def load_sample_data() -> None:
    result = db.load_demo_data(DEMO_CSV)
    st.session_state.selected_month = DEMO_MONTH
    message = f"Fictional sample data: {result.inserted} added, {result.skipped} already present."
    if result.conflicts:
        message += f" {len(result.conflicts)} conflicting IDs kept unchanged."
    st.toast(message)


@st.cache_data
def demo_fingerprints(csv_bytes: bytes) -> set[str]:
    transactions, _ = parse_transactions_csv(csv_bytes)
    return {tx.fingerprint for tx in transactions}


# -----------------------------------------------------------------------------
# Sidebar Navigation & Settings
# -----------------------------------------------------------------------------
with st.sidebar:
    # SpendStory brand wordmark
    st.html(
        """
        <div class="spendstory-logo">
            <span class="logo-dot"></span>
            <span>SpendStory</span>
        </div>
        """
    )

    # Count items needing review for navigation badge
    unreviewed_items = db.get_transactions(review_status="needs_review")
    review_label = f"Category Review ({len(unreviewed_items)})" if unreviewed_items else "Category Review"

    st.radio(
        "Navigation",
        options=NAV_OPTIONS,
        key="active_nav",
        format_func=lambda section: review_label if section == "Category Review" else section,
        label_visibility="collapsed",
    )

    st.html('<div class="sidebar-spacer" aria-hidden="true"></div>')

    with st.expander("Settings & Appearance"):
        st.toggle(
            "Kawaii Custom Cursor",
            value=st.session_state.custom_cursor_enabled,
            key="custom_cursor_enabled",
        )
        st.caption("Exact reference illustrated arrow and pointing hand cursor. Switch off anytime to use standard system cursor.")

    with st.expander("Demo tools"):
        st.caption("Load fictional student transactions and sample budgets.")
        st.button("Try sample data", key="sidebar_sample_data", on_click=load_sample_data, width="stretch")

    with st.expander("Reset / Clear Data"):
        st.caption("Clear this demo session’s ledger." if HOSTED_DEMO else "Erase local transactions and budgets stored in SQLite.")
        confirm = st.checkbox("I confirm clearing all data", key="clear_confirm_cb")
        if st.button("Clear All Data", type="secondary", disabled=not confirm, width="stretch"):
            db.clear_all_data()
            st.toast("Ledger cleared.")
            st.rerun()


# Inject dual-layer custom cursor according to user preference
cursor_is_active = st.session_state.get("custom_cursor_enabled", True)
st.html(get_cursor_css(cursor_is_active))
st.components.v1.html(get_cursor_follower_html(cursor_is_active), height=0)


# -----------------------------------------------------------------------------
# Contextual Top Toolbar
# -----------------------------------------------------------------------------
if HOSTED_DEMO:
    st.caption("Fictional demo · Use sample data only. Changes last for this browser session.")

all_txs_for_month = db.get_transactions(year_month=st.session_state.selected_month)
show_import_dialog = False

with st.container(key="dashboard_toolbar"):
    if st.session_state.active_nav == "Overview":
        toolbar_cols = st.columns([3.0, 2.0, 2.0, 1.2, 1.2], vertical_alignment="center")
        with toolbar_cols[0]:
            st.html('<h1 class="view-title">Overview</h1>')
        with toolbar_cols[1]:
            st.text_input(
                "Search",
                key="search_query",
                placeholder="Search transactions...",
                label_visibility="collapsed",
                on_change=open_search_results,
            )
        with toolbar_cols[2]:
            st.selectbox(
                "Month",
                options=available_months,
                key="selected_month",
                format_func=lambda ym: datetime.strptime(ym, "%Y-%m").strftime("%B %Y"),
                label_visibility="collapsed",
            )
        with toolbar_cols[3]:
            csv_bytes = export_transactions_to_csv(all_txs_for_month).encode("utf-8")
            st.download_button(
                label="Export CSV",
                data=csv_bytes,
                file_name=f"transactions_{st.session_state.selected_month}.csv",
                mime="text/csv",
                width="stretch",
            )
        with toolbar_cols[4]:
            show_import_dialog = st.button("Import CSV", width="stretch")

    elif st.session_state.active_nav == "Transactions":
        toolbar_cols = st.columns([2.6, 2.2, 1.8, 1.2, 1.2], vertical_alignment="center")
        with toolbar_cols[0]:
            st.html('<h1 class="view-title">Transactions</h1>')
        with toolbar_cols[1]:
            st.text_input(
                "Search",
                key="search_query",
                placeholder="Search transactions...",
                label_visibility="collapsed",
            )
        with toolbar_cols[2]:
            st.selectbox(
                "Month",
                options=available_months,
                key="selected_month",
                format_func=lambda ym: datetime.strptime(ym, "%Y-%m").strftime("%B %Y"),
                label_visibility="collapsed",
            )
        with toolbar_cols[3]:
            csv_bytes = export_transactions_to_csv(all_txs_for_month).encode("utf-8")
            st.download_button(
                label="Export CSV",
                data=csv_bytes,
                file_name=f"transactions_{st.session_state.selected_month}.csv",
                mime="text/csv",
                width="stretch",
            )
        with toolbar_cols[4]:
            show_import_dialog = st.button("Import CSV", width="stretch")

    elif st.session_state.active_nav == "Budgets":
        toolbar_cols = st.columns([5.5, 2.0, 2.5], vertical_alignment="center")
        with toolbar_cols[0]:
            st.html('<h1 class="view-title">Budgets</h1>')
        with toolbar_cols[1]:
            st.html('<div style="text-align:right; color:#747781; font-size:12px; font-weight:500;">Budget month</div>')
        with toolbar_cols[2]:
            st.selectbox(
                "Month",
                options=available_months,
                key="selected_month",
                format_func=lambda ym: datetime.strptime(ym, "%Y-%m").strftime("%B %Y"),
                label_visibility="collapsed",
                on_change=close_budget_editor,
            )

    elif st.session_state.active_nav == "Category Review":
        toolbar_cols = st.columns([4.2, 3.2, 2.6], vertical_alignment="center")
        with toolbar_cols[0]:
            st.html('<h1 class="view-title">Category Review</h1>')
        with toolbar_cols[1]:
            st.radio(
                "Review Scope",
                options=["All Records", "Current Month"],
                horizontal=True,
                key="review_scope",
                label_visibility="collapsed",
            )
        with toolbar_cols[2]:
            if st.session_state.get("review_scope") == "Current Month":
                st.selectbox(
                    "Month",
                    options=available_months,
                    key="selected_month",
                    format_func=lambda ym: datetime.strptime(ym, "%Y-%m").strftime("%B %Y"),
                    label_visibility="collapsed",
                )
            else:
                st.html('<div style="text-align:right; font-size:11.5px; color:#747781;">Scope: Entire Database</div>')

    elif st.session_state.active_nav == "Model Evaluation":
        toolbar_cols = st.columns([6.0, 4.0], vertical_alignment="center")
        with toolbar_cols[0]:
            st.html('<h1 class="view-title">Model Evaluation</h1>')
        with toolbar_cols[1]:
            st.html('<div style="text-align:right;"><span style="font-size:11.5px; background:#ECEEF1; color:#202126; padding:5px 10px; border-radius:12px; font-weight:600;">Fictional test data</span></div>')

# Sync query parameters with navigation & month
if query_nav != st.session_state.active_nav or query_month != st.session_state.selected_month:
    st.query_params.update(nav=st.session_state.active_nav, month=st.session_state.selected_month)

# CSV Import Panel
if show_import_dialog or st.session_state.get("show_import_panel", False):
    st.session_state.show_import_panel = True
    with st.container(border=True):
        st.subheader("Import Transactions CSV")
        st.caption("Upload a UTF-8 CSV with headers: `id,date,description,amount,type,category`. Limit 2 MB, 10,000 rows.")
        if HOSTED_DEMO:
            st.caption("Use fictional transactions here. For personal records, run SpendStory locally.")
        uploaded_file = st.file_uploader("Select CSV file", type=["csv"], label_visibility="collapsed")
        if uploaded_file:
            content_bytes = uploaded_file.read()
            txs, parse_errors = parse_transactions_csv(content_bytes)
            if parse_errors:
                st.error("Validation failed with zero records imported:")
                for err in parse_errors[:10]:
                    st.write(f"• {err}")
                if len(parse_errors) > 10:
                    st.caption(f"...and {len(parse_errors) - 10} more errors.")
            else:
                st.success(f"CSV validated successfully: {len(txs)} rows ready for atomic import.")
                preview_df = pd.DataFrame(
                    [
                        {
                            "ID": t.id,
                            "Date": t.date,
                            "Description": t.description,
                            "Amount (₹)": f"₹{t.amount_inr:,.2f}",
                            "Type": t.type,
                            "Category": t.category or "(Model Suggestion)",
                        }
                        for t in txs[:5]
                    ]
                )
                st.dataframe(preview_df, width="stretch", hide_index=True)
                if st.button("Commit Atomic Import", type="primary"):
                    prepared_txs = []
                    for t in txs:
                        if t.type == "expense" and not t.category:
                            pred = categorizer.predict(t.description)
                            prepared_txs.append(
                                Transaction(
                                    id=t.id,
                                    date=t.date,
                                    description=t.description,
                                    amount_paise=t.amount_paise,
                                    type=t.type,
                                    category=pred.category,
                                    category_source="model",
                                    review_status=pred.review_status,
                                    model_score=pred.model_score,
                                    fingerprint=t.fingerprint,
                                )
                            )
                        else:
                            prepared_txs.append(t)

                    res = db.save_transactions(prepared_txs)
                    st.toast(f"Import complete: {res.inserted} inserted, {res.skipped} skipped, {len(res.conflicts)} conflicts.")
                    st.session_state.show_import_panel = False
                    st.rerun()

        if st.button("Close Import Panel"):
            st.session_state.show_import_panel = False
            st.rerun()


# =============================================================================
# VIEW 1: OVERVIEW (Soft Neutral Canvas & White Surface Dashboard)
# =============================================================================
if st.session_state.active_nav == "Overview":
    month_name = datetime.strptime(st.session_state.selected_month, "%Y-%m").strftime("%B %Y")
    st.html(
        f'''
        <div class="greeting-header">Good day, Student 👋</div>
        <div class="greeting-subtext">Your money overview · {month_name}</div>
        '''
    )

    if not ledger_months:
        with st.container(border=True):
            st.markdown("**Explore SpendStory with a sample ledger**")
            st.caption("Load a year of fictional student transactions and budgets.")
            st.button("Try sample data", key="overview_sample_data", type="primary", on_click=load_sample_data)
    elif all_txs_for_month:
        fingerprints = demo_fingerprints(DEMO_CSV.read_bytes())
        if any(tx.fingerprint in fingerprints for tx in all_txs_for_month):
            st.html('<span class="sample-label">Includes fictional sample data</span>')

    summary = calculate_monthly_summary(all_txs_for_month, st.session_state.selected_month)

    # Distinct visual treatment for surplus vs deficit
    if summary.recorded_surplus_paise > 0:
        surplus_caption = "Positive surplus · Income less expenses"
        surplus_tone = "green"
    elif summary.recorded_surplus_paise < 0:
        surplus_caption = "Recorded deficit · Expenses exceed income"
        surplus_tone = "red"
    else:
        surplus_caption = "Exact balance"
        surplus_tone = "charcoal"

    metrics = (
        ("Recorded income", summary.income_paise, "Income this month", "green"),
        ("Recorded expenses", summary.expense_paise, "Spending this month", "charcoal"),
        ("Recorded surplus", summary.recorded_surplus_paise, surplus_caption, surplus_tone),
        ("Transfers excluded", summary.transfer_paise, "Tracked separately · Excluded from surplus", "secondary"),
    )

    with st.container(key="dashboard_metrics"):
        for column, (label, amount, caption, tone) in zip(st.columns(4), metrics):
            with column:
                st.html(
                    f'''
                    <div class="metric-card">
                        <span class="metric-label">{label}</span>
                        <div class="metric-figure">{format_inr(amount)}</div>
                        <div class="metric-badge {tone}">{caption}</div>
                    </div>
                    '''
                )

    trend, breakdown = st.columns([7.15, 2.85])
    with trend, st.container(key="dashboard_trend"):
        surplus_color = "#191A1F" if summary.recorded_surplus_paise >= 0 else "#C96F69"
        st.html(
            f'''
            <div class="panel-header">
                <div>
                    <div class="panel-title">Income &amp; expense trends</div>
                    <div class="trend-surplus" style="color: {surplus_color};">{format_inr(summary.recorded_surplus_paise)}</div>
                </div>
                <span class="chart-period">Recorded surplus · {month_name}</span>
            </div>
            '''
        )
        trend_data = calculate_cumulative_trend(all_txs_for_month, st.session_state.selected_month)
        if trend_data:
            render_trend(trend_data, key="overview_trend")
        else:
            st.caption("Add transactions to see how your month is taking shape.")

    with breakdown, st.container(key="dashboard_breakdown"):
        st.html('<div class="panel-header"><span class="panel-title">Monthly expenses breakdown</span></div>')
        donut_rows = [
            {"Category": category, "Amount": paise / 100}
            for category, paise in summary.expense_by_category_paise.items()
            if paise > 0
        ]
        if donut_rows:
            render_donut(donut_rows, key="overview_breakdown")
        else:
            st.caption("Your expense breakdown will appear here.")

    budgets, comparison = st.columns([2.85, 7.15])
    with budgets, st.container(key="dashboard_budgets"):
        st.html('<div class="panel-header"><span class="panel-title">Monthly budgets</span></div>')
        budget_targets = db.get_budgets(st.session_state.selected_month)
        comparisons = calculate_budget_comparisons(summary.expense_by_category_paise, budget_targets)
        if comparisons:
            colors = ("#78A98E", "#5E7C8D", "#8EA89D", "#C96F69", "#D4A451", "#202126", "#A0AEC0")
            rows = []
            for index, item in enumerate(comparisons[:5]):
                color = colors[index % len(colors)]
                spent = format_inr(item.spent_paise)
                if item.budget_paise is None:
                    status = spent + " · No target set"
                    badge_style = "color:#747781;"
                elif item.is_over:
                    status = format_inr(item.delta_paise) + " over"
                    badge_style = "color:#C96F69; font-weight:700;"
                else:
                    status = spent + " / " + format_inr(item.budget_paise)
                    badge_style = "color:#2B6E4F; font-weight:600;"
                progress = min(100, item.percent_used or 0)
                rows.append(
                    f'''
                    <div class="budget-preview-item">
                      <div class="budget-preview-label">
                        <span class="budget-dot" style="background:{color}" aria-hidden="true">{html.escape(item.category[:1])}</span>
                        <span>{html.escape(item.category)}</span><small style="{badge_style}">{status}</small>
                      </div>
                      <div class="budget-progress-track" aria-hidden="true">
                        <div class="budget-progress-fill" style="width:{progress}%;background:{color}"></div>
                      </div>
                    </div>
                    '''
                )
            st.html('<div class="budget-preview">' + "".join(rows) + '</div>')
            if len(comparisons) > 5:
                st.caption(f"Showing 5 of {len(comparisons)} categories.")
        else:
            st.caption("Set a budget to track spending against a target.")
        st.button("Manage all budgets →", key="btn_goto_budgets", width="stretch", on_click=open_budgets)

    with comparison, st.container(key="dashboard_comparison"):
        multi_month = calculate_multi_month_comparison(db.get_transactions())
        hint = '<span class="chart-period">Select a month to explore</span>' if multi_month else ''
        st.html(f'<div class="panel-header"><span class="panel-title">Monthly income vs expenses</span>{hint}</div>')
        if multi_month:
            render_monthly(multi_month, selected_month=st.session_state.selected_month, key="overview_monthly")
        else:
            st.caption("Record income or expenses to compare months.")


# =============================================================================
# VIEW 2: TRANSACTIONS & CSV WORKFLOWS
# =============================================================================
elif st.session_state.active_nav == "Transactions":
    month_name = datetime.strptime(st.session_state.selected_month, "%Y-%m").strftime("%B %Y")
    
    t_head_col, t_act_col = st.columns([7, 3], vertical_alignment="center")
    with t_head_col:
        st.subheader(f"Transactions — {month_name}")
        st.caption("Browse, filter, edit categories, and record student financial entries.")
    with t_act_col:
        add_clicked = st.button("➕ Add Transaction", type="primary", width="stretch")
        if add_clicked:
            st.session_state.show_add_tx = not st.session_state.get("show_add_tx", False)

    # Focused Add Transaction Editor
    if st.session_state.get("show_add_tx", False):
        with st.container(border=True):
            st.markdown("#### Record New Transaction")
            with st.form("add_tx_form", clear_on_submit=False):
                a_col1, a_col2 = st.columns([2, 2])
                with a_col1:
                    default_date = date.today()
                    try:
                        # Default date aligned with selected month
                        default_date = date(int(st.session_state.selected_month[:4]), int(st.session_state.selected_month[5:7]), 15)
                    except Exception:
                        pass
                    tx_date = st.date_input("Date", value=default_date)
                    tx_type = st.selectbox("Type", options=["expense", "income", "transfer"])
                with a_col2:
                    tx_amount = st.text_input("Amount in INR (₹)", placeholder="e.g. 150.00")
                    if tx_type == "expense":
                        tx_cat = st.selectbox(
                            "Category",
                            options=["(Let AI Suggest Category)"] + sorted(list(ALLOWED_EXPENSE_CATEGORIES)),
                        )
                    elif tx_type == "income":
                        tx_cat = "Income"
                        st.text_input("Category", value="Income", disabled=True)
                    else:
                        tx_cat = "Transfer"
                        st.text_input("Category", value="Transfer", disabled=True)

                tx_desc = st.text_input("Description", placeholder="e.g. University canteen thali, Semester book purchase")

                f_btn_col1, f_btn_col2 = st.columns([2, 8])
                with f_btn_col1:
                    submit_tx = st.form_submit_button("Record Transaction", type="primary", width="stretch")
                with f_btn_col2:
                    cancel_add = st.form_submit_button("Cancel", width="stretch")

                if cancel_add:
                    st.session_state.show_add_tx = False
                    st.rerun()

                if submit_tx:
                    clean_desc = tx_desc.strip()
                    if not clean_desc:
                        st.error("Description cannot be empty.")
                    else:
                        try:
                            paise = parse_amount_to_paise(tx_amount)
                            if paise <= 0:
                                st.error("Amount must be greater than zero.")
                            else:
                                iso_date = tx_date.isoformat()
                                gen_id = f"TX-{datetime.now().strftime('%Y%m%d%H%M%S%f')[:17]}"
                                final_cat = ""
                                cat_src = "manual"
                                status = "confirmed"
                                score = None

                                if tx_type == "income":
                                    final_cat = "Income"
                                raid_cat = "Transfer" if tx_type == "transfer" else None
                                if tx_type == "transfer":
                                    final_cat = "Transfer"
                                elif tx_type == "expense":
                                    if tx_cat == "(Let AI Suggest Category)":
                                        pred = categorizer.predict(clean_desc)
                                        final_cat = pred.category
                                        cat_src = "model"
                                        status = pred.review_status
                                        score = pred.model_score
                                    else:
                                        final_cat = tx_cat

                                fp = compute_fingerprint(iso_date, clean_desc, paise, tx_type)
                                new_tx = Transaction(
                                    id=gen_id,
                                    date=iso_date,
                                    description=clean_desc,
                                    amount_paise=paise,
                                    type=tx_type,
                                    category=final_cat,
                                    category_source=cat_src,
                                    review_status=status,
                                    model_score=score,
                                    fingerprint=fp,
                                )
                                db.add_transaction(new_tx)
                                st.session_state.show_add_tx = False
                                
                                # Inform if transaction date is outside currently active month
                                tx_month = iso_date[:7]
                                if tx_month != st.session_state.selected_month:
                                    st.info(f"Transaction recorded for {iso_date}! Note: This entry is in {tx_month}, outside your currently viewed month ({st.session_state.selected_month}).")
                                else:
                                    st.toast(f"Transaction recorded! Assigned category: {final_cat}")
                                st.rerun()
                        except Exception as e:
                            st.error(f"Error parsing amount: {e}")

    # Consolidated Filter Area
    with st.container(border=True):
        flt_c1, flt_c2, flt_c3, flt_c4 = st.columns([2.5, 2.5, 2.5, 2.5])
        with flt_c1:
            tx_type_options = ["All", "expense", "income", "transfer"]
            cur_type_idx = tx_type_options.index(st.session_state.tx_type_filter) if st.session_state.tx_type_filter in tx_type_options else 0
            selected_type = st.selectbox("Type", options=tx_type_options, index=cur_type_idx, key="tx_type_filter")
        with flt_c2:
            cat_options = ["All"] + sorted(list(ALLOWED_EXPENSE_CATEGORIES)) + ["Income", "Transfer"]
            cur_cat_idx = cat_options.index(st.session_state.tx_cat_filter) if st.session_state.tx_cat_filter in cat_options else 0
            selected_cat = st.selectbox("Category", options=cat_options, index=cur_cat_idx, key="tx_cat_filter")
        with flt_c3:
            rev_options = ["All", "needs_review", "confirmed"]
            cur_rev_idx = rev_options.index(st.session_state.tx_review_filter) if st.session_state.tx_review_filter in rev_options else 0
            selected_rev = st.selectbox("Review Status", options=rev_options, index=cur_rev_idx, key="tx_review_filter")
        with flt_c4:
            sort_order = st.selectbox("Sort Order", options=["Date: Newest First", "Date: Oldest First", "Amount: Highest First", "Amount: Lowest First"])

        active_chips = []
        if selected_type != "All":
            active_chips.append(f"Type: {selected_type}")
        if selected_cat != "All":
            active_chips.append(f"Category: {selected_cat}")
        if selected_rev != "All":
            active_chips.append(f"Status: {selected_rev}")
        if st.session_state.search_query.strip():
            active_chips.append(f'Search: "{st.session_state.search_query.strip()}"')

        ch_col, rst_col = st.columns([8, 2], vertical_alignment="center")
        with ch_col:
            if active_chips:
                st.html(f'<span style="font-size:12px; color:#191A1F;">Active Filters: <b>{" • ".join(active_chips)}</b></span>')
            else:
                st.html('<span style="font-size:12px; color:#747781;">Showing all records for selected month.</span>')
        with rst_col:
            if active_chips:
                if st.button("Reset Filters", width="stretch"):
                    st.session_state.tx_type_filter = "All"
                    st.session_state.tx_cat_filter = "All"
                    st.session_state.tx_review_filter = "All"
                    st.session_state.search_query = ""
                    st.rerun()

    # Query matching records
    matching_txs = db.get_transactions(
        year_month=st.session_state.selected_month,
        category=selected_cat if selected_cat != "All" else None,
        tx_type=selected_type if selected_type != "All" else None,
        review_status=selected_rev if selected_rev != "All" else None,
        search_query=st.session_state.search_query.strip() or None,
    )

    # Sort matching records
    if sort_order == "Date: Oldest First":
        matching_txs = sorted(matching_txs, key=lambda t: (t.date, t.id))
    elif sort_order == "Amount: Highest First":
        matching_txs = sorted(matching_txs, key=lambda t: t.amount_paise, reverse=True)
    elif sort_order == "Amount: Lowest First":
        matching_txs = sorted(matching_txs, key=lambda t: t.amount_paise)
    else:  # Date: Newest First
        matching_txs = sorted(matching_txs, key=lambda t: (t.date, t.id), reverse=True)

    if matching_txs:
        st.write(f"Showing **{len(matching_txs)}** transaction(s).")

        # Table Header
        h_cols = st.columns([1.5, 3.8, 1.6, 1.2, 2.4, 1.5])
        with h_cols[0]:
            st.markdown('<div class="ledger-header">Date</div>', unsafe_allow_html=True)
        with h_cols[1]:
            st.markdown('<div class="ledger-header">Description &amp; Status</div>', unsafe_allow_html=True)
        with h_cols[2]:
            st.markdown('<div class="ledger-header">Amount</div>', unsafe_allow_html=True)
        with h_cols[3]:
            st.markdown('<div class="ledger-header">Type</div>', unsafe_allow_html=True)
        with h_cols[4]:
            st.markdown('<div class="ledger-header">Category</div>', unsafe_allow_html=True)
        with h_cols[5]:
            st.markdown('<div class="ledger-header">Action</div>', unsafe_allow_html=True)

        for tx in matching_txs:
            with st.container(border=True):
                r_cols = st.columns([1.5, 3.8, 1.6, 1.2, 2.4, 1.5], vertical_alignment="center")
                with r_cols[0]:
                    st.write(f"**{tx.date}**")
                    st.html(f'<span style="font-size:10px; color:#747781; font-family:monospace;" title="{tx.id}">{tx.id[:12]}…</span>')
                with r_cols[1]:
                    st.write(html.escape(tx.description))
                    badge = f'<span class="badge-review">Review ({tx.model_score:.2f})</span>' if tx.review_status == "needs_review" else '<span class="badge-confirmed">Confirmed</span>'
                    st.html(f'<span style="font-size:11px; color:#747781;">Source: {tx.category_source} • {badge}</span>')
                with r_cols[2]:
                    amt_color = "#2B6E4F" if tx.type == "income" else ("#191A1F" if tx.type == "expense" else "#5E7C8D")
                    st.html(f'<span style="font-weight:700; color:{amt_color}; font-variant-numeric:tabular-nums;">{format_inr(tx.amount_paise)}</span>')
                with r_cols[3]:
                    st.code(tx.type, language=None)
                with r_cols[4]:
                    if tx.type == "expense":
                        cat_opts = sorted(list(ALLOWED_EXPENSE_CATEGORIES))
                        cur_idx = cat_opts.index(tx.category) if tx.category in cat_opts else 0
                        new_cat = st.selectbox(
                            "Category",
                            options=cat_opts,
                            index=cur_idx,
                            key=f"edit_cat_{tx.id}",
                            label_visibility="collapsed",
                        )
                        if new_cat != tx.category:
                            db.update_transaction_category(tx.id, new_cat, review_status="confirmed", category_source="manual")
                            st.toast(f"Updated {tx.id} category to {new_cat}")
                            st.rerun()
                    else:
                        st.write(f"*{tx.category}*")
                with r_cols[5]:
                    del_key = f"del_confirm_{tx.id}"
                    if not st.session_state.get(del_key, False):
                        if st.button("Delete", key=f"btn_del_{tx.id}", type="secondary", width="stretch"):
                            st.session_state[del_key] = True
                            st.rerun()
                    else:
                        st.error("Delete?")
                        d_c1, d_c2 = st.columns(2)
                        with d_c1:
                            if st.button("Yes", key=f"conf_yes_{tx.id}", type="primary"):
                                db.delete_transaction(tx.id)
                                st.session_state[del_key] = False
                                st.toast(f"Deleted {tx.description}")
                                st.rerun()
                        with d_c2:
                            if st.button("No", key=f"conf_no_{tx.id}"):
                                st.session_state[del_key] = False
                                st.rerun()
    else:
        st.info("No transactions match the selected criteria for this month.")


# =============================================================================
# VIEW 3: BUDGETS
# =============================================================================
elif st.session_state.active_nav == "Budgets":
    month = st.session_state.selected_month
    month_name = datetime.strptime(month, "%Y-%m").strftime("%B %Y")
    summary = calculate_monthly_summary(all_txs_for_month, month)
    current_budgets = db.get_budgets(month)
    comparisons = calculate_budget_comparisons(summary.expense_by_category_paise, current_budgets)

    title_col, action_col = st.columns([3, 1], vertical_alignment="center")
    with title_col:
        st.subheader(f"Category budgets · {month_name}")
        st.caption("See what you spent and how much room is left in each category.")
    with action_col:
        if st.button("Configure budgets", key="configure_budgets", type="primary", width="stretch"):
            st.session_state.budget_editor_month = month

    if st.session_state.get("budget_editor_month") == month:
        with st.container(key="budget_editor", border=True):
            st.markdown("#### Set your monthly limits")
            st.caption("Drag each slider to set a target. Turn tracking off to remove a target. A ₹0 target means no spending.")
            budget_entries = {}
            for cat in sorted(ALLOWED_EXPENSE_CATEGORIES):
                saved = current_budgets.get(cat)
                spent = summary.expense_by_category_paise.get(cat, 0)
                upper = max(1_000_000, 2 * max(saved or 0, spent))
                step = max(5_000, ((upper + 999_999) // 1_000_000) * 5_000)
                options = sorted(set(range(0, upper + step, step)) | {saved or 0})
                with st.container(key=f"budget_control_{cat}"):
                    track_col, slider_col = st.columns([1, 3], vertical_alignment="center")
                    with track_col:
                        enabled = st.toggle(f"Track {cat}", value=saved is not None, key=f"budget_track_{month}_{cat}")
                    with slider_col:
                        target = st.select_slider(
                            f"{cat} target", options=options, value=saved or 0,
                            format_func=format_inr, disabled=not enabled, key=f"budget_slider_{month}_{cat}",
                        )
                    budget_entries[cat] = target if enabled else None

            save_col, cancel_col = st.columns([1, 3])
            with save_col:
                save = st.button("Save budgets", key="save_budget_targets", type="primary", width="stretch")
            with cancel_col:
                cancel = st.button("Cancel", key="cancel_budget_targets")
            if save:
                changed = {cat: target for cat, target in budget_entries.items() if current_budgets.get(cat) != target}
                db.save_budget_targets(month, changed)
                st.toast(f"Budgets saved for {month_name}.")
            if save or cancel:
                st.session_state.budget_editor_month = None
                st.rerun()

    st.markdown("#### Spending against your targets")
    if not comparisons:
        st.info("Set a target or add an expense to start tracking a category.")

    # Put categories that need attention ahead of the categories on track.
    comparisons.sort(key=lambda comp: (not comp.is_over, comp.budget_paise is not None, comp.category))
    for comp in comparisons:
        spent_label = format_inr(comp.spent_paise)
        if comp.budget_paise is None:
            status, tone, note = "No target", "neutral", "Set a target to track this category."
            target_label = "—"
        elif comp.is_over:
            status, tone = f"{format_inr(comp.delta_paise)} over", "over"
            note = "Check upcoming expenses in this category before spending more."
            target_label = format_inr(comp.budget_paise)
        else:
            status = "At target" if comp.delta_paise == 0 else f"{format_inr(-comp.delta_paise)} left"
            tone, note = "on-track", ""
            target_label = format_inr(comp.budget_paise)

        usage = ""
        if comp.budget_paise and comp.percent_used is not None:
            progress = min(100.0, comp.percent_used)
            usage = (
                f'<div class="budget-usage" role="meter" aria-label="{html.escape(comp.category)} budget used" '
                f'aria-valuemin="0" aria-valuemax="100" aria-valuenow="{progress}" '
                f'aria-valuetext="{comp.percent_used:.1f}% used">'
                f'<div class="budget-progress-track"><div class="budget-progress-fill" style="width:{progress}%"></div></div>'
                f'<span>{comp.percent_used:.0f}% used</span></div>'
            )
        note_html = f'<div class="budget-note">{note}</div>' if note else ""
        st.html(
            f'''<article class="budget-summary {tone}">
                <div class="budget-summary-head"><h3>{html.escape(comp.category)}</h3>
                    <span class="budget-status">{status}</span></div>
                <div class="budget-amounts"><strong>{spent_label}</strong> spent
                    <span aria-hidden="true">·</span> <strong>{target_label}</strong> target</div>
                {usage}{note_html}
            </article>'''
        )


# =============================================================================
# VIEW 4: CATEGORY REVIEW
# =============================================================================
elif st.session_state.active_nav == "Category Review":
    scope_mode = st.session_state.get("review_scope", "All Records")
    month_name = datetime.strptime(st.session_state.selected_month, "%Y-%m").strftime("%B %Y")
    
    if scope_mode == "Current Month":
        pending_txs = db.get_transactions(year_month=st.session_state.selected_month, review_status="needs_review")
        scope_desc = f"Showing unconfirmed expenses for {month_name}"
    else:
        pending_txs = db.get_transactions(review_status="needs_review")
        scope_desc = "Showing unconfirmed expenses across all dates"

    st.subheader("AI Category Review Queue")
    st.caption(f"{scope_desc}. Verify or adjust predicted categories.")

    if not pending_txs:
        st.success("🎉 All transaction categories in this scope are confirmed! Zero items require review.")
        st.html(
            """
            <div style="text-align:center; padding: 40px 10px; color:#747781;">
                <div style="font-size: 32px; margin-bottom: 8px;">✨</div>
                <div style="font-size: 15px; font-weight: 600; color: #191A1F;">Queue is Completely Clear</div>
                <div style="font-size: 12.5px; color: #747781; margin-top: 4px;">
                    When you import new expenses with unfamiliar descriptions, they will appear here for verification.
                </div>
            </div>
            """
        )
    else:
        st.warning(f"**{len(pending_txs)}** transaction(s) require human review or confirmation.")

        cat_options = sorted(ALLOWED_EXPENSE_CATEGORIES)
        for tx in pending_txs:
            with st.container(border=True):
                st.html(f"<strong>{html.escape(tx.description)}</strong>")
                st.caption(f"{tx.date} · {format_inr(tx.amount_paise)} · Saved category: {tx.category or 'Unassigned'}")

                reason = "This record was marked for review. No model reason was recorded."
                if tx.category_source == "model":
                    check = categorizer.predict(tx.description)
                    if not check.is_abstention:
                        reason = f"The current model suggests {check.category}. This record is still awaiting confirmation."
                    elif check.reason.startswith("Unrecognized vocabulary"):
                        reason = "The current model found no words or phrases it recognized from training."
                    elif check.reason == "Empty description":
                        reason = "The current model needs a description to make a suggestion."
                    else:
                        reason = (
                            f"The current model scored its best match at {check.model_score:.4f}, "
                            f"below its {categorizer.confidence_threshold:.2f} cutoff."
                        )
                st.html(f'<div class="review-reason"><strong>Why this needs review</strong><br>{html.escape(reason)}</div>')

                choice_col, confirm_col = st.columns([3, 2], vertical_alignment="bottom")
                with choice_col:
                    chosen_cat = st.selectbox(
                        "Category to save", options=cat_options,
                        index=cat_options.index(tx.category) if tx.category in cat_options else None,
                        key=f"rev_cat_{tx.id}",
                    )
                with confirm_col:
                    if st.button("Confirm category", key=f"btn_confirm_{tx.id}", type="primary",
                                 width="stretch", disabled=chosen_cat is None):
                        db.update_transaction_category(tx.id, chosen_cat, review_status="confirmed", category_source="manual")
                        st.toast(f"Confirmed as {chosen_cat}")
                        st.rerun()


# =============================================================================
# VIEW 5: MODEL EVALUATION & TRANSPARENCY
# =============================================================================
elif st.session_state.active_nav == "Model Evaluation":
    st.caption("We tested the category model on fictional transactions it had never seen during training.")

    eval_json_path = Path("reports/model_evaluation.json")
    if eval_json_path.exists():
        with eval_json_path.open(encoding="utf-8") as report_file:
            report_data = json.load(report_file)

        meta = report_data["metadata"]
        samples = report_data["samples"]
        correct_count = sum(not sample["is_abstention"] and sample["is_correct"] for sample in samples)
        review_count = sum(sample["is_abstention"] for sample in samples)
        classified_count = len(samples) - review_count
        incorrect_count = classified_count - correct_count

        with st.container(key="holdout_explorer"):
            st.subheader(f"What happened in {len(samples)} test transactions?")
            st.html(
                f'''<div class="evaluation-results">
                    <div class="evaluation-result"><strong>{correct_count}</strong>Correctly categorized</div>
                    <div class="evaluation-result"><strong>{review_count}</strong>Asked for human review</div>
                    <div class="evaluation-result"><strong>{incorrect_count}</strong>Wrong category</div>
                </div>'''
            )
            st.caption("When the model cannot make a strong suggestion, it leaves the category for a person to confirm.")

        if samples:
            with st.expander("Explore individual examples"):
                def example_label(index: int) -> str:
                    sample = samples[index]
                    if sample["is_abstention"]:
                        result = "Needs review"
                    else:
                        result = "Correct" if sample["is_correct"] else "Incorrect"
                    return f"{result} · {sample['description']}"

                index = st.selectbox("Choose a test transaction", range(len(samples)), format_func=example_label)
                example = samples[index]
                response = "Asked for human review" if example["is_abstention"] else example["predicted_category"]
                st.write(f"**Correct category** · {example['true_category']}")
                st.write(f"**What the model did** · {response}")
                if example["is_abstention"]:
                    if example["reason"].startswith("Unrecognized vocabulary"):
                        st.caption("The description contained no words or phrases the model recognized.")
                    elif example["reason"].startswith("Low model confidence"):
                        st.caption("The model found a possible category, but the score was too low to use it.")
                    else:
                        st.caption(example["reason"])

        with st.expander("Technical details"):
            st.write(f"TF-IDF + logistic regression trained on {meta['training_samples']} examples.")
            st.write(f"**Overall accuracy** · {correct_count}/{len(samples)} test examples" if samples else "No test examples.")
            st.write(f"**Coverage** · {classified_count}/{len(samples)} classified automatically" if samples else "Coverage unavailable.")
            st.write(
                f"**Accuracy on predictions** · {correct_count}/{classified_count}"
                if classified_count else "Accuracy on predictions is unavailable because the model made no predictions."
            )
            st.caption(f"Decision cutoff: {meta['confidence_threshold']:.2f}. The test data are synthetic.")
            per_category = pd.DataFrame.from_dict(report_data["per_category_metrics"], orient="index")
            st.dataframe(per_category.rename_axis("Category").reset_index(), width="stretch", hide_index=True)
    else:
        st.info("Evaluation report not found. Run `python scripts/evaluate_model.py` to generate it.")
