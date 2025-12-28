"""
Dashboard Utilities
Helper functions for chart generation and formatting.
"""
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from .config import COLORS, CHART_HEIGHT, CHART_THEME

def create_divergence_chart(
    df: pd.DataFrame, 
    show_retail: bool = True, 
    show_institutional: bool = True, 
    show_price_z: bool = False,
    show_raw_price: bool = False
):
    """
    Creates the main divergence interaction chart.
    """
    # Create figure with secondary y-axis
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    if df.empty:
        return fig
        
    # Defensive check for required columns
    required_cols = ['date', 'retail_search_z', 'institutional_z', 'price_z', 'price_close']
    missing_cols = [c for c in required_cols if c not in df.columns]
    
    if missing_cols:
        # If columns are missing, return empty figure (or handle gracefully)
        # In a real app, logging this would be good
        return fig

    # 1. Retail Sentiment Z-Score (The "Noise")
    if show_retail:
        fig.add_trace(
            go.Scatter(
                x=df['date'], 
                y=df['retail_search_z'],
                name="Retail Hype (Z-Score)",
                line=dict(color=COLORS["retail"], width=2, dash='dot'),
                hovertemplate="Retail Z: %{y:.2f}<extra></extra>"
            ),
            secondary_y=False
        )

    # 2. Institutional Holdings Z-Score (The "Signal")
    if show_institutional:
        # Check if we can fill area between this and Retail
        fill_arg = 'tonexty' if show_retail else None
        
        fig.add_trace(
            go.Scatter(
                x=df['date'], 
                y=df['institutional_z'],
                name="Smart Money (Z-Score)",
                line=dict(color=COLORS["institutional"], width=3),
                fill=fill_arg,
                fillcolor='rgba(41, 182, 246, 0.1)', # Subtle fill
                hovertemplate="Inst. Z: %{y:.2f}<extra></extra>"
            ),
            secondary_y=False
        )

    # 3. Price Z-Score (Optional comparison)
    if show_price_z:
        fig.add_trace(
            go.Scatter(
                x=df['date'], 
                y=df['price_z'],
                name="Price Deviation (Z-Score)",
                line=dict(color=COLORS["price"], width=1.5, dash='dash'),
                hovertemplate="Price Z: %{y:.2f}<extra></extra>"
            ),
            secondary_y=False
        )
    
    # 4. Raw Price Overlay (Secondary Axis)
    if show_raw_price:
        fig.add_trace(
            go.Scatter(
                x=df['date'],
                y=df['price_close'],
                name="Stock Price ($)",
                line=dict(color=COLORS["price"], width=1.5),
                opacity=0.3, # Lighter opacity to separate from indicators
                hovertemplate="Price: $%{y:.2f}<extra></extra>"
            ),
            secondary_y=True
        )

    # Layout Styling
    fig.update_layout(
        template=CHART_THEME,
        height=CHART_HEIGHT,
        title_text="",  # Managed by Streamlit header
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        margin=dict(l=20, r=20, t=30, b=20),
        hovermode="x unified"
    )

    # Axis Styling
    fig.update_yaxes(
        title_text="Divergence (Z-Score)",
        secondary_y=False,
        zeroline=True,
        zerolinecolor='rgba(255, 255, 255, 0.3)', # Brighter zero line
        zerolinewidth=2,
        gridcolor=COLORS["grid"]
    )
    
    if show_raw_price:
        fig.update_yaxes(
            title_text="Price ($)",
            secondary_y=True,
            showgrid=False
        )

    fig.update_xaxes(
        gridcolor=COLORS["grid"]
    )

    return fig
