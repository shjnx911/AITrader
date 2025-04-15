# Tích hợp AITradeStrategist với Freqtrade

Module này cung cấp các công cụ để tích hợp AITradeStrategist với Freqtrade, cho phép:

1. Kết nối đến Freqtrade API để điều khiển bot
2. Đồng bộ dữ liệu từ database của Freqtrade vào AITradeStrategist
3. Sử dụng mô hình AI của AITradeStrategist để cải thiện chiến lược giao dịch của Freqtrade

## Cài đặt và cấu hình

### 1. Cài đặt Freqtrade

Nếu bạn chưa cài đặt Freqtrade, hãy thực hiện các bước sau:

```bash
git clone https://github.com/freqtrade/freqtrade.git
cd freqtrade
./setup.sh -i
```

### 2. Cấu hình Freqtrade

Tạo file cấu hình `config.json` trong thư mục freqtrade:

```json
{
    "max_open_trades": 5,
    "stake_currency": "USDT",
    "stake_amount": 100,
    "tradable_balance_ratio": 0.99,
    "timeframe": "5m",
    "dry_run": true,
    "dry_run_wallet": 1000,
    "cancel_open_orders_on_exit": false,
    "bid_strategy": {
        "price_side": "bid",
        "ask_last_balance": 0.0,
        "use_order_book": false,
        "order_book_top": 1
    },
    "ask_strategy": {
        "price_side": "ask",
        "use_order_book": false,
        "order_book_top": 1
    },
    "exchange": {
        "name": "binance",
        "key": "",
        "secret": "",
        "ccxt_config": {},
        "ccxt_async_config": {},
        "pair_whitelist": [
            "BTC/USDT",
            "ETH/USDT",
            "ADA/USDT"
        ],
        "pair_blacklist": []
    },
    "api_server": {
        "enabled": true,
        "listen_ip_address": "0.0.0.0",
        "listen_port": 8080,
        "verbosity": "info",
        "jwt_secret_key": "tạo_một_khóa_ngẫu_nhiên_ở_đây",
        "CORS_origins": ["http://localhost:5000"],
        "username": "freqtrader",
        "password": "password_mạnh"
    },
    "bot_name": "freqtrade",
    "initial_state": "running",
    "forcebuy_enable": true,
    "internals": {
        "process_throttle_secs": 5
    }
}
```

Thay thế các giá trị tương ứng như:
- `jwt_secret_key`: một chuỗi ngẫu nhiên để bảo mật JWT
- `username` và `password`: thông tin đăng nhập API
- Thêm API key và secret nếu giao dịch thật

### 3. Thiết lập biến môi trường

Tạo file `.env` hoặc thiết lập biến môi trường:

```
# Thông tin kết nối Freqtrade API
FREQTRADE_API_URL=http://localhost:8080
FREQTRADE_USERNAME=freqtrader
FREQTRADE_PASSWORD=password_mạnh

# Thông tin kết nối Freqtrade Database
FREQTRADE_DB_URL=postgresql://user:pass@localhost:5432/freqtrade
# Hoặc sử dụng SQLite
FREQTRADE_SQLITE_PATH=/path/to/freqtrade/tradesv3.sqlite
```

### 4. Tạo các bảng cần thiết trong AITradeStrategist

Chạy script tạo bảng:

```bash
python freqtrade_integration/create_tables.py
```

## Sử dụng tích hợp

### 1. Khởi động Freqtrade

```bash
cd freqtrade
freqtrade trade -c config.json
```

### 2. Đồng bộ dữ liệu từ Freqtrade

Bạn có thể đồng bộ dữ liệu một lần:

```bash
python freqtrade_integration/sync_data.py --once
```

Hoặc thiết lập đồng bộ tự động mỗi 30 phút:

```bash
python freqtrade_integration/sync_data.py --interval 30
```

### 3. Sử dụng API trong AITradeStrategist

Để sử dụng API Freqtrade trong AITradeStrategist, đăng ký các route:

```python
from freqtrade_integration.api_routes import register_freqtrade_api_routes

# Trong hàm tạo app Flask
def create_app():
    app = Flask(__name__)
    # ... cấu hình khác ...
    
    # Đăng ký các route Freqtrade API
    register_freqtrade_api_routes(app)
    
    return app
```

Sau đó, bạn có thể truy cập các API endpoint:
- `GET /api/freqtrade/status`: Trạng thái bot
- `GET /api/freqtrade/trades`: Danh sách giao dịch
- `GET /api/freqtrade/profit`: Thống kê lợi nhuận
- `GET /api/freqtrade/pairs`: Danh sách cặp giao dịch
- `GET /api/freqtrade/performance`: Hiệu suất giao dịch
- `POST /api/freqtrade/start`: Khởi động bot
- `POST /api/freqtrade/stop`: Dừng bot
- `POST /api/freqtrade/forcebuy`: Force buy một cặp giao dịch
- `POST /api/freqtrade/forcesell`: Force sell một giao dịch

## Tạo chiến lược tùy chỉnh

### 1. Tạo chiến lược sử dụng mô hình AITradeStrategist

```python
# freqtrade/user_data/strategies/ai_trade_strategist.py
import logging
import requests
from datetime import datetime
from freqtrade.strategy import IStrategy, IntParameter, DecimalParameter
from pandas import DataFrame

logger = logging.getLogger(__name__)

class AITradeStrategistStrategy(IStrategy):
    """
    Chiến lược giao dịch sử dụng AI từ AITradeStrategist
    """
    minimal_roi = {
        "0": 0.01
    }
    
    stoploss = -0.05
    timeframe = '1h'
    process_only_new_candles = True
    
    # Tham số có thể tùy chỉnh
    leverage = IntParameter(1, 5, default=1)
    
    def __init__(self, config: dict) -> None:
        super().__init__(config)
        self.ai_api_url = config.get('ai_api_url', 'http://localhost:5000/api/prediction')
    
    def informative_pairs(self):
        return []
    
    def get_ai_prediction(self, pair: str, dataframe: DataFrame):
        """Lấy dự đoán từ API AITradeStrategist"""
        try:
            # Trích xuất dữ liệu gần nhất
            last_candle = dataframe.iloc[-1].to_dict()
            
            # Gửi request đến API
            response = requests.post(
                self.ai_api_url,
                json={
                    'pair': pair,
                    'data': {
                        'open': float(last_candle['open']),
                        'high': float(last_candle['high']),
                        'low': float(last_candle['low']),
                        'close': float(last_candle['close']),
                        'volume': float(last_candle['volume']),
                        'date': datetime.fromtimestamp(last_candle['date']).isoformat()
                    }
                },
                timeout=5
            )
            
            if response.status_code == 200:
                prediction = response.json()
                logger.info(f"AI prediction for {pair}: {prediction}")
                return prediction
            else:
                logger.error(f"Error getting AI prediction: {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Exception getting AI prediction: {str(e)}")
            return None
    
    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """Thêm các chỉ báo vào dataframe"""
        # Thêm các chỉ báo thông thường (nếu cần)
        
        return dataframe
    
    def populate_buy_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """Xác định xu hướng mua dựa trên dự đoán AI"""
        # Lấy dự đoán từ API
        pair = metadata['pair']
        prediction = self.get_ai_prediction(pair, dataframe)
        
        # Mặc định, không có tín hiệu mua
        dataframe['buy'] = 0
        
        # Nếu có dự đoán và dự đoán là mua
        if prediction and prediction.get('action') == 'buy' and prediction.get('probability', 0) > 0.7:
            # Tạo tín hiệu mua cho candle gần nhất
            dataframe.loc[dataframe.index[-1], 'buy'] = 1
            logger.info(f"Generated BUY signal for {pair} with probability {prediction.get('probability')}")
        
        return dataframe
    
    def populate_sell_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """Xác định xu hướng bán dựa trên dự đoán AI"""
        # Lấy dự đoán từ API
        pair = metadata['pair']
        prediction = self.get_ai_prediction(pair, dataframe)
        
        # Mặc định, không có tín hiệu bán
        dataframe['sell'] = 0
        
        # Nếu có dự đoán và dự đoán là bán
        if prediction and prediction.get('action') == 'sell' and prediction.get('probability', 0) > 0.7:
            # Tạo tín hiệu bán cho candle gần nhất
            dataframe.loc[dataframe.index[-1], 'sell'] = 1
            logger.info(f"Generated SELL signal for {pair} with probability {prediction.get('probability')}")
        
        return dataframe
```

### 2. Tạo API endpoint dự đoán trong AITradeStrategist

```python
# Trong AITradeStrategist, thêm endpoint dự đoán
@app.route('/api/prediction', methods=['POST'])
def predict():
    """API endpoint để cung cấp dự đoán cho Freqtrade"""
    data = request.json
    
    if not data or 'pair' not in data or 'data' not in data:
        return jsonify({'error': 'Missing required data'}), 400
    
    pair = data['pair']
    candle_data = data['data']
    
    # Thực hiện dự đoán sử dụng mô hình AI
    prediction = predict_with_model(pair, candle_data)
    
    return jsonify(prediction)
```

## Giám sát và quản lý

Bạn có thể giám sát trạng thái của Freqtrade thông qua giao diện web của AITradeStrategist bằng cách:

1. Truy cập Freqtrade Status trong giao diện
2. Xem các biểu đồ hiệu suất được đồng bộ tự động
3. Theo dõi lịch sử giao dịch
4. Quản lý cài đặt kết nối Freqtrade

## Xử lý lỗi thường gặp

1. **Không thể kết nối đến Freqtrade API**
   - Kiểm tra xem Freqtrade có đang chạy không
   - Xác nhận cấu hình API server trong config.json
   - Xác minh thông tin đăng nhập API (username, password)

2. **Không thể kết nối đến Freqtrade Database**
   - Kiểm tra chuỗi kết nối database
   - Xác nhận quyền truy cập database
   - Với SQLite, kiểm tra đường dẫn file

3. **Lỗi đồng bộ dữ liệu**
   - Đảm bảo các bảng cần thiết đã được tạo
   - Kiểm tra định dạng dữ liệu
   - Kiểm tra nhật ký đồng bộ trong file sync_freqtrade_data.log