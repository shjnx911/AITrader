#!/usr/bin/env python
"""
Script tạo file chiến lược Freqtrade dựa trên mô hình AI đã huấn luyện.
Mục đích là tạo một chiến lược có thể sử dụng trong Freqtrade với mô hình AI đã huấn luyện.
"""
import os
import argparse
import logging
import pickle
import json
from datetime import datetime
from typing import Dict, List, Optional, Any, Union
import string
import random
import shutil

# Thiết lập logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def load_model(model_path: str) -> Any:
    """
    Tải mô hình đã huấn luyện
    
    Args:
        model_path: Đường dẫn đến file mô hình
        
    Returns:
        Mô hình đã tải
    """
    try:
        with open(model_path, 'rb') as f:
            model = pickle.load(f)
        logger.info(f"Đã tải mô hình từ {model_path}")
        return model
    except Exception as e:
        logger.error(f"Lỗi khi tải mô hình: {str(e)}")
        return None


def load_metadata(model_path: str) -> Dict[str, Any]:
    """
    Tải metadata của mô hình
    
    Args:
        model_path: Đường dẫn đến file mô hình
        
    Returns:
        Metadata của mô hình
    """
    meta_path = os.path.splitext(model_path)[0] + '_meta.json'
    
    try:
        with open(meta_path, 'r') as f:
            metadata = json.load(f)
        logger.info(f"Đã tải metadata từ {meta_path}")
        return metadata
    except Exception as e:
        logger.error(f"Lỗi khi tải metadata: {str(e)}")
        return {}


def generate_strategy_code(
    model_path: str,
    strategy_name: str,
    base_strategy: str,
    pair: str,
    timeframe: str
) -> str:
    """
    Tạo mã nguồn chiến lược Freqtrade sử dụng mô hình AI
    
    Args:
        model_path: Đường dẫn đến file mô hình
        strategy_name: Tên chiến lược mới
        base_strategy: Tên chiến lược cơ sở
        pair: Cặp giao dịch
        timeframe: Khung thời gian
        
    Returns:
        Mã nguồn của chiến lược
    """
    # Tải mô hình và metadata
    model = load_model(model_path)
    if model is None:
        return None
        
    metadata = load_metadata(model_path)
    
    # Xác định đường dẫn đến file mô hình trong thư mục chiến lược
    model_filename = os.path.basename(model_path)
    strategy_dir = "user_data/strategies"
    model_rel_path = f"models/{model_filename}"
    
    # Tạo nội dung file chiến lược
    current_date = datetime.now().strftime("%Y-%m-%d")
    
    code = f"""
# --- Được tạo bởi AITradeStrategist vào {current_date} ---
# Chiến lược AI tự động dựa trên mô hình LightGBM đã huấn luyện với kết quả backtest
import os
import pickle
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
from freqtrade.strategy import IStrategy, IntParameter, DecimalParameter
from freqtrade.strategy import CategoricalParameter
from freqtrade.strategy.interface import IStrategy
import talib.abstract as ta
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class {strategy_name}(IStrategy):
    \"\"\"
    Chiến lược giao dịch được tạo tự động bởi AITradeStrategist.
    Sử dụng mô hình AI được huấn luyện cho cặp {pair} với timeframe {timeframe}.
    
    Chiến lược này dựa trên {base_strategy} nhưng sử dụng AI để dự đoán khả năng
    thành công của các giao dịch dựa trên phân tích mẫu từ kết quả backtest.
    \"\"\"
    
    # Thông tin meta
    minimal_roi = {metadata.get('parameters', {}).get('minimal_roi', {"0": 0.1})}
    stoploss = {metadata.get('parameters', {}).get('stoploss', -0.1)}
    timeframe = "{timeframe}"
    startup_candle_count: int = {metadata.get('parameters', {}).get('startup_candle_count', 30)}
    
    # Định nghĩa tham số
    ai_threshold = DecimalParameter(0.5, 0.9, default=0.65, space="buy", optimize=True)
    
    def __init__(self, config: dict) -> None:
        \"\"\"
        Khởi tạo chiến lược
        \"\"\"
        super().__init__(config)
        
        # Tải mô hình AI
        self.model = None
        self.load_ai_model()
        
        # Đánh dấu là đang sử dụng mô hình
        self.using_ai_model = self.model is not None
    
    def load_ai_model(self):
        \"\"\"
        Tải mô hình AI từ file
        \"\"\"
        try:
            # Xác định đường dẫn tương đối tới mô hình
            rel_path = "{model_rel_path}"
            
            # Tìm đường dẫn từ thư mục chiến lược
            strategy_dir = Path(__file__).parent
            model_path = strategy_dir / rel_path
            
            # Tải mô hình
            with open(model_path, 'rb') as f:
                self.model = pickle.load(f)
                
            # Cũng tải scaler nếu có
            if hasattr(self.model, 'scaler'):
                self.scaler = self.model.scaler
            else:
                self.scaler = None
                
            logger.info(f"Đã tải mô hình AI thành công từ {{model_path}}")
            
        except Exception as e:
            logger.error(f"Lỗi khi tải mô hình AI: {{e}}")
            self.model = None
    
    def populate_indicators(self, dataframe: pd.DataFrame, metadata: dict) -> pd.DataFrame:
        \"\"\"
        Tính toán các chỉ báo kỹ thuật
        \"\"\"
        # Thêm các chỉ báo cơ bản
        dataframe['rsi'] = ta.RSI(dataframe, timeperiod=14)
        dataframe['ema_9'] = ta.EMA(dataframe, timeperiod=9)
        dataframe['ema_21'] = ta.EMA(dataframe, timeperiod=21)
        dataframe['macd'], dataframe['macdsignal'], dataframe['macdhist'] = ta.MACD(
            dataframe['close'], fastperiod=12, slowperiod=26, signalperiod=9
        )
        dataframe['mfi'] = ta.MFI(
            dataframe['high'], dataframe['low'], dataframe['close'], dataframe['volume'], timeperiod=14
        )
        
        # Thêm các tính toán khác nếu cần
        
        return dataframe
    
    def extract_features(self, dataframe: pd.DataFrame, row_index: int) -> pd.DataFrame:
        \"\"\"
        Trích xuất các features cần thiết để dự đoán với mô hình AI
        \"\"\"
        feature_names = {metadata.get('feature_names', [])}
        
        # Nếu không có thông tin feature, sử dụng tất cả các chỉ báo
        if not feature_names:
            # Sử dụng các chỉ báo cơ bản
            features = {{
                'param_rsi': dataframe['rsi'].iloc[row_index],
                'param_mfi': dataframe['mfi'].iloc[row_index],
                'param_macd': dataframe['macd'].iloc[row_index],
                'param_macdsignal': dataframe['macdsignal'].iloc[row_index],
                'param_ema_ratio': dataframe['ema_9'].iloc[row_index] / dataframe['ema_21'].iloc[row_index],
            }}
        else:
            # Trích xuất theo feature names từ mô hình
            features = {{}}
            for feature in feature_names:
                if feature.startswith('param_'):
                    param_name = feature[6:]  # Bỏ tiền tố 'param_'
                    
                    # Tìm chỉ báo tương ứng trong dataframe
                    if param_name in dataframe.columns:
                        features[feature] = dataframe[param_name].iloc[row_index]
                    else:
                        # Thử các biến thế khác
                        if param_name == 'ema_ratio' and 'ema_9' in dataframe.columns and 'ema_21' in dataframe.columns:
                            features[feature] = dataframe['ema_9'].iloc[row_index] / dataframe['ema_21'].iloc[row_index]
                        else:
                            # Gán giá trị mặc định nếu không tìm thấy
                            features[feature] = 0
        
        # Chuyển thành DataFrame để dễ xử lý
        features_df = pd.DataFrame([features])
        return features_df
    
    def predict_with_ai(self, dataframe: pd.DataFrame, row_index: int) -> float:
        \"\"\"
        Sử dụng mô hình AI để dự đoán xác suất giao dịch thành công
        \"\"\"
        if not self.using_ai_model:
            return 0.5  # Giá trị mặc định nếu không có mô hình
            
        try:
            # Trích xuất features
            features = self.extract_features(dataframe, row_index)
            
            # Chuẩn hóa dữ liệu nếu có scaler
            if self.scaler is not None:
                features_scaled = self.scaler.transform(features)
            else:
                features_scaled = features.values
            
            # Dự đoán với mô hình
            prediction = self.model.predict(features_scaled)
            
            return prediction[0]  # Xác suất giao dịch thành công
            
        except Exception as e:
            logger.error(f"Lỗi khi dự đoán với mô hình AI: {{e}}")
            return 0.5  # Giá trị mặc định nếu có lỗi
    
    def populate_buy_trend(self, dataframe: pd.DataFrame, metadata: dict) -> pd.DataFrame:
        \"\"\"
        Xác định tín hiệu mua
        \"\"\"
        if not self.using_ai_model:
            # Logic mua mặc định nếu không có mô hình AI
            dataframe.loc[
                (
                    (dataframe['rsi'] < 30) &
                    (dataframe['macd'] > dataframe['macdsignal']) &
                    (dataframe['ema_9'] > dataframe['ema_21'])
                ),
                'buy'] = 1
            return dataframe
        
        # Sử dụng mô hình AI để dự đoán tín hiệu mua
        for index, row in dataframe.iterrows():
            # Chỉ áp dụng cho các hàng cuối cùng (để tránh dự đoán lại dữ liệu lịch sử)
            if index >= len(dataframe) - 10:
                prediction = self.predict_with_ai(dataframe, index)
                
                # Đánh dấu tín hiệu mua nếu xác suất cao hơn ngưỡng
                if prediction > self.ai_threshold.value:
                    dataframe.loc[index, 'buy'] = 1
        
        return dataframe
    
    def populate_sell_trend(self, dataframe: pd.DataFrame, metadata: dict) -> pd.DataFrame:
        \"\"\"
        Xác định tín hiệu bán
        \"\"\"
        # Logic bán đơn giản
        dataframe.loc[
            (
                (dataframe['rsi'] > 70) |
                (dataframe['macd'] < dataframe['macdsignal'])
            ),
            'sell'] = 1
        return dataframe
"""
    
    return code


def copy_model_file(model_path: str, target_dir: str) -> bool:
    """
    Sao chép file mô hình vào thư mục chiến lược
    
    Args:
        model_path: Đường dẫn đến file mô hình
        target_dir: Thư mục đích
        
    Returns:
        True nếu sao chép thành công, False nếu thất bại
    """
    try:
        # Tạo thư mục models nếu chưa tồn tại
        models_dir = os.path.join(target_dir, "models")
        os.makedirs(models_dir, exist_ok=True)
        
        # Sao chép file mô hình
        model_filename = os.path.basename(model_path)
        target_path = os.path.join(models_dir, model_filename)
        shutil.copy2(model_path, target_path)
        
        # Sao chép file metadata
        meta_path = os.path.splitext(model_path)[0] + '_meta.json'
        meta_filename = os.path.basename(meta_path)
        target_meta_path = os.path.join(models_dir, meta_filename)
        
        if os.path.exists(meta_path):
            shutil.copy2(meta_path, target_meta_path)
        
        logger.info(f"Đã sao chép mô hình vào {target_path}")
        return True
        
    except Exception as e:
        logger.error(f"Lỗi khi sao chép file mô hình: {str(e)}")
        return False


def generate_ai_strategy(
    model_path: str,
    strategy_name: Optional[str] = None,
    base_strategy: str = "DefaultStrategy",
    pair: Optional[str] = None,
    timeframe: Optional[str] = None,
    output_dir: Optional[str] = None
) -> str:
    """
    Tạo file chiến lược hoàn chỉnh
    
    Args:
        model_path: Đường dẫn đến file mô hình
        strategy_name: Tên chiến lược (tùy chọn)
        base_strategy: Tên chiến lược cơ sở
        pair: Cặp giao dịch (tùy chọn)
        timeframe: Khung thời gian (tùy chọn)
        output_dir: Thư mục đầu ra (tùy chọn)
        
    Returns:
        Đường dẫn đến file chiến lược đã tạo hoặc None nếu thất bại
    """
    # Tải metadata để lấy thông tin
    metadata = load_metadata(model_path)
    
    # Sử dụng thông tin từ metadata nếu không được cung cấp
    if not pair:
        pair = metadata.get('pair', 'BTC/USDT')
    
    if not timeframe:
        timeframe = metadata.get('timeframe', '1h')
    
    # Tạo tên chiến lược nếu không được cung cấp
    if not strategy_name:
        base_name = metadata.get('strategy_name', base_strategy)
        pair_code = pair.replace('/', '_').upper()
        random_suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
        strategy_name = f"AI_{base_name}_{pair_code}_{random_suffix}"
    
    # Tạo mã nguồn chiến lược
    code = generate_strategy_code(model_path, strategy_name, base_strategy, pair, timeframe)
    if code is None:
        return None
    
    # Xác định thư mục đầu ra
    if not output_dir:
        output_dir = os.path.join(os.getcwd(), "strategies", "ai_generated")
    
    os.makedirs(output_dir, exist_ok=True)
    
    # Tạo file chiến lược
    strategy_file = os.path.join(output_dir, f"{strategy_name}.py")
    
    try:
        with open(strategy_file, 'w') as f:
            f.write(code)
        
        logger.info(f"Đã tạo chiến lược {strategy_name} tại {strategy_file}")
        
        # Sao chép file mô hình
        if copy_model_file(model_path, output_dir):
            return strategy_file
        else:
            return None
            
    except Exception as e:
        logger.error(f"Lỗi khi tạo file chiến lược: {str(e)}")
        return None


def parse_args():
    """Phân tích tham số dòng lệnh"""
    parser = argparse.ArgumentParser(description="Tạo chiến lược AI cho Freqtrade")
    
    parser.add_argument(
        "--model",
        type=str,
        required=True,
        help="Đường dẫn đến file mô hình hoặc ID mô hình trong database"
    )
    
    parser.add_argument(
        "--strategy-name",
        type=str,
        help="Tên chiến lược (nếu không cung cấp, sẽ tạo tự động)"
    )
    
    parser.add_argument(
        "--base-strategy",
        type=str,
        default="DefaultStrategy",
        help="Tên chiến lược cơ sở"
    )
    
    parser.add_argument(
        "--pair",
        type=str,
        help="Cặp giao dịch (nếu không cung cấp, sẽ lấy từ metadata)"
    )
    
    parser.add_argument(
        "--timeframe",
        type=str,
        help="Khung thời gian (nếu không cung cấp, sẽ lấy từ metadata)"
    )
    
    parser.add_argument(
        "--output-dir",
        type=str,
        help="Thư mục đầu ra (mặc định: strategies/ai_generated)"
    )
    
    parser.add_argument(
        "--from-db",
        action="store_true",
        help="Tìm mô hình từ database thay vì từ file"
    )
    
    return parser.parse_args()


def get_model_path_from_database(model_id: int) -> Optional[str]:
    """
    Lấy đường dẫn đến file mô hình từ database
    
    Args:
        model_id: ID của mô hình trong database
        
    Returns:
        Đường dẫn đến file mô hình hoặc None nếu không tìm thấy
    """
    try:
        from main import ModelBackup, db
        
        # Tìm mô hình trong database
        model = db.session.query(ModelBackup).filter_by(id=model_id).first()
        
        if model:
            return model.backup_path
            
        logger.error(f"Không tìm thấy mô hình với ID {model_id} trong database")
        return None
        
    except Exception as e:
        logger.error(f"Lỗi khi tìm mô hình từ database: {str(e)}")
        return None


def main():
    """Hàm chính"""
    args = parse_args()
    
    # Xác định đường dẫn đến file mô hình
    model_path = args.model
    
    # Nếu lấy từ database
    if args.from_db:
        try:
            model_id = int(args.model)
            model_path = get_model_path_from_database(model_id)
            
            if not model_path:
                logger.error(f"Không tìm thấy mô hình với ID {model_id}")
                return
                
        except ValueError:
            logger.error(f"ID mô hình không hợp lệ: {args.model}")
            return
    
    # Tạo chiến lược
    strategy_file = generate_ai_strategy(
        model_path=model_path,
        strategy_name=args.strategy_name,
        base_strategy=args.base_strategy,
        pair=args.pair,
        timeframe=args.timeframe,
        output_dir=args.output_dir
    )
    
    if strategy_file:
        logger.info(f"Đã tạo thành công chiến lược AI tại: {strategy_file}")
    else:
        logger.error("Không thể tạo chiến lược AI")


if __name__ == "__main__":
    main()