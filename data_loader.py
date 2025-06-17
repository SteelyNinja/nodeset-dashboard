import json
import os
import streamlit as st
from datetime import datetime

def load_validator_data():
    """Load validator data from cache file"""
    possible_paths = [
        './nodeset_validator_tracker_cache.json',
        './data/nodeset_validator_tracker_cache.json'
    ]
    
    for path in possible_paths:
        try:
            if os.path.exists(path):
                with open(path, 'r') as f:
                    cache = json.load(f)
                return cache, path
        except Exception as e:
            print(f"Error loading cache from {path}: {e}")
            continue
    
    return None, None

def load_proposals_data():
    """Load proposals data from JSON file"""
    possible_paths = [
        './proposals.json',
        './data/proposals.json'
    ]
    
    for path in possible_paths:
        try:
            if os.path.exists(path):
                with open(path, 'r') as f:
                    data = json.load(f)
                return data, path
        except Exception as e:
            print(f"Error loading proposals data from {path}: {e}")
            continue
    
    return None, None

def load_mev_analysis_data():
    """Load MEV analysis data from JSON file"""
    possible_paths = [
        './mev_analysis_results.json',
        './data/mev_analysis_results.json'
    ]
    
    for path in possible_paths:
        try:
            if os.path.exists(path):
                with open(path, 'r') as f:
                    data = json.load(f)
                return data, path
        except Exception as e:
            print(f"Error loading MEV analysis data from {path}: {e}")
            continue
    
    return None, None

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

def display_logo():
    """Display the NodeSet logo and header"""
    st.markdown("""
    <div style="text-align: center; margin-bottom: 2rem;">
        <h1 style="color: #4A90E2; margin-bottom: 0.5rem;">🌐 NodeSet Validator Dashboard</h1>
        <p style="color: #666; font-size: 1.1rem;">Real-time monitoring and analysis of NodeSet protocol validators</p>
    </div>
    """, unsafe_allow_html=True)
