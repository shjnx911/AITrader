"""
Unit tests for the GPU utilities used in the AITradeStrategist application.
"""
import os
import pytest
import sys
from unittest.mock import patch, MagicMock

# Add the project directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from utils import gpu_utils


@patch('utils.gpu_utils.check_amd_gpu_support')
def test_configure_lightgbm_directml_amd(mock_amd_available):
    """Test the function that configures LightGBM with DirectML when AMD GPU is available."""
    # Mock the AMD GPU check to return True
    mock_amd_available.return_value = True
    
    # Check if LightGBM was configured for DirectML
    result = gpu_utils.configure_lightgbm_directml()
    
    # The function should return True
    assert result is True
    
    # The AMD GPU check should have been called
    mock_amd_available.assert_called_once()


@patch('utils.gpu_utils.check_amd_gpu_support')
def test_configure_lightgbm_directml_no_gpu(mock_amd_support):
    """Test the function that configures LightGBM with DirectML when no AMD GPU is available."""
    # Mock the AMD GPU check to return False
    mock_amd_support.return_value = False
    
    # Check if LightGBM was configured for DirectML
    result = gpu_utils.configure_lightgbm_directml()
    
    # The function should return False
    assert result is False
    
    # The AMD GPU check should have been called
    mock_amd_support.assert_called_once()


@patch('utils.gpu_utils.subprocess.check_output')
def test_check_amd_gpu_support_linux(mock_check_output):
    """Test the function that checks for AMD GPU support on Linux."""
    # Mock subprocess to simulate the presence of an AMD GPU
    mock_check_output.return_value = b"AMD Radeon RX 6600"
    
    # Check if an AMD GPU is available
    with patch('utils.gpu_utils.sys.platform', 'linux'):
        result = gpu_utils.check_amd_gpu_support()
    
    # The function should return True
    assert result is True


@patch('utils.gpu_utils.subprocess.check_output')
def test_check_amd_gpu_support_windows(mock_check_output):
    """Test the function that checks for AMD GPU support on Windows."""
    # Mock subprocess to simulate the presence of an AMD GPU
    mock_check_output.return_value = b"AMD Radeon RX 6600"
    
    # Check if an AMD GPU is available
    with patch('utils.gpu_utils.sys.platform', 'win32'):
        result = gpu_utils.check_amd_gpu_support()
    
    # The function should return True
    assert result is True


@patch('utils.gpu_utils.subprocess.check_output')
def test_check_amd_gpu_support_no_gpu(mock_check_output):
    """Test the function that checks for AMD GPU support when no AMD GPU is present."""
    # Mock subprocess to simulate the absence of an AMD GPU
    mock_check_output.return_value = b"Intel UHD Graphics"
    
    # Check if an AMD GPU is available
    with patch('utils.gpu_utils.sys.platform', 'linux'):
        result = gpu_utils.check_amd_gpu_support()
    
    # The function should return False
    assert result is False


@patch('utils.gpu_utils.subprocess.check_output')
def test_check_amd_gpu_support_error(mock_check_output):
    """Test the function that checks for AMD GPU support when an error occurs."""
    # Mock subprocess to raise an exception
    mock_check_output.side_effect = Exception("Command failed")
    
    # Check if an AMD GPU is available
    with patch('utils.gpu_utils.sys.platform', 'linux'):
        result = gpu_utils.check_amd_gpu_support()
    
    # The function should return False due to the error
    assert result is False


@patch('utils.gpu_utils.onnx')
@patch('utils.gpu_utils.convert_lightgbm')
def test_export_to_onnx_success(mock_convert_lightgbm, mock_onnx):
    """Test the function that exports a LightGBM model to ONNX format."""
    # Mock the model conversion
    mock_model = MagicMock()
    mock_converted_model = MagicMock()
    mock_convert_lightgbm.return_value = mock_converted_model
    
    # Export the model to ONNX
    result = gpu_utils.export_to_onnx(mock_model, [1, 10], "/path/to/model.onnx")
    
    # The function should return True
    assert result is True
    
    # The ONNX save function should have been called
    mock_onnx.save_model.assert_called_once_with(mock_converted_model, "/path/to/model.onnx")


@patch('utils.gpu_utils.onnx')
def test_export_to_onnx_error(mock_onnx):
    """Test the function that exports a LightGBM model to ONNX format when an error occurs."""
    # Mock the onnx.save_model function to raise an exception
    mock_onnx.save_model.side_effect = Exception("Export error")
    
    # Export the model to ONNX
    result = gpu_utils.export_to_onnx(MagicMock(), [1, 10], "/path/to/model.onnx")
    
    # The function should return False due to the error
    assert result is False