import pandas as pd
from datetime import datetime
from utils import get_performance_category
from collections import Counter

def create_top_operators_table(operator_validators, operator_exited, ens_names):
    """Create table of top operators by validator count"""
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
    """Create table of operators by performance"""
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

def format_relay_name(relay_tag):
    """Format relay tag for display"""
    if not relay_tag:
        return "Locally Built"
    
    # Clean up common relay names for better display
    relay_display_map = {
        'bloxroute-max-profit-relay': 'BloxRoute Max Profit',
        'bloxroute-regulated-relay': 'BloxRoute Regulated', 
        'flashbots-relay': 'Flashbots',
        'eden-relay': 'Eden Network',
        'manifold-relay': 'Manifold',
        'ultra-sound-relay': 'Ultra Sound',
        'agnostic-relay': 'Agnostic Relay',
        'bloxml-relay': 'BloXML'
    }
    
    return relay_display_map.get(relay_tag, relay_tag.replace('-', ' ').title())

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
        
        # Get MEV relay information
        relay_tag = proposal.get('relay_tag', '')
        mev_relay = format_relay_name(relay_tag)
        
        table_data.append({
            'Date': proposal['date'],
            'Operator': operator_display,
            'Operator Address': operator_address,
            'Validator Pubkey': proposal['validator_pubkey'],
            'ETH Value': f"{proposal['total_value_eth']:.4f}",
            'Execution Rewards': f"{proposal.get('execution_fees_eth', 0):.4f}",
            'Consensus Rewards': f"{proposal.get('consensus_reward_eth', 0):.4f}",
            'MEV Rewards': f"{proposal.get('mev_breakdown_eth', 0):.4f}",
            'MEV Relay': mev_relay,
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
        
        # Get MEV relay information
        relay_tag = proposal.get('relay_tag', '')
        mev_relay = format_relay_name(relay_tag)
        
        table_data.append({
            'Date': proposal['date'],
            'Operator': operator_display,
            'Operator Address': operator_address,
            'Validator Pubkey': proposal['validator_pubkey'],
            'ETH Value': f"{proposal['total_value_eth']:.4f}",
            'Execution Rewards': f"{proposal.get('execution_fees_eth', 0):.4f}",
            'Consensus Rewards': f"{proposal.get('consensus_reward_eth', 0):.4f}",
            'MEV Rewards': f"{proposal.get('mev_breakdown_eth', 0):.4f}",
            'MEV Relay': mev_relay,
            'Slot': proposal['slot'],
            'Gas Used': f"{proposal['gas_used']:,}",
            'Gas Utilization': f"{proposal['gas_utilization']:.1f}%",
            'TX Count': proposal['tx_count']
        })
    
    return pd.DataFrame(table_data)

def create_mev_relay_breakdown_table(proposals_data):
    """Create a table showing MEV relay usage breakdown"""
    if not proposals_data:
        return pd.DataFrame()
    
    proposals = proposals_data.get('proposals', [])
    
    if not proposals:
        return pd.DataFrame()
    
    # Count relay usage
    relay_counts = Counter()
    for proposal in proposals:
        relay_tag = proposal.get('relay_tag', '')
        if not relay_tag:
            relay_counts['Locally Built'] += 1
        else:
            relay_counts[format_relay_name(relay_tag)] += 1
    
    # Convert to table data
    total_proposals = len(proposals)
    table_data = []
    
    for relay_name, count in relay_counts.most_common():
        percentage = (count / total_proposals) * 100
        table_data.append({
            'MEV Relay': relay_name,
            'Proposals': count,
            'Percentage': f"{percentage:.1f}%"
        })
    
    return pd.DataFrame(table_data)

def create_missed_proposals_table(missed_proposals_data, cache_data, proposals_data, ens_names):
    """Create a table showing missed proposals with operator statistics"""
    if not missed_proposals_data or not cache_data:
        return pd.DataFrame(), {}
    
    missed_proposals = missed_proposals_data.get('missed_proposals', [])
    
    if not missed_proposals:
        return pd.DataFrame(), {}
    
    # Count missed proposals by operator
    operator_missed_counts = Counter()
    operator_details = {}
    
    for missed in missed_proposals:
        operator = missed['operator']
        operator_missed_counts[operator] += 1
        
        if operator not in operator_details:
            operator_details[operator] = {
                'first_missed': missed['date'],
                'last_missed': missed['date'],
                'missed_slots': []
            }
        
        operator_details[operator]['missed_slots'].append({
            'slot': missed['slot'],
            'date': missed['date']
        })
        
        # Update date range
        if missed['date'] < operator_details[operator]['first_missed']:
            operator_details[operator]['first_missed'] = missed['date']
        if missed['date'] > operator_details[operator]['last_missed']:
            operator_details[operator]['last_missed'] = missed['date']
    
    # Count successful proposals by operator from proposals_data
    operator_successful_counts = Counter()
    if proposals_data and 'proposals' in proposals_data:
        for proposal in proposals_data['proposals']:
            operator = proposal.get('operator')
            if operator:
                operator_successful_counts[operator] += 1
    
    # Create table data
    table_data = []
    
    for missed in missed_proposals:
        operator = missed['operator']
        ens_name = ens_names.get(operator, "")
        
        # Format operator display
        if ens_name:
            operator_display = f"{ens_name}"
        else:
            operator_display = f"{operator[:8]}...{operator[-6:]}"
        
        # Calculate stats for this operator
        total_missed = operator_missed_counts[operator]
        total_successful = operator_successful_counts.get(operator, 0)
        
        # Calculate missed percentage
        total_attempts = total_missed + total_successful
        if total_attempts > 0:
            missed_percentage = f"{(total_missed / total_attempts * 100):.1f}%"
        else:
            missed_percentage = "N/A"
        
        table_data.append({
            'Date & Time': missed['date'],
            'Slot Number': missed['slot'],
            'Operator Name': operator_display,
            'Operator Address': operator,
            'Total Missed': total_missed if total_missed > 1 else 1,
            'Total Successful': total_successful,
            'Missed %': missed_percentage
        })
    
    # Sort by date (most recent first)
    table_data.sort(key=lambda x: x['Date & Time'], reverse=True)
    
    # Calculate summary statistics
    total_missed = len(missed_proposals)
    unique_operators = len(operator_missed_counts)
    
    summary_stats = {
        'total_missed': total_missed,
        'unique_operators': unique_operators,
        'operator_breakdown': dict(operator_missed_counts)
    }
    
    return pd.DataFrame(table_data), summary_stats

def create_proposals_operators_table(proposals_data, ens_names):
    """Create summary table of proposals by operator"""
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
            
            # Update proposals to include formatted relay names
            formatted_proposals = []
            for p in operator_proposals:
                formatted_p = p.copy()
                formatted_p['mev_relay'] = format_relay_name(p.get('relay_tag', ''))
                formatted_proposals.append(formatted_p)
            
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
                'proposals': formatted_proposals
            })
    
    return sorted(table_data, key=lambda x: x['proposal_count'], reverse=True)

def create_sync_committee_operators_table(sync_data, ens_names):
    """Create table of operators ranked by sync committee participation"""
    if not sync_data:
        return pd.DataFrame()
    
    operator_summary = sync_data.get('operator_summary', {})
    
    data = []
    for addr, stats in operator_summary.items():
        ens_name = ens_names.get(addr, "")
        
        data.append({
            'Rank': 0,
            'Address': addr,
            'ENS Name': ens_name,
            'Participation Rate': f"{stats['participation_rate']:.2f}%",
            'Participation_Raw': stats['participation_rate'],
            'Total Periods': stats['total_periods'],
            'Total Slots': f"{stats['total_slots']:,}",
            'Successful': f"{stats['total_successful']:,}",
            'Missed': f"{stats['total_missed']:,}",
        })
    
    if not data:
        return pd.DataFrame()
    
    df = pd.DataFrame(data)
    # Sort by Total Periods (highest first), then by Participation Rate for ties
    df = df.sort_values(['Total Periods', 'Participation_Raw'], ascending=[False, False]).reset_index(drop=True)
    df['Rank'] = range(1, len(df) + 1)
    
    return df

def create_sync_committee_periods_table(sync_data):
    """Create table showing participation by period"""
    if not sync_data:
        return pd.DataFrame()
    
    period_summary = sync_data.get('period_summary', {})
    
    data = []
    for period, stats in period_summary.items():
        data.append({
            'Period': period,
            'Validators': stats['our_validators_count'],
            'Total Slots': f"{stats['total_slots']:,}",
            'Successful': f"{stats['total_successful']:,}",
            'Missed': f"{stats['total_missed']:,}",
            'Participation Rate': f"{stats['participation_rate']:.2f}%",
            'Participation_Raw': stats['participation_rate']
        })
    
    if not data:
        return pd.DataFrame()
    
    df = pd.DataFrame(data)
    df = df.sort_values('Period', ascending=False)
    
    return df

def create_sync_committee_detailed_table(sync_data, ens_names):
    """Create detailed table of individual validator sync committee performance"""
    if not sync_data:
        return pd.DataFrame()
    
    detailed_stats = sync_data.get('detailed_stats', [])
    
    data = []
    for entry in detailed_stats:
        ens_name = ens_names.get(entry['operator'], "")
        operator_display = ens_name if ens_name else f"{entry['operator'][:8]}...{entry['operator'][-6:]}"
        
        # Calculate successful and missed percentages
        total_slots = entry['total_slots']
        successful_count = entry['successful_attestations']
        missed_count = entry['missed_attestations']
        
        # Calculate percentages
        successful_percentage = (successful_count / total_slots * 100) if total_slots > 0 else 0
        missed_percentage = (missed_count / total_slots * 100) if total_slots > 0 else 0
        
        data.append({
            'Period': entry['period'],
            'Operator': operator_display,
            'Operator Address': entry['operator'],
            'Validator Index': entry['validator_index'],
            'Validator Pubkey': entry['validator_pubkey'],
            'Participation Rate': f"{entry['participation_rate']:.2f}%",
            'Total Slots': f"{entry['total_slots']:,}",
            'Successful': f"{entry['successful_attestations']:,}",
            'Missed': f"{entry['missed_attestations']:,}",
            'Successful %': f"{successful_percentage:.2f}%",
            'Missed %': f"{missed_percentage:.2f}%",
            'Start Epoch': entry['start_epoch'],
            'End Epoch': entry['end_epoch'],
            'Partial Period': "Yes" if entry.get('is_partial_period', False) else "No"
        })
    
    if not data:
        return pd.DataFrame()
    
    df = pd.DataFrame(data)
    df = df.sort_values(['Period', 'Participation Rate'], ascending=[False, False])
    
    return df
