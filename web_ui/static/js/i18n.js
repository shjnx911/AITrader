/**
 * Internationalization support for AITradeStrategist
 * Supports English and Vietnamese languages
 */

// Default language is English
let currentLanguage = localStorage.getItem('aitrader_language') || 'en';

// Language data
const translations = {
    en: {
        // Navigation
        "dashboard": "Dashboard",
        "performance": "Performance",
        "models": "Models",
        "settings": "Settings",
        "system_info": "System Information",
        "english": "English",
        "vietnamese": "Vietnamese",
        
        // Common
        "refresh": "Refresh",
        "export_data": "Export Data",
        "filter": "Filter",
        "apply_filter": "Apply Filter",
        "time_period": "Time Period",
        "save": "Save",
        "cancel": "Cancel",
        "close": "Close",
        "loading": "Loading...",
        "no_data": "No data available",
        "all": "All",
        "active": "Active",
        "inactive": "Inactive",
        "daily_view": "Daily View",
        "weekly_view": "Weekly View",
        "monthly_view": "Monthly View",
        "cumulative_profit_curve": "Cumulative Profit Curve",

        // Dashboard
        "total_trades": "Total Trades",
        "win_rate": "Win Rate",
        "profit": "Profit",
        "profit_usdt": "Profit (USDT)",
        "performance_over_time": "Performance Over Time",
        "performance_by_pair": "Performance By Pair",
        "recent_trades": "Recent Trades",
        "pair": "Pair",
        "open_date": "Open Date",
        "close_date": "Close Date",
        "open_price": "Open Price",
        "close_price": "Close Price",
        "status": "Status",
        "open": "Open",
        "closed": "Closed",
        "daily_view": "Daily View",
        "weekly_view": "Weekly View",
        "monthly_view": "Monthly View",
        "time": "Time",
        "cumulative_profit": "Cumulative Profit (%)",

        // Performance Analysis
        "performance_analysis": "Performance Analysis",
        "time_filter": "Time Filter",
        "days_7": "7 days",
        "days_30": "30 days",
        "days_90": "90 days",
        "days_180": "180 days",
        "days_365": "365 days",
        "pair_filter": "Pair Filter",
        "timeframe": "Timeframe",
        "timeframe_filter": "Timeframe Filter",
        "strategy": "Strategy",
        "strategy_filter": "Strategy Filter",
        "performance_overview": "Performance Overview",
        "win_loss": "Win/Loss",
        "detailed_statistics": "Detailed Statistics",
        "avg_trade_duration": "Avg. Trade Duration",
        "max_profit": "Max Profit",
        "max_loss": "Max Loss",
        "max_drawdown": "Max Drawdown",
        "sharpe_ratio": "Sharpe Ratio",
        "time_statistics": "Time Statistics",
        "daily_profit_avg": "Daily Profit Avg",
        "weekly_profit_avg": "Weekly Profit Avg",
        "monthly_profit_avg": "Monthly Profit Avg",
        "trades_per_day": "Trades Per Day",
        "active_since": "Active Since",
        "cumulative_profit_curve": "Cumulative Profit Curve",
        "profit_distribution": "Profit Distribution",
        "trade_list": "Trade List",
        "trade_id": "ID",
        "trade_duration": "Duration",
        "exit_reason": "Exit Reason",
        "pagination": "Pagination",
        "previous": "Previous",
        "next": "Next",
        
        // Models
        "model_management": "Model Management",
        "upload_new_model": "Upload New Model",
        "active_models": "Active Models",
        "saved_models": "Saved Models",
        "model_name": "Model Name",
        "model_version": "Version",
        "created_date": "Created Date",
        "file_size": "File Size",
        "metrics": "Metrics",
        "actions": "Actions",
        "deactivate": "Deactivate",
        "activate": "Activate",
        "download": "Download",
        "delete": "Delete",
        "upload_model": "Upload Model",
        "drop_model_file": "Drop model file here",
        "or": "or",
        "select_file": "Select File",
        "supported_formats": "Supported formats: .pkl, .joblib, .onnx",
        "activate_after_upload": "Activate model after upload",
        
        // Settings
        "system_settings": "System Settings",
        "save_settings": "Save Settings",
        "trading_config": "Trading Configuration",
        "exchange": "Exchange",
        "base_currency": "Base Currency",
        "stake_amount": "Stake Amount",
        "max_open_trades": "Max Open Trades",
        "dry_run_mode": "Dry Run Mode (no real trading)",
        "ai_model_config": "AI Model Configuration",
        "default_strategy": "Default Strategy",
        "prediction_interval": "Prediction Interval (minutes)",
        "backtest_period": "Backtest Period",
        "model_update_interval": "Model Update Interval (hours)",
        "use_gpu": "Use GPU acceleration (if available)",
        "auto_optimize": "Auto-optimize hyperparameters",
        "notification_settings": "Notification Settings",
        "notification_channel": "Notification Channel",
        "notification_target": "Notification Target",
        "notify_trades": "Notify on new trades",
        "notify_performance": "Notify on performance reports",
        "notify_errors": "Notify on system errors",
        "api_settings": "API Settings",
        "freqtrade_api_url": "Freqtrade API URL",
        "api_key": "API Key",
        "api_secret": "API Secret",
        "test_connection": "Test Connection",
        
        // Documentation
        "documentation": "Documentation",
        "user_guide": "User Guide",
        "api_docs": "API Documentation",
        "getting_started": "Getting Started",
        "faq": "FAQ",
        
        // System Status
        "gpu": "GPU",
        "freqtrade": "Freqtrade",
        "cpu_mode": "CPU Mode",
        "not_connected": "Not Connected",
        "connected": "Connected",
        "checking": "Checking...",
        
        // Report
        "generate_report": "Generate Report",
        "export_chart": "Export Chart",
        "export_csv": "Export CSV",
        "export_pdf": "Export PDF",
        "report_period": "Report Period",
        "report_type": "Report Type",
        "summary_report": "Summary Report",
        "detailed_report": "Detailed Report",
        "custom_report": "Custom Report",
        
        // Theme
        "theme": "Theme",
        "dark_mode": "Dark Mode",
        "light_mode": "Light Mode",
        "system_default": "System Default",
        
        // Language
        "language": "Language",
        "english": "English",
        "vietnamese": "Vietnamese",
        
        // Notifications
        "success": "Success",
        "error": "Error",
        "warning": "Warning",
        "info": "Information",
        "settings_saved": "Settings saved successfully!",
        "connection_success": "Connection successful!",
        "connection_failed": "Connection failed!",
        "model_uploaded": "Model uploaded successfully!",
        "model_activated": "Model activated successfully!",
        "model_deactivated": "Model deactivated successfully!",
        "filter_applied": "Filters applied.",
        
        // Strategy recommendation
        "strategy_recommendation": "Strategy Recommendation",
        "recommended_strategies": "Recommended Strategies",
        "strategy_performance": "Strategy Performance",
        "strategy_description": "Strategy Description",
        "risk_level": "Risk Level",
        "low_risk": "Low Risk",
        "medium_risk": "Medium Risk",
        "high_risk": "High Risk",
        "expected_return": "Expected Return",
        "success_rate": "Success Rate",
        "apply_strategy": "Apply Strategy",
        "customize_strategy": "Customize Strategy",
        "strategy_details": "Strategy Details"
    },
    vi: {
        // Navigation
        "dashboard": "Dashboard",
        "performance": "Hiệu Suất",
        "models": "Mô Hình",
        "settings": "Cài Đặt",
        "system_info": "Thông Tin Hệ Thống",
        
        // Common
        "refresh": "Làm Mới",
        "export_data": "Xuất Dữ Liệu",
        "filter": "Bộ Lọc",
        "apply_filter": "Áp Dụng Bộ Lọc",
        "time_period": "Thời Gian",
        "save": "Lưu",
        "cancel": "Hủy",
        "close": "Đóng",
        "loading": "Đang tải...",
        "no_data": "Không có dữ liệu",
        "all": "Tất Cả",
        "active": "Đang Hoạt Động",
        "inactive": "Không Hoạt Động",

        // Dashboard
        "total_trades": "Tổng Giao Dịch",
        "win_rate": "Tỷ Lệ Thắng",
        "profit": "Lợi Nhuận",
        "profit_usdt": "Lợi Nhuận (USDT)",
        "performance_over_time": "Hiệu Suất Theo Thời Gian",
        "performance_by_pair": "Hiệu Suất Theo Cặp",
        "recent_trades": "Giao Dịch Gần Đây",
        "pair": "Cặp",
        "open_date": "Thời Gian Mở",
        "close_date": "Thời Gian Đóng",
        "open_price": "Giá Mở",
        "close_price": "Giá Đóng",
        "status": "Trạng Thái",
        "open": "Mở",
        "closed": "Đóng",

        // Performance Analysis
        "performance_analysis": "Phân Tích Hiệu Suất",
        "time_filter": "Lọc Thời Gian",
        "days_7": "7 ngày",
        "days_30": "30 ngày",
        "days_90": "90 ngày",
        "days_180": "180 ngày",
        "days_365": "365 ngày",
        "pair_filter": "Lọc Theo Cặp",
        "timeframe": "Khung Thời Gian",
        "timeframe_filter": "Lọc Khung Thời Gian",
        "strategy": "Chiến Lược",
        "strategy_filter": "Lọc Chiến Lược",
        "performance_overview": "Tổng Quan Hiệu Suất",
        "win_loss": "Thắng/Thua",
        "detailed_statistics": "Thống Kê Chi Tiết",
        "avg_trade_duration": "Thời Gian Giao Dịch TB",
        "max_profit": "Lợi Nhuận Lớn Nhất",
        "max_loss": "Lỗ Lớn Nhất",
        "max_drawdown": "Drawdown Tối Đa",
        "sharpe_ratio": "Sharpe Ratio",
        "time_statistics": "Thống Kê Theo Thời Gian",
        "daily_profit_avg": "Lợi Nhuận Hàng Ngày TB",
        "weekly_profit_avg": "Lợi Nhuận Hàng Tuần TB",
        "monthly_profit_avg": "Lợi Nhuận Hàng Tháng TB",
        "trades_per_day": "Giao Dịch Theo Ngày TB",
        "active_since": "Hoạt Động Từ",
        "cumulative_profit_curve": "Đường Cong Lợi Nhuận Tích Lũy",
        "profit_distribution": "Phân Phối Lợi Nhuận",
        "trade_list": "Danh Sách Giao Dịch",
        "daily_view": "Theo Ngày",
        "weekly_view": "Theo Tuần",
        "monthly_view": "Theo Tháng",
        "time": "Thời Gian",
        "cumulative_profit": "Lợi Nhuận Tích Lũy (%)",
        "trade_id": "ID",
        "trade_duration": "Thời Gian",
        "exit_reason": "Lý Do Đóng",
        "pagination": "Phân Trang",
        "previous": "Trước",
        "next": "Tiếp",
        
        // Models
        "model_management": "Quản Lý Mô Hình",
        "upload_new_model": "Tải Lên Mô Hình Mới",
        "active_models": "Mô Hình Đang Hoạt Động",
        "saved_models": "Mô Hình Đã Lưu",
        "model_name": "Tên Mô Hình",
        "model_version": "Phiên Bản",
        "created_date": "Ngày Tạo",
        "file_size": "Kích Thước",
        "metrics": "Chỉ Số",
        "actions": "Hành Động",
        "deactivate": "Ngừng Sử Dụng",
        "activate": "Kích Hoạt",
        "download": "Tải Về",
        "delete": "Xóa",
        "upload_model": "Tải Lên Mô Hình",
        "drop_model_file": "Kéo và thả tệp mô hình vào đây",
        "or": "hoặc",
        "select_file": "Chọn Tệp",
        "supported_formats": "Hỗ trợ định dạng: .pkl, .joblib, .onnx",
        "activate_after_upload": "Kích hoạt mô hình sau khi tải lên",
        
        // Settings
        "system_settings": "Cài Đặt Hệ Thống",
        "save_settings": "Lưu Cài Đặt",
        "trading_config": "Cấu Hình Giao Dịch",
        "exchange": "Sàn Giao Dịch",
        "base_currency": "Tiền Tệ Cơ Sở",
        "stake_amount": "Số Lượng Đặt Cọc",
        "max_open_trades": "Số Giao Dịch Mở Tối Đa",
        "dry_run_mode": "Chế Độ Thử Nghiệm (không giao dịch thật)",
        "ai_model_config": "Cấu Hình Mô Hình AI",
        "default_strategy": "Chiến Lược Mặc Định",
        "prediction_interval": "Khoảng Dự Đoán (phút)",
        "backtest_period": "Thời Gian Kiểm Định",
        "model_update_interval": "Cập Nhật Mô Hình (giờ)",
        "use_gpu": "Sử Dụng GPU để tăng tốc (nếu có)",
        "auto_optimize": "Tự động tối ưu hóa siêu tham số",
        "notification_settings": "Cài Đặt Thông Báo",
        "notification_channel": "Kênh Thông Báo",
        "notification_target": "Địa Chỉ Nhận Thông Báo",
        "notify_trades": "Thông báo giao dịch mới",
        "notify_performance": "Thông báo báo cáo hiệu suất",
        "notify_errors": "Thông báo lỗi hệ thống",
        "api_settings": "Thiết Lập API",
        "freqtrade_api_url": "URL API Freqtrade",
        "api_key": "Khóa API",
        "api_secret": "Bí Mật API",
        "test_connection": "Kiểm Tra Kết Nối",
        
        // Documentation
        "documentation": "Tài Liệu",
        "user_guide": "Hướng Dẫn Sử Dụng",
        "api_docs": "Tài Liệu API",
        "getting_started": "Bắt Đầu",
        "faq": "Câu Hỏi Thường Gặp",
        
        // System Status
        "gpu": "GPU",
        "freqtrade": "Freqtrade",
        "cpu_mode": "Chế Độ CPU",
        "not_connected": "Không Kết Nối",
        "connected": "Đã Kết Nối",
        "checking": "Đang Kiểm Tra...",
        
        // Report
        "generate_report": "Tạo Báo Cáo",
        "export_chart": "Xuất Biểu Đồ",
        "export_csv": "Xuất CSV",
        "export_pdf": "Xuất PDF",
        "report_period": "Thời Gian Báo Cáo",
        "report_type": "Loại Báo Cáo",
        "summary_report": "Báo Cáo Tóm Tắt",
        "detailed_report": "Báo Cáo Chi Tiết",
        "custom_report": "Báo Cáo Tùy Chỉnh",
        
        // Theme
        "theme": "Giao Diện",
        "dark_mode": "Chế Độ Tối",
        "light_mode": "Chế Độ Sáng",
        "system_default": "Mặc Định Hệ Thống",
        
        // Language
        "language": "Ngôn Ngữ",
        "english": "Tiếng Anh",
        "vietnamese": "Tiếng Việt",
        
        // Notifications
        "success": "Thành Công",
        "error": "Lỗi",
        "warning": "Cảnh Báo",
        "info": "Thông Tin",
        "settings_saved": "Đã lưu cài đặt thành công!",
        "connection_success": "Kết nối thành công!",
        "connection_failed": "Kết nối thất bại!",
        "model_uploaded": "Đã tải lên mô hình thành công!",
        "model_activated": "Đã kích hoạt mô hình thành công!",
        "model_deactivated": "Đã ngừng kích hoạt mô hình!",
        "filter_applied": "Đã áp dụng bộ lọc.",
        
        // Strategy recommendation
        "strategy_recommendation": "Gợi Ý Chiến Lược",
        "recommended_strategies": "Chiến Lược Được Gợi Ý",
        "strategy_performance": "Hiệu Suất Chiến Lược",
        "strategy_description": "Mô Tả Chiến Lược",
        "risk_level": "Mức Độ Rủi Ro",
        "low_risk": "Rủi Ro Thấp",
        "medium_risk": "Rủi Ro Trung Bình",
        "high_risk": "Rủi Ro Cao",
        "expected_return": "Lợi Nhuận Dự Kiến",
        "success_rate": "Tỷ Lệ Thành Công",
        "apply_strategy": "Áp Dụng Chiến Lược",
        "customize_strategy": "Tùy Chỉnh Chiến Lược",
        "strategy_details": "Chi Tiết Chiến Lược"
    }
};

/**
 * Get translation for a key
 * @param {string} key - The translation key
 * @returns {string} - The translated text
 */
function t(key) {
    if (translations[currentLanguage] && translations[currentLanguage][key]) {
        return translations[currentLanguage][key];
    }
    
    // Fallback to English if the key doesn't exist in the current language
    if (translations.en && translations.en[key]) {
        return translations.en[key];
    }
    
    // Return the key itself if no translation is found
    return key;
}

/**
 * Change the application language
 * @param {string} lang - The language code ('en' or 'vi')
 */
function changeLanguage(lang) {
    if (lang !== 'en' && lang !== 'vi') {
        console.error('Unsupported language:', lang);
        return;
    }
    
    currentLanguage = lang;
    localStorage.setItem('aitrader_language', lang);
    
    // Update all translatable elements on the page
    updatePageTranslations();
    
    // Trigger a custom event for components that need to know about language changes
    document.dispatchEvent(new CustomEvent('languageChanged', { detail: { language: lang } }));
}

/**
 * Update all translatable elements on the page
 */
function updatePageTranslations() {
    // Update all elements with data-i18n attribute
    document.querySelectorAll('[data-i18n]').forEach(element => {
        const key = element.getAttribute('data-i18n');
        element.textContent = t(key);
    });
    
    // Update all elements with data-i18n-placeholder attribute
    document.querySelectorAll('[data-i18n-placeholder]').forEach(element => {
        const key = element.getAttribute('data-i18n-placeholder');
        element.placeholder = t(key);
    });
    
    // Update all elements with data-i18n-title attribute
    document.querySelectorAll('[data-i18n-title]').forEach(element => {
        const key = element.getAttribute('data-i18n-title');
        element.title = t(key);
    });
}

/**
 * Get the current language
 * @returns {string} - The current language code
 */
function getCurrentLanguage() {
    return currentLanguage;
}

/**
 * Initialize internationalization
 */
function initI18n() {
    // Set up language switcher if it exists
    const languageSwitcher = document.getElementById('language-switcher');
    if (languageSwitcher) {
        languageSwitcher.value = currentLanguage;
        languageSwitcher.addEventListener('change', (e) => {
            changeLanguage(e.target.value);
        });
    }
    
    // Initial translation of the page
    updatePageTranslations();
}

// Initialize when the DOM is ready
document.addEventListener('DOMContentLoaded', initI18n);

// Export functions for use in other scripts
window.i18n = {
    t,
    changeLanguage,
    getCurrentLanguage,
    updatePageTranslations
};