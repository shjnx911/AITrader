"""
Model definitions for database schema.
"""
from datetime import datetime
from main import db

class ModelBackup(db.Model):
    """Model lưu thông tin về các backup mô hình AI"""
    id = db.Column(db.Integer, primary_key=True)
    model_name = db.Column(db.String(100), nullable=False)
    created_date = db.Column(db.DateTime, nullable=False)
    pair = db.Column(db.String(50), nullable=False)
    timeframe = db.Column(db.String(10), nullable=False)
    backup_path = db.Column(db.String(255), nullable=False)
    metrics = db.Column(db.JSON, nullable=True)
    is_active = db.Column(db.Boolean, default=False)

class TrainingConfig(db.Model):
    """Model lưu cấu hình huấn luyện"""
    id = db.Column(db.Integer, primary_key=True)
    config_name = db.Column(db.String(100), nullable=False)
    params = db.Column(db.JSON, nullable=False)
    created_date = db.Column(db.DateTime, nullable=False)

class TradingMetrics(db.Model):
    """Model lưu trữ thông tin hiệu suất giao dịch"""
    id = db.Column(db.Integer, primary_key=True)
    pair_name = db.Column(db.String(100), nullable=False)
    timeframe = db.Column(db.String(10), nullable=False)
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    total_trades = db.Column(db.Integer, nullable=False)
    win_trades = db.Column(db.Integer, nullable=False)
    loss_trades = db.Column(db.Integer, nullable=False)
    profit_percent = db.Column(db.Float, nullable=False)
    profit_abs = db.Column(db.Float, nullable=False)
    metrics_data = db.Column(db.JSON, nullable=True)