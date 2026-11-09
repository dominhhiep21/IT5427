# Performance Test Instructions

## 1. Ngưỡng phải kiểm

| Mã | Đối tượng | Ngưỡng | Nguồn |
|---|---|---|---|
| NFR1.1 | Đổi thẻ, mở/đóng màn hình chi tiết | < 2 giây | u6 `performance-requirements.md` |
| NFR1.2 | Chạy một truy vấn mẫu (C3 + U3 + đối chiếu) | < 2 giây | u3, u6 |
| NFR1.3 | Đề xuất nguồn (U5 `select_source`) | < 2 giây | u5, u6 |
| NFR1.4 | Mở tab lần đầu (đọc C5/C6/C7) | < 2 giây | u6 |
| NFR1.5 | Bấm "Chạy truy vấn" của vùng `don-theo-thang` | lần đầu ≤ 7 giây (5 nạp + 2 truy vấn), lần sau ≤ 2 giây | u1 + u6 |
| NFR1.1 (U1) | Một lần nạp 99.441 đơn | < 5 giây | u1 |
| NFR1.2 (U1) | Truy vấn đếm đơn theo tháng | < 2 giây | u1 |
| NFR1.1 (U4) | Chặn và xét 806.705 cặp ứng viên | ≤ 60 giây cho cả lượt | u4 |

## 2. Cách đo đã có trong mã

- **U1**: `LoadResult.elapsed_ms`, `QueryRunResult.elapsed_ms`; test hiệu năng ngưỡng cứng 2.000 ms trong `tests/unit/test_integration_query.py`.
- **U3**: `QueryRunResult.elapsed_ms` đo quanh lời gọi; vượt `SLOW_QUERY_MS` phát `integration.query.slow` mức WARNING (ghi nhận, không chặn).
- **U4**: `elapsed_ms` của `integration.linkage.completed`, đo **cả lượt** (đọc 4 CSV + chấm + ghi + kiểm lại); test hiệu năng chấm ~200.000 cặp trong bộ nhanh.
- **U6**: đo `time.perf_counter` quanh callback trong test dashboard.

## 3. Lệnh chạy

```powershell
.venv\Scripts\python.exe -X utf8 -m pytest tests/unit/test_integration_query.py -q
.venv\Scripts\python.exe -X utf8 -m pytest tests/unit/test_linkage_score.py -q
.venv\Scripts\python.exe -X utf8 -m pytest tests/unit/test_integration_tab.py tests/unit/test_dashboard_smoke.py -q
```

Đo trên dữ liệu thật: chạy `python -X utf8 -m src.pipeline run --stage all` rồi đọc `logs/*.jsonl` để lấy `elapsed_ms` của từng tầng.

## 4. Số đo tham chiếu (2026-11-09)

| Hạng mục | Số thật | Ngưỡng | Kết luận |
|---|---|---|---|
| ingest 1.550.922 dòng | 5,12 s | — | — |
| clean | 4,97 s | — | — |
| integrate | 3,46 s | — | — |
| linkage (806.705 cặp ứng viên) | 3,98 s | ≤ 60 s | đạt, biên rất rộng |
| analyze | 0,29 s | — | — |
| truy vấn đếm đơn (U1) | nằm trong ngưỡng test 2.000 ms | < 2 s | đạt |

## 5. Điều cần lưu ý khi đo lại

- Số đo phụ thuộc máy; ngưỡng là **trần**, không phải mục tiêu tối ưu.
- Lần bấm đầu của vùng `don-theo-thang` chịu thêm chi phí nạp CSV (~2,5 s theo ngân sách, 5 s là trần). Đừng so nó với ngưỡng 2 giây của các lần sau.
- Không đo trong lúc dashboard đang chạy song song với pipeline: cả hai cùng đọc `dataset/` và có thể tranh I/O.
