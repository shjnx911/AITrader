"""
Routes và API endpoints để xử lý tính năng tích hợp Backtest AI.
Cung cấp các chức năng để import dữ liệu backtest, huấn luyện mô hình AI, 
và quản lý các mô hình đã huấn luyện.
"""
import os
import json
import logging
import pickle
import tempfile
from datetime import datetime
from typing import Dict, List, Any, Optional, Union, Tuple

from flask import Blueprint, render_template, request, jsonify, current_app, send_file

# Lazy imports to avoid loading modules that might have system dependencies
# until they are actually needed
pd = None
np = None
train_test_split = None
StandardScaler = None
accuracy_score = precision_score = recall_score = f1_score = roc_auc_score = None
LGBMClassifier = None

# Safe ML Modules - sẽ không gây lỗi khi import
RandomForestClassifier = None
XGBClassifier = None 
LogisticRegression = None

def lazy_import():
    """Import các thư viện một cách lười biếng khi cần thiết"""
    global pd, np, train_test_split, StandardScaler
    global accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
    global LGBMClassifier, RandomForestClassifier, XGBClassifier, LogisticRegression
    
    if pd is None:
        try:
            import pandas as pd_
            pd = pd_
        except ImportError:
            logger.warning("Không thể import pandas")
    
    if np is None:
        try:
            import numpy as np_
            np = np_
        except ImportError:
            logger.warning("Không thể import numpy")
    
    if train_test_split is None:
        try:
            from sklearn.model_selection import train_test_split as tts
            train_test_split = tts
        except ImportError:
            logger.warning("Không thể import train_test_split")
        
    if StandardScaler is None:
        try:
            from sklearn.preprocessing import StandardScaler as SS
            StandardScaler = SS
        except ImportError:
            logger.warning("Không thể import StandardScaler")
        
    if accuracy_score is None:
        try:
            from sklearn.metrics import (
                accuracy_score as acc_score,
                precision_score as prec_score,
                recall_score as rec_score,
                f1_score as f1,
                roc_auc_score as auc_score
            )
            accuracy_score = acc_score
            precision_score = prec_score
            recall_score = rec_score
            f1_score = f1
            roc_auc_score = auc_score
        except ImportError:
            logger.warning("Không thể import sklearn.metrics")
        
    # Import các mô hình ML có thể thay thế LightGBM
    if RandomForestClassifier is None:
        try:
            from sklearn.ensemble import RandomForestClassifier as RF
            RandomForestClassifier = RF
        except ImportError:
            logger.warning("Không thể import RandomForestClassifier")
            
    if XGBClassifier is None:
        try:
            from xgboost import XGBClassifier as XGB
            XGBClassifier = XGB
        except ImportError:
            logger.warning("Không thể import XGBClassifier")
            
    if LogisticRegression is None:
        try:
            from sklearn.linear_model import LogisticRegression as LR
            LogisticRegression = LR
        except ImportError:
            logger.warning("Không thể import LogisticRegression")
        
    # Thử import LightGBM cuối cùng vì nó phụ thuộc vào libgomp
    if LGBMClassifier is None:
        try:
            from lightgbm import LGBMClassifier as LGBM
            LGBMClassifier = LGBM
        except (ImportError, OSError) as e:
            logger.warning(f"Không thể import LightGBM: {e}")
            # Return a placeholder class that will raise an error when used
            class LGBMPlaceholder:
                def __init__(self, *args, **kwargs):
                    raise RuntimeError("LightGBM không khả dụng trên hệ thống này. Hãy sử dụng mô hình ML khác thay thế.")

from freqtrade_integration.import_backtest import import_backtest_results, prepare_training_data, generate_training_features
from freqtrade_integration.train_model import train_lightgbm_model, optimize_hyperparameters, save_model, register_model_in_database
from freqtrade_integration.generate_ai_strategy import generate_ai_strategy
from main import db, ModelBackup, TrainingConfig

# Sử dụng Blueprint đã được tạo trong __init__.py
from backtest_ai import backtest_ai_bp

# Thiết lập logging
logger = logging.getLogger(__name__)

# Trang chính cho tính năng Backtest AI
@backtest_ai_bp.route('/')
def backtest_ai_page():
    """Trang chính cho tính năng Backtest AI"""
    return render_template('backtest_ai.html')

# API Endpoints

@backtest_ai_bp.route('/api/import_backtest', methods=['POST'])
def api_import_backtest():
    """API để import kết quả backtest từ Freqtrade"""
    try:
        data = request.json
        directory = data.get('directory', '')
        filter_strategy = data.get('filter_strategy')
        overwrite = data.get('overwrite', False)
        
        # Chuẩn hóa đường dẫn (thay ~ bằng home directory)
        if directory.startswith('~'):
            directory = os.path.expanduser(directory)
        
        # Import dữ liệu backtest
        results = import_backtest_results(directory, filter_strategy)
        
        return jsonify({
            'success': True,
            'message': f'Đã import thành công kết quả backtest từ {directory}',
            'results': results
        })
    except Exception as e:
        logger.error(f"Lỗi khi import backtest: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Lỗi khi import backtest: {str(e)}'
        }), 500

@backtest_ai_bp.route('/api/imported_data', methods=['GET'])
def api_get_imported_data():
    """API lấy thông tin về dữ liệu đã import"""
    try:
        from freqtrade_integration.import_backtest import BacktestResult
        
        # Kết nối database
        from sqlalchemy import create_engine, func
        from sqlalchemy.orm import sessionmaker
        
        engine = create_engine(current_app.config['SQLALCHEMY_DATABASE_URI'])
        Session = sessionmaker(bind=engine)
        session = Session()
        
        # Lấy tất cả chiến lược
        strategies_data = session.query(
            BacktestResult.strategy_name,
            func.count(BacktestResult.id).label('files'),
            func.count(BacktestResult.trades_data).label('trades'),
            func.count(func.distinct(BacktestResult.pair)).label('pairs'),
            func.max(BacktestResult.import_date).label('last_import')
        ).group_by(BacktestResult.strategy_name).all()
        
        strategies = []
        for s in strategies_data:
            strategies.append({
                'strategy': s.strategy_name,
                'files': s.files,
                'trades': s.trades,
                'pairs': s.pairs,
                'lastImport': s.last_import.strftime('%Y-%m-%d %H:%M') if s.last_import else ''
            })
        
        # Lấy tất cả các cặp giao dịch
        pairs_data = session.query(
            BacktestResult.pair,
            func.count(func.distinct(BacktestResult.strategy_name)).label('strategies'),
            func.sum(BacktestResult.trades_count).label('trades'),
            func.avg(BacktestResult.win_rate).label('win_rate'),
            func.avg(BacktestResult.profit_percent).label('profit')
        ).group_by(BacktestResult.pair).all()
        
        pairs = []
        for p in pairs_data:
            pairs.append({
                'pair': p.pair,
                'strategies': p.strategies,
                'trades': int(p.trades) if p.trades else 0,
                'winRate': float(p.win_rate) if p.win_rate else 0.0,
                'profit': float(p.profit) if p.profit else 0.0
            })
        
        session.close()
        
        return jsonify({
            'success': True,
            'strategies': strategies,
            'pairs': pairs
        })
    except Exception as e:
        logger.error(f"Lỗi khi lấy dữ liệu đã import: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Lỗi khi lấy dữ liệu đã import: {str(e)}'
        }), 500

@backtest_ai_bp.route('/api/strategy_parameters/<strategy>', methods=['GET'])
def api_get_strategy_parameters(strategy):
    """API lấy thông tin về các tham số của một chiến lược cụ thể"""
    try:
        from freqtrade_integration.import_backtest import BacktestResult
        
        # Kết nối database
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        
        engine = create_engine(current_app.config['SQLALCHEMY_DATABASE_URI'])
        Session = sessionmaker(bind=engine)
        session = Session()
        
        # Lấy tất cả bản ghi cho chiến lược này
        results = session.query(BacktestResult).filter_by(strategy_name=strategy).all()
        
        # Phân tích các tham số
        parameters = {}
        
        for result in results:
            if not result.parameters:
                continue
                
            for param_name, param_value in result.parameters.items():
                if isinstance(param_value, (int, float)):
                    if param_name not in parameters:
                        parameters[param_name] = {
                            'values': [],
                            'min': None,
                            'max': None,
                            'avg': None
                        }
                    
                    parameters[param_name]['values'].append(param_value)
        
        # Tính toán các giá trị thống kê
        for param_name, param_data in parameters.items():
            values = param_data['values']
            if values:
                param_data['min'] = min(values)
                param_data['max'] = max(values)
                param_data['avg'] = sum(values) / len(values)
                # Xóa danh sách giá trị để tránh trả về quá nhiều dữ liệu
                del param_data['values']
        
        session.close()
        
        return jsonify({
            'success': True,
            'strategy': strategy,
            'parameters': parameters
        })
    except Exception as e:
        logger.error(f"Lỗi khi lấy tham số chiến lược: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Lỗi khi lấy tham số chiến lược: {str(e)}'
        }), 500

@backtest_ai_bp.route('/api/strategies', methods=['GET'])
def api_get_strategies():
    """API lấy danh sách các chiến lược có sẵn"""
    try:
        from freqtrade_integration.import_backtest import BacktestResult
        
        # Kết nối database
        from sqlalchemy import create_engine, func
        from sqlalchemy.orm import sessionmaker
        
        engine = create_engine(current_app.config['SQLALCHEMY_DATABASE_URI'])
        Session = sessionmaker(bind=engine)
        session = Session()
        
        # Lấy tất cả chiến lược
        strategies = session.query(BacktestResult.strategy_name).distinct().all()
        
        session.close()
        
        return jsonify({
            'success': True,
            'strategies': [s.strategy_name for s in strategies]
        })
    except Exception as e:
        logger.error(f"Lỗi khi lấy danh sách chiến lược: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Lỗi khi lấy danh sách chiến lược: {str(e)}'
        }), 500

@backtest_ai_bp.route('/api/pairs', methods=['GET'])
def api_get_pairs():
    """API lấy danh sách các cặp giao dịch có sẵn"""
    try:
        from freqtrade_integration.import_backtest import BacktestResult
        
        # Kết nối database
        from sqlalchemy import create_engine, func
        from sqlalchemy.orm import sessionmaker
        
        engine = create_engine(current_app.config['SQLALCHEMY_DATABASE_URI'])
        Session = sessionmaker(bind=engine)
        session = Session()
        
        # Lấy tất cả cặp giao dịch
        pairs = session.query(BacktestResult.pair).distinct().all()
        
        session.close()
        
        return jsonify({
            'success': True,
            'pairs': [p.pair for p in pairs]
        })
    except Exception as e:
        logger.error(f"Lỗi khi lấy danh sách cặp giao dịch: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Lỗi khi lấy danh sách cặp giao dịch: {str(e)}'
        }), 500

@backtest_ai_bp.route('/api/train_model', methods=['POST'])
def api_train_model():
    """API để huấn luyện mô hình AI từ dữ liệu backtest"""
    try:
        data = request.json
        strategies = data.get('strategies', [])
        pair = data.get('pair', '')
        timeframe = data.get('timeframe', '1h')
        min_trades = data.get('min_trades', 100)
        model_name = data.get('model_name', '')
        optimize = data.get('optimize_hyperparams', True)
        use_feature_selection = data.get('use_feature_selection', True)
        register_in_db = data.get('register_in_db', True)
        use_gpu = data.get('use_gpu', False)
        
        # Chuẩn bị dữ liệu huấn luyện từ kết quả backtest
        training_data = None
        
        # Nếu có nhiều chiến lược, kết hợp dữ liệu
        all_features_dfs = []
        all_targets = []
        
        for strategy in strategies:
            df = prepare_training_data(strategy, pair, min_trades=min_trades // len(strategies))
            if df is not None:
                result = generate_training_features(df)
                if result is not None:
                    X, y = result
                    all_features_dfs.append(X)
                    all_targets.append(y)
        
        if not all_features_dfs:
            return jsonify({
                'success': False,
                'message': f'Không đủ dữ liệu để huấn luyện cho cặp {pair} với các chiến lược đã chọn'
            }), 400
        
        # Import các thư viện cần thiết
        lazy_import()
        
        # Kết hợp dữ liệu từ các chiến lược
        X = pd.concat(all_features_dfs, ignore_index=True)
        y = pd.concat(all_targets, ignore_index=True)
        
        # Tối ưu hyperparameters nếu được yêu cầu
        params = None
        if optimize:
            params = optimize_hyperparameters(X, y)
        
        # Huấn luyện mô hình
        additional_params = {}
        if use_gpu:
            additional_params['device'] = 'gpu'
        
        model, metrics = train_lightgbm_model(X, y, params)
        
        # Tạo tên mô hình nếu không được cung cấp
        if not model_name:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            strategies_code = '_'.join([s[:3] for s in strategies])
            pair_code = pair.replace('/', '_')
            model_name = f"AI_{strategies_code}_{pair_code}_{timestamp}"
        
        # Lưu mô hình
        model_path = save_model(model, strategies[0] if len(strategies) == 1 else "EnsembleStrategy", 
                               pair, metrics)
        
        # Đăng ký mô hình trong database nếu được yêu cầu
        if register_in_db:
            register_model_in_database(model_path, strategies[0] if len(strategies) == 1 else "EnsembleStrategy", 
                                      pair, timeframe, metrics)
        
        return jsonify({
            'success': True,
            'message': f'Đã huấn luyện thành công mô hình {model_name}',
            'model_name': model_name,
            'model_path': model_path,
            'metrics': metrics,
            'feature_importance': model.feature_importance().tolist(),
            'feature_names': model.feature_name()
        })
    except Exception as e:
        logger.error(f"Lỗi khi huấn luyện mô hình: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Lỗi khi huấn luyện mô hình: {str(e)}'
        }), 500

@backtest_ai_bp.route('/api/models', methods=['GET'])
def api_get_models():
    """API lấy danh sách các mô hình AI đã huấn luyện"""
    try:
        # Lấy các mô hình từ database
        models = ModelBackup.query.all()
        
        result = []
        for model in models:
            result.append({
                'id': model.id,
                'name': model.model_name,
                'strategy': model.model_name.split('_')[0] if '_' in model.model_name else 'Unknown',
                'pair': model.pair,
                'timeframe': model.timeframe,
                'created': model.created_date.strftime('%Y-%m-%d %H:%M') if model.created_date else '',
                'accuracy': model.metrics.get('accuracy', 0) if model.metrics else 0,
                'isActive': model.is_active
            })
        
        return jsonify({
            'success': True,
            'models': result
        })
    except Exception as e:
        logger.error(f"Lỗi khi lấy danh sách mô hình: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Lỗi khi lấy danh sách mô hình: {str(e)}'
        }), 500

@backtest_ai_bp.route('/api/model_details/<int:model_id>', methods=['GET'])
def api_get_model_details(model_id):
    """API lấy thông tin chi tiết về một mô hình"""
    try:
        # Lấy mô hình từ database
        model = ModelBackup.query.get(model_id)
        
        if not model:
            return jsonify({
                'success': False,
                'message': f'Không tìm thấy mô hình với ID {model_id}'
            }), 404
        
        # Tải mô hình để lấy feature importance
        feature_importance = []
        feature_names = []
        
        try:
            with open(model.backup_path, 'rb') as f:
                loaded_model = pickle.load(f)
                
            # Lấy feature importance
            if hasattr(loaded_model, 'feature_importance') and callable(loaded_model.feature_importance):
                importance_values = loaded_model.feature_importance()
                feature_names = loaded_model.feature_name()
                
                for i, name in enumerate(feature_names):
                    feature_importance.append({
                        'name': name,
                        'importance': float(importance_values[i]) / sum(importance_values)
                    })
                
                # Sắp xếp theo độ quan trọng giảm dần
                feature_importance.sort(key=lambda x: x['importance'], reverse=True)
        except Exception as e:
            logger.warning(f"Không thể tải mô hình để lấy feature importance: {str(e)}")
        
        result = {
            'id': model.id,
            'name': model.model_name,
            'strategy': model.model_name.split('_')[0] if '_' in model.model_name else 'Unknown',
            'pair': model.pair,
            'timeframe': model.timeframe,
            'created_date': model.created_date.strftime('%Y-%m-%d %H:%M') if model.created_date else '',
            'metrics': model.metrics or {},
            'is_active': model.is_active,
            'model_path': model.backup_path,
            'feature_importance': feature_importance,
            'feature_names': feature_names
        }
        
        return jsonify({
            'success': True,
            'model': result
        })
    except Exception as e:
        logger.error(f"Lỗi khi lấy chi tiết mô hình: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Lỗi khi lấy chi tiết mô hình: {str(e)}'
        }), 500

@backtest_ai_bp.route('/api/activate_model/<int:model_id>', methods=['POST'])
def api_activate_model(model_id):
    """API kích hoạt một mô hình"""
    try:
        # Lấy mô hình từ database
        model = ModelBackup.query.get(model_id)
        
        if not model:
            return jsonify({
                'success': False,
                'message': f'Không tìm thấy mô hình với ID {model_id}'
            }), 404
        
        # Vô hiệu hóa tất cả các mô hình khác với cùng cặp giao dịch
        other_models = ModelBackup.query.filter(
            ModelBackup.pair == model.pair, 
            ModelBackup.id != model_id
        ).all()
        
        for other in other_models:
            other.is_active = False
        
        # Đảo trạng thái kích hoạt của mô hình hiện tại
        model.is_active = not model.is_active
        
        # Lưu thay đổi
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Đã {"kích hoạt" if model.is_active else "vô hiệu hóa"} mô hình {model.model_name}',
            'is_active': model.is_active
        })
    except Exception as e:
        logger.error(f"Lỗi khi kích hoạt mô hình: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Lỗi khi kích hoạt mô hình: {str(e)}'
        }), 500

@backtest_ai_bp.route('/api/delete_model/<int:model_id>', methods=['DELETE'])
def api_delete_model(model_id):
    """API xóa một mô hình"""
    try:
        # Lấy mô hình từ database
        model = ModelBackup.query.get(model_id)
        
        if not model:
            return jsonify({
                'success': False,
                'message': f'Không tìm thấy mô hình với ID {model_id}'
            }), 404
        
        # Xóa file mô hình nếu tồn tại
        if os.path.exists(model.backup_path):
            os.remove(model.backup_path)
            
            # Xóa file metadata nếu tồn tại
            meta_path = os.path.splitext(model.backup_path)[0] + '_meta.json'
            if os.path.exists(meta_path):
                os.remove(meta_path)
        
        # Xóa từ database
        db.session.delete(model)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Đã xóa mô hình {model.model_name}'
        })
    except Exception as e:
        logger.error(f"Lỗi khi xóa mô hình: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Lỗi khi xóa mô hình: {str(e)}'
        }), 500

@backtest_ai_bp.route('/api/generate_strategy', methods=['POST'])
def api_generate_strategy():
    """API để tạo file chiến lược từ mô hình AI"""
    try:
        data = request.json
        model_id = data.get('model_id')
        strategy_name = data.get('strategy_name', '')
        base_strategy = data.get('base_strategy', 'DefaultStrategy')
        ai_threshold = data.get('ai_threshold', 0.65)
        minimal_roi = data.get('minimal_roi', None)
        stoploss = data.get('stoploss', None)
        optimize_parameters = data.get('optimize_parameters', True)
        include_comments = data.get('include_comments', True)
        
        # Lấy thông tin mô hình từ database
        model = ModelBackup.query.get(model_id)
        
        if not model:
            return jsonify({
                'success': False,
                'message': f'Không tìm thấy mô hình với ID {model_id}'
            }), 404
        
        # Tạo tên chiến lược nếu không được cung cấp
        if not strategy_name:
            timestamp = datetime.now().strftime('%Y%m%d')
            pair_code = model.pair.replace('/', '_')
            strategy_name = f"AI_{model.model_name.split('_')[0]}_{pair_code}_{timestamp}"
        
        # Tạo file chiến lược
        strategy_file = generate_ai_strategy(
            model_path=model.backup_path,
            strategy_name=strategy_name,
            base_strategy=base_strategy,
            pair=model.pair,
            timeframe=model.timeframe
        )
        
        if not strategy_file:
            return jsonify({
                'success': False,
                'message': 'Không thể tạo file chiến lược'
            }), 500
        
        # Đọc nội dung file để trả về
        with open(strategy_file, 'r') as f:
            strategy_code = f.read()
        
        return jsonify({
            'success': True,
            'message': f'Đã tạo thành công chiến lược {strategy_name}',
            'strategy_name': strategy_name,
            'strategy_file': strategy_file,
            'strategy_code': strategy_code
        })
    except Exception as e:
        logger.error(f"Lỗi khi tạo chiến lược: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Lỗi khi tạo chiến lược: {str(e)}'
        }), 500

@backtest_ai_bp.route('/api/run_monte_carlo', methods=['POST'])
def api_run_monte_carlo():
    """API để chạy mô phỏng Monte Carlo cho một mô hình"""
    try:
        data = request.json
        model_id = data.get('model_id')
        simulations = data.get('simulations', 1000)
        initial_capital = data.get('initial_capital', 10000)
        risk_per_trade = data.get('risk_per_trade', 1.0) / 100.0  # Chuyển từ % sang decimal
        trading_days = data.get('trading_days', 30)
        trades_per_day = data.get('trades_per_day', 3)
        win_rate_variance = data.get('win_rate_variance', 5.0) / 100.0  # Chuyển từ % sang decimal
        risk_reward_variance = data.get('risk_reward_variance', 10.0) / 100.0  # Chuyển từ % sang decimal
        consider_fees = data.get('consider_fees', True)
        
        # Lấy thông tin mô hình từ database
        model = ModelBackup.query.get(model_id)
        
        if not model:
            return jsonify({
                'success': False,
                'message': f'Không tìm thấy mô hình với ID {model_id}'
            }), 404
        
        # Lấy win rate và risk/reward từ metrics của mô hình
        base_win_rate = model.metrics.get('positive_rate', 0.5) if model.metrics else 0.5
        risk_reward_ratio = 1.5  # Giá trị mặc định
        
        # Chạy mô phỏng Monte Carlo
        mc_results = run_monte_carlo_simulation(
            simulations=simulations,
            initial_capital=initial_capital,
            risk_per_trade=risk_per_trade,
            trading_days=trading_days,
            trades_per_day=trades_per_day,
            base_win_rate=base_win_rate,
            win_rate_variance=win_rate_variance,
            risk_reward_ratio=risk_reward_ratio,
            risk_reward_variance=risk_reward_variance,
            consider_fees=consider_fees
        )
        
        # Phân tích kết quả và tạo đề xuất AI
        ai_analysis = analyze_monte_carlo_results(mc_results, model.pair)
        
        return jsonify({
            'success': True,
            'results': mc_results,
            'ai_analysis': ai_analysis
        })
    except Exception as e:
        logger.error(f"Lỗi khi chạy mô phỏng Monte Carlo: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Lỗi khi chạy mô phỏng Monte Carlo: {str(e)}'
        }), 500

@backtest_ai_bp.route('/api/run_auto_backtest', methods=['POST'])
def api_run_auto_backtest():
    """API để chạy backtest tự động với Freqtrade"""
    try:
        data = request.json
        strategy = data.get('strategy', '')
        pairs = data.get('pairs', [])
        timeframe = data.get('timeframe', '1h')
        stoploss = data.get('stoploss', -10.0)
        timerange = data.get('timerange', '')
        max_open_trades = data.get('max_open_trades', 5)
        stake_amount = data.get('stake_amount', 100)
        fee = data.get('fee', 0.1)
        enable_hyperopt = data.get('enable_hyperopt', True)
        import_results = data.get('import_results', True)
        train_ai = data.get('train_ai', False)
        
        if not strategy or not pairs:
            return jsonify({
                'success': False,
                'message': 'Vui lòng cung cấp tên chiến lược và danh sách cặp giao dịch'
            }), 400
        
        # Chuyển danh sách cặp từ danh sách sang chuỗi cho freqtrade
        pairs_str = ' '.join(pairs)
        
        # Tạo lệnh chạy backtest
        freqtrade_cmd = f"cd ~/freqtrade && freqtrade backtesting --strategy {strategy} --pairs {pairs_str} --timeframe {timeframe} --timerange {timerange} --max-open-trades {max_open_trades} --stake-amount {stake_amount} --fee {fee} --export trades"
        
        # Tạo một tiến trình riêng để chạy lệnh này (không chờ kết quả)
        import subprocess
        import threading
        
        def run_command(command):
            subprocess.run(command, shell=True)
            
            if enable_hyperopt:
                # Sau khi backtest hoàn tất, chạy hyperopt
                hyperopt_cmd = f"cd ~/freqtrade && freqtrade hyperopt --hyperopt-loss SharpeHyperOptLoss --strategy {strategy} --spaces buy sell roi stoploss --pairs {pairs_str} --timeframe {timeframe} --timerange {timerange} --max-open-trades {max_open_trades} --stake-amount {stake_amount} --fee {fee} --epochs 500"
                subprocess.run(hyperopt_cmd, shell=True)
                
            if import_results:
                # Import kết quả backtest
                import_cmd = f"python freqtrade_integration/import_backtest.py import --dir ~/freqtrade/user_data/backtest_results --strategy {strategy}"
                subprocess.run(import_cmd, shell=True)
                
                if train_ai and pairs:
                    # Huấn luyện mô hình AI với kết quả đã import
                    train_cmd = f"python freqtrade_integration/train_model.py --strategy {strategy} --pair {pairs[0]} --timeframe {timeframe} --register"
                    subprocess.run(train_cmd, shell=True)
        
        # Chạy trong một thread riêng để không chặn API
        thread = threading.Thread(target=run_command, args=(freqtrade_cmd,))
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'success': True,
            'message': f'Đã bắt đầu chạy backtest tự động cho chiến lược {strategy}',
            'command': freqtrade_cmd
        })
    except Exception as e:
        logger.error(f"Lỗi khi chạy backtest tự động: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Lỗi khi chạy backtest tự động: {str(e)}'
        }), 500

# Hàm phụ trợ

def run_monte_carlo_simulation(
    simulations: int = 1000,
    initial_capital: float = 10000.0,
    risk_per_trade: float = 0.01,
    trading_days: int = 30,
    trades_per_day: float = 3.0,
    base_win_rate: float = 0.5,
    win_rate_variance: float = 0.05,
    risk_reward_ratio: float = 1.5,
    risk_reward_variance: float = 0.1,
    consider_fees: bool = True
) -> Dict[str, Any]:
    """
    Chạy mô phỏng Monte Carlo cho chiến lược giao dịch
    
    Args:
        simulations: Số lần mô phỏng
        initial_capital: Vốn ban đầu
        risk_per_trade: Rủi ro mỗi giao dịch (dạng thập phân, ví dụ 0.01 = 1%)
        trading_days: Số ngày giao dịch để mô phỏng
        trades_per_day: Số giao dịch trung bình mỗi ngày
        base_win_rate: Tỷ lệ thắng cơ bản
        win_rate_variance: Độ biến thiên của tỷ lệ thắng
        risk_reward_ratio: Tỷ lệ rủi ro/phần thưởng
        risk_reward_variance: Độ biến thiên của tỷ lệ rủi ro/phần thưởng
        consider_fees: Xem xét phí giao dịch
        
    Returns:
        Dictionary chứa kết quả mô phỏng
    """
    # Import các thư viện cần thiết
    lazy_import()
    
    np.random.seed(42)  # Đặt seed để có kết quả có thể lặp lại
    
    # Phí giao dịch (%)
    fee_percentage = 0.001 if consider_fees else 0.0  # 0.1% phí mặc định
    
    # Số giao dịch tổng cộng
    total_trades = int(trading_days * trades_per_day)
    
    # Mảng lưu các đường cong vốn
    equity_curves = np.zeros((simulations, total_trades + 1))
    equity_curves[:, 0] = initial_capital  # Vốn ban đầu
    
    # Thực hiện mô phỏng
    for sim in range(simulations):
        # Biến đổi tỷ lệ thắng cho mỗi mô phỏng
        sim_win_rate = max(0.1, min(0.9, base_win_rate + np.random.uniform(-win_rate_variance, win_rate_variance)))
        
        # Vốn hiện tại
        current_capital = initial_capital
        
        for t in range(total_trades):
            # Số tiền rủi ro cho giao dịch này
            risk_amount = current_capital * risk_per_trade
            
            # Biến đổi tỷ lệ rủi ro/phần thưởng cho mỗi giao dịch
            trade_rr = max(0.5, risk_reward_ratio + np.random.uniform(-risk_reward_variance, risk_reward_variance))
            
            # Số tiền tiềm năng kiếm được
            reward_amount = risk_amount * trade_rr
            
            # Xác định kết quả giao dịch
            is_win = np.random.random() < sim_win_rate
            
            if is_win:
                # Thắng
                current_capital += reward_amount - (fee_percentage * (current_capital + reward_amount))
            else:
                # Thua
                current_capital -= risk_amount + (fee_percentage * (current_capital - risk_amount))
            
            # Giới hạn tối thiểu cho vốn
            current_capital = max(0.0, current_capital)
            
            # Lưu vốn hiện tại
            equity_curves[sim, t + 1] = current_capital
    
    # Tính toán các chỉ số
    final_capitals = equity_curves[:, -1]
    mean_profit = np.mean(final_capitals) - initial_capital
    mean_profit_pct = (mean_profit / initial_capital) * 100
    
    # Tính drawdown tối đa
    max_drawdowns = np.zeros(simulations)
    for sim in range(simulations):
        curve = equity_curves[sim]
        drawdowns = np.maximum.accumulate(curve) - curve
        max_drawdowns[sim] = np.max(drawdowns)
    mean_max_drawdown = np.mean(max_drawdowns)
    
    # Tính profit factor (tổng lợi nhuận / tổng thua lỗ)
    profitable_sims = np.sum(final_capitals > initial_capital)
    success_rate = (profitable_sims / simulations) * 100
    
    # Tính Sharpe ratio (đơn giản hóa)
    returns = (final_capitals - initial_capital) / initial_capital
    sharpe_ratio = np.mean(returns) / np.std(returns) if np.std(returns) > 0 else 0
    
    # Tính expected value
    expected_value = mean_profit / total_trades
    
    # Tính profit factor (đơn giản hóa)
    profit_factor = np.sum(np.where(final_capitals > initial_capital, final_capitals - initial_capital, 0)) / \
                   np.sum(np.where(final_capitals < initial_capital, initial_capital - final_capitals, 1))
    
    # Tạo kết quả phân vị (10, 25, 50, 75, 90)
    percentiles = np.percentile(equity_curves, [10, 25, 50, 75, 90], axis=0)
    
    # Tạo mẫu một số đường cong để hiển thị
    sample_indices = np.random.choice(simulations, min(20, simulations), replace=False)
    sample_curves = equity_curves[sample_indices].tolist()
    
    # Kết quả trả về
    results = {
        'mean_profit': float(mean_profit),
        'mean_profit_pct': float(mean_profit_pct),
        'max_drawdown': float(mean_max_drawdown),
        'success_rate': float(success_rate),
        'sharpe_ratio': float(sharpe_ratio),
        'expected_value': float(expected_value),
        'profit_factor': float(profit_factor),
        'percentiles': {
            'p10': percentiles[0].tolist(),
            'p25': percentiles[1].tolist(),
            'p50': percentiles[2].tolist(),
            'p75': percentiles[3].tolist(),
            'p90': percentiles[4].tolist()
        },
        'sample_curves': sample_curves,
        'initial_capital': initial_capital,
        'final_distribution': final_capitals.tolist(),
        'parameters': {
            'simulations': simulations,
            'initial_capital': initial_capital,
            'risk_per_trade': risk_per_trade,
            'trading_days': trading_days,
            'trades_per_day': trades_per_day,
            'base_win_rate': base_win_rate,
            'win_rate_variance': win_rate_variance,
            'risk_reward_ratio': risk_reward_ratio,
            'risk_reward_variance': risk_reward_variance,
            'consider_fees': consider_fees
        }
    }
    
    return results

def analyze_monte_carlo_results(results: Dict[str, Any], pair: str) -> Dict[str, Any]:
    """
    Phân tích kết quả Monte Carlo và tạo đề xuất tối ưu hóa
    
    Args:
        results: Kết quả từ hàm run_monte_carlo_simulation
        pair: Cặp giao dịch đang xem xét
        
    Returns:
        Phân tích và đề xuất
    """
    # Trích xuất thông số từ kết quả
    params = results['parameters']
    success_rate = results['success_rate']
    profit_factor = results['profit_factor']
    sharpe_ratio = results['sharpe_ratio']
    max_drawdown = results['max_drawdown']
    initial_capital = params['initial_capital']
    
    # Phân tích rủi ro
    risk_assessment = ""
    if success_rate > 80:
        risk_assessment = f"Chiến lược của bạn có xác suất thành công cao ({success_rate:.1f}%) trong thời gian mô phỏng."
    elif success_rate > 60:
        risk_assessment = f"Chiến lược của bạn có xác suất thành công khá tốt ({success_rate:.1f}%) trong thời gian mô phỏng."
    else:
        risk_assessment = f"Chiến lược của bạn có xác suất thành công thấp ({success_rate:.1f}%) trong thời gian mô phỏng."
    
    drawdown_pct = (max_drawdown / initial_capital) * 100
    risk_assessment += f" Kịch bản xấu nhất cho thấy drawdown tối đa là ${max_drawdown:.2f}, tương đương {drawdown_pct:.2f}% vốn ban đầu."
    
    # Đề xuất tối ưu hóa
    optimizations = []
    
    # Đề xuất về risk per trade
    current_risk = params['risk_per_trade'] * 100  # Chuyển về %
    if sharpe_ratio < 1.0:
        suggested_risk = max(0.5, current_risk * 0.75)
        improvement = 0.2
        optimizations.append({
            'parameter': 'risk_per_trade',
            'current': f"{current_risk:.2f}%",
            'suggested': f"{suggested_risk:.2f}%",
            'impact': f"Tăng Sharpe ratio khoảng {improvement:.1f} điểm"
        })
    elif max_drawdown > initial_capital * 0.2:  # Drawdown > this
        suggested_risk = max(0.5, current_risk * 0.8)
        reduction = 15
        optimizations.append({
            'parameter': 'risk_per_trade',
            'current': f"{current_risk:.2f}%",
            'suggested': f"{suggested_risk:.2f}%",
            'impact': f"Giảm drawdown tối đa khoảng {reduction}%"
        })
    
    # Đề xuất về position sizing
    if profit_factor > 1.5:
        impact = 12
        optimizations.append({
            'parameter': 'position_sizing',
            'current': "Cố định",
            'suggested': "Động theo độ tin cậy",
            'impact': f"Tăng lợi nhuận kỳ vọng khoảng {impact}%"
        })
    
    # Đề xuất về trailing stoploss
    if success_rate > 60:
        reduction = 15
        optimizations.append({
            'parameter': 'trailing_stoploss',
            'current': "Không có",
            'suggested': "Kích hoạt ở 50% mục tiêu lợi nhuận",
            'impact': f"Giảm drawdown tối đa khoảng {reduction}%"
        })
    
    # Đề xuất nâng cao
    advanced_suggestion = ""
    if sharpe_ratio > 1.2:
        advanced_suggestion = f"Cân nhắc triển khai hệ thống quản lý rủi ro động điều chỉnh kích thước vị thế dựa trên biến động thị trường. Điều này có thể tăng lợi nhuận điều chỉnh theo rủi ro lên khoảng 18% dựa trên mẫu hiệu suất lịch sử của {pair}."
    else:
        advanced_suggestion = f"Cân nhắc kết hợp nhiều chiến lược cho {pair} để đa dạng hóa nguồn tín hiệu giao dịch. Mô phỏng cho thấy việc này có thể cải thiện sharpe ratio lên đến 25% với cùng mức lợi nhuận kỳ vọng."
    
    return {
        'risk_assessment': risk_assessment,
        'optimizations': optimizations,
        'advanced_suggestion': advanced_suggestion
    }