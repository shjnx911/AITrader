#!/usr/bin/env python
"""
Script cài đặt các gói phụ thuộc cần thiết cho tích hợp Freqtrade.
"""
import os
import sys
import subprocess
import logging
import argparse

# Thiết lập logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Danh sách các gói cần thiết
REQUIRED_PACKAGES = [
    'requests',
    'python-dotenv',
    'schedule',
    'pandas',
    'sqlalchemy',
    'flask',
]

# Danh sách các gói tùy chọn (cho một số tính năng nâng cao)
OPTIONAL_PACKAGES = [
    'websocket-client',  # Cho các kết nối websocket
    'plotly',            # Cho biểu đồ tương tác
    'numpy',             # Cho tính toán hiệu suất
]


def check_package_installed(package_name: str) -> bool:
    """
    Kiểm tra xem một gói đã được cài đặt chưa.
    
    Args:
        package_name: Tên gói cần kiểm tra
        
    Returns:
        True nếu gói đã được cài đặt, False nếu chưa
    """
    try:
        __import__(package_name.split('==')[0])
        return True
    except ImportError:
        return False


def install_packages(packages: list, optional: bool = False) -> bool:
    """
    Cài đặt các gói Python.
    
    Args:
        packages: Danh sách các gói cần cài đặt
        optional: Có phải là gói tùy chọn không
        
    Returns:
        True nếu cài đặt thành công, False nếu không
    """
    prefix = "Tùy chọn" if optional else "Bắt buộc"
    
    # Lọc các gói chưa được cài đặt
    packages_to_install = [pkg for pkg in packages if not check_package_installed(pkg.split('==')[0])]
    
    if not packages_to_install:
        logger.info(f"Tất cả các gói {prefix.lower()} đã được cài đặt")
        return True
    
    logger.info(f"Cài đặt {len(packages_to_install)} gói {prefix.lower()}: {', '.join(packages_to_install)}")
    
    try:
        cmd = [sys.executable, "-m", "pip", "install"] + packages_to_install
        
        if optional:
            # Cài đặt các gói tùy chọn với --no-deps để tránh xung đột
            cmd.append("--no-deps")
            
        subprocess.check_call(cmd)
        
        logger.info(f"Đã cài đặt thành công các gói {prefix.lower()}")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Lỗi khi cài đặt các gói {prefix.lower()}: {e}")
        return False


def create_dot_env_file():
    """
    Tạo file .env mẫu nếu chưa tồn tại.
    """
    env_file = os.path.join(os.getcwd(), '.env')
    
    if os.path.exists(env_file):
        logger.info("File .env đã tồn tại")
        return
    
    logger.info("Tạo file .env mẫu")
    
    sample_env = """# Freqtrade API thông tin kết nối
FREQTRADE_API_URL=http://localhost:8080
FREQTRADE_USERNAME=freqtrader
FREQTRADE_PASSWORD=your_password_here

# Database thông tin kết nối (chọn một trong hai)
# PostgreSQL
# DATABASE_URL=postgresql://user:pass@localhost:5432/freqtrade

# SQLite
# FREQTRADE_SQLITE_PATH=/path/to/freqtrade/tradesv3.sqlite

# GPU detection (1 = force enable, 0 = force disable)
# FORCE_GPU_DETECTION=0
"""
    
    try:
        with open(env_file, 'w') as f:
            f.write(sample_env)
        logger.info(f"Đã tạo file .env tại {env_file}")
    except Exception as e:
        logger.error(f"Lỗi khi tạo file .env: {e}")


def parse_args():
    """Phân tích tham số dòng lệnh"""
    parser = argparse.ArgumentParser(description="Cài đặt các gói phụ thuộc cho tích hợp Freqtrade")
    
    parser.add_argument(
        "--all",
        action="store_true",
        help="Cài đặt tất cả các gói, bao gồm cả gói tùy chọn"
    )
    
    parser.add_argument(
        "--env",
        action="store_true",
        help="Tạo file .env mẫu"
    )
    
    return parser.parse_args()


def main():
    """Hàm chính"""
    args = parse_args()
    
    # Cài đặt các gói bắt buộc
    if not install_packages(REQUIRED_PACKAGES):
        logger.error("Không thể cài đặt các gói bắt buộc")
        sys.exit(1)
    
    # Cài đặt các gói tùy chọn nếu được yêu cầu
    if args.all:
        if not install_packages(OPTIONAL_PACKAGES, optional=True):
            logger.warning("Không thể cài đặt một số gói tùy chọn")
    
    # Tạo file .env
    if args.env:
        create_dot_env_file()
    
    logger.info("Cài đặt hoàn tất")


if __name__ == "__main__":
    main()