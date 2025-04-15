"""
Integration tests for the Freqtrade integration of the AITradeStrategist application.
"""
import os
import json
import pytest
from unittest.mock import patch, MagicMock
import pandas as pd

# Import the Freqtrade integration components
try:
    from freqtrade_integration.freqtrade_db_connector import FreqtradeDBConnector, AITradeStrategistDBConnector
    IMPORTS_AVAILABLE = True
except ImportError:
    IMPORTS_AVAILABLE = False


# Skip tests if imports are not available
pytestmark = pytest.mark.skipif(not IMPORTS_AVAILABLE, reason="Freqtrade integration components not available")


@patch('freqtrade_integration.freqtrade_db_connector.create_engine')
def test_freqtrade_db_connector_init(mock_create_engine):
    """Test initializing the FreqtradeDBConnector."""
    # Set up the mock
    mock_engine = MagicMock()
    mock_create_engine.return_value = mock_engine
    
    # Create a FreqtradeDBConnector with a database URL
    connector = FreqtradeDBConnector(db_url='postgresql://user:pass@localhost:5432/freqtrade')
    
    # Check that the connector was created
    assert connector is not None
    assert connector.db_url == 'postgresql://user:pass@localhost:5432/freqtrade'
    assert connector.sqlite_path is None
    
    # Check that create_engine was called with the database URL
    mock_create_engine.assert_called_once_with('postgresql://user:pass@localhost:5432/freqtrade')


@patch('freqtrade_integration.freqtrade_db_connector.create_engine')
def test_freqtrade_db_connector_init_sqlite(mock_create_engine):
    """Test initializing the FreqtradeDBConnector with an SQLite path."""
    # Set up the mock
    mock_engine = MagicMock()
    mock_create_engine.return_value = mock_engine
    
    # Create a FreqtradeDBConnector with an SQLite path
    connector = FreqtradeDBConnector(sqlite_path='/path/to/freqtrade.sqlite')
    
    # Check that the connector was created
    assert connector is not None
    assert connector.db_url is None
    assert connector.sqlite_path == '/path/to/freqtrade.sqlite'
    
    # Check that create_engine was called with the SQLite path
    mock_create_engine.assert_called_once_with('sqlite:////path/to/freqtrade.sqlite')


@patch('freqtrade_integration.freqtrade_db_connector.create_engine')
def test_freqtrade_db_connector_connect(mock_create_engine):
    """Test connecting to the Freqtrade database."""
    # Set up the mock
    mock_engine = MagicMock()
    mock_create_engine.return_value = mock_engine
    
    # Create a FreqtradeDBConnector
    connector = FreqtradeDBConnector(db_url='postgresql://user:pass@localhost:5432/freqtrade')
    
    # Connect to the database
    result = connector.connect()
    
    # Check that the connection was successful
    assert result is True
    
    # Check that create_engine was called with the database URL
    mock_create_engine.assert_called_once_with('postgresql://user:pass@localhost:5432/freqtrade')


@patch('freqtrade_integration.freqtrade_db_connector.create_engine')
def test_freqtrade_db_connector_connect_error(mock_create_engine):
    """Test connecting to the Freqtrade database when an error occurs."""
    # Set up the mock to raise an exception
    mock_create_engine.side_effect = Exception("Connection error")
    
    # Create a FreqtradeDBConnector
    connector = FreqtradeDBConnector(db_url='postgresql://user:pass@localhost:5432/freqtrade')
    
    # Connect to the database
    result = connector.connect()
    
    # Check that the connection failed
    assert result is False
    
    # Check that create_engine was called with the database URL
    mock_create_engine.assert_called_once_with('postgresql://user:pass@localhost:5432/freqtrade')


@patch('freqtrade_integration.freqtrade_db_connector.create_engine')
def test_freqtrade_db_connector_get_trades(mock_create_engine):
    """Test getting trades from the Freqtrade database."""
    # Set up the mock
    mock_engine = MagicMock()
    mock_create_engine.return_value = mock_engine
    
    # Create a FreqtradeDBConnector
    connector = FreqtradeDBConnector(db_url='postgresql://user:pass@localhost:5432/freqtrade')
    
    # Set up the mock connection and query result
    mock_connection = MagicMock()
    mock_engine.connect.return_value.__enter__.return_value = mock_connection
    
    # Sample trade data
    trade_data = {
        'id': [1, 2, 3],
        'pair': ['BTC/USDT', 'ETH/USDT', 'ADA/USDT'],
        'open_rate': [40000.0, 2500.0, 1.2],
        'close_rate': [42000.0, 2600.0, 1.3],
        'stake_amount': [1000.0, 1000.0, 1000.0],
        'close_profit': [0.05, 0.04, 0.08],
        'open_date': ['2025-01-01 12:00:00', '2025-01-02 12:00:00', '2025-01-03 12:00:00'],
        'close_date': ['2025-01-01 18:00:00', '2025-01-02 18:00:00', '2025-01-03 18:00:00'],
        'is_open': [0, 0, 0]
    }
    mock_result = pd.DataFrame(trade_data)
    
    # Mock the pandas.read_sql function
    with patch('freqtrade_integration.freqtrade_db_connector.pd.read_sql') as mock_read_sql:
        mock_read_sql.return_value = mock_result
        
        # Connect to the database
        connector.connect()
        
        # Get the trades
        trades = connector.get_trades(limit=3)
        
        # Check that the trades were returned
        assert trades is not None
        assert len(trades) == 3
        assert trades['pair'].tolist() == ['BTC/USDT', 'ETH/USDT', 'ADA/USDT']
        assert trades['close_profit'].tolist() == [0.05, 0.04, 0.08]


@patch('freqtrade_integration.freqtrade_db_connector.create_engine')
def test_freqtrade_db_connector_get_pairs(mock_create_engine):
    """Test getting pairs from the Freqtrade database."""
    # Set up the mock
    mock_engine = MagicMock()
    mock_create_engine.return_value = mock_engine
    
    # Create a FreqtradeDBConnector
    connector = FreqtradeDBConnector(db_url='postgresql://user:pass@localhost:5432/freqtrade')
    
    # Set up the mock connection and query result
    mock_connection = MagicMock()
    mock_engine.connect.return_value.__enter__.return_value = mock_connection
    
    # Sample pair data
    pair_data = {
        'pair': ['BTC/USDT', 'ETH/USDT', 'ADA/USDT', 'SOL/USDT', 'DOT/USDT']
    }
    mock_result = pd.DataFrame(pair_data)
    
    # Mock the pandas.read_sql function
    with patch('freqtrade_integration.freqtrade_db_connector.pd.read_sql') as mock_read_sql:
        mock_read_sql.return_value = mock_result
        
        # Connect to the database
        connector.connect()
        
        # Get the pairs
        pairs = connector.get_pairs()
        
        # Check that the pairs were returned
        assert pairs is not None
        assert len(pairs) == 5
        assert pairs == ['BTC/USDT', 'ETH/USDT', 'ADA/USDT', 'SOL/USDT', 'DOT/USDT']


@patch('freqtrade_integration.freqtrade_db_connector.create_engine')
def test_ai_trade_strategist_db_connector_init(mock_create_engine):
    """Test initializing the AITradeStrategistDBConnector."""
    # Set up the mock
    mock_engine = MagicMock()
    mock_create_engine.return_value = mock_engine
    
    # Create an AITradeStrategistDBConnector with a database URL
    connector = AITradeStrategistDBConnector(db_url='postgresql://user:pass@localhost:5432/aitradestrategist')
    
    # Check that the connector was created
    assert connector is not None
    assert connector.db_url == 'postgresql://user:pass@localhost:5432/aitradestrategist'
    
    # Check that create_engine was called with the database URL
    mock_create_engine.assert_called_once_with('postgresql://user:pass@localhost:5432/aitradestrategist')


@patch('freqtrade_integration.freqtrade_db_connector.create_engine')
def test_ai_trade_strategist_db_connector_connect(mock_create_engine):
    """Test connecting to the AITradeStrategist database."""
    # Set up the mock
    mock_engine = MagicMock()
    mock_create_engine.return_value = mock_engine
    
    # Create an AITradeStrategistDBConnector
    connector = AITradeStrategistDBConnector(db_url='postgresql://user:pass@localhost:5432/aitradestrategist')
    
    # Connect to the database
    result = connector.connect()
    
    # Check that the connection was successful
    assert result is True
    
    # Check that create_engine was called with the database URL
    mock_create_engine.assert_called_once_with('postgresql://user:pass@localhost:5432/aitradestrategist')


@patch('freqtrade_integration.freqtrade_db_connector.create_engine')
def test_ai_trade_strategist_db_connector_import_trading_pairs(mock_create_engine):
    """Test importing trading pairs into the AITradeStrategist database."""
    # Set up the mock
    mock_engine = MagicMock()
    mock_create_engine.return_value = mock_engine
    
    # Create an AITradeStrategistDBConnector
    connector = AITradeStrategistDBConnector(db_url='postgresql://user:pass@localhost:5432/aitradestrategist')
    
    # Connect to the database
    connector.connect()
    
    # Sample pairs
    pairs = ['BTC/USDT', 'ETH/USDT', 'ADA/USDT', 'SOL/USDT', 'DOT/USDT']
    
    # Import the pairs
    result = connector.import_trading_pairs(pairs)
    
    # Check that the import was successful
    assert result is True


@patch('freqtrade_integration.freqtrade_db_connector.create_engine')
def test_ai_trade_strategist_db_connector_import_trading_metrics(mock_create_engine):
    """Test importing trading metrics into the AITradeStrategist database."""
    # Set up the mock
    mock_engine = MagicMock()
    mock_create_engine.return_value = mock_engine
    
    # Create an AITradeStrategistDBConnector
    connector = AITradeStrategistDBConnector(db_url='postgresql://user:pass@localhost:5432/aitradestrategist')
    
    # Connect to the database
    connector.connect()
    
    # Sample metrics data
    metrics_data = {
        'pair': ['BTC/USDT', 'ETH/USDT', 'ADA/USDT'],
        'total_trades': [150, 120, 80],
        'win_trades': [95, 72, 45],
        'loss_trades': [55, 48, 35],
        'profit_percent': [15.8, 12.5, 10.2],
        'profit_abs': [1580.25, 1250.75, 1020.50]
    }
    metrics_df = pd.DataFrame(metrics_data)
    
    # Import the metrics
    result = connector.import_trading_metrics(metrics_df)
    
    # Check that the import was successful
    assert result is True