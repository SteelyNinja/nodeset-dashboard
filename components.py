import streamlit as st
import numpy as np
import os
from datetime import datetime
from utils import get_performance_category

def display_health_status(concentration_metrics, total_active, total_exited):
    """Display network health status"""
    st.subheader("🏥 Network Health Status")

    # Calculate metrics for glass cards
    gini = concentration_metrics.get('gini_coefficient', 0)
    total_validators = total_active + total_exited
    exit_rate = (total_exited / total_validators * 100) if total_validators > 0 else 0
    total_ops = concentration_metrics.get('total_operators', 0)
    avg_validators = (total_active / total_ops) if total_ops > 0 else 0

    # Determine status indicators
    if gini < 0.5:
        decentralization_status = "🟢 Good"
    elif gini < 0.7:
        decentralization_status = "🟡 Moderate"
    else:
        decentralization_status = "🔴 Concentrated"

    if exit_rate < 5:
        exit_status = "🟢 Low"
    elif exit_rate < 15:
        exit_status = "🟡 Moderate"
    else:
        exit_status = "🔴 High"

    if avg_validators < 50:
        operator_size_status = "🟢 Low"
    elif avg_validators <= 100:
        operator_size_status = "🟡 Moderate"
    else:
        operator_size_status = "🔴 High"

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

    # Calculate metrics for glass cards
    excellent_pct = (perf_categories['Excellent'] / total_validators * 100) if total_validators > 0 else 0
    poor_pct = (perf_categories['Poor'] / total_validators * 100) if total_validators > 0 else 0
    performances = list(operator_performance.values())
    perf_std = np.std(performances) if performances else 0

    # Determine status indicators
    if avg_performance >= 99:
        perf_status = "🟢 Excellent"
    elif avg_performance >= 98:
        perf_status = "🟡 Good"
    else:
        perf_status = "🔴 Needs Attention"

    if perf_std < 1.0:
        consistency_status = "🟢 Consistent"
    elif perf_std < 2.5:
        consistency_status = "🟡 Variable"
    else:
        consistency_status = "🔴 Inconsistent"

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

    st.subheader("🏷️ ENS Name Resolution Status")

    total_operators = len(operator_validators)
    ens_resolved = len(ens_names)
    coverage_pct = (ens_resolved / total_operators * 100) if total_operators > 0 else 0

    # Calculate metrics for glass cards
    validators_with_ens = sum(operator_validators.get(addr, 0) for addr in ens_names.keys())
    total_validators = sum(operator_validators.values())
    validator_coverage = (validators_with_ens / total_validators * 100) if total_validators > 0 else 0

    # Determine coverage status
    if coverage_pct >= 50:
        coverage_status = "🟢 Good"
    elif coverage_pct >= 25:
        coverage_status = "🟡 Moderate"
    else:
        coverage_status = "🔴 Low"

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

    st.caption(f"📊 Block: {last_block:,} • 🕘 {last_update.strftime('%H:%M:%S')}{ens_update_str} • 📁 {cache_file.split('/')[-1]}")

def show_refresh_button():
    """Show refresh button"""
    refresh_col1, refresh_col2 = st.columns([3, 1])
    with refresh_col2:
        if st.button("🔄 Refresh Data", help="Reload validator data", use_container_width=True):
            st.cache_data.clear()
            st.rerun()
