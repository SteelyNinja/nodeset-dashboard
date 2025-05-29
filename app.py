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

# Custom CSS for better styling
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
    
    /* Adjust main content area */
    .main .block-container {
        padding-left: 1rem;
        padding-right: 1rem;
        max-width: none;
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
    operator_counts.sort(reverse=True)

    # Gini coefficient calculation
    n = len(operator_counts)
    if n == 0:
        return {}

    index = np.arange(1, n + 1)
    gini = (2 * np.sum(index * operator_counts)) / (n * np.sum(operator_counts)) - (n + 1) / n

    # Concentration ratios
    top_1_pct = (operator_counts[0] / total_validators) * 100 if operator_counts else 0
    top_5_pct = (sum(operator_counts[:min(5, len(operator_counts))]) / total_validators) * 100
    top_10_pct = (sum(operator_counts[:min(10, len(operator_counts))]) / total_validators) * 100

    return {
        'gini_coefficient': gini,
        'top_1_concentration': top_1_pct,
        'top_5_concentration': top_5_pct,
        'top_10_concentration': top_10_pct,
        'total_operators': len(operator_validators),
        'total_validators': total_validators
    }

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
    """Create histogram of validator counts per operator"""
    if not operator_validators:
        return go.Figure()

    validator_counts = list(operator_validators.values())

    fig = px.histogram(
        x=validator_counts,
        nbins=max(10, min(50, len(set(validator_counts)))),
        title="Distribution of Validators per Operator",
        labels={'x': 'Validators per Operator', 'y': 'Number of Operators'},
        color_discrete_sequence=['#667eea']
    )

    fig.update_layout(
        height=400,
        showlegend=False
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
            'Operator': f"{addr[:8]}...{addr[-6:]}",
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

        if avg_validators < 10:  # Changed from 5 to 10
            status = "🟢 Low"  # Changed from "Diverse" to "Low"
            color = "status-good"
        elif avg_validators <= 50:  # Changed from 20 to 50
            status = "🟡 Moderate"
            color = "status-warning"
        else:
            status = "🔴 High"  # Changed from "Concentrated" to "High"
            color = "status-danger"

        st.markdown(f"**Operator Size:** <span class='{color}'>{status}</span>", unsafe_allow_html=True)
        st.caption(f"{avg_validators:.1f} avg validators/operator")

def main():
    # Header with refresh button and data info
    col1, col2, col3 = st.columns([3, 1, 1])
    with col1:
        st.title("🔗 NodeSet Validator Monitor")
        st.markdown("*Monitoring and analysis of NodeSet protocol validators*")

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

    # Data info and refresh button in header
    with col2:
        st.metric("Last Block", f"{last_block:,}")
        
    with col3:
        if st.button("🔄 Refresh Data", help="Reload validator data"):
            st.cache_data.clear()
            st.rerun()

    # Show data source info
    last_update = datetime.fromtimestamp(os.path.getmtime(cache_file))
    st.caption(f"📁 Data from: {cache_file.split('/')[-1]} | 🕒 Updated: {last_update.strftime('%Y-%m-%d %H:%M:%S')}")

    # Main metrics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Active Validators",
            f"{total_active:,}",
            delta=None,
            help="Currently active validators in the network"
        )

    with col2:
        st.metric(
            "Active Operators",
            len(active_validators),
            help="Operators with at least one active validator"
        )

    with col3:
        st.metric(
            "Exited Validators",
            f"{total_exited:,}",
            delta_color="inverse",
            help="Validators that have exited the network"
        )

    with col4:
        exit_rate = (total_exited / total_validators * 100) if total_validators > 0 else 0
        st.metric(
            "Exit Rate",
            f"{exit_rate:.1f}%",
            help="Percentage of validators that have exited"
        )

    # Health status
    concentration_metrics = calculate_concentration_metrics(active_validators)
    if concentration_metrics:
        display_health_status(concentration_metrics, total_active, total_exited)

    # Settings row
    st.markdown("---")
    col1, col2 = st.columns([3, 1])
    with col2:
        auto_refresh = st.checkbox("🔄 Auto-refresh (60 seconds)")

    # Detailed analysis tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📈 Distribution",
        "🎯 Concentration",
        "🏆 Top Operators",
        "🚪 Exit Analysis",
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
                median_validators = np.median(list(active_validators.values())) if active_validators else 0
                st.metric("Median per Operator", f"{median_validators:.1f}")

            with col3:
                single_validator_ops = sum(1 for v in active_validators.values() if v == 1)
                st.metric("Single-Validator Operators", single_validator_ops)
        else:
            st.info("No active validators found.")

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
        # UPDATED: Show all operators instead of top 20
        st.subheader("🏆 Top Operators by Active Validators")

        df_operators = create_top_operators_table(operator_validators, operator_exited)

        if not df_operators.empty:
            # Display table - REMOVED .head(20) to show all
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

            # Full addresses expandable section - REMOVED .head(10) to show all
            with st.expander("🔍 Show Full Addresses"):
                for _, row in df_operators.iterrows():
                    st.code(f"#{row['Rank']:2d} | {row['Active']:3d} validators | {row['Full Address']}")
        else:
            st.info("No operator data available.")

    with tab4:
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

    with tab5:
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
                "processed_transactions": len(cache.get('processed_transactions', []))
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
