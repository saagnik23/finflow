# SpendStory Exact Illustrated Cursor Implementation Guide

## 1. Overview & Reference Artwork Authenticity

The SpendStory custom cursor is an **exact, immutable reproduction** of the master artwork provided in `docs/cursor_reference.png`.

### Absolute Fidelity Rules
- **No reinterpretation:** The exact artwork, proportions, thick outline, facial expression, and cool-grey shadow have been extracted directly from the source image.
- **Silhouette & Geometry:**
  - **Arrow Pointer (Left State):** 301 × 471 px master artwork, 0.639 aspect ratio. Rendered at height 38px (width 24px) for crisp display. Hotspot is aligned exactly to the top-left pointing tip at `(1, 1)` in 38px coordinates (`11, 10` in master coordinates).
  - **Pointing Hand (Right State):** 459 × 469 px master artwork, 0.978 aspect ratio. Rendered at height 38px (width 37px) for crisp display. Hotspot is aligned exactly to the index fingertip at `(12, 0)` in 38px coordinates (`154, 4` in master coordinates).
- **Artwork Details:**
  - Thick black hand-drawn outline.
  - Solid opaque white interior fill.
  - Authentic cool-grey offset shadow (`#B5B5B5` / RGB ~181) on the lower-right perimeter.
  - Cute hand-drawn facial features (two solid round eyes and small `w`-shaped mouth) preserved at exact coordinates without retouching.

---

## 2. Dual-Layer Cursor Architecture

To guarantee both 100% reliability across Streamlit's dynamic component lifecycle and provide smooth visual follower motion, SpendStory uses a **dual-layer architecture**:

```
+-----------------------------------------------------------------+
|                   Browser Window Viewport                       |
|                                                                 |
|   Layer 1: Resilient Native CSS Cursor                         |
|   cursor: url('data:image/png;base64,...') <x> <y>, auto        |
|   - Hardware accelerated                                        |
|   - Zero latency                                                |
|   - Full coverage (app, sidebar, modals, shadow DOM charts)     |
|                                                                 |
|   Layer 2: Streamlit-Compatible Smooth Visual Follower          |
|   - requestAnimationFrame time-based interpolation              |
|   - exponential smoothing (alpha = 0.35)                        |
|   - pointer-events: none (zero click interference)              |
|   - Singleton guard on window (no duplicates on rerender)       |
|   - Disabled automatically on touch & prefers-reduced-motion    |
|   - Documented toggle switch in sidebar settings                |
+-----------------------------------------------------------------+
```

### 2.1. Layer 1: Resilient CSS Cursor
Defined directly in the page CSS rules:
- Normal page movement: `cursor: url('data:image/png;base64,...') 1 1, auto;`
- Interactive hover targets (buttons, links, selects, radios, chart slices, sliders): `cursor: url('data:image/png;base64,...') 12 0, pointer;`
- Text inputs / textareas: native `cursor: text !important;` (I-beam)
- Drag/resize: native cursors preserved

### 2.2. Layer 2: Smooth Follower Overlay
When enabled and on fine pointer devices (`@media (pointer: fine)`):
- Injects a singleton `<div id="spendstory-cursor-follower">` into `window.parent.document.body`.
- Tracks real pointer coordinates on `pointermove` with sub-pixel precision.
- Updates visual position using `requestAnimationFrame` with exponential smoothing:
  $$\text{pos}_{t} = \text{pos}_{t-1} + (\text{target} - \text{pos}_{t-1}) \times \text{smoothingFactor}$$
- Tuning: smoothing factor = `0.35` (instant response without visible drag lag, maintaining crisp alignment with the click target).
- Interactive state detection: dynamically adds `.hovering` class when the pointer hovers over clickable targets (`button`, `a`, `[role="button"]`, `.donut-slice`, etc.), seamlessly switching from Arrow to Hand artwork.
- Press state: subtle 0.95 scale transform on `pointerdown` without distorting aspect ratio or artwork.

---

## 3. Streamlit Compatibility & Lifecycle Guards

1. **Rerender Safety:** The follower initialization script checks `if (window.__spendstory_cursor_initialized) return;` to prevent duplicate event listeners and duplicate DOM nodes across Streamlit rerun cycles.
2. **Shadow DOM Handling:** Streamlit 1.66 charts render in shadow roots. Because pointer events have `composed: true`, pointer tracking continues uninterrupted as the mouse moves over charts. Additionally, `src/dashboard_charts.css` explicitly styles shadow DOM elements with the custom cursor.
3. **Accessibility & Motion Preferences:**
   - Detects `window.matchMedia('(prefers-reduced-motion: reduce)')`. If enabled, follower overlay smoothing is disabled and pure CSS cursor is used.
   - Detects touch devices (`@media (pointer: coarse)` / `'ontouchstart' in window`). If detected, custom cursors are completely suppressed.
4. **User Toggle:** A settings toggle in the sidebar (`st.toggle("Kawaii Custom Cursor", value=True)`) allows users to disable the custom cursor and return to native OS cursors at any time.

---

## 4. Asset Manifest

| Asset Name | Path | Dimensions | Hotspot (x, y) | Purpose |
|---|---|---|---|---|
| Master Arrow Reference | `src/assets/spendstory-cursor-arrow.png` | 301 × 471 | (11, 10) | Source high-resolution master |
| Master Hand Reference | `src/assets/spendstory-cursor-hand.png` | 459 × 469 | (154, 4) | Source high-resolution master |
| Web Arrow 38px | `src/assets/cursor-arrow-38.png` | 24 × 38 | (1, 1) | CSS cursor data URI (1x/2x) |
| Web Hand 38px | `src/assets/cursor-hand-38.png` | 37 × 38 | (12, 0) | CSS cursor data URI (1x/2x) |
| Web Arrow 32px | `src/assets/cursor-arrow-32.png` | 20 × 32 | (1, 1) | Compact standard display fallback |
| Web Hand 32px | `src/assets/cursor-hand-32.png` | 31 × 32 | (11, 0) | Compact standard display fallback |

