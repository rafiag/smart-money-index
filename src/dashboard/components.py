"""
Dashboard Components
Reusable UI blocks to keep the main application file clean.
"""
import streamlit as st
from datetime import datetime, timedelta
from .config import TITLES, EXPLANATIONS, PAGE_CONFIG
from .data_loader import get_all_tickers

def render_header():
    """Renders the main page header."""
    st.title(TITLES["main"])
    st.markdown("### Interactive Divergence Explorer")

def render_sidebar():
    """
    Renders the sidebar controls and returns the user selection.
    Returns a dictionary of filter values.
    """
    st.sidebar.title(TITLES["sidebar"])
    
    # Stock Selection
    # Fetch available tickers dynamically
    available_tickers = get_all_tickers()
    
    if not available_tickers:
        # Fallback if DB is empty - don't show confusing hardcoded tickers
        st.warning("No tickers found. Please run data collection.")
        ticker_options = []
        format_func = lambda x: x
    else:
        ticker_options = [t["symbol"] for t in available_tickers]
        # Create a mapping for display
        name_map = {t["symbol"]: t["name"] for t in available_tickers}
        format_func = lambda x: f"{x} - {name_map.get(x, '')}"

    selected_ticker = st.sidebar.selectbox(
        "Select Stock",
        options=ticker_options,
        format_func=format_func,
        index=0 if ticker_options else None
    )

    st.sidebar.markdown("---")

    # Date Selection
    st.sidebar.subheader("Time Period")
    # Default to YTD
    min_date = datetime(2025, 1, 1)
    default_start = min_date
    default_end = datetime.now()
    
    start_date = st.sidebar.date_input(
        "Start Date", 
        default_start,
        min_value=min_date,
        max_value=datetime.now()
    )
    end_date = st.sidebar.date_input(
        "End Date", 
        default_end,
        min_value=min_date,
        max_value=datetime.now()
    )

    st.sidebar.markdown("---")

    # Data Toggles
    st.sidebar.subheader("Visualization Layers")
    
    show_retail = st.sidebar.checkbox("Show Retail Hype (Search)", value=True, help=EXPLANATIONS["retail"])
    show_institutional = st.sidebar.checkbox("Show Smart Money (Holdings)", value=True, help=EXPLANATIONS["institutional"])
    show_price_z = st.sidebar.checkbox("Show Price Deviation", value=False)
    show_raw_price = st.sidebar.checkbox("Overlay Stock Price ($)", value=True)

    return {
        "ticker": selected_ticker,
        "start_date": start_date,
        "end_date": end_date,
        "show_retail": show_retail,
        "show_institutional": show_institutional,
        "show_price_z": show_price_z,
        "show_raw_price": show_raw_price
    }

def render_explanations():
    """Renders the collapsible help section."""
    with st.expander("ℹ️ How to read this chart"):
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(EXPLANATIONS["z_score"])
        with col2:
            st.markdown(EXPLANATIONS["divergence"])
