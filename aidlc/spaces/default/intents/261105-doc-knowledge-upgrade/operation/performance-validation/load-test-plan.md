# Load Test Plan

## 1. Không có load test theo nghĩa tải đồng thời

Một người dùng, một tiến trình, không có endpoint công khai. "Tải" duy nhất cần kiểm là **khối lượng dữ liệu** và **độ trễ của từng thao tác**.

## 2. Ba phép đo đã thực hiện

| Phép đo | Cách làm | Vì sao đây là "tải" thật |
|---|---|---|
| Toàn bộ pipeline trên dữ liệu gốc | `python -X utf8 -m src.pipeline run --stage all` | 1.550.922 dòng vào, 569.774 dòng ra, 806.705 cặp ghép ứng viên |
| Truy vấn đếm đơn của lát cắt | test hiệu năng ngưỡng cứng 2.000 ms | đo riêng phần thực thi, không tính nạp |
| Chấm toàn bộ cặp ghép khách | test hiệu năng ~200.000 cặp trong bộ nhanh; lượt đầy đủ 806.705 cặp đo qua `elapsed_ms` | thuật toán bậc hai nếu làm sai; đây là chỗ dễ nổ nhất |

## 3. Điều kiện đo

- Máy phát triển, Windows, Python 3.13, `.venv` với `--system-site-packages`.
- Dữ liệu thật trong `dataset/`, không dùng mẫu.
- Không chạy dashboard song song (tranh I/O và khoá `warehouse/`).
- Mọi lệnh chạy `-X utf8`.

## 4. Điều không làm

- **Không** giả lập nhiều người dùng đồng thời: kiến trúc không hỗ trợ và không có yêu cầu.
- **Không** đo p95/p99: với một người dùng, một phép đo mỗi thao tác là đủ; phân vị chỉ có nghĩa khi có phân bố.
- **Không** dựng môi trường giống production: không có production.

## 5. Khi dữ liệu tăng

Nếu `dataset/` lớn lên, chỗ vỡ đầu tiên theo thứ tự dự kiến:

1. `linkage` — số cặp ứng viên tăng theo bình phương số bản ghi trong một nhóm zip.
2. `ingest` — đọc CSV tuyến tính, tăng chậm hơn.
3. Kích thước tệp ghép — đang 4,07 MB, sát trần 5 MB.

Ngưỡng và cách kiểm đã có ở `performance-test-instructions.md` của Build and Test.
