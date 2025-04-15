#!/bin/bash

# Script để cài đặt các dependencies cần thiết cho AITradeStrategist
# Sử dụng: bash install_dependencies.sh

# Màu sắc cho output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}=== Cài đặt dependencies cho AITradeStrategist ===${NC}"
echo

# Kiểm tra môi trường ảo Freqtrade
if [ ! -d "./.env" ]; then
    echo -e "${RED}Không tìm thấy môi trường ảo Freqtrade (.env)${NC}"
    echo -e "${YELLOW}Bạn nên chạy script này từ thư mục gốc của Freqtrade${NC}"
    read -p "Tiếp tục cài đặt vào môi trường Python hiện tại? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${RED}Hủy cài đặt.${NC}"
        exit 1
    fi
    PYTHON_CMD="python"
    PIP_CMD="pip"
else
    echo -e "${GREEN}Phát hiện môi trường ảo Freqtrade${NC}"
    PYTHON_CMD="./.env/bin/python"
    PIP_CMD="./.env/bin/pip"
fi

# Cài đặt các gói phụ thuộc Python
echo -e "${YELLOW}Cài đặt các gói phụ thuộc Python...${NC}"
$PIP_CMD install --upgrade pip
$PIP_CMD install flask flask-sqlalchemy psycopg2-binary python-dotenv gunicorn email-validator

# Kiểm tra GPU và cài đặt các gói liên quan
echo -e "${YELLOW}Kiểm tra GPU...${NC}"
if [ "$(command -v nvidia-smi)" ]; then
    echo -e "${GREEN}Phát hiện NVIDIA GPU${NC}"
    $PIP_CMD install lightgbm --install-option=--gpu
    $PIP_CMD install skl2onnx onnxruntime-gpu
elif [ "$(command -v rocm-smi)" ] || [ -d "/opt/rocm" ]; then
    echo -e "${GREEN}Phát hiện AMD GPU với ROCm${NC}"
    $PIP_CMD install torch-directml
    $PIP_CMD install lightgbm
    $PIP_CMD install skl2onnx onnxruntime
else
    echo -e "${YELLOW}Không phát hiện GPU hỗ trợ. Cài đặt phiên bản CPU.${NC}"
    $PIP_CMD install lightgbm
    $PIP_CMD install skl2onnx onnxruntime
fi

# Cấu hình cơ sở dữ liệu
echo -e "${YELLOW}Kiểm tra cấu hình cơ sở dữ liệu...${NC}"
if [ -f ".env" ]; then
    echo -e "${GREEN}Tìm thấy file .env${NC}"
else
    echo -e "${YELLOW}Tạo file .env...${NC}"
    cat > .env << EOL
# OpenAI API Key
OPENAI_API_KEY=your_openai_api_key_here

# Database Configuration
DATABASE_URL=sqlite:///tradesys.db
# Uncomment để sử dụng PostgreSQL
# DATABASE_URL=postgresql://username:password@localhost:5432/freqai_db

# Application Settings
FLASK_SECRET_KEY=`openssl rand -hex 24`
DEBUG=True
LOG_LEVEL=INFO

# Trading Configuration
DEFAULT_PAIR=BTC/USDT
DEFAULT_TIMEFRAME=1h
EXCHANGE=binance
TRADING_MODE=futures

# Resources Management
MAX_CPU_USAGE=80
MAX_RAM_USAGE=80
MAX_GPU_USAGE=80
TRADING_PRIORITY=high
TRAINING_PRIORITY=medium
BACKTEST_PRIORITY=low

# Model Settings
DEFAULT_MODEL=LightGBM
USE_GPU=True
USE_ONNX=True
SAVE_BACKUPS=True
BACKUP_DIRECTORY=./model_backups
EOL
    echo -e "${GREEN}Đã tạo file .env${NC}"
fi

# Tạo thư mục cho backups và logs
mkdir -p model_backups logs

echo -e "${GREEN}Cài đặt hoàn tất!${NC}"
echo -e "${YELLOW}Khởi động ứng dụng: python main.py${NC}"