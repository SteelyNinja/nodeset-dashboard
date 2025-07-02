"""
API handler for serving performance data from the NodeSet dashboard
"""
import json
from datetime import datetime, timedelta
from data_loader import load_validator_data, load_proposals_data, load_ens_names, load_sync_committee_data


def get_validators_to_exclude(proposals_data, sync_committee_data, days_back):
    """Get validators that should be excluded due to proposals or sync duties"""
    current_time = datetime.now()
    cutoff_time = current_time - timedelta(days=days_back)
    cutoff_timestamp = cutoff_time.timestamp()
    
    validators_with_proposals = set()
    validators_with_sync_duties = set()
    
    # Get validators with proposals
    if proposals_data and 'proposals' in proposals_data:
        for proposal in proposals_data['proposals']:
            try:
                proposal_timestamp = proposal.get('timestamp', 0)
                if proposal_timestamp >= cutoff_timestamp:
                    validator_index = proposal.get('validator_index')
                    if validator_index:
                        validators_with_proposals.add(validator_index)
            except:
                continue
    
    # Get validators with sync committee duties
    if sync_committee_data and 'detailed_stats' in sync_committee_data:
        GENESIS_TIME = 1606824023
        
        for sync_entry in sync_committee_data['detailed_stats']:
            try:
                end_slot = sync_entry.get('end_slot', 0)
                end_timestamp = GENESIS_TIME + (end_slot * 12)
                
                if end_timestamp >= cutoff_timestamp:
                    validator_index = sync_entry.get('validator_index')
                    if validator_index:
                        validators_with_sync_duties.add(validator_index)
            except:
                continue
    
    return validators_with_proposals.union(validators_with_sync_duties)


def calculate_performance_data(period="7d"):
    """Calculate performance data for the specified period"""
    # Load required data
    cache_data, _ = load_validator_data()
    proposals_data, _ = load_proposals_data()
    sync_committee_data, _ = load_sync_committee_data()
    ens_names = load_ens_names()
    
    if not cache_data or 'validators' not in cache_data:
        return {"error": "No validator data available"}
    
    performance_data = cache_data['validators']
    current_time = datetime.now()
    
    # Set time windows based on period
    if period == "7d":
        days_back = 7
        days_active_required = 7
        performance_key = 'performance_7d'
        exclude_days_back = 9  # Look back 9 days for proposals/sync duties
    elif period == "31d":
        days_back = 31
        days_active_required = 32
        performance_key = 'performance_31d'
        exclude_days_back = 34  # Look back 34 days for proposals/sync duties
    else:
        return {"error": "Invalid period. Use '7d' or '31d'"}
    
    # Calculate timestamps
    active_cutoff_time = current_time - timedelta(days=days_active_required)
    active_cutoff_timestamp = active_cutoff_time.timestamp()
    
    # Get validators to exclude
    validators_to_exclude = get_validators_to_exclude(
        proposals_data, sync_committee_data, exclude_days_back
    )
    
    # Process operator data
    operator_data = {}
    
    for validator_pubkey, validator_info in performance_data.items():
        try:
            operator = validator_info.get('operator')
            if not operator:
                continue
                
            # Check if validator has been active long enough
            activation_data = validator_info.get('activation_data', {})
            activation_timestamp = activation_data.get('activation_timestamp', 0)
            if activation_timestamp == 0 or activation_timestamp > active_cutoff_timestamp:
                continue
            
            # Get performance data
            performance_metrics = validator_info.get('performance_metrics', {})
            performance_value = performance_metrics.get(performance_key, 0)
            validator_index = validator_info.get('validator_index')
            
            # Skip if validator index is missing
            if validator_index is None:
                continue
            
            # Initialize operator data if not exists
            if operator not in operator_data:
                operator_data[operator] = {
                    'validator_count': 0,
                    'total_performance': 0,
                    'regular_validators': []
                }
            
            # Add to operator data
            operator_data[operator]['validator_count'] += 1
            operator_data[operator]['total_performance'] += performance_value
            
            # Check if this validator should be excluded from regular performance
            if validator_index not in validators_to_exclude:
                operator_data[operator]['regular_validators'].append({
                    'validator_index': validator_index,
                    'performance': performance_value
                })
                
        except Exception as e:
            continue
    
    # Create final performance data
    performance_results = []
    for operator, data in operator_data.items():
        regular_validators = data['regular_validators']
        
        if len(regular_validators) == 0:
            continue
            
        # Calculate average performance of regular validators (exclude zero rewards)
        regular_performances = [v['performance'] for v in regular_validators if v['performance'] > 0]
        if len(regular_performances) == 0:
            continue
        
        regular_performance = sum(regular_performances) / len(regular_performances)
        
        # Get ENS/Discord name
        ens_name = ens_names.get(operator, "")
        
        # Count excluded validators
        excluded_count = data['validator_count'] - len(regular_validators)
        
        performance_results.append({
            'operator': operator,
            'ens_name': ens_name,
            'regular_performance_gwei': int(regular_performance),
            'attestation_validators': len(regular_validators),
            'excluded_validators': excluded_count,
            'total_validators': data['validator_count']
        })
    
    # Sort by regular performance
    performance_results.sort(key=lambda x: x['regular_performance_gwei'], reverse=True)
    
    # Add ranks and relative scores
    if performance_results:
        top_performance = performance_results[0]['regular_performance_gwei']
        
        for i, item in enumerate(performance_results):
            item['rank'] = i + 1
            relative_score = (item['regular_performance_gwei'] / top_performance) * 100
            item['relative_score_percent'] = round(relative_score, 1)
    
    return {
        'period': period,
        'timestamp': datetime.now().isoformat(),
        'total_operators': len(performance_results),
        'data': performance_results
    }


def get_api_response(endpoint, period=None, format_type="json"):
    """Main API response handler"""
    if endpoint == "performance":
        if not period:
            period = "7d"
        
        if period not in ["7d", "31d"]:
            return {"error": "Invalid period. Use '7d' or '31d'"}
        
        return calculate_performance_data(period)
    
    else:
        return {"error": "Invalid endpoint. Available endpoints: performance"}