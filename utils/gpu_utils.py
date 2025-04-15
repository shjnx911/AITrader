"""
Utility functions for GPU detection and DirectML integration with LightGBM.
"""
import os
import subprocess
import logging
import sys
from typing import Any, List, Optional

logger = logging.getLogger(__name__)

def check_amd_gpu_support() -> bool:
    """
    Check if AMD GPU is available and can be used with DirectML.
    
    Returns:
        bool: True if AMD GPU is available, False otherwise
    """
    try:
        # Kiểm tra biến môi trường để xem có thiết lập cưỡng chế nào không
        forced_gpu = os.environ.get('FORCE_GPU_DETECTION')
        if forced_gpu:
            logger.info(f"Using forced GPU detection value: {forced_gpu}")
            return forced_gpu.lower() in ('1', 'true', 'yes', 'on')
            
        # Kiểm tra GPU trên Linux
        if sys.platform.startswith('linux'):
            try:
                # Kiểm tra xem lspci có sẵn không
                subprocess.run(['which', 'lspci'], check=True, capture_output=True)
                
                # Sử dụng lspci để kiểm tra card GPU AMD
                output = subprocess.check_output("lspci | grep -E 'VGA|3D|Display' | grep -i AMD", shell=True)
                return b'AMD' in output or b'Radeon' in output
            except subprocess.CalledProcessError:
                logger.warning("lspci command not available - using alternative check method")
                # Kiểm tra thư mục /sys/bus/pci/devices cho thông tin GPU
                if os.path.exists('/sys/class/drm'):
                    gpu_dirs = os.listdir('/sys/class/drm')
                    for device in gpu_dirs:
                        vendor_path = f'/sys/class/drm/{device}/device/vendor'
                        if os.path.exists(vendor_path):
                            with open(vendor_path, 'r') as f:
                                vendor_id = f.read().strip()
                                # AMD vendor ID is 0x1002
                                if vendor_id == '0x1002':
                                    return True
                # Nếu không thể xác định, trả về False
                logger.warning("Could not detect GPU through sysfs - assuming no AMD GPU")
                return False
        
        # Kiểm tra GPU trên Windows
        elif sys.platform == 'win32':
            # Sử dụng wmic để kiểm tra card GPU AMD
            output = subprocess.check_output("wmic path win32_VideoController get name", shell=True)
            return b'AMD' in output or b'Radeon' in output
        
        # Kiểm tra GPU trên MacOS
        elif sys.platform == 'darwin':
            # MacOS thường không có GPU AMD như RX6600, nhưng vẫn kiểm tra
            try:
                output = subprocess.check_output("system_profiler SPDisplaysDataType | grep AMD", shell=True)
                return b'AMD' in output or b'Radeon' in output
            except subprocess.CalledProcessError:
                return False
        
        # Không hỗ trợ các hệ điều hành khác
        else:
            logger.warning(f"Unsupported operating system for GPU detection: {sys.platform}")
            return False
            
    except Exception as e:
        logger.error(f"Error checking GPU on {sys.platform}: {e}")
        # Trong môi trường phát triển, giả định không có GPU
        logger.info("Assuming no GPU in development environment")
        return False
        
def configure_lightgbm_directml() -> bool:
    """
    Configure LightGBM to use DirectML for GPU acceleration with AMD cards
    
    Returns:
        bool: True if configuration was successful, False otherwise
    """
    try:
        # Kiểm tra nếu có GPU AMD
        if check_amd_gpu_support():
            logger.info("AMD GPU detected, configuring LightGBM with DirectML")
            
            # Set biến môi trường cho DirectML
            os.environ["LIGHTGBM_DMLC"] = "1"
            
            # Trả về thành công
            return True
        else:
            logger.warning("No AMD GPU detected, falling back to CPU")
            return False
            
    except Exception as e:
        logger.error(f"Error configuring LightGBM DirectML: {e}")
        return False
        
def export_to_onnx(model: Any, input_shape: List[int], output_path: str) -> bool:
    """
    Export a LightGBM model to ONNX format for faster inference
    
    Args:
        model: Trained LightGBM model
        input_shape: Shape of input data
        output_path: Path to save the ONNX model
    
    Returns:
        bool: True if export was successful, False otherwise
    """
    try:
        import onnx
        from onnxmltools import convert_lightgbm
        from onnxmltools.convert.common.data_types import FloatTensorType

        # Chuyển đổi mô hình sang ONNX
        initial_type = [('input', FloatTensorType(input_shape))]
        onnx_model = convert_lightgbm(model, initial_types=initial_type)
        
        # Lưu mô hình
        onnx.save_model(onnx_model, output_path)
        logger.info(f"Model successfully exported to ONNX: {output_path}")
        return True
    except Exception as e:
        logger.error(f"Error exporting model to ONNX: {e}")
        return False