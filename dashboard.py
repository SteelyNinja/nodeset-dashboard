import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime
from collections import Counter

# Import our modules
from config import apply_page_config, apply_custom_css
from data_loader import load_validator_data, load_proposals_data, load_mev_analysis_data, load_sync_committee_data, load_missed_proposals_data, load_exit_data, display_logo
from analysis import calculate_concentration_metrics, create_performance_analysis, analyze_gas_limits_by_operator, analyze_client_diversity
from charts import (create_performance_charts, create_concentration_pie, create_distribution_histogram, 
                   create_concentration_curve, create_gas_limit_distribution_chart, create_operator_gas_strategy_chart,
                   create_client_diversity_pie_charts, create_client_combination_bar_chart)
from tables import (create_top_operators_table, create_performance_table, create_largest_proposals_table,
                   create_latest_proposals_table, create_proposals_operators_table, create_mev_relay_breakdown_table,
                   create_missed_proposals_table, create_sync_committee_operators_table, 
                   create_sync_committee_periods_table, create_sync_committee_detailed_table)
from components import (display_health_status, display_performance_health, display_ens_status,
                       display_network_overview, display_cache_info, show_refresh_button,
                       responsive_columns, display_health_summary)
from utils import format_operator_display_plain, get_performance_category, get_memory_usage



def run_dashboard():
    """Main dashboard function"""
    # Apply configuration and styling
    apply_page_config()
    apply_custom_css()
    
    # Detect mobile device and apply mobile-specific optimizations
    from config import detect_mobile_device
    detect_mobile_device()
    
    # Display logo and header
    display_logo()
    
    # Option 2: Compact Info Bar (TEMPORARY PREVIEW)
    st.markdown("""
        <style>
        .info-bar {
            background: linear-gradient(90deg, rgba(59, 130, 246, 0.1), rgba(147, 51, 234, 0.1));
            backdrop-filter: blur(10px);
            border: 1px solid rgba(0, 0, 0, 0.1);
            border-radius: 16px;
            padding: 24px 32px;
            margin: 1rem 0;
            display: flex;
            align-items: center;
            justify-content: space-between;
            flex-wrap: wrap;
            gap: 2rem;
        }
        
        .info-bar-left {
            display: flex;
            align-items: center;
            gap: 16px;
            color: #1f2937;
            flex: 1;
            min-width: 350px;
        }
        
        .info-bar-right {
            display: flex;
            align-items: center;
            gap: 16px;
            color: #374151;
            border-left: 1px solid rgba(0, 0, 0, 0.15);
            padding-left: 2rem;
        }
        
        /* Dark mode styles */
        @media (prefers-color-scheme: dark) {
            .info-bar {
                background: linear-gradient(90deg, rgba(59, 130, 246, 0.15), rgba(147, 51, 234, 0.15));
                border: 1px solid rgba(255, 255, 255, 0.1);
            }
            
            .info-bar-left {
                color: rgba(255, 255, 255, 0.95);
            }
            
            .info-bar-right {
                color: rgba(255, 255, 255, 0.8);
                border-left: 1px solid rgba(255, 255, 255, 0.2);
            }
        }
        
        /* Streamlit dark theme support */
        [data-theme="dark"] .info-bar,
        .stApp[data-theme="dark"] .info-bar {
            background: linear-gradient(90deg, rgba(59, 130, 246, 0.15), rgba(147, 51, 234, 0.15)) !important;
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
        }
        
        [data-theme="dark"] .info-bar-left,
        .stApp[data-theme="dark"] .info-bar-left {
            color: rgba(255, 255, 255, 0.95) !important;
        }
        
        [data-theme="dark"] .info-bar-right,
        .stApp[data-theme="dark"] .info-bar-right {
            color: rgba(255, 255, 255, 0.8) !important;
            border-left: 1px solid rgba(255, 255, 255, 0.2) !important;
        }
        </style>
        
        <div class="info-bar">
            <div class="info-bar-left">
                <span style="color: #3b82f6; font-size: 22px;">📊</span>
                <div style="font-size: 1.1rem; line-height: 1.5;">
                    <strong>Monitoring and analysis</strong> of NodeSet protocol validators on Stakewise<br>
                    <span style="opacity: 0.8;">Data cache updated every 15 minutes • Hit "Refresh Data" to reload • Latest cache time is reported in UTC time</span>
                </div>
            </div>
            <div class="info-bar-right">
                <span style="color: #f59e0b; font-size: 20px;">⚠️</span>
                <div style="font-size: 1rem; line-height: 1.4;">
                    <strong>Disclaimer</strong><br>
                    <span style="opacity: 0.8;">This site is independently maintained and is not affiliated with or managed by Nodeset.</span>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # Show refresh button
    show_refresh_button()

    # Load data
    cache_data = load_validator_data()
    if cache_data[0] is None:
        st.error("⚠️ **Cache file not found!**")
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

    # Extract data from cache
    operator_validators = cache.get('operator_validators', {})
    operator_exited = cache.get('exited_validators', {})
    operator_performance = cache.get('operator_performance', {})
    ens_names = cache.get('ens_names', {})
    ens_last_updated = cache.get('ens_last_updated', 0)
    last_block = cache.get('last_block', 0)

    # Calculate active validators
    active_validators = {}
    for operator, total_count in operator_validators.items():
        exited_count = operator_exited.get(operator, 0)
        active_count = total_count - exited_count
        if active_count > 0:
            active_validators[operator] = active_count

    total_active = sum(active_validators.values())
    total_exited = sum(operator_exited.values())

    # Display cache info
    display_cache_info(cache_file, last_block, ens_last_updated)

    # Display network overview
    total_activated, total_queued, active_validators = display_network_overview(cache, operator_validators, operator_exited)

    # Calculate metrics and display health status
    concentration_metrics = calculate_concentration_metrics(active_validators)
    display_health_summary(cache, operator_validators, operator_exited, operator_performance, 
                          ens_names, concentration_metrics, total_active, total_exited, 
                          total_activated, total_queued)

    # Create tabs
    create_dashboard_tabs(cache, operator_validators, operator_exited, operator_performance, 
                         ens_names, active_validators, concentration_metrics)

    # Footer
    st.markdown("---")
    ens_info = f" | ENS: {len(ens_names)} names resolved" if ens_names else ""
    st.markdown(f"*Dashboard last refreshed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{ens_info}*")


def create_dashboard_tabs(cache, operator_validators, operator_exited, operator_performance, 
                         ens_names, active_validators, concentration_metrics):
    """Create the main dashboard tabs"""
    
    st.markdown("---")

    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9, tab10, tab11 = st.tabs([
        "📈 Distribution",
        "🎯 Concentration", 
        "🏆 Top Operators",
        "⚡ Performance",
        "🤲 Proposals",
        "📡 Sync Committee",
        "🚪 Exit Analysis",
        "💰 Costs",
        "🔧 Client Diversity",
        "🔥 Pump the Gas!",
        "📋 Raw Data"
    ])

    with tab1:
        create_distribution_tab(active_validators)

    with tab2:
        create_concentration_tab(active_validators, concentration_metrics)

    with tab3:
        create_top_operators_tab(operator_validators, operator_exited, ens_names)

    with tab4:
        create_performance_tab(operator_performance, operator_validators, operator_exited, ens_names)

    with tab5:
        create_proposals_tab(ens_names)

    with tab6:
        create_sync_committee_tab(ens_names)

    with tab7:
        create_exit_analysis_tab(operator_validators, operator_exited, ens_names)

    with tab8:
        create_costs_tab(cache, operator_validators, operator_exited, ens_names)

    with tab9:
        create_client_diversity_tab(ens_names)

    with tab10:
        create_gas_analysis_tab(ens_names)

    with tab11:
        create_raw_data_tab(cache, operator_validators, operator_exited, ens_names)

def create_client_diversity_tab(ens_names):
    """Create the client diversity analysis tab"""
    st.subheader("🔧 Client Diversity Analysis")
    st.markdown("*Analysis of execution client, consensus client, and setup configurations from proposal graffiti data*")
    
    # Load proposals data
    proposals_cache = load_proposals_data()
    if proposals_cache[0] is None:
        st.error("⚠️ **Proposals data file not found!**")
        st.markdown("""
        **Setup Instructions:**
        1. Ensure `proposals.json` exists in your directory
        2. Place the file alongside this dashboard script
        
        **Expected file locations:**
        - `./proposals.json`
        - `./data/proposals.json`
        """)
        return
    
    proposals_data, proposals_file = proposals_cache
    
    # Load cache data for validator-operator mapping
    cache_data = load_validator_data()
    if cache_data[0] is None:
        st.error("⚠️ **Cache data not available for operator mapping!**")
        return
    
    cache, cache_file = cache_data
    
    # Analyze client diversity
    client_diversity_data = analyze_client_diversity(proposals_data, cache, ens_names)
    
    if not client_diversity_data:
        st.info("📊 No client diversity data available. This requires operators to have made proposals with valid graffiti data.")
        return
    
    # Display summary statistics
    total_operators = client_diversity_data['total_operators']
    operators_with_proposals = client_diversity_data['operators_with_proposals']
    
    # Calculate coverage percentage
    coverage_pct = (operators_with_proposals / total_operators) * 100 if total_operators > 0 else 0
    
    # Create glass-morphism cards for client diversity summary
    st.markdown("""
        <div class="glass-cards-grid">
            <div class="glass-card">
                <div class="glass-card-title">Total Operators</div>
                <div class="glass-card-value">{:,}</div>
                <div class="glass-card-caption">All tracked operators</div>
            </div>
            <div class="glass-card">
                <div class="glass-card-title">Operators with Proposals</div>
                <div class="glass-card-value">{:,}</div>
                <div class="glass-card-caption">Operators submitting proposals</div>
            </div>
            <div class="glass-card">
                <div class="glass-card-title">Graffiti Coverage</div>
                <div class="glass-card-value">{:.1f}%</div>
                <div class="glass-card-caption">Operators with graffiti data</div>
            </div>
        </div>
    """.format(total_operators, operators_with_proposals, coverage_pct), unsafe_allow_html=True)
    
    # Context text
    st.markdown(f"**📊 {operators_with_proposals} of {total_operators} operators have active proposals with graffiti data**")
    st.markdown("*Showing latest proposal configuration for each operator*")
    
    st.markdown("---")
    
    # Create the three pie charts
    fig_execution, fig_consensus, fig_setup = create_client_diversity_pie_charts(client_diversity_data)
    
    if fig_execution and fig_consensus and fig_setup:
        col1, col2, col3 = responsive_columns(3)
        
        with col1:
            st.plotly_chart(fig_execution, use_container_width=True)
        
        with col2:
            st.plotly_chart(fig_consensus, use_container_width=True)
        
        with col3:
            st.plotly_chart(fig_setup, use_container_width=True)
    
    st.markdown("---")
    
    # Create the combination bar chart
    fig_combinations = create_client_combination_bar_chart(client_diversity_data)
    if fig_combinations:
        st.plotly_chart(fig_combinations, use_container_width=True)
    
    # Download functionality
    st.markdown("---")
    col1, col2 = st.columns([3, 1])
    with col2:
        # Prepare export data
        export_data = []
        operator_details = client_diversity_data.get('operator_details', {})
        
        for operator_addr, data in operator_details.items():
            ens_name = ens_names.get(operator_addr, "")
            
            # Get client names
            exec_names = {'G': 'Geth', 'N': 'Nethermind', 'B': 'Besu', 'R': 'Reth'}
            cons_names = {'L': 'Lighthouse', 'S': 'Lodestar', 'N': 'Nimbus', 'P': 'Prysm', 'T': 'Teku'}
            setup_names = {'L': 'Local', 'X': 'External'}
            
            export_data.append({
                'operator_address': operator_addr,
                'ens_name': ens_name,
                'execution_client': exec_names.get(data['execution_client'], data['execution_client']),
                'consensus_client': cons_names.get(data['consensus_client'], data['consensus_client']),
                'setup_type': setup_names.get(data['setup_type'], data['setup_type']),
                'graffiti_text': data['graffiti_text'],
                'timestamp': data['timestamp']
            })
        
        if export_data:
            export_df = pd.DataFrame(export_data)
            export_csv = export_df.to_csv(index=False)
            
            st.download_button(
                label="📥 Download Client Diversity Data",
                data=export_csv,
                file_name=f"client_diversity_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                use_container_width=True
            )

def create_distribution_tab(active_validators):
    """Create the distribution analysis tab"""
    if active_validators:
        fig_hist = create_distribution_histogram(active_validators)
        st.plotly_chart(fig_hist, use_container_width=True)

        st.subheader("📊 Key Insights")
        
        validator_counts = list(active_validators.values())
        if validator_counts:
            max_validators = max(validator_counts)
            total_validators_dist = sum(validator_counts)
            total_operators = len(validator_counts)
            avg_validators_dist = np.mean(validator_counts)
            median_validators = np.median(validator_counts)
            min_validators = min(validator_counts)

            sorted_validators = sorted(validator_counts, reverse=True)
            top_3_validators = sum(sorted_validators[:3]) if len(sorted_validators) >= 3 else sum(sorted_validators)
            top_3_percentage = (top_3_validators / total_validators_dist * 100) if total_validators_dist > 0 else 0
            top_5_validators = sum(sorted_validators[:5]) if len(sorted_validators) >= 5 else sum(sorted_validators)
            top_5_percentage = (top_5_validators / total_validators_dist * 100) if total_validators_dist > 0 else 0
            top_10_validators = sum(sorted_validators[:10]) if len(sorted_validators) >= 10 else sum(sorted_validators)
            top_10_percentage = (top_10_validators / total_validators_dist * 100) if total_validators_dist > 0 else 0

            below_avg_count = sum(1 for count in validator_counts if count < avg_validators_dist)
            below_avg_percentage = (below_avg_count / total_operators * 100) if total_operators > 0 else 0

            cap_level = max_validators
            validators_to_cap = sum(max(0, cap_level - count) for count in validator_counts)
            eth_to_cap = validators_to_cap * 32
            operators_at_cap = sum(1 for count in validator_counts if count == cap_level)
            operators_at_cap_percentage = (operators_at_cap / total_operators * 100) if total_operators > 0 else 0
            operators_near_cap = sum(1 for count in validator_counts if count >= cap_level * 0.75)
            operators_near_cap_percentage = (operators_near_cap / total_operators * 100) if total_operators > 0 else 0

            # Create glass-morphism cards for key insights
            st.markdown("""
                <div class="glass-cards-grid">
                    <div class="glass-card">
                        <div class="glass-card-title">Largest Operator</div>
                        <div class="glass-card-value">{:,}</div>
                        <div class="glass-card-caption">validators</div>
                    </div>
                    <div class="glass-card">
                        <div class="glass-card-title">Average per Operator</div>
                        <div class="glass-card-value">{:.1f}</div>
                        <div class="glass-card-caption">validators</div>
                    </div>
                    <div class="glass-card">
                        <div class="glass-card-title">Median per Operator</div>
                        <div class="glass-card-value">{:.1f}</div>
                        <div class="glass-card-caption">validators</div>
                    </div>
                    <div class="glass-card">
                        <div class="glass-card-title">Smallest Operator</div>
                        <div class="glass-card-value">{:,}</div>
                        <div class="glass-card-caption">validators</div>
                    </div>
                </div>
            """.format(max_validators, avg_validators_dist, median_validators, min_validators), unsafe_allow_html=True)

            st.markdown("""
                <div class="glass-cards-grid">
                    <div class="glass-card">
                        <div class="glass-card-title">Top 3 Operators Control</div>
                        <div class="glass-card-value">{:.1f}%</div>
                        <div class="glass-card-caption">{:,} of {:,} validators</div>
                    </div>
                    <div class="glass-card">
                        <div class="glass-card-title">Top 5 Operators Control</div>
                        <div class="glass-card-value">{:.1f}%</div>
                        <div class="glass-card-caption">{:,} of {:,} validators</div>
                    </div>
                    <div class="glass-card">
                        <div class="glass-card-title">Top 10 Operators Control</div>
                        <div class="glass-card-value">{:.1f}%</div>
                        <div class="glass-card-caption">{:,} of {:,} validators</div>
                    </div>
                    <div class="glass-card">
                        <div class="glass-card-title">Below Average Operators</div>
                        <div class="glass-card-value">{:.1f}%</div>
                        <div class="glass-card-caption">{:,} operators</div>
                    </div>
                </div>
            """.format(top_3_percentage, top_3_validators, total_validators_dist,
                      top_5_percentage, top_5_validators, total_validators_dist,
                      top_10_percentage, top_10_validators, total_validators_dist,
                      below_avg_percentage, below_avg_count), unsafe_allow_html=True)

            st.markdown("""
                <div class="glass-cards-grid">
                    <div class="glass-card">
                        <div class="glass-card-title">Validators to Cap</div>
                        <div class="glass-card-value">{:,}</div>
                        <div class="glass-card-caption">Total needed to reach cap</div>
                    </div>
                    <div class="glass-card">
                        <div class="glass-card-title">ETH to Cap</div>
                        <div class="glass-card-value">{:,}</div>
                        <div class="glass-card-caption">@ 32 ETH per validator</div>
                    </div>
                    <div class="glass-card">
                        <div class="glass-card-title">Operators at Cap</div>
                        <div class="glass-card-value">{:.1f}%</div>
                        <div class="glass-card-caption">{:,} operators</div>
                    </div>
                    <div class="glass-card">
                        <div class="glass-card-title">Operators at 75%+ of Cap</div>
                        <div class="glass-card-value">{:.1f}%</div>
                        <div class="glass-card-caption">{:,} ops (≥75% of cap)</div>
                    </div>
                </div>
            """.format(validators_to_cap, eth_to_cap, 
                      operators_at_cap_percentage, operators_at_cap,
                      operators_near_cap_percentage, operators_near_cap), unsafe_allow_html=True)
    else:
        st.info("No active validator data available for insights.")

def create_concentration_tab(active_validators, concentration_metrics):
    """Create the concentration analysis tab"""
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
    else:
        st.info("No concentration data available.")

def create_top_operators_tab(operator_validators, operator_exited, ens_names):
    """Create the top operators tab"""
    st.subheader("🏆 Top Operators by Active Validators")
    
    df_operators = create_top_operators_table(operator_validators, operator_exited, ens_names)
    
    if not df_operators.empty:
        display_df = df_operators.copy()
        display_df['Active'] = display_df['Active'].astype(str)
        display_df['Total'] = display_df['Total'].astype(str)
        display_df['Exited'] = display_df['Exited'].astype(str)

        st.dataframe(display_df, use_container_width=True, hide_index=True)
        
        csv = df_operators.to_csv(index=False)
        st.download_button(
            label="📥 Download CSV",
            data=csv,
            file_name=f"nodeset_operators_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
    else:
        st.info("No operator data available.")

def create_performance_tab(operator_performance, operator_validators, operator_exited, ens_names):
    """Create the performance analysis tab"""
    st.subheader("⚡ Operator Performance Analysis (24 hours)")
    st.info("ℹ️ This is last 24 hour data only - note refreshes every 1 hour")

    if operator_performance:
        fig_scatter, fig_hist = create_performance_charts(operator_performance, operator_validators, ens_names)
        
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
                        "ENS / Discord Name": st.column_config.TextColumn("ENS / Discord Name", width="small"),
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

def create_proposals_tab(ens_names):
    """Create the proposals analysis tab"""
    st.subheader("🤲 Proposal Analysis")
    
    proposals_cache = load_proposals_data()
    if proposals_cache[0] is None:
        st.error("⚠️ **Proposals data file not found!**")
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
        
        # Calculate metrics for glass cards
        total_proposals = metadata.get('total_proposals', 1)
        total_value = metadata.get('total_value_eth', 0)
        avg_value = total_value / max(total_proposals, 1)
        
        # Create glass-morphism cards for proposals summary
        st.markdown("""
            <div class="glass-cards-grid">
                <div class="glass-card">
                    <div class="glass-card-title">Total Proposals</div>
                    <div class="glass-card-value">{:,}</div>
                    <div class="glass-card-caption">Block proposals tracked</div>
                </div>
                <div class="glass-card">
                    <div class="glass-card-title">Total ETH Value</div>
                    <div class="glass-card-value">{:.3f}</div>
                    <div class="glass-card-caption">ETH total value</div>
                </div>
                <div class="glass-card">
                    <div class="glass-card-title">Operators with Proposals</div>
                    <div class="glass-card-value">{:,}</div>
                    <div class="glass-card-caption">Active proposing operators</div>
                </div>
                <div class="glass-card">
                    <div class="glass-card-title">Avg Value/Proposal</div>
                    <div class="glass-card-value">{:.4f}</div>
                    <div class="glass-card-caption">ETH average per proposal</div>
                </div>
            </div>
        """.format(metadata.get('total_proposals', 0), total_value,
                  metadata.get('operators_tracked', 0), avg_value), unsafe_allow_html=True)
        
        if metadata.get('last_updated'):
            st.caption(f"📊 Proposals: {metadata['last_updated']} • 📄 {proposals_file.split('/')[-1]}")
        
        # Add Largest Proposals Table
        st.subheader("💎 Largest Proposals by Value")
        st.caption("Showing the 5 highest value proposals across all operators")
        
        largest_proposals_df = create_largest_proposals_table(proposals_data, ens_names, limit=5)
        
        if not largest_proposals_df.empty:
            display_largest_df = largest_proposals_df.drop(['Operator Address'], axis=1)
            st.dataframe(
                display_largest_df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Date": st.column_config.TextColumn("Date", width="medium"),
                    "Operator": st.column_config.TextColumn("Operator", width="medium"),
                    "Validator Pubkey": st.column_config.TextColumn("Validator Pubkey", width="large"),
                    "ETH Value": st.column_config.TextColumn("ETH Value", width="small"),
                    "Execution Rewards": st.column_config.TextColumn("Exec Rewards", width="small"),
                    "Consensus Rewards": st.column_config.TextColumn("Cons Rewards", width="small"),
                    "MEV Rewards": st.column_config.TextColumn("MEV Rewards", width="small"),
                    "MEV Relay": st.column_config.TextColumn("MEV Relay", width="medium"),
                    "Slot": st.column_config.TextColumn("Slot", width="small"),
                    "Gas Used": st.column_config.TextColumn("Gas Used", width="small"),
                    "Gas Utilization": st.column_config.TextColumn("Gas %", width="small"),
                    "TX Count": st.column_config.TextColumn("TXs", width="small")
                }
            )
            
            largest_csv = largest_proposals_df.to_csv(index=False)
            st.download_button(
                label="📥 Download Largest Proposals",
                data=largest_csv,
                file_name=f"largest_proposals_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
        else:
            st.info("No proposals available.")
        
        st.markdown("---")
        
        # Add Latest Proposals Table
        st.subheader("🕘 Latest Proposals")
        st.caption("Showing the 5 most recent proposals across all operators")
        
        latest_proposals_df = create_latest_proposals_table(proposals_data, ens_names, limit=5)
        
        if not latest_proposals_df.empty:
            display_latest_df = latest_proposals_df.drop(['Operator Address'], axis=1)
            st.dataframe(
                display_latest_df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Date": st.column_config.TextColumn("Date", width="medium"),
                    "Operator": st.column_config.TextColumn("Operator", width="medium"),
                    "Validator Pubkey": st.column_config.TextColumn("Validator Pubkey", width="large"),
                    "ETH Value": st.column_config.TextColumn("ETH Value", width="small"),
                    "Execution Rewards": st.column_config.TextColumn("Exec Rewards", width="small"),
                    "Consensus Rewards": st.column_config.TextColumn("Cons Rewards", width="small"),
                    "MEV Rewards": st.column_config.TextColumn("MEV Rewards", width="small"),
                    "MEV Relay": st.column_config.TextColumn("MEV Relay", width="medium"),
                    "Slot": st.column_config.TextColumn("Slot", width="small"),
                    "Gas Used": st.column_config.TextColumn("Gas Used", width="small"),
                    "Gas Utilization": st.column_config.TextColumn("Gas %", width="small"),
                    "TX Count": st.column_config.TextColumn("TXs", width="small")
                }
            )
            
            latest_csv = latest_proposals_df.to_csv(index=False)
            st.download_button(
                label="📥 Download Latest Proposals",
                data=latest_csv,
                file_name=f"latest_proposals_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
        else:
            st.info("No recent proposals available.")
        
        st.markdown("---")
        
        # Add MEV Relay Breakdown Table
        st.subheader("🔗 MEV Relay Usage Breakdown")
        st.caption("Breakdown of MEV relays used in proposals, sorted by usage count")
        
        mev_relay_df = create_mev_relay_breakdown_table(proposals_data)
        
        if not mev_relay_df.empty:
            st.dataframe(
                mev_relay_df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "MEV Relay": st.column_config.TextColumn("MEV Relay", width="large"),
                    "Proposals": st.column_config.TextColumn("Proposals", width="small"),
                    "Percentage": st.column_config.TextColumn("Percentage", width="small")
                }
            )
            
            relay_csv = mev_relay_df.to_csv(index=False)
            st.download_button(
                label="📥 Download MEV Relay Data",
                data=relay_csv,
                file_name=f"mev_relay_breakdown_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
        else:
            st.info("No MEV relay data available.")
        
        st.markdown("---")
        
        # Add Missed Proposals Section
        st.subheader("❌ Missed Proposals Analysis")
        
        # Load missed proposals data
        missed_cache = load_missed_proposals_data()
        cache_data = load_validator_data()
        
        if missed_cache[0] is None:
            st.info("📊 No missed proposals data available.")
            st.markdown("""
            **To enable missed proposals tracking:**
            1. Ensure `missed_proposals_cache.json` exists in your directory
            2. This file should be generated by your proposals tracking system
            
            **Expected file locations:**
            - `./missed_proposals_cache.json`
            - `./data/missed_proposals_cache.json`
            """)
        else:
            missed_data, missed_file = missed_cache
            cache, cache_file = cache_data if cache_data[0] is not None else (None, None)
            
            # Create missed proposals table and get summary stats
            missed_df, summary_stats = create_missed_proposals_table(missed_data, cache, proposals_data, ens_names)
            
            if not missed_df.empty and summary_stats:
                # Calculate successful proposals from proposals data
                total_successful = metadata.get('total_proposals', 0)
                total_missed = summary_stats['total_missed']
                total_all_proposals = total_successful + total_missed
                missed_percentage = (total_missed / total_all_proposals * 100) if total_all_proposals > 0 else 0
                
                # Display summary statistics in header
                st.markdown(f"""
                **Summary:** {total_successful:,} successful proposals • {total_missed:,} missed proposals • {missed_percentage:.1f}% missed rate
                """)
                
                st.caption(f"Showing {len(missed_df)} missed proposal records • 📄 {missed_file.split('/')[-1]}")
                
                # Display missed proposals table
                display_missed_df = missed_df.drop(['Operator Address'], axis=1)
                st.dataframe(
                    display_missed_df,
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "Date & Time": st.column_config.TextColumn("Date & Time", width="medium"),
                        "Slot Number": st.column_config.TextColumn("Slot Number", width="small"),
                        "Operator Name": st.column_config.TextColumn("Operator Name", width="medium"),
                        "Total Missed": st.column_config.TextColumn("Total Missed", width="small"),
                        "Total Successful": st.column_config.TextColumn("Total Successful", width="small"),
                        "Missed %": st.column_config.TextColumn("Missed %", width="small")
                    }
                )
                
                missed_csv = missed_df.to_csv(index=False)
                st.download_button(
                    label="📥 Download Missed Proposals",
                    data=missed_csv,
                    file_name=f"missed_proposals_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
            else:
                st.info("🎉 No missed proposals found!")
        
        st.markdown("---")
        
        # Add detailed operator proposals section (existing code continues...)
        proposals_operators = create_proposals_operators_table(proposals_data, ens_names)
        
        if proposals_operators:
            st.subheader("🏆Operators by Proposal Count")
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
            
            # Display detailed operator information
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
                    
                    # Proposal history table
                    st.markdown("**📋 Proposal History**")
                    proposals_list = op_data['proposals']
                    
                    if proposals_list:
                        df = pd.DataFrame(proposals_list)
                        
                        # Use the formatted MEV relay information
                        display_df = df[['date', 'slot', 'total_value_eth', 'gas_used', 'gas_utilization', 'tx_count', 'base_fee', 'mev_relay', 'validator_pubkey']].copy()
                        display_df.columns = ['Date', 'Slot', 'ETH Value', 'Gas Used', 'Gas %', 'TXs', 'Base Fee', 'MEV Relay', 'Validator Pubkey']
                        
                        display_df['ETH Value'] = display_df['ETH Value'].apply(lambda x: f"{x:.4f}")
                        display_df['Gas Used'] = display_df['Gas Used'].astype(str)
                        display_df['Gas %'] = display_df['Gas %'].apply(lambda x: f"{x:.1f}%")
                        display_df['TXs'] = display_df['TXs'].astype(str)
                        display_df['Base Fee'] = display_df['Base Fee'].astype(str)
                        display_df['Slot'] = display_df['Slot'].astype(str)
                        
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
                                "MEV Relay": st.column_config.TextColumn("MEV Relay", width="medium"),
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
            
            # Export all data
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

def create_sync_committee_tab(ens_names):
    """Create the sync committee analysis tab"""
    st.subheader("📡 Sync Committee Participation Analysis")
    st.markdown("*Analysis of validator participation in Ethereum sync committees*")
    
    sync_cache = load_sync_committee_data()
    if sync_cache[0] is None:
        st.error("⚠️ **Sync committee data file not found!**")
        st.markdown("""
        **Setup Instructions:**
        1. Ensure `sync_committee_participation.json` exists in your directory
        2. Place the file alongside this dashboard script
        
        **Expected file locations:**
        - `./sync_committee_participation.json`
        - `./data/sync_committee_participation.json`
        """)
    else:
        sync_data, sync_file = sync_cache
        metadata = sync_data.get('metadata', {})
        
        # Summary metrics
        # Calculate success rate
        success_rate = (metadata.get('total_successful_attestations', 0) / max(metadata.get('total_attestations_tracked', 1), 1) * 100)
        
        # Create glass-morphism cards for sync committee summary
        st.markdown("""
            <div class="glass-cards-grid">
                <div class="glass-card">
                    <div class="glass-card-title">Overall Participation</div>
                    <div class="glass-card-value">{:.2f}%</div>
                    <div class="glass-card-caption">Average participation rate</div>
                </div>
                <div class="glass-card">
                    <div class="glass-card-title">Total Periods Tracked</div>
                    <div class="glass-card-value">{:,}</div>
                    <div class="glass-card-caption">Sync committee periods</div>
                </div>
                <div class="glass-card">
                    <div class="glass-card-title">Total Attestations</div>
                    <div class="glass-card-value">{:,}</div>
                    <div class="glass-card-caption">Sync committee attestations</div>
                </div>
                <div class="glass-card">
                    <div class="glass-card-title">Success Rate</div>
                    <div class="glass-card-value">{:.2f}%</div>
                    <div class="glass-card-caption">Successful attestations</div>
                </div>
            </div>
        """.format(metadata.get('overall_participation_rate', 0), metadata.get('total_periods_tracked', 0),
                  metadata.get('total_attestations_tracked', 0), success_rate), unsafe_allow_html=True)
        
        if metadata.get('last_updated'):
            st.caption(f"📊 Last Updated: {metadata['last_updated']} • 📄 {sync_file.split('/')[-1]}")
        
        st.markdown("---")
        
        # Operator Rankings
        st.subheader("🏆 Operator Participation Rankings")
        st.caption("Operators ranked by sync committee participation rate")
        
        operators_df = create_sync_committee_operators_table(sync_data, ens_names)
        
        if not operators_df.empty:
            display_operators_df = operators_df.drop(['Participation_Raw'], axis=1)
            st.dataframe(
                display_operators_df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Rank": st.column_config.NumberColumn("Rank", width="small"),
                    "Address": st.column_config.TextColumn("Address", width="large"),
                    "ENS / Discord Name": st.column_config.TextColumn("ENS / Discord Name", width="medium"),
                    "Participation Rate": st.column_config.TextColumn("Participation Rate", width="small"),
                    "Total Periods": st.column_config.TextColumn("Periods", width="small"),
                    "Total Slots": st.column_config.TextColumn("Total Slots", width="small"),
                    "Successful": st.column_config.TextColumn("Successful", width="small"),
                    "Missed": st.column_config.TextColumn("Missed", width="small")
                }
            )
            
            operators_csv = operators_df.to_csv(index=False)
            st.download_button(
                label="📥 Download Operator Data",
                data=operators_csv,
                file_name=f"sync_committee_operators_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
        else:
            st.info("No operator sync committee data available.")
        
        st.markdown("---")
        
        # Period Analysis
        st.subheader("📊 Period-by-Period Analysis")
        st.caption("Sync committee performance across different periods")
        
        periods_df = create_sync_committee_periods_table(sync_data)
        
        if not periods_df.empty:
            display_periods_df = periods_df.drop(['Participation_Raw'], axis=1)
            st.dataframe(
                display_periods_df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Period": st.column_config.TextColumn("Period", width="small"),
                    "Validators": st.column_config.TextColumn("Validators", width="small"),
                    "Total Slots": st.column_config.TextColumn("Total Slots", width="small"),
                    "Successful": st.column_config.TextColumn("Successful", width="small"),
                    "Missed": st.column_config.TextColumn("Missed", width="small"),
                    "Participation Rate": st.column_config.TextColumn("Participation Rate", width="small")
                }
            )
            
            periods_csv = periods_df.to_csv(index=False)
            st.download_button(
                label="📥 Download Period Data",
                data=periods_csv,
                file_name=f"sync_committee_periods_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
        else:
            st.info("No period data available.")
        
        st.markdown("---")
        
        # Detailed Analysis
        st.subheader("🔍 Detailed Validator Analysis")
        st.caption("Individual validator performance in sync committees")
        
        detailed_df = create_sync_committee_detailed_table(sync_data, ens_names)
        
        if not detailed_df.empty:
            # Search functionality
            search_term = st.text_input(
                "🔍 Search by operator address or ENS name",
                placeholder="Enter address, ENS name, or partial match",
                key="sync_search_input"
            )
            
            if search_term:
                filtered_df = detailed_df[
                    detailed_df['Operator'].str.contains(search_term, case=False, na=False) |
                    detailed_df['Operator Address'].str.contains(search_term, case=False, na=False)
                ]
                
                if not filtered_df.empty:
                    st.info(f"Found {len(filtered_df)} records matching '{search_term}'")
                    display_detailed_df = filtered_df.drop(['Operator Address'], axis=1)
                else:
                    st.warning(f"No records found matching '{search_term}'")
                    display_detailed_df = pd.DataFrame()
            else:
                display_detailed_df = detailed_df.drop(['Operator Address'], axis=1)
            
            if not display_detailed_df.empty:
                st.dataframe(
                    display_detailed_df,
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "Period": st.column_config.TextColumn("Period", width="small"),
                        "Operator": st.column_config.TextColumn("Operator", width="medium"),
                        "Validator Index": st.column_config.TextColumn("Val Index", width="small"),
                        "Validator Pubkey": st.column_config.TextColumn("Validator Pubkey", width="large"),
                        "Participation Rate": st.column_config.TextColumn("Participation Rate", width="small"),
                        "Total Slots": st.column_config.TextColumn("Total Slots", width="small"),
                        "Successful": st.column_config.TextColumn("Successful", width="small"),
                        "Missed": st.column_config.TextColumn("Missed", width="small"),
                        "Start Epoch": st.column_config.TextColumn("Start Epoch", width="small"),
                        "End Epoch": st.column_config.TextColumn("End Epoch", width="small"),
                        "Partial Period": st.column_config.TextColumn("Partial", width="small")
                    }
                )
                
                detailed_csv = detailed_df.to_csv(index=False)
                st.download_button(
                    label="📥 Download Detailed Data",
                    data=detailed_csv,
                    file_name=f"sync_committee_detailed_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
        else:
            st.info("No detailed sync committee data available.")

def create_exit_analysis_tab(operator_validators, operator_exited, ens_names):
    """Create the exit analysis tab"""
    st.markdown("## 🚪 Exit Analysis")
    
    # Load exit data
    exit_data, exit_file = load_exit_data()
    
    if exit_data:
        # Display exit summary using glass cards
        exit_summary = exit_data.get('exit_summary', {})
        if exit_summary:
            total_exited = exit_summary.get('total_exited', 0)
            total_active = exit_summary.get('total_active', 0)
            exit_rate = exit_summary.get('exit_rate_percent', 0)
            
            # Create glass-morphism cards for exit analysis
            st.markdown("""
                <div class="glass-cards-grid">
                    <div class="glass-card">
                        <div class="glass-card-title">Total Exited</div>
                        <div class="glass-card-value">{:,}</div>
                        <div class="glass-card-caption">Validators that have exited</div>
                    </div>
                    <div class="glass-card">
                        <div class="glass-card-title">Total Active</div>
                        <div class="glass-card-value">{:,}</div>
                        <div class="glass-card-caption">Currently active validators</div>
                    </div>
                    <div class="glass-card">
                        <div class="glass-card-title">Exit Rate</div>
                        <div class="glass-card-value">{:.2f}%</div>
                        <div class="glass-card-caption">Percentage of validators exited</div>
                    </div>
                </div>
            """.format(total_exited, total_active, exit_rate), unsafe_allow_html=True)

        st.markdown("### Operators with Exits")
        
        operators_with_exits = exit_data.get('operators_with_exits', [])
        if operators_with_exits:
            exited_operators_data = []
            for operator_data in operators_with_exits:
                addr = operator_data.get('operator', '')
                display_name = format_operator_display_plain(addr, ens_names, show_full_address=True)
                
                # Calculate days since last exit
                latest_timestamp = operator_data.get('latest_exit_timestamp', 0)
                days_since_exit = ""
                if latest_timestamp:
                    days_diff = (datetime.now().timestamp() - latest_timestamp) / (24 * 3600)
                    days_since_exit = f"{int(days_diff)} days ago"

                exited_operators_data.append({
                    'Operator': display_name,
                    'Full Address': addr,
                    'Exits': operator_data.get('exits', 0),
                    'Still Active': operator_data.get('still_active', 0),
                    'Total Ever': operator_data.get('total_ever', 0),
                    'Exit Rate': f"{operator_data.get('exit_rate', 0):.1f}%",
                    'Latest Exit Date': operator_data.get('latest_exit_date', 'N/A'),
                    'Days Since Exit': days_since_exit
                })

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
                    "Exit Rate": st.column_config.TextColumn("Exit Rate", width="small"),
                    "Latest Exit Date": st.column_config.TextColumn("Latest Exit Date", width="medium"),
                    "Days Since Exit": st.column_config.TextColumn("Days Since Exit", width="medium")
                }
            )

            # Recent exits detail table
            recent_exits = exit_data.get('recent_exits', [])
            if recent_exits:
                st.markdown("### Recent Validator Exits")
                st.info(f"Showing the most recent {len(recent_exits)} validator exits")
                
                recent_exits_data = []
                for exit_record in recent_exits:
                    addr = exit_record.get('operator', '')
                    display_name = format_operator_display_plain(addr, ens_names, show_full_address=True)
                    
                    # Format exit date
                    exit_timestamp = exit_record.get('exit_timestamp', 0)
                    exit_date = ""
                    if exit_timestamp:
                        exit_date = datetime.fromtimestamp(exit_timestamp).strftime('%Y-%m-%d %H:%M')
                    
                    recent_exits_data.append({
                        'Validator Index': exit_record.get('validator_index', 'N/A'),
                        'Operator': display_name,
                        'Exit Date': exit_date,
                        'Exit Epoch': exit_record.get('exit_epoch', 'N/A')
                    })
                
                df_recent_exits = pd.DataFrame(recent_exits_data)
                st.dataframe(
                    df_recent_exits,
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "Validator Index": st.column_config.TextColumn("Validator Index", width="small"),
                        "Operator": st.column_config.TextColumn("Operator", width="large"),
                        "Exit Date": st.column_config.TextColumn("Exit Date", width="medium"),
                        "Exit Epoch": st.column_config.TextColumn("Exit Epoch", width="small")
                    }
                )

            # Download buttons
            exits_csv = display_exited_df.to_csv(index=False)
            st.download_button(
                label="📥 Download Exit Summary",
                data=exits_csv,
                file_name=f"nodeset_exits_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
            
            if recent_exits:
                recent_exits_csv = df_recent_exits.to_csv(index=False)
                st.download_button(
                    label="📥 Download Recent Exits",
                    data=recent_exits_csv,
                    file_name=f"nodeset_recent_exits_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
        else:
            st.info("No operators with exits found in the data.")
    else:
        # Fallback to old data if exit data not available
        total_exited = sum(operator_exited.values())
        if total_exited > 0:
            st.warning("⚠️ Detailed exit data not available. Showing basic exit information.")
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
            st.info("😊 Great news! No validator exits detected yet.")

def create_costs_tab(cache, operator_validators, operator_exited, ens_names):
    """Create the costs analysis tab"""
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

        # Calculate metrics for glass cards
        success_rate = (total_successful / total_transactions * 100) if total_transactions > 0 else 0
        avg_cost = total_gas_spent / total_transactions if total_transactions > 0 else 0
        total_active_validators = sum(v - operator_exited.get(k, 0) for k, v in operator_validators.items())
        cost_per_validator = total_gas_spent / total_active_validators if total_active_validators > 0 else 0
        
        # Calculate data age
        if cost_last_updated > 0:
            last_update_dt = datetime.fromtimestamp(cost_last_updated)
            hours_ago = (datetime.now() - last_update_dt).total_seconds() / 3600
            data_age = f"{hours_ago:.1f}h ago"
        else:
            data_age = "Unknown"
        
        # Create glass-morphism cards for transaction costs
        st.markdown("""
            <div class="glass-cards-grid">
                <div class="glass-card">
                    <div class="glass-card-title">Total Gas Spent</div>
                    <div class="glass-card-value">{:.6f}</div>
                    <div class="glass-card-caption">ETH total gas cost</div>
                </div>
                <div class="glass-card">
                    <div class="glass-card-title">Total Transactions</div>
                    <div class="glass-card-value">{:,}</div>
                    <div class="glass-card-caption">All tracked transactions</div>
                </div>
                <div class="glass-card">
                    <div class="glass-card-title">Success Rate</div>
                    <div class="glass-card-value">{:.1f}%</div>
                    <div class="glass-card-caption">Successful transactions</div>
                </div>
                <div class="glass-card">
                    <div class="glass-card-title">Avg Cost/TX</div>
                    <div class="glass-card-value">{:.6f}</div>
                    <div class="glass-card-caption">ETH average per transaction</div>
                </div>
            </div>
        """.format(total_gas_spent, total_transactions, success_rate, avg_cost), unsafe_allow_html=True)
        
        st.markdown("""
            <div class="glass-cards-grid">
                <div class="glass-card">
                    <div class="glass-card-title">Operators Tracked</div>
                    <div class="glass-card-value">{:,}</div>
                    <div class="glass-card-caption">Operators with cost data</div>
                </div>
                <div class="glass-card">
                    <div class="glass-card-title">Failed Transactions</div>
                    <div class="glass-card-value">{:,}</div>
                    <div class="glass-card-caption">Unsuccessful transactions</div>
                </div>
                <div class="glass-card">
                    <div class="glass-card-title">Cost per Validator</div>
                    <div class="glass-card-value">{:.6f}</div>
                    <div class="glass-card-caption">ETH average per validator</div>
                </div>
                <div class="glass-card">
                    <div class="glass-card-title">Data Age</div>
                    <div class="glass-card-value">{}</div>
                    <div class="glass-card-caption">Last cost update</div>
                </div>
            </div>
        """.format(operators_with_costs, total_failed, cost_per_validator, data_age), unsafe_allow_html=True)

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

def create_gas_analysis_tab(ens_names):
    """Create the gas analysis tab"""
    st.subheader("🔥 Pump the Gas! - Gas Limit Analysis")
    st.markdown("*Analysis of gas limit configurations across NodeSet operators- updates daily*")
    
    mev_cache = load_mev_analysis_data()
    if mev_cache[0] is None:
        st.error("⚠️ **MEV analysis data file not found!**")
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
            col1, col2, col3, col4 = responsive_columns(4)
            
            total_validators = sum(distribution.values())
            ultra_high = distribution.get('60000000', 0)
            high_45m = distribution.get('45000000', 0)
            boosted = distribution.get('36000000', 0) 
            standard = distribution.get('30000000', 0)
            
            # Calculate percentages for glass cards
            ultra_pct = (ultra_high / total_validators * 100) if total_validators > 0 else 0
            high45_pct = (high_45m / total_validators * 100) if total_validators > 0 else 0
            boosted_pct = (boosted / total_validators * 100) if total_validators > 0 else 0
            std_pct = (standard / total_validators * 100) if total_validators > 0 else 0
            consistency_rate = consistency_stats.get('consistency_rate', 0)
            
            # Create glass-morphism cards for gas analysis
            st.markdown("""
                <div class="glass-cards-grid">
                    <div class="glass-card">
                        <div class="glass-card-title">🔥🔥🔥🔥 Ultra (60M+)</div>
                        <div class="glass-card-value">{:,}</div>
                        <div class="glass-card-caption">{:.1f}% of validators</div>
                    </div>
                    <div class="glass-card">
                        <div class="glass-card-title">🔥🔥🔥 High (45M)</div>
                        <div class="glass-card-value">{:,}</div>
                        <div class="glass-card-caption">{:.1f}% of validators</div>
                    </div>
                    <div class="glass-card">
                        <div class="glass-card-title">🔥🔥 Normal (36M)</div>
                        <div class="glass-card-value">{:,}</div>
                        <div class="glass-card-caption">{:.1f}% of validators</div>
                    </div>
                    <div class="glass-card">
                        <div class="glass-card-title">🔥 Low (30M)</div>
                        <div class="glass-card-value">{:,}</div>
                        <div class="glass-card-caption">{:.1f}% of validators</div>
                    </div>
                    <div class="glass-card">
                        <div class="glass-card-title">🎯 Consistency Rate</div>
                        <div class="glass-card-value">{:.1f}%</div>
                        <div class="glass-card-caption">Gas strategy consistency</div>
                    </div>
                </div>
            """.format(ultra_high, ultra_pct, high_45m, high45_pct, boosted, boosted_pct, standard, std_pct, consistency_rate), unsafe_allow_html=True)
            
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

def create_raw_data_tab(cache, operator_validators, operator_exited, ens_names):
    """Create the raw data tab with memory usage indicator and all data files"""
    st.subheader("📋 Raw Cache Data")
    
    # Memory Usage Section
    st.markdown("### 💾 Memory Usage")
    
    try:
        memory_mb, memory_percentage = get_memory_usage()
        
        # Color code based on usage percentage
        if memory_percentage < 70:
            status_emoji = "🟢"
            status_text = "Good"
        elif memory_percentage < 85:
            status_emoji = "🟡"
            status_text = "Warning"
        else:
            status_emoji = "🔴"
            status_text = "Critical"
        
        remaining_mb = 1024 - memory_mb
        
        # Create glass-morphism cards for memory usage
        st.markdown(f"""
            <div class="glass-cards-grid">
                <div class="glass-card">
                    <div class="glass-card-title">Current Usage</div>
                    <div class="glass-card-value">{memory_mb:.1f}</div>
                    <div class="glass-card-caption">MB currently used</div>
                </div>
                <div class="glass-card">
                    <div class="glass-card-title">Limit Usage</div>
                    <div class="glass-card-value">{status_emoji} {memory_percentage:.1f}%</div>
                    <div class="glass-card-caption">{status_text} - of 1GB limit</div>
                </div>
                <div class="glass-card">
                    <div class="glass-card-title">Memory Remaining</div>
                    <div class="glass-card-value">{remaining_mb:.1f}</div>
                    <div class="glass-card-caption">MB available</div>
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    except ImportError:
        st.warning("⚠️ Install 'psutil' package to see memory usage: `pip install psutil`")
    except Exception as e:
        st.error(f"⚠️ Could not retrieve memory usage: {str(e)}")
    
    st.markdown("---")
    
    # Data Files Overview Section
    st.markdown("### 📁 Data Files Overview")
    
    # Load all data files and get their information
    data_files_info = []
    
    # 1. Main validator cache
    cache_data = load_validator_data()
    if cache_data[0] is not None:
        cache_content, cache_file = cache_data
        try:
            import os
            file_size = os.path.getsize(cache_file)
            file_size_mb = file_size / (1024 * 1024)
            last_modified = datetime.fromtimestamp(os.path.getmtime(cache_file))
            
            data_files_info.append({
                'File': 'nodeset_validator_tracker_cache.json',
                'Description': 'Main validator data, performance, costs, ENS names',
                'Size (MB)': f"{file_size_mb:.2f}",
                'Last Modified': last_modified.strftime('%Y-%m-%d %H:%M:%S'),
                'Status': '✅ Loaded',
                'Records': f"{len(cache_content.get('operator_validators', {}))} operators"
            })
        except Exception as e:
            data_files_info.append({
                'File': 'nodeset_validator_tracker_cache.json',
                'Description': 'Main validator data, performance, costs, ENS names',
                'Size (MB)': 'Unknown',
                'Last Modified': 'Unknown',
                'Status': '✅ Loaded',
                'Records': f"{len(cache.get('operator_validators', {}))} operators"
            })
    else:
        data_files_info.append({
            'File': 'nodeset_validator_tracker_cache.json',
            'Description': 'Main validator data, performance, costs, ENS names',
            'Size (MB)': 'N/A',
            'Last Modified': 'N/A',
            'Status': '❌ Missing',
            'Records': 'N/A'
        })
    
    # 2. Proposals data
    proposals_cache = load_proposals_data()
    if proposals_cache[0] is not None:
        proposals_content, proposals_file = proposals_cache
        try:
            import os
            file_size = os.path.getsize(proposals_file)
            file_size_mb = file_size / (1024 * 1024)
            last_modified = datetime.fromtimestamp(os.path.getmtime(proposals_file))
            
            metadata = proposals_content.get('metadata', {})
            data_files_info.append({
                'File': 'proposals.json',
                'Description': 'Block proposals, MEV data, validator performance',
                'Size (MB)': f"{file_size_mb:.2f}",
                'Last Modified': last_modified.strftime('%Y-%m-%d %H:%M:%S'),
                'Status': '✅ Loaded',
                'Records': f"{metadata.get('total_proposals', 0)} proposals"
            })
        except Exception as e:
            data_files_info.append({
                'File': 'proposals.json',
                'Description': 'Block proposals, MEV data, validator performance',
                'Size (MB)': 'Unknown',
                'Last Modified': 'Unknown',
                'Status': '✅ Loaded',
                'Records': f"{proposals_content.get('metadata', {}).get('total_proposals', 0)} proposals"
            })
    else:
        data_files_info.append({
            'File': 'proposals.json',
            'Description': 'Block proposals, MEV data, validator performance',
            'Size (MB)': 'N/A',
            'Last Modified': 'N/A',
            'Status': '❌ Missing',
            'Records': 'N/A'
        })
    
    # 3. MEV analysis data
    mev_cache = load_mev_analysis_data()
    if mev_cache[0] is not None:
        mev_content, mev_file = mev_cache
        try:
            import os
            file_size = os.path.getsize(mev_file)
            file_size_mb = file_size / (1024 * 1024)
            last_modified = datetime.fromtimestamp(os.path.getmtime(mev_file))
            
            gas_analysis = mev_content.get('gas_limit_analysis', {})
            distribution = gas_analysis.get('distribution', {})
            total_validators = sum(distribution.values()) if distribution else 0
            
            data_files_info.append({
                'File': 'mev_analysis_results.json',
                'Description': 'Gas limit analysis, MEV relay usage',
                'Size (MB)': f"{file_size_mb:.2f}",
                'Last Modified': last_modified.strftime('%Y-%m-%d %H:%M:%S'),
                'Status': '✅ Loaded',
                'Records': f"{total_validators} validators analyzed"
            })
        except Exception as e:
            data_files_info.append({
                'File': 'mev_analysis_results.json',
                'Description': 'Gas limit analysis, MEV relay usage',
                'Size (MB)': 'Unknown',
                'Last Modified': 'Unknown',
                'Status': '✅ Loaded',
                'Records': 'Unknown'
            })
    else:
        data_files_info.append({
            'File': 'mev_analysis_results.json',
            'Description': 'Gas limit analysis, MEV relay usage',
            'Size (MB)': 'N/A',
            'Last Modified': 'N/A',
            'Status': '❌ Missing',
            'Records': 'N/A'
        })
    
    # 4. Sync committee data
    sync_cache = load_sync_committee_data()
    if sync_cache[0] is not None:
        sync_content, sync_file = sync_cache
        try:
            import os
            file_size = os.path.getsize(sync_file)
            file_size_mb = file_size / (1024 * 1024)
            last_modified = datetime.fromtimestamp(os.path.getmtime(sync_file))
            
            metadata = sync_content.get('metadata', {})
            data_files_info.append({
                'File': 'sync_committee_participation.json',
                'Description': 'Sync committee participation tracking',
                'Size (MB)': f"{file_size_mb:.2f}",
                'Last Modified': last_modified.strftime('%Y-%m-%d %H:%M:%S'),
                'Status': '✅ Loaded',
                'Records': f"{metadata.get('total_periods_tracked', 0)} periods"
            })
        except Exception as e:
            data_files_info.append({
                'File': 'sync_committee_participation.json',
                'Description': 'Sync committee participation tracking',
                'Size (MB)': 'Unknown',
                'Last Modified': 'Unknown',
                'Status': '✅ Loaded',
                'Records': f"{sync_content.get('metadata', {}).get('total_periods_tracked', 0)} periods"
            })
    else:
        data_files_info.append({
            'File': 'sync_committee_participation.json',
            'Description': 'Sync committee participation tracking',
            'Size (MB)': 'N/A',
            'Last Modified': 'N/A',
            'Status': '❌ Missing',
            'Records': 'N/A'
        })
    
    # 5. Missed proposals data
    missed_cache = load_missed_proposals_data()
    if missed_cache[0] is not None:
        missed_content, missed_file = missed_cache
        try:
            import os
            file_size = os.path.getsize(missed_file)
            file_size_mb = file_size / (1024 * 1024)
            last_modified = datetime.fromtimestamp(os.path.getmtime(missed_file))
            
            missed_proposals = missed_content.get('missed_proposals', [])
            data_files_info.append({
                'File': 'missed_proposals_cache.json',
                'Description': 'Missed block proposals tracking',
                'Size (MB)': f"{file_size_mb:.2f}",
                'Last Modified': last_modified.strftime('%Y-%m-%d %H:%M:%S'),
                'Status': '✅ Loaded',
                'Records': f"{len(missed_proposals)} missed proposals"
            })
        except Exception as e:
            data_files_info.append({
                'File': 'missed_proposals_cache.json',
                'Description': 'Missed block proposals tracking',
                'Size (MB)': 'Unknown',
                'Last Modified': 'Unknown',
                'Status': '✅ Loaded',
                'Records': f"{len(missed_content.get('missed_proposals', []))} missed proposals"
            })
    else:
        data_files_info.append({
            'File': 'missed_proposals_cache.json',
            'Description': 'Missed block proposals tracking',
            'Size (MB)': 'N/A',
            'Last Modified': 'N/A',
            'Status': '❌ Missing',
            'Records': 'N/A'
        })
    
    # Display files overview table
    files_df = pd.DataFrame(data_files_info)
    st.dataframe(
        files_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "File": st.column_config.TextColumn("File", width="medium"),
            "Description": st.column_config.TextColumn("Description", width="large"),
            "Size (MB)": st.column_config.TextColumn("Size (MB)", width="small"),
            "Last Modified": st.column_config.TextColumn("Last Modified", width="medium"),
            "Status": st.column_config.TextColumn("Status", width="small"),
            "Records": st.column_config.TextColumn("Records", width="medium")
        }
    )
    
    # Calculate total size
    total_size = 0
    loaded_files = 0
    for file_info in data_files_info:
        if file_info['Status'] == '✅ Loaded' and file_info['Size (MB)'] != 'N/A' and file_info['Size (MB)'] != 'Unknown':
            try:
                total_size += float(file_info['Size (MB)'])
                loaded_files += 1
            except:
                pass
    
    col1, col2, col3 = st.columns(3)
    # Calculate status
    missing_files = 5 - loaded_files
    if missing_files == 0:
        status = "🟢 All files loaded"
    else:
        status = f"🟡 {missing_files} files missing"
    
    # Create glass-morphism cards for raw data overview
    st.markdown("""
        <div class="glass-cards-grid">
            <div class="glass-card">
                <div class="glass-card-title">Total Data Size</div>
                <div class="glass-card-value">{:.2f}</div>
                <div class="glass-card-caption">MB of cached data</div>
            </div>
            <div class="glass-card">
                <div class="glass-card-title">Files Loaded</div>
                <div class="glass-card-value">{}/5</div>
                <div class="glass-card-caption">Data files available</div>
            </div>
            <div class="glass-card">
                <div class="glass-card-title">Status</div>
                <div class="glass-card-value">{}</div>
                <div class="glass-card-caption">Data loading status</div>
            </div>
        </div>
    """.format(total_size, loaded_files, status), unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Detailed Cache Data Section
    st.markdown("### 🔍 Detailed Cache Data")
    
    # Create tabs for each data file
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🏠 Main Cache", 
        "🤲 Proposals", 
        "⛽ MEV Analysis", 
        "📡 Sync Committee", 
        "❌ Missed Proposals"
    ])
    
    with tab1:
        st.markdown("**Main Validator Cache Summary**")
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
            if st.button("🔄 Show Full Main Cache", key="show_main_cache"):
                st.json(cache)
    
    with tab2:
        if proposals_cache[0] is not None:
            proposals_content, _ = proposals_cache
            st.markdown("**Proposals Data Summary**")
            
            col1, col2 = st.columns(2)
            with col1:
                metadata = proposals_content.get('metadata', {})
                st.json(metadata)
            
            with col2:
                if st.button("🔄 Show Full Proposals Data", key="show_proposals_data"):
                    st.json(proposals_content)
        else:
            st.info("❌ Proposals data not loaded")
    
    with tab3:
        if mev_cache[0] is not None:
            mev_content, _ = mev_cache
            st.markdown("**MEV Analysis Data Summary**")
            
            col1, col2 = st.columns(2)
            with col1:
                gas_analysis = mev_content.get('gas_limit_analysis', {})
                summary = {
                    "distribution": gas_analysis.get('distribution', {}),
                    "consistency_stats": gas_analysis.get('consistency_stats', {}),
                    "operator_count": len(mev_content.get('operator_data', {}))
                }
                st.json(summary)
            
            with col2:
                if st.button("🔄 Show Full MEV Data", key="show_mev_data"):
                    st.json(mev_content)
        else:
            st.info("❌ MEV analysis data not loaded")
    
    with tab4:
        if sync_cache[0] is not None:
            sync_content, _ = sync_cache
            st.markdown("**Sync Committee Data Summary**")
            
            col1, col2 = st.columns(2)
            with col1:
                metadata = sync_content.get('metadata', {})
                summary = {
                    "metadata": metadata,
                    "operators_count": len(sync_content.get('operator_participation', {})),
                    "periods_count": len(sync_content.get('period_summaries', {}))
                }
                st.json(summary)
            
            with col2:
                if st.button("🔄 Show Full Sync Committee Data", key="show_sync_data"):
                    st.json(sync_content)
        else:
            st.info("❌ Sync committee data not loaded")
    
    with tab5:
        if missed_cache[0] is not None:
            missed_content, _ = missed_cache
            st.markdown("**Missed Proposals Data Summary**")
            
            col1, col2 = st.columns(2)
            with col1:
                summary = {
                    "missed_proposals_count": len(missed_content.get('missed_proposals', [])),
                    "last_updated": missed_content.get('last_updated', 'Unknown'),
                    "operators_with_misses": len(set(mp.get('operator_address', '') for mp in missed_content.get('missed_proposals', [])))
                }
                st.json(summary)
            
            with col2:
                if st.button("🔄 Show Full Missed Proposals Data", key="show_missed_data"):
                    st.json(missed_content)
        else:
            st.info("❌ Missed proposals data not loaded")

    # ENS names section (existing code)
    st.markdown("---")
    if ens_names:
        st.subheader("🏷️ Resolved ENS Names")

        ens_data = []
        for addr, ens_name in ens_names.items():
            validator_count = operator_validators.get(addr, 0)
            active_count = validator_count - operator_exited.get(addr, 0)

            ens_data.append({
                'ENS / Discord Name': ens_name,
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
                    "ENS / Discord Name": st.column_config.TextColumn("ENS / Discord Name", width="small"),
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


if __name__ == "__main__":
    run_dashboard()
