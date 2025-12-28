import streamlit as st
import sys
import os

# Add project root to path so 'src' module can be found
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
from src.dashboard.config import PAGE_CONFIG
from src.dashboard.components import render_header, render_sidebar, render_explanations
from src.dashboard.data_loader import get_ticker_data, get_ticker_metadata
from src.dashboard.utils import create_divergence_chart

# 1. Configure Page (Must be first)
st.set_page_config(**PAGE_CONFIG)

def main():
    # 2. Render Sidebar & Get User Inputs
    filters = render_sidebar()
    
    # 3. Render Header
    render_header()
    
    selected_ticker = filters["ticker"]
    
    if not selected_ticker:
        st.warning("No tickers found in database. Please run the data collection pipeline first.")
        return

    # 4. Fetch Data
    with st.spinner(f"Loading data for {selected_ticker}..."):
        df = get_ticker_data(
            selected_ticker, 
            filters["start_date"], 
            filters["end_date"]
        )
        
        # Fetch metadata for display
        metadata = get_ticker_metadata(selected_ticker)
        company_name = metadata["name"] if metadata else selected_ticker

    # 5. Display Content
    if df.empty:
        st.info(f"No data available for {company_name} ({selected_ticker}) in the selected range.")
        
        st.markdown("""
        **Troubleshooting:**
        1. **Check Date Range:** Ensure you selected a date range where data exists (typically 2024 onwards).
        2. **Run Data Collection:** If this is a fresh setup, you may need to populate the database.
           ```bash
           python scripts/collect_data.py
           ```
        3. **Check Ticker:** Ensure `{selected_ticker}` is a supported ticker.
        """)
    else:
        st.subheader(f"{company_name} ({selected_ticker})")
        
        # 6. Generate & Display Chart
        fig = create_divergence_chart(
            df,
            show_retail=filters["show_retail"],
            show_institutional=filters["show_institutional"],
            show_price_z=filters["show_price_z"],
            show_raw_price=filters["show_raw_price"]
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # 7. Explanations
        render_explanations()

if __name__ == "__main__":
    main()
