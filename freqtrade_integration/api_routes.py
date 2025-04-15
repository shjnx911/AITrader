"""
API routes for Freqtrade integration.
Defines the API endpoints for interacting with Freqtrade.
"""
import logging
import os
from typing import Optional

from flask import Blueprint, Flask, jsonify, request
from freqtrade_integration.endpoints import register_endpoints

# Thiết lập logging
logger = logging.getLogger(__name__)


def register_freqtrade_api_routes(app: Flask) -> None:
    """
    Register all Freqtrade API routes with the Flask app.
    
    Args:
        app: Flask application instance
    """
    try:
        # Đăng ký tất cả endpoints Freqtrade
        register_endpoints(app)
        
        # Đăng ký một route kiểm tra để thông báo Freqtrade API có sẵn
        @app.route('/api/freqtrade_available')
        def freqtrade_available():
            """Endpoint to check if Freqtrade integration is available"""
            return jsonify({
                'available': True,
                'version': '1.0.0'
            })
        
        logger.info("Đã đăng ký các routes Freqtrade API thành công")
    except Exception as e:
        logger.error(f"Lỗi khi đăng ký routes Freqtrade API: {str(e)}")
        raise