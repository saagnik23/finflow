import base64
from pathlib import Path

def get_b64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("ascii")

a38 = get_b64("src/assets/cursor-modern-black-36.png")
h38 = get_b64("src/assets/cursor-modern-hand-36.png")
ahi = get_b64("src/assets/modern-black-cursor-master.png")
hhi = get_b64("src/assets/modern-black-hand-master.png")

template = '''"""SpendStory Cursor Assets & Dual-Layer Implementation Module.

Exact modern black rounded cursor design:
- Arrow: 668x800 px master, apex hotspot at (2, 0) in 30x36 px web asset.
- Hand: 700x800 px master, fingertip hotspot at (10, 2) in 32x36 px web asset.
Scaled to display height 36px (Arrow: 30x36, hotspot 2, 0; Hand: 32x36, hotspot 10, 2).
"""

ARROW_HOTSPOT = (2, 0)
HAND_HOTSPOT = (10, 2)

ARROW_38_B64 = "''' + a38 + '''"
HAND_38_B64 = "''' + h38 + '''"
ARROW_HI_B64 = "''' + ahi + '''"
HAND_HI_B64 = "''' + hhi + '''"

ARROW_DATA_URI = f"data:image/png;base64,{ARROW_38_B64}"
HAND_DATA_URI = f"data:image/png;base64,{HAND_38_B64}"
ARROW_HI_DATA_URI = f"data:image/png;base64,{ARROW_HI_B64}"
HAND_HI_DATA_URI = f"data:image/png;base64,{HAND_HI_B64}"

def get_cursor_css(enabled: bool = True) -> str:
    """Return scoped CSS for custom illustrated cursor."""
    if not enabled:
        return """<style id="spendstory-cursor-css">/* Custom cursor disabled */</style>"""
    return f"""
    <style id="spendstory-cursor-css">
    @media (pointer: fine) {{
        /* Base page movement: Exact modern black arrow */
        html, body, .stApp, .stApp * {{
            cursor: url('{ARROW_DATA_URI}') 2 0, auto;
        }}
        
        /* Interactive targets: Modern black pointing hand */
        a, button, [role="button"], input[type="submit"], input[type="button"],
        .stButton > button, [data-testid="stBaseButton-secondary"], [data-testid="stBaseButton-primary"],
        select, [data-testid="stSelectbox"], [role="radiogroup"] label, .stRadio label,
        [role="tab"], [role="slider"], .donut-slice, .month-target, [data-baseweb="select"],
        .interactive, summary, [data-testid="stExpander"] summary {{
            cursor: url('{HAND_DATA_URI}') 10 2, pointer !important;
        }}
        
        /* Text input fields: Native I-beam */
        input[type="text"], input[type="number"], textarea, [contenteditable="true"] {{
            cursor: text !important;
        }}
    }}
    </style>
    """


def get_cursor_follower_html(enabled: bool = True) -> str:
    """Return HTML and client-side script for smooth visual follower overlay."""
    if not enabled:
        return """
        <script>
        (function() {
            const doc = window.parent?.document || document;
            const follower = doc.getElementById("spendstory-cursor-follower");
            if (follower) follower.remove();
            const style = doc.getElementById("spendstory-follower-style");
            if (style) style.remove();
        })();
        </script>
        """
    return f"""
    <div id="spendstory-cursor-anchor" style="display:none;" aria-hidden="true"></div>
    <script>
    (function() {{
        try {{
            const doc = window.parent?.document || document;
            const win = window.parent?.window || window;
            
            if (win.matchMedia && (win.matchMedia('(prefers-reduced-motion: reduce)').matches || win.matchMedia('(pointer: coarse)').matches)) {{
                return;
            }}
            
            if (doc.getElementById("spendstory-cursor-follower")) return;
            
            const style = doc.createElement("style");
            style.id = "spendstory-follower-style";
            style.textContent = `
                #spendstory-cursor-follower {{
                    position: fixed;
                    top: 0;
                    left: 0;
                    width: 40px;
                    height: 40px;
                    pointer-events: none;
                    z-index: 2147483647;
                    will-change: transform;
                    display: none;
                    user-select: none;
                    -webkit-user-select: none;
                }}
                #spendstory-cursor-follower.active {{
                    display: block;
                }}
                #spendstory-cursor-follower .cursor-img {{
                    position: absolute;
                    top: 0;
                    left: 0;
                    image-rendering: -webkit-optimize-contrast;
                    image-rendering: crisp-edges;
                }}
                #spendstory-cursor-follower .arrow-img {{
                    width: 30px;
                    height: 36px;
                    display: block;
                }}
                #spendstory-cursor-follower .hand-img {{
                    width: 32px;
                    height: 36px;
                    display: none;
                }}
                #spendstory-cursor-follower.is-interactive .arrow-img {{
                    display: none;
                }}
                #spendstory-cursor-follower.is-interactive .hand-img {{
                    display: block;
                }}
                #spendstory-cursor-follower.is-pressed {{
                    filter: brightness(0.97);
                }}
                @media (prefers-reduced-motion: reduce), (pointer: coarse) {{
                    #spendstory-cursor-follower {{ display: none !important; }}
                }}
            `;
            doc.head.appendChild(style);
            
            const follower = doc.createElement("div");
            follower.id = "spendstory-cursor-follower";
            follower.setAttribute("aria-hidden", "true");
            follower.innerHTML = '<img class="cursor-img arrow-img" src="{ARROW_HI_DATA_URI}" alt="" /><img class="cursor-img hand-img" src="{HAND_HI_DATA_URI}" alt="" />';
            doc.body.appendChild(follower);
            
            let targetX = -100, targetY = -100;
            let currentX = -100, currentY = -100;
            let isInteractive = false;
            let isPressed = false;
            let isText = false;
            let isVisible = false;
            let rafId = null;
            
            function onPointerMove(e) {{
                if (e.pointerType === "touch") {{
                    follower.classList.remove("active");
                    return;
                }}
                targetX = e.clientX;
                targetY = e.clientY;
                if (!isVisible) {{
                    isVisible = true;
                    currentX = targetX;
                    currentY = targetY;
                    follower.classList.add("active");
                }}
                
                const target = doc.elementFromPoint(e.clientX, e.clientY);
                if (target) {{
                    isText = !!target.closest('input[type="text"], input[type="number"], textarea, [contenteditable="true"]');
                    isInteractive = !isText && !!target.closest('button, a, [role="button"], select, [data-testid="stSelectbox"], .donut-slice, .month-target, [role="slider"], .stButton, [role="radiogroup"] label, .stRadio label, summary');
                }}
                if (isInteractive) {{
                    follower.classList.add("is-interactive");
                }} else {{
                    follower.classList.remove("is-interactive");
                }}
                follower.style.opacity = isText ? "0" : "1";
            }}
            
            function onPointerDown() {{
                isPressed = true;
                follower.classList.add("is-pressed");
            }}
            
            function onPointerUp() {{
                isPressed = false;
                follower.classList.remove("is-pressed");
            }}
            
            function onMouseLeave() {{
                isVisible = false;
                follower.classList.remove("active");
            }}
            
            function tick() {{
                if (isVisible) {{
                    currentX += (targetX - currentX) * 0.35;
                    currentY += (targetY - currentY) * 0.35;
                    
                    const offsetX = isInteractive ? -10 : -2;
                    const offsetY = isInteractive ? -2 : 0;
                    const scale = isPressed ? " scale(0.96)" : "";
                    const posX = Math.round((currentX + offsetX) * 10) / 10;
                    const posY = Math.round((currentY + offsetY) * 10) / 10;
                    
                    follower.style.transform = "translate3d(" + posX + "px, " + posY + "px, 0)" + scale;
                }}
                rafId = win.requestAnimationFrame(tick);
            }}
            
            win.addEventListener("pointermove", onPointerMove, {{ passive: true }});
            win.addEventListener("pointerdown", onPointerDown, {{ passive: true }});
            win.addEventListener("pointerup", onPointerUp, {{ passive: true }});
            doc.addEventListener("mouseleave", onMouseLeave, {{ passive: true }});
            
            rafId = win.requestAnimationFrame(tick);
            
            win.__spendstory_cursor_initialized = true;
        }} catch (err) {{
            console.warn("SpendStory custom cursor follower initialisation bypassed:", err);
        }}
    }})();
    </script>
    """
'''

with open("src/cursor_assets.py", "w") as f:
    f.write(template)
print("Wrote src/cursor_assets.py successfully!")
