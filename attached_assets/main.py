import os
import sys
import logging
from datetime import datetime
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase

# Cấu hình logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('freqai_lightgbm')

# Định nghĩa class Base cho SQLAlchemy
class Base(DeclarativeBase):
    pass

# Khởi tạo SQLAlchemy
db = SQLAlchemy(model_class=Base)

# Thêm đường dẫn gốc vào sys.path để import các module khác
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import app từ web_ui/app.py
from web_ui.app import app

# Cấu hình database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

# Khởi tạo database với ứng dụng
db.init_app(app)

# Khởi tạo database tables
with app.app_context():
    class ModelBackup(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        model_name = db.Column(db.String(100), nullable=False)
        created_date = db.Column(db.DateTime, nullable=False)
        pair = db.Column(db.String(50), nullable=False)
        timeframe = db.Column(db.String(10), nullable=False)
        backup_path = db.Column(db.String(255), nullable=False)
        metrics = db.Column(db.JSON, nullable=True)
        is_active = db.Column(db.Boolean, default=False)
        
    class TrainingConfig(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        config_name = db.Column(db.String(100), nullable=False)
        params = db.Column(db.JSON, nullable=False)
        created_date = db.Column(db.DateTime, nullable=False)
        
    db.create_all()

# Thêm các route mới cho tính năng backup và restore
@app.route('/api/backup_model', methods=['POST'])
def backup_model():
    """Lưu trữ một mô hình AI đã được huấn luyện"""
    data = request.json
    
    # Tạo bản ghi lưu trữ trong database
    new_backup = ModelBackup(
        model_name=data.get('model_name'),
        created_date=datetime.now(),
        pair=data.get('pair'),
        timeframe=data.get('timeframe'),
        backup_path=data.get('backup_path'),
        metrics=data.get('metrics', {}),
        is_active=data.get('is_active', False)
    )
    
    db.session.add(new_backup)
    db.session.commit()
    
    return jsonify({"status": "success", "message": "Model backup created", "id": new_backup.id})

@app.route('/api/get_model_backups', methods=['GET'])
def get_model_backups():
    """Lấy danh sách các backup mô hình"""
    backups = ModelBackup.query.order_by(ModelBackup.created_date.desc()).all()
    
    result = []
    for backup in backups:
        result.append({
            "id": backup.id,
            "model_name": backup.model_name,
            "created_date": backup.created_date.strftime("%Y-%m-%d %H:%M:%S"),
            "pair": backup.pair,
            "timeframe": backup.timeframe,
            "is_active": backup.is_active
        })
    
    return jsonify({"status": "success", "backups": result})

@app.route('/api/restore_model', methods=['POST'])
def restore_model():
    """Phục hồi một mô hình từ backup"""
    data = request.json
    backup_id = data.get('backup_id')
    
    backup = ModelBackup.query.get(backup_id)
    if not backup:
        return jsonify({"status": "error", "message": "Backup not found"})
    
    # Cập nhật trạng thái active cho tất cả các backup
    ModelBackup.query.update({ModelBackup.is_active: False})
    
    # Đặt backup được chọn thành active
    backup.is_active = True
    db.session.commit()
    
    return jsonify({
        "status": "success", 
        "message": "Model restored successfully",
        "model_info": {
            "model_name": backup.model_name,
            "pair": backup.pair,
            "timeframe": backup.timeframe,
            "backup_path": backup.backup_path
        }
    })

# Khởi chạy ứng dụng khi thực thi trực tiếp
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)