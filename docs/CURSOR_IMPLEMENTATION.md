# SpendStory Modern Black Cursor Implementation Guide

## 1. Overview & Modern Black Cursor Design

The SpendStory custom cursor has been updated to the **exact modern black rounded pointer cursor** provided in the user reference image (`media_1793986442335_385b3a09.png`).

### Visual Characteristics & Geometric Rules
- **Silhouette & Geometry:**
  - **Modern Arrow Pointer (Default State):** 668 × 800 px master artwork, solid black (`#000000`) with smooth pill-radius top-left apex, rounded wing, rounded tail, and smooth concave notch. Rendered at height 36px (width 30px). Hotspot is aligned precisely to the top-left pointing apex at `(2, 0)` in 36px coordinates (`45, 0` in master coordinates).
  - **Modern Pointing Hand (Hover/Interactive State):** 700 × 800 px master artwork, sleek matching solid black (`#000000`) with rounded index fingertip, pill-radius thumb and knuckles. Rendered at height 36px (width 32px). Hotspot is aligned to the index fingertip at `(10, 2)` in 36px coordinates.
- **Design Tokens:**
  - Color: Solid deep black (`#000000`, alpha 255) with antialiased translucent perimeter edges for seamless contrast on light backgrounds.
  - Scale: Compact 36px height (30 × 36 px arrow, 32 × 36 px hand) ensuring instant responsiveness and crisp clarity without visual obstruction.

---

## 2. Dual-Layer Cursor Architecture

SpendStory employs a robust **dual-layer architecture**:

```
+-----------------------------------------------------------------+
|                   Browser Window Viewport                       |
|                                                                 |
|   Layer 1: Resilient Native CSS Cursor                         |
|   cursor: url('data:image/png;base64,...') <x> <y>, auto        |
|   - Hardware accelerated                                        |
|   - Zero latency                                                |
|   - Full coverage (app, header, popovers, shadow DOM charts)   |
|                                                                 |
|   Layer 2: Streamlit-Compatible Smooth Visual Follower          |
|   - requestAnimationFrame time-based interpolation              |
|   - exponential smoothing (alpha = 0.35)                        |
|   - pointer-events: none (zero click interference)              |
|   - Singleton guard on window (no duplicates on rerender)       |
|   - Disabled automatically on touch & prefers-reduced-motion    |
|   - Documented toggle switch in settings popover                |
+-----------------------------------------------------------------+
```

### 2.1. Layer 1: Resilient CSS Cursor
Defined directly in the page CSS rules (`src/cursor_assets.py` and `src/dashboard_charts.css`):
- Normal page movement: `cursor: url('data:image/png;base64,...') 2 0, auto;`
- Interactive hover targets (buttons, links, selects, radios, chart slices, sliders): `cursor: url('data:image/png;base64,...') 10 2, pointer !important;`
- Text inputs / textareas: native `cursor: text !important;` (I-beam)
- Drag/resize: native cursors preserved

### 2.2. Layer 2: Smooth Follower Overlay
When enabled and on fine pointer devices (`@media (pointer: fine)`):
- Injects a singleton `<div id="spendstory-cursor-follower">` into `window.parent.document.body`.
- Tracks real pointer coordinates on `pointermove` with sub-pixel precision.
- Updates visual position using `requestAnimationFrame` with exponential smoothing:
  $$\text{pos}_{t} = \text{pos}_{t-1} + (\text{target} - \text{pos}_{t-1}) \times 0.35$$
- Hotspot offset correction:
  - Arrow: `offsetX = -2px`, `offsetY = 0px`
  - Hand: `offsetX = -10px`, `offsetY = -2px`
- Interactive state detection: dynamically adds `.is-interactive` class when the pointer hovers over clickable targets (`button`, `a`, `[role="button"]`, `.donut-slice`, etc.), seamlessly switching from Arrow to Hand artwork.
- Text input suppression: follower sets `opacity: 0` over text inputs (`input[type="text"]`, `textarea`, etc.) so the native OS I-beam is fully visible and unobstructed.
- Press state: subtle 0.96 scale transform on `pointerdown` for tactile feedback.

---

## 3. Streamlit Compatibility & Lifecycle Guards

1. **Rerender Safety:** The follower initialization script checks `if (window.__spendstory_cursor_initialized) return;` to prevent duplicate event listeners and duplicate DOM nodes across Streamlit rerun cycles.
2. **Shadow DOM Handling:** Streamlit charts render in shadow roots. Because pointer events have `composed: true`, pointer tracking continues uninterrupted as the mouse moves over charts. Additionally, `src/dashboard_charts.css` explicitly styles shadow DOM elements with the modern black custom cursor.
3. **Accessibility & Motion Preferences:**
   - Detects `window.matchMedia('(prefers-reduced-motion: reduce)')`. If enabled, follower overlay smoothing is disabled and pure CSS cursor is used.
   - Detects touch devices (`@media (pointer: coarse)` / `'ontouchstart' in window`). If detected, custom cursors are completely suppressed.
4. **User Toggle:** A settings toggle in the top-right Settings popover allows users to disable the custom cursor and return to native OS cursors at any time.

---

## 4. Asset Manifest

| Asset Name | Path | Dimensions | Hotspot (x, y) | Purpose |
|---|---|---|---|---|
| Master Arrow (Modern Black) | `src/assets/modern-black-cursor-master.png` | 668 × 800 | (45, 0) | High-res master asset |
| Master Hand (Modern Black) | `src/assets/modern-black-hand-master.png` | 700 × 800 | (218, 44) | High-res master asset |
| Web Arrow 36px | `src/assets/cursor-modern-black-36.png` | 30 × 36 | (2, 0) | Web & CSS cursor data URI |
| Web Hand 36px | `src/assets/cursor-modern-hand-36.png` | 32 × 36 | (10, 2) | Web & CSS cursor data URI |
| Web Arrow 30px | `src/assets/cursor-modern-black-30.png` | 25 × 30 | (2, 0) | Compact display fallback |

---

## 5. Verification & Testing

The cursor implementation was verified via automated Playwright tests (`scripts/verify_recomposition_cursor.py`):
1. **Neutral Hover:** Verified `spendstory-cursor-follower` exists and is non-interactive (Arrow displayed).
2. **Interactive Hover:** Verified hovering over navigation pills and buttons triggers `.is-interactive` (Hand displayed).
3. **Text Input Hover:** Verified hovering over search and text inputs sets follower `opacity: 0` (native I-beam cursor active).
4. **Pointer Down:** Verified active mouse click triggers `.is-pressed` scale transform.
5. **Unit Tests:** 32/32 unit and smoke tests passing via `pytest -v`.
