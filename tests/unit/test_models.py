"""
Unit tests for the database models used in the AITradeStrategist application.
"""
import os
import json
import pytest
from datetime import datetime
from sqlalchemy.exc import IntegrityError
from unittest.mock import patch, MagicMock

# Import the models and database from the application
try:
    from main import db, ModelBackup, TrainingConfig, TradingMetrics
    IMPORTS_AVAILABLE = True
except ImportError:
    IMPORTS_AVAILABLE = False


# Skip tests if imports are not available
pytestmark = pytest.mark.skipif(not IMPORTS_AVAILABLE, reason="Database models not available")


class TestModelBackup:
    """Tests for the ModelBackup model."""
    
    def test_create_model_backup(self, db_session):
        """Test creating a new model backup."""
        # Create a new model backup
        backup = ModelBackup(
            model_name="LightGBM-BTC-Test",
            created_date=datetime.now(),
            pair="BTC/USDT",
            timeframe="1h",
            backup_path="/tmp/models/backup_20250415_123456.model",
            metrics={"accuracy": 0.85, "precision": 0.82, "recall": 0.78},
            is_active=True
        )
        
        # Add the backup to the session and commit
        db_session.add(backup)
        db_session.commit()
        
        # Check that the backup was created
        assert backup.id is not None
        
        # Get the backup from the database and check its attributes
        retrieved_backup = db_session.query(ModelBackup).filter_by(id=backup.id).first()
        assert retrieved_backup is not None
        assert retrieved_backup.model_name == "LightGBM-BTC-Test"
        assert retrieved_backup.pair == "BTC/USDT"
        assert retrieved_backup.timeframe == "1h"
        assert retrieved_backup.backup_path == "/tmp/models/backup_20250415_123456.model"
        assert retrieved_backup.is_active is True
        assert "accuracy" in retrieved_backup.metrics
        assert retrieved_backup.metrics["accuracy"] == 0.85
    
    def test_update_model_backup(self, db_session):
        """Test updating an existing model backup."""
        # Create a new model backup
        backup = ModelBackup(
            model_name="LightGBM-ETH-Test",
            created_date=datetime.now(),
            pair="ETH/USDT",
            timeframe="4h",
            backup_path="/tmp/models/backup_20250415_234567.model",
            metrics={"accuracy": 0.79, "precision": 0.76, "recall": 0.73},
            is_active=False
        )
        
        # Add the backup to the session and commit
        db_session.add(backup)
        db_session.commit()
        
        # Update the backup
        backup.is_active = True
        backup.metrics = {"accuracy": 0.83, "precision": 0.80, "recall": 0.77}
        db_session.commit()
        
        # Get the backup from the database and check its attributes
        retrieved_backup = db_session.query(ModelBackup).filter_by(id=backup.id).first()
        assert retrieved_backup is not None
        assert retrieved_backup.is_active is True
        assert retrieved_backup.metrics["accuracy"] == 0.83
    
    def test_delete_model_backup(self, db_session):
        """Test deleting an existing model backup."""
        # Create a new model backup
        backup = ModelBackup(
            model_name="LightGBM-ADA-Test",
            created_date=datetime.now(),
            pair="ADA/USDT",
            timeframe="1d",
            backup_path="/tmp/models/backup_20250415_345678.model",
            metrics={"accuracy": 0.88, "precision": 0.85, "recall": 0.82},
            is_active=False
        )
        
        # Add the backup to the session and commit
        db_session.add(backup)
        db_session.commit()
        
        # Delete the backup
        db_session.delete(backup)
        db_session.commit()
        
        # Check that the backup was deleted
        retrieved_backup = db_session.query(ModelBackup).filter_by(id=backup.id).first()
        assert retrieved_backup is None
    
    def test_unique_active_backup_per_pair_timeframe(self, db_session):
        """Test that only one backup can be active for a given pair and timeframe."""
        # Create a new active model backup
        backup1 = ModelBackup(
            model_name="LightGBM-BTC-Test-1",
            created_date=datetime.now(),
            pair="BTC/USDT",
            timeframe="1h",
            backup_path="/tmp/models/backup_20250415_123456.model",
            metrics={"accuracy": 0.85, "precision": 0.82, "recall": 0.78},
            is_active=True
        )
        
        # Add the backup to the session and commit
        db_session.add(backup1)
        db_session.commit()
        
        # Create another active model backup for the same pair and timeframe
        backup2 = ModelBackup(
            model_name="LightGBM-BTC-Test-2",
            created_date=datetime.now(),
            pair="BTC/USDT",
            timeframe="1h",
            backup_path="/tmp/models/backup_20250415_234567.model",
            metrics={"accuracy": 0.87, "precision": 0.84, "recall": 0.81},
            is_active=True
        )
        
        # Add the backup to the session and commit
        db_session.add(backup2)
        db_session.commit()
        
        # Check that the first backup is no longer active
        retrieved_backup1 = db_session.query(ModelBackup).filter_by(id=backup1.id).first()
        assert retrieved_backup1 is not None
        assert retrieved_backup1.is_active is False
        
        # Check that the second backup is active
        retrieved_backup2 = db_session.query(ModelBackup).filter_by(id=backup2.id).first()
        assert retrieved_backup2 is not None
        assert retrieved_backup2.is_active is True


class TestTrainingConfig:
    """Tests for the TrainingConfig model."""
    
    def test_create_training_config(self, db_session):
        """Test creating a new training configuration."""
        # Create a new training configuration
        config = TrainingConfig(
            config_name="BTC-1h-Config",
            params={
                "model_type": "lightgbm",
                "learning_rate": 0.01,
                "max_depth": 5,
                "num_leaves": 31,
                "n_estimators": 100
            },
            created_date=datetime.now()
        )
        
        # Add the config to the session and commit
        db_session.add(config)
        db_session.commit()
        
        # Check that the config was created
        assert config.id is not None
        
        # Get the config from the database and check its attributes
        retrieved_config = db_session.query(TrainingConfig).filter_by(id=config.id).first()
        assert retrieved_config is not None
        assert retrieved_config.config_name == "BTC-1h-Config"
        assert "model_type" in retrieved_config.params
        assert retrieved_config.params["model_type"] == "lightgbm"
        assert retrieved_config.params["learning_rate"] == 0.01
    
    def test_update_training_config(self, db_session):
        """Test updating an existing training configuration."""
        # Create a new training configuration
        config = TrainingConfig(
            config_name="ETH-4h-Config",
            params={
                "model_type": "lightgbm",
                "learning_rate": 0.02,
                "max_depth": 7,
                "num_leaves": 63,
                "n_estimators": 200
            },
            created_date=datetime.now()
        )
        
        # Add the config to the session and commit
        db_session.add(config)
        db_session.commit()
        
        # Update the config
        config.params["learning_rate"] = 0.015
        config.params["max_depth"] = 6
        db_session.commit()
        
        # Get the config from the database and check its attributes
        retrieved_config = db_session.query(TrainingConfig).filter_by(id=config.id).first()
        assert retrieved_config is not None
        assert retrieved_config.params["learning_rate"] == 0.015
        assert retrieved_config.params["max_depth"] == 6


class TestTradingMetrics:
    """Tests for the TradingMetrics model."""
    
    def test_create_trading_metrics(self, db_session):
        """Test creating a new trading metrics record."""
        # Create a new trading metrics record
        metrics = TradingMetrics(
            pair="BTC/USDT",
            timeframe="1h",
            start_date=datetime(2025, 1, 1),
            end_date=datetime(2025, 4, 1),
            total_trades=150,
            win_trades=95,
            loss_trades=55,
            profit_percent=15.8,
            profit_abs=1580.25,
            metrics_data={
                "max_drawdown": 8.5,
                "max_drawdown_abs": 850.75,
                "best_trade": 4.2,
                "worst_trade": -3.1
            }
        )
        
        # Add the metrics to the session and commit
        db_session.add(metrics)
        db_session.commit()
        
        # Check that the metrics were created
        assert metrics.id is not None
        
        # Get the metrics from the database and check its attributes
        retrieved_metrics = db_session.query(TradingMetrics).filter_by(id=metrics.id).first()
        assert retrieved_metrics is not None
        assert retrieved_metrics.pair == "BTC/USDT"
        assert retrieved_metrics.timeframe == "1h"
        assert retrieved_metrics.total_trades == 150
        assert retrieved_metrics.win_trades == 95
        assert retrieved_metrics.loss_trades == 55
        assert retrieved_metrics.profit_percent == 15.8
        assert retrieved_metrics.profit_abs == 1580.25
        assert "max_drawdown" in retrieved_metrics.metrics_data
        assert retrieved_metrics.metrics_data["max_drawdown"] == 8.5
    
    def test_update_trading_metrics(self, db_session):
        """Test updating an existing trading metrics record."""
        # Create a new trading metrics record
        metrics = TradingMetrics(
            pair="ETH/USDT",
            timeframe="4h",
            start_date=datetime(2025, 1, 1),
            end_date=datetime(2025, 4, 1),
            total_trades=120,
            win_trades=72,
            loss_trades=48,
            profit_percent=12.5,
            profit_abs=1250.75,
            metrics_data={
                "max_drawdown": 7.2,
                "max_drawdown_abs": 720.50,
                "best_trade": 3.8,
                "worst_trade": -2.9
            }
        )
        
        # Add the metrics to the session and commit
        db_session.add(metrics)
        db_session.commit()
        
        # Update the metrics
        metrics.total_trades = 130
        metrics.win_trades = 80
        metrics.loss_trades = 50
        metrics.profit_percent = 13.2
        metrics.profit_abs = 1320.45
        metrics.metrics_data["max_drawdown"] = 7.5
        db_session.commit()
        
        # Get the metrics from the database and check its attributes
        retrieved_metrics = db_session.query(TradingMetrics).filter_by(id=metrics.id).first()
        assert retrieved_metrics is not None
        assert retrieved_metrics.total_trades == 130
        assert retrieved_metrics.win_trades == 80
        assert retrieved_metrics.loss_trades == 50
        assert retrieved_metrics.profit_percent == 13.2
        assert retrieved_metrics.profit_abs == 1320.45
        assert retrieved_metrics.metrics_data["max_drawdown"] == 7.5