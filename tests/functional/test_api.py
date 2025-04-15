"""
Functional tests for the API endpoints of the AITradeStrategist application.
"""
import json
import pytest
from datetime import datetime
from unittest.mock import patch


def test_api_stats_summary_structure(client):
    """Test the structure of the API stats summary endpoint response."""
    response = client.get('/api/stats/summary')
    
    # The endpoint should return a successful response
    assert response.status_code == 200
    
    # The response should be JSON
    data = json.loads(response.data)
    
    # The response should contain specific keys
    expected_keys = [
        'total_trades', 'win_trades', 'loss_trades',
        'win_rate', 'profit_percent', 'profit_abs'
    ]
    
    for key in expected_keys:
        assert key in data, f"Expected key '{key}' not found in API response"


def test_api_recent_trades_structure(client):
    """Test the structure of the API recent trades endpoint response."""
    response = client.get('/api/recent_trades')
    
    # The endpoint should return a successful response
    assert response.status_code == 200
    
    # The response should be JSON
    data = json.loads(response.data)
    
    # The response should contain the 'trades' key
    assert 'trades' in data, "Expected key 'trades' not found in API response"
    
    # If there are trades, check the structure of each trade
    if data['trades']:
        trade = data['trades'][0]
        expected_keys = [
            'id', 'pair', 'type', 'open_rate', 'close_rate',
            'profit', 'profit_percent', 'open_date', 'close_date'
        ]
        
        for key in expected_keys:
            assert key in trade, f"Expected key '{key}' not found in trade data"


def test_api_pairs_performance_structure(client):
    """Test the structure of the API pairs performance endpoint response."""
    response = client.get('/api/pairs/performance')
    
    # The endpoint should return a successful response
    assert response.status_code == 200
    
    # The response should be JSON
    data = json.loads(response.data)
    
    # The response should contain the 'pairs' key
    assert 'pairs' in data, "Expected key 'pairs' not found in API response"
    
    # If there are pairs, check the structure of each pair
    if data['pairs']:
        pair = data['pairs'][0]
        expected_keys = [
            'pair', 'profit_percent', 'profit_abs',
            'total_trades', 'win_rate'
        ]
        
        for key in expected_keys:
            assert key in pair, f"Expected key '{key}' not found in pair data"


@patch('main.gpu_utils.check_amd_gpu_support')
def test_api_gpu_status_with_gpu(mock_gpu_support, client):
    """Test the API GPU status endpoint when a GPU is available."""
    # Mock the GPU support check to return True
    mock_gpu_support.return_value = True
    
    # Call the API endpoint
    response = client.get('/api/gpu_status')
    
    # The endpoint should return a successful response
    assert response.status_code == 200
    
    # The response should be JSON
    data = json.loads(response.data)
    
    # The response should indicate that a GPU is available
    assert data['gpu_available'] is True
    assert "AMD" in data['gpu_type']
    assert data['acceleration'] == "DirectML"


@patch('main.gpu_utils.check_amd_gpu_support')
def test_api_gpu_status_without_gpu(mock_gpu_support, client):
    """Test the API GPU status endpoint when no GPU is available."""
    # Mock the GPU support check to return False
    mock_gpu_support.return_value = False
    
    # Call the API endpoint
    response = client.get('/api/gpu_status')
    
    # The endpoint should return a successful response
    assert response.status_code == 200
    
    # The response should be JSON
    data = json.loads(response.data)
    
    # The response should indicate that no GPU is available
    assert data['gpu_available'] is False
    assert data['gpu_type'] == "CPU Only"
    assert data['acceleration'] == "None"


@patch('main.FreqtradeAPI')
def test_api_freqtrade_status_connected(mock_freqtrade_api, client):
    """Test the API Freqtrade status endpoint when Freqtrade is connected."""
    # Mock the Freqtrade API to return a successful status
    mock_api_instance = mock_freqtrade_api.return_value
    mock_api_instance.get_status.return_value = {
        'version': '2023.4',
        'status': 'running',
        'running_mode': 'dry_run'
    }
    
    # Call the API endpoint
    response = client.get('/api/freqtrade/status')
    
    # The endpoint should return a successful response
    assert response.status_code == 200
    
    # The response should be JSON
    data = json.loads(response.data)
    
    # The response should indicate that Freqtrade is connected
    assert 'error' not in data
    assert 'version' in data
    assert 'status' in data
    assert data['status'] == 'running'


@patch('main.FreqtradeAPI')
def test_api_freqtrade_status_disconnected(mock_freqtrade_api, client):
    """Test the API Freqtrade status endpoint when Freqtrade is disconnected."""
    # Mock the Freqtrade API to raise an exception
    mock_api_instance = mock_freqtrade_api.return_value
    mock_api_instance.get_status.side_effect = Exception("Connection refused")
    
    # Call the API endpoint
    response = client.get('/api/freqtrade/status')
    
    # The endpoint should return a successful response
    assert response.status_code == 200
    
    # The response should be JSON
    data = json.loads(response.data)
    
    # The response should indicate that Freqtrade is disconnected
    assert 'error' in data
    assert data['error'] == 'Freqtrade API connection failed'