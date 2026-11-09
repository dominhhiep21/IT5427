# Drift Report

Rà soát chỗ tài liệu và mã đã lệch nhau trong đợt, và chỗ còn lệch.

## 1. Đã phát hiện và đã sửa

| Drift | Phát hiện bởi | Cách sửa |
|---|---|---|
| C9 thiếu chỗ cho vùng kết quả, nên U6 dựng lại tab làm mất số liệu lát cắt | Reviewer kiến trúc (vòng 2 của U1) | thêm `result_region_ids` vào C9; tab dựng mọi vùng; thêm `STATE_PENDING` |
| C8 khai `fields: list[str]` trong khi tệp thật là danh sách bản ghi có `source_column`/`data_type`/`loaded` | Reviewer (vòng 2 của U1) | C8 chốt hình dạng bản ghi; U2 đọc đúng |
| U3 định **thay thế** `don-theo-thang` trong khi change-policy C9 chỉ cho thêm | Reviewer (vòng 1 của U3) | BR3.1 và TS-U3-4 đổi thành "cộng thêm ba vùng" |
| Tài liệu U4 mô tả đọc nguồn bằng `pd.read_csv(usecols=…)` trong khi mã dùng helper `read_csv` đủ cột | Kiểm toán mã (subagent) | TS-U4-4 viết lại theo mã |
| Tài liệu U4 nói tệp kết quả chỉ có `customer_id` + `is_correct`, thực tế có 11 khoá | Kiểm toán mã | SR-U4-6 liệt kê đủ 11 khoá, sửa `bool` → `bool \| None` |
| Nhiều chỗ khẳng định "3 tab, 2 callback, 9 output" sau khi hình dạng đã là 4/8 | Quét tài liệu (subagent) | sửa ~40 chỗ ở U2, U3, U5, U6 và ghi chú cấp stage |

## 2. Drift còn lại, đã biết

| Chỗ lệch | Vì sao để lại | Rủi ro |
|---|---|---|
| `bang_giao` khai `loaded: true` nhưng bộ nạp không đọc bảng customers | sửa nó đổi hành vi thực thể `don_hang` mà U3/U4 đang dùng | giá trị trường luôn `None`; ghi nợ `TD-16` |
| `team.md` nói phiên bản = commit hash, `cicd-pipeline.md` của U1 đề xuất tag + CHANGELOG | chưa ai chốt | `CHANGELOG.md` có nhưng không gắn tag |
| `AGGENTS.md` dòng 15 ghi "chưa cài pyspark, duckdb…" đã lỗi thời | ngoài phạm vi đợt | người mới đọc sẽ tưởng thiếu phụ thuộc |
| Bảng "Tóm tắt quy tắc" của vài đơn vị chưa phản ánh hết bước mới | mức thấp, không ảnh hưởng mã | người đọc phải mở tệp gốc |

## 3. Cách phòng drift lần sau

- **Một sự thật, một chỗ**: khi sửa hình dạng dashboard, sửa test + tài liệu + `AGENTS.md` trong cùng thay đổi (luật `project.md`).
- **Test khoá hợp đồng**: ba test mới của đợt (C1 khớp ánh xạ, C7 trường↔bảng, C9 id lạ) đều là loại khoá này.
- **Kiểm toán định kỳ bằng subagent**: quét tài liệu vs mã rẻ hơn nhiều so với để reviewer phát hiện từng cái.
