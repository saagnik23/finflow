# SpendStory UI/UX Audit & Architecture Assessment

## 1. Executive Summary

This audit assesses the current visual design, technical stack, Streamlit rendering architecture, and interaction dynamics of **SpendStory** prior to implementing the exact cursor artwork and visual language redesign specified in the design brief.

SpendStory is an AI-assisted personal finance dashboard built for students, combining a local SQLite ledger, TF-IDF + Logistic Regression categorization with confidence-based human-in-the-loop review, and financial metrics computed in integer paise.

---

## 2. Technical Stack & Environment

| Component | Current Specification | Target / Constraints |
|---|---|---|
| **Runtime** | Python 3.13 (Host) / 3.12 compatible | Keep strict Python 3.12 compatibility |
| **Framework** | Streamlit 1.66.1 | Preserve Streamlit architecture; no framework rewrite |
| **Persistence** | SQLite (`storage/finance.db` or `:memory:` for hosted demo) | Preserve exact schema, table structures, and atomic commits |
| **ML Engine** | scikit-learn 1.9.1 (TF-IDF + Logistic Regression) | Preserve exact model weights, cutoff (0.42), and abstention logic |
| **Math / Logic** | Integer paise arithmetic, no floating-point currency drift | Preserved in `src/analytics.py` and `src/transactions.py` |
| **Component Model** | Streamlit Web Components v2 (`st.components.v2.component`) | Uses Shadow DOM for chart isolation |
| **Deployment** | Render Web Service (`render.yaml`) | Preserve exact build and start configurations |

---

## 3. Visual Baseline & Design Gaps

### 3.1. Color Palette Discrepancy
- **Current State:** The legacy interface uses a lavender-violet gradient canvas (`linear-gradient(161deg, #d7def8, #dedcf8, #e8d1f3)`), electric blue/purple brand accents (`#373EDC`, `#7E3AF2`), and magenta chart slices (`#ce38dd`, `#cc36df`).
- **Required State:** The visual reference specifies a clean, neutral canvas (`#F4F4F6`), crisp white rounded cards (`#FFFFFF`), subtle borders (`#E3E4E8`), charcoal typography (`#191A1F`), muted mint (`#CFE4D8`), mint accent (`#78A98E`), pale lime (`#E4F477`), and charcoal buttons (`#202126`). Dominant purple/violet must be completely eliminated.

### 3.2. Typography
- **Current State:** Defaults to standard system Inter / Segoe UI / sans-serif stack.
- **Required State:** Manrope as primary typeface (geometric, clean, slightly rounded, highly legible) with Inter / system-ui fallback, tabular numbers for all currency figures.

### 3.3. Component Surfaces & Shadows
- **Current State:** Heavy neon-purple border glow (`box-shadow: 0 0 0 11px rgba(255,255,255,.36), 0 22px 50px rgba(82,53,151,.14)`), inconsistent card heights, and generic table rows.
- **Required State:** Restrained, elegant soft surfaces with 14–16px rounded corners, 1px neutral borders (`#E3E4E8`), gentle micro-shadows (`rgba(20, 24, 45, 0.04)`), and clear visual hierarchy.

---

## 4. Streamlit 1.66 DOM & Component Inspection

### 4.1. DOM Hierarchy
- Streamlit 1.66 wraps the application in `[data-testid="stAppViewContainer"]` with a sidebar `[data-testid="stSidebar"]` and main content area `[data-testid="stMain"]`.
- `st.html(...)` injects `<style>` rules directly into the root document head, allowing reliable global CSS overrides.

### 4.2. Custom Charts & Shadow DOM
- `src/dashboard_charts.py` registers `_CHART = st.components.v2.component(...)`.
- In Streamlit 1.66, `st.components.v2.component` creates custom HTML elements with **Shadow Roots** (`attachShadow({mode: 'open'})`).
- **Implications for Cursors & Styling:**
  - Standard global CSS rules do not pierce the shadow boundary. Therefore, chart styles, interactive hover states, and cursor rules must be provided in `src/dashboard_charts.css`.
  - DOM pointer events (`pointermove`, `click`) have `composed: true` and naturally bubble out of shadow roots into the top-level `window` document.

### 4.3. Streamlit Rerender Lifecycle
- When a user changes navigation, filters, or inputs, Streamlit reruns the script top-to-bottom.
- Injected `<style>` blocks persist cleanly without flash.
- Any JavaScript must be idempotent, storing singleton instances on `window.__spendstory_cursor` to prevent duplicate event listeners or duplicate DOM overlay nodes.

---

## 5. Cursor Reference Inspection

- The master cursor reference (`docs/cursor_reference.png`) was inspected at high resolution:
  - **Left character:** Hand-drawn kawaii arrow pointer (301 × 471 px), pointing up-left. Thick black outline, solid white interior, cool-grey offset shadow on the right/bottom, cute face with black eyes and small `w`-shaped mouth.
  - **Right character:** Hand-drawn kawaii pointing hand (459 × 469 px), with index finger extended upward. Thick black outline, solid white interior, cool-grey offset shadow, matching facial expression.
- **Hotspots:**
  - Arrow: Tip of pointer at `(11, 10)` in source coordinates.
  - Hand: Index fingertip at `(154, 4)` in source coordinates.
- **Strategy:**
  1. Prepare high-resolution PNG assets with transparent exterior, preserving 100% of the original black outline, white fill, facial features, and cool-grey shadow.
  2. Implement an app-wide CSS `cursor: url(...)` base layer for instant, lag-free responsiveness across all elements.
  3. Complement with an optional smooth follower overlay with exponential smoothing (`requestAnimationFrame`) when supported, respecting `prefers-reduced-motion` and touch devices.

---

## 6. Audit Verdict & Implementation Plan

The SpendStory architecture is solid, modular, and ready for redesign. All business logic, tests, and SQLite persistence are decoupled from presentation. The redesign will proceed across the planned 7 phases with zero regressions.

