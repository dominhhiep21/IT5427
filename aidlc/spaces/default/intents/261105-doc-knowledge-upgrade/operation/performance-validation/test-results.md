# Performance Test Results

Đo ngày 2026-11-09 trên dữ liệu thật trong `dataset/`.

## 1. Pipeline

| Tầng | Dòng vào | Dòng ra | Thời gian |
|---|---|---|---|
| ingest | 1.550.922 | 1.550.922 | 5,12 s |
| clean | 1.550.922 | 569.774 | 4,97 s |
| quality | 569.774 | 569.774 | 0,45 s |
| integrate | — | — | 3,46 s |
| linkage | 806.705 cặp ứng viên | 794.092 cặp chấm | 3,98 s |
| analyze | — | — | 0,29 s |
| **Tổng** | | | **~18,3 s** |

## 2. Truy vấn và vùng số liệu

| Phép đo | Số thật | Ngưỡng |
|---|---|---|
| Truy vấn đếm đơn của lát cắt (`run_monthly_orders`) | trong ngưỡng test 2.000 ms | < 2 s |
| Bấm "Chạy truy vấn" lần đầu (nạp + truy vấn) | ~2,5 s nạp theo ngân sách + truy vấn | ≤ 7 s |
| Bấm lần sau (truy vấn trên dữ liệu đã nạp) | trong ngưỡng 2 s | ≤ 2 s |

## 3. Ghép bản ghi

| Phép đo | Số thật | Ngưỡng |
|---|---|---|
| Chấm toàn bộ cặp khách | 3,98 s cho 806.705 cặp ứng viên | ≤ 60 s |
| Kích thước tệp kết quả | 4,07 MB (customer) + 755 B (seller) | ≤ 5 MB |
| `correct_rate` | 0,5301 với 388/732 cặp so với 0,45% của hướng chỉ-địa-lý | không đặt ngưỡng; là số đo |

## 4. Bộ nhớ

Không vượt ngưỡng cảnh báo của `config.yaml` (`memory_warn_mb: 1536`, `memory_fail_mb: 2048`) trong lần chạy này. Không có số đo chi tiết hơn: pipeline không ghi đỉnh bộ nhớ, chỉ ghi cảnh báo khi vượt.

## 5. Độ phủ và lint (cổng chất lượng mã)

| Cổng | Kết quả |
|---|---|
| Phủ dòng `src/` | 90,69% (ngưỡng 80%) |
| `ruff check .` | 0 vi phạm |
| `ruff format --check` | 28 tệp đúng định dạng |

## 6. Điều cần lưu ý

- Số đo phụ thuộc máy; ngưỡng là trần, không phải mục tiêu.
- `elapsed_ms` của `linkage` đo **cả lượt** (đọc 4 CSV + chấm + ghi + kiểm lại), không riêng phần chấm — đừng so nó với ngưỡng của riêng thuật toán.
- Tệp ghép 4,07 MB sát trần 5 MB; đây là biên mỏng nhất trong toàn bộ hệ.
