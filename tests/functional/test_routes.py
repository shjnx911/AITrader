"""
Functional tests for the routes of the AITradeStrategist application.
"""
import json
import pytest
from datetime import datetime


def test_index_route(client):
    """Test the index route."""
    response = client.get('/')
    
    # The index route should redirect to the dashboard
    assert response.status_code == 302
    assert response.location.endswith('/dashboard')


def test_dashboard_route(client):
    """Test the dashboard route."""
    response = client.get('/dashboard')
    
    # The dashboard route should return a successful response
    assert response.status_code == 200
    
    # The response should contain the expected title and elements
    assert b'<title>AITradeStrategist - Dashboard</title>' in response.data
    assert b'Performance Overview' in response.data
    assert b'Recent Trades' in response.data
    assert b'Top Performing Pairs' in response.data


def test_models_route(client):
    """Test the models route."""
    response = client.get('/models')
    
    # The models route should return a successful response
    assert response.status_code == 200
    
    # The response should contain the expected title and elements
    assert b'<title>AITradeStrategist - Models</title>' in response.data
    assert b'Model Management' in response.data
    assert b'Available Models' in response.data
    assert b'Training Configuration' in response.data


def test_performance_route(client):
    """Test the performance route."""
    response = client.get('/performance')
    
    # The performance route should return a successful response
    assert response.status_code == 200
    
    # The response should contain the expected title and elements
    assert b'<title>AITradeStrategist - Performance</title>' in response.data
    assert b'Performance Analysis' in response.data
    assert b'Performance Over Time' in response.data
    assert b'Win Rate by Pair' in response.data
    assert b'Profit Distribution' in response.data


def test_settings_route(client):
    """Test the settings route."""
    response = client.get('/settings')
    
    # The settings route should return a successful response
    assert response.status_code == 200
    
    # The response should contain the expected title and elements
    assert b'<title>AITradeStrategist - Settings</title>' in response.data
    assert b'Application Settings' in response.data
    assert b'Theme Preferences' in response.data
    assert b'Language Settings' in response.data
    assert b'Freqtrade Connection' in response.data


def test_documentation_route(client):
    """Test the documentation route."""
    response = client.get('/documentation')
    
    # The documentation route should return a successful response
    assert response.status_code == 200
    
    # The response should contain the expected title and elements
    assert b'<title>AITradeStrategist - Documentation</title>' in response.data
    assert b'User Documentation' in response.data
    assert b'Getting Started' in response.data
    assert b'API Reference' in response.data


def test_backup_model_route(client):
    """Test the backup model route."""
    # Create a backup request
    backup_data = {
        'model_name': 'LightGBM-BTC-Test',
        'pair': 'BTC/USDT',
        'timeframe': '1h',
        'metrics': json.dumps({'accuracy': 0.85, 'precision': 0.82, 'recall': 0.78})
    }
    
    # Send the request
    response = client.post('/api/models/backup', data=backup_data)
    
    # The endpoint should return a successful response
    assert response.status_code == 200
    
    # The response should be JSON
    data = json.loads(response.data)
    
    # The response should indicate success
    assert 'success' in data
    assert data['success'] is True
    assert 'backup_id' in data


def test_restore_model_route(client, db_session):
    """Test the restore model route."""
    # Needs a model backup in the database to work
    # Assuming the backup_model_route test has created a backup
    
    # Get the model backups
    response = client.get('/api/models/backups')
    
    # The endpoint should return a successful response
    assert response.status_code == 200
    
    # The response should be JSON
    data = json.loads(response.data)
    
    # If there are backups, test restoring one
    if 'backups' in data and data['backups']:
        backup_id = data['backups'][0]['id']
        
        # Send the restore request
        response = client.post('/api/models/restore', data={'backup_id': backup_id})
        
        # The endpoint should return a successful response
        assert response.status_code == 200
        
        # The response should be JSON
        data = json.loads(response.data)
        
        # The response should indicate success
        assert 'success' in data
        assert data['success'] is True
        assert 'model_name' in data