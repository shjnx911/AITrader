"""
Routes cho tính năng Monte Carlo Simulation.
"""

import os
import json
import logging
from typing import Dict, List, Any, Optional, Tuple

try:
    import numpy as np
except ImportError:
    logging.warning("NumPy not available. Using fallback for simulation.")
    np = None  # Will be handled in the implementation

from flask import Blueprint, request, jsonify, current_app

# Import from models directly
from models import db, ModelBackup

# Tạo Blueprint
monte_carlo_bp = Blueprint('monte_carlo', __name__, url_prefix='/monte_carlo')


@monte_carlo_bp.route('/api/models', methods=['GET'])
def api_get_models():
    """Lấy danh sách các mô hình AI đã huấn luyện"""
    try:
        models = ModelBackup.query.all()
        
        models_data = []
        for model in models:
            # Extract metrics if available
            win_rate = None
            profit = None
            if model.metrics:
                win_rate = model.metrics.get('win_rate', 'N/A')
                profit = model.metrics.get('profit', 'N/A')
            
            models_data.append({
                'id': model.id,
                'name': model.model_name,
                'pair': model.pair,
                'timeframe': model.timeframe,
                'created_date': model.created_date.strftime('%Y-%m-%d %H:%M'),
                'is_active': model.is_active,
                'win_rate': win_rate,
                'profit': profit
            })
        
        return jsonify({
            'success': True,
            'models': models_data
        })
    except Exception as e:
        logging.error(f"Error retrieving models: {str(e)}")
        return jsonify({
            'success': False,
            'message': f"Error retrieving models: {str(e)}"
        }), 500


@monte_carlo_bp.route('/api/run_simulation', methods=['POST'])
def api_run_simulation():
    """Chạy mô phỏng Monte Carlo"""
    try:
        data = request.json
        
        if not data:
            return jsonify({
                'success': False,
                'message': 'Missing request data'
            }), 400
        
        model_id = data.get('model_id')
        if not model_id:
            return jsonify({
                'success': False,
                'message': 'Missing model_id parameter'
            }), 400
        
        # Check if model exists
        model = ModelBackup.query.get(model_id)
        if not model:
            return jsonify({
                'success': False, 
                'message': f'Model with ID {model_id} not found'
            }), 404
        
        # Get base win rate from model metrics
        base_win_rate = 0.5  # Default
        if model.metrics and 'win_rate' in model.metrics:
            base_win_rate = float(model.metrics['win_rate']) / 100  # Convert from percentage
        
        # Parse parameters
        params = {
            'simulations': int(data.get('simulations', 1000)),
            'initial_capital': float(data.get('initial_capital', 10000.0)),
            'risk_per_trade': float(data.get('risk_per_trade', 1.0)) / 100,  # Convert from percentage
            'trading_days': int(data.get('trading_days', 30)),
            'trades_per_day': float(data.get('trades_per_day', 3.0)),
            'base_win_rate': base_win_rate,
            'win_rate_variance': float(data.get('win_rate_variance', 5.0)) / 100,  # Convert from percentage
            'risk_reward_ratio': float(data.get('risk_reward_ratio', 1.5)),
            'risk_reward_variance': float(data.get('risk_reward_variance', 0.2)),
            'consider_fees': bool(data.get('consider_fees', True))
        }
        
        # Run simulation
        results = run_monte_carlo_simulation(**params)
        
        # Get AI analysis
        analysis = analyze_monte_carlo_results(results, model.pair)
        
        return jsonify({
            'success': True,
            'results': results,
            'ai_analysis': analysis
        })
    except Exception as e:
        logging.error(f"Error running Monte Carlo simulation: {str(e)}")
        return jsonify({
            'success': False,
            'message': f"Error running simulation: {str(e)}"
        }), 500


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
    # Tổng số giao dịch trong khoảng thời gian
    total_trades = int(trading_days * trades_per_day)
    
    # Khởi tạo mảng để lưu trữ kết quả
    all_equity_curves = np.zeros((simulations, trading_days + 1))
    all_equity_curves[:, 0] = initial_capital  # Vốn ban đầu
    
    # Phí giao dịch (nếu được bật)
    fee_rate = 0.001 if consider_fees else 0.0  # 0.1% phí giao dịch
    
    # Chạy các mô phỏng
    for sim in range(simulations):
        # Tạo tỷ lệ thắng ngẫu nhiên cho mô phỏng này, nằm trong phạm vi biến thiên
        sim_win_rate = np.random.uniform(
            base_win_rate - win_rate_variance,
            base_win_rate + win_rate_variance
        )
        
        # Tạo tỷ lệ R:R ngẫu nhiên cho mô phỏng này
        sim_risk_reward = np.random.uniform(
            risk_reward_ratio - risk_reward_variance,
            risk_reward_ratio + risk_reward_variance
        )
        
        # Tỷ lệ thắng trung bình mỗi ngày
        daily_win_rate = np.random.normal(sim_win_rate, win_rate_variance / 3, trading_days)
        daily_win_rate = np.clip(daily_win_rate, 0.1, 0.9)  # Giới hạn hợp lý
        
        # Khởi tạo vốn
        equity = initial_capital
        
        # Mô phỏng từng ngày giao dịch
        for day in range(trading_days):
            # Số giao dịch trong ngày (dao động xung quanh giá trị trung bình)
            day_trades = np.random.poisson(trades_per_day)
            
            # Tỷ lệ thắng cho ngày này
            win_rate_today = daily_win_rate[day]
            
            # Vốn cuối ngày trước
            prev_equity = equity
            
            # Mô phỏng các giao dịch trong ngày
            for _ in range(day_trades):
                # Số tiền rủi ro cho giao dịch này
                risk_amount = equity * risk_per_trade
                
                # Xác định kết quả giao dịch (thắng/thua)
                if np.random.random() < win_rate_today:
                    # Thắng: cộng thêm (risk_amount * R:R - phí)
                    win_amount = risk_amount * sim_risk_reward
                    equity += win_amount - (win_amount * fee_rate)
                else:
                    # Thua: trừ đi (risk_amount + phí)
                    equity -= risk_amount + (risk_amount * fee_rate)
                
                # Đảm bảo equity không thể âm
                equity = max(0, equity)
            
            # Lưu kết quả cuối ngày vào đường cong equity
            all_equity_curves[sim, day + 1] = equity
    
    # Tính các percentile cho đường cong equity
    percentiles = {
        'p10': np.percentile(all_equity_curves, 10, axis=0).tolist(),
        'p25': np.percentile(all_equity_curves, 25, axis=0).tolist(),
        'p50': np.percentile(all_equity_curves, 50, axis=0).tolist(),
        'p75': np.percentile(all_equity_curves, 75, axis=0).tolist(),
        'p90': np.percentile(all_equity_curves, 90, axis=0).tolist()
    }
    
    # Tính các số liệu thống kê
    final_equities = all_equity_curves[:, -1]
    
    # Lợi nhuận trung bình
    mean_profit_abs = np.mean(final_equities - initial_capital)
    mean_profit_pct = (mean_profit_abs / initial_capital) * 100
    
    # Tỷ lệ thành công
    success_rate = (np.sum(final_equities >= initial_capital) / simulations) * 100
    
    # Tính tỷ lệ drawdown tối đa
    max_drawdowns = np.zeros(simulations)
    for i in range(simulations):
        curve = all_equity_curves[i]
        peak = np.maximum.accumulate(curve)
        drawdown = (peak - curve) / peak * 100
        max_drawdowns[i] = np.max(drawdown)
    
    # Tỷ lệ profit factor
    winning_trades = np.sum(np.where(final_equities > initial_capital, 
                                    final_equities - initial_capital, 0))
    losing_trades = np.sum(np.where(final_equities < initial_capital, 
                                   initial_capital - final_equities, 0))
    profit_factor = winning_trades / losing_trades if losing_trades > 0 else float('inf')
    
    # Phân phối lợi nhuận cuối cùng
    profit_percentiles = {
        'p10': float(np.percentile(final_equities, 10)),
        'p25': float(np.percentile(final_equities, 25)),
        'p50': float(np.percentile(final_equities, 50)),
        'p75': float(np.percentile(final_equities, 75)),
        'p90': float(np.percentile(final_equities, 90))
    }
    
    # Tạo một mẫu nhỏ hơn của phân phối cuối cùng để trả về (tối đa 1000 điểm)
    sample_size = min(1000, simulations)
    sample_indices = np.random.choice(simulations, sample_size, replace=False)
    final_distribution_sample = final_equities[sample_indices].tolist()
    
    return {
        'mean_profit_abs': float(mean_profit_abs),
        'mean_profit_pct': float(mean_profit_pct),
        'success_rate': float(success_rate),
        'profit_factor': float(profit_factor),
        'max_drawdown': {
            'mean': float(np.mean(max_drawdowns)),
            'median': float(np.median(max_drawdowns)),
            'p90': float(np.percentile(max_drawdowns, 90))
        },
        'profit_percentiles': profit_percentiles,
        'percentiles': percentiles,
        'final_distribution': final_distribution_sample
    }


def analyze_monte_carlo_results(results: Dict[str, Any], pair: str) -> Dict[str, Any]:
    """
    Phân tích kết quả Monte Carlo và tạo đề xuất tối ưu hóa
    
    Args:
        results: Kết quả từ hàm run_monte_carlo_simulation
        pair: Cặp giao dịch đang xem xét
        
    Returns:
        Phân tích và đề xuất
    """
    # Phân tích mức độ rủi ro
    success_rate = results['success_rate']
    profit_factor = results['profit_factor']
    mean_profit_pct = results['mean_profit_pct']
    max_drawdown_mean = results['max_drawdown']['mean']
    
    # Xác định mức độ rủi ro
    risk_level = ""
    if success_rate < 40:
        risk_level = "Rất cao"
    elif success_rate < 55:
        risk_level = "Cao"
    elif success_rate < 70:
        risk_level = "Trung bình"
    elif success_rate < 85:
        risk_level = "Thấp"
    else:
        risk_level = "Rất thấp"
    
    # Tạo đánh giá rủi ro
    risk_assessment = f"Chiến lược giao dịch {pair} có mức độ rủi ro {risk_level.lower()}. "
    
    if success_rate < 50:
        risk_assessment += f"Với tỷ lệ thành công {success_rate:.1f}%, chiến lược này có nhiều khả năng sẽ dẫn đến lỗ vốn. "
    else:
        risk_assessment += f"Với tỷ lệ thành công {success_rate:.1f}%, chiến lược này có cơ hội sinh lời. "
    
    if profit_factor < 1.0:
        risk_assessment += f"Profit factor {profit_factor:.2f} cho thấy chiến lược không sinh lời dài hạn. "
    elif profit_factor < 1.5:
        risk_assessment += f"Profit factor {profit_factor:.2f} ở mức chấp nhận được nhưng cần cải thiện. "
    else:
        risk_assessment += f"Profit factor {profit_factor:.2f} cho thấy tiềm năng sinh lời tốt. "
    
    if max_drawdown_mean > 30:
        risk_assessment += f"Mức rút vốn tối đa trung bình {max_drawdown_mean:.1f}% rất cao, cân nhắc giảm kích thước vị thế. "
    elif max_drawdown_mean > 20:
        risk_assessment += f"Mức rút vốn tối đa trung bình {max_drawdown_mean:.1f}% ở mức cao, nên quản lý vốn chặt chẽ. "
    else:
        risk_assessment += f"Mức rút vốn tối đa trung bình {max_drawdown_mean:.1f}% ở mức chấp nhận được. "
    
    # Tạo các đề xuất tối ưu hóa
    optimizations = []
    
    # Đề xuất về kích thước vị thế (risk per trade)
    if mean_profit_pct < 0 or max_drawdown_mean > 25:
        optimizations.append({
            'parameter': 'Risk per trade',
            'current': '1.0%',
            'suggested': '0.5-0.75%',
            'impact': 'Giảm rủi ro, cải thiện khả năng tồn tại dài hạn'
        })
    
    # Đề xuất về tỷ lệ risk:reward
    if profit_factor < 1.5:
        optimizations.append({
            'parameter': 'Risk:Reward ratio',
            'current': '1.5',
            'suggested': '2.0-2.5',
            'impact': 'Tăng profit factor và cải thiện tỷ lệ thành công'
        })
    
    # Đề xuất về số lượng giao dịch
    if success_rate < 50:
        optimizations.append({
            'parameter': 'Số giao dịch',
            'current': '3 mỗi ngày',
            'suggested': '1-2 mỗi ngày',
            'impact': 'Tập trung vào chất lượng, giảm số lượng giao dịch thua lỗ'
        })
    
    # Đề xuất nâng cao
    advanced_suggestion = ""
    if mean_profit_pct < 0:
        advanced_suggestion = f"Chiến lược này chưa sẵn sàng để giao dịch thực tế. Cần cải thiện tỷ lệ thắng/thua và quản lý vốn trước khi triển khai."
    elif mean_profit_pct < 10:
        advanced_suggestion = f"Chiến lược này có thể được sử dụng với kích thước vị thế nhỏ. Theo dõi sát hiệu suất và sẵn sàng điều chỉnh nếu cần thiết."
    else:
        advanced_suggestion = f"Chiến lược này có tiềm năng sinh lời tốt. Bắt đầu với kích thước vị thế trung bình và tăng dần nếu hiệu suất duy trì ổn định."
    
    return {
        'risk_assessment': risk_assessment,
        'optimizations': optimizations,
        'advanced_suggestion': advanced_suggestion
    }