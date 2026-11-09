# Build and Test Summary

## 1. Kết luận

**Đạt.** Toàn bộ cổng của đợt xanh trên dữ liệu thật: 384 test (375 nhanh + 9 chậm), phủ **90,69%** so với ngưỡng 80%, `ruff` sạch, pipeline 6/6 tầng thành công, và cổng đúng đắn dữ liệu của lát cắt khớp **0 sai lệch** với phép tính độc lập.

## 2. Sáu đơn vị

| Đơn vị | Cổng nghiệm thu | Bằng chứng |
|---|---|---|
| u1-thin-slice | duyệt (skeleton + unit) | vùng `don-theo-thang` trong tab, 4 tab / 8 callback / 4 thẻ + 1 vùng |
| u2-mediated-schema | duyệt | đọc đúng C8: 3 thực thể, `don_hang` 7 trường, mọi trường `loaded: true` |
| u3-query-rewriter | duyệt | C3 được tiêu thụ thật; ánh xạ truy vấn→trường có test khoá |
| u4-record-linkage | duyệt | 806.705 cặp ứng viên trong 3,98 s; tệp kết quả không lộ khoá mốc |
| u5-source-selector | duyệt | C7 khai đủ bảng cho mọi trường phủ |
| u6-integration-ui | duyệt | dựng mọi `result_region_ids`; id lạ là lỗi cấu hình |

## 3. Cổng chất lượng

| Cổng | Kết quả | Ngưỡng |
|---|---|---|
| Bộ nhanh | 375 passed, 13,94 s | xanh |
| Bộ chậm | 9 passed, 52,26 s | xanh |
| Phủ dòng `src/` | **90,69%** | ≥ 80% |
| `ruff check .` | 0 vi phạm | 0 |
| `ruff format --check` | 28 tệp đúng định dạng | 0 tệp lệch |
| Pipeline `--stage all` | 6/6 tầng, `success=True` | xanh |
| Cổng đối chiếu lát cắt | 0 sai lệch | 0 |

## 4. Nợ kỹ thuật đã ghi nhận, không chặn

| Mã | Nội dung | Vì sao để lại |
|---|---|---|
| TD-09 | Bộ "nhanh" chưa hermetic: 5 test dashboard cần `warehouse/` và `data/marts/` | Sửa nó đổi 5 test ngoài phạm vi đợt; CI chạy pipeline trước để bù |
| TD-16 | `bang_giao` khai `loaded: true` nhưng bộ nạp chỉ đọc bảng khoá, nên giá trị luôn `None` | Sửa nó đổi hành vi thực thể `don_hang` mà U3/U4 đang dùng — cần một đợt riêng |
| — | `agg_sales_daily`, `agg_delivery_daily` chưa có baseline số dòng | Test hiện chỉ khẳng định 11 view tồn tại + số dòng 9 bảng mart |
| — | Không có test tự động cho tương phản màu và thứ tự tiêu điểm | Kiểm tay; cần công cụ đo tương phản để tự động hoá |
| — | Không có test tích hợp C5 thật (U4 → tab) và C9 nhiều vùng | Ghi ở `integration-test-instructions.md` §3 |

## 5. Việc chưa làm được trong đợt này

- **Kiểm bằng mắt trên trình duyệt** (bước 3 trong chuỗi xác nhận của `team.md`) chưa chạy trong phiên này: cần người mở `python -X utf8 -m src.dashboard` và bấm "Chạy truy vấn" ở vùng `don-theo-thang`.
- **Không có môi trường thứ hai**: "phát hành" = chạy từ mã nguồn trên máy local.

## 6. Đường đi tiếp

Stage kế tiếp theo workflow là `CI Pipeline`, rồi `Deployment Pipeline`, `Deployment Execution` và bốn stage `Operation` còn lại. Trước khi làm, cần người chốt: đợt này có cần dựng môi trường triển khai thật hay dừng ở mức chạy local (hiện `team.md` ghi "chưa có môi trường triển khai").
