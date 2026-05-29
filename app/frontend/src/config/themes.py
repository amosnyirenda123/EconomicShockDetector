LIGHT_THEME = {
    "primary": "#1f77b4",
    "background": "#ffffff",
    "text": "#2c3e50",
    "card_bg": "#f8f9fa"
}

DARK_THEME = {
    "primary": "#3498db",
    "background": "#1e1e1e",
    "text": "#ecf0f1",
    "card_bg": "#2d2d2d"
}

def get_theme(theme_name="light"):
    """Get theme configuration"""
    return LIGHT_THEME if theme_name == "light" else DARK_THEME