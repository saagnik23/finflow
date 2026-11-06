"""Reference Dashboard Visual Assets and SVGs for FinFlow.

Provides data URIs for all vector assets:
- Slim Left Floating Dock icons
- Iridescent 3D Crystal Octahedron on 3D Pedestal
- Top application brand monogram (stylized calligraphic 'A')
- Pro sparkline with vertical hatched pattern
- Spent spline wave chart with nodes
"""

from __future__ import annotations
import base64

def _svg_to_data_uri(svg: str) -> str:
    encoded = base64.b64encode(svg.strip().encode("utf-8")).decode("utf-8")
    return f"data:image/svg+xml;base64,{encoded}"

CRYSTAL_3D_SVG = """<svg viewBox="0 0 240 240" width="220" height="210" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <!-- Facet Gradients -->
    <linearGradient id="facetTopLeft" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#EBF4FF" stop-opacity="0.95"/>
      <stop offset="60%" stop-color="#80A8FF" stop-opacity="0.85"/>
      <stop offset="100%" stop-color="#5577ED" stop-opacity="0.9"/>
    </linearGradient>
    <linearGradient id="facetTopFront" x1="50%" y1="0%" x2="50%" y2="100%">
      <stop offset="0%" stop-color="#FFFFFF" stop-opacity="0.98"/>
      <stop offset="45%" stop-color="#A5C7FF" stop-opacity="0.8"/>
      <stop offset="100%" stop-color="#D982F4" stop-opacity="0.85"/>
    </linearGradient>
    <linearGradient id="facetTopRight" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#FFEBF8" stop-opacity="0.95"/>
      <stop offset="50%" stop-color="#E27DF0" stop-opacity="0.85"/>
      <stop offset="100%" stop-color="#8246E5" stop-opacity="0.9"/>
    </linearGradient>
    <linearGradient id="facetBotLeft" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#4F72E8" stop-opacity="0.9"/>
      <stop offset="60%" stop-color="#3D50B8" stop-opacity="0.95"/>
      <stop offset="100%" stop-color="#243075" stop-opacity="0.98"/>
    </linearGradient>
    <linearGradient id="facetBotFront" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#B265E6" stop-opacity="0.9"/>
      <stop offset="50%" stop-color="#673EB5" stop-opacity="0.95"/>
      <stop offset="100%" stop-color="#3A1F75" stop-opacity="0.98"/>
    </linearGradient>
    <linearGradient id="facetBotRight" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#7B3ABF" stop-opacity="0.85"/>
      <stop offset="100%" stop-color="#32145E" stop-opacity="0.95"/>
    </linearGradient>
    <linearGradient id="pedestalGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#DCE6F5"/>
      <stop offset="100%" stop-color="#BACBE2"/>
    </linearGradient>
    <filter id="crystalGlow" x="-20%" y="-20%" width="140%" height="140%">
      <feGaussianBlur stdDeviation="6" result="blur"/>
      <feComposite in="SourceGraphic" in2="blur" operator="over"/>
    </filter>
    <filter id="pedestalShadow" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="0" dy="10" stdDeviation="10" flood-color="#5577AA" flood-opacity="0.2"/>
    </filter>
  </defs>

  <!-- Ambient Floor Shadow -->
  <ellipse cx="120" cy="208" rx="72" ry="14" fill="#A8BBD6" opacity="0.45" />

  <!-- Pedestal -->
  <g filter="url(#pedestalShadow)">
    <path d="M 68 184 L 120 198 L 172 184 L 172 170 L 120 184 L 68 170 Z" fill="#99AEC9"/>
    <path d="M 68 170 L 120 184 L 120 198 L 68 184 Z" fill="#889DB8"/>
    <path d="M 120 184 L 172 170 L 172 184 L 120 198 Z" fill="#788DA8"/>
    <polygon points="120,154 172,170 120,184 68,170" fill="url(#pedestalGrad)"/>
    <polygon points="120,154 172,170 120,184 68,170" fill="#FFFFFF" opacity="0.4"/>
  </g>

  <!-- Floating 3D Crystal Octahedron -->
  <g filter="url(#crystalGlow)">
    <ellipse cx="120" cy="98" rx="42" ry="50" fill="#9FBFFF" opacity="0.35"/>
    <polygon points="120,24 76,96 120,108" fill="#5A7FE8" opacity="0.6"/>
    <polygon points="120,24 164,96 120,108" fill="#8C4BE8" opacity="0.6"/>
    <polygon points="120,24 76,96 120,108" fill="url(#facetTopLeft)"/>
    <polygon points="120,24 120,108 164,96" fill="url(#facetTopRight)"/>
    <polygon points="120,24 102,98 120,108" fill="url(#facetTopFront)" opacity="0.9"/>
    <line x1="120" y1="24" x2="120" y2="108" stroke="#FFFFFF" stroke-width="1.8" opacity="0.9"/>
    <line x1="120" y1="24" x2="76" y2="96" stroke="#FFFFFF" stroke-width="1.2" opacity="0.7"/>
    <line x1="120" y1="24" x2="164" y2="96" stroke="#FFFFFF" stroke-width="1.2" opacity="0.7"/>
    <polygon points="76,104 120,116 120,172" fill="url(#facetBotLeft)"/>
    <polygon points="164,104 120,116 120,172" fill="url(#facetBotRight)"/>
    <polygon points="104,111 120,116 120,172" fill="url(#facetBotFront)" opacity="0.9"/>
    <line x1="120" y1="116" x2="120" y2="172" stroke="#B8D0FF" stroke-width="1.6" opacity="0.8"/>
    <line x1="76" y1="104" x2="120" y2="172" stroke="#7A9CFF" stroke-width="1" opacity="0.6"/>
    <line x1="164" y1="104" x2="120" y2="172" stroke="#B575FF" stroke-width="1" opacity="0.6"/>
    <polygon points="76,96 120,108 164,96 164,104 120,116 76,104" fill="#C2D8FF" opacity="0.7"/>
  </g>
</svg>"""

PRO_SPARKLINE_SVG = """<svg viewBox="0 0 280 80" width="280" height="80" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <pattern id="diagonalHatch" width="6" height="6" patternTransform="rotate(90 0 0)" patternUnits="userSpaceOnUse">
      <line x1="0" y1="0" x2="0" y2="6" stroke="#DCE2ED" stroke-width="1.8" />
    </pattern>
  </defs>
  <path d="M 10 65 Q 70 65 110 50 T 200 40 T 270 15 L 270 75 L 10 75 Z" fill="url(#diagonalHatch)" />
  <path d="M 10 65 Q 70 65 110 50 T 200 40 T 270 15" fill="none" stroke="#18191D" stroke-width="2" />
  <circle cx="10" cy="65" r="3.5" fill="#18191D" />
  <circle cx="270" cy="15" r="3.5" fill="#18191D" />
</svg>"""

SPENT_SPLINE_SVG = """<svg viewBox="0 0 340 100" width="340" height="100" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="spentSplineGrad" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#EAECEF" stop-opacity="0.8"/>
      <stop offset="100%" stop-color="#FFFFFF" stop-opacity="0.0"/>
    </linearGradient>
  </defs>
  <path d="M 15 80 C 45 78, 65 60, 95 62 C 125 64, 145 75, 175 60 C 205 45, 220 30, 245 40 C 270 50, 285 25, 325 20 L 325 95 L 15 95 Z" fill="url(#spentSplineGrad)"/>
  <path d="M 15 80 C 45 78, 65 60, 95 62 C 125 64, 145 75, 175 60 C 205 45, 220 30, 245 40 C 270 50, 285 25, 325 20" fill="none" stroke="#18191D" stroke-width="2"/>
  <circle cx="15" cy="80" r="3.5" fill="#18191D"/>
  <circle cx="95" cy="62" r="3.5" fill="#18191D"/>
  <circle cx="175" cy="60" r="3.5" fill="#18191D"/>
  <circle cx="210" cy="40" r="3.5" fill="#18191D"/>
  <circle cx="245" cy="40" r="3.5" fill="#18191D"/>
  <circle cx="325" cy="20" r="3.5" fill="#18191D"/>
</svg>"""

BRAND_MONOGRAM_SVG = """<svg width="26" height="26" viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg">
  <path d="M5 27L16 5L21 14L11 27H5Z" fill="#111216"/>
  <path d="M22 17L27 27H20L17 21L22 17Z" fill="#111216"/>
  <circle cx="15.5" cy="18" r="2.2" fill="#75D2CD"/>
</svg>"""

ICON_HOME_SVG = """<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#FFFFFF" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" xmlns="http://www.w3.org/2000/svg"><path d="m3 9 9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>"""
ICON_WALLET_SVG = """<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#7A8190" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" xmlns="http://www.w3.org/2000/svg"><rect width="20" height="14" x="2" y="5" rx="2"/><line x1="2" x2="22" y1="10" y2="10"/></svg>"""
ICON_DOC_SVG = """<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#7A8190" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" xmlns="http://www.w3.org/2000/svg"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" x2="8" y1="13" y2="13"/><line x1="16" x2="8" y1="17" y2="17"/></svg>"""
ICON_CHAT_SVG = """<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#7A8190" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" xmlns="http://www.w3.org/2000/svg"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>"""
ICON_SETTINGS_SVG = """<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#7A8190" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" xmlns="http://www.w3.org/2000/svg"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"/></svg>"""
ICON_SUPPORT_SVG = """<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#7A8190" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" xmlns="http://www.w3.org/2000/svg"><path d="M3 18v-6a9 9 0 0 1 18 0v6"/><path d="M21 19a2 2 0 0 1-2 2h-1a2 2 0 0 1-2-2v-3a2 2 0 0 1 2-2h3zM3 19a2 2 0 0 0 2 2h1a2 2 0 0 0 2-2v-3a2 2 0 0 0-2-2H3z"/></svg>"""

CRYSTAL_3D_DATA_URI = _svg_to_data_uri(CRYSTAL_3D_SVG)
PRO_SPARKLINE_DATA_URI = _svg_to_data_uri(PRO_SPARKLINE_SVG)
SPENT_SPLINE_DATA_URI = _svg_to_data_uri(SPENT_SPLINE_SVG)
BRAND_MONOGRAM_DATA_URI = _svg_to_data_uri(BRAND_MONOGRAM_SVG)

ICON_HOME_DATA_URI = _svg_to_data_uri(ICON_HOME_SVG)
ICON_WALLET_DATA_URI = _svg_to_data_uri(ICON_WALLET_SVG)
ICON_DOC_DATA_URI = _svg_to_data_uri(ICON_DOC_SVG)
ICON_CHAT_DATA_URI = _svg_to_data_uri(ICON_CHAT_SVG)
ICON_SETTINGS_DATA_URI = _svg_to_data_uri(ICON_SETTINGS_SVG)
ICON_SUPPORT_DATA_URI = _svg_to_data_uri(ICON_SUPPORT_SVG)

def get_left_dock_html() -> str:
    return f"""
    <aside class="left-floating-dock" aria-label="Quick Dock Navigation">
        <div class="dock-top-group">
            <div class="dock-icon-btn active" title="Dashboard">
                <img src="{ICON_HOME_DATA_URI}" width="18" height="18" alt="Home" />
            </div>
            <div class="dock-icon-btn" title="Wallets & Cards">
                <img src="{ICON_WALLET_DATA_URI}" width="18" height="18" alt="Cards" />
            </div>
            <div class="dock-icon-btn" title="Reports & Statements">
                <img src="{ICON_DOC_DATA_URI}" width="18" height="18" alt="Reports" />
            </div>
            <div class="dock-icon-btn" title="Conversations">
                <img src="{ICON_CHAT_DATA_URI}" width="18" height="18" alt="Messages" />
            </div>
            <div class="dock-icon-btn" title="Settings">
                <img src="{ICON_SETTINGS_DATA_URI}" width="18" height="18" alt="Settings" />
            </div>
        </div>
        <div class="dock-bottom-group">
            <div class="dock-icon-btn" title="FinFlow Support">
                <img src="{ICON_SUPPORT_DATA_URI}" width="18" height="18" alt="Support" />
            </div>
        </div>
    </aside>
    """
