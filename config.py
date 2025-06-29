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
    /* ===== CSS VARIABLES - COLOR SYSTEM ===== */
    :root {
        /* Primary Brand Colors */
        --primary-blue: #3b82f6;
        --primary-purple: #9333ea;
        --primary-gradient: linear-gradient(135deg, var(--primary-blue), var(--primary-purple));
        
        /* Semantic Status Colors */
        --success-color: #10b981;
        --success-light: #d1fae5;
        --success-dark: #047857;
        
        --warning-color: #f59e0b;
        --warning-light: #fef3c7;
        --warning-dark: #d97706;
        
        --danger-color: #ef4444;
        --danger-light: #fee2e2;
        --danger-dark: #dc2626;
        
        --info-color: #3b82f6;
        --info-light: #dbeafe;
        --info-dark: #1d4ed8;
        
        /* Neutral Colors */
        --neutral-50: #f9fafb;
        --neutral-100: #f3f4f6;
        --neutral-200: #e5e7eb;
        --neutral-300: #d1d5db;
        --neutral-400: #9ca3af;
        --neutral-500: #6b7280;
        --neutral-600: #4b5563;
        --neutral-700: #374151;
        --neutral-800: #1f2937;
        --neutral-900: #111827;
        
        /* Typography Scale */
        --text-xs: 0.75rem;     /* 12px */
        --text-sm: 0.875rem;    /* 14px */
        --text-base: 1rem;      /* 16px */
        --text-lg: 1.125rem;    /* 18px */
        --text-xl: 1.25rem;     /* 20px */
        --text-2xl: 1.5rem;     /* 24px */
        --text-3xl: 1.875rem;   /* 30px */
        --text-4xl: 2.25rem;    /* 36px */
        --text-5xl: 3rem;       /* 48px */
        
        /* Spacing Scale */
        --space-1: 0.25rem;     /* 4px */
        --space-2: 0.5rem;      /* 8px */
        --space-3: 0.75rem;     /* 12px */
        --space-4: 1rem;        /* 16px */
        --space-5: 1.25rem;     /* 20px */
        --space-6: 1.5rem;      /* 24px */
        --space-8: 2rem;        /* 32px */
        --space-10: 2.5rem;     /* 40px */
        --space-12: 3rem;       /* 48px */
        --space-16: 4rem;       /* 64px */
        
        /* Border Radius */
        --radius-sm: 0.375rem;   /* 6px */
        --radius-md: 0.5rem;     /* 8px */
        --radius-lg: 0.75rem;    /* 12px */
        --radius-xl: 1rem;       /* 16px */
        --radius-2xl: 1.5rem;    /* 24px */
        
        /* Shadows */
        --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
        --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
        --shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
    }

    /* ===== TYPOGRAPHY HIERARCHY ===== */
    
    /* Main Dashboard Title */
    h1 {
        font-size: var(--text-4xl) !important;
        font-weight: 800 !important;
        color: var(--neutral-900) !important;
        margin-bottom: var(--space-8) !important;
        line-height: 1.1 !important;
        letter-spacing: -0.025em !important;
    }
    
    /* Section Headers */
    h2 {
        font-size: var(--text-2xl) !important;
        font-weight: 700 !important;
        color: var(--neutral-800) !important;
        margin: var(--space-8) 0 var(--space-4) 0 !important;
        line-height: 1.2 !important;
    }
    
    /* Subsection Headers */
    h3 {
        font-size: var(--text-xl) !important;
        font-weight: 600 !important;
        color: var(--neutral-700) !important;
        margin: var(--space-6) 0 var(--space-3) 0 !important;
        line-height: 1.3 !important;
    }
    
    /* Card/Component Titles */
    h4 {
        font-size: var(--text-lg) !important;
        font-weight: 600 !important;
        color: var(--neutral-700) !important;
        margin: var(--space-4) 0 var(--space-2) 0 !important;
    }
    
    /* Body Text */
    p, .stMarkdown p {
        font-size: var(--text-base) !important;
        line-height: 1.6 !important;
        color: var(--neutral-600) !important;
        margin-bottom: var(--space-4) !important;
    }
    
    /* Small Text */
    .text-sm {
        font-size: var(--text-sm) !important;
        color: var(--neutral-500) !important;
    }
    
    .text-xs {
        font-size: var(--text-xs) !important;
        color: var(--neutral-400) !important;
    }

    /* ===== STATUS COLORS ===== */
    .status-success, .status-good { 
        color: var(--success-color) !important; 
        font-weight: 600 !important;
    }
    .status-warning { 
        color: var(--warning-color) !important; 
        font-weight: 600 !important;
    }
    .status-danger, .status-error { 
        color: var(--danger-color) !important; 
        font-weight: 600 !important;
    }
    .status-info { 
        color: var(--info-color) !important; 
        font-weight: 600 !important;
    }

    /* ===== LEGACY COMPATIBILITY ===== */
    .metric-container {
        background: var(--primary-gradient);
        padding: var(--space-4);
        border-radius: var(--radius-lg);
        color: white;
        margin: var(--space-2) 0;
        text-align: center;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
    }

    .big-font {
        font-size: var(--text-2xl) !important;
        font-weight: 700 !important;
    }

    div[data-testid="metric-container"] {
        background-color: #f8f9fa;
        border: 1px solid #dee2e6;
        padding: 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 0.125rem 0.25rem rgba(0, 0, 0, 0.075);
        text-align: center !important;
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
        justify-content: center !important;
    }

    /* Ensure all text within metric containers is centered */
    div[data-testid="metric-container"] *,
    div[data-testid="metric-container"] div,
    div[data-testid="metric-container"] span,
    div[data-testid="metric-container"] p {
        text-align: center !important;
        justify-content: center !important;
        align-items: center !important;
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

    /* ===== RESPONSIVE DESIGN ===== */
    @media (max-width: 768px) {
        :root {
            /* Smaller typography scale for mobile */
            --text-4xl: 2rem;      /* 32px instead of 36px */
            --text-3xl: 1.5rem;    /* 24px instead of 30px */
            --text-2xl: 1.25rem;   /* 20px instead of 24px */
        }
        
        .main .block-container {
            padding-left: var(--space-2);
            padding-right: var(--space-2);
        }

        div[data-testid="metric-container"] {
            padding: var(--space-2);
            margin: var(--space-1) 0;
        }

        h1 {
            font-size: var(--text-3xl) !important;
            margin-bottom: var(--space-6) !important;
        }
        
        h2 {
            font-size: var(--text-xl) !important;
            margin: var(--space-6) 0 var(--space-3) 0 !important;
        }
        
        h3 {
            font-size: var(--text-lg) !important;
            margin: var(--space-4) 0 var(--space-2) 0 !important;
        }

        .metric-container {
            padding: var(--space-2);
            margin: var(--space-1) 0;
        }

        .logo-container img {
            max-height: 120px;
        }
        
        /* Mobile glass cards */
        .glass-card {
            padding: var(--space-4);
            margin: var(--space-2);
            border-radius: var(--radius-xl);
        }
        
        .glass-card-value {
            font-size: var(--text-2xl);
            text-align: left;
        }
        
        .glass-card-title {
            font-size: var(--text-xs);
            text-align: left;
        }
        
        .glass-card-caption {
            text-align: left;
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

    /* Dark mode background - subtle blue improvement from original */
    @media (prefers-color-scheme: dark) {
        .stApp {
            background: linear-gradient(135deg, #11182e 0%, #1f2a3f 50%, #11182e 100%);
        }
    }

    /* Streamlit dark theme support - subtle blue improvement */
    [data-theme="dark"] .stApp,
    .stApp[data-theme="dark"] {
        background: linear-gradient(135deg, #11182e 0%, #1f2a3f 50%, #11182e 100%) !important;
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
            background: linear-gradient(135deg, rgba(96, 165, 250, 0.2), rgba(167, 139, 250, 0.2)) !important;
            backdrop-filter: blur(15px) !important;
            -webkit-backdrop-filter: blur(15px) !important;
            border: 1px solid rgba(255, 255, 255, 0.25) !important;
            border-radius: 12px !important;
            overflow: visible !important;
            position: relative !important;
        }

        /* Dark mode mobile dataframe improvements */
        @media (max-width: 768px) {
            div[data-testid="stDataFrame"],
            div[data-testid="stTable"] {
                background: linear-gradient(135deg, rgba(96, 165, 250, 0.3), rgba(167, 139, 250, 0.3)) !important;
                backdrop-filter: blur(10px) !important;
                -webkit-backdrop-filter: blur(10px) !important;
                border: 2px solid rgba(255, 255, 255, 0.35) !important;
                box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2) !important;
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
            background: linear-gradient(135deg, rgba(96, 165, 250, 0.18), rgba(167, 139, 250, 0.18)) !important;
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
        background: linear-gradient(135deg, rgba(96, 165, 250, 0.2), rgba(167, 139, 250, 0.2)) !important;
        backdrop-filter: blur(15px) !important;
        -webkit-backdrop-filter: blur(15px) !important;
        border: 1px solid rgba(255, 255, 255, 0.25) !important;
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
        background: linear-gradient(135deg, rgba(96, 165, 250, 0.18), rgba(167, 139, 250, 0.18)) !important;
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

    /* ===== GLASS-MORPHISM CARDS ===== */
    .glass-card {
        background: linear-gradient(135deg, 
            rgba(var(--primary-blue-rgb, 59, 130, 246), 0.08), 
            rgba(var(--primary-purple-rgb, 147, 51, 234), 0.08));
        backdrop-filter: blur(15px);
        -webkit-backdrop-filter: blur(15px);
        border: 1px solid var(--neutral-200);
        border-radius: var(--radius-2xl);
        padding: var(--space-6);
        margin: var(--space-3);
        box-shadow: var(--shadow-lg);
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
        transform: translateY(-2px) scale(1.01);
        box-shadow: var(--shadow-xl);
        border-color: var(--neutral-300);
    }

    .glass-card-title {
        font-size: var(--text-sm);
        font-weight: 600;
        color: var(--neutral-700);
        margin-bottom: var(--space-2);
        text-transform: uppercase;
        letter-spacing: 0.05em;
        line-height: 1.4;
        text-align: left;
    }

    .glass-card-value {
        font-size: var(--text-3xl);
        font-weight: 800;
        color: var(--neutral-900);
        margin-bottom: var(--space-1);
        line-height: 1.1;
        letter-spacing: -0.025em;
        text-align: left;
    }

    .glass-card-caption {
        font-size: var(--text-xs);
        color: var(--neutral-500);
        line-height: 1.4;
        font-weight: 500;
        text-align: left;
    }

    /* ===== DARK MODE THEME ===== */
    @media (prefers-color-scheme: dark) {
        :root {
            /* Dark mode color overrides - subtle blue improvement */
            --neutral-50: #11182e;
            --neutral-100: #1f2a3f;
            --neutral-200: #334155;
            --neutral-300: #475569;
            --neutral-400: #64748b;
            --neutral-500: #94a3b8;
            --neutral-600: #cbd5e1;
            --neutral-700: #e2e8f0;
            --neutral-800: #f1f5f9;
            --neutral-900: #f8fafc;
            
            /* Lighter blue/purple theme for dark mode */
            --primary-blue: #60a5fa;      /* Lighter from #3b82f6 */
            --primary-purple: #a78bfa;    /* Lighter from #9333ea */
            --primary-gradient: linear-gradient(135deg, var(--primary-blue), var(--primary-purple));
        }
        
        /* Typography in dark mode */
        h1 { color: var(--neutral-900) !important; }
        h2 { color: var(--neutral-800) !important; }
        h3 { color: var(--neutral-700) !important; }
        h4 { color: var(--neutral-700) !important; }
        p, .stMarkdown p { color: var(--neutral-600) !important; }
        
        /* Glass cards in dark mode - enhanced effect */
        .glass-card {
            background: linear-gradient(135deg, 
                rgba(96, 165, 250, 0.12), 
                rgba(167, 139, 250, 0.12));
            backdrop-filter: blur(20px) saturate(1.4);
            -webkit-backdrop-filter: blur(20px) saturate(1.4);
            border: 1px solid rgba(255, 255, 255, 0.15);
            box-shadow: 
                0 8px 32px rgba(0, 0, 0, 0.3),
                0 1px 0 rgba(255, 255, 255, 0.1) inset,
                0 -1px 0 rgba(0, 0, 0, 0.2) inset;
        }
        
        .glass-card:hover {
            border-color: rgba(255, 255, 255, 0.25);
            background: linear-gradient(135deg, 
                rgba(96, 165, 250, 0.15), 
                rgba(167, 139, 250, 0.15));
            box-shadow: 
                0 12px 40px rgba(0, 0, 0, 0.4),
                0 1px 0 rgba(255, 255, 255, 0.15) inset,
                0 -1px 0 rgba(0, 0, 0, 0.25) inset;
        }
        
        .glass-card-title {
            color: var(--neutral-600);
        }

        .glass-card-value {
            color: var(--neutral-900);
        }

        .glass-card-caption {
            color: var(--neutral-500);
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
        background: linear-gradient(135deg, rgba(96, 165, 250, 0.12), rgba(167, 139, 250, 0.12)) !important;
        backdrop-filter: blur(20px) saturate(1.4) !important;
        -webkit-backdrop-filter: blur(20px) saturate(1.4) !important;
        border: 1px solid rgba(255, 255, 255, 0.15) !important;
        box-shadow: 
            0 8px 32px rgba(0, 0, 0, 0.3),
            0 1px 0 rgba(255, 255, 255, 0.1) inset,
            0 -1px 0 rgba(0, 0, 0, 0.2) inset !important;
    }

    [data-theme="dark"] .glass-card:hover,
    .stApp[data-theme="dark"] .glass-card:hover {
        border-color: rgba(255, 255, 255, 0.25) !important;
        background: linear-gradient(135deg, rgba(96, 165, 250, 0.15), rgba(167, 139, 250, 0.15)) !important;
        box-shadow: 
            0 12px 40px rgba(0, 0, 0, 0.4),
            0 1px 0 rgba(255, 255, 255, 0.15) inset,
            0 -1px 0 rgba(0, 0, 0, 0.25) inset !important;
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

    /* ===== UNIVERSAL VERTICAL CENTERING FIXES ===== */
    
    /* Streamlit button text centering - most specific selectors */
    div[data-testid="stButton"] button div,
    div[data-testid="stButton"] button span,
    div[data-testid="stButton"] button p {
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        height: 100% !important;
        line-height: 1.2 !important;
        margin: 0 !important;
        padding: 0 !important;
    }

    /* Tab button text centering - most specific selectors */
    button[data-baseweb="tab"] div,
    button[data-baseweb="tab"] span,
    button[data-baseweb="tab"] p,
    .stTabs button[data-baseweb="tab"] div,
    .stTabs button[data-baseweb="tab"] span,
    .stTabs button[data-baseweb="tab"] p {
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        height: 100% !important;
        line-height: 1.2 !important;
        margin: 0 !important;
        padding: 0 !important;
        font-size: inherit !important;
    }

    /* Override any potential text wrapping or positioning issues */
    button[data-baseweb="tab"],
    div[data-testid="stButton"] button {
        position: relative !important;
        overflow: hidden !important;
    }

    button[data-baseweb="tab"]::before,
    div[data-testid="stButton"] button::before {
        content: '' !important;
        position: absolute !important;
        top: 0 !important;
        left: 0 !important;
        right: 0 !important;
        bottom: 0 !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        pointer-events: none !important;
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
        background: linear-gradient(135deg, rgba(96, 165, 250, 0.35), rgba(167, 139, 250, 0.35)) !important;
        border: 1px solid rgba(255, 255, 255, 0.3) !important;
        border-radius: 8px !important;
        color: rgba(255, 255, 255, 0.95) !important;
        padding: 12px 16px !important;
        transition: all 0.3s ease !important;
        text-align: center !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        font-weight: 500 !important;
        min-height: 48px !important;
        height: 48px !important;
        line-height: 1.2 !important;
        vertical-align: middle !important;
        box-sizing: border-box !important;
    }

    /* Force button content vertical centering */
    html body button *,
    button *,
    [data-testid="stButton"] button *,
    div[data-testid="stButton"] > button * {
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        height: 100% !important;
        width: 100% !important;
        line-height: 1.2 !important;
        vertical-align: middle !important;
        margin: 0 !important;
        padding: 0 !important;
    }

    /* Button hover effects */
    html body div.stApp[data-theme="dark"] button:hover,
    html body div.stApp button:hover,
    html body button:hover,
    button:hover,
    [data-testid="stButton"] button:hover,
    div[data-testid="stButton"] > button:hover {
        background: linear-gradient(135deg, rgba(96, 165, 250, 0.45), rgba(167, 139, 250, 0.45)) !important;
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
            background: linear-gradient(135deg, rgba(96, 165, 250, 0.35), rgba(167, 139, 250, 0.35)) !important;
            border: 1px solid rgba(255, 255, 255, 0.3) !important;
            color: rgba(255, 255, 255, 0.95) !important;
        }
        
        html body button:hover,
        button:hover,
        [data-testid="stButton"] button:hover,
        div[data-testid="stButton"] > button:hover {
            background: linear-gradient(135deg, rgba(96, 165, 250, 0.45), rgba(167, 139, 250, 0.45)) !important;
            border: 1px solid rgba(255, 255, 255, 0.4) !important;
        }
    }

    /* TAB STYLING - Consistent blue/dark theme for all tabs */
    
    /* Tab container styling with sliding indicator */
    div[data-baseweb="tab-list"],
    .stTabs [data-baseweb="tab-list"] {
        background: linear-gradient(135deg, rgba(59, 130, 246, 0.15), rgba(147, 51, 234, 0.15)) !important;
        border-radius: 12px !important;
        padding: 4px !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        backdrop-filter: blur(10px) !important;
        -webkit-backdrop-filter: blur(10px) !important;
        justify-content: flex-start !important;
        align-items: flex-start !important;
        display: flex !important;
        flex-wrap: wrap !important;
        position: relative !important;
        overflow: hidden !important;
    }

    /* Simplified indicator - removed to avoid conflicts */
    /* Note: Sliding indicator removed to prevent Streamlit conflicts */

    /* Individual tab buttons - enhanced transitions */
    button[data-baseweb="tab"],
    .stTabs button[data-baseweb="tab"] {
        background: linear-gradient(135deg, rgba(59, 130, 246, 0.25), rgba(147, 51, 234, 0.25)) !important;
        color: rgba(255, 255, 255, 0.85) !important;
        border: 1px solid rgba(255, 255, 255, 0.15) !important;
        border-radius: 8px !important;
        padding: 12px 16px !important;
        margin: 2px !important;
        font-weight: 500 !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        backdrop-filter: blur(5px) !important;
        -webkit-backdrop-filter: blur(5px) !important;
        text-align: center !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        min-height: 48px !important;
        height: 48px !important;
        white-space: nowrap !important;
        line-height: 1.2 !important;
        vertical-align: middle !important;
        box-sizing: border-box !important;
        position: relative !important;
        overflow: hidden !important;
        transform: scale(1) !important;
    }

    /* Active tab styling with enhanced effects */
    button[data-baseweb="tab"][aria-selected="true"],
    .stTabs button[data-baseweb="tab"][aria-selected="true"] {
        background: linear-gradient(135deg, rgba(59, 130, 246, 0.6), rgba(147, 51, 234, 0.6)) !important;
        color: rgba(255, 255, 255, 0.95) !important;
        border: 1px solid rgba(255, 255, 255, 0.4) !important;
        font-weight: 600 !important;
        box-shadow: 
            0 4px 12px rgba(59, 130, 246, 0.3),
            0 2px 6px rgba(147, 51, 234, 0.2) !important;
        transform: translateY(-1px) scale(1.02) !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }

    /* Active tab styling enhanced - indicator removed for stability */

    /* Tab hover effects with smooth transitions */
    button[data-baseweb="tab"]:hover:not([aria-selected="true"]),
    .stTabs button[data-baseweb="tab"]:hover:not([aria-selected="true"]) {
        background: linear-gradient(135deg, rgba(59, 130, 246, 0.4), rgba(147, 51, 234, 0.4)) !important;
        color: rgba(255, 255, 255, 0.95) !important;
        border: 1px solid rgba(255, 255, 255, 0.3) !important;
        transform: translateY(-1px) scale(1.01) !important;
        box-shadow: 0 2px 8px rgba(59, 130, 246, 0.2) !important;
        transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }

    /* Tab content panels - simplified without interfering animations */
    div[data-baseweb="tab-panel"],
    .stTabs div[data-baseweb="tab-panel"] {
        background: transparent !important;
        padding: 1rem 0 !important;
        border: none !important;
        opacity: 1 !important;
        transform: none !important;
    }

    /* Gentle fade-in for new content only */
    div[data-baseweb="tab-panel"] {
        animation: gentleFadeIn 0.2s ease-out !important;
    }

    /* Gentle fade in animation */
    @keyframes gentleFadeIn {
        0% {
            opacity: 0.7;
        }
        100% {
            opacity: 1;
        }
    }

    /* Accessibility: Respect reduced motion preferences */
    @media (prefers-reduced-motion: reduce) {
        button[data-baseweb="tab"],
        .stTabs button[data-baseweb="tab"],
        div[data-baseweb="tab-panel"],
        .stTabs div[data-baseweb="tab-panel"],
        div[data-baseweb="tab-list"]::before,
        .stTabs [data-baseweb="tab-list"]::before {
            transition: none !important;
            animation: none !important;
            transform: none !important;
        }
        
        div[data-baseweb="tab-panel"] {
            opacity: 1 !important;
            animation: none !important;
        }
    }

    /* Force consistent tab styling - ultra high specificity */
    html body div.stApp div[data-baseweb="tab-list"],
    html body div[data-baseweb="tab-list"] {
        background: linear-gradient(135deg, rgba(59, 130, 246, 0.15), rgba(147, 51, 234, 0.15)) !important;
        justify-content: flex-start !important;
        align-items: flex-start !important;
        display: flex !important;
        flex-wrap: wrap !important;
        position: relative !important;
        overflow: hidden !important;
    }
    
    html body div.stApp button[data-baseweb="tab"],
    html body button[data-baseweb="tab"] {
        background: linear-gradient(135deg, rgba(59, 130, 246, 0.25), rgba(147, 51, 234, 0.25)) !important;
        color: rgba(255, 255, 255, 0.85) !important;
        border: 1px solid rgba(255, 255, 255, 0.15) !important;
        text-align: center !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        transform: scale(1) !important;
    }

    /* Ensure tab text is properly centered */
    html body div.stApp button[data-baseweb="tab"] *,
    html body button[data-baseweb="tab"] *,
    button[data-baseweb="tab"] *,
    .stTabs button[data-baseweb="tab"] * {
        text-align: center !important;
        justify-content: center !important;
        align-items: center !important;
        width: 100% !important;
        display: flex !important;
        height: 100% !important;
        line-height: 1.2 !important;
        vertical-align: middle !important;
    }

    /* Force tab content vertical centering */
    button[data-baseweb="tab"] > div,
    .stTabs button[data-baseweb="tab"] > div,
    button[data-baseweb="tab"] > span,
    .stTabs button[data-baseweb="tab"] > span {
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        height: 100% !important;
        width: 100% !important;
        margin: 0 !important;
        padding: 0 !important;
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
            background: linear-gradient(135deg, rgba(96, 165, 250, 0.25), rgba(167, 139, 250, 0.25)) !important;
            border: 1px solid rgba(255, 255, 255, 0.15) !important;
            justify-content: flex-start !important;
            align-items: flex-start !important;
            display: flex !important;
            flex-wrap: wrap !important;
            position: relative !important;
            overflow: hidden !important;
        }

        button[data-baseweb="tab"],
        .stTabs button[data-baseweb="tab"] {
            background: linear-gradient(135deg, rgba(96, 165, 250, 0.35), rgba(167, 139, 250, 0.35)) !important;
            color: rgba(255, 255, 255, 0.95) !important;
            border: 1px solid rgba(255, 255, 255, 0.25) !important;
        }

        button[data-baseweb="tab"][aria-selected="true"],
        .stTabs button[data-baseweb="tab"][aria-selected="true"] {
            background: linear-gradient(135deg, rgba(96, 165, 250, 0.7), rgba(167, 139, 250, 0.7)) !important;
            color: rgba(255, 255, 255, 0.98) !important;
            border: 1px solid rgba(255, 255, 255, 0.5) !important;
        }
    }

    /* Streamlit dark theme support for tabs */
    [data-theme="dark"] div[data-baseweb="tab-list"],
    .stApp[data-theme="dark"] div[data-baseweb="tab-list"] {
        background: linear-gradient(135deg, rgba(96, 165, 250, 0.25), rgba(167, 139, 250, 0.25)) !important;
        border: 1px solid rgba(255, 255, 255, 0.15) !important;
        justify-content: flex-start !important;
        align-items: flex-start !important;
        display: flex !important;
        flex-wrap: wrap !important;
    }
    
    [data-theme="dark"] button[data-baseweb="tab"],
    .stApp[data-theme="dark"] button[data-baseweb="tab"] {
        background: linear-gradient(135deg, rgba(96, 165, 250, 0.35), rgba(167, 139, 250, 0.35)) !important;
        color: rgba(255, 255, 255, 0.95) !important;
        border: 1px solid rgba(255, 255, 255, 0.25) !important;
    }

    [data-theme="dark"] button[data-baseweb="tab"][aria-selected="true"],
    .stApp[data-theme="dark"] button[data-baseweb="tab"][aria-selected="true"] {
        background: linear-gradient(135deg, rgba(96, 165, 250, 0.7), rgba(167, 139, 250, 0.7)) !important;
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

# CSS Class utilities for use in components
def get_status_class(status_type):
    """Get the appropriate CSS class for status indicators"""
    status_map = {
        'success': 'status-success',
        'good': 'status-success', 
        'warning': 'status-warning',
        'moderate': 'status-warning',
        'danger': 'status-danger',
        'error': 'status-danger',
        'info': 'status-info'
    }
    return status_map.get(status_type.lower(), 'status-info')

def format_status_text(text, status_type):
    """Format status text with appropriate CSS class"""
    css_class = get_status_class(status_type)
    return f'<span class="{css_class}">{text}</span>'
