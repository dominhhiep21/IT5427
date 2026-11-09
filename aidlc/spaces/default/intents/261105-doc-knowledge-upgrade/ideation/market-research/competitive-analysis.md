# Competitive Analysis — Nâng cấp tích hợp dữ liệu Olist

Bối cảnh lấy từ `ideation/intent-capture/intent-statement.md`: sản phẩm là một pipeline + dashboard Olist đang chạy, cần nâng cấp để thể hiện bốn nhóm kiến thức tích hợp dữ liệu trong `doc/`, phục vụ giảng viên/hội đồng chấm đồ án.

Phạm vi đối chiếu: cả hai nhóm công cụ — mã nguồn mở và thương mại — theo câu trả lời Q1. Ràng buộc sử dụng thật: chỉ công cụ/thư viện mã nguồn mở, miễn phí (Q4).

> Ghi chú bằng chứng: các nhận định dưới đây là kiến thức chung về định vị sản phẩm, chưa kiểm chứng lại trong phiên này. Giá, phiên bản và chi tiết tính năng cần kiểm chứng trước khi dùng trong tài liệu nộp. Chúng được ghi ở mức năng lực, không nêu số liệu cụ thể.

## Nhóm mã nguồn mở

| Công cụ | Năng lực chính | Liên quan tới nhóm chủ đề nào |
|---|---|---|
| dbt | Biến đổi SQL có kiểm soát phiên bản, mô hình hoá theo lớp; bản Cloud có semantic layer | Đồng nhất lược đồ ở mức biến đổi; semantic layer |
| Airbyte | Thu thập dữ liệu từ nhiều nguồn qua connector | Chọn nguồn dữ liệu, phần ingestion |
| Trino / Presto | Truy vấn phân tán trên nhiều nguồn dữ liệu khác nhau qua connector | Lược đồ trung gian, xử lý truy vấn, chọn nguồn |
| Splink / Zingg | Ghép bản ghi xác suất (probabilistic record linkage), blocking, so khớp | Ghép bản ghi / nhận dạng thực thể |
| DuckDB | Xử lý phân tích tại chỗ trên Parquet/CSV, SQL đầy đủ | Nền tảng lưu trữ và truy vấn tại chỗ |
| Great Expectations | Kiểm tra chất lượng dữ liệu theo bộ luật khai báo | Gián tiếp: chất lượng dữ liệu sau tích hợp |

## Nhóm thương mại

| Sản phẩm | Năng lực chính | Liên quan tới nhóm chủ đề nào |
|---|---|---|
| Denodo | Tích hợp dữ liệu ảo (virtual integration), lớp lược đồ trung gian, tối ưu truy vấn | Gần nhất với toàn bộ bốn nhóm |
| Informatica / Talend | Tích hợp, làm sạch, quản trị dữ liệu theo lô | Đồng nhất lược đồ, chất lượng dữ liệu |
| Fivetran | Sao chép dữ liệu từ nguồn vào kho | Chọn nguồn, ingestion |
| Ataccama và tương tự | Làm sạch, ghép bản ghi, quản trị chất lượng dữ liệu | Ghép bản ghi |

Giá và mô hình cấp phép của nhóm thương mại không được nêu ở đây vì chưa kiểm chứng; theo Q4 nhóm này chỉ xuất hiện để so sánh, không dùng trong sản phẩm.

## So sánh theo bốn nhóm chủ đề

| Nhóm chủ đề | Công cụ có sẵn | Hệ Olist hiện tại | Khoảng trống lần nâng cấp lấp |
|---|---|---|---|
| Đồng nhất lược đồ / lược đồ trung gian | Trino, Denodo, dbt (mức biến đổi) | Ghép theo khoá cứng trong `src/integrate`, không có lược đồ trung gian khai báo | Cần một lược đồ trung gian tường minh và ánh xạ từ nguồn |
| Ghép bản ghi / nhận dạng thực thể | Splink, Zingg, Ataccama | Dùng `customer_unique_id` có sẵn; không có blocking/so khớp | Cần blocking + độ tương đồng + ngưỡng, hiển thị được cặp khớp |
| Xử lý / viết lại truy vấn | Trino (tối ưu), Denodo (rewrite) | Truy vấn SQL viết tay trong `src/analytics` | Cần viết lại truy vấn từ lược đồ trung gian xuống nguồn |
| Chọn nguồn dữ liệu | Airbyte, Trino connector, Fivetran | Chọn nguồn cố định trong cấu hình pipeline | Cần luật chọn nguồn theo khả năng truy cập/chi phí |

## Điểm khác biệt của lần nâng cấp

- Công cụ có sẵn che thuật toán sau giao diện cấu hình; sản phẩm này phải *phơi ra* ánh xạ, cặp bản ghi khớp và kế hoạch truy vấn để người chấm thấy lý thuyết đang chạy.
- Quy mô nhỏ (9 CSV Olist, một máy) nên không cần hạ tầng phân tán; giá trị nằm ở tính minh bạch, không ở hiệu năng.
- Ràng buộc mã nguồn mở, miễn phí (Q4) loại nhóm thương mại khỏi phần triển khai, nhưng vẫn giữ chúng làm mốc so sánh (Q1).

## Rủi ro cạnh tranh

- Nếu chỉ dùng thư viện có sẵn cho phần lõi, bài nộp khó chứng minh hiểu lý thuyết; đây là lý do Q2 chọn tự xây phần lõi.
- Trino/Denodo đã làm rất tốt phần mediation; phần tự xây phải giới hạn ở mức đủ để minh hoạ, không cố đạt tính năng của sản phẩm thương mại.
