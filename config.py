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

        /* Mobile-specific dataframe improvements */
        div[data-testid="stDataFrame"],
        div[data-testid="stTable"] {
            font-size: 14px !important;
            padding: 12px !important;
            margin: 10px 0 !important;
            border-radius: 8px !important;
            background: rgba(255, 255, 255, 0.9) !important;
            border: 2px solid rgba(0, 0, 0, 0.15) !important;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1) !important;
        }

        /* Increase text contrast on mobile */
        div[data-testid="stDataFrame"] *,
        div[data-testid="stTable"] * {
            color: #1f2937 !important;
            font-weight: 500 !important;
        }

        /* Make headers more prominent on mobile */
        div[data-testid="stDataFrame"] th,
        div[data-testid="stTable"] th {
            background: rgba(59, 130, 246, 0.2) !important;
            color: #1f2937 !important;
            font-weight: 700 !important;
            font-size: 15px !important;
            padding: 12px 8px !important;
        }

        /* Improve row spacing on mobile */
        div[data-testid="stDataFrame"] td,
        div[data-testid="stTable"] td {
            padding: 10px 8px !important;
            border-bottom: 1px solid rgba(0, 0, 0, 0.1) !important;
        }

        /* Larger controls on mobile */
        div[data-testid="stDataFrame"] button,
        div[data-testid="stDataFrame"] input,
        div[data-testid="stDataFrame"] .ag-header-cell-menu-button {
            min-height: 44px !important;
            font-size: 16px !important;
            padding: 8px 12px !important;
        }

        /* Mobile chart improvements */
        div[data-testid="stPlotlyChart"] {
            margin: 8px 0 !important;
            padding: 8px !important;
            border-radius: 8px !important;
            background: rgba(255, 255, 255, 0.9) !important;
            border: 2px solid rgba(0, 0, 0, 0.1) !important;
        }

        /* Ensure charts fit mobile screens */
        div[data-testid="stPlotlyChart"] .js-plotly-plot,
        div[data-testid="stPlotlyChart"] .plotly-graph-div {
            max-width: calc(100vw - 40px) !important;
            overflow-x: auto !important;
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
        overflow: visible !important;
        position: relative !important;
    }

    /* Ensure dataframe search/filter controls are visible */
    div[data-testid="stDataFrame"] .stDataFrame-toolbar,
    div[data-testid="stDataFrame"] [data-testid="stDataFrameResizeHandle"],
    div[data-testid="stDataFrame"] .ag-header-cell-menu-button,
    div[data-testid="stDataFrame"] .ag-side-bar,
    div[data-testid="stDataFrame"] .ag-tool-panel,
    div[data-testid="stDataFrame"] .ag-column-drop,
    div[data-testid="stDataFrame"] .ag-filter-panel,
    div[data-testid="stDataFrame"] .ag-menu,
    div[data-testid="stDataFrame"] .ag-popup {
        z-index: 1000 !important;
        position: relative !important;
        overflow: visible !important;
    }

    /* Hide search overlay elements when not hovering - more aggressive approach */
    div[data-testid="stDataFrame"]:not(:hover) div[style*="position: absolute"][style*="z-index"] {
        opacity: 0 !important;
        transition: opacity 0.3s ease !important;
        pointer-events: none !important;
    }

    /* Specifically target blue search bar elements */
    div[data-testid="stDataFrame"]:not(:hover) div[style*="background-color: rgba"][style*="position: absolute"],
    div[data-testid="stDataFrame"]:not(:hover) div[style*="background: rgba"][style*="position: absolute"] {
        opacity: 0 !important;
        visibility: hidden !important;
        display: none !important;
    }

    /* Show search elements when hovering */
    div[data-testid="stDataFrame"]:hover div[style*="position: absolute"][style*="z-index"],
    div[data-testid="stDataFrame"]:hover div[style*="background-color: rgba"][style*="position: absolute"],
    div[data-testid="stDataFrame"]:hover div[style*="background: rgba"][style*="position: absolute"] {
        opacity: 1 !important;
        visibility: visible !important;
        display: block !important;
        transition: opacity 0.3s ease !important;
        pointer-events: auto !important;
    }


    /* Give extra space at the top of dataframes for controls */
    div[data-testid="stDataFrame"] {
        padding-top: 15px !important;
        margin-top: 5px !important;
    }

    div[data-testid="stPlotlyChart"] {
        background: rgba(255, 255, 255, 0.7) !important;
        border-radius: 12px !important;
        border: 1px solid rgba(0, 0, 0, 0.1) !important;
        padding: 8px !important;
        overflow: visible !important;
        width: 100% !important;
        max-width: 100% !important;
        box-sizing: border-box !important;
    }

    /* Ensure Plotly charts respect container boundaries */
    div[data-testid="stPlotlyChart"] .js-plotly-plot,
    div[data-testid="stPlotlyChart"] .plotly-graph-div,
    div[data-testid="stPlotlyChart"] .svg-container,
    div[data-testid="stPlotlyChart"] .plot-container,
    div[data-testid="stPlotlyChart"] svg,
    div[data-testid="stPlotlyChart"] .main-svg {
        width: 100% !important;
        max-width: 100% !important;
        overflow: hidden !important;
        box-sizing: border-box !important;
    }

    /* Allow legends to extend outside chart area, but contain main plot */
    div[data-testid="stPlotlyChart"] .plot-container,
    div[data-testid="stPlotlyChart"] .svg-container {
        max-width: 100% !important;
        overflow: visible !important;
    }
    
    /* Keep main plot elements contained but allow legend overflow */
    div[data-testid="stPlotlyChart"] .main-svg {
        max-width: 100% !important;
        overflow: visible !important;
    }

    /* Specifically target Plotly's modebar and other floating elements */
    div[data-testid="stPlotlyChart"] .modebar,
    div[data-testid="stPlotlyChart"] .modebar-container {
        position: absolute !important;
        right: 10px !important;
        top: 10px !important;
        z-index: 1000 !important;
    }

    /* Additional Streamlit component backgrounds */
    div[data-testid="column"] > div,
    div[data-testid="stVerticalBlock"] > div[data-testid="element-container"] {
        background: transparent !important;
    }

    /* Force Streamlit columns to contain their content - but allow dataframe controls to overflow */
    div[data-testid="column"] {
        overflow: visible !important;
        width: 100% !important;
        max-width: 100% !important;
        box-sizing: border-box !important;
        position: relative !important;
    }

    /* Allow chart columns to show legends outside boundaries */
    div[data-testid="column"]:has(div[data-testid="stPlotlyChart"]) {
        overflow: visible !important;
    }

    /* Container for chart elements - allow dataframe controls to overflow */
    div[data-testid="element-container"] {
        overflow: visible !important;
        width: 100% !important;
        max-width: 100% !important;
        box-sizing: border-box !important;
        position: relative !important;
    }

    /* Allow chart element containers to show legends outside boundaries */
    div[data-testid="element-container"]:has(div[data-testid="stPlotlyChart"]) {
        overflow: visible !important;
    }

    /* Dark mode for charts and tables - Fixed text visibility */
    @media (prefers-color-scheme: dark) {
        /* Main dataframe container only */
        div[data-testid="stDataFrame"],
        div[data-testid="stTable"] {
            background: linear-gradient(135deg, rgba(59, 130, 246, 0.2), rgba(147, 51, 234, 0.2)) !important;
            backdrop-filter: blur(15px) !important;
            -webkit-backdrop-filter: blur(15px) !important;
            border: 1px solid rgba(255, 255, 255, 0.2) !important;
            border-radius: 12px !important;
            overflow: visible !important;
            position: relative !important;
        }

        /* Dark mode mobile dataframe improvements */
        @media (max-width: 768px) {
            div[data-testid="stDataFrame"],
            div[data-testid="stTable"] {
                background: linear-gradient(135deg, rgba(59, 130, 246, 0.3), rgba(147, 51, 234, 0.3)) !important;
                backdrop-filter: blur(10px) !important;
                -webkit-backdrop-filter: blur(10px) !important;
                border: 2px solid rgba(255, 255, 255, 0.3) !important;
                box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3) !important;
            }

            /* Improve text contrast in dark mode mobile */
            div[data-testid="stDataFrame"] *,
            div[data-testid="stTable"] * {
                color: rgba(255, 255, 255, 0.95) !important;
                font-weight: 600 !important;
            }

            /* Dark mode mobile headers */
            div[data-testid="stDataFrame"] th,
            div[data-testid="stTable"] th {
                background: rgba(255, 255, 255, 0.15) !important;
                color: rgba(255, 255, 255, 0.95) !important;
                border-bottom: 1px solid rgba(255, 255, 255, 0.2) !important;
            }

            /* Dark mode mobile table cells */
            div[data-testid="stDataFrame"] td,
            div[data-testid="stTable"] td {
                border-bottom: 1px solid rgba(255, 255, 255, 0.1) !important;
            }
        }

        /* Table content - no blur, solid background for text readability */
        div[data-testid="stDataFrame"] *,
        div[data-testid="stTable"] *,
        .stDataFrame,
        .stDataFrame *,
        .dataframe,
        .dataframe * {
            background: rgba(59, 130, 246, 0.08) !important;
            backdrop-filter: none !important;
            -webkit-backdrop-filter: none !important;
            color: rgba(255, 255, 255, 0.95) !important;
            border-color: rgba(255, 255, 255, 0.1) !important;
        }

        /* Table cells and text elements */
        div[data-testid="stDataFrame"] div,
        div[data-testid="stDataFrame"] span,
        div[data-testid="stDataFrame"] td,
        div[data-testid="stDataFrame"] th,
        div[data-testid="stDataFrame"] iframe,
        div[data-testid="stDataFrame"] iframe html,
        div[data-testid="stDataFrame"] iframe body,
        div[data-testid="stDataFrame"] iframe table,
        div[data-testid="stDataFrame"] iframe tr,
        div[data-testid="stDataFrame"] iframe td,
        div[data-testid="stDataFrame"] iframe th {
            background: transparent !important;
            backdrop-filter: none !important;
            -webkit-backdrop-filter: none !important;
            color: rgba(255, 255, 255, 0.95) !important;
        }

        div[data-testid="stPlotlyChart"] {
            background: linear-gradient(135deg, rgba(59, 130, 246, 0.15), rgba(147, 51, 234, 0.15)) !important;
            backdrop-filter: blur(15px) !important;
            -webkit-backdrop-filter: blur(15px) !important;
            border: 1px solid rgba(255, 255, 255, 0.2) !important;
            overflow: hidden !important;
            width: 100% !important;
            max-width: 100% !important;
            box-sizing: border-box !important;
        }
    }

    /* Streamlit dark theme support - Fixed text visibility */
    [data-theme="dark"] div[data-testid="stDataFrame"],
    [data-theme="dark"] div[data-testid="stTable"],
    .stApp[data-theme="dark"] div[data-testid="stDataFrame"],
    .stApp[data-theme="dark"] div[data-testid="stTable"] {
        background: linear-gradient(135deg, rgba(59, 130, 246, 0.2), rgba(147, 51, 234, 0.2)) !important;
        backdrop-filter: blur(15px) !important;
        -webkit-backdrop-filter: blur(15px) !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        border-radius: 12px !important;
        overflow: visible !important;
        position: relative !important;
    }

    /* Table content - no blur for text readability */
    [data-theme="dark"] div[data-testid="stDataFrame"] *,
    [data-theme="dark"] div[data-testid="stTable"] *,
    [data-theme="dark"] .stDataFrame,
    [data-theme="dark"] .stDataFrame *,
    [data-theme="dark"] .dataframe,
    [data-theme="dark"] .dataframe *,
    .stApp[data-theme="dark"] div[data-testid="stDataFrame"] *,
    .stApp[data-theme="dark"] div[data-testid="stTable"] *,
    .stApp[data-theme="dark"] .stDataFrame,
    .stApp[data-theme="dark"] .stDataFrame *,
    .stApp[data-theme="dark"] .dataframe,
    .stApp[data-theme="dark"] .dataframe * {
        background: rgba(59, 130, 246, 0.08) !important;
        backdrop-filter: none !important;
        -webkit-backdrop-filter: none !important;
        color: rgba(255, 255, 255, 0.95) !important;
        border-color: rgba(255, 255, 255, 0.1) !important;
    }

    /* Text elements with transparent background */
    [data-theme="dark"] div[data-testid="stDataFrame"] div,
    [data-theme="dark"] div[data-testid="stDataFrame"] span,
    [data-theme="dark"] div[data-testid="stDataFrame"] td,
    [data-theme="dark"] div[data-testid="stDataFrame"] th,
    [data-theme="dark"] div[data-testid="stDataFrame"] iframe,
    [data-theme="dark"] div[data-testid="stDataFrame"] iframe html,
    [data-theme="dark"] div[data-testid="stDataFrame"] iframe body,
    [data-theme="dark"] div[data-testid="stDataFrame"] iframe table,
    [data-theme="dark"] div[data-testid="stDataFrame"] iframe tr,
    [data-theme="dark"] div[data-testid="stDataFrame"] iframe td,
    [data-theme="dark"] div[data-testid="stDataFrame"] iframe th,
    .stApp[data-theme="dark"] div[data-testid="stDataFrame"] div,
    .stApp[data-theme="dark"] div[data-testid="stDataFrame"] span,
    .stApp[data-theme="dark"] div[data-testid="stDataFrame"] td,
    .stApp[data-theme="dark"] div[data-testid="stDataFrame"] th,
    .stApp[data-theme="dark"] div[data-testid="stDataFrame"] iframe,
    .stApp[data-theme="dark"] div[data-testid="stDataFrame"] iframe html,
    .stApp[data-theme="dark"] div[data-testid="stDataFrame"] iframe body,
    .stApp[data-theme="dark"] div[data-testid="stDataFrame"] iframe table,
    .stApp[data-theme="dark"] div[data-testid="stDataFrame"] iframe tr,
    .stApp[data-theme="dark"] div[data-testid="stDataFrame"] iframe td,
    .stApp[data-theme="dark"] div[data-testid="stDataFrame"] iframe th {
        background: transparent !important;
        backdrop-filter: none !important;
        -webkit-backdrop-filter: none !important;
        color: rgba(255, 255, 255, 0.95) !important;
    }

    [data-theme="dark"] div[data-testid="stPlotlyChart"],
    .stApp[data-theme="dark"] div[data-testid="stPlotlyChart"] {
        background: linear-gradient(135deg, rgba(59, 130, 246, 0.15), rgba(147, 51, 234, 0.15)) !important;
        backdrop-filter: blur(15px) !important;
        -webkit-backdrop-filter: blur(15px) !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        overflow: hidden !important;
        width: 100% !important;
        max-width: 100% !important;
        box-sizing: border-box !important;
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

    /* Streamlit dataframe search/filter controls styling */
    div[data-testid="stDataFrame"] input,
    div[data-testid="stDataFrame"] .stSelectbox,
    div[data-testid="stDataFrame"] .stMultiSelect,
    div[data-testid="stDataFrame"] button,
    .stDataFrame-toolbar,
    .stDataFrame-toolbar input,
    .stDataFrame-toolbar button,
    [data-testid="stDataFrameResizeHandle"],
    .ag-header-cell-menu-button,
    .ag-icon,
    .ag-menu,
    .ag-popup,
    .ag-filter-panel {
        background: rgba(255, 255, 255, 0.9) !important;
        color: #1f2937 !important;
        border: 1px solid rgba(0, 0, 0, 0.2) !important;
        border-radius: 6px !important;
    }

    /* Dark mode for dataframe controls */
    @media (prefers-color-scheme: dark) {
        div[data-testid="stDataFrame"] input,
        div[data-testid="stDataFrame"] .stSelectbox,
        div[data-testid="stDataFrame"] .stMultiSelect,
        div[data-testid="stDataFrame"] button,
        .stDataFrame-toolbar,
        .stDataFrame-toolbar input,
        .stDataFrame-toolbar button,
        [data-testid="stDataFrameResizeHandle"],
        .ag-header-cell-menu-button,
        .ag-icon,
        .ag-menu,
        .ag-popup,
        .ag-filter-panel {
            background: rgba(255, 255, 255, 0.95) !important;
            color: #1f2937 !important;
            border: 1px solid rgba(255, 255, 255, 0.3) !important;
            border-radius: 6px !important;
        }
    }

    /* Streamlit dark theme support for dataframe controls */
    [data-theme="dark"] div[data-testid="stDataFrame"] input,
    [data-theme="dark"] div[data-testid="stDataFrame"] .stSelectbox,
    [data-theme="dark"] div[data-testid="stDataFrame"] .stMultiSelect,
    [data-theme="dark"] div[data-testid="stDataFrame"] button,
    [data-theme="dark"] .stDataFrame-toolbar,
    [data-theme="dark"] .stDataFrame-toolbar input,
    [data-theme="dark"] .stDataFrame-toolbar button,
    [data-theme="dark"] [data-testid="stDataFrameResizeHandle"],
    [data-theme="dark"] .ag-header-cell-menu-button,
    [data-theme="dark"] .ag-icon,
    [data-theme="dark"] .ag-menu,
    [data-theme="dark"] .ag-popup,
    [data-theme="dark"] .ag-filter-panel,
    .stApp[data-theme="dark"] div[data-testid="stDataFrame"] input,
    .stApp[data-theme="dark"] div[data-testid="stDataFrame"] .stSelectbox,
    .stApp[data-theme="dark"] div[data-testid="stDataFrame"] .stMultiSelect,
    .stApp[data-theme="dark"] div[data-testid="stDataFrame"] button,
    .stApp[data-theme="dark"] .stDataFrame-toolbar,
    .stApp[data-theme="dark"] .stDataFrame-toolbar input,
    .stApp[data-theme="dark"] .stDataFrame-toolbar button,
    .stApp[data-theme="dark"] [data-testid="stDataFrameResizeHandle"],
    .stApp[data-theme="dark"] .ag-header-cell-menu-button,
    .stApp[data-theme="dark"] .ag-icon,
    .stApp[data-theme="dark"] .ag-menu,
    .stApp[data-theme="dark"] .ag-popup,
    .stApp[data-theme="dark"] .ag-filter-panel {
        background: rgba(255, 255, 255, 0.95) !important;
        color: #1f2937 !important;
        border: 1px solid rgba(255, 255, 255, 0.3) !important;
        border-radius: 6px !important;
    }

    /* FORCE TABLE STYLING - Ultra high specificity to override any existing styles */
    html body div.stApp[data-theme="dark"] div[data-testid="stDataFrame"],
    html body div.stApp div[data-testid="stDataFrame"],
    html body div[data-testid="stDataFrame"],
    div[data-testid="stDataFrame"] {
        background: linear-gradient(135deg, rgba(59, 130, 246, 0.25), rgba(147, 51, 234, 0.25)) !important;
        border: 1px solid rgba(255, 255, 255, 0.3) !important;
        border-radius: 12px !important;
        color: rgba(255, 255, 255, 0.95) !important;
        overflow: visible !important;
        position: relative !important;
    }

    /* Force all nested elements to inherit the blue theme */
    html body div.stApp[data-theme="dark"] div[data-testid="stDataFrame"] *,
    html body div.stApp div[data-testid="stDataFrame"] *,
    html body div[data-testid="stDataFrame"] *,
    div[data-testid="stDataFrame"] * {
        background: rgba(59, 130, 246, 0.15) !important;
        color: rgba(255, 255, 255, 0.95) !important;
        border-color: rgba(255, 255, 255, 0.2) !important;
    }

    /* Media query override for absolute certainty */
    @media (prefers-color-scheme: dark) {
        html body div[data-testid="stDataFrame"],
        div[data-testid="stDataFrame"] {
            background: linear-gradient(135deg, rgba(59, 130, 246, 0.25), rgba(147, 51, 234, 0.25)) !important;
            border: 1px solid rgba(255, 255, 255, 0.3) !important;
        }
        
        html body div[data-testid="stDataFrame"] *,
        div[data-testid="stDataFrame"] * {
            background: rgba(59, 130, 246, 0.15) !important;
            color: rgba(255, 255, 255, 0.95) !important;
        }
    }

    /* Last resort universal override for all tables */
    * [data-testid="stDataFrame"] {
        background: linear-gradient(135deg, rgba(59, 130, 246, 0.25), rgba(147, 51, 234, 0.25)) !important;
    }
    
    * [data-testid="stDataFrame"] * {
        background: rgba(59, 130, 246, 0.15) !important;
        color: rgba(255, 255, 255, 0.95) !important;
    }

    /* FORCE BUTTON STYLING - Ultra high specificity for Refresh button */
    html body div.stApp[data-theme="dark"] button,
    html body div.stApp button,
    html body button,
    button,
    [data-testid="stButton"] button,
    div[data-testid="stButton"] > button {
        background: linear-gradient(135deg, rgba(59, 130, 246, 0.3), rgba(147, 51, 234, 0.3)) !important;
        border: 1px solid rgba(255, 255, 255, 0.3) !important;
        border-radius: 8px !important;
        color: rgba(255, 255, 255, 0.95) !important;
        padding: 0.5rem 1rem !important;
        transition: all 0.3s ease !important;
    }

    /* Button hover effects */
    html body div.stApp[data-theme="dark"] button:hover,
    html body div.stApp button:hover,
    html body button:hover,
    button:hover,
    [data-testid="stButton"] button:hover,
    div[data-testid="stButton"] > button:hover {
        background: linear-gradient(135deg, rgba(59, 130, 246, 0.4), rgba(147, 51, 234, 0.4)) !important;
        border: 1px solid rgba(255, 255, 255, 0.4) !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3) !important;
    }

    /* Media query override for buttons */
    @media (prefers-color-scheme: dark) {
        html body button,
        button,
        [data-testid="stButton"] button,
        div[data-testid="stButton"] > button {
            background: linear-gradient(135deg, rgba(59, 130, 246, 0.3), rgba(147, 51, 234, 0.3)) !important;
            border: 1px solid rgba(255, 255, 255, 0.3) !important;
            color: rgba(255, 255, 255, 0.95) !important;
        }
        
        html body button:hover,
        button:hover,
        [data-testid="stButton"] button:hover,
        div[data-testid="stButton"] > button:hover {
            background: linear-gradient(135deg, rgba(59, 130, 246, 0.4), rgba(147, 51, 234, 0.4)) !important;
            border: 1px solid rgba(255, 255, 255, 0.4) !important;
        }
    }

    /* TAB STYLING - Consistent blue/dark theme for all tabs */
    
    /* Tab container styling */
    div[data-baseweb="tab-list"],
    .stTabs [data-baseweb="tab-list"] {
        background: linear-gradient(135deg, rgba(59, 130, 246, 0.15), rgba(147, 51, 234, 0.15)) !important;
        border-radius: 12px !important;
        padding: 4px !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        backdrop-filter: blur(10px) !important;
        -webkit-backdrop-filter: blur(10px) !important;
    }

    /* Individual tab buttons - consistent styling */
    button[data-baseweb="tab"],
    .stTabs button[data-baseweb="tab"] {
        background: linear-gradient(135deg, rgba(59, 130, 246, 0.25), rgba(147, 51, 234, 0.25)) !important;
        color: rgba(255, 255, 255, 0.85) !important;
        border: 1px solid rgba(255, 255, 255, 0.15) !important;
        border-radius: 8px !important;
        padding: 8px 16px !important;
        margin: 2px !important;
        font-weight: 500 !important;
        transition: all 0.3s ease !important;
        backdrop-filter: blur(5px) !important;
        -webkit-backdrop-filter: blur(5px) !important;
    }

    /* Active tab styling */
    button[data-baseweb="tab"][aria-selected="true"],
    .stTabs button[data-baseweb="tab"][aria-selected="true"] {
        background: linear-gradient(135deg, rgba(59, 130, 246, 0.6), rgba(147, 51, 234, 0.6)) !important;
        color: rgba(255, 255, 255, 0.95) !important;
        border: 1px solid rgba(255, 255, 255, 0.4) !important;
        font-weight: 600 !important;
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3) !important;
        transform: translateY(-1px) !important;
    }

    /* Tab hover effects */
    button[data-baseweb="tab"]:hover,
    .stTabs button[data-baseweb="tab"]:hover {
        background: linear-gradient(135deg, rgba(59, 130, 246, 0.4), rgba(147, 51, 234, 0.4)) !important;
        color: rgba(255, 255, 255, 0.95) !important;
        border: 1px solid rgba(255, 255, 255, 0.3) !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 2px 8px rgba(59, 130, 246, 0.2) !important;
    }

    /* Tab content panels */
    div[data-baseweb="tab-panel"],
    .stTabs div[data-baseweb="tab-panel"] {
        background: transparent !important;
        padding: 1rem 0 !important;
        border: none !important;
    }

    /* Force consistent tab styling - ultra high specificity */
    html body div.stApp div[data-baseweb="tab-list"],
    html body div.stApp button[data-baseweb="tab"],
    html body div[data-baseweb="tab-list"],
    html body button[data-baseweb="tab"] {
        background: linear-gradient(135deg, rgba(59, 130, 246, 0.25), rgba(147, 51, 234, 0.25)) !important;
        color: rgba(255, 255, 255, 0.85) !important;
        border: 1px solid rgba(255, 255, 255, 0.15) !important;
    }

    /* Active tab - ultra high specificity */
    html body div.stApp button[data-baseweb="tab"][aria-selected="true"],
    html body button[data-baseweb="tab"][aria-selected="true"] {
        background: linear-gradient(135deg, rgba(59, 130, 246, 0.6), rgba(147, 51, 234, 0.6)) !important;
        color: rgba(255, 255, 255, 0.95) !important;
        border: 1px solid rgba(255, 255, 255, 0.4) !important;
    }

    /* Dark mode tab styling */
    @media (prefers-color-scheme: dark) {
        div[data-baseweb="tab-list"],
        .stTabs [data-baseweb="tab-list"] {
            background: linear-gradient(135deg, rgba(59, 130, 246, 0.2), rgba(147, 51, 234, 0.2)) !important;
            border: 1px solid rgba(255, 255, 255, 0.15) !important;
        }

        button[data-baseweb="tab"],
        .stTabs button[data-baseweb="tab"] {
            background: linear-gradient(135deg, rgba(59, 130, 246, 0.3), rgba(147, 51, 234, 0.3)) !important;
            color: rgba(255, 255, 255, 0.9) !important;
            border: 1px solid rgba(255, 255, 255, 0.2) !important;
        }

        button[data-baseweb="tab"][aria-selected="true"],
        .stTabs button[data-baseweb="tab"][aria-selected="true"] {
            background: linear-gradient(135deg, rgba(59, 130, 246, 0.7), rgba(147, 51, 234, 0.7)) !important;
            color: rgba(255, 255, 255, 0.98) !important;
            border: 1px solid rgba(255, 255, 255, 0.5) !important;
        }
    }

    /* Streamlit dark theme support for tabs */
    [data-theme="dark"] div[data-baseweb="tab-list"],
    [data-theme="dark"] button[data-baseweb="tab"],
    .stApp[data-theme="dark"] div[data-baseweb="tab-list"],
    .stApp[data-theme="dark"] button[data-baseweb="tab"] {
        background: linear-gradient(135deg, rgba(59, 130, 246, 0.3), rgba(147, 51, 234, 0.3)) !important;
        color: rgba(255, 255, 255, 0.9) !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
    }

    [data-theme="dark"] button[data-baseweb="tab"][aria-selected="true"],
    .stApp[data-theme="dark"] button[data-baseweb="tab"][aria-selected="true"] {
        background: linear-gradient(135deg, rgba(59, 130, 246, 0.7), rgba(147, 51, 234, 0.7)) !important;
        color: rgba(255, 255, 255, 0.98) !important;
        border: 1px solid rgba(255, 255, 255, 0.5) !important;
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
