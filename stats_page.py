import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import pandas as pd
from usage_tracker import usage_tracker

def apply_chart_styling(fig):
    """Apply consistent styling to charts for readability"""
    fig.update_layout(
        plot_bgcolor='white',
        paper_bgcolor='white',
        font_color='#1f2937',
        title_font_color='#1f2937',
        title_font_size=16,
        font_size=12,
        height=400,  # Force minimum height
        margin=dict(l=50, r=50, t=60, b=50),  # Add proper margins
        xaxis=dict(
            gridcolor='#e5e7eb',
            color='#1f2937',
            showgrid=True,
            zeroline=False
        ),
        yaxis=dict(
            gridcolor='#e5e7eb', 
            color='#1f2937',
            showgrid=True,
            zeroline=False
        )
    )
    return fig

def display_chart(fig):
    """Display chart with proper configuration"""
    st.plotly_chart(
        fig, 
        use_container_width=True, 
        config={
            'displayModeBar': False,  # Hide the entire toolbar
            'responsive': True,
            'displaylogo': False,
            'staticPlot': False,  # Keep interactivity but hide buttons
            'doubleClick': 'reset',  # Double-click to reset zoom
            'showTips': False,  # Hide tips
            'showAxisDragHandles': False,  # Hide axis drag handles
            'showAxisRangeEntryBoxes': False,  # Hide range entry boxes
            'modeBarButtonsToRemove': [
                'zoom2d', 'pan2d', 'select2d', 'lasso2d', 'zoomIn2d', 'zoomOut2d',
                'autoScale2d', 'resetScale2d', 'hoverClosestCartesian', 'hoverCompareCartesian',
                'zoom3d', 'pan3d', 'resetCameraDefault3d', 'resetCameraLastSave3d',
                'hoverClosest3d', 'orbitRotation', 'tableRotation', 'zoomInGeo',
                'zoomOutGeo', 'resetGeo', 'hoverClosestGeo', 'sendDataToCloud',
                'hoverClosestGl2d', 'hoverClosestPie', 'toggleHover', 'resetViews',
                'toggleSpikelines', 'resetViewMapbox', 'downloadPlot'
            ]
        }
    )

def show_statistics_page():
    """Display the hidden statistics page"""
    
    # Apply stats-specific styling to fix readability
    st.markdown("""
    <style>
    /* Override dashboard styling for stats page */
    .js-plotly-plot,
    .js-plotly-plot .plotly,
    .js-plotly-plot .plot-container,
    .js-plotly-plot .svg-container,
    .plotly-graph-div {
        background: white !important;
        color: #1f2937 !important;
    }
    
    /* Force chart text to be dark and readable */
    .js-plotly-plot text,
    .js-plotly-plot .xtick text,
    .js-plotly-plot .ytick text,
    .js-plotly-plot .legendtext,
    .js-plotly-plot .colorbar text {
        fill: #1f2937 !important;
        color: #1f2937 !important;
    }
    
    /* Chart backgrounds should be white */
    .js-plotly-plot .bg,
    .js-plotly-plot .plot .bg,
    .js-plotly-plot rect.bg {
        fill: white !important;
    }
    
    /* Grid lines should be visible */
    .js-plotly-plot .gridlayer .crisp {
        stroke: #e5e7eb !important;
    }
    
    /* Force Streamlit containers to have white background on stats page */
    div[data-testid="stPlotlyChart"] {
        background: white !important;
        border: 1px solid #e5e7eb !important;
        border-radius: 8px !important;
        padding: 16px !important;
        min-height: 450px !important;
        height: auto !important;
    }
    
    /* Ensure the Plotly chart itself has proper dimensions */
    div[data-testid="stPlotlyChart"] .js-plotly-plot,
    div[data-testid="stPlotlyChart"] .plotly-graph-div {
        min-height: 400px !important;
        height: 400px !important;
        width: 100% !important;
    }
    
    /* Ensure dataframes are readable */
    div[data-testid="stDataFrame"],
    div[data-testid="stTable"] {
        background: white !important;
        color: #1f2937 !important;
        border: 1px solid #e5e7eb !important;
    }
    
    div[data-testid="stDataFrame"] *,
    div[data-testid="stTable"] * {
        color: #1f2937 !important;
        background: white !important;
    }
    
    /* Override any theme restrictions on chart heights */
    .stApp div[data-testid="stPlotlyChart"] {
        min-height: 450px !important;
        max-height: none !important;
    }
    
    /* Ensure charts are not compressed */
    .js-plotly-plot .plot-container .svg-container svg {
        min-height: 400px !important;
    }
    
    /* Force proper chart sizing */
    .main-svg {
        min-height: 400px !important;
        height: 400px !important;
    }
    
    /* Nuclear option: override all inherited theme restrictions */
    body div[data-testid="stPlotlyChart"],
    .stApp div[data-testid="stPlotlyChart"],
    [data-theme] div[data-testid="stPlotlyChart"] {
        min-height: 450px !important;
        height: auto !important;
        max-height: none !important;
        overflow: visible !important;
    }
    
    /* Ensure text is always visible */
    .js-plotly-plot text {
        fill: #1f2937 !important;
        font-size: 12px !important;
        opacity: 1 !important;
    }
    
    /* Hide all Plotly toolbar elements */
    .modebar,
    .modebar-container,
    .modebar-group,
    .modebar-btn,
    .js-plotly-plot .modebar,
    .js-plotly-plot .modebar-container,
    .plotly .modebar {
        display: none !important;
        visibility: hidden !important;
        opacity: 0 !important;
    }
    
    /* Hide any floating toolbar elements */
    div[data-testid="stPlotlyChart"] .modebar {
        display: none !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.title("📊 Dashboard Usage Statistics")
    st.markdown("*Interactive charts - hover for details, double-click to reset zoom*")
    st.markdown("---")
    
    # Get detailed stats
    stats = usage_tracker.get_detailed_stats()
    summary = stats['summary']
    
    # Summary metrics in columns
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            label="Total Visits",
            value=summary['total_visits'],
            delta=summary['visits_today'] if summary['visits_today'] > 0 else None
        )
    
    with col2:
        st.metric(
            label="Today's Visits",
            value=summary['visits_today'],
            delta=summary['visits_today'] - summary['visits_yesterday']
        )
    
    with col3:
        st.metric(
            label="Total Sessions",
            value=summary['total_sessions'],
            delta=summary['active_sessions'] if summary['active_sessions'] > 0 else None
        )
    
    # Additional info
    st.markdown("---")
    col1, col2 = st.columns(2)
    
    with col1:
        st.info(f"**Peak Hour:** {summary['peak_hour']}:00")
    
    with col2:
        if summary['first_visit']:
            first_visit = datetime.fromisoformat(summary['first_visit'])
            st.info(f"**First Visit:** {first_visit.strftime('%Y-%m-%d %H:%M')}")
        if summary['last_visit']:
            last_visit = datetime.fromisoformat(summary['last_visit'])
            st.info(f"**Last Visit:** {last_visit.strftime('%Y-%m-%d %H:%M')}")
    
    # Charts section
    st.markdown("---")
    st.subheader("📈 Usage Patterns")
    
    # Daily visits chart
    if stats['daily_visits']:
        st.markdown("### Daily Visits")
        daily_df = pd.DataFrame(
            list(stats['daily_visits'].items()),
            columns=['Date', 'Visits']
        )
        daily_df['Date'] = pd.to_datetime(daily_df['Date'])
        daily_df = daily_df.sort_values('Date')
        
        fig_daily = px.line(
            daily_df, 
            x='Date', 
            y='Visits',
            title='Daily Visits Over Time',
            markers=True
        )
        fig_daily.update_layout(
            xaxis_title="Date",
            yaxis_title="Number of Visits",
            hovermode='x unified'
        )
        fig_daily = apply_chart_styling(fig_daily)
        display_chart(fig_daily)
    
    
    # Hourly distribution
    if any(stats['hourly_distribution'].values()):
        st.markdown("### Hourly Usage Distribution")
        hourly_df = pd.DataFrame(
            [(int(hour), count) for hour, count in stats['hourly_distribution'].items()],
            columns=['Hour', 'Visits']
        )
        hourly_df = hourly_df.sort_values('Hour')
        
        fig_hourly = px.bar(
            hourly_df,
            x='Hour',
            y='Visits',
            title='Visits by Hour of Day'
        )
        fig_hourly.update_layout(
            xaxis_title="Hour of Day",
            yaxis_title="Number of Visits",
            xaxis=dict(tickmode='linear', tick0=0, dtick=1)
        )
        fig_hourly = apply_chart_styling(fig_hourly)
        display_chart(fig_hourly)
    
    # Weekly distribution
    if any(stats['daily_distribution'].values()):
        st.markdown("### Weekly Usage Distribution")
        day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        weekly_df = pd.DataFrame(
            [(day_names[int(day)], count) for day, count in stats['daily_distribution'].items()],
            columns=['Day', 'Visits']
        )
        
        fig_weekly = px.bar(
            weekly_df,
            x='Day',
            y='Visits',
            title='Visits by Day of Week'
        )
        fig_weekly.update_layout(
            xaxis_title="Day of Week",
            yaxis_title="Number of Visits"
        )
        fig_weekly = apply_chart_styling(fig_weekly)
        display_chart(fig_weekly)
    
    # Monthly visits
    if stats['monthly_visits']:
        st.markdown("### Monthly Visits")
        monthly_df = pd.DataFrame(
            list(stats['monthly_visits'].items()),
            columns=['Month', 'Visits']
        )
        monthly_df = monthly_df.sort_values('Month')
        
        fig_monthly = px.bar(
            monthly_df,
            x='Month',
            y='Visits',
            title='Monthly Visit Counts'
        )
        fig_monthly.update_layout(
            xaxis_title="Month",
            yaxis_title="Number of Visits"
        )
        fig_monthly = apply_chart_styling(fig_monthly)
        display_chart(fig_monthly)
    
    # Session info
    st.markdown("---")
    st.subheader("📊 Session Information")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Total Sessions", summary['total_sessions'])
    
    with col2:
        st.metric("Active Sessions", summary['active_sessions'])
    
    # User agents (simplified)
    if stats['user_agents']:
        st.markdown("---")
        st.subheader("🌐 Browser Information")
        
        # Simplify user agent strings for display
        simplified_agents = {}
        for agent, count in stats['user_agents'].items():
            if 'Chrome' in agent:
                browser = 'Chrome'
            elif 'Firefox' in agent:
                browser = 'Firefox'
            elif 'Safari' in agent and 'Chrome' not in agent:
                browser = 'Safari'
            elif 'Edge' in agent:
                browser = 'Edge'
            else:
                browser = 'Other'
            
            simplified_agents[browser] = simplified_agents.get(browser, 0) + count
        
        if simplified_agents:
            browser_df = pd.DataFrame(
                list(simplified_agents.items()),
                columns=['Browser', 'Visits']
            )
            
            fig_browsers = px.pie(
                browser_df,
                values='Visits',
                names='Browser',
                title='Browser Usage Distribution'
            )
            # Special handling for pie chart
            fig_browsers.update_layout(
                height=400,
                margin=dict(l=50, r=50, t=60, b=50),
                plot_bgcolor='white',
                paper_bgcolor='white',
                font_color='#1f2937',
                title_font_color='#1f2937',
                title_font_size=16,
                font_size=12
            )
            display_chart(fig_browsers)
    
    # Management section
    st.markdown("---")
    st.subheader("⚙️ Management")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🧹 Clean Old Sessions (30+ days)"):
            removed = usage_tracker.cleanup_old_sessions(30)
            st.success(f"Removed {removed} old sessions")
    
    with col2:
        if st.button("🔄 Refresh Statistics"):
            st.rerun()
    
    # Raw data (expandable)
    with st.expander("📄 Raw Statistics Data"):
        st.json(stats)
    
    st.markdown("---")
    st.caption("Statistics are automatically saved to `usage_stats.json` and persist across app restarts.")

def show_usage_api():
    """Show usage statistics in API format"""
    stats = usage_tracker.get_detailed_stats()
    return {
        "status": "success",
        "data": stats,
        "timestamp": datetime.now().isoformat()
    }