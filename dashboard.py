import pandas as pd
from datetime import datetime
from utils import get_performance_category

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
        
        # MEV boost indicator
        is_mev_boost = proposal.get('is_mev_boost_block', False)
        mev_indicator = "✓" if is_mev_boost else "✗"
        
        table_data.append({
            'Date': proposal['date'],
            'Operator': operator_display,
            'Operator Address': operator_address,
            'Validator Pubkey': proposal['validator_pubkey'],
            'ETH Value': f"{proposal['total_value_eth']:.4f}",
            'Execution Rewards': f"{proposal.get('execution_fees_eth', 0):.4f}",
            'Consensus Rewards': f"{proposal.get('consensus_reward_eth', 0):.4f}",
            'MEV Rewards': f"{proposal.get('mev_breakdown_eth', 0):.4f}",
            'MEV Block': mev_indicator,
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
        
        # MEV boost indicator
        is_mev_boost = proposal.get('is_mev_boost_block', False)
        mev_indicator = "✓" if is_mev_boost else "✗"
        
        table_data.append({
            'Date': proposal['date'],
            'Operator': operator_display,
            'Operator Address': operator_address,
            'Validator Pubkey': proposal['validator_pubkey'],
            'ETH Value': f"{proposal['total_value_eth']:.4f}",
            'Execution Rewards': f"{proposal.get('execution_fees_eth', 0):.4f}",
            'Consensus Rewards': f"{proposal.get('consensus_reward_eth', 0):.4f}",
            'MEV Rewards': f"{proposal.get('mev_breakdown_eth', 0):.4f}",
            'MEV Block': mev_indicator,
            'Slot': proposal['slot'],
            'Gas Used': f"{proposal['gas_used']:,}",
            'Gas Utilization': f"{proposal['gas_utilization']:.1f}%",
            'TX Count': proposal['tx_count']
        })
    
    return pd.DataFrame(table_data)

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
    df = df.sort_values('Participation_Raw', ascending=False).reset_index(drop=True)
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
            'Start Epoch': entry['start_epoch'],
            'End Epoch': entry['end_epoch'],
            'Partial Period': "Yes" if entry.get('is_partial_period', False) else "No"
        })
    
    if not data:
        return pd.DataFrame()
    
    df = pd.DataFrame(data)
    df = df.sort_values(['Period', 'Participation Rate'], ascending=[False, False])
    
    return df
