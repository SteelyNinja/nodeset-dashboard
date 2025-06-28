def format_operator_display(address: str, ens_names: dict, short: bool = False) -> str:
    """Format operator display with ENS name if available"""
    ens_name = ens_names.get(address)

    if ens_name:
        if short:
            return f"{ens_name}"
        else:
            return f"{ens_name}\n({address[:8]}...{address[-6:]})"
    else:
        return f"{address[:8]}...{address[-6:]}"

def format_operator_display_plain(address: str, ens_names: dict, show_full_address: bool = False) -> str:
    """Format operator display for plain text (no newlines)"""
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

def get_performance_category(performance):
    """Categorize performance based on percentage"""
    if performance >= 99.5:
        return 'Excellent'
    elif performance >= 98.5:
        return 'Good'
    elif performance >= 95.0:
        return 'Average'
    else:
        return 'Poor'

def get_performance_category_display(performance):
    """Get performance category with emoji for display purposes"""
    if performance >= 99.5:
        return '🌟 Excellent'
    elif performance >= 98.5:
        return '✅ Good'
    elif performance >= 95.0:
        return '⚠️ Average'
    else:
        return '🔴 Poor'
