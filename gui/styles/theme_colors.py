"""
Color definitions for dark and light themes.
"""

DARK_THEME = {
    # Background colors
    "bg_primary": "#1e1e1e",
    "bg_secondary": "#2b2b2b",
    "bg_tertiary": "#3d3d3d",
    "bg_alternate": "#252525",

    # Text colors
    "text_primary": "#e0e0e0",
    "text_secondary": "#a0a0a0",
    "text_white": "#ffffff",

    # Accent and highlight colors
    "accent": "#14ffec",
    "accent_hover": "#32ffee",
    "selection": "#0d7377",

    # State colors
    "success": "#00cc66",
    "warning": "#ffaa00",
    "error": "#ff4444",
    "info": "#00aaff",

    # Profit level colors
    "profit_high": "#00ff88",
    "profit_high_text": "#1a1a1a",
    "profit_medium": "#ffd700",
    "profit_medium_text": "#1a1a1a",
    "profit_low": "#ff6b6b",
    "profit_low_text": "#ffffff",

    # Borders and dividers
    "border_light": "#3d3d3d",
    "border_medium": "#5d5d5d",
    "border_dark": "#1a1a1a",

    # Table specific
    "header_bg": "#1a1a1a",
    "header_text": "#14ffec",
    "grid_line": "#3d3d3d",
    "spread_high": "#00ff88",
    "spread_medium": "#ffd700",
}

LIGHT_THEME = {
    # Background colors
    "bg_primary": "#ffffff",
    "bg_secondary": "#f5f5f5",
    "bg_tertiary": "#e0e0e0",
    "bg_alternate": "#fafafa",

    # Text colors
    "text_primary": "#1a1a1a",
    "text_secondary": "#666666",
    "text_white": "#ffffff",

    # Accent and highlight colors
    "accent": "#0066cc",
    "accent_hover": "#0055aa",
    "selection": "#0d7377",

    # State colors
    "success": "#00aa66",
    "warning": "#ff8800",
    "error": "#cc0000",
    "info": "#0088cc",

    # Profit level colors
    "profit_high": "#00cc66",
    "profit_high_text": "#ffffff",
    "profit_medium": "#ffaa00",
    "profit_medium_text": "#ffffff",
    "profit_low": "#ff4444",
    "profit_low_text": "#ffffff",

    # Borders and dividers
    "border_light": "#d0d0d0",
    "border_medium": "#a0a0a0",
    "border_dark": "#808080",

    # Table specific
    "header_bg": "#e0e0e0",
    "header_text": "#0066cc",
    "grid_line": "#d0d0d0",
    "spread_high": "#00cc66",
    "spread_medium": "#ffaa00",
}


def get_theme_colors(theme_name: str) -> dict:
    """
    Get color dictionary for specified theme.

    Args:
        theme_name: Either 'dark' or 'light'

    Returns:
        Dictionary of color values
    """
    if theme_name.lower() == 'light':
        return LIGHT_THEME
    return DARK_THEME
