# Security Design — u6-integration-ui

Nguồn: `nfr-requirements/security-requirements.md` (SR-U6-1..9), `nfr-requirements/tech-stack-decisions.md` (TS-U6-1..7), `functional-design/functional-spec.md` (W1–W7, BR6.1–BR6.12), `inception/contract-design/contract-summary.md` (C3–C9).

Là tầng hiển thị, đơn vị này không giữ bí mật và không quyết định số liệu. Ba rủi ro thật của nó là: **làm hỏng ba tab cũ**, **làm sập cả tab vì một hợp đồng lỗi**, và **để lộ thông điệp nội bộ ra màn hình**.

## ADR-U6-S1 — Tab mới đọc hợp đồng bên trong callback, không đọc lúc dựng layout

**Bối cảnh.** `app.layout` dựng toàn bộ bốn tab cùng lúc. Nếu tab mới đọc C5/C6/C7 ngay trong `build_layout`, một tệp kết quả thiếu hoặc một hợp đồng lỗi sẽ làm cả bốn tab không dựng được — đúng điều SR-U6-8 cấm.

**Quyết định.** `build_layout` chỉ dựng khung: bốn thẻ với trạng thái `rong`, vùng kết quả và bốn màn hình chi tiết rỗng. Dữ liệu được đọc trong **sáu** callback: `load_overview` (kích hoạt ngay khi tab được mở, đọc C5/C6/C7 để điền hai dòng số liệu và trạng thái của bốn thẻ), `route`, `run_query`, `suggest_source`, `reload`, và callback của vùng kết quả. Việc đọc nằm trong callback, không nằm trong `build_layout`, nên vẫn giữ được mục đích của quyết định: một hợp đồng lỗi chỉ làm hỏng thẻ/màn hình của nó.

**Hệ quả.** Ba tab cũ không bao giờ bị ảnh hưởng bởi lỗi của tab mới; tab mới mở được ngay cả khi chưa chạy `--stage all`, và mỗi màn hình tự hiện trạng thái rỗng kèm hướng dẫn.

**Phương án đã loại.** *Đọc hết lúc dựng layout*: đơn giản hơn nhưng biến một tệp thiếu thành sự cố toàn dashboard.

## ADR-U6-S2 — Bốn thẻ thay hẳn ba khối kết quả cũ, kèm cập nhật cấu hình tab

**Bối cảnh.** `config/integration-tab.yaml` đang có cả `card_ids` và `result_block_ids` (ba mã truy vấn của lát cắt mỏng); đơn vị này bỏ `result_block_ids`, **giữ `card_ids` và `result_region_ids`** — và `load_tab_config` bắt buộc hai khoá đó.

**Quyết định.** `TabConfig` giữ `card_ids` (bốn giá trị theo C9) và `result_region_ids`; `load_tab_config` bắt buộc `card_ids` và `result_region_ids`, bỏ `result_block_ids`; tệp cấu hình, `card.py`, `app.py` và năm test của `test_integration_card.py` sửa trong cùng thay đổi.

**Hệ quả.** Chỉ một nguồn sự thật cho danh sách thẻ. Đổi là thay đổi có chủ đích, có test.

**Phương án đã loại.** *Giữ cả hai khoá*: hai nguồn sự thật, dễ lệch.

## ADR-U6-S3 — Dùng lại bộ token `data-state` hiện có

**Bối cảnh.** `src/integration/card.py` đang xuất `rong`, `dang-tai`, `day-du`, `mot-phan`, `loi`; các test đọc `data-state` theo đúng bộ đó.

**Quyết định.** `StateBlock` dùng đúng năm token này; tên tiếng Anh trong tài liệu chỉ là nhãn đọc. Không thêm token mới.

**Hệ quả.** Test cũ không phải viết lại vì tên trạng thái; chỉ số thẻ và số callback đổi.

## ADR-U6-S4 — Mọi chuỗi từ hợp đồng là text, không phải HTML

**Bối cảnh.** Lý do chọn nguồn, câu `coverage`, tên danh mục đều là chuỗi do hệ thống sinh, nhưng vẫn đi qua giao diện.

**Quyết định.** Không dùng `dangerously_allow_html`. Mọi chuỗi đi qua `html.Td(str(...))` hoặc `dmc.Text`. Thông điệp lỗi là câu tiếng Việt tự dựng, không chép nguyên văn ngoại lệ.

**Hệ quả.** Không có đường chèn HTML; thông điệp lỗi không lộ đường dẫn nội bộ hay traceback.

## ADR-U6-S5 — Sáu callback riêng, không đụng callback của ba tab cũ

**Quyết định.** Tab mới có **sáu** `callback_id` riêng: `load_overview`, `route`, `run_query`, `suggest_source`, `reload`, và callback của vùng kết quả (`don-theo-thang`). Tổng dashboard: **8** callback (2 cũ + 6 mới).

**Hệ quả.** Mỗi callback một việc; test hình dạng dashboard khẳng định đúng 8. `load_overview` là callback duy nhất chạy khi mở tab, nên W1 bước 3–6 thực hiện được mà không phải đọc dữ liệu trong `build_layout`.

## Bảng truy vết quyết định → yêu cầu

| Quyết định | Yêu cầu bảo mật | Chỉ tiêu |
|---|---|---|
| ADR-U6-S1 | SR-U6-8, SR-U6-4 | NFR1.4 |
| ADR-U6-S2 | SR-U6-8 | NFR5.1 |
| ADR-U6-S3 | SR-U6-8 | NFR5.1 |
| ADR-U6-S4 | SR-U6-5, SR-U6-4 | NFR4.1 |
| ADR-U6-S5 | SR-U6-8 | NFR1.1 |

## Không áp dụng

Xác thực/phân quyền (OS5), mã hoá đường truyền (không có mạng), tuân thủ PII (không hiển thị PII — SR-U6-7).
