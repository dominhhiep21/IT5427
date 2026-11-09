# Scope Document — Nâng cấp tích hợp dữ liệu Olist

Bối cảnh: `ideation/intent-capture/intent-statement.md`, `ideation/feasibility/feasibility-assessment.md`, `ideation/feasibility/constraint-register.md`.

## Trong phạm vi

| Nhóm | Mức độ | Nội dung |
|---|---|---|
| Đồng nhất lược đồ / lược đồ trung gian | Sâu | Lược đồ trung gian khai báo cho thực thể chính (đơn, mặt hàng, khách, người bán, sản phẩm, thanh toán, đánh giá, địa lý) và ánh xạ từ 9 CSV + cache IBGE |
| Xử lý và viết lại truy vấn | Sâu | Viết lại một tập truy vấn mẫu từ lược đồ trung gian xuống SQL trên nguồn, có hiển thị kế hoạch viết lại |
| Ghép bản ghi / nhận dạng thực thể | Tối thiểu | Một kịch bản: blocking theo khoá, tính điểm tương đồng, ngưỡng, báo cáo cặp khớp |
| Chọn nguồn dữ liệu | Tối thiểu | Luật chọn nguồn theo khả năng truy cập và chi phí ước tính, chạy trên hai nguồn hiện có |
| Giao diện | Trung bình | Một tab mới "Tích hợp" gộp bốn nhóm; hiển thị ánh xạ, cặp khớp, kế hoạch truy vấn |
| Lớp ngữ nghĩa | Trung bình | Định nghĩa KPI dùng chung để dashboard và lớp truy vấn không lệch số |
| Không hồi quy | Bắt buộc | Giữ KPI baseline và toàn bộ test hiện có xanh |

## Ngoài phạm vi

| Nội dung | Lý do |
|---|---|
| Thêm nguồn dữ liệu ngoài Olist + cache IBGE | Biên giới ở `intent-statement.md` |
| ML dự báo giao trễ | Chưa cần để thể hiện bốn nhóm chủ đề |
| Đổi công nghệ lớn (Spark, Kafka, Docker, cloud) | Ràng buộc TC-02, TC-04 |
| Đăng nhập / phân quyền nhiều người dùng | Không có yêu cầu bảo mật (RC-01) |
| Dùng công cụ thương mại trong sản phẩm | Ràng buộc BC-01 |
| Tối ưu truy vấn tổng quát như một CSDL thực thụ | Vượt mức "đủ thể hiện lý thuyết" (R-02) |

## Ranh giới mức độ

- Hai nhóm cốt lõi (lược đồ trung gian, viết lại truy vấn) làm sâu: có thuật toán tự viết, có kiểm thử, có hiển thị trên giao diện.
- Hai nhóm còn lại làm ở mức một kịch bản chạy được trên dữ liệu thật; không mở rộng thêm biến thể nếu chưa xong hai nhóm cốt lõi.
- Mọi nhóm đều phải chạy được bằng một lệnh trên máy local, không cần mạng.

## Thứ tự thi công

Theo phụ thuộc (Q3 = A):

1. Lược đồ trung gian và ánh xạ — nền cho tất cả.
2. Mô tả nguồn và luật chọn nguồn — dựa trên mô tả nguồn trong lược đồ.
3. Viết lại truy vấn — dựa trên lược đồ và mô tả nguồn.
4. Ghép bản ghi — dựa trên thực thể khách/người bán trong lược đồ.
5. Lớp ngữ nghĩa — gom các KPI đã có về một định nghĩa.
6. Tab "Tích hợp" — làm sau khi bốn nhóm có dữ liệu trả về.
7. Làm mới ba tab hiện có — làm cuối, khi số liệu đã ổn định.

## Bản đồ chuỗi giá trị

```
Nguồn (9 CSV + cache IBGE)
   -> Mô tả nguồn, ánh xạ vào lược đồ trung gian
   -> Truy vấn trên lược đồ trung gian (viết lại xuống nguồn)
   -> Kết quả đã hợp nhất + lớp ngữ nghĩa KPI
   -> Tab "Tích hợp" và ba tab báo cáo hiện có
   -> Người xem: giảng viên/hội đồng kiểm chứng lý thuyết trên dữ liệu thật
```

<!-- Text fallback: dữ liệu đi từ nguồn CSV và cache IBGE, qua mô tả nguồn và ánh xạ lược đồ trung gian, qua lớp viết lại truy vấn, tới kết quả hợp nhất và lớp ngữ nghĩa, rồi hiển thị trên dashboard. -->

## Ràng buộc áp dụng

- Thời gian 1–2 tuần (OC-01): mỗi nhóm chỉ một kịch bản, trừ hai nhóm cốt lõi.
- Chỉ thư viện mã nguồn mở nhỏ (TC-03), chạy local (TC-04).
- `dataset/` bất biến (TC-05).
- Không hồi quy KPI và test (TC-06).
