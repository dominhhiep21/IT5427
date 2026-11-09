# Observability Requirements — u1-thin-slice

Nguồn: `construction/u1-thin-slice/functional-design/functional-spec.md`, `technology-stack.md`, `inception/refined-mockups/accessibility-checklist.md`, `team-practices.md`.

## Tiếp cận (NFR4 — WCAG 2.1 AA)

| Mã | Yêu cầu | Đo bằng |
|---|---|---|
| NFR4.1 | Mọi chức năng của **tab "Tích hợp"** — bốn thẻ, vùng `don-theo-thang`, nút chạy và nút thử lại — thao tác được hoàn toàn bằng bàn phím | đi hết các phần tử tương tác bằng Tab/Enter, không dùng chuột |
| NFR4.2 | Tiêu điểm bàn phím hiện rõ, tương phản ≥ 3:1 | quan sát viền focus; đối chiếu token `focus` trong `refined-mockups/design-system-mapping.md` |
| NFR4.3 | Chữ thường tương phản ≥ 4.5:1, chữ lớn ≥ 3:1 | đo bằng công cụ kiểm tương phản |
| NFR4.4 | Không trạng thái nào chỉ dùng màu để truyền đạt | mỗi trạng thái có chữ và biểu tượng |

Chi tiết kiểm thủ công: `inception/refined-mockups/accessibility-checklist.md`.

## Nhật ký và tín hiệu

| Mã | Yêu cầu | Cách đáp ứng |
|---|---|---|
| OB-U1-1 | Mỗi lần chạy truy vấn ghi được thời gian và số dòng | ghi `elapsed_ms`, `row_count` vào kết quả trả về; sự kiện phát sinh từ dashboard dùng **một `RunContext` cho cả phiên tiến trình** (`run_id` tạo một lần, dạng `<YYYYMMDDTHHMMSS>-<micro>`) với `stage="integration"`, ghi nối vào tệp JSONL mới nhất trong `logs_dir` hoặc mở tệp `integration-<run_id>.jsonl` nếu `logs/` trống |
| OB-U1-2 | Lỗi nạp dữ liệu ghi rõ trường và cột sai | `SchemaError` mang tên trường và tên cột, đúng BR1.3; tên bảng nguồn là phần **bổ sung** của nhật ký (không phải nội dung BR1.3) và chỉ dùng cho người đọc log |
| OB-U1-3 | Số bản ghi bị loại được đếm và báo | ghi vào kết quả nạp và nhật ký |
| OB-U1-4 | Giao diện phân biệt rỗng, một phần, đầy đủ, lỗi | BR1.8; nhãn trạng thái kèm chữ, không chỉ màu |

## Ghi chú

Không có yêu cầu về metric tập trung, tracing hay alerting: hệ chạy local một người dùng. Nhật ký JSONL hiện có là đủ; đơn vị này chỉ bổ sung trường `stage` cho sự kiện phát sinh từ dashboard.
