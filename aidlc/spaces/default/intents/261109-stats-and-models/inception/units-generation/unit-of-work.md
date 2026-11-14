# Units of Work

Nguồn: `../domain-design/components.md`, `../domain-design/decisions.md`, `../requirements-analysis/requirements.md`, `../user-stories/stories.md`, và `units-generation-questions.md`.

```yaml
units:
  - name: u1-statistics
    kind: service
    depends_on: []
  - name: u2-model
    kind: library
    depends_on: [u1-statistics]
  - name: u3-display
    kind: ui
    depends_on: [u1-statistics, u2-model]
```

## Bảng đơn vị

| Unit ID | Tên | Directory | Triển khai | Độ phức tạp |
|---|---|---|---|---|
| U1 | u1-statistics | `src/analytics/`, `src/pipeline/stages.py` | shared | M |
| U2 | u2-model | `src/analytics/` | shared | L |
| U3 | u3-display | `src/dashboard/`, `src/dashboard/app.py` | embedded | M |

## Ranh giới từng đơn vị

| Unit | Thuộc | Không thuộc |
|---|---|---|
| U1 | Mô-đun kiểm định; thành phần ghi/đọc báo cáo; tầng `stats` chạy **riêng** khối thống kê; cấu hình đường dẫn báo cáo; nhánh CI, README, CHANGELOG | Mô hình, khối mô hình trong báo cáo, tab hiển thị |
| U2 | Mô-đun mô hình; đặc trưng, chia theo thời gian, huấn luyện, chọn ngưỡng; mở rộng tầng `stats` để chạy thêm khối mô hình | Sửa công thức kiểm định; giao diện |
| U3 | Tab kết quả, dải tóm tắt, hai khối, bộ chọn ngưỡng, năm trạng thái; gắn tab vào `app.py`; sửa ba test hình dạng dashboard | Tính toán; định dạng tệp báo cáo |

## Yêu cầu phủ

| Đơn vị | Yêu cầu |
|---|---|
| u1-statistics | FR1, FR3, FR5.1, FR5.2, FR5.3, NFR1–NFR4 |
| u2-model | FR2, NFR1, NFR2 |
| u3-display | FR4, NFR5 |

FR5.3 chỉ thuộc u1; u3 không nhận FR5.3.

## Điều kiện xong

Mỗi đơn vị xong khi có test end-to-end riêng xanh trên dữ liệu thật, và chuỗi xác nhận bốn bước chạy đúng thứ tự. [Q5]

- U1: báo cáo có khối thống kê; khối mô hình vắng mặt và tab hiển thị đúng trạng thái "chưa có". Điều này thoả FR3.1 sau khi U2 xong; ở mốc U1, báo cáo là một phần hợp lệ.
- U2: báo cáo có đủ hai khối; AUC, ngưỡng, precision/recall đúng như FR2.
- U3: tab hiện đúng năm trạng thái, không vỡ ở 1280px, ba test hình dạng đã cập nhật.

## Ghi chú về ranh giới U1/U2

`stats-stage` thuộc U1 nhưng chỉ gọi `stats-module`; U2 mở rộng chính tầng đó để gọi thêm `model-module`. Nhờ vậy chiều phụ thuộc chỉ đi một hướng U1 → U2 → U3, không có chu trình. [Q3]
