"""
Module tích hợp backtest với AI.
Cung cấp các công cụ để import dữ liệu backtest, huấn luyện mô hình AI, 
và áp dụng mô hình vào chiến lược giao dịch.
"""

# Tạo blueprint trước khi import routes để tránh lỗi circular import
from flask import Blueprint
backtest_ai_bp = Blueprint('backtest_ai', __name__, url_prefix='/backtest_ai')

# Import các routes cho blueprint sau khi đã tạo blueprint
from .routes import *

# Import routes cho Monte Carlo simulation
from .monte_carlo_routes import monte_carlo_bp