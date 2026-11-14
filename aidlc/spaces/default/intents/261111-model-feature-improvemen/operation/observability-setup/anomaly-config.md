# Anomaly Detection Configuration — intent `261111-model-feature-improvemen`

## 1. Không có phát hiện dị thường tự động, và cái gì thay thế

Không có chuỗi thời gian liên tục để học đường cơ sở: mỗi lượt chạy là một sự kiện rời rạc do người dùng kích hoạt. Phát hiện dị thường theo mùa/thống kê cần dữ liệu đều đặn — không có.

Thay vào đó là **kiểm dị thường theo luật**, đã có sẵn và đang chạy:

| Luật | Ở đâu | Phát hiện gì |
|---|---|---|
| 10 bộ đếm allowlist | `src/quality/allowlist.py` | null bất thường, giá outlier, thiếu category, thiếu translation, nhiều review một đơn… |
| 9 check số dòng | `src/quality/gate.py` chế độ `full` | bảng nguồn/mart lệch số dòng đã chốt |
| 5 KPI + dung sai | `src/integrate/reconcile.py` | doanh thu/đơn/AOV/tỉ lệ trễ lệch |
| Cờ `is_sparse_period` | khối thống kê | tháng quá ít đơn để so sánh |
| `auc_below_target` | khối mô hình | AUC dưới mốc mục tiêu |

## 2. Thêm một luật mới trong đợt này

`beats_floor(auc, baseline_auc)` — mốc sàn không bao giờ thấp hơn baseline đo lại, nên hai cổng không thể cho hai kết luận trái nhau. Chạy trong test `slow` trên báo cáo thật.

## 3. Khi nào mới đáng phát hiện dị thường tự động

Khi có ≥ 30 lượt chạy đều đặn (ví dụ chạy theo lịch). Khi đó mới có đường cơ sở cho: thời gian tầng `stats`, số dòng quần thể, AUC, tỉ lệ gắn cờ. Hiện chưa có lịch chạy nên chưa có đường cơ sở.

## 4. Điều không làm

- Không có mô hình phát hiện dị thường (thêm phụ thuộc, thêm dữ liệu huấn luyện, không có nhu cầu).
- Không có ngưỡng động.
- Không có cảnh báo tự động — xem `alarms.md` §1.
