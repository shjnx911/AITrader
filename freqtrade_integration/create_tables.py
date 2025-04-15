#!/usr/bin/env python
"""
Script tạo các bảng cần thiết cho AITradeStrategist để lưu trữ dữ liệu từ Freqtrade.
Chạy script này trước khi sử dụng tích hợp Freqtrade.
"""
import os
import sys
import logging
import argparse
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, JSON, Boolean, UniqueConstraint, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

# Thiết lập logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Tạo base class cho các model
Base = declarative_base()


class TradingPairs(Base):
    """Bảng lưu trữ các cặp giao dịch từ Freqtrade"""
    __tablename__ = 'trading_pairs'
    
    id = Column(Integer, primary_key=True)
    pair = Column(String(50), nullable=False, unique=True)
    is_active = Column(Boolean, default=True)
    created_date = Column(DateTime, nullable=False, default=datetime.now)
    last_updated = Column(DateTime, nullable=True, onupdate=datetime.now)


class TradingMetrics(Base):
    """Bảng lưu trữ metrics hiệu suất giao dịch"""
    __tablename__ = 'trading_metrics'
    
    id = Column(Integer, primary_key=True)
    pair = Column(String(50), nullable=False)
    timeframe = Column(String(10), nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    total_trades = Column(Integer, nullable=False)
    win_trades = Column(Integer, nullable=False)
    loss_trades = Column(Integer, nullable=False)
    profit_percent = Column(Float, nullable=False)
    profit_abs = Column(Float, nullable=False)
    metrics_data = Column(JSON, nullable=True)
    created_date = Column(DateTime, nullable=False, default=datetime.now)
    last_updated = Column(DateTime, nullable=True, onupdate=datetime.now)
    
    # Ràng buộc duy nhất để tránh trùng lặp dữ liệu
    __table_args__ = (
        UniqueConstraint('pair', 'timeframe', 'start_date', 'end_date', name='uix_trading_metrics'),
    )


def create_tables(db_url):
    """Tạo các bảng trong database"""
    try:
        # Kết nối đến database
        engine = create_engine(db_url)
        
        # Tạo các bảng
        Base.metadata.create_all(engine)
        
        logger.info("Đã tạo các bảng thành công")
        
        # Tạo session để kiểm tra kết nối
        Session = sessionmaker(bind=engine)
        session = Session()
        
        # Kiểm tra xem bảng đã tồn tại chưa
        result = session.execute(text("SELECT COUNT(*) FROM trading_pairs")).scalar()
        logger.info(f"Số lượng cặp giao dịch trong database: {result}")
        
        result = session.execute(text("SELECT COUNT(*) FROM trading_metrics")).scalar()
        logger.info(f"Số lượng bản ghi metrics trong database: {result}")
        
        session.close()
        
        return True
        
    except Exception as e:
        logger.error(f"Lỗi tạo bảng: {str(e)}")
        return False


def parse_args():
    """Phân tích tham số dòng lệnh"""
    parser = argparse.ArgumentParser(description="Tạo các bảng cần thiết cho AITradeStrategist")
    
    parser.add_argument(
        "--db-url",
        help="Database URL của AITradeStrategist. Nếu không được cung cấp, sử dụng biến môi trường DATABASE_URL"
    )
    
    return parser.parse_args()


def main():
    """Hàm chính"""
    args = parse_args()
    
    # Lấy database URL
    db_url = args.db_url or os.environ.get('DATABASE_URL')
    
    if not db_url:
        logger.error("Không tìm thấy DATABASE_URL. Vui lòng cung cấp thông qua tham số --db-url hoặc biến môi trường DATABASE_URL")
        sys.exit(1)
    
    # Tạo các bảng
    if create_tables(db_url):
        logger.info("Tạo bảng thành công")
    else:
        logger.error("Tạo bảng thất bại")
        sys.exit(1)


if __name__ == "__main__":
    main()