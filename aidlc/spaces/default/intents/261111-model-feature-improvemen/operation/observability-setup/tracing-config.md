# Tracing Configuration — intent `261111-model-feature-improvemen`

## 1. Không có distributed tracing, và lý do

Không có lời gọi mạng giữa các thành phần: một tiến trình Python, một tệp DuckDB nhúng, hai tệp cục bộ (`analysis.json`, `model.pkl`). Không có ranh giới nào để một trace băng qua. Thêm OpenTelemetry vào đây là dựng hạ tầng cho một đường đi không tồn tại.

## 2. Cái đóng vai trace: `run_id`

| Ranh giới | Cách nối |
|---|---|
| Một lượt chạy pipeline | mọi sự kiện trong lượt mang cùng `run_id` (`<UTC>%Y%m%dT%H%M%S>-<8 hex>`) |
| Một lần bấm Dự đoán | ba sự kiện `prediction.*` ghi cùng tệp nhật ký của dashboard (`stage="integration"`) |
| Từ người dùng tới dữ liệu | tab hiện `status` + `missing` từ `ReportView`, đủ để biết báo cáo nào đang được đọc |

Đây là tương quan theo **thời điểm và tệp**, không phải span tree. Với một tiến trình, thế là đủ.

## 3. Nếu sau này có nhiều tiến trình

Khi tách dashboard thành dịch vụ riêng và pipeline thành worker, điều kiện để thêm tracing: có ít nhất hai tiến trình gọi nhau. Khi đó mới đáng truyền `run_id`/`trace_id` qua header và dựng span cho ba chặng: đọc báo cáo → nạp mô hình → chấm điểm.

## 4. Điều đã làm để không phải thêm tracing sau này

- Mọi sự kiện đã có `run_id`, `stage`, `event` — khuôn đã đúng để nối vào một hệ trace.
- Lỗi mô hình ghi **thông điệp thô** vào nhật ký (không vào giao diện), nên chẩn đoán không cần trace.
