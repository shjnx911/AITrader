"""
Công cụ kết nối dữ liệu giữa AITradeStrategist và Freqtrade.
Script này có thể được sử dụng để đồng bộ dữ liệu từ database của Freqtrade 
vào database của AITradeStrategist.
"""
import os
import json
import logging
import pandas as pd
from datetime import datetime
from typing import List, Dict, Any, Optional, Union
from sqlalchemy import create_engine, text, Column, Integer, String, Float, DateTime, JSON, Boolean
from sqlalchemy.orm import Session, declarative_base
from sqlalchemy.exc import SQLAlchemyError

logger = logging.getLogger(__name__)

class FreqtradeDBConnector:
    """Kết nối và đọc dữ liệu từ database của Freqtrade"""
    
    def __init__(self, db_url: Optional[str] = None, sqlite_path: Optional[str] = None):
        """
        Khởi tạo kết nối DB
        
        Args:
            db_url: Chuỗi kết nối database (PostgreSQL)
            sqlite_path: Đường dẫn đến file SQLite của Freqtrade
        """
        self.db_url = db_url
        self.sqlite_path = sqlite_path
        self.engine = None
        
    def connect(self) -> bool:
        """
        Kết nối đến database
        
        Returns:
            True nếu kết nối thành công, False nếu không
        """
        try:
            if self.db_url:
                # Sử dụng PostgreSQL
                self.engine = create_engine(self.db_url)
            elif self.sqlite_path:
                # Sử dụng SQLite
                self.engine = create_engine(f"sqlite:///{self.sqlite_path}")
            else:
                logger.error("Không có thông tin kết nối database")
                return False
                
            # Kiểm tra kết nối
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
                
            logger.info("Kết nối database Freqtrade thành công")
            return True
            
        except Exception as e:
            logger.error(f"Lỗi kết nối database Freqtrade: {str(e)}")
            return False
    
    def disconnect(self):
        """Đóng kết nối database"""
        if self.engine:
            self.engine.dispose()
            logger.info("Đã đóng kết nối database Freqtrade")
    
    def get_trades(self, limit: int = 500) -> pd.DataFrame:
        """
        Lấy dữ liệu giao dịch từ Freqtrade
        
        Args:
            limit: Số lượng giao dịch tối đa
            
        Returns:
            DataFrame chứa dữ liệu giao dịch
        """
        if not self.engine:
            if not self.connect():
                return pd.DataFrame()
        
        try:
            query = f"""
                SELECT * FROM trades 
                ORDER BY close_date DESC 
                LIMIT {limit}
            """
            
            df = pd.read_sql(query, self.engine)
            logger.info(f"Đã lấy {len(df)} giao dịch từ Freqtrade")
            return df
            
        except Exception as e:
            logger.error(f"Lỗi lấy dữ liệu giao dịch từ Freqtrade: {str(e)}")
            return pd.DataFrame()
    
    def get_pairs(self) -> List[str]:
        """
        Lấy danh sách các cặp giao dịch từ database
        
        Returns:
            Danh sách các cặp giao dịch
        """
        if not self.engine:
            if not self.connect():
                return []
        
        try:
            query = """
                SELECT DISTINCT pair FROM trades
                ORDER BY pair
            """
            
            df = pd.read_sql(query, self.engine)
            pairs = df['pair'].tolist()
            logger.info(f"Đã lấy {len(pairs)} cặp giao dịch từ Freqtrade")
            return pairs
            
        except Exception as e:
            logger.error(f"Lỗi lấy danh sách cặp giao dịch từ Freqtrade: {str(e)}")
            return []
    
    def get_strategy_performance(self, strategy_name: Optional[str] = None) -> pd.DataFrame:
        """
        Lấy thông tin hiệu suất của chiến lược
        
        Args:
            strategy_name: Tên chiến lược (không bắt buộc)
            
        Returns:
            DataFrame chứa dữ liệu hiệu suất theo chiến lược
        """
        if not self.engine:
            if not self.connect():
                return pd.DataFrame()
        
        try:
            query = """
                SELECT 
                    pair,
                    strategy,
                    COUNT(*) as total_trades,
                    SUM(CASE WHEN close_profit > 0 THEN 1 ELSE 0 END) as win_trades,
                    SUM(CASE WHEN close_profit <= 0 THEN 1 ELSE 0 END) as loss_trades,
                    AVG(close_profit) * 100 as avg_profit_pct,
                    SUM(close_profit_abs) as total_profit_abs,
                    AVG(close_profit_abs) as avg_profit_abs,
                    MIN(close_date) as start_date,
                    MAX(close_date) as end_date
                FROM trades
                WHERE close_date IS NOT NULL
            """
            
            if strategy_name:
                query += f" AND strategy = '{strategy_name}'"
                
            query += " GROUP BY pair, strategy ORDER BY pair"
            
            df = pd.read_sql(query, self.engine)
            df['win_rate'] = (df['win_trades'] / df['total_trades']) * 100
            
            logger.info(f"Đã lấy hiệu suất của {len(df)} cặp giao dịch từ Freqtrade")
            return df
            
        except Exception as e:
            logger.error(f"Lỗi lấy dữ liệu hiệu suất từ Freqtrade: {str(e)}")
            return pd.DataFrame()


class AITradeStrategistDBConnector:
    """Kết nối và ghi dữ liệu vào database của AITradeStrategist"""
    
    def __init__(self, db_url: Optional[str] = None):
        """
        Khởi tạo kết nối DB
        
        Args:
            db_url: Chuỗi kết nối database (PostgreSQL)
        """
        self.db_url = db_url or os.environ.get('DATABASE_URL')
        self.engine = None
        
    def connect(self) -> bool:
        """
        Kết nối đến database
        
        Returns:
            True nếu kết nối thành công, False nếu không
        """
        try:
            if not self.db_url:
                logger.error("Không có thông tin kết nối database")
                return False
                
            self.engine = create_engine(self.db_url)
            
            # Kiểm tra kết nối
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
                
            logger.info("Kết nối database AITradeStrategist thành công")
            return True
            
        except Exception as e:
            logger.error(f"Lỗi kết nối database AITradeStrategist: {str(e)}")
            return False
    
    def disconnect(self):
        """Đóng kết nối database"""
        if self.engine:
            self.engine.dispose()
            logger.info("Đã đóng kết nối database AITradeStrategist")
    
    def import_trading_pairs(self, pairs: List[str]) -> bool:
        """
        Import danh sách cặp giao dịch vào database
        
        Args:
            pairs: Danh sách các cặp giao dịch
            
        Returns:
            True nếu thành công, False nếu không
        """
        if not self.engine:
            if not self.connect():
                return False
        
        try:
            # Tạo query để thêm cặp giao dịch vào bảng trading_pairs (giả sử bảng này đã tồn tại)
            with Session(self.engine) as session:
                for pair in pairs:
                    # Kiểm tra xem cặp đã tồn tại chưa
                    result = session.execute(
                        text("SELECT 1 FROM trading_pairs WHERE pair = :pair"),
                        {"pair": pair}
                    ).fetchone()
                    
                    if not result:
                        # Thêm cặp mới
                        session.execute(
                            text("INSERT INTO trading_pairs (pair, is_active, created_date) VALUES (:pair, :is_active, :created_date)"),
                            {
                                "pair": pair, 
                                "is_active": True, 
                                "created_date": datetime.now()
                            }
                        )
                
                session.commit()
                
            logger.info(f"Đã import {len(pairs)} cặp giao dịch vào AITradeStrategist")
            return True
            
        except Exception as e:
            logger.error(f"Lỗi import cặp giao dịch vào AITradeStrategist: {str(e)}")
            return False
    
    def import_trading_metrics(self, metrics_df: pd.DataFrame) -> bool:
        """
        Import dữ liệu hiệu suất giao dịch vào database
        
        Args:
            metrics_df: DataFrame chứa dữ liệu hiệu suất
            
        Returns:
            True nếu thành công, False nếu không
        """
        if not self.engine:
            if not self.connect():
                return False
        
        try:
            # Tạo query để thêm dữ liệu vào bảng trading_metrics
            with Session(self.engine) as session:
                for _, row in metrics_df.iterrows():
                    # Tạo dữ liệu metrics chi tiết dưới dạng JSON
                    metrics_data = {
                        "win_rate": float(row.get('win_rate', 0)),
                        "avg_profit_pct": float(row.get('avg_profit_pct', 0)),
                        "avg_profit_abs": float(row.get('avg_profit_abs', 0)),
                    }
                    
                    # Thêm hoặc cập nhật dữ liệu
                    session.execute(
                        text("""
                            INSERT INTO trading_metrics 
                            (pair, timeframe, start_date, end_date, total_trades, win_trades, loss_trades, 
                             profit_percent, profit_abs, metrics_data, created_date)
                            VALUES 
                            (:pair, :timeframe, :start_date, :end_date, :total_trades, :win_trades, :loss_trades,
                             :profit_percent, :profit_abs, :metrics_data, :created_date)
                            ON CONFLICT (pair, timeframe, CAST(start_date AS DATE), CAST(end_date AS DATE))
                            DO UPDATE SET
                                total_trades = EXCLUDED.total_trades,
                                win_trades = EXCLUDED.win_trades,
                                loss_trades = EXCLUDED.loss_trades,
                                profit_percent = EXCLUDED.profit_percent,
                                profit_abs = EXCLUDED.profit_abs,
                                metrics_data = EXCLUDED.metrics_data
                        """),
                        {
                            "pair": row['pair'],
                            "timeframe": row.get('timeframe', '1d'),  # Mặc định là 1d
                            "start_date": row.get('start_date', datetime.now()),
                            "end_date": row.get('end_date', datetime.now()),
                            "total_trades": int(row.get('total_trades', 0)),
                            "win_trades": int(row.get('win_trades', 0)),
                            "loss_trades": int(row.get('loss_trades', 0)),
                            "profit_percent": float(row.get('avg_profit_pct', 0)),
                            "profit_abs": float(row.get('total_profit_abs', 0)),
                            "metrics_data": json.dumps(metrics_data),
                            "created_date": datetime.now()
                        }
                    )
                
                session.commit()
                
            logger.info(f"Đã import {len(metrics_df)} bản ghi hiệu suất vào AITradeStrategist")
            return True
            
        except Exception as e:
            logger.error(f"Lỗi import dữ liệu hiệu suất vào AITradeStrategist: {str(e)}")
            return False


def main():
    """Hàm main để chạy đồng bộ dữ liệu"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Kết nối đến Freqtrade
    freqtrade_db = FreqtradeDBConnector(
        db_url=os.environ.get('FREQTRADE_DB_URL'),
        sqlite_path=os.environ.get('FREQTRADE_SQLITE_PATH')
    )
    
    if not freqtrade_db.connect():
        logger.error("Không thể kết nối đến database Freqtrade, kết thúc chương trình")
        return
    
    # Kết nối đến AITradeStrategist
    ai_db = AITradeStrategistDBConnector(db_url=os.environ.get('DATABASE_URL'))
    
    if not ai_db.connect():
        logger.error("Không thể kết nối đến database AITradeStrategist, kết thúc chương trình")
        freqtrade_db.disconnect()
        return
    
    try:
        # Lấy danh sách cặp giao dịch
        pairs = freqtrade_db.get_pairs()
        if pairs:
            ai_db.import_trading_pairs(pairs)
        
        # Lấy dữ liệu hiệu suất
        performance_df = freqtrade_db.get_strategy_performance()
        if not performance_df.empty:
            ai_db.import_trading_metrics(performance_df)
            
        logger.info("Đồng bộ dữ liệu thành công")
        
    except Exception as e:
        logger.error(f"Lỗi đồng bộ dữ liệu: {str(e)}")
    
    finally:
        # Đóng kết nối
        freqtrade_db.disconnect()
        ai_db.disconnect()


if __name__ == "__main__":
    main()