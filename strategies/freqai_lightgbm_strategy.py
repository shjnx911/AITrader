#!/usr/bin/env python3
"""
FreqAI LightGBM strategy for cryptocurrency trading.
This strategy uses LightGBM with FreqAI integration for prediction-based trading.
"""
import logging
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple, Union, Any

from freqtrade.strategy import IStrategy, IntParameter, DecimalParameter, CategoricalParameter
from freqtrade.strategy.interface import IStrategy
from freqtrade.freqai.base_models.BaseRegressionModel import BaseRegressionModel
from freqtrade.freqai.base_models.FreqaiMultiOutputRegressor import FreqaiMultiOutputRegressor
from freqtrade.optimize.space import Categorical, Dimension, Integer, SKDecimal

import logging
logger = logging.getLogger(__name__)


class FreqAI_LGBM_Strategy(IStrategy):
    """
    LightGBM strategy with FreqAI integration.
    Uses machine learning predictions to generate trading signals.
    
    FreqAI settings:
    - Trains a LightGBM model on historical data
    - Uses predictions to decide trade entries and exits
    - Supports GPU acceleration through DirectML
    - Can export models to ONNX for faster inference
    """
    
    # Strategy parameters
    minimal_roi = {
        "0": 0.01  # Take profit is handled dynamically by target
    }
    
    # Fixed stoploss
    stoploss = -0.05  # Can be modified by prediction targets
    
    # Trading settings
    trailing_stop = True
    trailing_stop_positive = 0.005
    trailing_stop_positive_offset = 0.01
    trailing_only_offset_is_reached = True
    
    # Timeframe for the strategy
    timeframe = '1h'
    
    # Run only once at the start of the strategy
    process_only_new_candles = True
    
    # For live training
    startup_candle_count: int = 300
    
    # Enable order types: limit, market, etc.
    order_types = {
        'entry': 'market',
        'exit': 'market',
        'stoploss': 'market',
        'stoploss_on_exchange': False
    }
    
    # Define parameter ranges for optimization
    buy_params = {
        'entry_threshold': 0.65,
    }
    
    # Strategy parameters that can be optimized
    entry_threshold = DecimalParameter(0.55, 0.85, default=0.65, space='buy', optimize=True)
    exit_threshold = DecimalParameter(0.55, 0.85, default=0.65, space='sell', optimize=True)
    trailing_factor = DecimalParameter(1.0, 4.0, default=2.0, space='buy', optimize=True)
    
    # Prediction features and targets
    model_features = [
        'rsi', 'mfi', 'adx', 'cci', 'macd', 'macdsignal', 'macdhist',
        'bbdelta', 'closedelta', 'tail', 'volume_mean_24h', 'volume_std_24h',
        'volume_change_24h', 'close_mean_24h', 'close_std_24h', 'close_change_24h'
    ]
    
    model_features_ds = [
        'rsi_24h', 'mfi_24h', 'adx_24h', 'cci_24h', 'macd_24h', 'macdsignal_24h', 'macdhist_24h',
        'volume_mean_24h_24h', 'volume_std_24h_24h', 'volume_change_24h_24h',
        'close_mean_24h_24h', 'close_std_24h_24h', 'close_change_24h_24h'
    ]
    
    # FreqAI settings
    use_custom_stoploss = True
    
    def feature_engineering_expand_all(self, dataframe: pd.DataFrame, period: int, 
                                      metadata: Dict, **kwargs) -> pd.DataFrame:
        """
        Creates additional features from existing data.
        
        Args:
            dataframe: Strategy dataframe
            period: Backtest period
            metadata: Strategy metadata
            
        Returns:
            Dataframe with additional features
        """
        # Define target (predict future price vs current price)
        dataframe['&s-up_or_down'] = np.where(dataframe["close"].shift(-period) >
                                            dataframe["close"], 1, 0)
        
        # Add RSI
        dataframe['rsi'] = ta.RSI(dataframe, timeperiod=14)
        
        # Add MFI
        dataframe['mfi'] = ta.MFI(dataframe, timeperiod=14)
        
        # Add ADX
        dataframe['adx'] = ta.ADX(dataframe, timeperiod=14)
        
        # Add CCI
        dataframe['cci'] = ta.CCI(dataframe, timeperiod=14)
        
        # Add MACD
        macd = ta.MACD(dataframe)
        dataframe['macd'] = macd['macd']
        dataframe['macdsignal'] = macd['macdsignal']
        dataframe['macdhist'] = macd['macdhist']
        
        # Bollinger Bands
        bollinger = ta.BBANDS(dataframe, timeperiod=20, nbdevup=2, nbdevdn=2)
        dataframe['bb_upperband'] = bollinger['upperband']
        dataframe['bb_middleband'] = bollinger['middleband']
        dataframe['bb_lowerband'] = bollinger['lowerband']
        dataframe['bbdelta'] = (dataframe['bb_middleband'] - dataframe['bb_lowerband']).abs()
        dataframe['closedelta'] = (dataframe['close'] - dataframe['close'].shift()).abs()
        dataframe['tail'] = (dataframe['close'] - dataframe['bb_lowerband']).abs()
        
        # Simple price features
        dataframe['close_mean_24h'] = dataframe['close'].rolling(24).mean()
        dataframe['close_std_24h'] = dataframe['close'].rolling(24).std()
        dataframe['close_change_24h'] = dataframe['close'].pct_change(24)
        
        # Volume features
        dataframe['volume_mean_24h'] = dataframe['volume'].rolling(24).mean()
        dataframe['volume_std_24h'] = dataframe['volume'].rolling(24).std()
        dataframe['volume_change_24h'] = dataframe['volume'].pct_change(24)
        
        # Add DS features (shifted features)
        for feature in self.model_features:
            dataframe[f'{feature}_24h'] = dataframe[feature].shift(24)
        
        return dataframe
    
    def feature_engineering_expand_basic(self, dataframe: pd.DataFrame, period: int, 
                                      metadata: Dict, **kwargs) -> pd.DataFrame:
        """
        Creates only necessary features from existing data.
        This is used when not all features are needed (e.g., for live trading)
        
        Args:
            dataframe: Strategy dataframe
            period: Backtest period
            metadata: Strategy metadata
            
        Returns:
            Dataframe with basic features
        """
        # Only predict target
        dataframe['&s-up_or_down'] = np.where(dataframe["close"].shift(-period) >
                                          dataframe["close"], 1, 0)
        
        return dataframe
    
    def feature_engineering_standard(self, dataframe: pd.DataFrame, metadata: Dict, **kwargs) -> pd.DataFrame:
        """
        Standard feature engineering that occurs after all expand steps.
        
        Args:
            dataframe: Strategy dataframe
            metadata: Strategy metadata
            
        Returns:
            Dataframe with normalized features
        """
        # Fill missing values to avoid NaN issues
        dataframe = dataframe.fillna(method='ffill')
        
        return dataframe
    
    def set_freqai_targets(self, dataframe: pd.DataFrame, metadata: Dict, **kwargs) -> pd.DataFrame:
        """
        Set prediction targets
        
        Args:
            dataframe: Strategy dataframe
            metadata: Strategy metadata
            
        Returns:
            Dataframe with prediction targets
        """
        # For classification - predict if price will go up or down
        return dataframe
    
    def populate_indicators(self, dataframe: pd.DataFrame, metadata: Dict) -> pd.DataFrame:
        """
        Add indicators to the strategy
        
        Args:
            dataframe: Strategy dataframe
            metadata: Pair metadata
            
        Returns:
            Dataframe with indicators
        """
        # Run FreqAI first to get predictions
        dataframe = self.freqai.start(dataframe, metadata, self)
        
        # If predictions are not available, return dataframe as is
        if not self.freqai.live:
            return dataframe
        
        # Add additional indicators if needed
        return dataframe
    
    def populate_entry_trend(self, dataframe: pd.DataFrame, metadata: Dict) -> pd.DataFrame:
        """
        Entry signal logic
        
        Args:
            dataframe: Strategy dataframe with indicators
            metadata: Pair metadata
            
        Returns:
            Dataframe with entry signals
        """
        dataframe.loc[:, 'enter_long'] = 0
        dataframe.loc[:, 'enter_short'] = 0
        
        # Entry signal for long trades
        dataframe.loc[
            (
                (dataframe['&s-up_or_down_prediction'] > self.entry_threshold.value) &
                (dataframe['volume'] > 0)  # Make sure volume is not 0
            ),
            'enter_long'
        ] = 1
        
        # Entry signal for short trades (if futures)
        dataframe.loc[
            (
                (dataframe['&s-up_or_down_prediction'] < (1 - self.entry_threshold.value)) &
                (dataframe['volume'] > 0)  # Make sure volume is not 0
            ),
            'enter_short'
        ] = 1
        
        return dataframe
    
    def populate_exit_trend(self, dataframe: pd.DataFrame, metadata: Dict) -> pd.DataFrame:
        """
        Exit signal logic
        
        Args:
            dataframe: Strategy dataframe with indicators
            metadata: Pair metadata
            
        Returns:
            Dataframe with exit signals
        """
        dataframe.loc[:, 'exit_long'] = 0
        dataframe.loc[:, 'exit_short'] = 0
        
        # Exit signal for long trades
        dataframe.loc[
            (
                (dataframe['&s-up_or_down_prediction'] < (1 - self.exit_threshold.value)) &
                (dataframe['volume'] > 0)  # Make sure volume is not 0
            ),
            'exit_long'
        ] = 1
        
        # Exit signal for short trades
        dataframe.loc[
            (
                (dataframe['&s-up_or_down_prediction'] > self.exit_threshold.value) &
                (dataframe['volume'] > 0)  # Make sure volume is not 0
            ),
            'exit_short'
        ] = 1
        
        return dataframe
    
    def custom_stoploss(self, pair: str, trade: 'Trade', current_time: datetime,
                      current_rate: float, current_profit: float, **kwargs) -> float:
        """
        Custom stoploss logic, uses prediction-based adjustments.
        
        Args:
            pair: Pair that's currently in a trade
            trade: Trade object
            current_time: Current datetime
            current_rate: Current price
            current_profit: Current profit/loss ratio
            
        Returns:
            New stoploss value relative to the entry price
        """
        # Get dataframe for this pair
        dataframe, _ = self.dp.get_analyzed_dataframe(pair, self.timeframe)
        
        # Get the last prediction
        if len(dataframe) > 0 and '&s-up_or_down_prediction' in dataframe.columns:
            last_prediction = dataframe['&s-up_or_down_prediction'].iloc[-1]
            base_stoploss = self.stoploss
            
            # Adjust stoploss based on confidence
            if last_prediction > 0.8:  # High confidence for upward movement
                # Looser stoploss on high confidence
                return base_stoploss * 1.5  # Example: -0.05 * 1.5 = -0.075
            elif last_prediction < 0.2:  # High confidence for downward movement
                # Tighter stoploss on low confidence
                return base_stoploss * 0.5  # Example: -0.05 * 0.5 = -0.025
        
        # Default to strategy stoploss
        return self.stoploss
    
    def confirm_trade_entry(self, pair: str, order_type: str, amount: float, rate: float,
                           time_in_force: str, current_time: datetime, **kwargs) -> bool:
        """
        Additional confirmation for trade entry.
        
        Args:
            pair: Pair being traded
            order_type: Order type (market, limit)
            amount: Amount being traded
            rate: Rate of the trade
            time_in_force: Time in force for the order
            current_time: Current datetime
            
        Returns:
            True if trade should be executed, False otherwise
        """
        # Get dataframe for this pair
        dataframe, _ = self.dp.get_analyzed_dataframe(pair, self.timeframe)
        
        # Skip trading if no dataframe or insufficient data
        if len(dataframe) < 2:
            return False
        
        # Check prediction confidence
        if '&s-up_or_down_prediction' in dataframe.columns:
            last_prediction = dataframe['&s-up_or_down_prediction'].iloc[-1]
            
            # For long trades, require high confidence
            if kwargs.get('side') == 'long' and last_prediction < self.entry_threshold.value:
                return False
            
            # For short trades, require low prediction (high confidence for down)
            if kwargs.get('side') == 'short' and last_prediction > (1 - self.entry_threshold.value):
                return False
        
        return True
    
    def confirm_trade_exit(self, pair: str, trade: 'Trade', order_type: str, amount: float,
                         rate: float, time_in_force: str, exit_reason: str,
                         current_time: datetime, **kwargs) -> bool:
        """
        Additional confirmation for exiting a trade.
        
        Args:
            pair: Pair being traded
            trade: Trade object
            order_type: Order type (market, limit)
            amount: Amount being traded
            rate: Rate of the trade
            time_in_force: Time in force for the order
            exit_reason: Reason for exit
            current_time: Current datetime
            
        Returns:
            True if exit should be executed, False otherwise
        """
        # Always exit if stoploss triggered or custom exit reason
        if exit_reason in ('stoploss', 'custom_exit'):
            return True
        
        # Get dataframe for this pair
        dataframe, _ = self.dp.get_analyzed_dataframe(pair, self.timeframe)
        
        # Skip if no dataframe or insufficient data
        if len(dataframe) < 2:
            return True  # Default to exiting if we can't check
        
        # Check prediction confidence
        if '&s-up_or_down_prediction' in dataframe.columns:
            last_prediction = dataframe['&s-up_or_down_prediction'].iloc[-1]
            
            # For long trades, confirm exit if prediction is bearish
            if trade.is_open and trade.is_long and last_prediction > (1 - self.exit_threshold.value):
                return False  # Don't exit yet, prediction still bullish
            
            # For short trades, confirm exit if prediction is bullish
            if trade.is_open and not trade.is_long and last_prediction < self.exit_threshold.value:
                return False  # Don't exit yet, prediction still bearish
        
        return True


class LightGBMClassifier(BaseRegressionModel):
    """
    LightGBM classifier that can be used with FreqAI.
    Supports both CPU and GPU (DirectML) acceleration.
    """
    
    def __init__(self, **freqai_params):
        """
        Initialize the LightGBM classifier.
        
        Args:
            freqai_params: Parameters for FreqAI
        """
        super().__init__(**freqai_params)
        
        # Check if GPU acceleration is enabled
        self.use_gpu = self.freqai_info.get('use_gpu', True)
        
        # Log the model type
        logger.info(f"Using LightGBM classifier with GPU: {self.use_gpu}")
        
    def fit(self, data_dictionary: Dict, dk: Any) -> Any:
        """
        Fit the LightGBM model.
        
        Args:
            data_dictionary: Dictionary containing training data
            dk: FreqAI DataHandler
            
        Returns:
            Trained model
        """
        try:
            import lightgbm as lgb
            
            # Get training data
            X = data_dictionary["train_features"]
            y = data_dictionary["train_labels"]
            
            # Default parameters for LightGBM
            params = {
                "objective": "binary",
                "boosting_type": "goss",
                "n_estimators": 800,
                "learning_rate": 0.02,
                "max_depth": 6,
                "num_leaves": 32,
                "verbosity": -1,
            }
            
            # Update with parameters from config
            model_training_parameters = self.freqai_info.get('model_training_parameters', {})
            params.update(model_training_parameters)
            
            # Set device parameters if GPU is available
            if self.use_gpu:
                from utils.gpu_utils import configure_lightgbm_directml
                gpu_params = configure_lightgbm_directml()
                params.update(gpu_params)
            
            # For multi-class classification with multiple targets
            if len(data_dictionary["train_labels"].shape) > 1 and data_dictionary["train_labels"].shape[1] > 1:
                model = FreqaiMultiOutputRegressor(
                    lgb.LGBMClassifier(**params)
                )
            else:
                model = lgb.LGBMClassifier(**params)
            
            # Fit the model
            model.fit(X, y)
            
            # Export model to ONNX if requested
            if self.freqai_info.get('use_onnx', True):
                model_path = os.path.join(self.data_path, f"{dk.pair}_lightgbm_model.onnx")
                self.save_model_to_onnx(model, X.shape[1], model_path)
            
            # Return the trained model
            return model
            
        except ImportError:
            logger.error("LightGBM is not installed. Please install it to use this model.")
            raise
    
    def predict(self, unfiltered_df: pd.DataFrame, dk: Any, **kwargs) -> pd.DataFrame:
        """
        Make predictions using the trained LightGBM model.
        
        Args:
            unfiltered_df: Dataframe with features
            dk: FreqAI DataHandler
            
        Returns:
            Dataframe with predictions
        """
        # Get features for prediction
        filtered_df, _ = dk.filter_features(unfiltered_df, training_features=dk.training_features)
        
        # Generate predictions
        predictions = self.model.predict_proba(filtered_df)
        
        # Handle multi-class and binary predictions differently
        if hasattr(self.model, "classes_"):
            # For binary classification
            if len(self.model.classes_) == 2:
                return pd.DataFrame(predictions[:, 1], columns=[f"{dk.label}_prediction"], index=filtered_df.index)
            # For multi-class
            else:
                pred_df = pd.DataFrame(predictions, index=filtered_df.index)
                pred_df.columns = [f"{dk.label}_prediction_{i}" for i in range(pred_df.shape[1])]
                return pred_df
        else:
            # For multi-target models
            pred_df = pd.DataFrame(predictions, index=filtered_df.index)
            pred_df.columns = [f"{l}_prediction" for l in dk.label_list]
            return pred_df
    
    def save_model_to_onnx(self, model, input_dim: int, output_path: str) -> bool:
        """
        Save LightGBM model to ONNX format for faster inference.
        
        Args:
            model: Trained LightGBM model
            input_dim: Input dimension
            output_path: Path to save the ONNX model
            
        Returns:
            True if successful, False otherwise
        """
        try:
            from utils.gpu_utils import export_to_onnx
            return export_to_onnx(model, input_dim, output_path)
        except Exception as e:
            logger.error(f"Error exporting model to ONNX: {e}")
            return False


# Import the talib library for indicators
try:
    import talib.abstract as ta
except ImportError:
    import pandas_ta as ta
