"""
Dashboard Configuration
Centralizes UI settings, color themes, and chart constants for easy maintenance.
"""

# Page Settings
PAGE_CONFIG = {
    "page_title": "Smart Money Divergence Index",
    "page_icon": "📈",
    "layout": "wide",
    "initial_sidebar_state": "expanded"
}

# Color Palette (Dark Mode Optimized)
COLORS = {
    "background": "#0E1117",  # Streamlit default dark
    "text": "#FAFAFA",
    "institutional": "#29B6F6",  # Light Blue
    "retail": "#66BB6A",        # Green
    "price": "#FFA726",         # Orange
    "grid": "#262730",          # Dark Grey for grid lines
    "divergence_high": "#EF5350", # Red (High Divergence)
    "divergence_low": "#26A69A"   # Teal (Low Divergence)
}

# Chart Settings
CHART_HEIGHT = 600
CHART_THEME = "plotly_dark"

# Caching
import os
IS_DEV = os.getenv('ENVIRONMENT', 'development') == 'development'
CACHE_TTL = 300 if IS_DEV else 3600  # 5 min in dev, 1 hour in prod

# Text Content
TITLES = {
    "main": "📈 Smart Money Divergence Index",
    "sidebar": "Controls",
    "price_chart": "Price vs. Divergence Analysis"
}

# Tooltips and Explanations
EXPLANATIONS = {
    "z_score": """
    **What is a Z-Score?**
    It measures how far a value is from its 'normal' average.
    - **0**: Completely normal.
    - **+2.0**: Very high (2 standard deviations above average).
    - **-2.0**: Very low (2 standard deviations below average).
    """,
    "divergence": """
    **Divergence:** When 'Smart Money' (Institutions) and 'Retail Hype' move in opposite directions.
    """,
    "institutional": """
    **Institutional Holdings (Smart Money):**
    Data from SEC filings (13F and Form 4) showing ownership by large funds and company insiders.
    Typically represents longer-term, fundamental conviction.
    """,
    "retail": """
    **Retail Sentiment (Hype):**
    Derived from Google Trends search volume. 
    Represents short-term interest and momentum from individual investors.
    """
}
