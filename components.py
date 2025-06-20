import streamlit as st
import numpy as np
import os
from datetime import datetime
from utils import get_performance_category

def display_health_status(concentration_metrics, total_active, total_exited):
    """Display network health status"""
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
    """Display ENS name resolution status"""
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

    # Add activation/queue rate percentage display with color coding
    if total_activated + total_queued > 0:
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
