import streamlit as st
import json
import os
import base64
from datetime import datetime
from config import CACHE_FILES, PROPOSALS_FILES, MEV_FILES, DARK_LOGO_PATH, LIGHT_LOGO_PATH

@st.cache_data(ttl=900)  # 15 minutes - matches backend update frequency
def load_validator_data():
    """Load validator data from cache file"""
    for cache_file in CACHE_FILES:
        if os.path.exists(cache_file):
            try:
                with open(cache_file, 'r') as f:
                    cache = json.load(f)
                return cache, cache_file
            except Exception as e:
                st.error(f"⚠ Error loading {cache_file}: {str(e)}")
    
    return None, None

@st.cache_data(ttl=900)  # 15 minutes - matches backend update frequency
def load_proposals_data():
    """Load proposals data from JSON file"""
    for proposals_file in PROPOSALS_FILES:
        if os.path.exists(proposals_file):
            try:
                with open(proposals_file, 'r') as f:
                    data = json.load(f)
                return data, proposals_file
            except Exception as e:
                st.error(f"⚠ Error loading {proposals_file}: {str(e)}")
    
    return None, None

@st.cache_data(ttl=900)  # 15 minutes
def load_missed_proposals_data():
    """Load missed proposals data from JSON file"""
    possible_paths = [
        './missed_proposals_cache.json',
        './data/missed_proposals_cache.json'
    ]
    
    for path in possible_paths:
        try:
            if os.path.exists(path):
                with open(path, 'r') as f:
                    data = json.load(f)
                return data, path
        except Exception as e:
            print(f"Error loading missed proposals data from {path}: {e}")
            continue
    
    return None, None

@st.cache_data(ttl=900)  # 15 minutes
def load_mev_analysis_data():
    """Load MEV relay analysis data for gas limit analysis"""
    for mev_file in MEV_FILES:
        if os.path.exists(mev_file):
            try:
                with open(mev_file, 'r') as f:
                    data = json.load(f)
                return data, mev_file
            except Exception as e:
                st.error(f"⚠ Error loading {mev_file}: {str(e)}")
    
    return None, None

@st.cache_data(ttl=900)  # 15 minutes
def load_sync_committee_data():
    """Load sync committee participation data from JSON file"""
    possible_paths = [
        './sync_committee_participation.json',
        './data/sync_committee_participation.json'
    ]
    
    for path in possible_paths:
        try:
            if os.path.exists(path):
                with open(path, 'r') as f:
                    data = json.load(f)
                return data, path
        except Exception as e:
            print(f"Error loading sync committee data from {path}: {e}")
            continue
    
    return None, None

@st.cache_data(ttl=1800)  # 30 minutes - exit data changes less frequently
def load_exit_data():
    """Load exit analysis data from JSON file"""
    possible_paths = [
        './dashboard_exit_data.json',
        './data/dashboard_exit_data.json'
    ]
    
    for path in possible_paths:
        try:
            if os.path.exists(path):
                with open(path, 'r') as f:
                    data = json.load(f)
                return data, path
        except Exception as e:
            print(f"Error loading exit data from {path}: {e}")
            continue
    
    return None, None

@st.cache_data(ttl=1800)  # 30 minutes - performance data changes slowly
def load_validator_performance_data():
    """Load validator performance cache data from JSON file"""
    possible_paths = [
        './validator_performance_cache.json',
        './data/validator_performance_cache.json'
    ]
    
    for path in possible_paths:
        try:
            if os.path.exists(path):
                with open(path, 'r') as f:
                    data = json.load(f)
                return data, path
        except Exception as e:
            print(f"Error loading validator performance data from {path}: {e}")
            continue
    
    return None, None

@st.cache_data(ttl=3600)  # 1 hour - ENS names rarely change
def load_ens_names():
    """Load ENS names mapping from JSON file"""
    possible_paths = [
        './manual_ens_names.json',
        './data/manual_ens_names.json'
    ]
    
    for path in possible_paths:
        try:
            if os.path.exists(path):
                with open(path, 'r') as f:
                    data = json.load(f)
                return data
        except Exception as e:
            print(f"Error loading ENS names from {path}: {e}")
            continue
    
    return {}

def get_base64_image(image_path):
    """Convert image to base64 string for embedding in HTML"""
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except Exception as e:
        st.error(f"Error loading image {image_path}: {str(e)}")
        return ""

def display_logo():
    """Display the appropriate logo based on system theme preference"""
    # Check if files exist
    dark_exists = os.path.exists(DARK_LOGO_PATH)
    light_exists = os.path.exists(LIGHT_LOGO_PATH)
    
    if dark_exists and light_exists:
        # Convert images to base64 for embedding
        dark_b64 = get_base64_image(DARK_LOGO_PATH)
        light_b64 = get_base64_image(LIGHT_LOGO_PATH)
        
        if dark_b64 and light_b64:
            # Use CSS media queries for automatic theme switching
            logo_html = f"""
            <div class="logo-container">
                <style>
                .logo-dark {{
                    display: block;
                    height: 90px;
                    width: auto;
                    cursor: pointer;
                }}
                .logo-light {{
                    display: none;
                    height: 90px;
                    width: auto;
                    cursor: pointer;
                }}
                @media (prefers-color-scheme: light) {{
                    .logo-dark {{
                        display: none;
                    }}
                    .logo-light {{
                        display: block;
                    }}
                }}
                </style>
                <a href="https://nodeset.io" target="_blank">
                    <img src="data:image/png;base64,{dark_b64}" class="logo-dark" alt="NodeSet Dark Logo">
                    <img src="data:image/png;base64,{light_b64}" class="logo-light" alt="NodeSet Light Logo">
                </a>
            </div>
            """
            st.markdown(logo_html, unsafe_allow_html=True)
        else:
            # Fallback if base64 conversion fails
            st.markdown('<a href="https://nodeset.io" target="_blank">', unsafe_allow_html=True)
            st.image(DARK_LOGO_PATH, width=306)
            st.markdown('</a>', unsafe_allow_html=True)
            
    elif dark_exists:
        st.markdown('<div class="logo-container"><a href="https://nodeset.io" target="_blank">', unsafe_allow_html=True)
        st.image(DARK_LOGO_PATH, width=204)
        st.markdown('</a></div>', unsafe_allow_html=True)
    elif light_exists:
        st.markdown('<div class="logo-container"><a href="https://nodeset.io" target="_blank">', unsafe_allow_html=True)
        st.image(LIGHT_LOGO_PATH, width=306)
        st.markdown('</a></div>', unsafe_allow_html=True)
    else:
        st.error("Logo files not found: Nodeset_dark_mode.png and Nodeset_light_mode.png")
        st.title("🔗 NodeSet Validator Monitor")
