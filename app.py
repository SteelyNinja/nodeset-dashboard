import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
import os
from datetime import datetime, timedelta
from collections import Counter
import numpy as np
from pathlib import Path

# Dashboard configuration
st.set_page_config(
    page_title="NodeSet Validator Monitor",
    page_icon="🔗",
    layout="wide",
    initial_sidebar_state="collapsed"  # Collapse sidebar by default
)

# Custom CSS for better styling and responsive design
st.markdown("""
<style>
    .metric-container {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        margin: 0.5rem 0;
    }

    .big-font {
        font-size: 24px !important;
        font-weight: bold;
    }

    .status-good { color: #28a745; }
    .status-warning { color: #ffc107; }
    .status-danger { color: #dc3545; }

    div[data-testid="metric-container"] {
        background-color: #f8f9fa;
        border: 1px solid #dee2e6;
        padding: 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 0.125rem 0.25rem rgba(0, 0, 0, 0.075);
    }

    /* Hide sidebar completely */
    .css-1d391kg {
        display: none;
    }

    section[data-testid="stSidebar"] {
        display: none;
    }

    /* Responsive design adjustments */
    .main .block-container {
        padding-left: 1rem;
        padding-right: 1rem;
        max-width: none;
    }

    /* Mobile-friendly adjustments */
    @media (max-width: 768px) {
        .main .block-container {
            padding-left: 0.5rem;
            padding-right: 0.5rem;
        }

        div[data-testid="metric-container"] {
            padding: 0.5rem;
            margin: 0.25rem 0;
        }

        h1 {
            font-size: 1.5rem !important;
        }

        .metric-container {
            padding: 0.5rem;
            margin: 0.25rem 0;
        }
    }

    /* Tablet adjustments */
    @media (min-width: 769px) and (max-width: 1024px) {
        .main .block-container {
            padding-left: 0.75rem;
            padding-right: 0.75rem;
        }
    }

    /* Wide screen adjustments */
    @media (min-width: 1400px) {
        .main .block-container {
            max-width: 1400px;
            margin: 0 auto;
        }
    }

    /* Health status responsive text */
    @media (max-width: 768px) {
        .health-summary {
            font-size: 0.9rem;
            line-height: 1.4;
        }
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=300)  # Cache for 5 minutes
def load_validator_data():
    """Load and process validator data from cache file"""
    cache_files = [
        'nodeset_validator_tracker_cache.json',
        './data/nodeset_validator_tracker_cache.json',
        '../nodeset_validator_tracker_cache.json'
    ]

    for cache_file in cache_files:
        if os.path.exists(cache_file):
            try:
                with open(cache_file, 'r') as f:
                    cache = json.load(f)
                return cache, cache_file
            except Exception as e:
                st.error(f"❌ Error loading {cache_file}: {str(e)}")

    return None, None

def calculate_concentration_metrics(operator_validators):
    """Calculate concentration and decentralization metrics"""
    if not operator_validators:
        return {}

    total_validators = sum(operator_validators.values())
    operator_counts = list(operator_validators.values())

    # Sort in ascending order for proper Gini calculation
    operator_counts.sort()

    # Gini coefficient calculation - CORRECTED VERSION
    n = len(operator_counts)
    if n == 0 or total_validators == 0:
        return {}

    # Standard Gini formula
    index = np.arange(1, n + 1)  # 1, 2, 3, ..., n
    gini = (2 * np.sum(index * operator_counts)) / (n * total_validators) - (n + 1) / n

    # Ensure Gini is between 0 and 1
    gini = max(0, min(1, gini))

    # Sort in descending order for concentration ratios
    operator_counts_desc = sorted(operator_counts, reverse=True)

    # Concentration ratios
    top_1_pct = (operator_counts_desc[0] / total_validators) * 100 if operator_counts_desc else 0
    top_5_pct = (sum(operator_counts_desc[:min(5, len(operator_counts_desc))]) / total_validators) * 100
    top_10_pct = (sum(operator_counts_desc[:min(10, len(operator_counts_desc))]) / total_validators) * 100

    return {
        'gini_coefficient': gini,
        'top_1_concentration': top_1_pct,
        'top_5_concentration': top_5_pct,
        'top_10_concentration': top_10_pct,
        'total_operators': len(operator_validators),
        'total_validators': total_validators
    }

def get_performance_category(performance):
    """Categorize performance levels"""
    if performance >= 99.5:
        return 'Excellent'
    elif performance >= 98.5:
        return 'Good'
    elif performance >= 95.0:
        return 'Average'
    else:
        return 'Poor'

def create_performance_analysis(operator_performance, operator_validators):
    """Create performance analysis visualizations"""
    if not operator_performance:
        return None, None, None

    # Combine performance with validator counts
    perf_data = []
    for addr, performance in operator_performance.items():
        validator_count = operator_validators.get(addr, 0)
        if validator_count > 0:  # Only include operators with validators
            perf_data.append({
                'operator': f"{addr[:8]}...{addr[-6:]}",
                'full_address': addr,
                'performance': performance,
                'validator_count': validator_count,
                'performance_category': get_performance_category(performance)
            })

    if not perf_data:
        return None, None, None

    df = pd.DataFrame(perf_data)

    # FIXED: Force categorical order for legend
    df['performance_category'] = pd.Categorical(df['performance_category'],
                                              categories=['Excellent', 'Good', 'Average', 'Poor'],
                                              ordered=True)

    # Performance vs Validator Count scatter plot
    fig_scatter = px.scatter(
        df,
        x='validator_count',
        y='performance',
        size='validator_count',
        color='performance_category',
        hover_data=['operator'],
        title="Operator Performance vs Validator Count",
        labels={
            'validator_count': 'Number of Validators',
            'performance': 'Performance (%)',
            'performance_category': 'Performance Level'
        },
        color_discrete_map={
            'Excellent': '#17a2b8',
            'Good': '#28a745',
            'Average': '#ffc107',
            'Poor': '#dc3545'
        },
        category_orders={'performance_category': ['Excellent', 'Good', 'Average', 'Poor']}
    )
    fig_scatter.update_layout(height=500)

    # Performance distribution histogram
    fig_hist = px.histogram(
        df,
        x='performance',
        nbins=20,
        title="Distribution of Operator Performance",
        labels={'x': 'Performance (%)', 'y': 'Number of Operators'},
        color_discrete_sequence=['#667eea']
    )
    fig_hist.update_layout(height=400)

    return fig_scatter, fig_hist, df

def create_concentration_pie(operator_validators, title="Validator Distribution"):
    """Create pie chart showing operator concentration"""
    if not operator_validators:
        fig = go.Figure()
        fig.add_annotation(text="No data available", x=0.5, y=0.5, showarrow=False)
        return fig

    # Group smaller operators
    sorted_ops = sorted(operator_validators.items(), key=lambda x: x[1], reverse=True)

    labels = []
    values = []

    # Show top 8 operators individually
    for i, (addr, count) in enumerate(sorted_ops[:8]):
        labels.append(f"{addr[:6]}...{addr[-4:]} ({count})")
        values.append(count)

    # Group remaining operators
    if len(sorted_ops) > 8:
        remaining_count = sum(count for _, count in sorted_ops[8:])
        remaining_ops = len(sorted_ops) - 8
        labels.append(f"Others ({remaining_ops} operators)")
        values.append(remaining_count)

    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=0.4,
        textinfo='label+percent',
        textposition='outside'
    )])

    fig.update_layout(
        title=title,
        showlegend=True,
        height=500,
        font=dict(size=12)
    )

    return fig

def create_distribution_histogram(operator_validators):
    """Create histogram of validator counts per operator with discrete bins"""
    if not operator_validators:
        return go.Figure()

    validator_counts = list(operator_validators.values())

    # Get the range of validator counts
    min_validators = min(validator_counts)
    max_validators = max(validator_counts)

    fig = px.histogram(
        x=validator_counts,
        title="Distribution of Validators per Operator",
        labels={'x': 'Validators per Operator', 'y': 'Number of Operators'},
        color_discrete_sequence=['#667eea']
    )

    # Override with custom bins to ensure whole number alignment
    fig.update_traces(
        xbins=dict(
            start=min_validators - 0.5,
            end=max_validators + 0.5,
            size=1  # Each bin represents exactly 1 validator
        )
    )

    # Set x-axis to show only whole numbers
    fig.update_layout(
        height=400,
        showlegend=False,
        xaxis=dict(
            tick0=min_validators,
            dtick=1,  # Show tick marks at every whole number
            tickmode='linear'
        ),
        bargap=0.1  # Small gap between bars for clarity
    )

    return fig

def create_concentration_curve(operator_validators):
    """Create Lorenz curve showing concentration"""
    if not operator_validators:
        return go.Figure()

    validator_counts = sorted(operator_validators.values())
    n = len(validator_counts)
    total_validators = sum(validator_counts)

    if total_validators == 0:
        return go.Figure()

    # Calculate cumulative percentages
    cum_operators = np.arange(1, n + 1) / n * 100
    cum_validators = np.cumsum(validator_counts) / total_validators * 100

    # Perfect equality line
    equality_line = np.linspace(0, 100, 100)

    fig = go.Figure()

    # Add Lorenz curve
    fig.add_trace(go.Scatter(
        x=cum_operators,
        y=cum_validators,
        mode='lines+markers',
        name='Actual Distribution',
        line=dict(color='#667eea', width=3),
        marker=dict(size=4)
    ))

    # Add perfect equality line
    fig.add_trace(go.Scatter(
        x=equality_line,
        y=equality_line,
        mode='lines',
        name='Perfect Equality',
        line=dict(color='#FF6B6B', dash='dash', width=2)
    ))

    fig.update_layout(
        title="Validator Concentration Curve (Lorenz Curve)",
        xaxis_title="Cumulative % of Operators",
        yaxis_title="Cumulative % of Validators",
        height=500,
        hovermode='x unified'
    )

    return fig

def create_top_operators_table(operator_validators, operator_exited):
    """Create formatted table of top operators"""
    if not operator_validators:
        return pd.DataFrame()

    data = []
    for addr, total_count in operator_validators.items():
        exited_count = operator_exited.get(addr, 0)
        active_count = total_count - exited_count
        exit_rate = (exited_count / total_count * 100) if total_count > 0 else 0

        data.append({
            'Rank': 0,  # Will be set after sorting
            'Operator': addr,
            'Full Address': addr,
            'Active': active_count,
            'Total': total_count,
            'Exited': exited_count,
            'Exit Rate': f"{exit_rate:.1f}%",
            'Market Share': f"{(active_count / sum(v - operator_exited.get(k, 0) for k, v in operator_validators.items()) * 100):.2f}%"
        })

    df = pd.DataFrame(data)
    df = df.sort_values('Active', ascending=False).reset_index(drop=True)
    df['Rank'] = range(1, len(df) + 1)

    return df

def create_performance_table(operator_performance, operator_validators, operator_exited):
    """Create enhanced operator table with performance data"""
    if not operator_performance:
        return pd.DataFrame()

    data = []
    for addr, performance in operator_performance.items():
        total_count = operator_validators.get(addr, 0)
        exited_count = operator_exited.get(addr, 0)
        active_count = total_count - exited_count

        if total_count > 0:  # Only include operators with validators
            data.append({
                'Rank': 0,  # Will be set after sorting
                'Operator': addr,
                'Full Address': addr,
                'Performance': f"{performance:.2f}%",
                'Performance_Raw': performance,
                'Category': get_performance_category(performance),
                'Active': active_count,
                'Total': total_count,
                'Exited': exited_count,
            })

    if not data:
        return pd.DataFrame()

    df = pd.DataFrame(data)
    # Sort by performance first, then by active validators
    df = df.sort_values(['Performance_Raw', 'Active'], ascending=[False, False]).reset_index(drop=True)
    df['Rank'] = range(1, len(df) + 1)

    return df

def display_health_status(concentration_metrics, total_active, total_exited):
    """Display network health indicators"""
    st.subheader("🏥 Network Health Status")

    col1, col2, col3 = st.columns(3)

    with col1:
        # Decentralization health
        gini = concentration_metrics.get('gini_coefficient', 0)
        if gini < 0.5:
            status = "🟢 Good"
            color = "status-good"
        elif gini < 0.7:
            status = "🟡 Moderate"
            color = "status-warning"
        else:
            status = "🔴 Concentrated"
            color = "status-danger"

        st.markdown(f"**Decentralization:** <span class='{color}'>{status}</span>", unsafe_allow_html=True)
        st.caption(f"Gini: {gini:.3f} (lower is better)")

    with col2:
        # Exit rate health
        total_validators = total_active + total_exited
        exit_rate = (total_exited / total_validators * 100) if total_validators > 0 else 0

        if exit_rate < 5:
            status = "🟢 Low"
            color = "status-good"
        elif exit_rate < 15:
            status = "🟡 Moderate"
            color = "status-warning"
        else:
            status = "🔴 High"
            color = "status-danger"

        st.markdown(f"**Exit Rate:** <span class='{color}'>{status}</span>", unsafe_allow_html=True)
        st.caption(f"{exit_rate:.1f}% validators exited")

    with col3:
        # Operator diversity - UPDATED THRESHOLDS
        total_ops = concentration_metrics.get('total_operators', 0)
        avg_validators = (total_active / total_ops) if total_ops > 0 else 0

        if avg_validators < 50:
            status = "🟢 Low"
            color = "status-good"
        elif avg_validators <= 100:
            status = "🟡 Moderate"
            color = "status-warning"
        else:
            status = "🔴 High"
            color = "status-danger"

        st.markdown(f"**Operator Size:** <span class='{color}'>{status}</span>", unsafe_allow_html=True)
        st.caption(f"{avg_validators:.1f} avg validators/operator")

def display_performance_health(operator_performance, operator_validators):
    """Display performance-based health indicators"""
    if not operator_performance:
        return

    st.subheader("🎯 Performance Health Status")

    # Calculate weighted average performance
    total_weighted_performance = 0
    total_validators = 0

    perf_categories = {'Excellent': 0, 'Good': 0, 'Average': 0, 'Poor': 0}

    for addr, performance in operator_performance.items():
        validator_count = operator_validators.get(addr, 0)
        if validator_count > 0:
            total_weighted_performance += performance * validator_count
            total_validators += validator_count
            perf_categories[get_performance_category(performance)] += validator_count

    avg_performance = total_weighted_performance / total_validators if total_validators > 0 else 0

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        if avg_performance >= 99:
            status = "🟢 Excellent"
            color = "status-good"
        elif avg_performance >= 98:
            status = "🟡 Good"
            color = "status-warning"
        else:
            status = "🔴 Needs Attention"
            color = "status-danger"

        st.markdown(f"**Network Performance:** <span class='{color}'>{status}</span>", unsafe_allow_html=True)
        st.caption(f"Weighted avg: {avg_performance:.2f}%")

    with col2:
        excellent_pct = (perf_categories['Excellent'] / total_validators * 100) if total_validators > 0 else 0
        st.metric("Excellent Performers", f"{excellent_pct:.1f}%")
        st.caption(f"{perf_categories['Excellent']} validators")

    with col3:
        poor_pct = (perf_categories['Poor'] / total_validators * 100) if total_validators > 0 else 0
        if poor_pct < 5:
            color = "status-good"
        elif poor_pct < 15:
            color = "status-warning"
        else:
            color = "status-danger"

        st.markdown(f"**Poor Performers:** <span class='{color}'>{poor_pct:.1f}%</span>", unsafe_allow_html=True)
        st.caption(f"{perf_categories['Poor']} validators")

    with col4:
        # Performance consistency (std deviation)
        performances = list(operator_performance.values())
        perf_std = np.std(performances) if performances else 0

        if perf_std < 1.0:
            status = "🟢 Consistent"
            color = "status-good"
        elif perf_std < 2.5:
            status = "🟡 Variable"
            color = "status-warning"
        else:
            status = "🔴 Inconsistent"
            color = "status-danger"

        st.markdown(f"**Consistency:** <span class='{color}'>{status}</span>", unsafe_allow_html=True)
        st.caption(f"Std dev: {perf_std:.2f}%")

def main():
    # Responsive header design
    st.title("🔗 NodeSet Validator Monitor")
    st.markdown("*Real-time monitoring and analysis of NodeSet protocol validators*")

    # Refresh button (full width on mobile, right-aligned on desktop)
    refresh_col1, refresh_col2 = st.columns([3, 1])
    with refresh_col2:
        if st.button("🔄 Refresh Data", help="Reload validator data", use_container_width=True):
            st.cache_data.clear()
            st.rerun()

    # Load data
    cache_data = load_validator_data()
    if cache_data[0] is None:
        st.error("❌ **Cache file not found!**")
        st.markdown("""
        **Setup Instructions:**
        1. Run your NodeSet validator tracker script first
        2. Ensure `nodeset_validator_tracker_cache.json` exists
        3. Place the cache file in the same directory as this dashboard

        **Expected file locations:**
        - `./nodeset_validator_tracker_cache.json`
        - `./data/nodeset_validator_tracker_cache.json`
        """)
        return

    cache, cache_file = cache_data

    # Extract data
    operator_validators = cache.get('operator_validators', {})
    operator_exited = cache.get('exited_validators', {})
    operator_performance = cache.get('operator_performance', {})
    total_validators = cache.get('total_validators', 0)
    total_exited = cache.get('total_exited', 0)
    last_block = cache.get('last_block', 0)

    # Calculate active validators per operator
    active_validators = {}
    for operator, total_count in operator_validators.items():
        exited_count = operator_exited.get(operator, 0)
        active_count = total_count - exited_count
        if active_count > 0:
            active_validators[operator] = active_count

    total_active = sum(active_validators.values())

    # Data source info (responsive)
    last_update = datetime.fromtimestamp(os.path.getmtime(cache_file))
    st.caption(f"📊 Block: {last_block:,} • 🕒 {last_update.strftime('%H:%M:%S')} • 📁 {cache_file.split('/')[-1]}")

    # Responsive metrics layout
    st.markdown("### 📈 Network Overview")

    # Use responsive columns - fewer on mobile
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Active Validators", f"{total_active:,}")

    with col2:
        st.metric("Active Operators", len(active_validators))

    with col3:
        st.metric("Exited Validators", f"{total_exited:,}")

    with col4:
        exit_rate = (total_exited / total_validators * 100) if total_validators > 0 else 0
        st.metric("Exit Rate", f"{exit_rate:.1f}%")

    # Auto-refresh in separate row for better mobile layout
    st.markdown("---")
    auto_refresh_col1, auto_refresh_col2 = st.columns([3, 1])
    with auto_refresh_col2:
        auto_refresh = st.checkbox("🔄 Auto-refresh (60s)")

    # Combined health status with responsive design
    concentration_metrics = calculate_concentration_metrics(active_validators)

    # Network Health Summary (responsive text)
    if concentration_metrics:
        gini = concentration_metrics.get('gini_coefficient', 0)
        total_ops = concentration_metrics.get('total_operators', 0)
        avg_validators = (total_active / total_ops) if total_ops > 0 else 0

        # Determine overall health status
        health_indicators = []
        if gini < 0.5:
            health_indicators.append("🟢 Well Decentralized")
        elif gini < 0.7:
            health_indicators.append("🟡 Moderately Decentralized")
        else:
            health_indicators.append("🔴 Concentrated")

        if exit_rate < 5:
            health_indicators.append("🟢 Low Exit Rate")
        elif exit_rate < 15:
            health_indicators.append("🟡 Moderate Exits")
        else:
            health_indicators.append("🔴 High Exits")

        if avg_validators < 50:
            health_indicators.append("🟢 Small Operators")
        elif avg_validators <= 100:
            health_indicators.append("🟡 Medium Operators")
        else:
            health_indicators.append("🔴 Large Operators")

        # Responsive health display
        st.markdown(f"<div class='health-summary'><strong>Network Health:</strong> {' • '.join(health_indicators)}</div>", unsafe_allow_html=True)

    # Performance summary (if available) - responsive
    if operator_performance:
        total_weighted_performance = 0
        total_validators_perf = 0
        perf_categories = {'Excellent': 0, 'Good': 0, 'Average': 0, 'Poor': 0}

        for addr, performance in operator_performance.items():
            validator_count = operator_validators.get(addr, 0)
            if validator_count > 0:
                total_weighted_performance += performance * validator_count
                total_validators_perf += validator_count
                perf_categories[get_performance_category(performance)] += validator_count

        avg_performance = total_weighted_performance / total_validators_perf if total_validators_perf > 0 else 0
        excellent_pct = (perf_categories['Excellent'] / total_validators_perf * 100) if total_validators_perf > 0 else 0
        poor_pct = (perf_categories['Poor'] / total_validators_perf * 100) if total_validators_perf > 0 else 0

        perf_status = []
        if avg_performance >= 99:
            perf_status.append("🟢 Excellent Performance")
        elif avg_performance >= 98:
            perf_status.append("🟡 Good Performance")
        else:
            perf_status.append("🔴 Performance Issues")

        perf_status.append(f"{excellent_pct:.1f}% Excellent")
        if poor_pct > 0:
            perf_status.append(f"{poor_pct:.1f}% Poor")

        st.markdown(f"<div class='health-summary'><strong>Performance Health (24 hours):</strong> {' • '.join(perf_status)}</div>", unsafe_allow_html=True)

    # Expandable detailed health metrics - responsive columns
    with st.expander("🔍 Detailed Health Metrics"):
        if concentration_metrics:
            detail_col1, detail_col2 = st.columns([1, 1])
            with detail_col1:
                st.markdown("**Decentralization Metrics**")
                st.write(f"• Gini Coefficient: {gini:.3f}")
                st.write(f"• Top 1 Operator: {concentration_metrics['top_1_concentration']:.1f}%")
                st.write(f"• Top 5 Operators: {concentration_metrics['top_5_concentration']:.1f}%")
                st.write(f"• Average Validators/Operator: {avg_validators:.1f}")

            with detail_col2:
                if operator_performance:
                    st.markdown("**Performance Metrics**")
                    st.write(f"• Network Average: {avg_performance:.2f}%")
                    st.write(f"• Excellent Performers: {excellent_pct:.1f}%")
                    st.write(f"• Poor Performers: {poor_pct:.1f}%")
                    performances = list(operator_performance.values())
                    st.write(f"• Performance Std Dev: {np.std(performances):.2f}%")

    st.markdown("---")

    # Detailed analysis tabs
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        "📈 Distribution",
        "🎯 Concentration",
        "🏆 Top Operators",
        "⚡ Performance",
        "🚪 Exit Analysis",
        "💰 Costs",
        "📋 Raw Data"
    ])

    with tab1:
        # UPDATED: Remove pie chart, keep only histogram
        if active_validators:
            fig_hist = create_distribution_histogram(active_validators)
            st.plotly_chart(fig_hist, use_container_width=True)

            # Key insights
            st.subheader("📊 Key Insights")
            col1, col2, col3 = st.columns(3)

with col1:
    max_validators = max(active_validators.values()) if active_validators else 0
    st.metric("Largest Operator", f"{max_validators} validators")

with col2:
    # Average validators per operator
    avg_validators = np.mean(list(active_validators.values())) if active_validators else 0
    st.metric("Average per Operator", f"{avg_validators:.1f} validators")

with col3:
    # Concentration metric - what % of validators are controlled by largest operators
    if active_validators:
        sorted_validators = sorted(active_validators.values(), reverse=True)
        total_validators = sum(sorted_validators)
        # Top 3 operators' share
        top_3_validators = sum(sorted_validators[:3]) if len(sorted_validators) >= 3 else sum(sorted_validators)
        top_3_percentage = (top_3_validators / total_validators * 100) if total_validators > 0 else 0
        st.metric("Top 3 Operators Control", f"{top_3_percentage:.1f}%")
        st.caption(f"{top_3_validators} of {total_validators} validators")
    else:
        st.metric("Top 3 Operators Control", "0%")

    with tab2:
        if concentration_metrics:
            col1, col2 = st.columns([2, 1])

            with col1:
                fig_curve = create_concentration_curve(active_validators)
                st.plotly_chart(fig_curve, use_container_width=True)

            with col2:
                st.subheader("📏 Concentration Metrics")

                metrics_df = pd.DataFrame([
                    {"Metric": "Gini Coefficient", "Value": f"{concentration_metrics['gini_coefficient']:.4f}"},
                    {"Metric": "Top 1 Operator", "Value": f"{concentration_metrics['top_1_concentration']:.2f}%"},
                    {"Metric": "Top 5 Operators", "Value": f"{concentration_metrics['top_5_concentration']:.2f}%"},
                    {"Metric": "Top 10 Operators", "Value": f"{concentration_metrics['top_10_concentration']:.2f}%"},
                ])

                st.dataframe(metrics_df, use_container_width=True, hide_index=True)

                st.markdown("""
                **Interpretation:**
                - **Gini = 0**: Perfect equality
                - **Gini = 1**: Maximum concentration
                - **Lower values** = more decentralized
                """)
        else:
            st.info("No concentration data available.")

    with tab3:
        # Show all operators
        st.subheader("🏆 Top Operators by Active Validators")

        df_operators = create_top_operators_table(operator_validators, operator_exited)

        if not df_operators.empty:
            # Display table - show all operators
            display_df = df_operators.drop(['Full Address'], axis=1)
            st.dataframe(
                display_df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Rank": st.column_config.NumberColumn("Rank", width="small"),
                    "Active": st.column_config.NumberColumn("Active", format="%d"),
                    "Total": st.column_config.NumberColumn("Total", format="%d"),
                    "Exited": st.column_config.NumberColumn("Exited", format="%d"),
                }
            )

            # Download CSV
            csv = display_df.to_csv(index=False)
            st.download_button(
                label="📥 Download CSV",
                data=csv,
                file_name=f"nodeset_operators_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
        else:
            st.info("No operator data available.")

    with tab4:
        st.subheader("⚡ Operator Performance Analysis (24 hours)")
        st.info("ℹ️ This is last 24 hour data only")

        if operator_performance:
            fig_scatter, fig_hist, perf_df = create_performance_analysis(
                operator_performance, operator_validators
            )

            if fig_scatter and fig_hist:
                # Performance scatter plot
                st.plotly_chart(fig_scatter, use_container_width=True)

                col1, col2 = st.columns(2)

                with col1:
                    # Performance distribution
                    st.plotly_chart(fig_hist, use_container_width=True)

                with col2:
                    # Performance summary stats
                    st.subheader("📊 Performance Summary")
                    performances = list(operator_performance.values())

                    summary_stats = pd.DataFrame([
                        {"Metric": "Average", "Value": f"{np.mean(performances):.2f}%"},
                        {"Metric": "Median", "Value": f"{np.median(performances):.2f}%"},
                        {"Metric": "Best", "Value": f"{np.max(performances):.2f}%"},
                        {"Metric": "Worst", "Value": f"{np.min(performances):.2f}%"},
                        {"Metric": "Std Dev", "Value": f"{np.std(performances):.2f}%"},
                    ])

                    st.dataframe(summary_stats, use_container_width=True, hide_index=True)

                # Enhanced performance table
                st.subheader("🏆 Operators by Performance")
                perf_table_df = create_performance_table(
                    operator_performance, operator_validators, operator_exited
                )

                if not perf_table_df.empty:
                    display_perf_df = perf_table_df.drop(['Full Address', 'Performance_Raw'], axis=1)
                    st.dataframe(
                        display_perf_df,
                        use_container_width=True,
                        hide_index=True,
                        column_config={
                            "Category": st.column_config.TextColumn(
                                "Category",
                                help="Performance category based on percentage"
                            )
                        }
                    )
            else:
                st.info("Insufficient performance data for analysis.")
        else:
            st.info("No performance data available in cache file.")

    with tab5:
        if total_exited > 0:
            st.subheader("🚪 Exit Analysis")

            col1, col2 = st.columns(2)

            with col1:
                # Exit distribution
                exit_counts = [count for count in operator_exited.values() if count > 0]
                if exit_counts:
                    fig_exits = px.histogram(
                        x=exit_counts,
                        title="Distribution of Exits per Operator",
                        labels={'x': 'Exits per Operator', 'y': 'Number of Operators'},
                        color_discrete_sequence=['#FF6B6B']
                    )
                    st.plotly_chart(fig_exits, use_container_width=True)

            with col2:
                # Exit rate by operator size
                if operator_validators and operator_exited:
                    exit_rate_data = []
                    for addr, total_count in operator_validators.items():
                        if total_count >= 2:  # Only include operators with 2+ validators
                            exited_count = operator_exited.get(addr, 0)
                            exit_rate = (exited_count / total_count * 100) if total_count > 0 else 0
                            exit_rate_data.append({
                                'Total Validators': total_count,
                                'Exit Rate (%)': exit_rate
                            })

                    if exit_rate_data:
                        df_exits = pd.DataFrame(exit_rate_data)
                        fig_scatter = px.scatter(
                            df_exits,
                            x='Total Validators',
                            y='Exit Rate (%)',
                            title="Exit Rate vs Operator Size",
                            color_discrete_sequence=['#764ba2']
                        )
                        st.plotly_chart(fig_scatter, use_container_width=True)

            # Operators with highest exit rates
            st.subheader("Operators with Exits")
            exited_operators_data = []
            for addr, exit_count in operator_exited.items():
                if exit_count > 0:
                    total_count = operator_validators.get(addr, 0)
                    active_count = total_count - exit_count
                    exit_rate = (exit_count / total_count * 100) if total_count > 0 else 0

                    exited_operators_data.append({
                        'Operator': f"{addr[:8]}...{addr[-6:]}",
                        'Exits': exit_count,
                        'Still Active': active_count,
                        'Total Ever': total_count,
                        'Exit Rate': f"{exit_rate:.1f}%"
                    })

            if exited_operators_data:
                df_exited = pd.DataFrame(exited_operators_data)
                df_exited = df_exited.sort_values('Exit Rate', key=lambda x: x.str.rstrip('%').astype(float), ascending=False)
                st.dataframe(df_exited, use_container_width=True, hide_index=True)
            else:
                st.info("No exits detected in current data.")
        else:
            st.info("😊 Great news! No validator exits detected yet.")

    with tab6:
        st.subheader("💰 Transaction Cost Analysis")
        
        operator_costs = cache.get('operator_costs', {})
        operator_transactions = cache.get('operator_transactions', {})
        cost_last_updated = cache.get('cost_last_updated', 0)
        
        if not operator_costs:
            st.info("💡 No cost data available. Ensure ETHERSCAN_API_KEY is set and run the tracker script to collect transaction cost data.")
            st.markdown("""
            **To enable cost tracking:**
            1. Set `ETHERSCAN_API_KEY` environment variable
            2. Run the NodeSet validator tracker script
            3. Cost data will be collected for all operators
            """)
        else:
            # Summary metrics at the top
            total_gas_spent = sum(cost['total_cost_eth'] for cost in operator_costs.values())
            total_transactions = sum(cost['total_txs'] for cost in operator_costs.values())
            total_successful = sum(cost['successful_txs'] for cost in operator_costs.values())
            total_failed = sum(cost['failed_txs'] for cost in operator_costs.values())
            operators_with_costs = len([c for c in operator_costs.values() if c['total_txs'] > 0])
            
            # Cost summary cards
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Gas Spent", f"{total_gas_spent:.6f} ETH")
                
            with col2:
                st.metric("Total Transactions", f"{total_transactions:,}")
                
            with col3:
                success_rate = (total_successful / total_transactions * 100) if total_transactions > 0 else 0
                st.metric("Success Rate", f"{success_rate:.1f}%")
                
            with col4:
                avg_cost = total_gas_spent / total_transactions if total_transactions > 0 else 0
                st.metric("Avg Cost/TX", f"{avg_cost:.6f} ETH")

            # Additional summary row
            col5, col6, col7, col8 = st.columns(4)
            
            with col5:
                st.metric("Operators Tracked", f"{operators_with_costs}")
                
            with col6:
                st.metric("Failed Transactions", f"{total_failed:,}")
                    
            with col7:
                # Cost per validator
                total_active_validators = sum(v - operator_exited.get(k, 0) for k, v in operator_validators.items())
                cost_per_validator = total_gas_spent / total_active_validators if total_active_validators > 0 else 0
                st.metric("Cost per Validator", f"{cost_per_validator:.6f} ETH")
                
            with col8:
                if cost_last_updated > 0:
                    last_update_dt = datetime.fromtimestamp(cost_last_updated)
                    hours_ago = (datetime.now() - last_update_dt).total_seconds() / 3600
                    st.metric("Data Age", f"{hours_ago:.1f}h ago")
                else:
                    st.metric("Data Age", "Unknown")

            st.markdown("---")
            
            # Create operator cost table
            cost_data = []
            for operator, cost_info in operator_costs.items():
                if cost_info['total_txs'] > 0:
                    validator_count = operator_validators.get(operator, 0)
                    active_validators = validator_count - operator_exited.get(operator, 0)
                    
                    cost_data.append({
                        'operator': operator,
                        'operator_short': f"{operator[:8]}...{operator[-6:]}",
                        'total_cost_eth': cost_info['total_cost_eth'],
                        'total_txs': cost_info['total_txs'],
                        'successful_txs': cost_info['successful_txs'],
                        'failed_txs': cost_info['failed_txs'],
                        'avg_cost_per_tx': cost_info['avg_cost_per_tx'],
                        'success_rate': (cost_info['successful_txs'] / cost_info['total_txs'] * 100) if cost_info['total_txs'] > 0 else 0,
                        'validators': active_validators,
                        'cost_per_validator': cost_info['total_cost_eth'] / active_validators if active_validators > 0 else 0
                    })
            
            if cost_data:
                # Sort by total cost descending
                cost_data.sort(key=lambda x: x['total_cost_eth'], reverse=True)
                
                st.subheader("📊 Operator Cost Rankings")
                st.caption(f"Showing {len(cost_data)} operators with transaction data, sorted by total gas spent")
                
                # Add search functionality
                search_term = st.text_input(
                    "🔍 Search operators by address",
                    placeholder="Enter full or partial address (e.g., 0x1878f36 or f36F8442)",
                    help="Search is case-insensitive and matches any part of the address"
                )
                
                # Filter data based on search
                if search_term:
                    filtered_data = [row for row in cost_data if search_term.lower() in row['operator'].lower()]
                    if filtered_data:
                        st.info(f"Found {len(filtered_data)} operators matching '{search_term}'")
                        display_data = filtered_data
                    else:
                        st.warning(f"No operators found matching '{search_term}'")
                        display_data = []
                else:
                    display_data = cost_data
                
                # Create expandable table
                for i, row in enumerate(display_data):
                    with st.expander(
                        f"#{i+1} {row['operator']} - {row['total_cost_eth']:.6f} ETH ({row['total_txs']} txs)", 
                        expanded=False
                    ):
                        # Operator summary in columns
                        detail_col1, detail_col2, detail_col3 = st.columns(3)
                        
                        with detail_col1:
                            st.markdown("**📊 Transaction Summary**")
                            st.write(f"• Total Cost: **{row['total_cost_eth']:.6f} ETH**")
                            st.write(f"• Total Transactions: **{row['total_txs']:,}**")
                            st.write(f"• Average per TX: **{row['avg_cost_per_tx']:.6f} ETH**")
                            
                        with detail_col2:
                            st.markdown("**✅ Success Metrics**")
                            st.write(f"• Successful: **{row['successful_txs']:,}**")
                            st.write(f"• Failed: **{row['failed_txs']:,}**")
                            st.write(f"• Success Rate: **{row['success_rate']:.1f}%**")
                            
                        with detail_col3:
                            st.markdown("**🔗 Validator Metrics**")
                            st.write(f"• Active Validators: **{row['validators']:,}**")
                            if row['validators'] > 0:
                                st.write(f"• Cost per Validator: **{row['cost_per_validator']:.6f} ETH**")
                            else:
                                st.write(f"• Cost per Validator: **N/A**")
                            st.write(f"• Full Address: `{row['operator']}`")
                        
                        # Transaction details table
                        operator_txs = operator_transactions.get(row['operator'], [])
                        if operator_txs:
                            st.markdown("**📋 Transaction History**")
                            
                            # Convert to DataFrame and sort by date/time
                            tx_df = pd.DataFrame(operator_txs)
                            tx_df['datetime'] = pd.to_datetime(tx_df['date'] + ' ' + tx_df['time'])
                            tx_df = tx_df.sort_values('datetime', ascending=False)
                            
                            # Add validator count column for successful transactions
                            tx_df['validator_count'] = tx_df.apply(
                                lambda row_data: row_data.get('validator_count', 0) if row_data['status'] == 'Successful' else 0, 
                                axis=1
                            )
                            
                            # Ensure validator_count is numeric
                            tx_df['validator_count'] = pd.to_numeric(tx_df['validator_count'], errors='coerce').fillna(0).astype(int)
                            
                            # Format for display - show empty string for failed transactions
                            display_tx_df = tx_df[['date', 'time', 'total_cost_eth', 'status', 'validator_count', 'gas_used', 'gas_price']].copy()
                            display_tx_df['validator_count_display'] = display_tx_df.apply(
                                lambda row: str(row['validator_count']) if row['status'] == 'Successful' and row['validator_count'] > 0 else '', 
                                axis=1
                            )
                            
                            # Create final display dataframe
                            final_display_df = display_tx_df[['date', 'time', 'total_cost_eth', 'status', 'validator_count_display', 'gas_used', 'gas_price']].copy()
                            final_display_df.columns = ['Date', 'Time', 'Cost (ETH)', 'Status', 'Validators', 'Gas Used', 'Gas Price']
                            
                            # Style the status column
                            def style_status(val):
                                if val == 'Successful':
                                    return 'color: green'
                                else:
                                    return 'color: red'
                            
                            st.dataframe(
                                final_display_df.style.map(style_status, subset=['Status']),
                                use_container_width=True,
                                hide_index=True,
                                column_config={
                                    "Cost (ETH)": st.column_config.NumberColumn(
                                        "Cost (ETH)",
                                        format="%.6f"
                                    ),
                                    "Validators": st.column_config.TextColumn(
                                        "Validators",
                                        help="Number of validator deposits in successful transactions"
                                    ),
                                    "Gas Used": st.column_config.NumberColumn(
                                        "Gas Used",
                                        format="%d"
                                    ),
                                    "Gas Price": st.column_config.NumberColumn(
                                        "Gas Price",
                                        format="%d"
                                    )
                                }
                            )
                            
                            # Download individual operator data
                            csv_data = tx_df.to_csv(index=False)
                            st.download_button(
                                label=f"📥 Download {row['operator_short']} transactions",
                                data=csv_data,
                                file_name=f"nodeset_costs_{row['operator_short']}_{datetime.now().strftime('%Y%m%d')}.csv",
                                mime="text/csv",
                                key=f"download_{i}"
                            )
                        else:
                            st.info("No detailed transaction data available for this operator.")
                
                # Download all cost data
                st.markdown("---")
                col1, col2 = st.columns([3, 1])
                with col2:
                    # Create summary CSV
                    summary_df = pd.DataFrame(cost_data)
                    summary_csv = summary_df[[
                        'operator', 'total_cost_eth', 'total_txs', 'successful_txs', 
                        'failed_txs', 'success_rate', 'validators', 'cost_per_validator'
                    ]].to_csv(index=False)
                    
                    st.download_button(
                        label="📥 Download All Cost Data",
                        data=summary_csv,
                        file_name=f"nodeset_all_costs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv",
                        use_container_width=True
                    )
            else:
                st.info("No operators found with transaction cost data.")

    with tab7:
        st.subheader("📋 Raw Cache Data")

        col1, col2 = st.columns(2)

        with col1:
            st.json({
                "total_validators": cache.get('total_validators', 0),
                "total_exited": cache.get('total_exited', 0),
                "last_block": cache.get('last_block', 0),
                "last_epoch_checked": cache.get('last_epoch_checked', 0),
                "total_operators": len(cache.get('operator_validators', {})),
                "pending_pubkeys": len(cache.get('pending_pubkeys', [])),
                "processed_transactions": len(cache.get('processed_transactions', [])),
                "performance_metrics": len(cache.get('operator_performance', {})),
                "cost_metrics": len(cache.get('operator_costs', {})),
                "transaction_records": len(cache.get('operator_transactions', {}))
            })

        with col2:
            if st.button("📄 Show Full Cache"):
                st.json(cache)

    # Auto-refresh handling
    if auto_refresh:
        import time
        time.sleep(60)
        st.rerun()

    # Footer
    st.markdown("---")
    st.markdown(f"*Dashboard last refreshed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")

if __name__ == "__main__":
    main()
