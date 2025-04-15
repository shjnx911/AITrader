#!/usr/bin/env python3
"""
Main entry point for the FreqAI LightGBM trading application with Freqtrade integration.
This script starts the Flask web application that connects to Freqtrade's API.
"""
import os
import sys
import logging
from pathlib import Path
from flask import Flask, jsonify, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('freqai_lightgbm')

# Add parent directory to sys.path to allow imports
sys.path.append(str(Path(__file__).parent))

# Initialize database
class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

# Import GPU utils
from utils.gpu_utils import check_amd_gpu_support

# Create Flask app instance (will be imported by web_ui)
app = Flask(__name__, 
            static_folder='web_ui/static', 
            template_folder='web_ui/templates')

# Configure app
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "freqai_lightgbm_secret_key")

# Database configuration
# If Freqtrade is using SQLite
# app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///freqtrade/tradesv3.sqlite")

# If Freqtrade is using PostgreSQL
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize database with the app
db.init_app(app)

# Định nghĩa một hàm để đăng ký routes sau khi tạo ứng dụng
def register_app_routes():
    from web_ui.routes import register_routes
    register_routes(app)

# Routes sẽ được đăng ký sau khi models đã được khai báo

# Create a redirect from root to dashboard
@app.route('/')
def index():
    return redirect(url_for('dashboard'))

# Add API endpoint for GPU information
@app.route('/api/gpu_status')
def gpu_status():
    gpu_available = check_amd_gpu_support()
    return jsonify({
        "gpu_available": gpu_available,
        "gpu_type": "AMD (DirectML)" if gpu_available else "Not detected",
        "acceleration": "Enabled" if gpu_available else "Disabled"
    })

# Create database tables
with app.app_context():
    # Import models
    from web_ui.models import ModelBackup, TrainingConfig, TradingPair, TradingMetrics
    
    # Check if tables exist already
    engine = db.get_engine()
    if not engine.dialect.has_table(engine, ModelBackup.__tablename__):
        logger.info("Creating database tables...")
        db.create_all()
        logger.info("Database tables created.")
    else:
        logger.info("Database tables already exist.")

# Freqtrade API Integration
class FreqtradeAPI:
    """Helper class for Freqtrade REST API integration"""
    
    def __init__(self, server_url="http://localhost:8080", api_key=None):
        self.server_url = server_url
        self.api_key = api_key
        
    def get_headers(self):
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers
    
    def get_status(self):
        """Get Freqtrade bot status"""
        try:
            import requests
            response = requests.get(f"{self.server_url}/api/v1/status", headers=self.get_headers())
            if response.status_code == 200:
                return response.json()
            return {"error": f"Error {response.status_code}: {response.text}"}
        except Exception as e:
            return {"error": str(e)}
    
    def get_trades(self, limit=50):
        """Get recent trades"""
        try:
            import requests
            response = requests.get(f"{self.server_url}/api/v1/trades", 
                                   params={"limit": limit},
                                   headers=self.get_headers())
            if response.status_code == 200:
                return response.json()
            return {"error": f"Error {response.status_code}: {response.text}"}
        except Exception as e:
            return {"error": str(e)}

# Add API endpoints for Freqtrade integration
@app.route('/api/freqtrade/status')
def freqtrade_status():
    api = FreqtradeAPI(
        server_url=os.environ.get("FREQTRADE_SERVER_URL", "http://localhost:8080"),
        api_key=os.environ.get("FREQTRADE_API_KEY")
    )
    return jsonify(api.get_status())

@app.route('/api/freqtrade/trades')
def freqtrade_trades():
    api = FreqtradeAPI(
        server_url=os.environ.get("FREQTRADE_SERVER_URL", "http://localhost:8080"),
        api_key=os.environ.get("FREQTRADE_API_KEY")
    )
    return jsonify(api.get_trades())

if __name__ == '__main__':
    # Check AMD GPU support
    gpu_available = check_amd_gpu_support()
    if gpu_available:
        logger.info("AMD GPU support detected. DirectML acceleration will be used.")
    else:
        logger.warning("AMD GPU support not detected. Running in CPU mode.")
    
    # Check Freqtrade connection
    api = FreqtradeAPI(
        server_url=os.environ.get("FREQTRADE_SERVER_URL", "http://localhost:8080"),
        api_key=os.environ.get("FREQTRADE_API_KEY")
    )
    
    status = api.get_status()
    if "error" in status:
        logger.warning(f"Could not connect to Freqtrade API: {status['error']}")
        logger.warning("Make sure Freqtrade is running with API enabled")
    else:
        logger.info(f"Connected to Freqtrade: {status.get('version', 'Unknown version')}")
    
    # Start the web application
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=os.environ.get("DEBUG", "False").lower() == "true")