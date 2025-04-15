#!/usr/bin/env python
"""
Script đồng bộ dữ liệu từ Freqtrade vào AITradeStrategist.
Chạy script này định kỳ để cập nhật dữ liệu mới nhất từ Freqtrade.
"""
import os
import sys
import time
import logging
import argparse
import schedule
from freqtrade_db_connector import FreqtradeDBConnector, AITradeStrategistDBConnector

# Thiết lập logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('sync_freqtrade_data.log')
    ]
)
logger = logging.getLogger(__name__)


def sync_data():
    """Hàm đồng bộ dữ liệu từ Freqtrade vào AITradeStrategist"""
    logger.info("Bắt đầu đồng bộ dữ liệu...")
    
    # Kết nối đến Freqtrade
    freqtrade_db = FreqtradeDBConnector(
        db_url=os.environ.get('FREQTRADE_DB_URL'),
        sqlite_path=os.environ.get('FREQTRADE_SQLITE_PATH')
    )
    
    if not freqtrade_db.connect():
        logger.error("Không thể kết nối đến database Freqtrade, kết thúc đồng bộ")
        return
    
    # Kết nối đến AITradeStrategist
    ai_db = AITradeStrategistDBConnector(db_url=os.environ.get('DATABASE_URL'))
    
    if not ai_db.connect():
        logger.error("Không thể kết nối đến database AITradeStrategist, kết thúc đồng bộ")
        freqtrade_db.disconnect()
        return
    
    try:
        # Lấy dữ liệu giao dịch
        trades_df = freqtrade_db.get_trades(limit=1000)  # Lấy 1000 giao dịch gần nhất
        if not trades_df.empty:
            logger.info(f"Đã lấy {len(trades_df)} giao dịch từ Freqtrade")
            
            # Phân tích dữ liệu (có thể thêm phân tích chi tiết ở đây)
            open_trades = trades_df[trades_df['is_open'] == True].shape[0]
            closed_trades = trades_df[trades_df['is_open'] == False].shape[0]
            profitable_trades = trades_df[(trades_df['is_open'] == False) & (trades_df['close_profit'] > 0)].shape[0]
            
            logger.info(f"Thống kê: {open_trades} giao dịch đang mở, {closed_trades} giao dịch đã đóng, {profitable_trades} giao dịch có lãi")
        
        # Lấy danh sách cặp giao dịch
        pairs = freqtrade_db.get_pairs()
        if pairs:
            logger.info(f"Đã lấy {len(pairs)} cặp giao dịch từ Freqtrade")
            ai_db.import_trading_pairs(pairs)
        
        # Lấy dữ liệu hiệu suất
        performance_df = freqtrade_db.get_strategy_performance()
        if not performance_df.empty:
            logger.info(f"Đã lấy hiệu suất của {len(performance_df)} cặp giao dịch từ Freqtrade")
            ai_db.import_trading_metrics(performance_df)
            
        logger.info("Đồng bộ dữ liệu thành công")
        
    except Exception as e:
        logger.error(f"Lỗi đồng bộ dữ liệu: {str(e)}")
    
    finally:
        # Đóng kết nối
        freqtrade_db.disconnect()
        ai_db.disconnect()


def parse_args():
    """Phân tích tham số dòng lệnh"""
    parser = argparse.ArgumentParser(description="Đồng bộ dữ liệu từ Freqtrade vào AITradeStrategist")
    
    parser.add_argument(
        "--once",
        action="store_true",
        help="Chỉ đồng bộ một lần rồi thoát"
    )
    
    parser.add_argument(
        "--interval",
        type=int,
        default=60,
        help="Khoảng thời gian giữa các lần đồng bộ (phút)"
    )
    
    parser.add_argument(
        "--db-url",
        help="Database URL của Freqtrade. Nếu không được cung cấp, sử dụng biến môi trường FREQTRADE_DB_URL"
    )
    
    parser.add_argument(
        "--sqlite-path",
        help="Đường dẫn đến file SQLite của Freqtrade. Nếu không được cung cấp, sử dụng biến môi trường FREQTRADE_SQLITE_PATH"
    )
    
    return parser.parse_args()


def main():
    """Hàm chính"""
    args = parse_args()
    
    # Thiết lập biến môi trường từ tham số dòng lệnh
    if args.db_url:
        os.environ['FREQTRADE_DB_URL'] = args.db_url
        
    if args.sqlite_path:
        os.environ['FREQTRADE_SQLITE_PATH'] = args.sqlite_path
    
    if args.once:
        # Chỉ đồng bộ một lần
        sync_data()
    else:
        # Đồng bộ định kỳ
        logger.info(f"Thiết lập đồng bộ dữ liệu tự động mỗi {args.interval} phút")
        
        # Đồng bộ ngay lần đầu
        sync_data()
        
        # Lịch đồng bộ định kỳ
        schedule.every(args.interval).minutes.do(sync_data)
        
        # Vòng lặp chính
        try:
            while True:
                schedule.run_pending()
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Đã nhận lệnh thoát, kết thúc ứng dụng")
        except Exception as e:
            logger.error(f"Lỗi không mong đợi: {str(e)}")


if __name__ == "__main__":
    main()