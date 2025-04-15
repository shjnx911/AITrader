# Hướng dẫn tích hợp AITradeStrategist với Freqtrade

## 1. Giới thiệu

Tài liệu này hướng dẫn chi tiết cách tích hợp AITradeStrategist với Freqtrade để tận dụng:
- Các chiến lược AI (LightGBM) với FreqAI
- Hỗ trợ tăng tốc GPU cho AMD thông qua DirectML
- Giao diện web quản lý mô hình và theo dõi hiệu suất

## 2. Yêu cầu hệ thống

- Python 3.8+
- Freqtrade 2023.3+
- PostgreSQL 13+ (khuyến nghị) hoặc SQLite
- CUDA 11.2+ hoặc AMD ROCm/DirectML (tùy chọn cho hỗ trợ GPU)

## 3. Cài đặt

### 3.1. Cài đặt Freqtrade

Nếu bạn chưa cài đặt Freqtrade, hãy làm theo hướng dẫn chính thức tại: 
https://www.freqtrade.io/en/stable/installation/

```bash
git clone https://github.com/freqtrade/freqtrade.git
cd freqtrade
./setup.sh -i
```

### 3.2. Cài đặt AITradeStrategist

```bash
# Đi đến thư mục Freqtrade
cd freqtrade

# Tải mã nguồn AITradeStrategist
git clone https://github.com/shjnx911/AITradeStrategist.git UI

# Cài đặt dependencies
cd UI
bash install_dependencies.sh
```

## 4. Cấu hình

### 4.1. Thiết lập cơ sở dữ liệu

Để sử dụng PostgreSQL (khuyến nghị):

```bash
# Tạo database
sudo -u postgres createdb freqai_db
sudo -u postgres psql -c "CREATE USER freqai WITH PASSWORD 'yourpassword';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE freqai_db TO freqai;"

# Cập nhật file .env
# DATABASE_URL=postgresql://freqai:yourpassword@localhost:5432/freqai_db
```

### 4.2. Thiết lập FreqAI trong Freqtrade

Sao chép file cấu hình mẫu:

```bash
cp UI/freqtrade_integration/config_examples/freqai_config.json user_data/config.json
```

Chỉnh sửa cấu hình theo nhu cầu:
- Thêm API key/secret của sàn giao dịch
- Điều chỉnh cặp giao dịch
- Cấu hình chiến lược

### 4.3. Sao chép chiến lược FreqAI LightGBM

```bash
cp UI/strategies/freqai_lightgbm_strategy.py user_data/strategies/
```

## 5. Khởi chạy

### 5.1. Khởi động Freqtrade

```bash
# Chế độ backtest
freqtrade backtesting --config user_data/config.json --strategy FreqAI_LGBM_Strategy

# Hoặc chế độ dry-run
freqtrade trade --config user_data/config.json --strategy FreqAI_LGBM_Strategy
```

### 5.2. Khởi động Web UI

```bash
cd UI
python main_integration.py
```

Giao diện web sẽ chạy tại: http://localhost:5000

## 6. Tích hợp nâng cao

### 6.1. Sử dụng GPU AMD với DirectML

1. Đảm bảo đã cài đặt driver AMD mới nhất
2. Cài đặt thư viện hỗ trợ:
   ```bash
   pip install torch-directml
   ```
3. Thiết lập biến môi trường:
   ```bash
   export USE_GPU=True
   ```

### 6.2. Tối ưu hóa mô hình với ONNX

1. Đảm bảo đã cài đặt thư viện ONNX:
   ```bash
   pip install onnxruntime onnxruntime-gpu skl2onnx
   ```
2. Trong cấu hình FreqAI, bật tính năng ONNX:
   ```json
   "onnx_parameters": {
       "activate_onnx_export": true,
       "output_directory": "user_data/models/onnx/"
   }
   ```

### 6.3. Tích hợp Telegram Alerts

1. Thêm cấu hình Telegram trong file config.json
2. Kết nối webhook từ Web UI đến bot Telegram

## 7. Xử lý sự cố

### 7.1. Vấn đề về cơ sở dữ liệu

Kiểm tra kết nối:
```bash
psql -h localhost -U freqai -d freqai_db
```

Nếu gặp lỗi, kiểm tra file logs:
```bash
cat logs/freqai_db.log
```

### 7.2. Vấn đề về GPU

Chạy script chẩn đoán:
```bash
python -c "from utils.gpu_utils import check_amd_gpu_support; print(check_amd_gpu_support())"
```

### 7.3. Xung đột phiên bản

Nếu có xung đột phiên bản, thử cài đặt trong môi trường ảo riêng:
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## 8. Tham khảo

- [Tài liệu Freqtrade](https://www.freqtrade.io/en/stable/)
- [Tài liệu FreqAI](https://www.freqtrade.io/en/stable/freqai/)
- [LightGBM với GPU](https://lightgbm.readthedocs.io/en/latest/GPU-Tutorial.html)
- [DirectML cho AMD GPU](https://learn.microsoft.com/en-us/windows/ai/directml/gpu-tensorflow-plugin)