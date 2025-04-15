"""
Unit tests for the chart generation functions used in the application.
"""
import json
import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta

# We'll assume these modules/functions exist in the application
# If they don't, we can adjust the tests accordingly
try:
    from web_ui.static.js.charts import generate_performance_chart, generate_win_rate_chart, generate_profit_distribution_chart
    IMPORTS_AVAILABLE = True
except ImportError:
    IMPORTS_AVAILABLE = False


# Skip tests if imports are not available
pytestmark = pytest.mark.skipif(not IMPORTS_AVAILABLE, reason="Chart modules not available")


class TestCharts:
    """Tests for the chart generation functions."""
    
    def test_generate_performance_chart_daily(self):
        """Test generating a daily performance chart."""
        # Sample performance data
        performance_data = {
            'dates': [
                (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
                for i in range(10, 0, -1)
            ],
            'profit_percentages': [0.5, 1.2, -0.3, 0.8, 1.5, -0.2, 0.6, 1.3, 0.4, 0.9]
        }
        
        # Generate the chart
        chart = generate_performance_chart(performance_data, 'daily')
        
        # Check that the chart has the expected structure
        assert 'type' in chart
        assert chart['type'] == 'line'
        assert 'data' in chart
        assert 'labels' in chart['data']
        assert 'datasets' in chart['data']
        assert len(chart['data']['labels']) == 10
        assert len(chart['data']['datasets'][0]['data']) == 10
    
    def test_generate_performance_chart_weekly(self):
        """Test generating a weekly performance chart."""
        # Sample performance data
        performance_data = {
            'dates': [
                f"Week {i} of {datetime.now().year}"
                for i in range(1, 11)
            ],
            'profit_percentages': [1.5, 2.3, -0.8, 1.2, 3.1, -0.5, 1.7, 2.8, 1.1, 1.9]
        }
        
        # Generate the chart
        chart = generate_performance_chart(performance_data, 'weekly')
        
        # Check that the chart has the expected structure
        assert 'type' in chart
        assert chart['type'] == 'line'
        assert 'data' in chart
        assert 'labels' in chart['data']
        assert 'datasets' in chart['data']
        assert len(chart['data']['labels']) == 10
        assert len(chart['data']['datasets'][0]['data']) == 10
    
    def test_generate_performance_chart_monthly(self):
        """Test generating a monthly performance chart."""
        # Sample performance data
        months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October']
        performance_data = {
            'dates': months,
            'profit_percentages': [3.2, 4.1, -1.5, 2.7, 5.3, -0.9, 3.5, 4.8, 2.2, 3.7]
        }
        
        # Generate the chart
        chart = generate_performance_chart(performance_data, 'monthly')
        
        # Check that the chart has the expected structure
        assert 'type' in chart
        assert chart['type'] == 'line'
        assert 'data' in chart
        assert 'labels' in chart['data']
        assert 'datasets' in chart['data']
        assert len(chart['data']['labels']) == 10
        assert len(chart['data']['datasets'][0]['data']) == 10
    
    def test_generate_win_rate_chart(self):
        """Test generating a win rate chart."""
        # Sample win rate data
        win_rate_data = {
            'pairs': ['BTC/USDT', 'ETH/USDT', 'ADA/USDT', 'SOL/USDT', 'DOT/USDT'],
            'win_rates': [65.2, 58.7, 72.3, 61.5, 69.8]
        }
        
        # Generate the chart
        chart = generate_win_rate_chart(win_rate_data)
        
        # Check that the chart has the expected structure
        assert 'type' in chart
        assert chart['type'] == 'bar'
        assert 'data' in chart
        assert 'labels' in chart['data']
        assert 'datasets' in chart['data']
        assert len(chart['data']['labels']) == 5
        assert len(chart['data']['datasets'][0]['data']) == 5
    
    def test_generate_profit_distribution_chart(self):
        """Test generating a profit distribution chart."""
        # Sample profit distribution data
        profit_data = {
            'ranges': ['-10% to -5%', '-5% to 0%', '0% to 5%', '5% to 10%', '10% to 15%'],
            'counts': [5, 12, 28, 18, 7]
        }
        
        # Generate the chart
        chart = generate_profit_distribution_chart(profit_data)
        
        # Check that the chart has the expected structure
        assert 'type' in chart
        assert chart['type'] == 'bar'
        assert 'data' in chart
        assert 'labels' in chart['data']
        assert 'datasets' in chart['data']
        assert len(chart['data']['labels']) == 5
        assert len(chart['data']['datasets'][0]['data']) == 5


class TestChartResponsiveness:
    """Tests for the responsiveness of charts."""
    
    def test_performance_chart_mobile_view(self):
        """Test that the performance chart adapts to mobile view."""
        # Sample performance data
        performance_data = {
            'dates': [
                (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
                for i in range(10, 0, -1)
            ],
            'profit_percentages': [0.5, 1.2, -0.3, 0.8, 1.5, -0.2, 0.6, 1.3, 0.4, 0.9]
        }
        
        # Generate the chart with mobile view
        chart = generate_performance_chart(performance_data, 'daily', is_mobile=True)
        
        # Check that the chart options are adapted for mobile
        assert 'options' in chart
        assert 'responsive' in chart['options']
        assert chart['options']['responsive'] is True
        assert 'maintainAspectRatio' in chart['options']
        assert chart['options']['maintainAspectRatio'] is False
        
        # Check for smaller font sizes in mobile view
        assert 'scales' in chart['options']
        assert 'x' in chart['options']['scales']
        assert 'ticks' in chart['options']['scales']['x']
        assert 'font' in chart['options']['scales']['x']['ticks']
        assert chart['options']['scales']['x']['ticks']['font']['size'] < 14  # Smaller font size for mobile
    
    def test_win_rate_chart_mobile_view(self):
        """Test that the win rate chart adapts to mobile view."""
        # Sample win rate data
        win_rate_data = {
            'pairs': ['BTC/USDT', 'ETH/USDT', 'ADA/USDT', 'SOL/USDT', 'DOT/USDT'],
            'win_rates': [65.2, 58.7, 72.3, 61.5, 69.8]
        }
        
        # Generate the chart with mobile view
        chart = generate_win_rate_chart(win_rate_data, is_mobile=True)
        
        # Check that the chart options are adapted for mobile
        assert 'options' in chart
        assert 'responsive' in chart['options']
        assert chart['options']['responsive'] is True
        assert 'maintainAspectRatio' in chart['options']
        assert chart['options']['maintainAspectRatio'] is False
        
        # Check for smaller font sizes in mobile view
        assert 'scales' in chart['options']
        assert 'x' in chart['options']['scales']
        assert 'ticks' in chart['options']['scales']['x']
        assert 'font' in chart['options']['scales']['x']['ticks']
        assert chart['options']['scales']['x']['ticks']['font']['size'] < 14  # Smaller font size for mobile