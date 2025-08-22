import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import sys
import os

# Add utils to path
sys.path.append('utils')
sys.path.append('.')

from utils.data_collector import DataCollector
from utils.model import CreditScoringModel
from utils.explainer import CreditExplainer
from config import COMPANIES, RISK_LEVELS

# Configure Streamlit
st.set_page_config(
    page_title="Credit Intelligence Platform",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'data_cache' not in st.session_state:
    st.session_state.data_cache = {}
if 'model' not in st.session_state:
    st.session_state.model = None
if 'last_update' not in st.session_state:
    st.session_state.last_update = None

# Custom CSS for modern UI
st.markdown("""
<style>
    /* Import modern fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global styling */
    .main {
        font-family: 'Inter', sans-serif;
    }
    
    /* Metric cards with gradient backgrounds */
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 12px;
        border: none;
        box-shadow: 0 8px 32px rgba(31, 38, 135, 0.37);
        backdrop-filter: blur(4px);
        border: 1px solid rgba(255, 255, 255, 0.18);
        color: white;
        margin-bottom: 1rem;
    }
    
    .risk-low { 
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%) !important; 
    }
    .risk-medium { 
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%) !important; 
    }
    .risk-high { 
        background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%) !important; 
        color: #333 !important;
    }
    .risk-very-high { 
        background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%) !important; 
    }
    
    /* Enhanced button styling */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1.5rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 16px rgba(102, 126, 234, 0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(102, 126, 234, 0.4);
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=600)  # Cache for 10 minutes
def load_company_data(ticker):
    """Load and cache company data"""
    collector = DataCollector()
    return collector.get_complete_data(ticker)

@st.cache_resource
def initialize_model():
    """Initialize and train model (cached)"""
    collector = DataCollector()
    model = CreditScoringModel()
    
    # Collect training data
    companies_data = {}
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for i, (name, ticker) in enumerate(COMPANIES.items()):
        status_text.text(f'Loading data for {name}...')
        data = collector.get_complete_data(ticker)
        if data:
            companies_data[ticker] = data
        progress_bar.progress((i + 1) / len(COMPANIES))
    
    status_text.text('Training model...')
    model.train_model(companies_data)
    
    progress_bar.empty()
    status_text.empty()
    
    return model, companies_data

def create_score_gauge(score, risk_category):
    """Create a modern gauge chart for credit score"""
    # Determine colors based on score
    if score >= 70:
        color = "#00C851"  # Green
        threshold_color = "#00C851"
    elif score >= 50:
        color = "#ffbb33"  # Amber
        threshold_color = "#ffbb33"
    elif score >= 30:
        color = "#ff4444"  # Red
        threshold_color = "#ff4444"
    else:
        color = "#CC0000"  # Dark Red
        threshold_color = "#CC0000"
    
    fig = go.Figure(go.Indicator(
        mode = "gauge+number+delta",
        value = score,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {
            'text': "Credit Score", 
            'font': {'size': 24, 'color': '#2E4057'}
        },
        number = {
            'font': {'size': 48, 'color': color}
        },
        delta = {'reference': 50, 'increasing': {'color': '#00C851'}, 'decreasing': {'color': '#ff4444'}},
        gauge = {
            'axis': {
                'range': [None, 100],
                'tickwidth': 1,
                'tickcolor': "#2E4057",
                'tickfont': {'size': 12, 'color': '#2E4057'}
            },
            'bar': {'color': color, 'thickness': 0.3},
            'steps': [
                {'range': [0, 30], 'color': "rgba(255, 68, 68, 0.2)"},    # Light red
                {'range': [30, 50], 'color': "rgba(255, 187, 51, 0.2)"},  # Light amber
                {'range': [50, 70], 'color': "rgba(255, 213, 79, 0.2)"},  # Light yellow
                {'range': [70, 100], 'color': "rgba(0, 200, 81, 0.2)"}    # Light green
            ],
            'threshold': {
                'line': {'color': threshold_color, 'width': 4},
                'thickness': 0.8,
                'value': score
            },
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "#E8E8E8"
        }
    ))
    
    fig.update_layout(
        height=350,
        margin=dict(l=20, r=20, t=40, b=20),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={'color': '#2E4057'}
    )
    return fig

def create_feature_importance_chart(feature_impacts):
    """Create modern feature importance visualization"""
    # Prepare data
    features = []
    impacts = []
    colors = []
    hover_text = []
    
    for feature, impact_data in feature_impacts.items():
        if isinstance(impact_data, dict):
            feature_name = feature.replace('_', ' ').title()
            features.append(feature_name)
            
            # Create impact score based on type and strength
            impact_score = impact_data.get('value', 0)
            if impact_data.get('impact_type') == 'negative':
                impact_score = -abs(impact_score) if impact_score > 0 else impact_score
            
            impacts.append(impact_score)
            
            # Enhanced color scheme
            if impact_data.get('impact_type') == 'positive':
                colors.append('#00C851')  # Modern green
            elif impact_data.get('impact_type') == 'negative':
                colors.append('#ff4444')  # Modern red
            else:
                colors.append('#6c757d')  # Modern gray
                
            # Add hover information
            hover_text.append(f"{feature_name}<br>Impact: {impact_score:.2f}<br>Type: {impact_data.get('impact_type', 'neutral').title()}")
    
    # Create horizontal bar chart with enhanced styling
    fig = go.Figure(data=[
        go.Bar(
            y=features,
            x=impacts,
            orientation='h',
            marker=dict(
                color=colors,
                line=dict(color='rgba(0,0,0,0.1)', width=1)
            ),
            text=[f"{x:.1f}" for x in impacts],
            textposition='auto',
            textfont=dict(color='white', size=11, family='Arial Black'),
            hovertemplate='%{customdata}<extra></extra>',
            customdata=hover_text
        )
    ])
    
    fig.update_layout(
        title=dict(
            text="Feature Impact Analysis",
            font=dict(size=20, color='#2E4057', family='Arial Black'),
            x=0.5
        ),
        xaxis=dict(
            title="Impact Score",
            title_font=dict(size=14, color='#2E4057'),
            tickfont=dict(size=12, color='#2E4057'),
            gridcolor='rgba(128,128,128,0.2)',
            zerolinecolor='rgba(128,128,128,0.3)',
            zerolinewidth=2
        ),
        yaxis=dict(
            title="Features",
            title_font=dict(size=14, color='#2E4057'),
            tickfont=dict(size=11, color='#2E4057'),
            gridcolor='rgba(128,128,128,0.1)'
        ),
        height=450,
        margin=dict(l=180, r=50, t=70, b=50),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        showlegend=False,
        hovermode='closest'
    )
    
    return fig

def display_news_analysis(news_data):
    """Display news sentiment analysis"""
    if not news_data.get('recent_news'):
        st.info("No recent news available")
        return
    
    st.subheader("📰 Recent News Analysis")
    
    # Sentiment summary
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("News Sentiment", news_data.get('sentiment_label', 'Neutral'))
    with col2:
        st.metric("Sentiment Score", f"{news_data.get('sentiment_score', 50):.1f}/100")
    with col3:
        st.metric("Articles Analyzed", news_data.get('news_count', 0))
    
    # Recent headlines
    st.write("**Recent Headlines:**")
    for news_item in news_data.get('recent_news', [])[:3]:
        sentiment_color = (
            "🟢" if news_item.get('sentiment', 0) > 0.1 else
            "🔴" if news_item.get('sentiment', 0) < -0.1 else "⚪"
        )
        
        st.info(f"{sentiment_color} **{news_item.get('title', 'No title')}**<br><small>Sentiment: {news_item.get('sentiment', 0):.2f} | {news_item.get('date', 'Unknown date')}</small>")

def main():
    # Header
    st.title("🏦 Real-Time Credit Intelligence Platform")
    st.markdown("**Explainable AI-Powered Credit Risk Assessment**")
    
    # Sidebar
    st.sidebar.header("📊 Company Selection")
    
    # Company selector
    company_options = list(COMPANIES.keys())
    selected_company = st.sidebar.selectbox(
        "Choose a company to analyze:",
        company_options,
        index=0
    )
    
    selected_ticker = COMPANIES[selected_company]
    
    # Analysis button
    if st.sidebar.button("🔄 Refresh Analysis", type="primary"):
        # Clear cache for this company
        if selected_ticker in st.session_state.data_cache:
            del st.session_state.data_cache[selected_ticker]
        st.rerun()
    
    # Auto-refresh toggle
    auto_refresh = st.sidebar.checkbox("🔄 Auto-refresh (demo)", value=False)
    if auto_refresh:
        st.sidebar.info("In production: Updates every 15 minutes")
    
    # Initialize model if needed
    if st.session_state.model is None:
        with st.spinner("Initializing Credit Intelligence System..."):
            st.session_state.model, training_data = initialize_model()
            st.success("✅ System initialized successfully!")
    
    model = st.session_state.model
    
    # Load company data
    with st.spinner(f"Analyzing {selected_company}..."):
        company_data = load_company_data(selected_ticker)
    
    if not company_data:
        st.error(f"❌ Could not load data for {selected_company}")
        return
    
    # Generate prediction and explanation
    explainer = CreditExplainer(model)
    score = model.predict(company_data)
    explanation = explainer.explain_prediction(company_data, score)
    
    # Main dashboard layout
    st.markdown("---")
    
    # Key metrics row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        risk_class = f"risk-{explanation['risk_category']['level'].lower().replace(' ', '-')}"
        st.markdown(f"""
        <div class="metric-card {risk_class}">
            <h3>Credit Score</h3>
            <h1>{score:.1f}/100</h1>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        risk_info = explanation['risk_category']
        st.markdown(f"""
        <div class="metric-card">
            <h3>Risk Level</h3>
            <h2>{risk_info['level']}</h2>
            <p>{risk_info['description']}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <h3>Sector</h3>
            <h2>{company_data.get('sector', 'Unknown')}</h2>
            <p>{company_data.get('industry', 'Unknown Industry')}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        market_cap = company_data.get('market_cap', 0)
        market_cap_str = f"${market_cap/1e9:.1f}B" if market_cap > 1e9 else f"${market_cap/1e6:.1f}M" if market_cap > 1e6 else f"${market_cap:,.0f}"
        st.markdown(f"""
        <div class="metric-card">
            <h3>Market Cap</h3>
            <h2>{market_cap_str}</h2>
            <p>Last Updated: {datetime.now().strftime('%H:%M')}</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Main content area with tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Score Analysis", "🔍 Detailed Explanation", "📈 Financial Metrics", "📰 News & Sentiment"])
    
    with tab1:
        col1, col2 = st.columns([1, 1])
        
        with col1:
            # Score gauge
            gauge_fig = create_score_gauge(score, explanation['risk_category'])
            st.plotly_chart(gauge_fig, use_container_width=True)
            
            # Key strengths and weaknesses
            st.subheader("💪 Key Strengths")
            if explanation['key_strengths']:
                for strength in explanation['key_strengths'][:3]:
                    st.success(f"**{strength['feature'].replace('_', ' ').title()}**: {strength.get('explanation', 'Positive factor')}")
            else:
                st.info("No significant strengths identified")
            
            st.subheader("⚠️ Key Concerns")
            if explanation['key_weaknesses']:
                for weakness in explanation['key_weaknesses'][:3]:
                    st.error(f"**{weakness['feature'].replace('_', ' ').title()}**: {weakness.get('explanation', 'Risk factor')}")
            else:
                st.success("No significant concerns identified")
        
        with col2:
            # Feature importance chart
            importance_fig = create_feature_importance_chart(explanation['feature_impacts'])
            st.plotly_chart(importance_fig, use_container_width=True)
    
    with tab2:
        # Executive summary
        st.subheader("📋 Executive Summary")
        st.info(explanation['summary'])
        
        # Detailed feature analysis
        st.subheader("🔬 Detailed Feature Analysis")
        
        for feature, impact_data in explanation['feature_impacts'].items():
            if isinstance(impact_data, dict):
                feature_name = feature.replace('_', ' ').title()
                value = impact_data.get('value', 0)
                impact_type = impact_data.get('impact_type', 'neutral')
                explanation_text = impact_data.get('explanation', 'No explanation available')
                
                # Color based on impact
                if impact_type == 'positive':
                    st.success(f"**{feature_name}**: {value:.2f} - {explanation_text}")
                elif impact_type == 'negative':
                    st.error(f"**{feature_name}**: {value:.2f} - {explanation_text}")
                else:
                    st.info(f"**{feature_name}**: {value:.2f} - {explanation_text}")
        
        # Recommendations
        if explanation['recommendations']:
            st.subheader("💡 Recommendations")
            for rec in explanation['recommendations']:
                priority_color = {
                    'Critical': '🔴',
                    'High': '🟠', 
                    'Medium': '🟡',
                    'Low': '🟢'
                }.get(rec['priority'], '⚪')
                
                st.markdown(f"{priority_color} **{rec['category']}** ({rec['priority']} Priority): {rec['recommendation']}")
    
    with tab3:
        # Financial metrics table
        st.subheader("💰 Key Financial Metrics")
        
        financial_metrics = {
            'Liquidity Ratios': {
                'Current Ratio': f"{company_data.get('current_ratio', 0):.2f}",
                'Quick Ratio': f"{company_data.get('quick_ratio', 0):.2f}"
            },
            'Profitability Ratios': {
                'Return on Equity (%)': f"{company_data.get('return_on_equity', 0):.1f}%",
                'Return on Assets (%)': f"{company_data.get('return_on_assets', 0):.1f}%",
                'Profit Margin (%)': f"{company_data.get('profit_margin', 0):.1f}%",
                'Operating Margin (%)': f"{company_data.get('operating_margin', 0):.1f}%"
            },
            'Leverage Ratios': {
                'Debt-to-Equity': f"{company_data.get('debt_to_equity', 0):.1f}",
            },
            'Growth Metrics': {
                'Revenue Growth (%)': f"{company_data.get('revenue_growth', 0):.1f}%",
                'Earnings Growth (%)': f"{company_data.get('earnings_growth', 0):.1f}%"
            },
            'Market Metrics': {
                'Price-to-Book': f"{company_data.get('price_to_book', 0):.2f}",
                'Price-to-Earnings': f"{company_data.get('price_to_earnings', 0):.1f}",
                'Beta': f"{company_data.get('beta', 0):.2f}",
                'Stock Volatility (%)': f"{company_data.get('stock_volatility', 0):.1f}%"
            }
        }
        
        # Display metrics in organized sections
        for section, metrics in financial_metrics.items():
            st.write(f"**{section}**")
            cols = st.columns(min(len(metrics), 4))
            for i, (metric, value) in enumerate(metrics.items()):
                with cols[i % 4]:
                    st.metric(metric, value)
            st.markdown("---")
    
    with tab4:
        display_news_analysis(company_data)
    
    # Footer
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.caption(f"📊 Data sources: Yahoo Finance, News APIs")
    with col2:
        st.caption(f"🤖 Model: XGBoost with SHAP explanations")
    with col3:
        st.caption(f"🕐 Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
