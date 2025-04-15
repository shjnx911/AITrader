"""
Flask application configuration for FreqAI LightGBM web interface
"""
import os
import sys
from pathlib import Path
import logging

# Add parent directory to sys.path if needed
parent_dir = Path(__file__).resolve().parent.parent
if str(parent_dir) not in sys.path:
    sys.path.append(str(parent_dir))

# This app is imported into main.py, not directly run
from main import app, db

# Set up logging
logger = logging.getLogger('freqai_lightgbm.web_ui')
