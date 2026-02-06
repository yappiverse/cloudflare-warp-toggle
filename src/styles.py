CLOUDFLARE_ORANGE = "#f48120"
CLOUDFLARE_ORANGE_DARK = "#e6711a"

CSS = f"""
/* Use system theme colors via GTK variables */

/* Header - subtle background */
#header-box {{
    padding: 24px 20px 16px 20px;
}}

#app-title {{
    font-size: 18px;
    font-weight: 600;
}}

#app-subtitle {{
    font-size: 11px;
    opacity: 0.6;
}}

/* Status Display */
#status-connected {{
    color: #22c55e;
    font-size: 16px;
    font-weight: 600;
}}

#status-disconnected {{
    font-size: 16px;
    font-weight: 600;
    opacity: 0.6;
}}

/* Tabs - centered using padding */
notebook header tabs tab {{
    padding: 12px 20px;
}}

notebook header tabs tab:checked {{
    color: {CLOUDFLARE_ORANGE};
    border-bottom: 2px solid {CLOUDFLARE_ORANGE};
}}

/* Tab Content */
#tab-content {{
    padding: 20px;
}}

/* Cards - use alpha for transparency that works with any theme */
#info-card {{
    background: alpha(currentColor, 0.08);
    border-radius: 8px;
    padding: 12px 16px;
}}

#card-label {{
    opacity: 0.6;
    font-size: 11px;
}}

#card-value {{
    font-size: 13px;
}}

/* Buttons - Cloudflare orange stays consistent */
#apply-button {{
    background: {CLOUDFLARE_ORANGE};
    color: white;
    border: none;
    border-radius: 6px;
    padding: 10px 24px;
    font-weight: 500;
    font-size: 13px;
}}

#apply-button:hover {{
    background: {CLOUDFLARE_ORANGE_DARK};
}}

#link-button {{
    color: {CLOUDFLARE_ORANGE};
    font-size: 12px;
    background: transparent;
    border: none;
}}

/* Delete button - red accent */
#delete-button {{
    background: alpha(#f44336, 0.1);
    color: #f44336;
    border: 1px solid #f44336;
    border-radius: 6px;
    padding: 10px 16px;
    font-weight: 500;
    font-size: 13px;
}}

#delete-button:hover {{
    background: alpha(#f44336, 0.2);
}}

/* Section Headers */
#section-title {{
    font-size: 12px;
    font-weight: 600;
    opacity: 0.6;
}}

/* Mode Selection */
#mode-item {{
    background: alpha(currentColor, 0.08);
    border-radius: 8px;
    padding: 12px 16px;
}}

#mode-item-selected {{
    background: alpha(currentColor, 0.08);
    border: 1px solid {CLOUDFLARE_ORANGE};
    border-radius: 8px;
    padding: 12px 16px;
}}

#mode-name {{
    font-size: 13px;
    font-weight: 500;
}}

#mode-desc {{
    opacity: 0.6;
    font-size: 11px;
}}
"""


def get_css_bytes():
    """Return CSS as bytes for GTK CSS provider"""
    return CSS.encode('utf-8')
