#!/usr/bin/env python
"""
Script nhập dữ liệu từ kết quả backtest của Freqtrade để huấn luyện AI.
Kết quả backtest chứa thông tin quý giá về hiệu suất chiến lược trong điều kiện lịch sử.
"""
import os
import json
import argparse
import logging
import glob
from datetime import datetime
from typing import Dict, List, Optional, Any, Union

import pandas as pd
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Tải biến môi trường
load_dotenv()

# Thiết lập logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Tạo base model
Base = declarative_base()

# Định nghĩa model để lưu trữ dữ liệu backtest
class BacktestResult(Base):
    """Model lưu trữ kết quả backtesting từ Freqtrade"""
    __tablename__ = 'backtest_results'
    
    id = Column(Integer, primary_key=True)
    strategy_name = Column(String(100), nullable=False)
    pair = Column(String(50), nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    timeframe = Column(String(10), nullable=False)
    
    # Metrics tổng quan
    profit_percent = Column(Float, nullable=False)
    profit_abs = Column(Float, nullable=False)
    trades_count = Column(Integer, nullable=False)
    win_rate = Column(Float, nullable=False)
    risk_reward_ratio = Column(Float, nullable=True)
    average_duration = Column(String(50), nullable=True)
    
    # Dữ liệu chi tiết
    trades_data = Column(JSON, nullable=True)  # Thông tin chi tiết về các giao dịch
    parameters = Column(JSON, nullable=True)   # Tham số chiến lược đã sử dụng
    
    # Thông tin file backup
    file_path = Column(String(255), nullable=False)
    import_date = Column(DateTime, nullable=False, default=datetime.now)
    is_used_for_training = Column(Boolean, default=False)
    
    # Model sử dụng kết quả này
    used_by_model_id = Column(Integer, nullable=True)


def connect_to_database():
    """Kết nối đến database"""
    db_url = os.getenv('DATABASE_URL')
    if not db_url:
        raise ValueError("Không tìm thấy DATABASE_URL trong biến môi trường")
    
    engine = create_engine(db_url)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return Session()


def parse_backtest_file(file_path: str) -> Dict[str, Any]:
    """
    Phân tích file kết quả backtest của Freqtrade
    
    Args:
        file_path: Đường dẫn tới file JSON chứa kết quả backtest
        
    Returns:
        Dictionary chứa dữ liệu đã xử lý
    """
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        # Kiểm tra dữ liệu hợp lệ
        if not isinstance(data, dict) or 'strategy' not in data or 'strategy_comparison' not in data:
            logger.error(f"Định dạng dữ liệu backtest không hợp lệ trong {file_path}")
            return None
        
        # Lấy thông tin chiến lược
        strategy_info = data['strategy_comparison'][0] if data['strategy_comparison'] else None
        if not strategy_info:
            logger.error(f"Không tìm thấy thông tin chiến lược trong {file_path}")
            return None
        
        # Chuẩn bị dữ liệu trả về
        result = {
            'strategy_name': data['strategy'],
            'file_path': file_path,
            'timeframe': data.get('timeframe', 'unknown'),
            'start_date': datetime.fromtimestamp(data.get('backtest_start_time', 0)),
            'end_date': datetime.fromtimestamp(data.get('backtest_end_time', 0)),
            'parameters': data.get('strategy_parameters', {}),
            'trades_data': data.get('trades', []),
            
            # Metrics từ strategy_comparison
            'profit_percent': strategy_info.get('profit_total_pct', 0.0),
            'profit_abs': strategy_info.get('profit_total', 0.0),
            'trades_count': strategy_info.get('trades', 0),
            'win_rate': strategy_info.get('win_ratio', 0.0) * 100,  # Chuyển sang phần trăm
            'risk_reward_ratio': strategy_info.get('risk_reward_ratio', 0.0),
            'average_duration': strategy_info.get('avg_duration', ''),
        }
        
        # Xử lý dữ liệu các cặp giao dịch
        pairs_data = data.get('strategy_comparison_per_pair', [])
        pairs = []
        for pair_data in pairs_data:
            pairs.append(pair_data.get('key', 'UNKNOWN'))
        
        result['pairs'] = pairs
        
        return result
    
    except Exception as e:
        logger.error(f"Lỗi khi phân tích file backtest {file_path}: {str(e)}")
        return None


def import_backtest_results(directory: str, filter_strategy: Optional[str] = None):
    """
    Import tất cả kết quả backtest từ một thư mục
    
    Args:
        directory: Thư mục chứa kết quả backtest
        filter_strategy: Chỉ import kết quả của chiến lược này (tùy chọn)
    """
    # Tìm tất cả file json trong thư mục
    files = glob.glob(os.path.join(directory, '*.json'))
    if not files:
        logger.warning(f"Không tìm thấy file backtest nào trong {directory}")
        return
    
    # Kết nối database
    session = connect_to_database()
    
    # Import từng file
    total_files = len(files)
    imported_count = 0
    skipped_count = 0
    
    for file_path in files:
        # Kiểm tra xem file đã được import chưa
        existing = session.query(BacktestResult).filter_by(file_path=file_path).first()
        if existing:
            logger.info(f"Bỏ qua file đã import: {os.path.basename(file_path)}")
            skipped_count += 1
            continue
        
        # Phân tích file
        data = parse_backtest_file(file_path)
        if not data:
            skipped_count += 1
            continue
        
        # Lọc theo chiến lược nếu được yêu cầu
        if filter_strategy and data['strategy_name'] != filter_strategy:
            logger.info(f"Bỏ qua chiến lược không khớp: {data['strategy_name']} != {filter_strategy}")
            skipped_count += 1
            continue
        
        # Import cho từng cặp giao dịch
        for pair in data.get('pairs', ['UNKNOWN']):
            backtest_entry = BacktestResult(
                strategy_name=data['strategy_name'],
                pair=pair,
                start_date=data['start_date'],
                end_date=data['end_date'],
                timeframe=data['timeframe'],
                profit_percent=data['profit_percent'],
                profit_abs=data['profit_abs'],
                trades_count=data['trades_count'],
                win_rate=data['win_rate'],
                risk_reward_ratio=data['risk_reward_ratio'],
                average_duration=data['average_duration'],
                trades_data=data['trades_data'],
                parameters=data['parameters'],
                file_path=file_path,
                import_date=datetime.now(),
                is_used_for_training=False
            )
            
            session.add(backtest_entry)
        
        # Lưu vào database
        try:
            session.commit()
            logger.info(f"Đã import backtest: {os.path.basename(file_path)}")
            imported_count += 1
        except Exception as e:
            session.rollback()
            logger.error(f"Lỗi khi import backtest {file_path}: {str(e)}")
            skipped_count += 1
    
    session.close()
    logger.info(f"Hoàn tất: Đã import {imported_count}/{total_files} files, bỏ qua {skipped_count} files")


def prepare_training_data(strategy_name: str, pair: str, min_trades: int = 20) -> Optional[pd.DataFrame]:
    """
    Chuẩn bị dữ liệu huấn luyện từ kết quả backtest
    
    Args:
        strategy_name: Tên chiến lược
        pair: Cặp giao dịch
        min_trades: Số lượng giao dịch tối thiểu để đưa vào huấn luyện
        
    Returns:
        DataFrame chứa dữ liệu đã chuẩn bị hoặc None nếu không đủ dữ liệu
    """
    # Kết nối database
    session = connect_to_database()
    
    # Lấy tất cả kết quả backtest cho chiến lược và cặp giao dịch
    results = session.query(BacktestResult).filter_by(
        strategy_name=strategy_name,
        pair=pair
    ).all()
    
    if not results:
        logger.error(f"Không tìm thấy kết quả backtest cho {strategy_name} với cặp {pair}")
        session.close()
        return None
    
    # Tổng hợp dữ liệu từ tất cả các kết quả
    all_trades = []
    
    for result in results:
        # Kiểm tra xem có dữ liệu giao dịch không
        if not result.trades_data:
            continue
        
        # Thêm tham số chiến lược vào mỗi giao dịch
        parameters = result.parameters or {}
        trades = result.trades_data
        
        for trade in trades:
            # Chỉ lấy các giao dịch của cặp đang xét
            if trade.get('pair') != pair:
                continue
                
            # Kết hợp thông tin giao dịch với tham số
            trade_data = {
                'trade_id': trade.get('trade_id'),
                'pair': trade.get('pair'),
                'open_time': trade.get('open_date'),
                'close_time': trade.get('close_date'),
                'open_rate': trade.get('open_rate'),
                'close_rate': trade.get('close_rate'),
                'profit_percent': trade.get('profit_percent'),
                'profit_abs': trade.get('profit_abs'),
                'trade_duration': trade.get('trade_duration'),
                'is_profitable': trade.get('profit_percent', 0) > 0,
            }
            
            # Thêm các thông số chiến lược
            for param_name, param_value in parameters.items():
                # Chỉ lấy các tham số số học để huấn luyện
                if isinstance(param_value, (int, float)):
                    trade_data[f'param_{param_name}'] = param_value
            
            all_trades.append(trade_data)
    
    session.close()
    
    # Kiểm tra đủ dữ liệu
    if len(all_trades) < min_trades:
        logger.warning(f"Không đủ giao dịch để huấn luyện ({len(all_trades)}/{min_trades})")
        return None
    
    # Chuyển thành DataFrame
    df = pd.DataFrame(all_trades)
    
    # Xử lý dữ liệu nếu cần
    logger.info(f"Đã chuẩn bị {len(df)} giao dịch cho huấn luyện")
    
    return df


def generate_training_features(df: pd.DataFrame) -> Optional[tuple]:
    """
    Tạo features và target cho huấn luyện AI
    
    Args:
        df: DataFrame chứa dữ liệu giao dịch từ backtest
        
    Returns:
        Tuple (X, y) cho huấn luyện AI hoặc None nếu không tạo được
    """
    try:
        # Kiểm tra và lọc cột
        param_columns = [col for col in df.columns if col.startswith('param_')]
        
        if not param_columns:
            logger.error("Không tìm thấy tham số chiến lược trong dữ liệu")
            return None
        
        # Tạo features (X) và target (y)
        X = df[param_columns].copy()
        y = df['is_profitable'].astype(int).copy()
        
        # Thông tin về feature engineering
        logger.info(f"Đã tạo {len(X.columns)} features từ các tham số chiến lược:")
        for col in X.columns:
            logger.info(f"  - {col}")
            
        # Thống kê cơ bản
        positive_rate = y.mean() * 100
        logger.info(f"Tỷ lệ giao dịch có lợi nhuận: {positive_rate:.2f}%")
        
        return X, y
    
    except Exception as e:
        logger.error(f"Lỗi khi tạo features: {str(e)}")
        return None


def parse_args():
    """Phân tích tham số dòng lệnh"""
    parser = argparse.ArgumentParser(description="Import dữ liệu backtest từ Freqtrade")
    
    # Các tham số chung
    parser.add_argument(
        "--dir",
        type=str,
        default=os.path.expanduser("~/freqtrade/user_data/backtest_results"),
        help="Thư mục chứa kết quả backtest"
    )
    
    # Lệnh phụ
    subparsers = parser.add_subparsers(dest="command", help="Lệnh cần thực hiện")
    
    # Lệnh import
    import_parser = subparsers.add_parser("import", help="Import kết quả backtest")
    import_parser.add_argument(
        "--strategy",
        type=str,
        help="Chỉ import cho chiến lược cụ thể"
    )
    
    # Lệnh prepare
    prepare_parser = subparsers.add_parser("prepare", help="Chuẩn bị dữ liệu huấn luyện")
    prepare_parser.add_argument(
        "--strategy",
        type=str,
        required=True,
        help="Tên chiến lược"
    )
    prepare_parser.add_argument(
        "--pair",
        type=str,
        required=True,
        help="Cặp giao dịch"
    )
    prepare_parser.add_argument(
        "--min-trades",
        type=int,
        default=20,
        help="Số lượng giao dịch tối thiểu cần để huấn luyện"
    )
    prepare_parser.add_argument(
        "--output",
        type=str,
        help="File CSV để lưu dữ liệu đã chuẩn bị"
    )
    
    return parser.parse_args()


def main():
    """Hàm chính"""
    args = parse_args()
    
    if args.command == "import":
        import_backtest_results(args.dir, args.strategy)
        
    elif args.command == "prepare":
        df = prepare_training_data(args.strategy, args.pair, args.min_trades)
        
        if df is not None and args.output:
            # Lưu DataFrame ra file CSV nếu có đường dẫn đầu ra
            df.to_csv(args.output, index=False)
            logger.info(f"Đã lưu dữ liệu huấn luyện vào {args.output}")
            
            # Thử tạo features và target
            result = generate_training_features(df)
            if result:
                X, y = result
                logger.info(f"Đã chuẩn bị thành công dữ liệu huấn luyện: {X.shape[0]} mẫu, {X.shape[1]} features")
    
    else:
        logger.error("Hãy chọn lệnh: import hoặc prepare")


if __name__ == "__main__":
    main()