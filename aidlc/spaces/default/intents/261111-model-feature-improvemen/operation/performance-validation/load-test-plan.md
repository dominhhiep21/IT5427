# Load Test Plan — intent `261111-model-feature-improvemen`

## 1. Không có load test, và lý do cụ thể

Hệ thống là **một tiến trình localhost cho một người**. Không có người dùng đồng thời, không có hàng đợi, không có tầng mạng. Một load test (LOCUST/k6/JMeter) ở đây sẽ đo… chính cái máy đang chạy nó.

Điều **đo được và đã đo** là ba ngưỡng tương tác và hai ngân sách lô:

| Loại | Công cụ | Đo gì |
|---|---|---|
| Ngân sách lô | `time.perf_counter()` trong test `slow` | thời gian tầng `stats` và riêng bước huấn luyện |
| Ngân sách tương tác | test đơn vị `-k budget` | `score_item`, `load_model`, `build_prediction_body` |
| Tải dữ liệu | `--stage all` trên `dataset/` thật | toàn pipeline qua 9 CSV |

## 2. Kịch bản "tải" thật của đợt này

| Kịch bản | Mô phỏng bằng | Kỳ vọng |
|---|---|---|
| Mở tab khi báo cáo đủ | `render_analysis(config, TAB_VALUE)` trong test | dựng 4 mục, không ném |
| Bấm Dự đoán 20 lần liên tiếp | 20 lần `score_item` (PR3.1) | trung bình < 200 ms |
| Nạp mô hình sau khi huấn luyện lại | `load_model` trên tệp mới (PR3.2) | < 2 s |
| Chạy lại toàn pipeline | `run --stage all` + `--stage stats` (chuỗi xác nhận) | `stats` < 300 s, huấn luyện < 240 s |

## 3. Điều kiện để cần load test thật

Khi có ≥ 2 người dùng đồng thời **hoặc** dashboard được phục vụ qua mạng. Lúc đó mới cần: k6 với 10–50 VU, đo p95 của `/` và callback, và một ngưỡng p95 riêng cho lần bấm Dự đoán.

## 4. Không đo trong đợt này

- Bộ nhớ: khối dựng cây nhỏ, mô hình 4,8 KB.
- Độ trễ mạng: bind `127.0.0.1`.
- Auto-scaling: không có hạ tầng co giãn.
