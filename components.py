import streamlit as st
import numpy as np
import os
from datetime import datetime
from utils import get_performance_category

def responsive_columns(column_spec):
    """Create responsive columns that work better at 125% zoom
    
    Args:
        column_spec: Either an integer (equal columns) or list of ratios
    
    Returns:
        Streamlit columns with responsive design considerations
    """
    # Add CSS for responsive column behavior
    st.markdown("""
    <style>
    /* Responsive column fixes for 125% zoom */
    @media (max-width: 1600px) {
        div[data-testid="column"] {
            min-width: 200px !important;
        }
    }
    
    @media (max-width: 1280px) {
        div[data-testid="column"] {
            min-width: 180px !important;
        }
    }
    
    @media (max-width: 1024px) {
        div[data-testid="column"] {
            min-width: 160px !important;
            margin-bottom: 1rem !important;
        }
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Create columns with the original specification
    # Streamlit will handle the responsive behavior with our CSS
    if isinstance(column_spec, int):
        return st.columns(column_spec)
    else:
        return st.columns(column_spec)

def mobile_optimized_layout(desktop_cols, mobile_cols=1):
    """
    Create a layout that automatically adapts based on screen size
    
    Args:
        desktop_cols: Number of columns for desktop (int or list of ratios)
        mobile_cols: Number of columns for mobile (default: 1 for single column)
    
    Returns:
        Column objects for layout
    """
    # Add JavaScript to detect screen size and adjust layout
    layout_script = f"""
    <script>
    function adjustLayout() {{
        const isMobile = window.innerWidth <= 768;
        const layoutInfo = {{
            isMobile: isMobile,
            desktopCols: {desktop_cols if isinstance(desktop_cols, int) else len(desktop_cols)},
            mobileCols: {mobile_cols}
        }};
        
        // Store in session storage for potential use
        sessionStorage.setItem('layoutInfo', JSON.stringify(layoutInfo));
        
        // Add CSS class for mobile layout
        if (isMobile) {{
            document.body.classList.add('mobile-layout');
            document.body.classList.remove('desktop-layout');
        }} else {{
            document.body.classList.add('desktop-layout');
            document.body.classList.remove('mobile-layout');
        }}
    }}
    
    adjustLayout();
    window.addEventListener('resize', adjustLayout);
    </script>
    
    <style>
    .mobile-layout .stColumns {{
        flex-direction: column !important;
    }}
    .mobile-layout .stColumn {{
        width: 100% !important;
        margin-bottom: 1rem !important;
    }}
    </style>
    """
    
    st.markdown(layout_script, unsafe_allow_html=True)
    
    # Return appropriate columns based on desktop configuration
    if isinstance(desktop_cols, int):
        return st.columns(desktop_cols)
    else:
        return st.columns(desktop_cols)

def mobile_friendly_tabs(tab_names, selected_index=0):
    """
    Create mobile-friendly tabs with horizontal scrolling
    
    Args:
        tab_names: List of tab names
        selected_index: Index of initially selected tab
    
    Returns:
        Selected tab name and index
    """
    # Add mobile tab styling
    mobile_tab_css = """
    <style>
    @media (max-width: 768px) {
        .stTabs [data-baseweb="tab-list"] {
            overflow-x: auto;
            overflow-y: hidden;
            white-space: nowrap;
            scrollbar-width: thin;
            -webkit-overflow-scrolling: touch;
            padding: 4px;
        }
        
        .stTabs button[data-baseweb="tab"] {
            flex-shrink: 0;
            white-space: nowrap;
            margin-right: 4px;
            min-width: auto;
            padding: 8px 12px;
            font-size: 14px;
        }
    }
    </style>
    """
    
    st.markdown(mobile_tab_css, unsafe_allow_html=True)
    
    # Create tabs normally - CSS will handle mobile optimization
    tabs = st.tabs(tab_names)
    return tabs

def mobile_info_card(title, value, description=None, status_color=None):
    """
    Create a mobile-optimized information card
    
    Args:
        title: Card title
        value: Main value to display
        description: Optional description text
        status_color: Optional status color for the card
    """
    color_map = {
        'success': '#10b981',
        'warning': '#f59e0b', 
        'danger': '#ef4444',
        'info': '#3b82f6'
    }
    
    bg_color = color_map.get(status_color, '#3b82f6')
    
    card_html = f"""
    <div style="
        background: linear-gradient(135deg, {bg_color}20, {bg_color}10);
        border: 1px solid {bg_color}30;
        border-radius: 12px;
        padding: 1rem;
        margin: 0.5rem 0;
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        min-height: 80px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    ">
        <div style="
            font-size: 0.8rem;
            font-weight: 600;
            color: #6b7280;
            margin-bottom: 0.25rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        ">{title}</div>
        <div style="
            font-size: 1.5rem;
            font-weight: 800;
            color: #1f2937;
            margin-bottom: 0.25rem;
        ">{value}</div>
        {f'<div style="font-size: 0.75rem; color: #6b7280;">{description}</div>' if description else ''}
    </div>
    """
    
    st.markdown(card_html, unsafe_allow_html=True)

def display_health_status(concentration_metrics, total_active, total_exited):
    """Display network health status"""
    st.markdown("## 🏥 Network Health Status")

    # Calculate metrics for glass cards
    gini = concentration_metrics.get('gini_coefficient', 0)
    total_validators = total_active + total_exited
    exit_rate = (total_exited / total_validators * 100) if total_validators > 0 else 0
    total_ops = concentration_metrics.get('total_operators', 0)
    avg_validators = (total_active / total_ops) if total_ops > 0 else 0

    # Determine status indicators using semantic colors
    if gini < 0.5:
        decentralization_status = '<span class="status-success">🟢 Good</span>'
    elif gini < 0.7:
        decentralization_status = '<span class="status-warning">🟡 Moderate</span>'
    else:
        decentralization_status = '<span class="status-danger">🔴 Concentrated</span>'

    if exit_rate < 5:
        exit_status = '<span class="status-success">🟢 Low</span>'
    elif exit_rate < 15:
        exit_status = '<span class="status-warning">🟡 Moderate</span>'
    else:
        exit_status = '<span class="status-danger">🔴 High</span>'

    if avg_validators < 50:
        operator_size_status = '<span class="status-success">🟢 Low</span>'
    elif avg_validators <= 100:
        operator_size_status = '<span class="status-warning">🟡 Moderate</span>'
    else:
        operator_size_status = '<span class="status-danger">🔴 High</span>'

    # Create glass-morphism cards for health status
    st.markdown("""
        <div class="glass-cards-grid">
            <div class="glass-card">
                <div class="glass-card-title">Decentralization</div>
                <div class="glass-card-value">{}</div>
                <div class="glass-card-caption">Gini: {:.3f} (lower is better)</div>
            </div>
            <div class="glass-card">
                <div class="glass-card-title">Exit Rate</div>
                <div class="glass-card-value">{}</div>
                <div class="glass-card-caption">{:.1f}% validators exited</div>
            </div>
            <div class="glass-card">
                <div class="glass-card-title">Operator Size</div>
                <div class="glass-card-value">{}</div>
                <div class="glass-card-caption">{:.1f} avg validators/operator</div>
            </div>
        </div>
    """.format(decentralization_status, gini, exit_status, exit_rate, 
              operator_size_status, avg_validators), unsafe_allow_html=True)

def display_performance_health(operator_performance, operator_validators):
    """Display performance health status"""
    if not operator_performance:
        return

    st.markdown("## 🎯 Performance Health Status")

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

    # Calculate metrics for glass cards
    excellent_pct = (perf_categories['Excellent'] / total_validators * 100) if total_validators > 0 else 0
    poor_pct = (perf_categories['Poor'] / total_validators * 100) if total_validators > 0 else 0
    performances = list(operator_performance.values())
    perf_std = np.std(performances) if performances else 0

    # Determine status indicators using semantic colors
    if avg_performance >= 99:
        perf_status = '<span class="status-success">🟢 Excellent</span>'
    elif avg_performance >= 98:
        perf_status = '<span class="status-warning">🟡 Good</span>'
    else:
        perf_status = '<span class="status-danger">🔴 Needs Attention</span>'

    if perf_std < 1.0:
        consistency_status = '<span class="status-success">🟢 Consistent</span>'
    elif perf_std < 2.5:
        consistency_status = '<span class="status-warning">🟡 Variable</span>'
    else:
        consistency_status = '<span class="status-danger">🔴 Inconsistent</span>'

    # Create glass-morphism cards for performance health
    st.markdown("""
        <div class="glass-cards-grid">
            <div class="glass-card">
                <div class="glass-card-title">Network Performance</div>
                <div class="glass-card-value">{}</div>
                <div class="glass-card-caption">Weighted avg: {:.2f}%</div>
            </div>
            <div class="glass-card">
                <div class="glass-card-title">Excellent Performers</div>
                <div class="glass-card-value">{:.1f}%</div>
                <div class="glass-card-caption">{:,} validators</div>
            </div>
            <div class="glass-card">
                <div class="glass-card-title">Poor Performers</div>
                <div class="glass-card-value">{:.1f}%</div>
                <div class="glass-card-caption">{:,} validators</div>
            </div>
            <div class="glass-card">
                <div class="glass-card-title">Consistency</div>
                <div class="glass-card-value">{}</div>
                <div class="glass-card-caption">Std dev: {:.2f}%</div>
            </div>
        </div>
    """.format(perf_status, avg_performance, excellent_pct, perf_categories['Excellent'],
              poor_pct, perf_categories['Poor'], consistency_status, perf_std), unsafe_allow_html=True)

def display_ens_status(ens_names, operator_validators):
    """Display ENS name resolution status"""
    if not ens_names:
        return

    st.markdown("## 🏷️ ENS Name Resolution Status")

    total_operators = len(operator_validators)
    ens_resolved = len(ens_names)
    coverage_pct = (ens_resolved / total_operators * 100) if total_operators > 0 else 0

    # Calculate metrics for glass cards
    validators_with_ens = sum(operator_validators.get(addr, 0) for addr in ens_names.keys())
    total_validators = sum(operator_validators.values())
    validator_coverage = (validators_with_ens / total_validators * 100) if total_validators > 0 else 0

    # Determine coverage status using semantic colors
    if coverage_pct >= 50:
        coverage_status = '<span class="status-success">🟢 Good</span>'
    elif coverage_pct >= 25:
        coverage_status = '<span class="status-warning">🟡 Moderate</span>'
    else:
        coverage_status = '<span class="status-danger">🔴 Low</span>'

    # Create glass-morphism cards for ENS status
    st.markdown("""
        <div class="glass-cards-grid">
            <div class="glass-card">
                <div class="glass-card-title">ENS Names Found</div>
                <div class="glass-card-value">{:,}</div>
                <div class="glass-card-caption">Resolved operator names</div>
            </div>
            <div class="glass-card">
                <div class="glass-card-title">Total Operators</div>
                <div class="glass-card-value">{:,}</div>
                <div class="glass-card-caption">All tracked operators</div>
            </div>
            <div class="glass-card">
                <div class="glass-card-title">Operator Coverage</div>
                <div class="glass-card-value">{}</div>
                <div class="glass-card-caption">{:.1f}% operators with ENS</div>
            </div>
            <div class="glass-card">
                <div class="glass-card-title">Validator Coverage</div>
                <div class="glass-card-value">{:.1f}%</div>
                <div class="glass-card-caption">{:,} of {:,} validators</div>
            </div>
        </div>
    """.format(ens_resolved, total_operators, coverage_status, coverage_pct,
              validator_coverage, validators_with_ens, total_validators), unsafe_allow_html=True)

def display_network_overview(cache, operator_validators, operator_exited):
    """Display network overview metrics"""
    st.markdown("### 📈 Network Overview")

    validator_indices = cache.get('validator_indices', {})
    pending_pubkeys = cache.get('pending_pubkeys', [])

    total_activated = len(validator_indices) if validator_indices else 0
    total_queued = len(pending_pubkeys) if pending_pubkeys else 0
    total_validators = cache.get('total_validators', 0)
    total_exited = cache.get('total_exited', 0)

    active_validators = {}
    for operator, total_count in operator_validators.items():
        exited_count = operator_exited.get(operator, 0)
        active_count = total_count - exited_count
        if active_count > 0:
            active_validators[operator] = active_count

    # Create glass-morphism cards for network overview
    exit_rate = (total_exited / total_validators * 100) if total_validators > 0 else 0
    
    st.markdown("""
        <div class="glass-cards-grid">
            <div class="glass-card">
                <div class="glass-card-title">Deposited Validators</div>
                <div class="glass-card-value">{:,}</div>
                <div class="glass-card-caption">All validators deposited</div>
            </div>
            <div class="glass-card">
                <div class="glass-card-title">Activated Validators</div>
                <div class="glass-card-value">{:,}</div>
                <div class="glass-card-caption">Participating in consensus</div>
            </div>
            <div class="glass-card">
                <div class="glass-card-title">Validators in Queue</div>
                <div class="glass-card-value">{:,}</div>
                <div class="glass-card-caption">Waiting for activation</div>
            </div>
            <div class="glass-card">
                <div class="glass-card-title">Active Operators</div>
                <div class="glass-card-value">{:,}</div>
                <div class="glass-card-caption">Operating validators</div>
            </div>
            <div class="glass-card">
                <div class="glass-card-title">Exited Validators</div>
                <div class="glass-card-value">{:,}</div>
                <div class="glass-card-caption">No longer active</div>
            </div>
            <div class="glass-card">
                <div class="glass-card-title">Exit Rate</div>
                <div class="glass-card-value">{:.1f}%</div>
                <div class="glass-card-caption">Percentage exited</div>
            </div>
        </div>
    """.format(total_activated + total_queued, total_activated, total_queued, 
              len(active_validators), total_exited, exit_rate), unsafe_allow_html=True)

    # Add activation/queue rate percentage display with glass cards
    if total_activated + total_queued > 0:
        activation_rate = (total_activated / (total_activated + total_queued) * 100)
        queue_rate = (total_queued / (total_activated + total_queued) * 100)

        st.markdown("---")
        st.markdown("""
            <div class="glass-cards-grid">
                <div class="glass-card">
                    <div class="glass-card-title">Activation Rate</div>
                    <div class="glass-card-value">{:.1f}%</div>
                    <div class="glass-card-caption">{:,} of {:,} validators activated</div>
                </div>
                <div class="glass-card">
                    <div class="glass-card-title">Queue Rate</div>
                    <div class="glass-card-value">{:.1f}%</div>
                    <div class="glass-card-caption">{:,} validators waiting for activation</div>
                </div>
            </div>
        """.format(activation_rate, total_activated, total_activated + total_queued,
                  queue_rate, total_queued), unsafe_allow_html=True)

    return total_activated, total_queued, active_validators

def display_cache_info(cache_file, last_block, ens_last_updated):
    """Display cache information"""
    last_update = datetime.fromtimestamp(os.path.getmtime(cache_file))

    ens_update_str = ""
    if ens_last_updated > 0:
        ens_update_time = datetime.fromtimestamp(ens_last_updated)
        ens_update_str = f" • 🏷️ ENS: {ens_update_time.strftime('%H:%M:%S')}"

    st.markdown(f'<p class="text-sm">📊 Block: {last_block:,} • 🕘 {last_update.strftime("%H:%M:%S")}{ens_update_str} • 📁 {cache_file.split("/")[-1]}</p>', unsafe_allow_html=True)

def show_refresh_button():
    """Show refresh button"""
    refresh_col1, refresh_col2 = st.columns([3, 1])
    with refresh_col2:
        if st.button("🔄 Refresh Data", help="Reload validator data", use_container_width=True):
            # Track refresh usage
            try:
                from usage_tracker import usage_tracker
                usage_tracker.track_refresh()
            except Exception:
                pass  # Continue if tracking fails
            
            st.cache_data.clear()
            st.rerun()

def display_health_summary(cache, operator_validators, operator_exited, operator_performance, 
                          ens_names, concentration_metrics, total_active, total_exited, 
                          total_activated, total_queued):
    """Display comprehensive health summary"""
    
    if concentration_metrics:
        gini = concentration_metrics.get('gini_coefficient', 0)
        total_ops = concentration_metrics.get('total_operators', 0)
        avg_validators = (total_active / total_ops) if total_ops > 0 else 0
        
        activation_rate = (total_activated / (total_activated + total_queued) * 100) if (total_activated + total_queued) > 0 else 0
        exit_rate = (total_exited / (total_active + total_exited) * 100) if (total_active + total_exited) > 0 else 0

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

    # Performance health summary
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

    # ENS summary
    if ens_names:
        ens_coverage = len(ens_names) / len(operator_validators) * 100 if operator_validators else 0
        validators_with_ens = sum(operator_validators.get(addr, 0) for addr in ens_names.keys())
        validator_coverage = validators_with_ens / total_active * 100 if total_active > 0 else 0

        st.markdown(f"<div class='health-summary'><strong>ENS / Discord Name Resolution:</strong> {len(ens_names)} names found • {ens_coverage:.1f}% operator coverage • {validator_coverage:.1f}% validator coverage</div>", unsafe_allow_html=True)

    # Add the detailed health metrics expander
    with st.expander("🔍 Detailed Metrics"):
        if concentration_metrics:
            detail_col1, detail_col2, detail_col3, detail_col4 = responsive_columns([1, 1, 1, 1])
            
            with detail_col1:
                st.markdown("**Decentralization Metrics**")
                st.write(f"• Gini Coefficient: {gini:.3f}")
                st.write(f"• Top 1 Operator: {concentration_metrics['top_1_concentration']:.1f}%")
                st.write(f"• Top 5 Operators: {concentration_metrics['top_5_concentration']:.1f}%")
                st.write(f"• Average Validators/Operator: {avg_validators:.1f}")

            with detail_col2:
                if operator_performance:
                    st.markdown("**Performance Metrics**")
                    # Calculate the performance metrics here
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
                    
                    st.write(f"• Network Average: {avg_performance:.2f}%")
                    st.write(f"• Excellent Performers: {excellent_pct:.1f}%")
                    st.write(f"• Poor Performers: {poor_pct:.1f}%")
                    performances = list(operator_performance.values())
                    st.write(f"• Performance Std Dev: {np.std(performances):.2f}%")

            with detail_col3:
                if ens_names:
                    st.markdown("**ENS Resolution Metrics**")
                    ens_coverage = len(ens_names) / len(operator_validators) * 100 if operator_validators else 0
                    validators_with_ens = sum(operator_validators.get(addr, 0) for addr in ens_names.keys())
                    validator_coverage = validators_with_ens / total_active * 100 if total_active > 0 else 0
                    
                    st.write(f"• Total ENS Names: {len(ens_names)}")
                    st.write(f"• Operator Coverage: {ens_coverage:.1f}%")
                    st.write(f"• Validator Coverage: {validator_coverage:.1f}%")
                    if cache.get('ens_last_updated', 0) > 0:
                        ens_last_updated = cache.get('ens_last_updated', 0)
                        hours_ago = (datetime.now().timestamp() - ens_last_updated) / 3600
                        st.write(f"• Last Updated: {hours_ago:.1f}h ago")

            with detail_col4:
                st.markdown("**Activation Metrics**")
                activation_rate = (total_activated / (total_activated + total_queued) * 100) if (total_activated + total_queued) > 0 else 0
                st.write(f"• Activation Rate: {activation_rate:.1f}%")
                st.write(f"• Activated Count: {total_activated:,}")
                st.write(f"• Queue Count: {total_queued:,}")
