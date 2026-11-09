# External Dependency Map — Nâng cấp tích hợp dữ liệu Olist

Một **Bolt** là một lượt xây trọn vẹn trên một phần công việc, kết thúc bằng thứ chạy được. Tài liệu này liệt kê những gì nằm ngoài tầm kiểm soát của người thực hiện và có thể chặn một Bolt.

## Kết luận

**Không có phụ thuộc bên ngoài nào có thể chặn tiến độ.** Người đặt yêu cầu xác nhận mọi thứ nằm trong máy và trong repo. Dự án chạy localhost, không có dịch vụ ngoài, không có phê duyệt từ bên thứ ba.

## Những thứ trông giống phụ thuộc nhưng không phải

| Hạng mục | Vì sao không phải phụ thuộc ngoài | Bolt liên quan |
|---|---|---|
| `dataset/` chín tệp CSV | Đã có sẵn trong repo, bất biến | Tất cả |
| Cache IBGE cục bộ `dataset/external/ibge/` | Đã có sẵn; không cần gọi API | Bolt 3 |
| `warehouse/olist.duckdb` | Sinh ra khi chạy pipeline trên máy | Bolt 1, 4 |
| Dash Mantine Components | Cài bằng `pip` từ mạng một lần rồi ghim phiên bản | Bolt 6 |
| `ruff` | Cài bằng `pip` một lần rồi ghim phiên bản | Bolt 1 |

## Rủi ro mạng duy nhất

Hai gói cần cài từ mạng (`dash-mantine-components`, `ruff`). Nếu máy đang không có mạng tại thời điểm đó:

- `ruff` không cài được → tạm dùng kiểm tra tay, và ghi rõ trong biên bản Bolt; không thay bằng công cụ khác.
- `dash-mantine-components` không cài được → Bolt 6 bị chặn; các Bolt 1–5 vẫn làm được vì không phụ thuộc `dmc`.

## Bảng theo Bolt

| Bolt | Phụ thuộc ngoài | Chủ sở hữu | Nếu trượt |
|---|---|---|---|
| Bolt 1 | không | — | — |
| Bolt 2 | không | — | — |
| Bolt 3 | không | — | — |
| Bolt 4 | không | — | — |
| Bolt 5 | không | — | — |
| Bolt 6 | `dash-mantine-components` từ PyPI | người thực hiện | Hoãn Bolt 6, ghi rõ là chưa cài được; không đổi sang thư viện khác mà không hỏi |
