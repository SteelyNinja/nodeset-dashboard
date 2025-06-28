import streamlit as st

# Dashboard configuration
PAGE_CONFIG = {
    "page_title": "NodeSet Validator Monitor",
    "page_icon": "🔗",
    "layout": "wide",
    "initial_sidebar_state": "collapsed"
}

# Custom CSS for better styling and responsive design
CUSTOM_CSS = """
<style>
    .metric-container {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        margin: 0.5rem 0;
    }

    .big-font {
        font-size: 24px !important;
        font-weight: bold;
    }

    .status-good { color: #28a745; }
    .status-warning { color: #ffc107; }
    .status-danger { color: #dc3545; }

    div[data-testid="metric-container"] {
        background-color: #f8f9fa;
        border: 1px solid #dee2e6;
        padding: 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 0.125rem 0.25rem rgba(0, 0, 0, 0.075);
    }

    .css-1d391kg {
        display: none;
    }

    section[data-testid="stSidebar"] {
        display: none;
    }

    .main .block-container {
        padding-left: 1rem;
        padding-right: 1rem;
        max-width: none;
    }

    .logo-container {
        text-align: left;
        margin-bottom: 1rem;
    }

    @media (max-width: 768px) {
        .main .block-container {
            padding-left: 0.5rem;
            padding-right: 0.5rem;
        }

        div[data-testid="metric-container"] {
            padding: 0.5rem;
            margin: 0.25rem 0;
        }

        h1 {
            font-size: 1.5rem !important;
        }

        .metric-container {
            padding: 0.5rem;
            margin: 0.25rem 0;
        }

        .logo-container img {
            max-height: 120px;
        }
    }

    @media (min-width: 769px) and (max-width: 1024px) {
        .main .block-container {
            padding-left: 0.75rem;
            padding-right: 0.75rem;
        }
    }

    @media (min-width: 1400px) {
        .main .block-container {
            max-width: 1400px;
            margin: 0 auto;
        }
    }

    @media (max-width: 768px) {
        .health-summary {
            font-size: 0.9rem;
            line-height: 1.4;
        }
    }

    .ens-name {
        color: #007bff;
        font-weight: 600;
    }

    .operator-address {
        color: #6c757d;
        font-family: monospace;
        font-size: 0.9em;
    }

    /* 3D Glass-morphism Cards for Key Insights */
    .glass-card {
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.1), rgba(255, 255, 255, 0.05));
        backdrop-filter: blur(15px);
        -webkit-backdrop-filter: blur(15px);
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 16px;
        padding: 1.5rem;
        margin: 0.75rem;
        box-shadow: 
            0 8px 32px rgba(0, 0, 0, 0.1),
            0 4px 16px rgba(0, 0, 0, 0.05),
            inset 0 1px 0 rgba(255, 255, 255, 0.3);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }

    .glass-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.4), transparent);
    }

    .glass-card:hover {
        transform: translateY(-5px) scale(1.02);
        box-shadow: 
            0 16px 48px rgba(0, 0, 0, 0.15),
            0 8px 24px rgba(0, 0, 0, 0.1),
            inset 0 1px 0 rgba(255, 255, 255, 0.4);
        border-color: rgba(255, 255, 255, 0.3);
    }

    .glass-card-title {
        font-size: 0.9rem;
        font-weight: 600;
        color: #4a5568;
        margin-bottom: 0.5rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    .glass-card-value {
        font-size: 1.8rem;
        font-weight: 700;
        color: #2d3748;
        margin-bottom: 0.25rem;
        line-height: 1.1;
    }

    .glass-card-caption {
        font-size: 0.8rem;
        color: #718096;
        line-height: 1.3;
        opacity: 0.8;
    }

    /* Responsive adjustments for glass cards */
    @media (max-width: 768px) {
        .glass-card {
            padding: 1rem;
            margin: 0.5rem;
            border-radius: 12px;
        }
        
        .glass-card-value {
            font-size: 1.5rem;
        }
        
        .glass-card-title {
            font-size: 0.8rem;
        }
    }

    /* Grid layout for glass cards */
    .glass-cards-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        gap: 1rem;
        margin: 1rem 0;
    }

    @media (max-width: 768px) {
        .glass-cards-grid {
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 0.75rem;
        }
    }
</style>
"""

# File paths for data loading
CACHE_FILES = [
    'nodeset_validator_tracker_cache.json',
    './data/nodeset_validator_tracker_cache.json',
    '../nodeset_validator_tracker_cache.json'
]

PROPOSALS_FILES = [
    'proposals.json',
    './data/proposals.json',
    '../proposals.json'
]

MEV_FILES = [
    'mev_analysis_results.json',
    './data/mev_analysis_results.json', 
    '../mev_analysis_results.json'
]

# Logo file paths
DARK_LOGO_PATH = "Nodeset_dark_mode.png"
LIGHT_LOGO_PATH = "Nodeset_light_mode.png"

def apply_page_config():
    """Apply Streamlit page configuration"""
    st.set_page_config(**PAGE_CONFIG)

def apply_custom_css():
    """Apply custom CSS styling"""
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
