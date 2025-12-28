import streamlit as st
import pandas as pd
import os
from datetime import datetime

# Set page config
st.set_page_config(
    page_title="Smart Money Divergence Index",
    page_icon="📈",
    layout="wide",
)

# Title and Description
st.title("📈 Smart Money Divergence Index")
st.markdown("""
### Phase 1.3: Dashboard (Work in Progress)
This dashboard will visualize the divergence between institutional 'smart money' and retail 'hype'.

**Status:**
- [x] Phase 1.1: Data Collection
- [x] Phase 1.2: Z-Score Engine (In Progress)
- [ ] Phase 1.3: Interactive Dashboard (Current)
""")

# Sidebar
st.sidebar.title("Controls")
ticker = st.sidebar.selectbox(
    "Select Ticker",
    ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA", "ASTS", "MU", "COIN", "SMCI", "HOOD"]
)

# Placeholder for the chart
st.info(f"Visualizing data for {ticker}...")
st.warning("Data visualization components are being implemented in Phase 1.3.")

# Environment Info
st.sidebar.markdown("---")
st.sidebar.write(f"**Environment:** {os.getenv('ENVIRONMENT', 'development')}")
st.sidebar.write(f"**Database:** {'PostgreSQL' if 'postgresql' in os.getenv('DATABASE_URL', '') else 'SQLite'}")
st.sidebar.write(f"**Last Sync:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
