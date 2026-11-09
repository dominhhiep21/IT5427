# Deployment Strategy

## 1. Chiến lược: recreate, trên một máy

Không blue-green, không canary, không rolling: cả ba cần hai môi trường hoặc lưu lượng để chia, đợt này không có cái nào.

| Bước | Việc | Lệnh |
|---|---|---|
| 1 | Dừng tiến trình cũ | `Ctrl+C` ở cửa sổ dashboard |
| 2 | Cập nhật mã | `git checkout <commit>` hoặc `git pull` trên nhánh làm việc |
| 3 | Cài lại phụ thuộc (nếu `requirements.txt` đổi) | `.venv\Scripts\python.exe -m pip install -r requirements.txt` |
| 4 | Dựng dữ liệu | `.venv\Scripts\python.exe -X utf8 -m src.pipeline run --stage all` |
| 5 | Chạy | `.venv\Scripts\python.exe -X utf8 -m src.dashboard` |
| 6 | Kiểm tra khói | mở tab "Tích hợp", bấm "Chạy truy vấn" ở vùng `don-theo-thang` |

**Bước 1 là bắt buộc trước bước 4**: dashboard và `integrate` dùng chung tệp `warehouse/olist.duckdb`, nên chạy song song sẽ khoá.

## 2. Vì sao không có "môi trường thứ hai"

- Không có người dùng thứ hai; dashboard bind `127.0.0.1`.
- Không có dịch vụ ngoài nào cần mạng, trừ lời gọi IBGE có điều kiện trong `integrate`.
- Toàn bộ dữ liệu dẫn xuất tái lập được từ `dataset/`, nên "triển khai lại từ đầu" chỉ là xoá bốn thư mục sinh ra và chạy lại.

## 3. Cổng trước khi coi là đã phát hành

| Cổng | Ngưỡng | Chạy ở đâu |
|---|---|---|
| Bộ test nhanh | 375 test xanh | máy local |
| Bộ test chậm | 9 test xanh | máy local |
| Phủ dòng | ≥ 80% (thực tế 90,69%) | máy local |
| Lint + định dạng | 0 vi phạm | máy local và CI |
| Pipeline + `QualityGate` + `KpiReconciler` | xanh 6/6 tầng | máy local và CI |
| Kiểm bằng mắt | vùng `don-theo-thang` hiện số liệu | máy local, có người |

Không cổng nào được bỏ qua vì "lần trước vẫn chạy được".

## 4. Không áp dụng

Feature flag, dark launch, migration cơ sở dữ liệu, auto-scaling, multi-AZ, multi-region: không có thành phần nào cần chúng trong một tiến trình local, một người dùng.
