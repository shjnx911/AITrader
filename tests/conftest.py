"""
Fixtures for testing the AITradeStrategist application.
"""
import os
import tempfile
import pytest
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from datetime import datetime

# Define a base class for the models
class Base(DeclarativeBase):
    pass


# Create a SQLAlchemy instance
db = SQLAlchemy(model_class=Base)


@pytest.fixture
def app():
    """Create and configure a Flask app for testing."""
    # Create a temporary file to use as a test database
    db_fd, db_path = tempfile.mkstemp()
    
    # Create the app
    app = Flask(__name__)
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize the database
    db.init_app(app)
    
    # Create the database tables
    with app.app_context():
        # Import the models
        from main import ModelBackup, TrainingConfig, TradingMetrics
        
        # Create the tables
        db.create_all()
    
    # Yield the app for testing
    yield app
    
    # Close and remove the temporary database
    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def client(app):
    """Create a test client for the app."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """Create a CLI test runner for the app."""
    return app.test_cli_runner()


@pytest.fixture
def db_session(app):
    """Create a database session for testing."""
    with app.app_context():
        connection = db.engine.connect()
        transaction = connection.begin()
        
        # Use a nested transaction to rollback database changes after each test
        session = db.session
        
        yield session
        
        # Rollback the transaction and close the connection
        session.close()
        transaction.rollback()
        connection.close()


@pytest.fixture
def mock_gpu_support():
    """Mock the GPU support functions for testing."""
    # This fixture can be used to mock GPU support functions
    # It doesn't actually do anything, but it's a placeholder for tests that need it
    pass


@pytest.fixture
def mock_freqtrade_api():
    """Mock the Freqtrade API for testing."""
    # This fixture can be used to mock the Freqtrade API
    # It doesn't actually do anything, but it's a placeholder for tests that need it
    pass


@pytest.fixture
def sample_model_data():
    """Sample model data for testing."""
    return {
        'model_name': 'LightGBM-Test',
        'created_date': datetime.now(),
        'pair': 'BTC/USDT',
        'timeframe': '1h',
        'backup_path': '/tmp/models/backup_test.model',
        'metrics': {'accuracy': 0.85, 'precision': 0.82, 'recall': 0.78},
        'is_active': True
    }


@pytest.fixture
def sample_training_config():
    """Sample training configuration for testing."""
    return {
        'config_name': 'Test-Config',
        'params': {
            'model_type': 'lightgbm',
            'learning_rate': 0.01,
            'max_depth': 5,
            'num_leaves': 31,
            'n_estimators': 100
        },
        'created_date': datetime.now()
    }


@pytest.fixture
def sample_trading_metrics():
    """Sample trading metrics for testing."""
    return {
        'pair': 'BTC/USDT',
        'timeframe': '1h',
        'start_date': datetime(2025, 1, 1),
        'end_date': datetime(2025, 4, 1),
        'total_trades': 150,
        'win_trades': 95,
        'loss_trades': 55,
        'profit_percent': 15.8,
        'profit_abs': 1580.25,
        'metrics_data': {
            'max_drawdown': 8.5,
            'max_drawdown_abs': 850.75,
            'best_trade': 4.2,
            'worst_trade': -3.1
        }
    }