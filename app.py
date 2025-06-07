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
    initial_sidebar_state="collapsed"
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

    .css-1d391kg {
        display: none;
    }

    section[data-testid="stSidebar"] {
        display: none;
    }

    .main .block-container {
        padding-left: 1rem;
        padding-right: 1rem;
        max-width: none;
    }

    .logo-container {
        text-align: left;
        margin-bottom: 1rem;
    }

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

        .logo-container img {
            max-height: 80px;
        }
    }

    @media (min-width: 769px) and (max-width: 1024px) {
        .main .block-container {
            padding-left: 0.75rem;
            padding-right: 0.75rem;
        }
    }

    @media (min-width: 1400px) {
        .main .block-container {
            max-width: 1400px;
            margin: 0 auto;
        }
    }

    @media (max-width: 768px) {
        .health-summary {
            font-size: 0.9rem;
            line-height: 1.4;
        }
    }

    .ens-name {
        color: #007bff;
        font-weight: 600;
    }

    .operator-address {
        color: #6c757d;
        font-family: monospace;
        font-size: 0.9em;
    }
</style>
""", unsafe_allow_html=True)

def display_logo():
    """Display the appropriate logo based on system theme preference"""
    dark_logo_path = "Nodeset_dark_mode.png"
    light_logo_path = "Nodeset_light_mode.png"
    
    # Check if files exist
    dark_exists = os.path.exists(dark_logo_path)
    light_exists = os.path.exists(light_logo_path)
    
    if dark_exists and light_exists:
        # Convert images to base64 for embedding
        dark_b64 = get_base64_image(dark_logo_path)
        light_b64 = get_base64_image(light_logo_path)
        
        if dark_b64 and light_b64:
            # Use CSS media queries for automatic theme switching
            logo_html = f"""
            <div class="logo-container">
                <style>
                .logo-dark {{
                    display: block;
                    height: 60px;
                    width: auto;
                }}
                .logo-light {{
                    display: none;
                    height: 60px;
                    width: auto;
                }}
                @media (prefers-color-scheme: light) {{
                    .logo-dark {{
                        display: none;
                    }}
                    .logo-light {{
                        display: block;
                    }}
                }}
                </style>
                <img src="data:image/png;base64,{dark_b64}" class="logo-dark" alt="NodeSet Dark Logo">
                <img src="data:image/png;base64,{light_b64}" class="logo-light" alt="NodeSet Light Logo">
            </div>
            """
            st.markdown(logo_html, unsafe_allow_html=True)
        else:
            # Fallback if base64 conversion fails
            st.image(dark_logo_path, width=204)
            
    elif dark_exists:
        st.markdown('<div class="logo-container">', unsafe_allow_html=True)
        st.image(dark_logo_path, width=204)
        st.markdown('</div>', unsafe_allow_html=True)
    elif light_exists:
        st.markdown('<div class="logo-container">', unsafe_allow_html=True)
        st.image(light_logo_path, width=204)
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.error("Logo files not found: Nodeset_dark_mode.png and Nodeset_light_mode.png")
        st.title("🔗 NodeSet Validator Monitor")

def get_base64_image(image_path):
    """Convert image to base64 string for embedding in HTML"""
    import base64
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except Exception as e:
        st.error(f"Error loading image {image_path}: {str(e)}")
        return ""

@st.cache_data(ttl=300)
def load_validator_data():
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
                st.error(f"⚠ Error loading {cache_file}: {str(e)}")

    return None, None

@st.cache_data(ttl=300)
def load_proposals_data():
    proposals_files = [
        'proposals.json',
        './data/proposals.json',
        '../proposals.json'
    ]
    
    for proposals_file in proposals_files:
        if os.path.exists(proposals_file):
            try:
                with open(proposals_file, 'r') as f:
                    data = json.load(f)
                return data, proposals_file
            except Exception as e:
                st.error(f"⚠ Error loading {proposals_file}: {str(e)}")
    
    return None, None

@st.cache_data(ttl=300)
def load_mev_analysis_data():
    """Load MEV relay analysis data for gas limit analysis"""
    mev_files = [
        'mev_analysis_results.json',
        './data/mev_analysis_results.json', 
        '../mev_analysis_results.json'
    ]
    
    for mev_file in mev_files:
        if os.path.exists(mev_file):
            try:
                with open(mev_file, 'r') as f:
                    data = json.load(f)
                return data, mev_file
            except Exception as e:
                st.error(f"⚠ Error loading {mev_file}: {str(e)}")
    
    return None, None

def format_operator_display(address: str, ens_names: dict, short: bool = False) -> str:
    ens_name = ens_names.get(address)

    if ens_name:
        if short:
            return f"{ens_name}"
        else:
            return f"{ens_name}\n({address[:8]}...{address[-6:]})"
    else:
        return f"{address[:8]}...{address[-6:]}"

def format_operator_display_plain(address: str, ens_names: dict, show_full_address: bool = False) -> str:
    ens_name = ens_names.get(address)

    if ens_name:
        if show_full_address:
            return f"{ens_name} ({address})"
        else:
            return f"{ens_name} ({address[:8]}...{address[-6:]})"
    else:
        if show_full_address:
            return address
        else:
            return f"{address[:8]}...{address[-6:]}"

def calculate_concentration_metrics(operator_validators):
    if not operator_validators:
        return {}

    total_validators = sum(operator_validators.values())
    operator_counts = list(operator_validators.values())

    operator_counts.sort()

    n = len(operator_counts)
    if n == 0 or total_validators == 0:
        return {}

    index = np.arange(1, n + 1)
    gini = (2 * np.sum(index * operator_counts)) / (n * total_validators) - (n + 1) / n

    gini = max(0, min(1, gini))

    operator_counts_desc = sorted(operator_counts, reverse=True)

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
    if performance >= 99.5:
        return 'Excellent'
    elif performance >= 98.5:
        return 'Good'
    elif performance >= 95.0:
        return 'Average'
    else:
        return 'Poor'

def create_performance_analysis(operator_performance, operator_validators, ens_names):
    if not operator_performance:
        return None, None, None

    perf_data = []
    for addr, performance in operator_performance.items():
        validator_count = operator_validators.get(addr, 0)
        if validator_count > 0:
            display_name = format_operator_display_plain(addr, ens_names)
            perf_data.append({
                'operator': display_name,
                'full_address': addr,
                'performance': performance,
                'validator_count': validator_count,
                'performance_category': get_performance_category(performance)
            })

    if not perf_data:
        return None, None, None

    df = pd.DataFrame(perf_data)

    df['performance_category'] = pd.Categorical(df['performance_category'],
                                              categories=['Excellent', 'Good', 'Average', 'Poor'],
                                              ordered=True)

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

def create_concentration_pie(operator_validators, ens_names, title="Validator Distribution"):
    if not operator_validators:
        fig = go.Figure()
        fig.add_annotation(text="No data available", x=0.5, y=0.5, showarrow=False)
        return fig

    sorted_ops = sorted(operator_validators.items(), key=lambda x: x[1], reverse=True)

    labels = []
    values = []

    for i, (addr, count) in enumerate(sorted_ops[:8]):
        display_name = format_operator_display_plain(addr, ens_names)
        labels.append(f"{display_name} ({count})")
        values.append(count)

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
    if not operator_validators:
        return go.Figure()

    validator_counts = list(operator_validators.values())

    min_validators = min(validator_counts)
    max_validators = max(validator_counts)

    fig = px.histogram(
        x=validator_counts,
        title="Distribution of Validators per Operator",
        labels={'x': 'Validators per Operator', 'y': 'Number of Operators'},
        color_discrete_sequence=['#667eea']
    )

    fig.update_traces(
        xbins=dict(
            start=min_validators - 0.5,
            end=max_validators + 0.5,
            size=1
        )
    )

    fig.update_layout(
        height=400,
        showlegend=False,
        xaxis=dict(
            tick0=min_validators,
            dtick=1,
            tickmode='linear'
        ),
        bargap=0.1
    )

    return fig

def create_concentration_curve(operator_validators):
    if not operator_validators:
        return go.Figure()

    validator_counts = sorted(operator_validators.values())
    n = len(validator_counts)
    total_validators = sum(validator_counts)

    if total_validators == 0:
        return go.Figure()

    cum_operators = np.arange(1, n + 1) / n * 100
    cum_validators = np.cumsum(validator_counts) / total_validators * 100

    equality_line = np.linspace(0, 100, 100)

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=cum_operators,
        y=cum_validators,
        mode='lines+markers',
        name='Actual Distribution',
        line=dict(color='#667eea', width=3),
        marker=dict(size=4)
    ))

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

def create_top_operators_table(operator_validators, operator_exited, ens_names):
    if not operator_validators:
        return pd.DataFrame()

    data = []
    for addr, total_count in operator_validators.items():
        exited_count = operator_exited.get(addr, 0)
        active_count = total_count - exited_count
        exit_rate = (exited_count / total_count * 100) if total_count > 0 else 0

        ens_name = ens_names.get(addr, "")

        data.append({
            'Rank': 0,
            'Address': addr,
            'ENS Name': ens_name,
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

def create_performance_table(operator_performance, operator_validators, operator_exited, ens_names):
    if not operator_performance:
        return pd.DataFrame()

    data = []
    for addr, performance in operator_performance.items():
        total_count = operator_validators.get(addr, 0)
        exited_count = operator_exited.get(addr, 0)
        active_count = total_count - exited_count

        if total_count > 0:
            ens_name = ens_names.get(addr, "")

            data.append({
                'Rank': 0,
                'Address': addr,
                'ENS Name': ens_name,
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
    df = df.sort_values(['Performance_Raw', 'Active'], ascending=[False, False]).reset_index(drop=True)
    df['Rank'] = range(1, len(df) + 1)

    return df

def create_largest_proposals_table(proposals_data, ens_names, limit=3):
    """Create a table showing the largest proposals by ETH value"""
    if not proposals_data:
        return pd.DataFrame()
    
    proposals = proposals_data.get('proposals', [])
    
    if not proposals:
        return pd.DataFrame()
    
    # Sort proposals by ETH value (largest first) and take the top N
    largest_proposals = sorted(proposals, key=lambda x: x['total_value_eth'], reverse=True)[:limit]
    
    # Format the data for display
    table_data = []
    for proposal in largest_proposals:
        operator_address = proposal['operator']
        ens_name = ens_names.get(operator_address, "")
        
        # Format operator display
        if ens_name:
            operator_display = f"{ens_name} ({operator_address[:8]}...{operator_address[-6:]})"
        else:
            operator_display = f"{operator_address[:8]}...{operator_address[-6:]}"
        
        table_data.append({
            'Date': proposal['date'],
            'Operator': operator_display,
            'Operator Address': operator_address,
            'Validator Pubkey': proposal['validator_pubkey'],
            'ETH Value': f"{proposal['total_value_eth']:.4f}",
            'Slot': proposal['slot'],
            'Gas Used': f"{proposal['gas_used']:,}",
            'Gas Utilization': f"{proposal['gas_utilization']:.1f}%",
            'TX Count': proposal['tx_count']
        })
    
    return pd.DataFrame(table_data)

def create_latest_proposals_table(proposals_data, ens_names, limit=5):
    """Create a table showing the latest proposals across all operators"""
    if not proposals_data:
        return pd.DataFrame()
    
    proposals = proposals_data.get('proposals', [])
    
    if not proposals:
        return pd.DataFrame()
    
    # Sort proposals by date (latest first) and take the top N
    latest_proposals = sorted(proposals, key=lambda x: x['date'], reverse=True)[:limit]
    
    # Format the data for display
    table_data = []
    for proposal in latest_proposals:
        operator_address = proposal['operator']
        ens_name = ens_names.get(operator_address, "")
        
        # Format operator display
        if ens_name:
            operator_display = f"{ens_name} ({operator_address[:8]}...{operator_address[-6:]})"
        else:
            operator_display = f"{operator_address[:8]}...{operator_address[-6:]}"
        
        table_data.append({
            'Date': proposal['date'],
            'Operator': operator_display,
            'Operator Address': operator_address,
            'Validator Pubkey': proposal['validator_pubkey'],
            'ETH Value': f"{proposal['total_value_eth']:.4f}",
            'Slot': proposal['slot'],
            'Gas Used': f"{proposal['gas_used']:,}",
            'Gas Utilization': f"{proposal['gas_utilization']:.1f}%",
            'TX Count': proposal['tx_count']
        })
    
    return pd.DataFrame(table_data)

def create_proposals_operators_table(proposals_data, ens_names):
    if not proposals_data:
        return []
    
    operator_summary = proposals_data.get('operator_summary', {})
    proposals = proposals_data.get('proposals', [])
    
    table_data = []
    for addr, summary in operator_summary.items():
        operator_proposals = [p for p in proposals if p['operator'] == addr]
        
        if operator_proposals:
            dates = [p['date'] for p in operator_proposals]
            gas_used = sum(p['gas_used'] for p in operator_proposals)
            avg_gas_util = sum(p['gas_utilization'] for p in operator_proposals) / len(operator_proposals)
            avg_txs = sum(p['tx_count'] for p in operator_proposals) / len(operator_proposals)
            highest_value = max(p['total_value_eth'] for p in operator_proposals)
            
            table_data.append({
                'operator': addr,
                'ens_name': ens_names.get(addr, ''),
                'proposal_count': summary['proposal_count'],
                'total_value_eth': summary['total_value_eth'],
                'average_value_eth': summary['average_value_eth'],
                'highest_value_eth': highest_value,
                'total_gas_used': gas_used,
                'avg_gas_utilization': avg_gas_util,
                'avg_tx_count': avg_txs,
                'first_proposal': min(dates),
                'last_proposal': max(dates),
                'proposals': operator_proposals
            })
    
    return sorted(table_data, key=lambda x: x['proposal_count'], reverse=True)

def analyze_gas_limits_by_operator(mev_data, ens_names):
    """Analyze gas limit choices by operator"""
    if not mev_data:
        return []
    
    operator_analysis = mev_data.get('operator_analysis', {})
    gas_data = []
    
    for operator_addr, data in operator_analysis.items():
        gas_limits = data.get('gas_limits', [])
        if gas_limits:
            # Calculate gas limit statistics for this operator
            unique_limits = list(set(gas_limits))
            avg_gas = data.get('average_gas_limit', 0)
            
            # Determine operator's gas strategy
            if len(unique_limits) == 1:
                strategy = "Consistent"
                consistency_score = 100.0
            else:
                strategy = "Mixed"
                # Calculate consistency as percentage of validators using most common limit
                most_common_limit = max(set(gas_limits), key=gas_limits.count)
                consistency_score = (gas_limits.count(most_common_limit) / len(gas_limits)) * 100
            
            # Categorize gas limit approach
            max_gas = max(gas_limits)
            if max_gas >= 60000000:
                gas_category = "Ultra High (60M+)"
                gas_emoji = "🔥🔥🔥"
            elif max_gas >= 36000000:
                gas_category = "High (36M)"
                gas_emoji = "🔥🔥"
            elif max_gas >= 30000000:
                gas_category = "Standard (30M)"
                gas_emoji = "🔥"
            else:
                gas_category = "Conservative"
                gas_emoji = "❄️"
            
            # Get display name
            ens_name = ens_names.get(operator_addr, "")
            if ens_name:
                display_name = f"{ens_name} ({operator_addr[:8]}...{operator_addr[-6:]})"
            else:
                display_name = f"{operator_addr[:8]}...{operator_addr[-6:]}"
            
            gas_data.append({
                'operator': operator_addr,
                'display_name': display_name,
                'ens_name': ens_name,
                'total_validators': len(gas_limits),
                'gas_limits': gas_limits,
                'unique_limits': unique_limits,
                'average_gas_limit': avg_gas,
                'max_gas_limit': max_gas,
                'min_gas_limit': min(gas_limits),
                'strategy': strategy,
                'consistency_score': consistency_score,
                'gas_category': gas_category,
                'gas_emoji': gas_emoji
            })
    
    return sorted(gas_data, key=lambda x: x['max_gas_limit'], reverse=True)

def create_gas_limit_distribution_chart(mev_data):
    """Create gas limit distribution chart"""
    if not mev_data:
        return None
    
    gas_analysis = mev_data.get('gas_limit_analysis', {})
    distribution = gas_analysis.get('distribution', {})
    
    if not distribution:
        return None
    
    # Convert to human readable format and sort by gas limit (ascending)
    gas_data = []
    for gas_limit, count in distribution.items():
        gas_limit_int = int(gas_limit)
        if gas_limit_int >= 60000000:
            label = f"Ultra High\n{gas_limit_int//1000000}M gas"
            color = '#FF4444'  # Red
        elif gas_limit_int >= 36000000:
            label = f"High\n{gas_limit_int//1000000}M gas"
            color = '#FF8800'  # Orange
        else:
            label = f"Standard\n{gas_limit_int//1000000}M gas"
            color = '#4488FF'  # Blue
        
        gas_data.append({
            'gas_limit': gas_limit_int,
            'label': label,
            'count': count,
            'color': color
        })
    
    # Sort by gas limit in ascending order
    gas_data.sort(key=lambda x: x['gas_limit'])
    
    labels = [item['label'] for item in gas_data]
    values = [item['count'] for item in gas_data]
    colors = [item['color'] for item in gas_data]
    
    fig = go.Figure(data=[go.Bar(
        x=labels,
        y=values,
        marker_color=colors,
        text=values,
        textposition='auto'
    )])
    
    fig.update_layout(
        title="🔥 Gas Limit Distribution Across All Validators",
        xaxis_title="Gas Limit Setting",
        yaxis_title="Number of Validators",
        height=400,
        showlegend=False
    )
    
    return fig

def create_operator_gas_strategy_chart(gas_data):
    """Create operator gas strategy comparison"""
    if not gas_data:
        return None
    
    # Group by gas category
    category_counts = {}
    for operator in gas_data:
        category = operator['gas_category']
        if category not in category_counts:
            category_counts[category] = 0
        category_counts[category] += 1
    
    # Create pie chart
    labels = list(category_counts.keys())
    values = list(category_counts.values())
    
    # Assign colors based on gas level
    color_map = {
        'Ultra High (60M+)': '#FF4444',
        'High (36M)': '#FF8800', 
        'Standard (30M)': '#4488FF',
        'Conservative': '#88FF88'
    }
    colors = [color_map.get(label, '#CCCCCC') for label in labels]
    
    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=0.4,
        marker_colors=colors,
        textinfo='label+percent+value',
        textposition='outside'
    )])
    
    fig.update_layout(
        title="🎯 Operator Gas Strategy Distribution",
        height=600,
        showlegend=True
    )
    
    return fig

def display_health_status(concentration_metrics, total_active, total_exited):
    st.subheader("🏥 Network Health Status")

    col1, col2, col3 = st.columns(3)

    with col1:
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
    if not operator_performance:
        return

    st.subheader("🎯 Performance Health Status")

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

def display_ens_status(ens_names, operator_validators):
    if not ens_names:
        return

    st.subheader("🏷️ ENS Name Resolution Status")

    total_operators = len(operator_validators)
    ens_resolved = len(ens_names)
    coverage_pct = (ens_resolved / total_operators * 100) if total_operators > 0 else 0

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("ENS Names Found", f"{ens_resolved}")

    with col2:
        st.metric("Total Operators", f"{total_operators}")

    with col3:
        if coverage_pct >= 50:
            color = "status-good"
        elif coverage_pct >= 25:
            color = "status-warning"
        else:
            color = "status-danger"
        st.markdown(f"**Coverage:** <span class='{color}'>{coverage_pct:.1f}%</span>", unsafe_allow_html=True)

    with col4:
        validators_with_ens = sum(operator_validators.get(addr, 0) for addr in ens_names.keys())
        total_validators = sum(operator_validators.values())
        validator_coverage = (validators_with_ens / total_validators * 100) if total_validators > 0 else 0
        st.metric("Validator Coverage", f"{validator_coverage:.1f}%")
        st.caption(f"{validators_with_ens} of {total_validators} validators")

def main():
    display_logo()
    st.markdown("*Monitoring and analysis of NodeSet protocol validators on Stakewise - data cache updated every 15 minutes hit \"Refresh Data\" button to reload. Latest cache time is reported in UTC time.*")
    st.markdown("*** This site is independently maintained and is not affiliated with or managed by Nodeset. ***")

    refresh_col1, refresh_col2 = st.columns([3, 1])
    with refresh_col2:
        if st.button("🔄 Refresh Data", help="Reload validator data", use_container_width=True):
            st.cache_data.clear()
            st.rerun()

    cache_data = load_validator_data()
    if cache_data[0] is None:
        st.error("⚠ **Cache file not found!**")
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

    operator_validators = cache.get('operator_validators', {})
    operator_exited = cache.get('exited_validators', {})
    operator_performance = cache.get('operator_performance', {})
    ens_names = cache.get('ens_names', {})
    ens_last_updated = cache.get('ens_last_updated', 0)
    total_validators = cache.get('total_validators', 0)
    total_exited = cache.get('total_exited', 0)
    last_block = cache.get('last_block', 0)

    active_validators = {}
    for operator, total_count in operator_validators.items():
        exited_count = operator_exited.get(operator, 0)
        active_count = total_count - exited_count
        if active_count > 0:
            active_validators[operator] = active_count

    total_active = sum(active_validators.values())

    last_update = datetime.fromtimestamp(os.path.getmtime(cache_file))

    ens_update_str = ""
    if ens_last_updated > 0:
        ens_update_time = datetime.fromtimestamp(ens_last_updated)
        ens_update_str = f" • 🏷️ ENS: {ens_update_time.strftime('%H:%M:%S')}"

    st.caption(f"📊 Block: {last_block:,} • 🕘 {last_update.strftime('%H:%M:%S')}{ens_update_str} • 📁 {cache_file.split('/')[-1]}")

    st.markdown("### 📈 Network Overview")

    validator_indices = cache.get('validator_indices', {})
    pending_pubkeys = cache.get('pending_pubkeys', [])

    total_activated = len(validator_indices) if validator_indices else 0
    total_queued = len(pending_pubkeys) if pending_pubkeys else 0

    col1, col2, col3, col4, col5, col6 = st.columns(6)

    with col1:
        st.metric("Total Deposited Validators", f"{total_activated + total_queued:,}",
                  help="All validators that have been deposited (includes activated and queued)")

    with col2:
        st.metric("Activated Validators", f"{total_activated:,}",
                  help="Validators with assigned index numbers (participating in consensus)")

    with col3:
        st.metric("Validators in Queue", f"{total_queued:,}",
                  help="Validators deposited but waiting for activation")

    with col4:
        st.metric("Active Operators", len(active_validators))

    with col5:
        st.metric("Exited Validators", f"{total_exited:,}")

    with col6:
        exit_rate = (total_exited / total_validators * 100) if total_validators > 0 else 0
        st.metric("Exit Rate", f"{exit_rate:.1f}%")

    if total_active > 0:
        activation_rate = (total_activated / (total_activated + total_queued) * 100)
        queue_rate = (total_queued / (total_activated + total_queued) * 100)

        st.markdown("---")
        act_col1, act_col2 = st.columns(2)

        with act_col1:
            color = "status-good" if activation_rate >= 95 else "status-warning" if activation_rate >= 85 else "status-danger"
            st.markdown(f"**Activation Rate:** <span class='{color}'>{activation_rate:.1f}%</span>",
                       unsafe_allow_html=True)
            st.caption(f"{total_activated:,} of {total_activated + total_queued:,} validators activated")

        with act_col2:
            color = "status-good" if queue_rate <= 5 else "status-warning" if queue_rate <= 15 else "status-danger"
            st.markdown(f"**Queue Rate:** <span class='{color}'>{queue_rate:.1f}%</span>",
                       unsafe_allow_html=True)
            st.caption(f"{total_queued:,} validators waiting for activation")

    auto_refresh_col1, auto_refresh_col2 = st.columns([3, 1])
    with auto_refresh_col2:
        auto_refresh = st.checkbox("🔄 Auto-refresh (60s)")

    concentration_metrics = calculate_concentration_metrics(active_validators)

    if concentration_metrics:
        gini = concentration_metrics.get('gini_coefficient', 0)
        total_ops = concentration_metrics.get('total_operators', 0)
        avg_validators = (total_active / total_ops) if total_ops > 0 else 0

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

        if activation_rate >= 95:
            health_indicators.append("🟢 Fully Activated")
        elif activation_rate >= 85:
            health_indicators.append("🟡 Mostly Activated")
        else:
            health_indicators.append("🔴 Activation Pending")

        st.markdown(f"<div class='health-summary'><strong>Network Health:</strong> {' • '.join(health_indicators)}</div>", unsafe_allow_html=True)

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

    if ens_names:
        ens_coverage = len(ens_names) / len(operator_validators) * 100 if operator_validators else 0
        validators_with_ens = sum(operator_validators.get(addr, 0) for addr in ens_names.keys())
        validator_coverage = validators_with_ens / total_active * 100 if total_active > 0 else 0

        st.markdown(f"<div class='health-summary'><strong>ENS Resolution:</strong> {len(ens_names)} names found • {ens_coverage:.1f}% operator coverage • {validator_coverage:.1f}% validator coverage</div>", unsafe_allow_html=True)

    with st.expander("🔍 Detailed Health Metrics"):
        if concentration_metrics:
            detail_col1, detail_col2, detail_col3, detail_col4 = st.columns([1, 1, 1, 1])
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

            with detail_col3:
                if ens_names:
                    st.markdown("**ENS Resolution Metrics**")
                    st.write(f"• Total ENS Names: {len(ens_names)}")
                    st.write(f"• Operator Coverage: {ens_coverage:.1f}%")
                    st.write(f"• Validator Coverage: {validator_coverage:.1f}%")
                    if ens_last_updated > 0:
                        hours_ago = (datetime.now().timestamp() - ens_last_updated) / 3600
                        st.write(f"• Last Updated: {hours_ago:.1f}h ago")

            with detail_col4:
                st.markdown("**Activation Metrics**")
                st.write(f"• Activation Rate: {activation_rate:.1f}%")
                st.write(f"• Activated Count: {total_activated:,}")
                st.write(f"• Queue Count: {total_queued:,}")

    st.markdown("---")

    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9 = st.tabs([
        "📈 Distribution",
        "🎯 Concentration",
        "🏆 Top Operators",
        "⚡ Performance",
        "🤲 Proposals",
        "🚪 Exit Analysis",
        "💰 Costs",
        "🔥 Pump the Gas!",
        "📋 Raw Data"
    ])

    with tab1:
        if active_validators:
            fig_hist = create_distribution_histogram(active_validators)
            st.plotly_chart(fig_hist, use_container_width=True)

            st.subheader("📊 Key Insights")

            validator_counts = list(active_validators.values())
            max_validators = max(validator_counts) if validator_counts else 0
            total_validators_dist = sum(validator_counts)
            total_operators = len(validator_counts)
            avg_validators_dist = np.mean(validator_counts) if validator_counts else 0
            median_validators = np.median(validator_counts) if validator_counts else 0
            min_validators = min(validator_counts) if validator_counts else 0

            sorted_validators = sorted(validator_counts, reverse=True)
            top_3_validators = sum(sorted_validators[:3]) if len(sorted_validators) >= 3 else sum(sorted_validators)
            top_3_percentage = (top_3_validators / total_validators_dist * 100) if total_validators_dist > 0 else 0
            top_5_validators = sum(sorted_validators[:5]) if len(sorted_validators) >= 5 else sum(sorted_validators)
            top_5_percentage = (top_5_validators / total_validators_dist * 100) if total_validators_dist > 0 else 0
            top_10_validators = sum(sorted_validators[:10]) if len(sorted_validators) >= 10 else sum(sorted_validators)
            top_10_percentage = (top_10_validators / total_validators_dist * 100) if total_validators_dist > 0 else 0

            below_avg_count = sum(1 for count in validator_counts if count < avg_validators_dist)
            below_avg_percentage = (below_avg_count / total_operators * 100) if total_operators > 0 else 0

            large_operators_count = sum(1 for count in validator_counts if count > median_validators)
            large_operators_percentage = (large_operators_count / total_operators * 100) if total_operators > 0 else 0

            cap_level = max_validators

            validators_to_cap = sum(max(0, cap_level - count) for count in validator_counts)

            eth_to_cap = validators_to_cap * 32

            operators_at_cap = sum(1 for count in validator_counts if count == cap_level)
            operators_at_cap_percentage = (operators_at_cap / total_operators * 100) if total_operators > 0 else 0

            operators_near_cap = sum(1 for count in validator_counts if count >= cap_level * 0.75)
            operators_near_cap_percentage = (operators_near_cap / total_operators * 100) if total_operators > 0 else 0

            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric("Largest Operator", f"{max_validators} validators")
            with col2:
                st.metric("Average per Operator", f"{avg_validators_dist:.1f} validators")
            with col3:
                st.metric("Median per Operator", f"{median_validators:.1f} validators")
            with col4:
                st.metric("Smallest Operator", f"{min_validators} validators")

            col5, col6, col7, col8 = st.columns(4)
            with col5:
                st.metric("Top 3 Operators Control", f"{top_3_percentage:.1f}%")
                st.caption(f"{top_3_validators} of {total_validators_dist} validators")
            with col6:
                st.metric("Top 5 Operators Control", f"{top_5_percentage:.1f}%")
                st.caption(f"{top_5_validators} of {total_validators_dist} validators")
            with col7:
                st.metric("Top 10 Operators Control", f"{top_10_percentage:.1f}%")
                st.caption(f"{top_10_validators} of {total_validators_dist} validators")
            with col8:
                st.metric("Below Average Operators", f"{below_avg_percentage:.1f}%")
                st.caption(f"{below_avg_count} operators")

            col9, col10, col11, col12 = st.columns(4)
            with col9:
                st.metric("Validators to Cap", f"{validators_to_cap:,}")
                st.caption("Total needed to reach cap")
            with col10:
                st.metric("ETH to Cap", f"{eth_to_cap:,} ETH")
                st.caption(f"@ 32 ETH per validator")
            with col11:
                st.metric("Operators at Cap", f"{operators_at_cap_percentage:.1f}%")
                st.caption(f"{operators_at_cap} operators")
            with col12:
                st.metric("Operators at 75%+ of Cap", f"{operators_near_cap_percentage:.1f}%")
                st.caption(f"{operators_near_cap} ops (≥75% of cap)")
        else:
            st.info("No active validator data available for insights.")

    with tab2:
        if concentration_metrics:
            col1, col2 = st.columns([2, 1])

            with col1:
                fig_curve = create_concentration_curve(active_validators)
                st.plotly_chart(fig_curve, use_container_width=True)

            with col2:
                st.subheader("🔍 Concentration Metrics")

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
        st.subheader("🏆 Top Operators by Active Validators")

        df_operators = create_top_operators_table(operator_validators, operator_exited, ens_names)

        if not df_operators.empty:
            display_df = df_operators.copy()

            display_df['Active'] = display_df['Active'].astype(str)
            display_df['Total'] = display_df['Total'].astype(str)
            display_df['Exited'] = display_df['Exited'].astype(str)

            st.dataframe(
                display_df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Rank": st.column_config.NumberColumn("Rank", width="small"),
                    "Address": st.column_config.TextColumn("Address", width="large"),
                    "ENS Name": st.column_config.TextColumn("ENS Name", width="small"),
                    "Active": st.column_config.TextColumn("Active", width="small"),
                    "Total": st.column_config.TextColumn("Total", width="small"),
                    "Exited": st.column_config.TextColumn("Exited", width="small"),
                    "Exit Rate": st.column_config.TextColumn("Exit Rate", width="small"),
                    "Market Share": st.column_config.TextColumn("Market Share", width="small")
                }
            )

            csv = df_operators.to_csv(index=False)
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
                operator_performance, operator_validators, ens_names
            )

            if fig_scatter and fig_hist:
                st.plotly_chart(fig_scatter, use_container_width=True)

                col1, col2 = st.columns(2)

                with col1:
                    st.plotly_chart(fig_hist, use_container_width=True)

                with col2:
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

                st.subheader("🏆 Operators by Performance")
                perf_table_df = create_performance_table(
                    operator_performance, operator_validators, operator_exited, ens_names
                )

                if not perf_table_df.empty:
                    display_perf_df = perf_table_df.drop(['Performance_Raw'], axis=1).copy()

                    display_perf_df['Active'] = display_perf_df['Active'].astype(str)
                    display_perf_df['Total'] = display_perf_df['Total'].astype(str)
                    display_perf_df['Exited'] = display_perf_df['Exited'].astype(str)

                    st.dataframe(
                        display_perf_df,
                        use_container_width=True,
                        hide_index=True,
                        column_config={
                            "Rank": st.column_config.NumberColumn("Rank", width="small"),
                            "Address": st.column_config.TextColumn("Address", width="large"),
                            "ENS Name": st.column_config.TextColumn("ENS Name", width="small"),
                            "Performance": st.column_config.TextColumn("Performance", width="small"),
                            "Category": st.column_config.TextColumn("Category", width="small"),
                            "Active": st.column_config.TextColumn("Active", width="small"),
                            "Total": st.column_config.TextColumn("Total", width="small"),
                            "Exited": st.column_config.TextColumn("Exited", width="small")
                        }
                    )

                    export_perf_df = perf_table_df.drop(['Performance_Raw'], axis=1)

                    perf_csv = export_perf_df.to_csv(index=False)
                    st.download_button(
                        label="📥 Download Performance Data",
                        data=perf_csv,
                        file_name=f"nodeset_performance_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv"
                    )
            else:
                st.info("Insufficient performance data for analysis.")
        else:
            st.info("No performance data available in cache file.")

    with tab5:
        st.subheader("🤲 Proposal Analysis")
        
        proposals_cache = load_proposals_data()
        if proposals_cache[0] is None:
            st.error("⚠ **Proposals data file not found!**")
            st.markdown("""
            **Setup Instructions:**
            1. Ensure `proposals.json` exists in your directory
            2. Place the file alongside this dashboard script
            
            **Expected file locations:**
            - `./proposals.json`
            - `./data/proposals.json`
            """)
        else:
            proposals_data, proposals_file = proposals_cache
            metadata = proposals_data.get('metadata', {})
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Proposals", f"{metadata.get('total_proposals', 0):,}")
                
            with col2:
                st.metric("Total ETH Value", f"{metadata.get('total_value_eth', 0):.3f} ETH")
                
            with col3:
                st.metric("Operators with Proposals", f"{metadata.get('operators_tracked', 0)}")
                
            with col4:
                total_proposals = metadata.get('total_proposals', 1)
                total_value = metadata.get('total_value_eth', 0)
                avg_value = total_value / max(total_proposals, 1)
                st.metric("Avg Value/Proposal", f"{avg_value:.4f} ETH")
            
            if metadata.get('last_updated'):
                st.caption(f"📊 Proposals: {metadata['last_updated']} • 📁 {proposals_file.split('/')[-1]}")
            
            # Add Largest Proposals Table (NEW)
            st.subheader("💎 Largest Proposals by Value")
            st.caption("Showing the 5 highest value proposals across all operators")
            
            largest_proposals_df = create_largest_proposals_table(proposals_data, ens_names, limit=5)
            
            if not largest_proposals_df.empty:
                # Display the table
                display_largest_df = largest_proposals_df.drop(['Operator Address'], axis=1)  # Hide full address for cleaner display
                
                st.dataframe(
                    display_largest_df,
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "Date": st.column_config.TextColumn("Date", width="medium"),
                        "Operator": st.column_config.TextColumn("Operator", width="large"),
                        "Validator Pubkey": st.column_config.TextColumn("Validator Pubkey", width="large"),
                        "ETH Value": st.column_config.TextColumn("ETH Value", width="small"),
                        "Slot": st.column_config.TextColumn("Slot", width="small"),
                        "Gas Used": st.column_config.TextColumn("Gas Used", width="small"),
                        "Gas Utilization": st.column_config.TextColumn("Gas %", width="small"),
                        "TX Count": st.column_config.TextColumn("TXs", width="small")
                    }
                )
                
                # Optional: Add download button for largest proposals
                largest_csv = largest_proposals_df.to_csv(index=False)
                st.download_button(
                    label="📥 Download Largest Proposals",
                    data=largest_csv,
                    file_name=f"largest_proposals_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
            else:
                st.info("No proposals available.")
            
            st.markdown("---")  # Add separator between the two tables
            
            # Add Latest Proposals Table
            st.subheader("🕘 Latest Proposals")
            st.caption("Showing the 5 most recent proposals across all operators")
            
            latest_proposals_df = create_latest_proposals_table(proposals_data, ens_names, limit=5)
            
            if not latest_proposals_df.empty:
                # Display the table
                display_latest_df = latest_proposals_df.drop(['Operator Address'], axis=1)  # Hide full address for cleaner display
                
                st.dataframe(
                    display_latest_df,
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "Date": st.column_config.TextColumn("Date", width="medium"),
                        "Operator": st.column_config.TextColumn("Operator", width="large"),
                        "Validator Pubkey": st.column_config.TextColumn("Validator Pubkey", width="large"),
                        "ETH Value": st.column_config.TextColumn("ETH Value", width="small"),
                        "Slot": st.column_config.TextColumn("Slot", width="small"),
                        "Gas Used": st.column_config.TextColumn("Gas Used", width="small"),
                        "Gas Utilization": st.column_config.TextColumn("Gas %", width="small"),
                        "TX Count": st.column_config.TextColumn("TXs", width="small")
                    }
                )
                
                # Optional: Add download button for latest proposals
                latest_csv = latest_proposals_df.to_csv(index=False)
                st.download_button(
                    label="📥 Download Latest Proposals",
                    data=latest_csv,
                    file_name=f"latest_proposals_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
            else:
                st.info("No recent proposals available.")
            
            st.markdown("---")  # Add separator before the next section
            
            proposals_operators = create_proposals_operators_table(proposals_data, ens_names)
            
            if proposals_operators:
                st.subheader("🏆 Proposal Operators by Proposal Count")
                st.caption(f"Showing {len(proposals_operators)} operators with proposals")
                
                search_term = st.text_input(
                    "🔍 Search proposal operators by address or ENS name",
                    placeholder="Enter address, ENS name, or partial match",
                    key="proposals_search_input"
                )
                
                if search_term:
                    filtered_ops = []
                    for op in proposals_operators:
                        ens_name = op['ens_name']
                        if (search_term.lower() in op['operator'].lower() or
                            (ens_name and search_term.lower() in ens_name.lower())):
                            filtered_ops.append(op)
                    
                    if filtered_ops:
                        st.info(f"Found {len(filtered_ops)} operators matching '{search_term}'")
                        display_ops = filtered_ops
                    else:
                        st.warning(f"No operators found matching '{search_term}'")
                        display_ops = []
                else:
                    display_ops = proposals_operators
                
                for i, op_data in enumerate(display_ops):
                    ens_name = op_data['ens_name']
                    operator = op_data['operator']
                    
                    if ens_name:
                        header = f"#{i+1} 🏷️ {ens_name} ({operator}) - {op_data['proposal_count']} proposals"
                    else:
                        header = f"#{i+1} {operator} - {op_data['proposal_count']} proposals"
                    
                    header += f" ({op_data['total_value_eth']:.4f} ETH)"
                    
                    with st.expander(header, expanded=False):
                        if ens_name:
                            st.markdown(f"**ENS:** {ens_name}")
                        st.markdown(f"**Address:** `{operator}`")
                        
                        st.markdown("---")
                        
                        detail_col1, detail_col2, detail_col3 = st.columns(3)
                        
                        with detail_col1:
                            st.markdown("**💰 Proposal Performance**")
                            st.write(f"• Proposals: **{op_data['proposal_count']}**")
                            st.write(f"• Total Value: **{op_data['total_value_eth']:.4f} ETH**")
                            st.write(f"• Average: **{op_data['average_value_eth']:.4f} ETH**")
                            st.write(f"• Highest: **{op_data['highest_value_eth']:.4f} ETH**")
                        
                        with detail_col2:
                            st.markdown("**⚡ Block Performance**")
                            st.write(f"• Gas Used: **{op_data['total_gas_used']:,}**")
                            st.write(f"• Avg Gas Util: **{op_data['avg_gas_utilization']:.1f}%**")
                            st.write(f"• Avg TXs: **{op_data['avg_tx_count']:.0f}**")
                            
                            efficiency = op_data['total_value_eth'] / (op_data['total_gas_used'] / 1e9) if op_data['total_gas_used'] > 0 else 0
                            st.write(f"• ETH/M Gas: **{efficiency:.6f}**")
                        
                        with detail_col3:
                            st.markdown("**📅 Activity**")
                            st.write(f"• First: **{op_data['first_proposal']}**")
                            st.write(f"• Latest: **{op_data['last_proposal']}**")
                            
                            if len(op_data['proposals']) > 1:
                                try:
                                    first = datetime.strptime(op_data['first_proposal'], '%Y-%m-%d %H:%M:%S')
                                    last = datetime.strptime(op_data['last_proposal'], '%Y-%m-%d %H:%M:%S')
                                    span = (last - first).days
                                    st.write(f"• Span: **{span} days**")
                                    if span > 0:
                                        freq = op_data['proposal_count'] / span
                                        st.write(f"• Rate: **{freq:.2f}/day**")
                                except:
                                    pass
                        
                        st.markdown("**📋 Proposal History**")
                        proposals_list = op_data['proposals']
                        
                        if proposals_list:
                            df = pd.DataFrame(proposals_list)
                            
                            display_df = df[['date', 'slot', 'total_value_eth', 'gas_used', 'gas_utilization', 'tx_count', 'base_fee', 'validator_pubkey']].copy()
                            display_df.columns = ['Date', 'Slot', 'ETH Value', 'Gas Used', 'Gas %', 'TXs', 'Base Fee', 'Validator Pubkey']
                            
                            display_df['ETH Value'] = display_df['ETH Value'].apply(lambda x: f"{x:.4f}")
                            display_df['Gas Used'] = display_df['Gas Used'].astype(str)
                            display_df['Gas %'] = display_df['Gas %'].apply(lambda x: f"{x:.1f}%")
                            display_df['TXs'] = display_df['TXs'].astype(str)
                            display_df['Base Fee'] = display_df['Base Fee'].astype(str)
                            display_df['Slot'] = display_df['Slot'].astype(str)
                            # Keep validator pubkey full - no truncation
                            
                            display_df = display_df.sort_values('Date', ascending=False)
                            
                            st.dataframe(
                                display_df,
                                use_container_width=True,
                                hide_index=True,
                                column_config={
                                    "Date": st.column_config.TextColumn("Date", width="medium"),
                                    "Slot": st.column_config.TextColumn("Slot", width="small"),
                                    "ETH Value": st.column_config.TextColumn("ETH Value", width="small"),
                                    "Gas Used": st.column_config.TextColumn("Gas Used", width="small"),
                                    "Gas %": st.column_config.TextColumn("Gas %", width="small"),
                                    "TXs": st.column_config.TextColumn("TXs", width="small"),
                                    "Base Fee": st.column_config.TextColumn("Base Fee", width="small"),
                                    "Validator Pubkey": st.column_config.TextColumn("Validator Pubkey", width="large")
                                }
                            )
                            
                            if ens_name:
                                filename = ens_name.replace('.', '_')
                            else:
                                filename = f"{operator[:8]}_{operator[-6:]}"
                            
                            csv = df.to_csv(index=False)
                            st.download_button(
                                label=f"📥 Download {ens_name if ens_name else operator[:10]+'...'} proposals",
                                data=csv,
                                file_name=f"proposals_{filename}_{datetime.now().strftime('%Y%m%d')}.csv",
                                mime="text/csv",
                                key=f"proposals_download_{i}"
                            )
                        else:
                            st.info("No proposal details available.")
                
                st.markdown("---")
                col1, col2 = st.columns([3, 1])
                with col2:
                    export_data = []
                    for op in proposals_operators:
                        export_data.append({
                            'address': op['operator'],
                            'ens_name': op['ens_name'],
                            'proposal_count': op['proposal_count'],
                            'total_value_eth': op['total_value_eth'],
                            'average_value_eth': op['average_value_eth'],
                            'highest_value_eth': op['highest_value_eth'],
                            'total_gas_used': op['total_gas_used'],
                            'avg_gas_utilization': op['avg_gas_utilization'],
                            'avg_tx_count': op['avg_tx_count'],
                            'first_proposal': op['first_proposal'],
                            'last_proposal': op['last_proposal']
                        })
                    
                    export_df = pd.DataFrame(export_data)
                    export_csv = export_df.to_csv(index=False)
                    
                    st.download_button(
                        label="📥 Download All Proposal Data",
                        data=export_csv,
                        file_name=f"proposals_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv",
                        use_container_width=True
                    )
            else:
                st.info("No proposal data available.")

    with tab6:
        if total_exited > 0:
            st.subheader("🚪 Exit Analysis")

            col1, col2 = st.columns(2)

            with col1:
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
                if operator_validators and operator_exited:
                    exit_rate_data = []
                    for addr, total_count in operator_validators.items():
                        if total_count >= 2:
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

            st.subheader("Operators with Exits")
            exited_operators_data = []
            for addr, exit_count in operator_exited.items():
                if exit_count > 0:
                    total_count = operator_validators.get(addr, 0)
                    active_count = total_count - exit_count
                    exit_rate = (exit_count / total_count * 100) if total_count > 0 else 0
                    display_name = format_operator_display_plain(addr, ens_names, show_full_address=True)

                    exited_operators_data.append({
                        'Operator': display_name,
                        'Full Address': addr,
                        'Exits': exit_count,
                        'Still Active': active_count,
                        'Total Ever': total_count,
                        'Exit Rate': f"{exit_rate:.1f}%"
                    })

            if exited_operators_data:
                df_exited = pd.DataFrame(exited_operators_data)
                df_exited = df_exited.sort_values('Exit Rate', key=lambda x: x.str.rstrip('%').astype(float), ascending=False)

                df_exited['Exits'] = df_exited['Exits'].astype(str)
                df_exited['Still Active'] = df_exited['Still Active'].astype(str)
                df_exited['Total Ever'] = df_exited['Total Ever'].astype(str)

                display_exited_df = df_exited.drop(['Full Address'], axis=1)
                st.dataframe(
                    display_exited_df,
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "Operator": st.column_config.TextColumn("Operator", width="large"),
                        "Exits": st.column_config.TextColumn("Exits", width="small"),
                        "Still Active": st.column_config.TextColumn("Still Active", width="small"),
                        "Total Ever": st.column_config.TextColumn("Total Ever", width="small"),
                        "Exit Rate": st.column_config.TextColumn("Exit Rate", width="small")
                    }
                )

                exits_csv = display_exited_df.to_csv(index=False)
                st.download_button(
                    label="📥 Download Exit Data",
                    data=exits_csv,
                    file_name=f"nodeset_exits_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
            else:
                st.info("No exits detected in current data.")
        else:
            st.info("😊 Great news! No validator exits detected yet.")

    with tab7:
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
            total_gas_spent = sum(cost['total_cost_eth'] for cost in operator_costs.values())
            total_transactions = sum(cost['total_txs'] for cost in operator_costs.values())
            total_successful = sum(cost['successful_txs'] for cost in operator_costs.values())
            total_failed = sum(cost['failed_txs'] for cost in operator_costs.values())
            operators_with_costs = len([c for c in operator_costs.values() if c['total_txs'] > 0])

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

            col5, col6, col7, col8 = st.columns(4)

            with col5:
                st.metric("Operators Tracked", f"{operators_with_costs}")

            with col6:
                st.metric("Failed Transactions", f"{total_failed:,}")

            with col7:
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
                cost_data.sort(key=lambda x: x['total_cost_eth'], reverse=True)

                st.subheader("📊 Operator Cost Rankings")
                st.caption(f"Showing {len(cost_data)} operators with transaction data, sorted by total gas spent")

                search_term = st.text_input(
                    "🔍 Search operators by address or ENS name",
                    placeholder="Enter address, ENS name, or partial match (e.g., 0x1878f36, vitalik.eth)",
                    help="Search is case-insensitive and matches any part of the address or ENS name",
                    key="cost_search_input"
                )

                if search_term:
                    filtered_data = []
                    for row in cost_data:
                        ens_name = ens_names.get(row['operator'], "")
                        if (search_term.lower() in row['operator'].lower() or
                            (ens_name and search_term.lower() in ens_name.lower())):
                            filtered_data.append(row)

                    if filtered_data:
                        st.info(f"Found {len(filtered_data)} operators matching '{search_term}'")
                        display_data = filtered_data
                    else:
                        st.warning(f"No operators found matching '{search_term}'")
                        display_data = []
                else:
                    display_data = cost_data

                for i, row in enumerate(display_data):
                    ens_name = ens_names.get(row['operator'], "")
                    if ens_name:
                        header_display = f"#{i+1} 🏷️ {ens_name} ({row['operator']}) - {row['total_cost_eth']:.6f} ETH ({row['total_txs']} txs)"
                        operator_info = f"**ENS:** {ens_name}  \n**Address:** `{row['operator']}`"
                    else:
                        header_display = f"#{i+1} {row['operator']} - {row['total_cost_eth']:.6f} ETH ({row['total_txs']} txs)"
                        operator_info = f"**Address:** `{row['operator']}`"

                    with st.expander(header_display, expanded=False):
                        st.markdown("**🔗 Operator Information**")
                        st.markdown(operator_info)

                        st.markdown("---")

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

                        operator_txs = operator_transactions.get(row['operator'], [])
                        if operator_txs:
                            st.markdown("**📋 Transaction History**")

                            tx_df = pd.DataFrame(operator_txs)
                            tx_df['datetime'] = pd.to_datetime(tx_df['date'] + ' ' + tx_df['time'])
                            tx_df = tx_df.sort_values('datetime', ascending=False)

                            tx_df['validator_count'] = tx_df.apply(
                                lambda row_data: row_data.get('validator_count', 0) if row_data['status'] == 'Successful' else 0,
                                axis=1
                            )

                            tx_df['validator_count'] = pd.to_numeric(tx_df['validator_count'], errors='coerce').fillna(0).astype(int)

                            display_tx_df = tx_df[['date', 'time', 'total_cost_eth', 'status', 'validator_count', 'gas_used', 'gas_price']].copy()
                            display_tx_df['validator_count_display'] = display_tx_df.apply(
                                lambda row: str(row['validator_count']) if row['status'] == 'Successful' and row['validator_count'] > 0 else '',
                                axis=1
                            )

                            final_display_df = display_tx_df[['date', 'time', 'total_cost_eth', 'status', 'validator_count_display', 'gas_used', 'gas_price']].copy()
                            final_display_df.columns = ['Date', 'Time', 'Cost (ETH)', 'Status', 'Validators', 'Gas Used', 'Gas Price']

                            final_display_df['Gas Used'] = final_display_df['Gas Used'].astype(str)
                            final_display_df['Gas Price'] = final_display_df['Gas Price'].astype(str)

                            st.dataframe(
                                final_display_df,
                                use_container_width=True,
                                hide_index=True,
                                column_config={
                                    "Date": st.column_config.TextColumn("Date", width="small"),
                                    "Time": st.column_config.TextColumn("Time", width="small"),
                                    "Cost (ETH)": st.column_config.TextColumn("Cost (ETH)", width="small"),
                                    "Status": st.column_config.TextColumn("Status", width="small"),
                                    "Validators": st.column_config.TextColumn("Validators", width="small"),
                                    "Gas Used": st.column_config.TextColumn("Gas Used", width="small"),
                                    "Gas Price": st.column_config.TextColumn("Gas Price", width="small")
                                }
                            )

                            ens_name = ens_names.get(row['operator'], "")
                            if ens_name:
                                filename_part = ens_name.replace('.', '_')
                            else:
                                filename_part = f"{row['operator'][:8]}_{row['operator'][-6:]}"

                            csv_data = tx_df.to_csv(index=False)
                            st.download_button(
                                label=f"📥 Download {ens_name if ens_name else row['operator'][:10]+'...'} transactions",
                                data=csv_data,
                                file_name=f"nodeset_costs_{filename_part}_{datetime.now().strftime('%Y%m%d')}.csv",
                                mime="text/csv",
                                key=f"download_{i}"
                            )
                        else:
                            st.info("No detailed transaction data available for this operator.")

                st.markdown("---")
                col1, col2 = st.columns([3, 1])
                with col2:
                    summary_df = pd.DataFrame(cost_data)

                    export_cost_data = []
                    for row in cost_data:
                        ens_name = ens_names.get(row['operator'], "")
                        export_cost_data.append({
                            'address': row['operator'],
                            'ens_name': ens_name,
                            'total_cost_eth': row['total_cost_eth'],
                            'total_txs': row['total_txs'],
                            'successful_txs': row['successful_txs'],
                            'failed_txs': row['failed_txs'],
                            'success_rate': row['success_rate'],
                            'validators': row['validators'],
                            'cost_per_validator': row['cost_per_validator']
                        })

                    export_df = pd.DataFrame(export_cost_data)
                    summary_csv = export_df.to_csv(index=False)

                    st.download_button(
                        label="📥 Download All Cost Data",
                        data=summary_csv,
                        file_name=f"nodeset_all_costs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv",
                        use_container_width=True
                    )
            else:
                st.info("No operators found with transaction cost data.")

    with tab8:
        st.subheader("🔥 Pump the Gas! - Gas Limit Analysis")
        st.markdown("*Analysis of gas limit configurations across NodeSet operators*")
        
        # Load MEV analysis data
        mev_cache = load_mev_analysis_data()
        if mev_cache[0] is None:
            st.error("⚠ **MEV analysis data file not found!**")
            st.markdown("""
            **Setup Instructions:**
            1. Ensure `mev_analysis_results.json` exists in your directory
            2. Place the file alongside this dashboard script
            
            **Expected file locations:**
            - `./mev_analysis_results.json`
            - `./data/mev_analysis_results.json`
            """)
        else:
            mev_data, mev_file = mev_cache
            
            # Overall gas limit statistics
            gas_analysis = mev_data.get('gas_limit_analysis', {})
            distribution = gas_analysis.get('distribution', {})
            consistency_stats = gas_analysis.get('consistency_stats', {})
            
            if distribution:
                # Summary metrics
                col1, col2, col3, col4 = st.columns(4)
                
                total_validators = sum(distribution.values())
                ultra_high = distribution.get('60000000', 0)
                high = distribution.get('36000000', 0) 
                standard = distribution.get('30000000', 0)
                
                with col1:
                    ultra_pct = (ultra_high / total_validators * 100) if total_validators > 0 else 0
                    st.metric("🔥🔥🔥 Ultra High Gas (60M)", f"{ultra_high:,}", f"{ultra_pct:.1f}%")
                
                with col2:
                    high_pct = (high / total_validators * 100) if total_validators > 0 else 0
                    st.metric("🔥🔥 High Gas (36M)", f"{high:,}", f"{high_pct:.1f}%")
                
                with col3:
                    std_pct = (standard / total_validators * 100) if total_validators > 0 else 0
                    st.metric("🔥 Standard Gas (30M)", f"{standard:,}", f"{std_pct:.1f}%")
                
                with col4:
                    consistency_rate = consistency_stats.get('consistency_rate', 0)
                    st.metric("🎯 Consistency Rate", f"{consistency_rate:.1f}%")
                
                # Gas limit distribution chart
                fig_distribution = create_gas_limit_distribution_chart(mev_data)
                if fig_distribution:
                    st.plotly_chart(fig_distribution, use_container_width=True)
                
                # Operator analysis
                gas_operator_data = analyze_gas_limits_by_operator(mev_data, ens_names)
                
                if gas_operator_data:
                    # Make the pie chart larger by giving it full width
                    fig_strategy = create_operator_gas_strategy_chart(gas_operator_data)
                    if fig_strategy:
                        st.plotly_chart(fig_strategy, use_container_width=True)
                    
                    # Detailed operator breakdown
                    st.subheader("🏆 Operator Gas Limit Rankings")
                    st.caption("Operators ranked by their maximum gas limit settings")
                    
                    # Search functionality
                    search_term = st.text_input(
                        "🔍 Search operators by address or ENS name",
                        placeholder="Enter address, ENS name, or partial match",
                        key="gas_search_input"
                    )
                    
                    if search_term:
                        filtered_data = []
                        for op in gas_operator_data:
                            if (search_term.lower() in op['operator'].lower() or
                                (op['ens_name'] and search_term.lower() in op['ens_name'].lower())):
                                filtered_data.append(op)
                        
                        if filtered_data:
                            st.info(f"Found {len(filtered_data)} operators matching '{search_term}'")
                            display_data = filtered_data
                        else:
                            st.warning(f"No operators found matching '{search_term}'")
                            display_data = []
                    else:
                        display_data = gas_operator_data
                    
                    # Display operator details
                    for i, op_data in enumerate(display_data):
                        ens_name = op_data['ens_name']
                        
                        header = f"#{i+1} {op_data['gas_emoji']} "
                        if ens_name:
                            header += f"{ens_name} ({op_data['operator'][:8]}...{op_data['operator'][-6:]})"
                        else:
                            header += f"{op_data['operator'][:8]}...{op_data['operator'][-6:]}"
                        
                        header += f" - {op_data['gas_category']} | {op_data['total_validators']} validators"
                        
                        with st.expander(header, expanded=False):
                            if ens_name:
                                st.markdown(f"**🏷️ ENS:** {ens_name}")
                            st.markdown(f"**🔍 Address:** `{op_data['operator']}`")
                            
                            st.markdown("---")
                            
                            detail_col1, detail_col2, detail_col3 = st.columns(3)
                            
                            with detail_col1:
                                st.markdown("**🔥 Gas Limit Strategy**")
                                st.write(f"• Category: **{op_data['gas_category']}**")
                                st.write(f"• Strategy: **{op_data['strategy']}**")
                                st.write(f"• Consistency: **{op_data['consistency_score']:.1f}%**")
                            
                            with detail_col2:
                                st.markdown("**📊 Gas Limit Stats**")
                                st.write(f"• Maximum: **{op_data['max_gas_limit']:,}**")
                                st.write(f"• Average: **{op_data['average_gas_limit']:,.0f}**")
                                st.write(f"• Minimum: **{op_data['min_gas_limit']:,}**")
                            
                            with detail_col3:
                                st.markdown("**🔍 Validator Details**")
                                st.write(f"• Total Validators: **{op_data['total_validators']}**")
                                st.write(f"• Unique Gas Limits: **{len(op_data['unique_limits'])}**")
                                if len(op_data['unique_limits']) > 1:
                                    st.write(f"• Limits Used: **{', '.join(f'{x:,}' for x in sorted(op_data['unique_limits'], reverse=True))}**")
                            
                            # Show individual validator gas limits if mixed strategy
                            if op_data['strategy'] == "Mixed":
                                st.markdown("**⚠️ Mixed Gas Limit Configuration**")
                                gas_limit_counts = {}
                                for limit in op_data['gas_limits']:
                                    gas_limit_counts[limit] = gas_limit_counts.get(limit, 0) + 1
                                
                                for limit, count in sorted(gas_limit_counts.items(), reverse=True):
                                    pct = (count / op_data['total_validators'] * 100)
                                    st.write(f"• **{limit:,}** gas: {count} validators ({pct:.1f}%)")
                    
                    # Download functionality
                    st.markdown("---")
                    col1, col2 = st.columns([3, 1])
                    with col2:
                        # Prepare export data
                        export_data = []
                        for op in gas_operator_data:
                            export_data.append({
                                'address': op['operator'],
                                'ens_name': op['ens_name'],
                                'total_validators': op['total_validators'],
                                'max_gas_limit': op['max_gas_limit'],
                                'average_gas_limit': op['average_gas_limit'],
                                'min_gas_limit': op['min_gas_limit'],
                                'gas_category': op['gas_category'],
                                'strategy': op['strategy'],
                                'consistency_score': op['consistency_score'],
                                'unique_gas_limits': len(op['unique_limits'])
                            })
                        
                        export_df = pd.DataFrame(export_data)
                        export_csv = export_df.to_csv(index=False)
                        
                        st.download_button(
                            label="📥 Download Gas Analysis",
                            data=export_csv,
                            file_name=f"gas_limit_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                            mime="text/csv",
                            use_container_width=True
                        )
                else:
                    st.info("No operator gas limit data available for analysis.")
            else:
                st.info("No gas limit distribution data available.")

    with tab9:
        st.subheader("📋 Raw Cache Data")

        col1, col2 = st.columns(2)

        with col1:
            cache_summary = {
                "total_validators": cache.get('total_validators', 0),
                "total_exited": cache.get('total_exited', 0),
                "last_block": cache.get('last_block', 0),
                "last_epoch_checked": cache.get('last_epoch_checked', 0),
                "total_operators": len(cache.get('operator_validators', {})),
                "pending_pubkeys": len(cache.get('pending_pubkeys', [])),
                "processed_transactions": len(cache.get('processed_transactions', [])),
                "performance_metrics": len(cache.get('operator_performance', {})),
                "cost_metrics": len(cache.get('operator_costs', {})),
                "transaction_records": len(cache.get('operator_transactions', {})),
                "ens_names_resolved": len(cache.get('ens_names', {})),
                "ens_last_updated": cache.get('ens_last_updated', 0),
                "ens_update_failures": len(cache.get('ens_update_failures', {})),
                "validator_indices": len(cache.get('validator_indices', {})),
                "validators_in_queue": len(cache.get('pending_pubkeys', []))
            }

            st.json(cache_summary)

        with col2:
            if st.button("🔄 Show Full Cache"):
                st.json(cache)

        if ens_names:
            st.subheader("🏷️ Resolved ENS Names")

            ens_data = []
            for addr, ens_name in ens_names.items():
                validator_count = operator_validators.get(addr, 0)
                active_count = validator_count - operator_exited.get(addr, 0)

                ens_data.append({
                    'ENS Name': ens_name,
                    'Address': addr,
                    'Active Validators': active_count,
                    'Total Validators': validator_count
                })

            if ens_data:
                ens_df = pd.DataFrame(ens_data)
                ens_df = ens_df.sort_values('Active Validators', ascending=False)

                ens_df['Active Validators'] = ens_df['Active Validators'].astype(str)
                ens_df['Total Validators'] = ens_df['Total Validators'].astype(str)

                st.dataframe(
                    ens_df,
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "ENS Name": st.column_config.TextColumn("ENS Name", width="small"),
                        "Address": st.column_config.TextColumn("Address", width="large"),
                        "Active Validators": st.column_config.TextColumn("Active Validators", width="small"),
                        "Total Validators": st.column_config.TextColumn("Total Validators", width="small")
                    }
                )

                ens_csv = ens_df.to_csv(index=False)
                st.download_button(
                    label="📥 Download ENS Data",
                    data=ens_csv,
                    file_name=f"nodeset_ens_names_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )

    if auto_refresh:
        import time
        time.sleep(60)
        st.rerun()

    st.markdown("---")
    ens_info = f" | ENS: {len(ens_names)} names resolved" if ens_names else ""
    st.markdown(f"*Dashboard last refreshed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{ens_info}*")

if __name__ == "__main__":
    main()
