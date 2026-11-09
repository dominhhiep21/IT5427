# Performance Requirements — u6-integration-ui

Nguồn: `functional-design/functional-spec.md` (W1–W7), `inception/requirements-analysis/requirements.md` (NFR1, NFR4), `inception/contract-design/contract-summary.md` (C3–C9), `construction/u1-thin-slice/nfr-requirements/performance-requirements.md` (ngân sách lần bấm đầu của vùng `don-theo-thang`).

Đơn vị này là tầng hiển thị; ngân sách 2 giây của NFR1 chia cho ba loại việc: **đổi màn hình/thực thể** (chỉ vẽ lại), **chạy một truy vấn mẫu** (gọi U5 + U3 + đối chiếu), và **chạy vùng số liệu của lát cắt** (`don-theo-thang`, nạp U1 rồi truy vấn — đường khác hẳn hai đường trên).

## 1. Chỉ tiêu

| Mã | Việc | Ngưỡng | Đo bằng |
|---|---|---|---|
| NFR1.1 | Đổi thẻ, mở/đóng màn hình chi tiết, đổi thực thể ở màn hình lược đồ | < 2 giây | Đo `time.perf_counter` quanh callback trong test dashboard; không gọi lại hợp đồng |
| NFR1.2 | Chạy một truy vấn mẫu (gọi C3 + U3 + đối chiếu) | < 2 giây | Tổng thời gian callback, ghi vào log; đo trên dữ liệu thật ở Build and Test |
| NFR1.3 | Đề xuất nguồn (gọi U5 `select_source`) | < 2 giây | Như trên |
| NFR1.4 | Mở tab lần đầu (đọc C5, C6, C7) | < 2 giây | Đo trong test dashboard với tệp mẫu |
| NFR1.5 | Bấm "Chạy truy vấn" của vùng `don-theo-thang` | **lần bấm đầu ≤ 7 giây** (nạp U1 ≤ 5 + truy vấn ≤ 2); **mọi lần sau ≤ 2 giây** | `elapsed_ms` trong kết quả U1; đo trên dữ liệu thật |

**Vì sao NFR1.5 tách khỏi NFR1.1–1.4:** vùng `don-theo-thang` không đi qua C3/U3 — nó gọi U1 (`load_don_hang` + `run_monthly_orders`) trong chính tiến trình dashboard, và lần bấm đầu trả cả chi phí nạp CSV. Ngân sách 7 giây lấy đúng từ `u1-thin-slice/nfr-requirements/performance-requirements.md` (NFR1.1 + NFR1.3), không phải con số mới.

## 2. Cách giữ ngân sách

- Mở tab chỉ đọc dữ liệu đã có, **không** chạy truy vấn nào (W1 bước 2 chỉ dựng vùng ở trạng thái "Chưa chạy").
- Kết quả màn hình truy vấn giữ trong `_LAST_RUNS` của `src/integration/tab.py` theo `template_id`; kết quả vùng `don-theo-thang` giữ trong biến cấp tiến trình của `src/integration/card.py` (`_LAST_RESULT`). Đổi màn hình không chạy lại.
- Mỗi tương tác chậm hiện trạng thái chờ thay vì treo; nút bị vô hiệu trong lúc chạy.

## 3. Không áp dụng

Không có yêu cầu thông lượng hay tải đồng thời: dashboard chạy local, một người dùng (OS5).

## 4. Danh sách mã do tệp này sở hữu

`NFR1.1`, `NFR1.2`, `NFR1.3`, `NFR1.4`, `NFR1.5` — `traceability.json` trỏ về tệp này cho cả năm mã. `NFR4.1–4.4` (tiếp cận) nằm ở `functional-design/functional-spec.md` và `nfr-design/observability-design.md`, không định nghĩa lại ở đây.
