#!/usr/bin/env python
"""
Module huấn luyện mô hình AI từ dữ liệu backtest Freqtrade.
Sử dụng LightGBM để tạo một mô hình dự đoán giao dịch có lợi nhuận.
"""
import os
import argparse
import logging
import pickle
import json
from datetime import datetime
from typing import Dict, Any, Optional, Tuple

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
import lightgbm as lgb

from import_backtest import prepare_training_data, generate_training_features
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from dotenv import load_dotenv

# Tải biến môi trường
load_dotenv()

# Thiết lập logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Tạo base model
Base = declarative_base()


def train_lightgbm_model(X: pd.DataFrame, y: pd.Series, params: Dict[str, Any] = None) -> Tuple[Any, Dict[str, float]]:
    """
    Huấn luyện mô hình LightGBM cho dự đoán kết quả giao dịch
    
    Args:
        X: Features (tham số chiến lược)
        y: Target (giao dịch có lợi nhuận hay không)
        params: Tham số LightGBM (tùy chọn)
        
    Returns:
        Tuple (model, metrics): Mô hình đã huấn luyện và chỉ số đánh giá
    """
    # Chia dữ liệu thành training và testing
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Chuẩn hóa dữ liệu
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Tham số mặc định cho LightGBM nếu không được cung cấp
    if params is None:
        params = {
            'objective': 'binary',
            'metric': 'binary_logloss',
            'boosting_type': 'gbdt',
            'num_leaves': 31,
            'learning_rate': 0.05,
            'feature_fraction': 0.9,
            'bagging_fraction': 0.8,
            'bagging_freq': 5,
            'verbose': -1
        }
    
    # Tạo dataset cho LightGBM
    train_data = lgb.Dataset(X_train_scaled, label=y_train)
    test_data = lgb.Dataset(X_test_scaled, label=y_test, reference=train_data)
    
    # Huấn luyện mô hình
    logger.info("Bắt đầu huấn luyện mô hình LightGBM")
    model = lgb.train(
        params,
        train_data,
        num_boost_round=500,
        valid_sets=[test_data],
        early_stopping_rounds=50,
        verbose_eval=100
    )
    
    # Dự đoán và đánh giá
    y_pred_proba = model.predict(X_test_scaled)
    y_pred = (y_pred_proba > 0.5).astype(int)
    
    # Tính các metric
    metrics = {
        'accuracy': accuracy_score(y_test, y_pred),
        'precision': precision_score(y_test, y_pred, zero_division=0),
        'recall': recall_score(y_test, y_pred, zero_division=0),
        'f1': f1_score(y_test, y_pred, zero_division=0),
        'auc': roc_auc_score(y_test, y_pred_proba),
        'test_size': len(y_test),
        'train_size': len(y_train),
        'positive_rate': y.mean()
    }
    
    logger.info(f"Đã huấn luyện mô hình với {len(y_train)} mẫu, AUC: {metrics['auc']:.4f}")
    for metric_name, metric_value in metrics.items():
        logger.info(f"  - {metric_name}: {metric_value:.4f}")
    
    # Lưu cả scaler để sử dụng khi dự đoán
    model.scaler = scaler
    
    return model, metrics


def optimize_hyperparameters(X: pd.DataFrame, y: pd.Series) -> Dict[str, Any]:
    """
    Tối ưu hóa hyperparameters cho mô hình LightGBM
    
    Args:
        X: Features
        y: Target
        
    Returns:
        Parameters tốt nhất tìm được
    """
    logger.info("Bắt đầu tối ưu hóa hyperparameters")
    
    # Chia dữ liệu
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Chuẩn hóa dữ liệu
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    
    # Tham số cần tối ưu
    param_grid = {
        'num_leaves': [15, 31, 63],
        'learning_rate': [0.01, 0.05, 0.1],
        'n_estimators': [100, 200, 300],
        'colsample_bytree': [0.6, 0.8, 1.0],
        'subsample': [0.6, 0.8, 1.0],
        'reg_alpha': [0, 0.1, 0.5],
        'reg_lambda': [0, 0.1, 0.5]
    }
    
    # Tạo mô hình LightGBM cho GridSearchCV
    lgbm = lgb.LGBMClassifier(objective='binary', metric='binary_logloss', verbose=-1)
    
    # Tìm kiếm lưới
    grid_search = GridSearchCV(
        estimator=lgbm,
        param_grid=param_grid,
        cv=3,
        scoring='roc_auc',
        n_jobs=-1,
        verbose=1
    )
    
    grid_search.fit(X_train_scaled, y_train)
    
    logger.info(f"Tham số tốt nhất: {grid_search.best_params_}")
    logger.info(f"AUC tốt nhất: {grid_search.best_score_:.4f}")
    
    # Chuyển đổi sang định dạng tham số cho lightgbm.train
    best_params = {
        'objective': 'binary',
        'metric': 'binary_logloss',
        'boosting_type': 'gbdt',
        'verbose': -1,
        'num_leaves': grid_search.best_params_.get('num_leaves', 31),
        'learning_rate': grid_search.best_params_.get('learning_rate', 0.05),
        'feature_fraction': grid_search.best_params_.get('colsample_bytree', 0.8),
        'bagging_fraction': grid_search.best_params_.get('subsample', 0.8),
        'lambda_l1': grid_search.best_params_.get('reg_alpha', 0),
        'lambda_l2': grid_search.best_params_.get('reg_lambda', 0),
    }
    
    return best_params


def save_model(model, strategy_name: str, pair: str, metrics: Dict[str, float]) -> str:
    """
    Lưu mô hình và thông tin liên quan
    
    Args:
        model: Mô hình đã huấn luyện
        strategy_name: Tên chiến lược
        pair: Cặp giao dịch
        metrics: Chỉ số đánh giá mô hình
        
    Returns:
        Đường dẫn đến file mô hình đã lưu
    """
    # Tạo thư mục models nếu chưa tồn tại
    models_dir = os.path.join(os.getcwd(), 'models')
    os.makedirs(models_dir, exist_ok=True)
    
    # Tạo tên file dựa trên thông tin
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    model_filename = f"{strategy_name}_{pair.replace('/', '_')}_{timestamp}.pkl"
    model_path = os.path.join(models_dir, model_filename)
    
    # Lưu mô hình
    with open(model_path, 'wb') as f:
        pickle.dump(model, f)
    
    # Lưu thông tin metadata
    meta_filename = f"{os.path.splitext(model_filename)[0]}_meta.json"
    meta_path = os.path.join(models_dir, meta_filename)
    
    metadata = {
        'strategy_name': strategy_name,
        'pair': pair,
        'created_date': datetime.now().isoformat(),
        'metrics': metrics,
        'feature_names': model.feature_name(),
        'feature_importance': model.feature_importance().tolist(),
        'model_file': model_filename
    }
    
    with open(meta_path, 'w') as f:
        json.dump(metadata, f, indent=2)
    
    logger.info(f"Đã lưu mô hình vào {model_path}")
    logger.info(f"Đã lưu metadata vào {meta_path}")
    
    return model_path


def register_model_in_database(
    model_path: str, 
    strategy_name: str, 
    pair: str, 
    timeframe: str, 
    metrics: Dict[str, float]
) -> bool:
    """
    Đăng ký mô hình trong database
    
    Args:
        model_path: Đường dẫn đến file mô hình
        strategy_name: Tên chiến lược
        pair: Cặp giao dịch
        timeframe: Khung thời gian
        metrics: Các chỉ số đánh giá mô hình
        
    Returns:
        True nếu đăng ký thành công, False nếu không
    """
    from main import ModelBackup, db
    
    try:
        # Tạo entry mới trong database
        new_model = ModelBackup(
            model_name=f"{strategy_name}_{pair}",
            created_date=datetime.now(),
            pair=pair,
            timeframe=timeframe,
            backup_path=model_path,
            metrics=metrics,
            is_active=False  # Mặc định không active
        )
        
        # Thêm vào database
        db.session.add(new_model)
        db.session.commit()
        
        logger.info(f"Đã đăng ký mô hình trong database với ID {new_model.id}")
        return True
        
    except Exception as e:
        logger.error(f"Lỗi khi đăng ký mô hình trong database: {str(e)}")
        return False


def parse_args():
    """Phân tích tham số dòng lệnh"""
    parser = argparse.ArgumentParser(description="Huấn luyện mô hình AI từ dữ liệu backtest")
    
    parser.add_argument(
        "--strategy",
        type=str,
        required=True,
        help="Tên chiến lược"
    )
    
    parser.add_argument(
        "--pair",
        type=str,
        required=True,
        help="Cặp giao dịch"
    )
    
    parser.add_argument(
        "--timeframe",
        type=str,
        default="1h",
        help="Khung thời gian"
    )
    
    parser.add_argument(
        "--optimize",
        action="store_true",
        help="Tối ưu hóa hyperparameters"
    )
    
    parser.add_argument(
        "--min-trades",
        type=int,
        default=100,
        help="Số lượng giao dịch tối thiểu cần để huấn luyện"
    )
    
    parser.add_argument(
        "--register",
        action="store_true",
        help="Đăng ký mô hình trong database"
    )
    
    return parser.parse_args()


def main():
    """Hàm chính"""
    args = parse_args()
    
    # Chuẩn bị dữ liệu huấn luyện từ kết quả backtest
    df = prepare_training_data(args.strategy, args.pair, args.min_trades)
    
    if df is None:
        logger.error("Không có đủ dữ liệu để huấn luyện!")
        return
    
    # Tạo features và target
    result = generate_training_features(df)
    if result is None:
        logger.error("Không thể tạo features từ dữ liệu!")
        return
    
    X, y = result
    logger.info(f"Đã chuẩn bị: {X.shape[0]} mẫu với {X.shape[1]} features")
    
    # Tối ưu hóa hyperparameters nếu được yêu cầu
    params = None
    if args.optimize:
        params = optimize_hyperparameters(X, y)
    
    # Huấn luyện mô hình
    model, metrics = train_lightgbm_model(X, y, params)
    
    # Lưu mô hình
    model_path = save_model(model, args.strategy, args.pair, metrics)
    
    # Đăng ký mô hình trong database nếu được yêu cầu
    if args.register:
        register_model_in_database(model_path, args.strategy, args.pair, args.timeframe, metrics)


if __name__ == "__main__":
    main()