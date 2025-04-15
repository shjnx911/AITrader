"""
API integration with Freqtrade.
This module handles API connections to a running Freqtrade instance.
"""
import os
import json
import logging
import requests
from typing import Dict, List, Optional, Any, Union

logger = logging.getLogger(__name__)

class FreqtradeAPI:
    """Helper class for Freqtrade REST API integration."""
    
    def __init__(self, server_url: str = None, api_key: str = None, username: str = None, password: str = None):
        """
        Initialize the Freqtrade API connection.
        
        Args:
            server_url: URL to the Freqtrade API server (e.g., http://localhost:8080)
            api_key: API key for authentication (older method)
            username: Username for Freqtrade API authentication
            password: Password for Freqtrade API authentication
        """
        self.server_url = server_url or os.environ.get('FREQTRADE_API_URL', 'http://localhost:8080')
        self.api_key = api_key or os.environ.get('FREQTRADE_API_KEY', '')
        self.username = username or os.environ.get('FREQTRADE_USERNAME', 'freqtrader')
        self.password = password or os.environ.get('FREQTRADE_PASSWORD', '')
        self._token = None
        
    def get_headers(self) -> Dict[str, str]:
        """Get HTTP headers for API requests."""
        headers = {
            'Content-Type': 'application/json',
        }
        
        # Add token if available
        if self._token:
            headers['Authorization'] = f'Bearer {self._token}'
            
        return headers
    
    def _login(self) -> bool:
        """
        Login to the Freqtrade API and get JWT token.
        
        Returns:
            True if login successful, False otherwise
        """
        try:
            response = requests.post(
                f"{self.server_url}/api/v1/token/login",
                data=json.dumps({
                    "username": self.username,
                    "password": self.password
                }),
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                data = response.json()
                self._token = data.get('access_token')
                return bool(self._token)
                
            logger.error(f"Failed to login to Freqtrade API: {response.text}")
            return False
            
        except Exception as e:
            logger.error(f"Error connecting to Freqtrade API: {str(e)}")
            return False
    
    def api_request(self, endpoint: str, method: str = 'GET', 
                   data: dict = None) -> Optional[Dict[str, Any]]:
        """
        Send request to Freqtrade API.
        
        Args:
            endpoint: API endpoint (without leading slash)
            method: HTTP method (GET, POST, etc.)
            data: Request data for POST/PUT methods
            
        Returns:
            Response data as dictionary or None if request failed
        """
        if not self._token and not self._login():
            logger.error("Not authenticated to Freqtrade API")
            return None
            
        url = f"{self.server_url}/api/v1/{endpoint}"
        
        try:
            if method.upper() == 'GET':
                response = requests.get(url, headers=self.get_headers())
            elif method.upper() == 'POST':
                response = requests.post(
                    url, 
                    data=json.dumps(data) if data else None,
                    headers=self.get_headers()
                )
            elif method.upper() == 'PUT':
                response = requests.put(
                    url, 
                    data=json.dumps(data) if data else None,
                    headers=self.get_headers()
                )
            elif method.upper() == 'DELETE':
                response = requests.delete(url, headers=self.get_headers())
            else:
                logger.error(f"Unsupported HTTP method: {method}")
                return None
                
            # Check if token expired
            if response.status_code == 401:
                logger.info("Token expired, logging in again...")
                if self._login():
                    return self.api_request(endpoint, method, data)
                else:
                    return None
                
            # Parse response
            if response.status_code in (200, 201):
                return response.json()
                
            logger.error(f"API request failed: {response.text}")
            return None
            
        except Exception as e:
            logger.error(f"Error during API request: {str(e)}")
            return None
    
    def get_status(self) -> Optional[Dict[str, Any]]:
        """
        Get Freqtrade bot status.
        
        Returns:
            Status information or None if request failed
        """
        return self.api_request('status')
    
    def get_trades(self, limit: int = 50) -> Optional[List[Dict[str, Any]]]:
        """
        Get recent trades.
        
        Args:
            limit: Maximum number of trades to fetch
            
        Returns:
            List of trades or None if request failed
        """
        result = self.api_request(f'trades?limit={limit}')
        return result.get('trades') if result else None
    
    def get_profit(self) -> Optional[Dict[str, Any]]:
        """
        Get profit statistics.
        
        Returns:
            Profit statistics or None if request failed
        """
        return self.api_request('profit')
    
    def get_pairs(self) -> Optional[List[str]]:
        """
        Get list of trading pairs.
        
        Returns:
            List of pairs or None if request failed
        """
        result = self.api_request('pairs')
        return result.get('pairs') if result else None
    
    def get_performance(self) -> Optional[List[Dict[str, Any]]]:
        """
        Get performance by pair.
        
        Returns:
            Performance statistics or None if request failed
        """
        return self.api_request('performance')
    
    def start_bot(self) -> bool:
        """
        Start the Freqtrade bot.
        
        Returns:
            True if successful, False otherwise
        """
        result = self.api_request('start', method='POST')
        return bool(result and result.get('status') == 'running')
    
    def stop_bot(self) -> bool:
        """
        Stop the Freqtrade bot.
        
        Returns:
            True if successful, False otherwise
        """
        result = self.api_request('stop', method='POST')
        return bool(result and result.get('status') == 'stopped')
    
    def force_buy(self, pair: str, price: Optional[float] = None) -> Optional[Dict[str, Any]]:
        """
        Force buy a trading pair.
        
        Args:
            pair: Trading pair (e.g., BTC/USDT)
            price: Buy price (optional)
            
        Returns:
            Trade result or None if request failed
        """
        data = {'pair': pair}
        if price:
            data['price'] = price
            
        return self.api_request('forcebuy', method='POST', data=data)
    
    def force_sell(self, trade_id: Union[str, int]) -> Optional[Dict[str, Any]]:
        """
        Force sell a trade.
        
        Args:
            trade_id: ID of the trade to sell
            
        Returns:
            Result or None if request failed
        """
        return self.api_request('forcesell', method='POST', data={'tradeid': str(trade_id)})