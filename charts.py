import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from utils import format_operator_display_plain, get_performance_category

def create_performance_charts(operator_performance, operator_validators, ens_names):
    """Create performance scatter and histogram charts"""
    if not operator_performance:
        return None, None
    
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
        return None, None

    import pandas as pd
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

    return fig_scatter, fig_hist

def create_concentration_pie(operator_validators, ens_names, title="Validator Distribution"):
    """Create pie chart showing validator distribution"""
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
    """Create histogram of validator distribution"""
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
    """Create Lorenz curve for concentration analysis"""
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
