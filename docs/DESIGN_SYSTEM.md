# SpendStory Design System Specification

## 1. Design Philosophy

The SpendStory design system adapts the visual language of the reference dashboard for a focused, student-oriented personal finance application.

### Key Principles
1. **Calm, Neutral Grounding:** A soft near-white canvas (`#F4F4F6`) creates breathing room, allowing information-dense cards to stand out without visual exhaustion.
2. **Layered Surfaces:** Primary white cards (`#FFFFFF`) rest gently on the canvas, framed by razor-thin borders (`#E3E4E8`) and soft ambient shadows (`rgba(20, 24, 45, 0.04)`).
3. **Intentional Accentuation:** Mint (`#78A98E`), soft muted mint (`#CFE4D8`), and restrained pale lime (`#E4F477`) serve exclusively as accents to denote positive surpluses, completed targets, and subtle selections.
4. **Legibility & Numerals:** Manrope font family paired with tabular figures (`font-variant-numeric: tabular-nums`) guarantees unambiguous financial review.
5. **Zero Gimmicks:** No crypto widgets, no superfluous avatars, and strictly no dominant purple or violet branding.

---

## 2. Color Palette & Semantic Tokens

| Token Name | Hex Code | Primary Usage |
|---|---|---|
| `--app-bg` | `#F4F4F6` | Master page background / viewport frame |
| `--surface-primary` | `#FFFFFF` | Financial metric cards, chart panels, ledger table rows |
| `--surface-secondary`| `#ECEEF1` | Card sub-panels, hover fills, badge containers |
| `--text-primary` | `#191A1F` | Headlines, metric figures, table values |
| `--text-secondary` | `#747781` | Metric labels, captions, metadata timestamps |
| `--border-subtle` | `#E3E4E8` | Card dividers, input borders, structural rules |
| `--mint-muted` | `#CFE4D8` | Soft positive badge backgrounds, progress tracks |
| `--mint-accent` | `#78A98E` | Positive cashflow lines, confirmed tags, primary success indicators |
| `--lime-pale` | `#E4F477` | Highlight badges, secondary selection states |
| `--charcoal-deep` | `#202126` | Primary action buttons, active navigation states, strong contrast elements |
| `--danger` | `#C96F69` | Deficit warnings, over-budget alerts, deletion confirmations |
| `--warning` | `#D4A451` | Review-required badges, unconfirmed predictions |

---

## 3. Typography Architecture

- **Primary Font Family:** `'Manrope', -apple-system, BlinkMacSystemFont, 'Inter', 'Segoe UI', sans-serif`
- **Numerical Formatting:** `tabular-nums` applied globally to financial numbers, currencies, dates, and percentages.
- **Hierarchy:**
  - **Display / H1:** 22px / 700 weight / letter-spacing -0.4px (`.view-title`, `.greeting-header`)
  - **Section Titles / H2:** 15px / 650 weight / letter-spacing -0.2px (`.panel-title`)
  - **Metric Figures:** 24px / 700 weight / letter-spacing -0.6px (`.metric-figure`)
  - **Body / Labels:** 13px / 400–500 weight (`.metric-label`, `.ledger-row`)
  - **Micro-copy / Badges:** 11px / 600 weight (`.metric-badge`, `.badge-confirmed`)

---

## 4. Surfaces, Radius & Elevation

- **Card Radius:** `14px` border-radius on major containers.
- **Micro Radius:** `8px` on buttons, inputs, chips, and progress bars.
- **Elevation System:**
  - `Flat:` `border: 1px solid #E3E4E8; background: #FFFFFF;`
  - `Hover Card:` `box-shadow: 0 4px 16px rgba(25, 26, 31, 0.05); transform: translateY(-1px);`
  - `Dropdown / Tooltip:` `box-shadow: 0 8px 24px rgba(25, 26, 31, 0.08); border: 1px solid #E3E4E8;`

---

## 5. Chart Visualization Tokens

- **Trend Chart:**
  - Income curve: `#78A98E` (Mint accent) with soft gradient fill
  - Expense curve: `#202126` (Charcoal) with soft ambient drop
  - Gridlines: `#E3E4E8` dashed stroke
- **Category Donut:**
  - Slices: Harmonic categorical tokens (`#78A98E`, `#5E7C8D`, `#8EA89D`, `#C96F69`, `#D4A451`, `#202126`, `#A0AEC0`)
- **Monthly Comparison:**
  - Paired income (`#78A98E`) and expense (`#202126`) bar groups with clean hover callouts.

