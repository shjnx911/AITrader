#!/usr/bin/env python3
"""
Main entry point for the Freqtrade LightGBM AI strategy.
This script sets up the environment and starts the Freqtrade bot with FreqAI.
"""
import logging
import sys
from pathlib import Path

# Add parent directory to sys.path to allow imports
sys.path.append(str(Path(__file__).parent))

from freqtrade.main import main
from utils.gpu_utils import check_amd_gpu_support


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    )
    logger = logging.getLogger('freqai_lightgbm')
    
    # Check AMD GPU support
    gpu_available = check_amd_gpu_support()
    if gpu_available:
        logger.info("AMD GPU support detected. DirectML acceleration will be used.")
    else:
        logger.warning("AMD GPU support not detected. Running in CPU mode.")
    
    # Run the Freqtrade bot
    main()
