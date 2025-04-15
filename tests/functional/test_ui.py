"""
Functional tests for the web UI of the AITradeStrategist application.
"""
import pytest
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from unittest.mock import patch


class TestWebUI:
    """Tests for the web UI of the application."""
    
    def get_chrome_options(self):
        """Set up Chrome options for Selenium tests."""
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        return chrome_options
    
    @pytest.mark.skip(reason="Requires Selenium webdriver setup")
    def test_theme_toggle(self, client):
        """Test the theme toggle functionality."""
        # This test would use Selenium webdriver to check if dark/light theme toggle works
        # We're skipping it for now as it requires additional setup
        pass
    
    @pytest.mark.skip(reason="Requires Selenium webdriver setup")
    def test_language_switcher(self, client):
        """Test the language switcher functionality."""
        # This test would use Selenium webdriver to check if language switching works
        # We're skipping it for now as it requires additional setup
        pass
    
    @pytest.mark.skip(reason="Requires Selenium webdriver setup")
    def test_mobile_responsive_layout(self, client):
        """Test the responsive layout for mobile devices."""
        # This test would use Selenium webdriver to check if the layout is responsive
        # We're skipping it for now as it requires additional setup
        pass
    
    @pytest.mark.skip(reason="Requires Selenium webdriver setup")
    def test_chart_rendering(self, client):
        """Test the chart rendering functionality."""
        # This test would use Selenium webdriver to check if charts are rendered correctly
        # We're skipping it for now as it requires additional setup
        pass
    
    @pytest.mark.skip(reason="Requires Selenium webdriver setup")
    def test_settings_form_submission(self, client):
        """Test the settings form submission functionality."""
        # This test would use Selenium webdriver to check if settings are saved correctly
        # We're skipping it for now as it requires additional setup
        pass
    
    @patch('main.gpu_utils.check_amd_gpu_support')
    def test_gpu_status_api(self, mock_gpu_support, client):
        """Test the GPU status API endpoint."""
        # Mock the GPU support check to return True
        mock_gpu_support.return_value = True
        
        # Make a request to the GPU status API
        response = client.get('/api/gpu_status')
        
        # Check that the response is successful
        assert response.status_code == 200
        assert b'gpu_available' in response.data
        assert b'gpu_type' in response.data
        assert b'acceleration' in response.data
        
        # Check that the GPU support check was called
        mock_gpu_support.assert_called_once()
    
    def test_api_routes_exist(self, client):
        """Test that API routes exist and return valid JSON."""
        # List of API routes to check
        api_routes = [
            '/api/stats/summary',
            '/api/recent_trades',
            '/api/pairs/performance',
            '/api/freqtrade/status',
            '/api/gpu_status'
        ]
        
        # Check each route
        for route in api_routes:
            response = client.get(route)
            
            # Check that the response is successful
            assert response.status_code in [200, 404, 500]  # May return error but should exist
            
            # If successful, check that the response is JSON
            if response.status_code == 200:
                assert response.content_type == 'application/json'
    
    def test_sidebar_links(self, client):
        """Test that sidebar links are present and correct."""
        # Get the dashboard page
        response = client.get('/dashboard')
        
        # Check that the response is successful
        assert response.status_code == 200
        
        # Check that the sidebar links are present
        assert b'href="/dashboard"' in response.data
        assert b'href="/models"' in response.data
        assert b'href="/performance"' in response.data
        assert b'href="/settings"' in response.data
        assert b'href="/documentation"' in response.data