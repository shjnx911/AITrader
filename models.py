"""
Database models for the AITradeStrategist application.
"""

from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

# This is a reference to the db variable in main.py
# It will be initialized when main.py imports this module
db = SQLAlchemy()

# Model for storing AI model backups
class ModelBackup(db.Model):
    """Model lưu thông tin về các backup mô hình AI"""
    id = db.Column(db.Integer, primary_key=True)
    model_name = db.Column(db.String(100), nullable=False)
    created_date = db.Column(db.DateTime, nullable=False, default=datetime.now)
    pair = db.Column(db.String(50), nullable=False)
    timeframe = db.Column(db.String(10), nullable=False)
    backup_path = db.Column(db.String(255), nullable=False)
    metrics = db.Column(db.JSON, nullable=True)
    is_active = db.Column(db.Boolean, default=False)
    uses_gpu = db.Column(db.Boolean, nullable=True)
    description = db.Column(db.String(255), nullable=True)
    version = db.Column(db.String(50), nullable=True)

# Model for storing training configuration
class TrainingConfig(db.Model):
    """Model lưu cấu hình huấn luyện"""
    id = db.Column(db.Integer, primary_key=True)
    config_name = db.Column(db.String(100), nullable=False)
    params = db.Column(db.JSON, nullable=False)
    created_date = db.Column(db.DateTime, nullable=False, default=datetime.now)
    is_default = db.Column(db.Boolean, nullable=True)
    description = db.Column(db.String(255), nullable=True)

# Model for storing trading metrics
class TradingMetrics(db.Model):
    """Model lưu trữ thông tin hiệu suất giao dịch"""
    id = db.Column(db.Integer, primary_key=True)
    pair = db.Column(db.String(100), nullable=False)
    timeframe = db.Column(db.String(10), nullable=False)
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    total_trades = db.Column(db.Integer, nullable=False)
    win_trades = db.Column(db.Integer, nullable=False)
    loss_trades = db.Column(db.Integer, nullable=False)
    profit_percent = db.Column(db.Float, nullable=False)
    profit_abs = db.Column(db.Float, nullable=False)
    metrics_data = db.Column(db.JSON, nullable=True)
    max_drawdown = db.Column(db.Float, nullable=True)
    model_id = db.Column(db.Integer, nullable=True)