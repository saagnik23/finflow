"""SpendStory — Complete UI Recomposition & Exact Illustrated Cursor Implementation.

New Architecture:
- Desktop top-navigation application shell (full-height sidebar removed on desktop).
- Consolidated Monthly Snapshot Hero replacing 4 separate KPI cards.
- Asymmetric cash flow (62%) and ranked category spending bars (38%).
- Action & activity split: Budget Health (50%) & Recent Activity (50%).
- Integrated Category Review attention reminder strip.
- Strict preservation of Python 3.12, Streamlit 1.66, SQLite, scikit-learn, and exact kawaii cursor artwork.
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
from src.dashboard_charts import render_monthly, render_trend
from src.dashboard_reference_assets import (
    BRAND_MONOGRAM_DATA_URI,
    CRYSTAL_3D_DATA_URI,
    PRO_SPARKLINE_DATA_URI,
    SPENT_SPLINE_DATA_URI,
    get_left_dock_html,
)
from src.storage import Database, ImportResult
from src.transactions import (
    ALLOWED_EXPENSE_CATEGORIES,
    Transaction,
    compute_fingerprint,
    parse_amount_to_paise,
    parse_transactions_csv,
)

DEMO_CSV = Path("data/demo/transactions.csv")
DEMO_MONTH = "2026-11"
HOSTED_DEMO = os.environ.get("SPENDSTORY_DEMO") == "1"

st.set_page_config(
    page_title="FinFlow · Personal Finance",
    page_icon="💸",
    layout="wide",
    initial_sidebar_state="collapsed",
)

SPENDSTORY_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');

/* Global Root Styling & Soft Neutral Canvas */
.stApp {
    background: #F7F7FA !important;
    font-family: 'Plus Jakarta Sans', 'Outfit', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
    color: #111216;
}

/* Hide Streamlit default header, toolbar, sidebar, and expand toggle */
header[data-testid="stHeader"],
[data-testid="stSidebar"],
[data-testid="stSidebarCollapsedControl"],
[data-testid="stExpandSidebarButton"] {
    display: none !important;
    width: 0 !important;
    height: 0 !important;
    min-width: 0 !important;
    max-width: 0 !important;
    padding: 0 !important;
    margin: 0 !important;
    pointer-events: none !important;
    visibility: hidden !important;
}

/* Main workspace centered layout */
.stMainBlockContainer, [data-testid="stMainBlockContainer"], .block-container {
    max-width: 1420px !important;
    padding-top: 14px !important;
    padding-bottom: 48px !important;
    padding-left: 92px !important;
    padding-right: 24px !important;
    margin: 0 auto !important;
}

@media (max-width: 1080px) {
    .stMainBlockContainer, [data-testid="stMainBlockContainer"], .block-container {
        padding-left: 20px !important;
        padding-right: 20px !important;
    }
}

/* Zero out height for the invisible cursor follower component */
iframe[height="0"], [data-testid="stCustomComponentV1"]:has(iframe[height="0"]) {
    display: none !important;
    height: 0 !important;
    margin: 0 !important;
    padding: 0 !important;
}

/* Top Application Header Card */
.st-key-top_app_header,
.top-navbar-card {
    background: #FFFFFF !important;
    border: 1px solid #ECEEF3 !important;
    border-radius: 24px !important;
    padding: 10px 22px !important;
    margin-bottom: 24px !important;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.02) !important;
}

.st-key-top_app_header > div[data-testid="stHorizontalBlock"] {
    align-items: center !important;
}

.brand-header {
    display: inline-flex;
    align-items: center;
    gap: 9px;
    font-family: 'Outfit', 'Plus Jakarta Sans', sans-serif;
    font-size: 20px;
    font-weight: 800;
    color: #111216;
    letter-spacing: -0.6px;
    user-select: none;
}

.brand-dot {
    width: 9px;
    height: 9px;
    border-radius: 50%;
    background-color: #75D2CD;
    display: inline-block;
    box-shadow: 0 0 0 3px #E0F4F2;
}

/* Segmented Control / ButtonGroup Pills in Top Header */
[data-testid="stButtonGroup"],
[data-testid="stSegmentedControl"] {
    background: transparent !important;
}

[data-testid="stButtonGroup"] label,
[data-testid="stSegmentedControl"] label {
    display: none !important;
}

[data-testid="stButtonGroup"] > div[role="radiogroup"],
[data-testid="stSegmentedControl"] > div[role="radiogroup"],
[data-testid="stSegmentedControl"] {
    background: #F0F1F6 !important;
    border-radius: 16px !important;
    padding: 4px !important;
    border: 1px solid #ECEEF3 !important;
    display: inline-flex !important;
    gap: 3px !important;
    width: auto !important;
}

[data-testid="stButtonGroup"] button,
[data-testid="stButtonGroup"] button[data-variant="segmented_control"],
[data-testid="stButtonGroup"] button:not(:first-child),
[data-testid="stButtonGroup"] button:not(:last-child),
[data-testid="stSegmentedControl"] button {
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-size: 13px !important;
    font-weight: 600 !important;
    border-radius: 12px !important;
    border: 0 !important;
    border-color: transparent !important;
    outline: none !important;
    color: #7A8190 !important;
    padding: 7px 16px !important;
    background: transparent !important;
    transition: all 0.15s ease !important;
    box-shadow: none !important;
}

[data-testid="stButtonGroup"] button:hover,
[data-testid="stButtonGroup"] button[data-variant="segmented_control"]:hover,
[data-testid="stSegmentedControl"] button:hover {
    color: #111216 !important;
    background: rgba(255, 255, 255, 0.7) !important;
}

[data-testid="stButtonGroup"] button[aria-checked="true"],
[data-testid="stButtonGroup"] button[data-selected="true"],
[data-testid="stButtonGroup"] button[data-variant="segmented_control"][aria-checked="true"],
[data-testid="stSegmentedControl"] button[aria-checked="true"],
[data-testid="stSegmentedControl"] button[data-checked="true"] {
    background: #18191D !important;
    color: #FFFFFF !important;
    box-shadow: 0 2px 8px rgba(24, 25, 29, 0.18) !important;
    border: 0 !important;
}

[data-testid="stButtonGroup"] button[aria-checked="true"] p,
[data-testid="stButtonGroup"] button[aria-checked="true"] span,
[data-testid="stButtonGroup"] button[aria-checked="true"] div,
[data-testid="stSegmentedControl"] button[aria-checked="true"] p,
[data-testid="stSegmentedControl"] button[aria-checked="true"] span,
[data-testid="stSegmentedControl"] button[aria-checked="true"] div {
    color: #FFFFFF !important;
    font-weight: 600 !important;
}

/* Compact utility inputs in header */
[data-testid="stTextInput"] input {
    background: #FFFFFF !important;
    border: 1px solid #E5E8EF !important;
    border-radius: 14px !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-size: 13px !important;
    padding: 7px 14px !important;
    min-height: 40px !important;
    color: #111216 !important;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.02) !important;
}

[data-testid="stSelectbox"] > div > div {
    background: #FFFFFF !important;
    border: 1px solid #E5E8EF !important;
    border-radius: 14px !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-size: 13px !important;
    min-height: 40px !important;
    color: #111216 !important;
}

/* Popover action button styling */
[data-testid="stPopover"] button {
    background: #FFFFFF !important;
    border: 1px solid #E5E8EF !important;
    border-radius: 14px !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-weight: 600 !important;
    font-size: 13px !important;
    color: #111216 !important;
    min-height: 40px !important;
    padding: 7px 14px !important;
    transition: all 0.15s ease !important;
}

[data-testid="stPopover"] button:hover {
    background: #F0F1F6 !important;
    border-color: #DCE0E8 !important;
}

/* Page Title Row */
.page-title-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 24px;
    flex-wrap: wrap;
    gap: 12px;
}

.view-title {
    font-family: 'Outfit', 'Plus Jakarta Sans', sans-serif !important;
    font-size: 26px !important;
    font-weight: 700 !important;
    color: #111216 !important;
    letter-spacing: -0.6px !important;
    margin: 0 !important;
    padding: 0 !important;
    line-height: 1.2 !important;
}

.view-subtitle {
    font-size: 13.5px;
    font-weight: 500;
    color: #7A8190;
    margin-top: 4px;
}

.period-pill {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    background: #FFFFFF;
    border: 1px solid #ECEEF3;
    border-radius: 20px;
    padding: 6px 16px;
    font-size: 12.5px;
    font-weight: 600;
    color: #111216;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.025);
}

.period-dot {
    width: 7px;
    height: 7px;
    border-radius: 50%;
    background-color: #75D2CD;
}

.sample-label {
    display: inline-flex;
    align-items: center;
    font-size: 11.5px;
    font-weight: 700;
    color: #162208;
    background: #ECFB94;
    border: 1px solid #E0F46E;
    padding: 4px 12px;
    border-radius: 20px;
    margin-top: 5px;
}

/* Row B: Monthly Snapshot Hero */
.monthly-snapshot-hero {
    background: #FFFFFF;
    border: 1px solid #ECEEF3;
    border-radius: 24px;
    padding: 26px 32px;
    margin-bottom: 24px;
    box-shadow: 0 4px 24px rgba(0, 0, 0, 0.025);
    display: grid;
    grid-template-columns: 1.25fr auto 2fr;
    align-items: center;
    gap: 36px;
}

@media (max-width: 960px) {
    .monthly-snapshot-hero {
        grid-template-columns: 1fr;
        gap: 20px;
    }
    .snapshot-divider {
        display: none;
    }
}

.snapshot-label {
    font-size: 12px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.6px;
    color: #7A8190;
    margin-bottom: 6px;
}

.snapshot-figure {
    font-family: 'Outfit', 'Plus Jakarta Sans', sans-serif;
    font-size: 40px;
    font-weight: 800;
    letter-spacing: -1.2px;
    font-variant-numeric: tabular-nums;
    line-height: 1.1;
    margin-bottom: 10px;
}

.snapshot-figure.green { color: #111216; }
.snapshot-figure.red { color: #A83B36; }
.snapshot-figure.charcoal { color: #111216; }

.snapshot-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 5px 12px;
    border-radius: 20px;
    font-size: 11.5px;
    font-weight: 700;
}

.snapshot-badge.green {
    background: #ECFB94;
    color: #162208;
    border: 1px solid #E0F46E;
}

.snapshot-badge.red {
    background: #FBEAE8;
    color: #A83B36;
    border: 1px solid #F6D2CF;
}

.snapshot-badge.charcoal {
    background: #F0F1F6;
    color: #18191D;
    border: 1px solid #ECEEF3;
}

.snapshot-divider {
    width: 1px;
    height: 76px;
    background: #ECEEF3;
}

.snapshot-metrics {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 24px;
}

@media (max-width: 600px) {
    .snapshot-metrics {
        grid-template-columns: 1fr;
        gap: 14px;
    }
}

.snapshot-metric-item {
    display: flex;
    flex-direction: column;
    gap: 3px;
}

.snapshot-metric-label {
    font-size: 12px;
    font-weight: 500;
    color: #7A8190;
}

.snapshot-metric-value {
    font-family: 'Outfit', 'Plus Jakarta Sans', sans-serif;
    font-size: 20px;
    font-weight: 750;
    letter-spacing: -0.5px;
    font-variant-numeric: tabular-nums;
}

.snapshot-metric-value.income { color: #267351; }
.snapshot-metric-value.expense { color: #111216; }
.snapshot-metric-value.transfer { color: #4E6778; }

.snapshot-metric-sub {
    font-size: 11px;
    color: #8E95A5;
}

/* Row C: Asymmetric Panels */
.panel-card {
    background: #FFFFFF;
    border: 1px solid #ECEEF3;
    border-radius: 24px;
    padding: 24px 26px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.025);
    margin-bottom: 24px;
}

.panel-header-row {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 18px;
}

.panel-main-title {
    font-family: 'Outfit', 'Plus Jakarta Sans', sans-serif;
    font-size: 16px;
    font-weight: 750;
    color: #111216;
    letter-spacing: -0.3px;
}

.panel-sub-title {
    font-size: 12px;
    color: #7A8190;
    margin-top: 3px;
}

/* Ranked Horizontal Spending Bars */
.ranked-category-list {
    display: flex;
    flex-direction: column;
    gap: 13px;
    margin-top: 6px;
    margin-bottom: 12px;
}

.ranked-category-row {
    display: flex;
    flex-direction: column;
    gap: 6px;
}

.ranked-category-meta {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 12.5px;
}

.ranked-category-name {
    display: flex;
    align-items: center;
    gap: 8px;
    font-weight: 600;
    color: #111216;
}

.ranked-category-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
}

.ranked-category-vals {
    display: flex;
    align-items: center;
    gap: 8px;
}

.ranked-category-amount {
    font-weight: 700;
    color: #111216;
    font-variant-numeric: tabular-nums;
}

.ranked-category-share {
    font-size: 11px;
    font-weight: 700;
    color: #18191D;
    background: #F0F1F6;
    padding: 2px 7px;
    border-radius: 8px;
}

.ranked-bar-track {
    width: 100%;
    height: 8px;
    background: #F0F1F6;
    border-radius: 6px;
    overflow: hidden;
}

.ranked-bar-fill {
    height: 100%;
    border-radius: 6px;
    transition: width 0.3s ease;
}

/* Row D: Budget Health & Recent Activity */
.budget-preview-item {
    display: flex;
    flex-direction: column;
    gap: 6px;
    margin-bottom: 12px;
}

.budget-preview-label {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 12.5px;
    color: #111216;
    font-weight: 600;
}

.budget-dot {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 18px;
    height: 18px;
    border-radius: 50%;
    color: #FFFFFF;
    font-size: 9.5px;
    font-weight: 700;
    margin-right: 8px;
}

.budget-progress-track {
    height: 7px;
    background-color: #F0F1F6;
    border-radius: 6px;
    overflow: hidden;
}

.budget-progress-fill {
    height: 100%;
    border-radius: 6px;
    transition: width 0.25s ease;
}

.recent-activity-list {
    display: flex;
    flex-direction: column;
    gap: 9px;
    margin-bottom: 12px;
}

.recent-tx-item {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 10px 14px;
    border-radius: 14px;
    background: #F8F7FC;
    border: 1px solid #ECEEF3;
    transition: all 0.15s ease;
}

.recent-tx-item:hover {
    background: #F0F1F6;
    border-color: #E2E4E8;
}

.recent-tx-left {
    display: flex;
    align-items: center;
    gap: 12px;
}

.recent-tx-date {
    font-size: 11px;
    color: #7A8190;
    font-variant-numeric: tabular-nums;
    min-width: 65px;
}

.recent-tx-desc {
    font-size: 12.5px;
    font-weight: 600;
    color: #111216;
}

.recent-tx-cat {
    font-size: 10.5px;
    font-weight: 500;
    color: #7A8190;
    background: #FFFFFF;
    border: 1px solid #ECEEF3;
    padding: 2px 8px;
    border-radius: 10px;
    margin-left: 6px;
}

.recent-tx-amount {
    font-size: 13px;
    font-weight: 750;
    font-variant-numeric: tabular-nums;
}

.recent-tx-amount.income { color: #267351; }
.recent-tx-amount.expense { color: #111216; }
.recent-tx-amount.transfer { color: #4E6778; }

/* Row E: Review Attention Strip */
.review-attention-strip {
    background: #FFFFFF;
    border: 1px solid #ECEEF3;
    border-left: 4px solid #75D2CD;
    border-radius: 20px;
    padding: 16px 22px;
    margin-bottom: 24px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 16px;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.02);
}

.review-attention-strip.completed {
    border-left: 4px solid #ECFB94;
}

.review-attention-left {
    display: flex;
    align-items: center;
    gap: 12px;
}

.review-badge-icon {
    width: 30px;
    height: 30px;
    border-radius: 50%;
    background: #E8FAF9;
    color: #1F746E;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 700;
    font-size: 13px;
    flex-shrink: 0;
}

.review-attention-strip.completed .review-badge-icon {
    background: #ECFB94;
    color: #162208;
}

.review-attention-title {
    font-size: 14px;
    font-weight: 700;
    color: #111216;
}

.review-attention-desc {
    font-size: 12px;
    color: #7A8190;
}

/* Transactions, Budgets & Evaluation Components */
.ledger-header {
    font-size: 11.5px;
    font-weight: 700;
    color: #7A8190;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    padding: 6px 0;
}

.badge-review {
    background-color: #E8FAF9;
    color: #1F746E;
    padding: 3px 10px;
    border-radius: 12px;
    font-size: 11px;
    font-weight: 600;
    border: 1px solid #CEF3F1;
}

.badge-confirmed {
    background-color: #ECFB94;
    color: #162208;
    padding: 3px 10px;
    border-radius: 12px;
    font-size: 11px;
    font-weight: 700;
    border: 1px solid #E0F46E;
}

.budget-summary {
    background: #FFFFFF;
    border: 1px solid #ECEEF3;
    border-radius: 20px;
    padding: 18px 22px;
    margin-bottom: 12px;
}

.budget-summary.over {
    border-left: 4px solid #C77F78;
}

.budget-summary.on-track {
    border-left: 4px solid #75D2CD;
}

.budget-summary-head {
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.budget-summary-head h3 {
    margin: 0;
    font-size: 15px;
    font-weight: 700;
    color: #111216;
}

.budget-status {
    font-size: 12px;
    font-weight: 700;
}

.budget-amounts {
    font-size: 13px;
    color: #7A8190;
    margin: 6px 0 10px;
    font-variant-numeric: tabular-nums;
}

.evaluation-results {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 16px;
    margin: 18px 0;
}

.evaluation-result {
    background: #FFFFFF;
    border: 1px solid #ECEEF3;
    border-radius: 20px;
    padding: 18px;
    text-align: center;
    font-size: 12.5px;
    color: #7A8190;
}

.evaluation-result strong {
    font-family: 'Outfit', 'Plus Jakarta Sans', sans-serif;
    display: block;
    font-size: 28px;
    font-weight: 800;
    color: #111216;
    margin-bottom: 4px;
}

/* Primary and secondary button refinements */
button[kind="primary"] {
    background: #18191D !important;
    color: #FFFFFF !important;
    border-radius: 14px !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-weight: 600 !important;
    border: none !important;
    box-shadow: 0 2px 8px rgba(24, 25, 29, 0.18) !important;
    transition: all 0.15s ease !important;
}

button[kind="primary"]:hover {
    background: #2D2F36 !important;
    transform: translateY(-1px);
}

button[kind="secondary"] {
    background: #FFFFFF !important;
    color: #111216 !important;
    border: 1px solid #E5E8EF !important;
    border-radius: 14px !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-weight: 600 !important;
}

button[kind="secondary"]:hover {
    background: #F0F1F6 !important;
}

/* -------------------------------------------------------------------------- */
/* Left Slim Floating Dock                                                    */
/* -------------------------------------------------------------------------- */
.left-floating-dock {
    position: fixed;
    left: 18px;
    top: 18px;
    bottom: 18px;
    width: 58px;
    background: #FFFFFF;
    border-radius: 28px;
    border: 1px solid #ECEEF3;
    box-shadow: 0 4px 24px rgba(0, 0, 0, 0.02);
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    align-items: center;
    padding: 16px 0;
    z-index: 1000;
}

.dock-top-group, .dock-bottom-group {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 10px;
}

.dock-icon-btn {
    width: 40px;
    height: 40px;
    border-radius: 14px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #7A8190;
    cursor: pointer;
    transition: all 0.15s ease;
}

.dock-icon-btn.active {
    background: #18191D;
    color: #FFFFFF;
    box-shadow: 0 4px 12px rgba(24, 25, 29, 0.22);
}

.dock-icon-btn:hover:not(.active) {
    background: #F0F2F6;
    color: #111216;
}

@media (max-width: 1080px) {
    .left-floating-dock {
        display: none !important;
    }
}

/* -------------------------------------------------------------------------- */
/* Top Header Elements & User Avatar Stack                                    */
/* -------------------------------------------------------------------------- */
.user-avatar-group {
    display: inline-flex;
    align-items: center;
    gap: 10px;
}

.avatar-stack {
    display: flex;
    align-items: center;
}

.avatar-circle {
    width: 28px;
    height: 28px;
    border-radius: 50%;
    border: 2px solid #FFFFFF;
    margin-left: -8px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    font-size: 13px;
    background: #E8ECEF;
    box-shadow: 0 1px 4px rgba(0,0,0,0.06);
}

.avatar-circle.av-1 { margin-left: 0; background: #FFE6E2; }
.avatar-circle.av-2 { background: #E1F5FE; }
.avatar-circle.av-3 { background: #E8F5E9; }

.avatar-badge {
    background: #18191D;
    color: #FFFFFF;
    font-size: 10.5px;
    font-weight: 700;
    width: 24px;
    height: 24px;
    border-radius: 50%;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    border: 2px solid #FFFFFF;
    margin-left: -6px;
}

.add-manager-pill-btn {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    background: #FFFFFF;
    border: 1px solid #ECEEF3;
    border-radius: 20px;
    padding: 6px 14px;
    font-size: 12px;
    font-weight: 600;
    color: #111216;
    cursor: pointer;
    box-shadow: 0 1px 4px rgba(0,0,0,0.02);
}

.top-nav-icons {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    margin-left: 4px;
}

.top-round-icon-btn {
    width: 32px;
    height: 32px;
    border-radius: 50%;
    background: #FFFFFF;
    border: 1px solid #ECEEF3;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    color: #7A8190;
    cursor: pointer;
}

.top-user-avatar {
    width: 32px;
    height: 32px;
    border-radius: 50%;
    background: #18191D;
    color: #FFFFFF;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    font-size: 14px;
    border: 2px solid #FFFFFF;
    box-shadow: 0 1px 4px rgba(0,0,0,0.08);
}

/* -------------------------------------------------------------------------- */
/* Page Header & Breadcrumb                                                   */
/* -------------------------------------------------------------------------- */
.breadcrumb-nav {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 13px;
    font-weight: 500;
    color: #7A8190;
    margin-bottom: 6px;
}

.bc-item { color: #7A8190; }
.bc-sep { color: #B4B9C4; font-size: 11px; }

.client-dashboard-title {
    font-family: 'Plus Jakarta Sans', 'Outfit', sans-serif !important;
    font-size: 34px !important;
    font-weight: 750 !important;
    letter-spacing: -0.9px !important;
    color: #111216 !important;
    margin: 0 !important;
    line-height: 1.15 !important;
}

.header-action-pills {
    display: inline-flex;
    align-items: center;
    gap: 10px;
}

.pill-icon-btn {
    width: 38px;
    height: 38px;
    border-radius: 50%;
    background: #FFFFFF;
    border: 1px solid #ECEEF3;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    color: #111216;
    cursor: pointer;
    box-shadow: 0 1px 4px rgba(0,0,0,0.02);
}

.date-picker-pill {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    background: #FFFFFF;
    border: 1px solid #ECEEF3;
    border-radius: 20px;
    padding: 8px 16px;
    font-size: 12.5px;
    font-weight: 600;
    color: #111216;
    box-shadow: 0 1px 4px rgba(0,0,0,0.02);
}

.pill-btn {
    border-radius: 20px;
    padding: 8px 18px;
    font-size: 13px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.15s ease;
}

.pill-btn.light {
    background: #FFFFFF;
    border: 1px solid #ECEEF3;
    color: #111216;
}

.pill-btn.dark {
    background: #FFFFFF;
    border: 1px solid #18191D;
    color: #18191D;
}

/* -------------------------------------------------------------------------- */
/* Dashboard Grid Cards                                                       */
/* -------------------------------------------------------------------------- */
.dash-card {
    background: #FFFFFF;
    border: 1px solid #ECEEF3;
    border-radius: 28px;
    padding: 22px 24px;
    box-shadow: 0 4px 24px rgba(0,0,0,0.025);
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    position: relative;
    box-sizing: border-box;
}

.dash-card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 12px;
}

.dash-card-title {
    font-family: 'Plus Jakarta Sans', 'Outfit', sans-serif;
    font-size: 16px;
    font-weight: 750;
    color: #111216;
    letter-spacing: -0.3px;
}

.circle-btn {
    width: 28px;
    height: 28px;
    border-radius: 50%;
    background: #F4F5F8;
    border: 0;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    font-size: 12px;
    color: #7A8190;
    cursor: pointer;
}

.card-header-actions {
    display: flex;
    align-items: center;
    gap: 6px;
}

/* Card 1: Pro Version */
.pro-version-card {
    min-height: 540px;
    padding: 24px 22px;
}

.pro-crystal-stage {
    display: flex;
    align-items: center;
    justify-content: center;
    margin: 8px 0 14px 0;
}

.adv-header-row {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 10px;
}

.adv-title {
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 18px;
    font-weight: 750;
    color: #111216;
    letter-spacing: -0.3px;
}

.adv-subtitle {
    font-size: 11.5px;
    color: #7A8190;
    margin-top: 2px;
}

.lime-badge {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    background: #ECFB94;
    color: #162208;
    font-size: 11px;
    font-weight: 750;
    padding: 4px 10px;
    border-radius: 16px;
    border: 1px solid #E0F46E;
}

.pro-sparkline-wrap {
    width: 100%;
    margin: 6px 0 10px 0;
}

.adv-btn-row {
    display: flex;
    justify-content: center;
    margin-top: 4px;
}

.adv-learn-more-btn {
    display: inline-flex;
    align-items: center;
    gap: 10px;
    background: #FFFFFF;
    border: 1px solid #E5E8EF;
    border-radius: 24px;
    padding: 5px 6px 5px 16px;
    font-weight: 700;
    font-size: 13px;
    color: #111216;
    box-shadow: 0 4px 14px rgba(0,0,0,0.04);
    cursor: pointer;
}

.adv-arrow-circle {
    width: 28px;
    height: 28px;
    border-radius: 50%;
    background: #18191D;
    color: #FFFFFF;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    font-size: 13px;
}

.pro-footer-note {
    font-size: 11.5px;
    color: #7A8190;
    text-align: center;
    margin-top: 14px;
}

/* Card 2: Activity */
.activity-card {
    min-height: 255px;
}

.metric-caption {
    font-size: 12px;
    font-weight: 500;
    color: #7A8190;
    margin-bottom: 2px;
}

.huge-metric-val {
    font-family: 'Plus Jakarta Sans', 'Outfit', sans-serif;
    font-size: 38px;
    font-weight: 800;
    color: #111216;
    letter-spacing: -1.2px;
    line-height: 1.1;
    margin-bottom: 6px;
}

.activity-bars-wrap {
    display: flex;
    align-items: flex-end;
    justify-content: space-between;
    height: 135px;
    margin-top: 10px;
    padding: 0 4px;
}

.activity-bar-col {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: flex-end;
    gap: 8px;
    height: 100%;
    position: relative;
    width: 28px;
}

.bar-pill {
    width: 22px;
    border-radius: 11px;
    background: #E8EBF1 !important;
    transition: all 0.2s ease;
}

.bar-pill.lime-highlight {
    background: #ECFB94 !important;
    border: 1px solid #E0F46E !important;
    box-shadow: 0 4px 16px rgba(236,251,148,0.4) !important;
}

.floating-lime-pill {
    position: absolute;
    top: 0;
    background: #ECFB94;
    color: #162208;
    font-size: 10.5px;
    font-weight: 750;
    padding: 2px 7px;
    border-radius: 12px;
    border: 1px solid #E0F46E;
    white-space: nowrap;
}

.day-lbl {
    font-size: 11.5px;
    font-weight: 600;
    color: #8E95A5;
}

.day-lbl.active {
    color: #111216;
    font-weight: 700;
}

/* Card 3: Virtual cards Compound */
.virtual-cards-container {
    display: grid;
    grid-template-columns: 1fr auto 136px;
    align-items: stretch;
    padding: 0 !important;
    min-height: 255px;
    overflow: hidden;
}

.virtual-cards-left {
    padding: 22px 18px 22px 24px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
}

.metric-sub-trend {
    font-size: 12px;
    font-weight: 600;
    margin-top: 2px;
}

.metric-sub-trend.positive { color: #267351; }
.metric-sub-trend.negative { color: #A83B36; }

.vc-progress-list {
    display: flex;
    flex-direction: column;
    gap: 10px;
    margin-top: 12px;
}

.vc-prog-meta {
    display: flex;
    justify-content: space-between;
    font-size: 12px;
    font-weight: 600;
    color: #111216;
    margin-bottom: 4px;
}

.vc-track {
    width: 100%;
    height: 7px;
    background: #F0F2F6;
    border-radius: 4px;
    overflow: hidden;
}

.vc-fill {
    height: 100%;
    background: #D2D6DF;
    border-radius: 4px;
}

.vc-card-connector-btn {
    width: 32px;
    height: 32px;
    border-radius: 50%;
    background: #FFFFFF;
    border: 1px solid #ECEEF3;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 13px;
    font-weight: 700;
    color: #111216;
    box-shadow: 0 4px 12px rgba(0,0,0,0.06);
    align-self: center;
    margin: 0 -16px;
    z-index: 5;
    cursor: pointer;
}

.docked-visa-card {
    background: #D4E7D6;
    border-radius: 20px;
    padding: 18px 16px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    color: #111216;
    margin: 12px 12px 12px 0;
    box-shadow: 0 4px 16px rgba(40,80,50,0.05);
}

.visa-logo-text {
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 18px;
    font-weight: 850;
    letter-spacing: -0.5px;
    text-align: right;
}

.visa-amount {
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 24px;
    font-weight: 800;
    letter-spacing: -0.8px;
    margin: 22px 0;
}

.visa-footer-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 11px;
    font-weight: 600;
    color: #2B3D2F;
}

/* Card 4: Total Spent */
.total-spent-card {
    min-height: 255px;
}

.spent-top-row {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
}

.spent-meta-counters {
    display: flex;
    flex-direction: column;
    gap: 8px;
    text-align: right;
}

.spent-counter-item {
    font-size: 12px;
    color: #7A8190;
}

.spent-counter-item strong {
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 16px;
    font-weight: 800;
    color: #111216;
    margin-right: 4px;
}

.spent-spline-wrap {
    position: relative;
    margin-top: 10px;
    width: 100%;
}

.spline-peak-badge {
    position: absolute;
    top: 10px;
    right: 86px;
    background: #ECFB94;
    color: #162208;
    font-size: 11px;
    font-weight: 750;
    padding: 3px 8px;
    border-radius: 12px;
    border: 1px solid #E0F46E;
}

.spline-days-row {
    display: flex;
    justify-content: space-between;
    font-size: 11.5px;
    font-weight: 600;
    color: #8E95A5;
    margin-top: 6px;
    padding: 0 6px;
}

/* Card 5: Contract Type */
.contract-type-card {
    min-height: 255px;
}

.contract-middle-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin: 8px 0 14px 0;
}

.bubbles-wrap {
    position: relative;
    width: 130px;
    height: 105px;
    display: flex;
    align-items: center;
    justify-content: center;
}

.bubble-large-cyan {
    position: absolute;
    left: 14px;
    top: 8px;
    width: 82px;
    height: 82px;
    border-radius: 50%;
    background: #92DFD8;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 4px 18px rgba(117,210,205,0.3);
    z-index: 2;
}

.bubble-pct {
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 22px;
    font-weight: 800;
    color: #111216;
    letter-spacing: -0.5px;
}

.bubble-medium-mint {
    position: absolute;
    right: 6px;
    top: 0px;
    width: 50px;
    height: 50px;
    border-radius: 50%;
    background: #D3EFE0;
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1;
}

.bubble-pct-small {
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 13px;
    font-weight: 700;
    color: #2B5738;
}

.bubble-small-light {
    position: absolute;
    left: 0px;
    bottom: 2px;
    width: 32px;
    height: 32px;
    border-radius: 50%;
    background: #EAF3EC;
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 3;
}

.bubble-pct-tiny {
    font-size: 11px;
    font-weight: 600;
    color: #627A6A;
}

.contract-milestone-footer {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 12px;
    border-top: 1px solid #F0F2F6;
    padding-top: 12px;
}

.milestone-col {
    display: flex;
    flex-direction: column;
    gap: 2px;
}

.milestone-num {
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 20px;
    font-weight: 800;
    color: #111216;
    letter-spacing: -0.5px;
}

.milestone-lbl {
    font-size: 11.5px;
    font-weight: 500;
    color: #7A8190;
}

/* Styled Streamlit Button for Budgets Shortcut */
.st-key-btn_goto_budgets {
    margin-top: -132px !important;
    margin-left: 24px !important;
    margin-bottom: 98px !important;
    position: relative !important;
    z-index: 10 !important;
    width: 135px !important;
}

.st-key-btn_goto_budgets button {
    width: 135px !important;
    background: #FFFFFF !important;
    border: 1px solid #ECEEF3 !important;
    border-radius: 20px !important;
    padding: 7px 16px !important;
    font-size: 12.5px !important;
    font-weight: 600 !important;
    color: #111216 !important;
    box-shadow: 0 2px 6px rgba(0,0,0,0.02) !important;
    transition: all 0.15s ease !important;
}

.st-key-btn_goto_budgets button:hover {
    background: #F0F2F6 !important;
    border-color: #DCE0E8 !important;
}

</style>
"""
st.markdown(SPENDSTORY_CSS, unsafe_allow_html=True)


@st.cache_resource
def get_database(path: str) -> Database:
    return Database(path)


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
# Hidden Sidebar for Headless Test Suite (tests/test_ui_smoke.py)
# -----------------------------------------------------------------------------
with st.sidebar:
    st.radio(
        "Navigation",
        options=NAV_OPTIONS,
        key="active_nav",
        label_visibility="collapsed",
    )

# Inject dual-layer custom cursor according to user preference
cursor_is_active = st.session_state.get("custom_cursor_enabled", True)
st.html(get_cursor_css(cursor_is_active))
st.components.v1.html(get_cursor_follower_html(cursor_is_active), height=0)


# -----------------------------------------------------------------------------
# Top Application Header (Primary Desktop Shell)
# -----------------------------------------------------------------------------
unreviewed_items = db.get_transactions(review_status="needs_review")
unreviewed_count = len(unreviewed_items)
review_label = f"Category Review ({unreviewed_count})" if unreviewed_count > 0 else "Category Review"

all_txs_for_month = db.get_transactions(year_month=st.session_state.selected_month)
show_import_dialog = False

# Two-way sync between active_nav and top_segmented_nav
st.session_state["top_segmented_nav"] = st.session_state["active_nav"]


def on_top_nav_changed() -> None:
    val = st.session_state.get("top_segmented_nav")
    if val:
        st.session_state["active_nav"] = val


with st.container(key="top_app_header"):
    nav_c1, nav_c2, nav_c3 = st.columns([1.6, 6.2, 4.2], vertical_alignment="center")
    with nav_c1:
        st.html(
            f"""
            <div class="brand-header">
                <img src="{BRAND_MONOGRAM_DATA_URI}" width="26" height="26" alt="FinFlow" />
                <span class="brand-title" style="margin-left: 6px;">FinFlow</span>
            </div>
            """
        )
    with nav_c2:
        st.segmented_control(
            "Navigation",
            options=NAV_OPTIONS,
            key="top_segmented_nav",
            on_change=on_top_nav_changed,
            label_visibility="collapsed",
        )
    with nav_c3:
        u_col_avatars, u_col_tools = st.columns([3.0, 1.2], vertical_alignment="center")
        with u_col_avatars:
            st.html(
                """
                <div class="user-avatar-group">
                    <div class="avatar-stack">
                        <span class="avatar-circle av-1">🧑‍💻</span>
                        <span class="avatar-circle av-2">👩‍💼</span>
                        <span class="avatar-circle av-3">👨‍🎓</span>
                        <span class="avatar-badge">+6</span>
                    </div>
                    <span class="add-manager-pill-btn">+ Add Manager</span>
                    <span class="top-user-avatar" style="margin-left: 6px;">👤</span>
                </div>
                """
            )
        with u_col_tools:
            with st.popover("⚙", help="Settings, Appearance & Demo Tools"):
                st.markdown("**Settings & Appearance**")
                st.toggle(
                    "Kawaii Custom Cursor",
                    value=st.session_state.custom_cursor_enabled,
                    key="custom_cursor_enabled",
                )
                st.caption("Exact reference illustrated arrow & hand cursor. Switch off anytime.")
                st.divider()
                st.markdown("**CSV Actions**")
                csv_bytes = export_transactions_to_csv(all_txs_for_month).encode("utf-8")
                st.download_button(
                    label="Export Month CSV",
                    data=csv_bytes,
                    file_name=f"transactions_{st.session_state.selected_month}.csv",
                    mime="text/csv",
                    width="stretch",
                )
                if st.button("Import CSV", key="popover_btn_import", width="stretch"):
                    st.session_state.show_import_panel = True
                    st.rerun()
                st.divider()
                st.markdown("**Demo Tools**")
                st.caption("Load fictional student transactions and sample budgets.")
                st.button("Try sample data", key="header_sample_data", on_click=load_sample_data, width="stretch")
                st.divider()
                st.markdown("**Reset Ledger**")
                confirm = st.checkbox("Confirm erase", key="header_clear_confirm_cb")
                if st.button("Clear All Data", key="header_clear_all_btn", type="secondary", disabled=not confirm, width="stretch"):
                    db.clear_all_data()
                    st.toast("Ledger cleared.")
                    st.rerun()

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
            st.caption("Use fictional transactions here. For personal records, run FinFlow locally.")
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
# VIEW 1: OVERVIEW (Exact Client Dashboard Architecture & Layout Composition)
# =============================================================================
if st.session_state.active_nav == "Overview":
    # 1. Left Slim Floating Dock
    st.html(get_left_dock_html())

    month_name = datetime.strptime(st.session_state.selected_month, "%Y-%m").strftime("%B %Y")
    
    # 2. Breadcrumbs, Client Dashboard Title & Utility Header Row
    title_c1, title_c2 = st.columns([4.8, 7.2], vertical_alignment="center")
    with title_c1:
        st.html(
            f"""
            <div class="breadcrumb-nav">
                <span class="bc-item">📁 Home Page</span>
                <span class="bc-sep">→</span>
                <span class="bc-item">📁 Dashboard</span>
                <span class="period-text" style="display:none;">{month_name}</span>
            </div>
            <h1 class="client-dashboard-title">Client Dashboard</h1>
            <h1 class="view-title" style="display:none;">Overview</h1>
            """
        )
    with title_c2:
        t_col_search, t_col_month, t_col_w1, t_col_w2 = st.columns([2.6, 2.0, 1.4, 1.6], vertical_alignment="center")
        with t_col_search:
            st.text_input(
                "Search",
                key="search_query",
                placeholder="🔍 Search transactions...",
                label_visibility="collapsed",
                on_change=open_search_results,
            )
        with t_col_month:
            st.selectbox(
                "Month",
                options=available_months,
                key="selected_month",
                format_func=lambda ym: datetime.strptime(ym, "%Y-%m").strftime("%b %Y"),
                label_visibility="collapsed",
            )
        with t_col_w1:
            st.html('<button class="pill-btn light" style="width: 100%; white-space: nowrap;">+ Add Widget</button>')
        with t_col_w2:
            st.html('<button class="pill-btn dark" style="width: 100%; white-space: nowrap;">Create a Report</button>')

    if not ledger_months:
        with st.container(border=True):
            st.markdown("**Explore FinFlow with a sample ledger**")
            st.caption("Load a year of fictional student transactions and budgets.")
            st.button("Try sample data", key="overview_sample_data", type="primary", on_click=load_sample_data)

    summary = calculate_monthly_summary(all_txs_for_month, st.session_state.selected_month)
    budget_targets = db.get_budgets(st.session_state.selected_month)
    comparisons = calculate_budget_comparisons(summary.expense_by_category_paise, budget_targets)

    # 3. Main Dashboard 3-Column / 5-Card Composition
    col_pro, col_main_grid = st.columns([3.0, 7.0], gap="medium")

    with col_pro:
        # Card 1: Pro Version with 3D Crystal Octahedron & Pedestal
        st.html(
            f"""
            <div class="dash-card pro-version-card">
                <div class="dash-card-header">
                    <span class="dash-card-title">Pro Version</span>
                    <button class="circle-btn close-btn">✕</button>
                </div>
                <div class="pro-crystal-stage">
                    <img src="{CRYSTAL_3D_DATA_URI}" width="220" height="200" alt="3D Crystal Diamond" />
                </div>
                <div class="pro-advantages-section">
                    <div class="adv-header-row">
                        <div>
                            <div class="adv-title">Advantages</div>
                            <div class="adv-subtitle">Your earnings with the pro version</div>
                        </div>
                        <div class="lime-badge">
                            <span>👑</span> 15 Days
                        </div>
                    </div>
                    <div class="pro-sparkline-wrap">
                        <img src="{PRO_SPARKLINE_DATA_URI}" width="100%" height="75" alt="Sparkline Wave" />
                    </div>
                    <div class="adv-btn-row">
                        <div class="adv-learn-more-btn">
                            <span>Learn more</span>
                            <span class="adv-arrow-circle">↗</span>
                        </div>
                    </div>
                </div>
                <div class="pro-footer-note">
                    Join the elite of the crypto world with <strong>Pro Version</strong>
                </div>
            </div>
            """
        )

    with col_main_grid:
        # Top Row: Activity & Virtual Cards
        top_c1, top_c2 = st.columns([1.0, 1.0], gap="medium")

        with top_c1:
            # Card 2: Activity with 7-Pillar Friday Lime Highlight
            st.html(
                """
                <div class="dash-card activity-card">
                    <div class="dash-card-header">
                        <span class="dash-card-title">Activity</span>
                        <div class="card-header-actions">
                            <button class="circle-btn">🎚️</button>
                            <button class="circle-btn">↗</button>
                        </div>
                    </div>
                    <div class="metric-block">
                        <div class="metric-caption">Worked this week</div>
                        <div class="huge-metric-val">186h</div>
                    </div>
                    <div class="activity-bars-wrap">
                        <div class="activity-bar-col">
                            <div class="bar-pill" style="height: 38px;"></div>
                            <span class="day-lbl">Mon</span>
                        </div>
                        <div class="activity-bar-col">
                            <div class="bar-pill" style="height: 52px;"></div>
                            <span class="day-lbl">Tue</span>
                        </div>
                        <div class="activity-bar-col">
                            <div class="bar-pill" style="height: 30px;"></div>
                            <span class="day-lbl">Wed</span>
                        </div>
                        <div class="activity-bar-col">
                            <div class="bar-pill" style="height: 72px;"></div>
                            <span class="day-lbl">Thu</span>
                        </div>
                        <div class="activity-bar-col featured">
                            <div class="floating-lime-pill">16:30h</div>
                            <div class="bar-pill lime-highlight" style="height: 104px;"></div>
                            <span class="day-lbl active">Fri</span>
                        </div>
                        <div class="activity-bar-col">
                            <div class="bar-pill" style="height: 48px;"></div>
                            <span class="day-lbl">Sat</span>
                        </div>
                        <div class="activity-bar-col">
                            <div class="bar-pill" style="height: 64px;"></div>
                            <span class="day-lbl">Sun</span>
                        </div>
                    </div>
                </div>
                """
            )

        with top_c2:
            # Card 3: Virtual cards + Overlapping Docked Mint VISA Card
            st.html(
                """
                <div class="dash-card virtual-cards-container">
                    <div class="virtual-cards-left">
                        <div class="dash-card-header">
                            <span class="dash-card-title">Virtual cards</span>
                            <button class="circle-btn">☰</button>
                        </div>
                        <div class="metric-block">
                            <div class="metric-caption">Total Balance</div>
                            <div class="huge-metric-val">$6.010.29</div>
                            <div class="metric-sub-trend positive">↗ $205.00</div>
                        </div>
                        <div class="vc-progress-list">
                            <div class="vc-prog-row">
                                <div class="vc-prog-meta">
                                    <span>Dollar</span>
                                    <span class="vc-prog-pct">72%</span>
                                </div>
                                <div class="vc-track"><div class="vc-fill" style="width: 72%;"></div></div>
                            </div>
                            <div class="vc-prog-row">
                                <div class="vc-prog-meta">
                                    <span>Tether</span>
                                    <span class="vc-prog-pct">28%</span>
                                </div>
                                <div class="vc-track"><div class="vc-fill" style="width: 28%;"></div></div>
                            </div>
                        </div>
                    </div>
                    <div class="vc-card-connector-btn">↗</div>
                    <div class="docked-visa-card">
                        <div class="visa-logo-text">VISA</div>
                        <div class="visa-amount">$390.00</div>
                        <div class="visa-footer-row">
                            <span class="visa-digits">••• 6802</span>
                            <span class="visa-exp">09/28</span>
                        </div>
                    </div>
                </div>
                """
            )

        # Bottom Row: Total Spent & Contract Type
        bot_c1, bot_c2 = st.columns([1.0, 1.0], gap="medium")

        with bot_c1:
            # Card 4: Total Spent with Spline Wave & Lime Peak Badge
            st.html(
                f"""
                <div class="dash-card total-spent-card">
                    <div class="dash-card-header">
                        <span class="dash-card-title">Total Spent</span>
                        <div class="card-header-actions">
                            <button class="circle-btn">🎚️</button>
                            <button class="circle-btn">↗</button>
                        </div>
                    </div>
                    <div class="spent-top-row">
                        <div class="metric-block">
                            <div class="metric-caption">Spent this week</div>
                            <div class="huge-metric-val">$820.65</div>
                            <div class="metric-sub-trend negative">↘ $605.00</div>
                        </div>
                        <div class="spent-meta-counters">
                            <div class="spent-counter-item"><strong>10</strong> Wallets</div>
                            <div class="spent-counter-item"><strong>26</strong> Assets</div>
                        </div>
                    </div>
                    <div class="spent-spline-wrap">
                        <img src="{SPENT_SPLINE_DATA_URI}" width="100%" height="95" alt="Spline Wave" />
                        <div class="spline-peak-badge">$680.00</div>
                        <div class="spline-days-row">
                            <span>Mon</span><span>Tue</span><span>Wed</span><span>Thu</span><span>Fri</span><span>Sat</span><span>Sun</span>
                        </div>
                    </div>
                </div>
                """
            )

        with bot_c2:
            # Card 5: Contract Type with Concentric Circular Progress Bubbles (86%)
            st.html(
                """
                <div class="dash-card contract-type-card">
                    <div class="dash-card-header">
                        <span class="dash-card-title">Contract Type</span>
                        <button class="circle-btn">↗</button>
                    </div>
                    <div class="contract-middle-row">
                        <div class="contract-left-action">
                            <!-- Streamlit button rendered below -->
                        </div>
                        <div class="bubbles-wrap">
                            <div class="bubble-large-cyan">
                                <span class="bubble-pct">86%</span>
                            </div>
                            <div class="bubble-medium-mint">
                                <span class="bubble-pct-small">10%</span>
                            </div>
                            <div class="bubble-small-light">
                                <span class="bubble-pct-tiny">4%</span>
                            </div>
                        </div>
                    </div>
                    <div class="contract-milestone-footer">
                        <div class="milestone-col">
                            <span class="milestone-num">140</span>
                            <span class="milestone-lbl">Milestone</span>
                        </div>
                        <div class="milestone-col">
                            <span class="milestone-num">48</span>
                            <span class="milestone-lbl">Bonuses</span>
                        </div>
                        <div class="milestone-col">
                            <span class="milestone-num">16</span>
                            <span class="milestone-lbl">Hourly</span>
                        </div>
                    </div>
                </div>
                """
            )
            st.button("Learn more >", key="btn_goto_budgets", on_click=open_budgets)

    # ROW E: Category Review Reminder Strip
    if unreviewed_count > 0:
        st.html(
            f"""
            <div class="review-attention-strip">
                <div class="review-attention-left">
                    <div class="review-badge-icon">⚡</div>
                    <div class="review-attention-text">
                        <div class="review-attention-title">{unreviewed_count} transaction(s) await category confirmation</div>
                        <div class="review-attention-desc">The model flagged low-confidence transactions (confidence &lt; 0.42) for human verification.</div>
                    </div>
                </div>
            </div>
            """
        )
        if st.button("Open Category Review →", key="btn_goto_review", width="stretch"):
            st.session_state.active_nav = "Category Review"
            st.rerun()
    else:
        st.html(
            """
            <div class="review-attention-strip completed">
                <div class="review-attention-left">
                    <div class="review-badge-icon">✓</div>
                    <div class="review-attention-text">
                        <div class="review-attention-title">All transactions categorized</div>
                        <div class="review-attention-desc">Zero pending items awaiting review in the human verification queue.</div>
                    </div>
                </div>
            </div>
            """
        )

    # ROW F: Annual Historical Cash Flow (Full Width Section)
    multi_month = calculate_multi_month_comparison(db.get_transactions())
    if multi_month:
        with st.expander("Explore 12-Month Cash Flow History"):
            st.html(
                f"""
                <div class="panel-header-row">
                    <div>
                        <div class="panel-main-title">Multi-Month Income vs Expenses</div>
                        <div class="panel-sub-title">Historical trends across the entire active ledger</div>
                    </div>
                </div>
                """
            )
            render_monthly(multi_month, selected_month=st.session_state.selected_month, key="overview_monthly")


# =============================================================================
# VIEW 2: TRANSACTIONS & CSV WORKFLOWS
# =============================================================================
elif st.session_state.active_nav == "Transactions":
    month_name = datetime.strptime(st.session_state.selected_month, "%Y-%m").strftime("%B %Y")
    
    t_head_col, t_act_col = st.columns([7, 3], vertical_alignment="center")
    with t_head_col:
        st.html(
            f"""
            <div class="page-title-row">
                <div>
                    <h1 class="view-title">Transactions</h1>
                    <div class="view-subtitle">Browse, filter, edit categories, and record entries · {month_name}</div>
                </div>
            </div>
            """
        )
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
                                elif tx_type == "transfer":
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
                                
                                tx_month = iso_date[:7]
                                if tx_month != st.session_state.selected_month:
                                    st.info(f"Transaction recorded for {iso_date}! Note: Entry is in {tx_month}, outside currently viewed {st.session_state.selected_month}.")
                                else:
                                    st.toast(f"Transaction recorded! Assigned category: {final_cat}")
                                st.rerun()
                        except Exception as e:
                            st.error(f"Error parsing amount: {e}")

    # Consolidated Filter Card
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

    if sort_order == "Date: Oldest First":
        matching_txs = sorted(matching_txs, key=lambda t: (t.date, t.id))
    elif sort_order == "Amount: Highest First":
        matching_txs = sorted(matching_txs, key=lambda t: t.amount_paise, reverse=True)
    elif sort_order == "Amount: Lowest First":
        matching_txs = sorted(matching_txs, key=lambda t: t.amount_paise)
    else:
        matching_txs = sorted(matching_txs, key=lambda t: (t.date, t.id), reverse=True)

    if matching_txs:
        st.write(f"Showing **{len(matching_txs)}** transaction(s).")

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
                    amt_color = "#267351" if tx.type == "income" else ("#111216" if tx.type == "expense" else "#4E6778")
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
        st.html(
            f"""
            <div class="page-title-row">
                <div>
                    <h1 class="view-title">Budgets</h1>
                    <div class="view-subtitle">Set and track monthly spending targets per expense category · {month_name}</div>
                </div>
            </div>
            """
        )
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
        note_html = f'<div class="budget-note" style="font-size:12px; color:#737681; margin-top:4px;">{note}</div>' if note else ""
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

    st.html(
        """
        <div class="page-title-row">
            <div>
                <h1 class="view-title">Category Review</h1>
                <div class="view-subtitle">Human-in-the-loop verification for uncertain machine learning predictions (score &lt; 0.42)</div>
            </div>
        </div>
        """
    )

    review_scope_col1, review_scope_col2 = st.columns([6, 4], vertical_alignment="center")
    with review_scope_col1:
        st.caption(f"{scope_desc}. Verify or adjust predicted categories.")
    with review_scope_col2:
        st.radio(
            "Review Scope",
            options=["All Records", "Current Month"],
            horizontal=True,
            key="review_scope",
            label_visibility="collapsed",
        )

    if not pending_txs:
        st.html(
            """
            <div class="review-attention-strip completed">
                <div class="review-attention-left">
                    <div class="review-badge-icon">✓</div>
                    <div class="review-attention-text">
                        <div class="review-attention-title">Category Review Queue is Clear</div>
                        <div class="review-attention-desc">All transaction descriptions are confirmed. When new unclassified expenses arrive, they will appear here.</div>
                    </div>
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
                st.html(f'<div class="review-reason" style="font-size:12px; color:#737681; margin:6px 0;"><strong>Why this needs review</strong><br>{html.escape(reason)}</div>')

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
    st.html(
        """
        <div class="page-title-row">
            <div>
                <h1 class="view-title">Model Evaluation</h1>
                <div class="view-subtitle">Synthetic holdout test results and classification diagnostics</div>
            </div>
        </div>
        """
    )
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
