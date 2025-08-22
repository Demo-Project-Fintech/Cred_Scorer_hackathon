import streamlit as st
import time
import random
import plotly.graph_objects as go
from datetime import datetime, timedelta
import pandas as pd

st.set_page_config(page_title="Real-Time Demo", page_icon="⚡", layout="wide")

st.title("⚡ Real-Time Credit Monitoring Demo")
st.markdown("Simulated real-time credit score updates (in production, this would connect to live data feeds)")

# Demo controls
col1, col2, col3 = st.columns(3)
with col1:
    demo_company = st.selectbox("Select Company for Demo", ["Apple Inc.", "Tesla Inc.", "JPMorgan Chase"])
with col2:
    update_interval = st.slider("Update Interval (seconds)", 1, 10, 3)
with col3:
    run_demo = st.checkbox("🔄 Run Real-Time Demo")

if run_demo:
    # Initialize demo data
    if 'demo_data' not in st.session_state:
        st.session_state.demo_data = {
            'timestamps': [],
            'scores': [],
            'events': []
        }
        base_score = random.uniform(60, 80)
        st.session_state.demo_base_score = base_score
    
    # Placeholder for charts
    score_chart = st.empty()
    metrics_col1, metrics_col2, metrics_col3 = st.columns(3)
    events_placeholder = st.empty()
    
    # Demo loop
    for i in range(60):  # Run for 60 iterations
        if not run_demo:  # Check if user stopped demo
            break
            
        # Simulate score changes
        current_time = datetime.now()
        
        # Random walk for score
        change = random.gauss(0, 0.5)
        new_score = max(0, min(100, st.session_state.demo_base_score + change))
        st.session_state.demo_base_score = new_score
        
        # Add to data
        st.session_state.demo_data['timestamps'].append(current_time)
        st.session_state.demo_data['scores'].append(new_score)
        
        # Simulate events
        if random.random() < 0.1:  # 10% chance of event
            events = [
                "📈 Quarterly earnings beat expectations",
                "📉 Credit rating agency review initiated", 
                "📊 New debt issuance announced",
                "💰 Major acquisition completed",
                "⚠️ Regulatory investigation reported",
                "🎯 Guidance raised for next quarter"
            ]
            event = random.choice(events)
            st.session_state.demo_data['events'].append({
                'time': current_time,
                'event': event,
                'score_impact': change
            })
        
        # Update visualizations
        with score_chart.container():
            # Create real-time chart
            if len(st.session_state.demo_data['scores']) > 1:
                fig = go.Figure()
                
                # Main score line
                fig.add_trace(go.Scatter(
                    x=st.session_state.demo_data['timestamps'][-20:],  # Last 20 points
                    y=st.session_state.demo_data['scores'][-20:],
                    mode='lines+markers',
                    name='Credit Score',
                    line=dict(
                        color='#00C851',
                        width=4,
                        shape='spline',
                        smoothing=1.3
                    ),
                    marker=dict(
                        color='#00C851',
                        size=8,
                        line=dict(color='white', width=2)
                    ),
                    fill='tonexty',
                    fillcolor='rgba(0, 200, 81, 0.1)',
                    hovertemplate='<b>Real-Time Credit Score</b><br>Time: %{x}<br>Score: %{y:.1f}<extra></extra>'
                ))
                
                # Add risk zone backgrounds
                fig.add_hrect(y0=70, y1=100, fillcolor="rgba(0, 200, 81, 0.1)", 
                             layer="below", line_width=0, annotation_text="Low Risk Zone",
                             annotation_position="top left")
                fig.add_hrect(y0=50, y1=70, fillcolor="rgba(255, 187, 51, 0.1)", 
                             layer="below", line_width=0, annotation_text="Medium Risk Zone",
                             annotation_position="top left")
                fig.add_hrect(y0=0, y1=50, fillcolor="rgba(255, 68, 68, 0.1)", 
                             layer="below", line_width=0, annotation_text="High Risk Zone",
                             annotation_position="top left")
                
                fig.update_layout(
                    title=dict(
                        text=f"🔴 LIVE: Real-Time Credit Score - {demo_company}",
                        font=dict(size=20, color='#2E4057', family='Arial Black'),
                        x=0.5
                    ),
                    xaxis=dict(
                        title=dict(text="Time", font=dict(size=14, color='#2E4057')),
                        tickfont=dict(size=12, color='#2E4057'),
                        gridcolor='rgba(128,128,128,0.2)'
                    ),
                    yaxis=dict(
                        title=dict(text="Credit Score", font=dict(size=14, color='#2E4057')),
                        tickfont=dict(size=12, color='#2E4057'),
                        gridcolor='rgba(128,128,128,0.2)',
                        range=[0, 100]
                    ),
                    height=450,
                    margin=dict(l=60, r=60, t=80, b=60),
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    showlegend=False,
                    hovermode='x unified'
                )
                
                st.plotly_chart(fig, use_container_width=True)
        
        # Update metrics
        with metrics_col1:
            st.metric(
                "Current Score", 
                f"{new_score:.1f}",
                f"{change:+.1f}" if i > 0 else None
            )
        
        with metrics_col2:
            volatility = pd.Series(st.session_state.demo_data['scores'][-10:]).std() if len(st.session_state.demo_data['scores']) >= 10 else 0
            st.metric("10-Point Volatility", f"{volatility:.1f}")
        
        with metrics_col3:
            risk_level = "Low" if new_score > 70 else "Medium" if new_score > 50 else "High"
            st.metric("Risk Level", risk_level)
        
        # Show recent events
        with events_placeholder.container():
            if st.session_state.demo_data['events']:
                st.subheader("📢 Recent Events")
                for event_data in st.session_state.demo_data['events'][-3:]:  # Last 3 events
                    impact_indicator = "📈" if event_data['score_impact'] > 0 else "📉" if event_data['score_impact'] < 0 else "➡️"
                    st.info(f"{impact_indicator} {event_data['event']} ({event_data['time'].strftime('%H:%M:%S')})")
        
        # Wait for next update
        time.sleep(update_interval)
    
    if run_demo:
        st.success("✅ Demo completed! In production, this would run continuously with live data feeds.")

else:
    st.info("👆 Enable 'Run Real-Time Demo' above to see simulated real-time credit score updates")
    
    # Show demo features
    st.markdown("""
    ## 🚀 Real-Time Features (Production)
    
    **Data Sources (Live Updates):**
    - 📊 Market data feeds (Yahoo Finance, Bloomberg API)
    - 📰 News sentiment analysis (NewsAPI, social media)
    - 🏛️ Economic indicators (Federal Reserve, World Bank)
    - 📋 SEC filings (EDGAR real-time notifications)
    
    **Update Frequencies:**
    - Market data: Every 15 minutes during trading hours
    - News sentiment: Every 30 minutes
    - Company filings: Real-time notifications
    - Economic data: As published by sources
    
    **Alert System:**
    - Score changes > 5 points: Instant alert
    - Major news events: Real-time notifications
    - Regulatory filings: Same-day analysis
    """)