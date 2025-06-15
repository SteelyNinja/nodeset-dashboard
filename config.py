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
