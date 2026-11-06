# SpendStory UI Recomposition & Exact Cursor Master Plan

## 1. Executive Summary & Core Mandate

This plan defines the architectural recomposition and visual redesign of SpendStory.
The previous design pass retained the legacy Streamlit composition (full-height left sidebar, top utility toolbar, four equal KPI cards, large line chart beside oversized donut chart). This master implementation replaces that legacy layout with an entirely new information architecture inspired by the supplied visual reference while strictly preserving the exact kawaii cursor artwork and the underlying Python/Streamlit/SQLite/scikit-learn stack.

---

## 2. Information Architecture: Old vs. New

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ BEFORE (Legacy Composition)                                                            │
├──────────────┬─────────────────────────────────────────────────────────────────────────┤
│ Full-height  │ Top toolbar: Search | Month Select | CSV Export | CSV Import            │
│ Left Sidebar │ Greeting: "Good day, Student"                                           │
│ (Nav radio,  ├──────────────────┬──────────────────┬──────────────────┬────────────────┤
│ Demo tools,  │ KPI 1 (Income)   │ KPI 2 (Expense)  │ KPI 3 (Surplus)  │ KPI 4 (Transfer)│
│ Settings,    ├──────────────────┴──────────────────┴──────────────────┴────────────────┤
│ Reset DB)    │ Cash Flow Line Chart (65%)          │ Oversized Purple Donut (35%)       │
│              ├─────────────────────────────────────┼───────────────────────────────────┤
│              │ Budget Progress (50%)               │ Monthly Comparison Bars (50%)     │
└──────────────┴─────────────────────────────────────┴───────────────────────────────────┘

┌────────────────────────────────────────────────────────────────────────────────────────┐
│ AFTER (Recomposed Top-Navigation Application Shell)                                    │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ TOP APPLICATION HEADER (Horizontal, Compact, Zero Sidebar on Desktop)                  │
│ [Brand • SpendStory]     [Overview | Transactions | Budgets | Review (N) | Model Eval] │
│                          [Search input] [Month Dropdown] [Import/Export] [⚙ Settings]  │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ MAIN CONTENT WORKSPACE (Centered, Max-Width 1360px, Generous Padding)                  │
│                                                                                        │
│ ROW A: Title & Period Context                                                          │
│ "Overview" • "Your money, organised for this month." • [Selected Month Tag]            │
│                                                                                        │
│ ROW B: Single Monthly Snapshot Hero (Replaces the 4 separate KPI cards)                │
│ ┌────────────────────────────────────────────────────────────────────────────────────┐ │
│ │  RECORDED SURPLUS: ₹5,140.00 [Positive Surplus Badge]                              │ │
│ │  Income: ₹19,300.00  |  Expenses: ₹14,160.00  |  Transfers Excluded: ₹2,750.00     │ │
│ └────────────────────────────────────────────────────────────────────────────────────┘ │
│                                                                                        │
│ ROW C: Main Financial Story (Asymmetric 62% / 38% Composition)                         │
│ ┌───────────────────────────────────────────┬────────────────────────────────────────┐ │
│ │ CASH FLOW TIMELINE (62%)                  │ SPENDING BY CATEGORY (38%)             │ │
│ │ Income (Sage #83AD96) & Expenses (Coral)  │ Ranked Category List with Horizontal   │ │
│ │ Daily accumulation & active tooltip point │ Bars, Rupee Values & % Shares          │ │
│ └───────────────────────────────────────────┴────────────────────────────────────────┘ │
│                                                                                        │
│ ROW D: Action & Activity Split (50% / 50%)                                             │
│ ┌───────────────────────────────────────────┬────────────────────────────────────────┐ │
│ │ BUDGET HEALTH PANEL (50%)                 │ RECENT ACTIVITY PANEL (50%)            │ │
│ │ Target vs Spent, Remaining/Over warning,  │ Latest 5 transactions with date, badge,│ │
│ │ Thin progress bars & "View all budgets"   │ amount & "View all transactions" link  │ │
│ └───────────────────────────────────────────┴────────────────────────────────────────┘ │
│                                                                                        │
│ ROW E: Category Review Reminder Strip                                                  │
│ ┌────────────────────────────────────────────────────────────────────────────────────┐ │
│ │ ⚡ Attention Needed: 2 transactions await category confirmation. [Review Now Button] │ │
│ └────────────────────────────────────────────────────────────────────────────────────┘ │
│                                                                                        │
│ ROW F: Optional Annual Historical Cash Flow (Full Width Section)                       │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Design Tokens & Visual Hierarchy

| Category | Token | Hex | Role |
|---|---|---|---|
| **Canvas** | `canvas` | `#F4F4F6` | Global page background |
| **Surfaces** | `surface` | `#FFFFFF` | Primary card and container surfaces |
| | `surface-soft` | `#ECEEF1` | Secondary neutral fill, tracks, badges |
| | `surface-muted` | `#F7F7F8` | Form inputs, subtle table row alternations |
| **Borders** | `border` | `#E2E4E8` | 1px dividers and card boundaries |
| **Typography**| `text-primary`| `#191A1F` | Main headlines, key amounts, high-emphasis labels |
| | `text-secondary`|`#737681`| Subtitles, timestamps, captions, axis labels |
| **Controls** | `charcoal` | `#202126` | Active navigation pills, primary buttons |
| **Accents** | `mint-soft` | `#D1E5D9` | Positive trend tags, highlight pills |
| | `mint` | `#83AD96` | Income series, surplus indicators, healthy budgets |
| | `sage-dark` | `#527D68` | Strong positive emphasis |
| | `lime` | `#E4F477` | Highlight accents, active points on charts |
| | `expense-muted`|`#C77F78`| Expense series, deficit badges, over-budget warnings |
| | `warning` | `#D6A451` | Review status, pending warnings |
| | `danger` | `#BD6662` | Destructive actions, severe errors |

**Typography**: Manrope (400, 500, 600, 700), with tabular figures (`tabular-nums`) for currency and numerical tables.

---

## 4. Execution Phases

### Phase 1 — Application Shell & Header
- Implement top horizontal navigation shell using `st.segmented_control` / `st.pills` synchronized with `active_nav`.
- Hide Streamlit default desktop sidebar via CSS (`display: none !important`), retaining `st.sidebar.radio` internally for test suite compatibility (`tests/test_ui_smoke.py`).
- Integrate Month Selector, Search input, CSV Actions, and Settings popover into the top header.

### Phase 2 — Recomposed Overview View
- Row A: Page title, period context, and dataset tag.
- Row B: Single Monthly Snapshot Hero card with recorded surplus callout and inline income/expense/transfer metrics.
- Row C: Cash Flow timeline (62%) and Ranked Horizontal Category Bars (38%).
- Row D: Budget Health card (50%) and Recent Transactions list (50%).
- Row E: Human-in-the-loop Category Review banner.

### Phase 3 — Refined Secondary Pages
- Transactions: Unified search/category/type filter card, tabular ledger, quick add form, CSV export.
- Budgets: Summary banner, limit editor modal preserving all test keys (`configure_budgets`, `save_budget_targets`, `budget_slider_*`).
- Category Review: Review queue header, model confidence transparency, approval/reclassification actions.
- Model Evaluation: Holdout metrics dashboard, confusion matrix, and interactive description tester.

### Phase 4 — Exact Cursor Integration
- Preserve exact Arrow (38px, hotspot `1, 1`) and Hand (38px, hotspot `12, 0`) raster assets.
- Ensure Layer 1 CSS cursor and Layer 2 RAF follower seamlessly adapt to the new top-navigation header, popovers, and ranked bars.
- Retain native I-beam on inputs, touch suppression, reduced-motion bypass, and the Settings toggle.

### Phase 5 — Verification & Testing
- Run full pytest test suite (32 tests).
- Execute model evaluation holdout script.
- Capture responsive screenshots (Desktop 1440px, Laptop 1280px, Tablet 768px, Mobile 375px).
- Verify objective visual differences against baseline before-state.
