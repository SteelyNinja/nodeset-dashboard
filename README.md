# Nodeset Validator Tracker Dashboard

A Streamlit-based web dashboard for monitoring NodeSet protocol validators on Stakewise. The application provides real-time analysis of validator performance, concentration metrics, proposals data, and sync committee participation.

## Features

- **Real-time Validator Monitoring**: Track validator performance and health status
- **Concentration Analysis**: Gini coefficient calculations and distribution metrics
- **Block Proposals Tracking**: Monitor proposal success rates and missed blocks
- **Sync Committee Participation**: Analyze committee participation patterns
- **MEV Analysis**: Relay breakdown and MEV performance insights
- **Client Diversity Analysis**: Monitor client distribution and gas limit strategies
- **Performance Categorization**: Health status indicators and performance metrics

## Installation

### Quick Setup
```bash
# Clone the repository
git clone <repository-url>
cd nodeset-dashboard

# Setup and install dependencies
./deploy.sh
```

### Manual Setup
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Usage

### Running the Application
```bash
# Using the main entry point
python app.py

# Or directly with Streamlit
streamlit run app.py

# Alternative launcher
python run.py
```

The dashboard will be available at `http://localhost:8501`

## Data Requirements

The application requires these JSON data files to be present in the project directory:

- `nodeset_validator_tracker_cache.json` - Primary validator data
- `proposals.json` - Block proposals data
- `sync_committee_participation.json` - Sync committee data
- `missed_proposals_cache.json` - Missed proposals tracking
- `mev_analysis_results.json` - MEV analysis data

## Architecture

### Project Structure
```
nodeset-dashboard/
├── app.py                 # Entry point with error handling and dependency checks
├── dashboard.py           # Main application logic and tab organization (2135 lines)
├── config.py              # Configuration, constants, and CSS styling
├── data_loader.py         # Data loading and caching functions (@st.cache_data)
├── utils.py               # Utility functions for formatting and calculations
├── analysis.py            # Analysis and metric calculation functions
├── charts.py              # Chart and visualization creation functions (Plotly)
├── tables.py              # Table creation and data formatting functions
├── components.py          # UI components and status displays
├── deploy.sh              # Setup script for dependencies and virtual environment
├── requirements.txt       # Python dependencies
└── README.md              # This file
```

### Data Flow
1. **Data Loading**: `data_loader.py` loads and caches JSON data files
2. **Analysis**: `analysis.py` processes raw data into metrics
3. **Visualization**: `charts.py` and `tables.py` create visual representations
4. **Assembly**: `dashboard.py` orchestrates components into tabs
5. **UI Components**: `components.py` provides status displays

### Caching Strategy
- All data loading functions use `@st.cache_data(ttl=300)` for 5-minute cache TTL
- Memory usage monitoring with `psutil` (1GB Streamlit limit)
- Automatic cache invalidation through refresh buttons

## Dashboard Tabs

- **Overview**: Concentration metrics and validator distribution
- **Operator Performance**: Individual operator analysis and health status
- **Block Proposals**: Proposal tracking and success rates
- **Sync Committee**: Committee participation analysis
- **MEV Analysis**: Relay breakdown and MEV performance

## Dependencies

Key dependencies include:
- `streamlit` - Web application framework
- `plotly` - Interactive charts and visualizations
- `pandas` - Data manipulation and analysis
- `psutil` - System and memory monitoring

See `requirements.txt` for complete dependency list.

## Contributing

Please reach out first before contributing to ensure the latest working code is uploaded to GitHub and to discuss requirements.

## Error Handling

The application includes:
- Graceful degradation when data files are missing
- Try-catch blocks with user-friendly error messages
- Fallback paths for different data file locations
- Memory usage monitoring and warnings

