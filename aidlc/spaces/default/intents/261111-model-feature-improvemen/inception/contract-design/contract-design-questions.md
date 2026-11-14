# Câu hỏi — Contract Design

Hai ranh giới cần đóng thành hợp đồng: `U1 → U2` (trong cùng tiến trình) và `U2 → U3` (hai tệp trên đĩa). Ba câu hỏi dưới đây là chỗ thiết kế chưa tự quyết; phần còn lại (không retry, không timeout, không versioning động) là hệ quả của cơ chế, không phải lựa chọn.

## Q1. `U2 → U3` là một hợp đồng hay hai?

- A. **Tệp `analysis.json` là hợp đồng chính thức** (có schema, có phiên bản); tệp mô hình là **artefact kèm theo** — `pickle` không có schema, chỉ có JSON mô tả đặc trưng và phiên bản thư viện
- B. Định nghĩa schema YAML cho **cả hai** tệp và coi cả hai là hợp đồng ngang hàng
- C. Gộp metadata mô hình vào `analysis.json` để chỉ còn **một** tệp hợp đồng
- X. Khác (vui lòng nêu rõ)

[Answer]: A

## Q2. Chính sách phiên bản và thay đổi phá vỡ

- A. **Chỉ U2 (người ghi) được đổi schema**; U3 đọc theo `version`; phiên bản khác → trạng thái `loi` có thông điệp, **không** ném (đúng ADR-002)
- B. Cho consumer đọc mềm: thiếu trường thì dùng mặc định, trường lạ thì bỏ qua
- C. Không cần chính sách — một người làm cả hai đơn vị
- X. Khác (vui lòng nêu rõ)

[Answer]: A

## Q3. `U1 → U2` có cần spec YAML không?

- A. **Có**: một khối `shared-schema` cho ba cột mart mới, `CohortCounts`, và chữ ký hàm đo baseline
- B. Không: chỉ prose, vì cùng tiến trình và cùng ngôn ngữ
- C. Chỉ chữ ký hàm, không schema cột (mart đã có `StarSchemaValidator` canh)
- X. Khác (vui lòng nêu rõ)

[Answer]: A

## Consolidated Summary Confirmation

Ba câu đã trả lời, và bộ hợp đồng mà chúng tạo ra:

- **`U2 → U3` là một hợp đồng, không phải hai** [Q1 = A]: `analysis.json` là hợp đồng **chính thức** — có schema YAML, có `version`, có luật thay đổi. Tệp mô hình ở `data/models/` là **artefact kèm theo**: `pickle` không có schema và không phải định dạng trao đổi giữa các máy, nên nó chỉ được mô tả bằng JSON metadata (danh sách đặc trưng + phiên bản thư viện), không được hứa như một hợp đồng ngang hàng.
- **Chỉ người ghi đổi schema** [Q2 = A]: U2 sở hữu schema `analysis.json`; U3 đọc theo `version`; phiên bản khác → trạng thái `loi` có thông điệp và **không** ném (ADR-002). Không có "đọc mềm" — vì nó xoá mất khả năng phân biệt "tệp cũ" với "tệp thiếu trường", đúng lý do đã loại phương án đó ở Domain Design.
- **`U1 → U2` có spec** [Q3 = A]: một khối `shared-schema` YAML cho ba cột mart mới, `CohortCounts`, và chữ ký hàm đo baseline. Mart vẫn có `StarSchemaValidator` canh số dòng, nhưng hợp đồng cột và chữ ký hàm phải viết ra vì U2 là người dùng đầu tiên của cả hai.
- **Hai hợp đồng, hai cơ chế**: `U1 → U2` là **gọi hàm trong cùng tiến trình** (shared schema + chữ ký); `U2 → U3` là **hai tệp trên đĩa** (JSON có schema + artefact `pickle`). Không có REST, không có event, không có mạng — nên **không** có timeout, retry, idempotency key hay versioning động; chỉ có kiểm phiên bản và trạng thái lỗi có kiểu.
- **Chủ hợp đồng**: U1 sở hữu schema mart + `CohortCounts` + chữ ký hàm; U2 sở hữu schema `analysis.json` và metadata mô hình; U3 chỉ là người đọc, không được đổi schema.

- Looks correct
- Request changes

[Answer]: Looks correct
