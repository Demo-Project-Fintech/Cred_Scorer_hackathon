import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import sys
import os

sys.path.append('utils')
sys.path.append('..')

from utils.data_collector import DataCollector
from utils.model import CreditScoringModel
from config import COMPANIES

st.set_page_config(page_title="Company Comparison", page_icon="🔄", layout="wide")

st.title("🔄 Company Comparison")
st.markdown("Compare credit scores and financial metrics across multiple companies")

# Multi-select for companies
selected_companies = st.multiselect(
    "Select companies to compare (2-5 recommended):",
    list(COMPANIES.keys()),
    default=list(COMPANIES.keys())[:3]
)

if len(selected_companies) < 2:
    st.warning("Please select at least 2 companies to compare")
    st.stop()

# Load model (simplified for comparison page)
@st.cache_resource
def load_model_simple():
    collector = DataCollector()
    model = CreditScoringModel()
    
    # Quick training with available data
    companies_data = {}
    for name, ticker in COMPANIES.items():
        data = collector.get_complete_data(ticker)
        if data:
            companies_data[ticker] = data
            if len(companies_data) >= 5:  # Minimum for training
                break
    
    model.train_model(companies_data)
    return model

if st.button("🔄 Generate Comparison"):
    model = load_model_simple()
    collector = DataCollector()
    
    # Collect data for selected companies
    comparison_data = []
    
    progress_bar = st.progress(0)
    for i, company_name in enumerate(selected_companies):
        ticker = COMPANIES[company_name]
        data = collector.get_complete_data(ticker)
        
        if data:
            score = model.predict(data)
            
            comparison_data.append({
                'Company': company_name,
                'Ticker': ticker,
                'Credit Score': score,
                'Risk Level': 'Low' if score > 70 else 'Medium' if score > 50 else 'High',
                'Debt-to-Equity': data.get('debt_to_equity', 0),
                'Current Ratio': data.get('current_ratio', 0),
                'ROE (%)': data.get('return_on_equity', 0),
                'Profit Margin (%)': data.get('profit_margin', 0),
                'Sentiment Score': data.get('sentiment_score', 50),
                'Market Cap (B)': data.get('market_cap', 0) / 1e9,
                'Sector': data.get('sector', 'Unknown')
            })
        
        progress_bar.progress((i + 1) / len(selected_companies))
    
    if comparison_data:
        df = pd.DataFrame(comparison_data)
        
        # Credit Score Comparison Chart
        st.subheader("📊 Credit Score Comparison")
        
        # Enhanced bar chart with better styling
        fig = go.Figure(data=[
            go.Bar(
                x=df['Company'],
                y=df['Credit Score'],
                text=[f"{x:.1f}" for x in df['Credit Score']],
                textposition='auto',
                textfont=dict(size=12, color='white', family='Arial Black'),
                marker=dict(
                    color=[
                        '#00C851' if x > 70 else '#ffbb33' if x > 50 else '#ff4444' 
                        for x in df['Credit Score']
                    ],
                    line=dict(color='rgba(0,0,0,0.1)', width=1)
                ),
                hovertemplate='<b>%{x}</b><br>Credit Score: %{y:.1f}<br>Risk: %{customdata}<extra></extra>',
                customdata=df['Risk Level']
            )
        ])
        
        fig.update_layout(
            title=dict(
                text="Credit Scores by Company",
                font=dict(size=20, color='#2E4057', family='Arial Black'),
                x=0.5
            ),
            xaxis=dict(
                title=dict(text="Company", font=dict(size=14, color='#2E4057')),
                tickfont=dict(size=12, color='#2E4057'),
                tickangle=45
            ),
            yaxis=dict(
                title=dict(text="Credit Score (0-100)", font=dict(size=14, color='#2E4057')),
                tickfont=dict(size=12, color='#2E4057'),
                gridcolor='rgba(128,128,128,0.2)',
                range=[0, 100]
            ),
            height=450,
            margin=dict(l=60, r=60, t=80, b=120),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            showlegend=False
        )
        
        # Add risk zone lines
        fig.add_hline(y=70, line_dash="dash", line_color="#00C851", line_width=2,
                      annotation_text="Low Risk Threshold", annotation_position="top right")
        fig.add_hline(y=50, line_dash="dash", line_color="#ffbb33", line_width=2,
                      annotation_text="Medium Risk Threshold", annotation_position="top right")
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Multi-metric comparison radar chart
        st.subheader("🎯 Multi-Metric Comparison")
        
        # Create radar chart for comparison
        fig_radar = go.Figure()
        
        colors = ['#00C851', '#ffbb33', '#ff4444', '#2196F3', '#9C27B0']
        
        for i, (_, row) in enumerate(df.head(5).iterrows()):  # Limit to 5 companies for clarity
            # Normalize metrics for radar chart
            metrics = [
                min(100, max(0, row['Current Ratio'] * 50)),  # Liquidity
                min(100, max(0, row['ROE (%)'] * 5)),         # Profitability  
                min(100, max(0, 100 - row['Debt-to-Equity'])), # Financial Stability
                min(100, max(0, row['Sentiment Score'])),      # Market Sentiment
                row['Credit Score']                             # Overall Score
            ]
            
            categories = ['Liquidity', 'Profitability', 'Financial Stability', 'Market Sentiment', 'Credit Score']
            
            fig_radar.add_trace(go.Scatterpolar(
                r=metrics + [metrics[0]],  # Close the shape
                theta=categories + [categories[0]],
                fill='toself',
                fillcolor=f'rgba{tuple(list(bytes.fromhex(colors[i % len(colors)][1:])) + [0.1])}',
                line=dict(color=colors[i % len(colors)], width=2),
                marker=dict(color=colors[i % len(colors)], size=6),
                name=row['Company'],
                hovertemplate='<b>%{fullData.name}</b><br>%{theta}: %{r:.1f}<extra></extra>'
            ))
        
        fig_radar.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 100],
                    tickmode='linear',
                    tick0=0,
                    dtick=20,
                    gridcolor='rgba(128,128,128,0.3)',
                    gridwidth=1,
                    tickfont=dict(size=10, color='#2E4057')
                ),
                angularaxis=dict(
                    tickfont=dict(size=12, color='#2E4057', family='Arial'),
                    gridcolor='rgba(128,128,128,0.3)'
                ),
                bgcolor="rgba(0,0,0,0)"
            ),
            title=dict(
                text="Multi-Dimensional Company Comparison",
                font=dict(size=18, color='#2E4057', family='Arial Black'),
                x=0.5
            ),
            height=500,
            margin=dict(l=80, r=80, t=80, b=80),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.2,
                xanchor="center",
                x=0.5,
                font=dict(size=12, color='#2E4057')
            )
        )
        
        st.plotly_chart(fig_radar, use_container_width=True)
        
        # Detailed comparison table
        st.subheader("📋 Detailed Comparison")
        st.dataframe(df, use_container_width=True)
        
        # Best/Worst performers
        col1, col2 = st.columns(2)
        
        with col1:
            best_performer = df.loc[df['Credit Score'].idxmax()]
            st.success(f"🏆 **Best Credit Score**: {best_performer['Company']} ({best_performer['Credit Score']:.1f})")
        
        with col2:
            worst_performer = df.loc[df['Credit Score'].idxmin()]
            st.error(f"⚠️ **Highest Risk**: {worst_performer['Company']} ({worst_performer['Credit Score']:.1f})")