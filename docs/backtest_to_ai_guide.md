# Hướng dẫn sử dụng kết quả Backtest để huấn luyện AI

## Giới thiệu

AITradeStrategist có khả năng đặc biệt là sử dụng kết quả backtest từ Freqtrade để huấn luyện các mô hình AI. Điều này cho phép:

1. **Tối ưu hóa tham số chiến lược**: AI có thể tìm ra bộ tham số tối ưu cho từng cặp giao dịch.
2. **Dự đoán giao dịch thành công**: Phân tích các điều kiện dẫn đến giao dịch có lợi nhuận.
3. **Giảm thiểu rủi ro**: Học từ các giao dịch lỗ để tránh các mẫu tương tự trong tương lai.

## Quy trình tổng quan

Quy trình sử dụng backtest để huấn luyện AI bao gồm các bước sau:

1. Thực hiện backtest với Freqtrade cho nhiều bộ tham số khác nhau
2. Import kết quả backtest vào AITradeStrategist
3. Chuẩn bị dữ liệu huấn luyện từ các kết quả backtest
4. Huấn luyện mô hình AI (LightGBM) với dữ liệu đã chuẩn bị
5. Đánh giá và lưu mô hình AI
6. Tích hợp mô hình AI vào chiến lược giao dịch

## Các bước chi tiết

### 1. Thực hiện backtest với Freqtrade

Để có dữ liệu huấn luyện AI chất lượng, bạn cần thực hiện nhiều backtest với các tham số khác nhau:

```bash
# Backtest với hyperopt để tạo nhiều kết quả với các tham số khác nhau
freqtrade hyperopt --hyperopt-loss SharpeHyperOptLoss --strategy YourStrategy --spaces buy sell --timeframe 1h --timerange 20220101-20230101

# Backtest thông thường với các tham số cụ thể
freqtrade backtesting --strategy YourStrategy --timeframe 1h --timerange 20220101-20230101
```

Các kết quả backtest sẽ được lưu trong thư mục `user_data/backtest_results`.

### 2. Import kết quả backtest

Sử dụng công cụ import trong AITradeStrategist:

```bash
# Import tất cả kết quả backtest
python freqtrade_integration/import_backtest.py import --dir ~/freqtrade/user_data/backtest_results

# Import chỉ cho một chiến lược cụ thể
python freqtrade_integration/import_backtest.py import --dir ~/freqtrade/user_data/backtest_results --strategy YourStrategy
```

### 3. Chuẩn bị dữ liệu huấn luyện

Dữ liệu được chuẩn bị dựa trên chiến lược và cặp giao dịch:

```bash
# Chuẩn bị dữ liệu huấn luyện và lưu thành file CSV
python freqtrade_integration/import_backtest.py prepare --strategy YourStrategy --pair BTC/USDT --min-trades 100 --output training_data.csv
```

Quá trình này sẽ trích xuất các tham số chiến lược (features) và kết quả giao dịch (target) để huấn luyện AI.

### 4. Huấn luyện mô hình AI

Sử dụng script huấn luyện để tạo mô hình:

```bash
# Huấn luyện mô hình cơ bản
python freqtrade_integration/train_model.py --strategy YourStrategy --pair BTC/USDT --timeframe 1h

# Tối ưu hóa hyperparameters
python freqtrade_integration/train_model.py --strategy YourStrategy --pair BTC/USDT --timeframe 1h --optimize

# Đăng ký mô hình trong database
python freqtrade_integration/train_model.py --strategy YourStrategy --pair BTC/USDT --timeframe 1h --register
```

### 5. Đánh giá mô hình

Sau khi huấn luyện, bạn sẽ thấy các chỉ số đánh giá như:
- **Accuracy**: Tỷ lệ dự đoán đúng
- **Precision**: Tỷ lệ dự đoán đúng trong các dự đoán tích cực
- **Recall**: Tỷ lệ dự đoán đúng các trường hợp thực sự tích cực
- **F1 Score**: Trung bình điều hòa của precision và recall
- **AUC**: Diện tích dưới đường cong ROC

Chỉ số AUC > 0.7 thường đại diện cho một mô hình có khả năng dự đoán tốt.

### 6. Tích hợp mô hình vào chiến lược

Bạn có thể sử dụng mô hình đã huấn luyện theo hai cách:

#### A. Trong AITradeStrategist

Trên giao diện web AITradeStrategist:
1. Truy cập trang "Models"
2. Chọn mô hình đã huấn luyện
3. Nhấn "Activate Model" để đánh dấu là mô hình đang hoạt động
4. Nhấn "Generate Strategy" để tạo file chiến lược tương ứng

#### B. Trong Freqtrade

Copy file chiến lược được tạo vào thư mục `user_data/strategies` của Freqtrade:

```bash
cp strategies/ai_generated/AI_YourStrategy_BTC_USDT.py ~/freqtrade/user_data/strategies/
```

Sau đó, bạn có thể chạy Freqtrade với chiến lược này:

```bash
freqtrade trade --strategy AI_YourStrategy_BTC_USDT
```

## Phân tích và tối ưu hóa mô hình

### Feature Importance

AITradeStrategist hiển thị tầm quan trọng của từng tham số chiến lược đối với kết quả giao dịch:

1. Truy cập trang "Models"
2. Chọn mô hình cần phân tích
3. Xem biểu đồ "Feature Importance"

Điều này giúp bạn hiểu các tham số nào có ảnh hưởng lớn nhất đến thành công của chiến lược.

### Hyperparameter Tuning

Quá trình tối ưu hóa hyperparameter tự động tìm ra các cài đặt tốt nhất cho mô hình LightGBM, bao gồm:

- `num_leaves`: Số lượng nút lá (ảnh hưởng đến độ phức tạp của mô hình)
- `learning_rate`: Tốc độ học (ảnh hưởng đến tốc độ hội tụ)
- `feature_fraction`: Tỷ lệ features được sử dụng trong mỗi cây
- `bagging_fraction`: Tỷ lệ mẫu được sử dụng trong mỗi lần lặp

## Các chiến lược nâng cao

### Ensemble Learning

Kết hợp nhiều mô hình để tăng độ chính xác:

```bash
# Huấn luyện nhiều mô hình cho cùng một cặp
python freqtrade_integration/train_model.py --strategy Strategy1 --pair BTC/USDT
python freqtrade_integration/train_model.py --strategy Strategy2 --pair BTC/USDT
python freqtrade_integration/train_model.py --strategy Strategy3 --pair BTC/USDT

# Tạo mô hình ensemble
python freqtrade_integration/create_ensemble.py --models model1_id model2_id model3_id --pair BTC/USDT
```

### Transfer Learning

Áp dụng kiến thức từ một cặp giao dịch sang cặp khác:

```bash
# Huấn luyện mô hình gốc
python freqtrade_integration/train_model.py --strategy YourStrategy --pair BTC/USDT

# Áp dụng transfer learning cho cặp mới
python freqtrade_integration/transfer_model.py --source-model model_id --target-pair ETH/USDT
```

## Lời khuyên khi sử dụng AI với backtest

1. **Số lượng dữ liệu**: Cần ít nhất 100 giao dịch để huấn luyện mô hình có ý nghĩa.
2. **Đa dạng tham số**: Thực hiện backtest với nhiều bộ tham số khác nhau để tạo dữ liệu phong phú.
3. **Kiểm tra overfitting**: Luôn kiểm tra hiệu suất trên tập test, không chỉ tập train.
4. **Đánh giá thực tế**: Kiểm tra mô hình trong môi trường dry-run trước khi giao dịch thật.
5. **Giám sát liên tục**: Theo dõi hiệu suất mô hình và huấn luyện lại khi cần thiết.

## Tham khảo

- [Tài liệu LightGBM](https://lightgbm.readthedocs.io/)
- [Freqtrade Documentation](https://www.freqtrade.io/en/stable/)
- [Scikit-learn Documentation](https://scikit-learn.org/stable/)