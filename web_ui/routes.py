#!/usr/bin/env python3
"""
Routes cho ứng dụng AITradeStrategist.
Định nghĩa các route URL và xử lý người dùng.
"""
import os
import json
from datetime import datetime, timedelta
from flask import render_template, request, jsonify, redirect, url_for

from web_ui.models import ModelBackup, TrainingConfig, TradingPair, TradingMetrics, TradeRecord

def register_routes(app):
    """Đăng ký tất cả routes cho Flask app"""
    
    @app.route('/dashboard')
    def dashboard():
        """Hiển thị trang dashboard chính"""
        return render_template('dashboard.html')
    
    @app.route('/models')
    def models():
        """Hiển thị trang quản lý models"""
        return render_template('models.html')
    
    @app.route('/performance')
    def performance():
        """Hiển thị trang phân tích hiệu suất"""
        return render_template('performance.html')
    
    @app.route('/settings')
    def settings():
        """Hiển thị trang cài đặt"""
        return render_template('settings.html')
    
    # Các API cho việc lấy dữ liệu
    @app.route('/api/stats/summary')
    def api_stats_summary():
        """Lấy thông tin tóm tắt hiệu suất"""
        try:
            # Lấy metrics tổng thể từ database
            metrics = TradingMetrics.query.filter(
                TradingMetrics.pair_name == 'ALL',
                TradingMetrics.timeframe == 'ALL'
            ).order_by(TradingMetrics.end_date.desc()).first()
            
            if metrics:
                return jsonify(metrics.to_dict())
            
            # Nếu không có dữ liệu, trả về dữ liệu trống
            return jsonify({
                'total_trades': 0,
                'win_trades': 0,
                'loss_trades': 0,
                'win_rate': 0,
                'profit_percent': 0,
                'profit_abs': 0
            })
        except Exception as e:
            app.logger.error(f"Lỗi khi lấy dữ liệu tổng hợp: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/stats/recent_trades')
    def api_recent_trades():
        """Lấy danh sách các giao dịch gần đây"""
        try:
            limit = int(request.args.get('limit', 10))
            
            # Lấy các giao dịch gần đây
            trades = TradeRecord.query.order_by(
                TradeRecord.open_date.desc()
            ).limit(limit).all()
            
            return jsonify([trade.to_dict() for trade in trades])
        except Exception as e:
            app.logger.error(f"Lỗi khi lấy dữ liệu giao dịch gần đây: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/stats/pairs_performance')
    def api_pairs_performance():
        """Lấy hiệu suất của các cặp giao dịch"""
        try:
            # Lấy hiệu suất theo từng cặp
            metrics = TradingMetrics.query.filter(
                TradingMetrics.pair_name != 'ALL',
                TradingMetrics.timeframe == 'ALL'
            ).order_by(TradingMetrics.profit_percent.desc()).all()
            
            return jsonify([m.to_dict() for m in metrics])
        except Exception as e:
            app.logger.error(f"Lỗi khi lấy hiệu suất các cặp: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/stats/performance_timeframe')
    def api_performance_timeframe():
        """Lấy hiệu suất theo timeframe"""
        try:
            # Lấy hiệu suất theo từng timeframe
            metrics = TradingMetrics.query.filter(
                TradingMetrics.pair_name == 'ALL',
                TradingMetrics.timeframe != 'ALL'
            ).order_by(TradingMetrics.timeframe).all()
            
            return jsonify([m.to_dict() for m in metrics])
        except Exception as e:
            app.logger.error(f"Lỗi khi lấy hiệu suất theo timeframe: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/stats/performance_history')
    def api_performance_history():
        """Lấy lịch sử hiệu suất theo thời gian"""
        try:
            days = int(request.args.get('days', 30))
            pair = request.args.get('pair', 'ALL')
            timeframe = request.args.get('timeframe', 'ALL')
            
            # Tính toán ngày bắt đầu
            start_date = datetime.utcnow() - timedelta(days=days)
            
            # Query dữ liệu metrics trong khoảng thời gian
            query = TradingMetrics.query.filter(
                TradingMetrics.end_date >= start_date
            )
            
            if pair != 'ALL':
                query = query.filter(TradingMetrics.pair_name == pair)
                
            if timeframe != 'ALL':
                query = query.filter(TradingMetrics.timeframe == timeframe)
                
            metrics = query.order_by(TradingMetrics.end_date).all()
            
            return jsonify([m.to_dict() for m in metrics])
        except Exception as e:
            app.logger.error(f"Lỗi khi lấy lịch sử hiệu suất: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/models/list')
    def api_models_list():
        """Lấy danh sách các model đã backup"""
        try:
            models = ModelBackup.query.order_by(ModelBackup.created_date.desc()).all()
            return jsonify([m.to_dict() for m in models])
        except Exception as e:
            app.logger.error(f"Lỗi khi lấy danh sách models: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/trading/pairs')
    def api_trading_pairs():
        """Lấy danh sách các cặp giao dịch"""
        try:
            pairs = TradingPair.query.order_by(TradingPair.name).all()
            return jsonify([p.to_dict() for p in pairs])
        except Exception as e:
            app.logger.error(f"Lỗi khi lấy danh sách cặp giao dịch: {e}")
            return jsonify({'error': str(e)}), 500
    
    # Thêm các route khác khi cần