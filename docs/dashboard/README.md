# Interactive Dashboard Documentation

## Overview
The Interactive Dashboard is the primary user interface for the Smart Money Divergence Index. It allows users to visualize the divergence between institutional capital flows ("Smart Money") and retail investor sentiment ("Hype").

## Features (Phase 1.3)
- **Stock Selection**: Dropdown menu for 12 supported tickers.
- **Date Range Filter**: Custom start and end dates.
- **Z-Score Visualization**:
    - **Retail Z-Score (Green)**: Normalized Google Trends search volume.
    - **Institutional Z-Score (Blue)**: Normalized 13F/Form 4 holdings data.
    - **Price Z-Score (Orange)**: Normalized price deviation (optional).
- **Price Overlay**: Raw stock price on a secondary Y-axis.
- **Interactive Explanations**: Educational tooltips explaining key concepts.

## Setup
The dashboard is built with [Streamlit](https://streamlit.io/).

### Prerequisites
Ensure dependencies are installed:
```bash
pip install -r requirements.txt
```

### Running Locally
To launch the dashboard:
```bash
streamlit run src/dashboard/app.py
```
The app will open in your default browser at `http://localhost:8501`.

## Navigation
For technical architecture details, see [DASHBOARD.md](./DASHBOARD.md).
