import numpy as np
import pandas as pd
from utils import format_operator_display_plain, get_performance_category

def calculate_concentration_metrics(operator_validators):
    """Calculate concentration metrics including Gini coefficient"""
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

def create_performance_analysis(operator_performance, operator_validators, ens_names):
    """Create performance analysis data and charts"""
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

    return df

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
