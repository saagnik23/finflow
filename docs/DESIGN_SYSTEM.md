# SpendStory Design System Specification

## 1. Design Philosophy

The SpendStory design system translates the visual language of the reference dashboard into an authentic, calm, and financially transparent experience tailored for students.

### Core Principles
1. **Calm, Neutral Grounding:** A soft light grey / cool pale neutral canvas (`#F7F7FA`) creates generous negative space, allowing data cards to feel airy and uncluttered.
2. **Top-Navigation Application Shell:** A clean horizontal header replaces the legacy vertical left sidebar on desktop, maximizing vertical and horizontal room for financial analytics.
3. **Consolidated Financial Story:** Instead of fragmented KPI cards, a unified Monthly Snapshot Hero provides immediate context: Surplus at the center, supported cleanly by Income, Expenses, and Transfers Excluded.
4. **Scannable Ranked Bars:** Spending distribution is presented as ranked horizontal bars with category names, exact rupee amounts, and percentages, replacing the previous oversized donut chart.
5. **Exact Modern Black Cursor Integration:** The sleek modern black rounded pointer arrow and pointing hand are preserved as exact source artwork, integrating seamlessly via a dual-layer hardware CSS data URI and RAF smooth follower system.

---

## 2. Color Palette & Semantic Tokens

| Token Name | Hex Code | Primary Usage |
|---|---|---|
| `canvas` | `#F7F7FA` | Global page canvas background |
| `surface` | `#FFFFFF` | Cards, panels, hero containers, and tables |
| `surface-soft` | `#F0F1F6` | Secondary neutral surface, badge bases, pill tracks |
| `surface-subtle` | `#F8F7FC` | Form inputs, alternating table rows, recent transactions |
| `text-primary` | `#111216` | Headlines, primary values, card titles |
| `text-secondary` | `#7A8190` | Supporting labels, subtitles, axis text, timestamps |
| `border` | `#ECEEF3` | Dividers, card borders, subtle table lines |
| `charcoal` | `#18191D` | Top navigation active pill, primary action buttons |
| `teal-mint` | `#75D2CD` | Key accent: Income series, positive badges, category bars |
| `forest-green`| `#267351` | Strong positive income typography |
| `lime-volt` | `#ECFB94` | Key accent: Surplus highlight badge, Friday activity highlight |
| `coral-expense`| `#C77F78` | Expense series, recorded deficits, over-budget warnings |
| `soft-blue` | `#5B8EE4` | Education category accent |
| `lavender` | `#D8B4E2` | Shopping category accent |
| `transfer` | `#4E6778` | Internal transfers (excluded from surplus) |

---

## 3. Typography Architecture

- **Primary Headings & Hero Figures:** `'Outfit', sans-serif` (weights 300, 400, 500, 600, 700, 800)
- **Primary Body & Interactive Elements:** `'Plus Jakarta Sans', sans-serif` (weights 300, 400, 500, 600, 700, 800)
- **Numerical Formatting:** `tabular-nums` applied across all currency displays, budgets, tables, and metric figures.
- **Hierarchy:**
  - **Page Title (`h1`):** 26px / 700 weight / letter-spacing -0.6px
  - **Hero Net Metric:** 40px / 800 weight / letter-spacing -1.2px
  - **Section Titles (`h2`):** 16px / 750 weight / letter-spacing -0.3px
  - **Inline Hero Metrics:** 20px / 750 weight / letter-spacing -0.5px
  - **Body / Labels:** 13px / 500 weight (`.metric-label`, `.ledger-cell`)
  - **Micro-copy / Badges:** 11.5px / 700 weight / letter-spacing +0.2px

---

## 4. Surfaces & Layout Geometry

- **Top Navigation Header:**
  - Compact horizontal height (`56px`).
  - Brand mark on left, segmented pill navigation in center, utility controls (search, month select, CSV actions, settings popover) on right.
  - Border radius: `24px`.
- **Desktop Content Workspace:**
  - Centered workspace with `max-width: 1360px` and `padding: 0 24px`.
- **Card Geometry:**
  - Primary radius: `24px` on cards, `16px` on inner items, `14px` on buttons & inputs, `20px` on pill badges.
  - Borders: `1px solid #ECEEF3`.
  - Ambient Shadow: `0 4px 20px rgba(0, 0, 0, 0.025)`.

---

## 5. Chart & Data Visualization System

- **Cash Flow Timeline:**
  - Income curve: Fresh mint/teal (`#75D2CD`) with soft gradient fill.
  - Expense curve: Charcoal / soft coral (`#18191D` / `#C77F78`) with soft drop.
  - Active hover point: Electric lime (`#ECFB94`) band & highlight ring.
  - Gridlines: `#ECEEF3` fine dashed lines.
- **Spending by Category (Ranked Bars):**
  - Horizontal bar tracks with proportionate widths (`width: X%`).
  - Bar track: `#F0F1F6` with `border-radius: 6px`.
  - Bar fill: Fresh teal/mint (`#75D2CD`) for top category, harmonic palette (`#E4FA53`, `#5B8EE4`, `#C77F78`, `#D8B4E2`, `#18191D`, `#9DA5B4`) for secondary categories.
- **Budget Health Indicators:**
  - Healthy (`<80%`): Teal/Mint (`#75D2CD`).
  - Approaching (`80–100%`): Lime/Amber (`#E4FA53`).
  - Over Budget (`>100%`): Coral/Danger (`#C77F78`).
