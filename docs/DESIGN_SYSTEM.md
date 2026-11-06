# SpendStory Design System Specification

## 1. Design Philosophy

The SpendStory design system translates the visual language of the reference dashboard into an authentic, calm, and financially transparent experience tailored for students.

### Core Principles
1. **Calm, Neutral Grounding:** A soft light grey / off-white canvas (`#F4F4F6`) creates generous negative space, allowing data cards to feel airy and uncluttered.
2. **Top-Navigation Application Shell:** A clean horizontal header replaces the legacy vertical left sidebar on desktop, maximizing vertical and horizontal room for financial analytics.
3. **Consolidated Financial Story:** Instead of fragmented KPI cards, a unified Monthly Snapshot Hero provides immediate context: Surplus at the center, supported cleanly by Income, Expenses, and Transfers Excluded.
4. **Scannable Ranked Bars:** Spending distribution is presented as ranked horizontal bars with category names, exact rupee amounts, and percentages, replacing the previous oversized donut chart.
5. **Exact Kawaii Cursor Integration:** The illustrated arrow and pointing hand are preserved as exact source artwork, integrating seamlessly without color pollution or distortion.

---

## 2. Color Palette & Semantic Tokens

| Token Name | Hex Code | Primary Usage |
|---|---|---|
| `canvas` | `#F4F4F6` | Global page canvas background |
| `surface` | `#FFFFFF` | Cards, panels, hero containers, and tables |
| `surface-soft` | `#ECEEF1` | Secondary neutral surface, badge bases, pill tracks |
| `surface-muted` | `#F7F7F8` | Form inputs, alternating table rows |
| `text-primary` | `#191A1F` | Headlines, primary values, card titles |
| `text-secondary` | `#737681` | Supporting labels, subtitles, axis text, timestamps |
| `border` | `#E2E4E8` | Dividers, card borders, subtle table lines |
| `charcoal` | `#202126` | Top navigation active pill, primary action buttons |
| `mint-soft` | `#D1E5D9` | Calm positive emphasis, positive badge backgrounds |
| `mint` | `#83AD96` | Income series, surplus indicators, healthy budget bars |
| `sage-dark` | `#527D68` | Strong positive emphasis |
| `lime` | `#E4F477` | Highlight accents, active chart data points |
| `expense-muted` | `#C77F78` | Expense series, recorded deficits, over-budget warnings |
| `warning` | `#D6A451` | Review status, pending human verification items |
| `danger` | `#BD6662` | Destructive confirmations, error states |

---

## 3. Typography Architecture

- **Primary Typeface:** `'Manrope', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif`
- **Numerical Formatting:** `tabular-nums` applied across all currency displays, budgets, tables, and metric figures.
- **Hierarchy:**
  - **Page Title (`h1`):** 24px / 800 weight / letter-spacing -0.5px
  - **Hero Net Metric:** 36px / 800 weight / letter-spacing -0.8px
  - **Section Titles (`h2`):** 16px / 700 weight / letter-spacing -0.3px
  - **Inline Hero Metrics:** 18px / 700 weight / letter-spacing -0.4px
  - **Body / Labels:** 13px / 500 weight (`.metric-label`, `.ledger-cell`)
  - **Micro-copy / Badges:** 11px / 600 weight / letter-spacing +0.2px

---

## 4. Surfaces & Layout Geometry

- **Top Navigation Header:**
  - Compact horizontal height (`56px`).
  - Brand mark on left, segmented pill navigation in center, utility controls (search, month select, CSV actions, settings popover) on right.
- **Desktop Content Workspace:**
  - Centered workspace with `max-width: 1360px` and `padding: 0 24px`.
- **Card Geometry:**
  - Primary radius: `16px`.
  - Micro radius: `8px` (inputs, buttons, pill badges).
  - Borders: `1px solid #E2E4E8`.
  - Ambient Shadow: `0 2px 8px rgba(25, 26, 31, 0.04)`.

---

## 5. Chart & Data Visualization System

- **Cash Flow Timeline:**
  - Income curve: Muted mint/sage (`#83AD96`) with soft subtle fill.
  - Expense curve: Charcoal / soft coral (`#C77F78`) with soft drop.
  - Active hover point: Lime (`#E4F477`) ring.
  - Gridlines: `#E2E4E8` fine dashed lines.
- **Spending by Category (Ranked Bars):**
  - Horizontal bar tracks with proportionate widths (`width: X%`).
  - Bar fill: Muted sage (`#83AD96`) for top category, harmonic slate tones (`#5E7C8D`, `#8EA89D`, `#9CA3AF`) for secondary categories.
- **Budget Health Indicators:**
  - Healthy (`<80%`): Mint (`#83AD96`).
  - Approaching (`80–100%`): Lime/Amber (`#D6A451`).
  - Over Budget (`>100%`): Coral/Danger (`#C77F78`).
