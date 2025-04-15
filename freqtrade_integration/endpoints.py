"""
API endpoints for Freqtrade integration.
Cung cấp các endpoint API để tương tác với Freqtrade.
"""
import os
import logging
from typing import Any, Dict, List, Optional, Union
from datetime import datetime

from flask import Blueprint, jsonify, request, current_app

from freqtrade_integration.freqtrade_api import FreqtradeAPI

# Thiết lập logging
logger = logging.getLogger(__name__)

# Tạo blueprint cho các endpoint Freqtrade
freqtrade_bp = Blueprint('freqtrade', __name__, url_prefix='/api/freqtrade')

# Cache API instance
_api_instance = None


def get_api() -> Optional[FreqtradeAPI]:
    """Lấy hoặc tạo instance FreqtradeAPI"""
    global _api_instance
    
    if _api_instance is None:
        # Lấy cấu hình từ biến môi trường hoặc config
        server_url = os.environ.get('FREQTRADE_API_URL', 'http://localhost:8080')
        username = os.environ.get('FREQTRADE_USERNAME')
        password = os.environ.get('FREQTRADE_PASSWORD')
        
        # Tạo instance mới
        _api_instance = FreqtradeAPI(server_url=server_url, username=username, password=password)
        
        # Đăng nhập
        if not _api_instance._login():
            logger.error("Không thể đăng nhập vào Freqtrade API")
            _api_instance = None
    
    return _api_instance


@freqtrade_bp.route('/status', methods=['GET'])
def freqtrade_status():
    """Lấy trạng thái Freqtrade bot"""
    try:
        api = get_api()
        if api is None:
            return jsonify({
                'status': 'error',
                'message': 'Không thể kết nối đến Freqtrade API',
                'error': 'connection_error'
            }), 500
        
        status = api.get_status()
        if status is None:
            return jsonify({
                'status': 'error',
                'message': 'Không nhận được phản hồi từ Freqtrade API',
                'error': 'no_response'
            }), 500
        
        return jsonify(status)
    except Exception as e:
        logger.error(f"Lỗi khi lấy trạng thái Freqtrade: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'Lỗi: {str(e)}',
            'error': 'api_error'
        }), 500


@freqtrade_bp.route('/trades', methods=['GET'])
def freqtrade_trades():
    """Lấy danh sách giao dịch từ Freqtrade"""
    try:
        limit = request.args.get('limit', default=50, type=int)
        
        api = get_api()
        if api is None:
            return jsonify({
                'status': 'error',
                'message': 'Không thể kết nối đến Freqtrade API',
                'error': 'connection_error'
            }), 500
        
        trades = api.get_trades(limit=limit)
        if trades is None:
            return jsonify({
                'status': 'error',
                'message': 'Không nhận được phản hồi từ Freqtrade API',
                'error': 'no_response'
            }), 500
        
        return jsonify(trades)
    except Exception as e:
        logger.error(f"Lỗi khi lấy danh sách giao dịch: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'Lỗi: {str(e)}',
            'error': 'api_error'
        }), 500


@freqtrade_bp.route('/profit', methods=['GET'])
def freqtrade_profit():
    """Lấy thống kê lợi nhuận từ Freqtrade"""
    try:
        api = get_api()
        if api is None:
            return jsonify({
                'status': 'error',
                'message': 'Không thể kết nối đến Freqtrade API',
                'error': 'connection_error'
            }), 500
        
        profit = api.get_profit()
        if profit is None:
            return jsonify({
                'status': 'error',
                'message': 'Không nhận được phản hồi từ Freqtrade API',
                'error': 'no_response'
            }), 500
        
        return jsonify(profit)
    except Exception as e:
        logger.error(f"Lỗi khi lấy thống kê lợi nhuận: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'Lỗi: {str(e)}',
            'error': 'api_error'
        }), 500


@freqtrade_bp.route('/pairs', methods=['GET'])
def freqtrade_pairs():
    """Lấy danh sách các cặp giao dịch từ Freqtrade"""
    try:
        api = get_api()
        if api is None:
            return jsonify({
                'status': 'error',
                'message': 'Không thể kết nối đến Freqtrade API',
                'error': 'connection_error'
            }), 500
        
        pairs = api.get_pairs()
        if pairs is None:
            return jsonify({
                'status': 'error',
                'message': 'Không nhận được phản hồi từ Freqtrade API',
                'error': 'no_response'
            }), 500
        
        return jsonify(pairs)
    except Exception as e:
        logger.error(f"Lỗi khi lấy danh sách các cặp giao dịch: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'Lỗi: {str(e)}',
            'error': 'api_error'
        }), 500


@freqtrade_bp.route('/performance', methods=['GET'])
def freqtrade_performance():
    """Lấy thống kê hiệu suất từ Freqtrade"""
    try:
        api = get_api()
        if api is None:
            return jsonify({
                'status': 'error',
                'message': 'Không thể kết nối đến Freqtrade API',
                'error': 'connection_error'
            }), 500
        
        performance = api.get_performance()
        if performance is None:
            return jsonify({
                'status': 'error',
                'message': 'Không nhận được phản hồi từ Freqtrade API',
                'error': 'no_response'
            }), 500
        
        return jsonify(performance)
    except Exception as e:
        logger.error(f"Lỗi khi lấy thống kê hiệu suất: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'Lỗi: {str(e)}',
            'error': 'api_error'
        }), 500


@freqtrade_bp.route('/start', methods=['POST'])
def freqtrade_start():
    """Khởi động Freqtrade bot"""
    try:
        api = get_api()
        if api is None:
            return jsonify({
                'status': 'error',
                'message': 'Không thể kết nối đến Freqtrade API',
                'error': 'connection_error'
            }), 500
        
        result = api.start_bot()
        if not result:
            return jsonify({
                'status': 'error',
                'message': 'Không thể khởi động Freqtrade bot',
                'error': 'start_error'
            }), 500
        
        return jsonify({
            'status': 'success',
            'message': 'Đã khởi động Freqtrade bot thành công'
        })
    except Exception as e:
        logger.error(f"Lỗi khi khởi động Freqtrade bot: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'Lỗi: {str(e)}',
            'error': 'api_error'
        }), 500


@freqtrade_bp.route('/stop', methods=['POST'])
def freqtrade_stop():
    """Dừng Freqtrade bot"""
    try:
        api = get_api()
        if api is None:
            return jsonify({
                'status': 'error',
                'message': 'Không thể kết nối đến Freqtrade API',
                'error': 'connection_error'
            }), 500
        
        result = api.stop_bot()
        if not result:
            return jsonify({
                'status': 'error',
                'message': 'Không thể dừng Freqtrade bot',
                'error': 'stop_error'
            }), 500
        
        return jsonify({
            'status': 'success',
            'message': 'Đã dừng Freqtrade bot thành công'
        })
    except Exception as e:
        logger.error(f"Lỗi khi dừng Freqtrade bot: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'Lỗi: {str(e)}',
            'error': 'api_error'
        }), 500


@freqtrade_bp.route('/forcebuy', methods=['POST'])
def freqtrade_forcebuy():
    """Force buy một cặp giao dịch"""
    try:
        data = request.get_json()
        if not data or 'pair' not in data:
            return jsonify({
                'status': 'error',
                'message': 'Thiếu thông tin cặp giao dịch',
                'error': 'missing_data'
            }), 400
        
        pair = data.get('pair')
        price = data.get('price')  # Optional
        
        api = get_api()
        if api is None:
            return jsonify({
                'status': 'error',
                'message': 'Không thể kết nối đến Freqtrade API',
                'error': 'connection_error'
            }), 500
        
        result = api.force_buy(pair=pair, price=price)
        if result is None:
            return jsonify({
                'status': 'error',
                'message': 'Không thể thực hiện force buy',
                'error': 'forcebuy_error'
            }), 500
        
        return jsonify({
            'status': 'success',
            'message': f'Đã thực hiện force buy {pair} thành công',
            'result': result
        })
    except Exception as e:
        logger.error(f"Lỗi khi thực hiện force buy: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'Lỗi: {str(e)}',
            'error': 'api_error'
        }), 500


@freqtrade_bp.route('/forcesell', methods=['POST'])
def freqtrade_forcesell():
    """Force sell một giao dịch"""
    try:
        data = request.get_json()
        if not data or 'trade_id' not in data:
            return jsonify({
                'status': 'error',
                'message': 'Thiếu thông tin ID giao dịch',
                'error': 'missing_data'
            }), 400
        
        trade_id = data.get('trade_id')
        
        api = get_api()
        if api is None:
            return jsonify({
                'status': 'error',
                'message': 'Không thể kết nối đến Freqtrade API',
                'error': 'connection_error'
            }), 500
        
        result = api.force_sell(trade_id=trade_id)
        if result is None:
            return jsonify({
                'status': 'error',
                'message': 'Không thể thực hiện force sell',
                'error': 'forcesell_error'
            }), 500
        
        return jsonify({
            'status': 'success',
            'message': f'Đã thực hiện force sell giao dịch {trade_id} thành công',
            'result': result
        })
    except Exception as e:
        logger.error(f"Lỗi khi thực hiện force sell: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'Lỗi: {str(e)}',
            'error': 'api_error'
        }), 500


def register_endpoints(app):
    """Đăng ký tất cả endpoints Freqtrade với Flask app"""
    app.register_blueprint(freqtrade_bp)
    logger.info("Đã đăng ký các endpoint Freqtrade API")