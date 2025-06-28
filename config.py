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

    /* App Background Colors */
    .stApp {
        background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 50%, #f0f9ff 100%);
        min-height: 100vh;
    }

    .main .block-container {
        background: transparent;
    }

    /* Dark mode background */
    @media (prefers-color-scheme: dark) {
        .stApp {
            background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #0f172a 100%);
        }
    }

    /* Streamlit dark theme support */
    [data-theme="dark"] .stApp,
    .stApp[data-theme="dark"] {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #0f172a 100%) !important;
    }

    /* Plotly Charts Background - Multiple Selectors */
    .js-plotly-plot,
    .js-plotly-plot .plotly,
    .js-plotly-plot .plot-container,
    .js-plotly-plot .svg-container,
    .plotly-graph-div,
    div[data-testid="stPlotlyChart"] > div,
    div[data-testid="stPlotlyChart"] .js-plotly-plot {
        background: rgba(255, 255, 255, 0.7) !important;
        border-radius: 12px !important;
        border: 1px solid rgba(0, 0, 0, 0.1) !important;
    }

    /* Streamlit Tables - Multiple Selectors */
    .stDataFrame,
    .stDataFrame > div,
    div[data-testid="stDataFrame"],
    div[data-testid="stDataFrame"] > div,
    .stTable,
    .stTable > div,
    table,
    .dataframe {
        background: rgba(255, 255, 255, 0.7) !important;
        border-radius: 12px !important;
        border: 1px solid rgba(0, 0, 0, 0.1) !important;
        overflow: hidden !important;
    }

    /* Table Headers */
    th,
    thead th,
    .stDataFrame th,
    .dataframe th {
        background: rgba(59, 130, 246, 0.15) !important;
        color: #1f2937 !important;
        border-bottom: 1px solid rgba(0, 0, 0, 0.1) !important;
    }

    /* Table Rows */
    tr:nth-child(even),
    tbody tr:nth-child(even),
    .stDataFrame tr:nth-child(even) {
        background: rgba(255, 255, 255, 0.5) !important;
    }

    tr:nth-child(odd),
    tbody tr:nth-child(odd),
    .stDataFrame tr:nth-child(odd) {
        background: rgba(255, 255, 255, 0.3) !important;
    }

    /* Clean approach - target specific Streamlit containers only */
    div[data-testid="stDataFrame"],
    div[data-testid="stTable"] {
        background: rgba(255, 255, 255, 0.7) !important;
        border-radius: 12px !important;
        border: 1px solid rgba(0, 0, 0, 0.1) !important;
        padding: 8px !important;
    }

    div[data-testid="stPlotlyChart"] {
        background: rgba(255, 255, 255, 0.7) !important;
        border-radius: 12px !important;
        border: 1px solid rgba(0, 0, 0, 0.1) !important;
        padding: 8px !important;
    }

    /* Additional Streamlit component backgrounds */
    div[data-testid="column"] > div,
    div[data-testid="stVerticalBlock"] > div[data-testid="element-container"] {
        background: transparent !important;
    }

    /* Dark mode for charts and tables */
    @media (prefers-color-scheme: dark) {
        div[data-testid="stDataFrame"],
        div[data-testid="stTable"] {
            background: rgba(15, 23, 42, 0.8) !important;
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
        }

        div[data-testid="stPlotlyChart"] {
            background: rgba(15, 23, 42, 0.8) !important;
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
        }
    }

    /* Streamlit dark theme support */
    [data-theme="dark"] div[data-testid="stDataFrame"],
    [data-theme="dark"] div[data-testid="stTable"],
    .stApp[data-theme="dark"] div[data-testid="stDataFrame"],
    .stApp[data-theme="dark"] div[data-testid="stTable"] {
        background: rgba(15, 23, 42, 0.8) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
    }

    [data-theme="dark"] div[data-testid="stPlotlyChart"],
    .stApp[data-theme="dark"] div[data-testid="stPlotlyChart"] {
        background: rgba(15, 23, 42, 0.8) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
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
        background: linear-gradient(135deg, rgba(59, 130, 246, 0.08), rgba(147, 51, 234, 0.08));
        backdrop-filter: blur(15px);
        -webkit-backdrop-filter: blur(15px);
        border: 1px solid rgba(0, 0, 0, 0.1);
        border-radius: 16px;
        padding: 1.5rem;
        margin: 0.75rem;
        box-shadow: 
            0 8px 32px rgba(0, 0, 0, 0.1),
            0 4px 16px rgba(0, 0, 0, 0.05);
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
        color: #374151;
        margin-bottom: 0.5rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    .glass-card-value {
        font-size: 1.8rem;
        font-weight: 700;
        color: #1f2937;
        margin-bottom: 0.25rem;
        line-height: 1.1;
    }

    .glass-card-caption {
        font-size: 0.8rem;
        color: #6b7280;
        line-height: 1.3;
        opacity: 0.8;
    }

    /* Dark mode adjustments for glass cards */
    @media (prefers-color-scheme: dark) {
        .glass-card {
            background: linear-gradient(135deg, rgba(59, 130, 246, 0.12), rgba(147, 51, 234, 0.12));
            border: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        .glass-card:hover {
            border-color: rgba(255, 255, 255, 0.2);
        }
        
        .glass-card-title {
            color: rgba(255, 255, 255, 0.8);
        }

        .glass-card-value {
            color: rgba(255, 255, 255, 0.95);
        }

        .glass-card-caption {
            color: rgba(255, 255, 255, 0.6);
        }
    }

    /* Streamlit dark theme support */
    [data-theme="dark"] .glass-card-title,
    .stApp[data-theme="dark"] .glass-card-title {
        color: rgba(255, 255, 255, 0.8) !important;
    }

    [data-theme="dark"] .glass-card-value,
    .stApp[data-theme="dark"] .glass-card-value {
        color: rgba(255, 255, 255, 0.95) !important;
    }

    [data-theme="dark"] .glass-card-caption,
    .stApp[data-theme="dark"] .glass-card-caption {
        color: rgba(255, 255, 255, 0.6) !important;
    }

    [data-theme="dark"] .glass-card,
    .stApp[data-theme="dark"] .glass-card {
        background: linear-gradient(135deg, rgba(59, 130, 246, 0.12), rgba(147, 51, 234, 0.12)) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
    }

    [data-theme="dark"] .glass-card:hover,
    .stApp[data-theme="dark"] .glass-card:hover {
        border-color: rgba(255, 255, 255, 0.2) !important;
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
