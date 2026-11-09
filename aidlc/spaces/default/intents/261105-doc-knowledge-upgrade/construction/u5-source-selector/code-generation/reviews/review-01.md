## Review

**Verdict:** READY
**Reviewer:** aidlc-architecture-reviewer-agent
**Date:** 2026-11-08T08:06:56Z
**Iteration:** 1
**Verdict Dictated:** no

### Findings

| ID | Severity | Location | Finding | Required action | Status |
|---|---|---|---|---|---|
| R-01 | Major | src/integration/selector.py > _checked_source_set | Hàm chỉ kiểm ba việc: tên nguồn thuộc tập kín ba tên, không trùng, và đúng một nguồn mô phỏng. Nó **không** kiểm bộ hồ sơ có đủ cả ba nguồn. W1 bước 2 của functional-spec đòi "kiểm tập nguồn đúng ba tên đã chốt" và BR5.2 nói bộ nguồn gồm đúng ba nguồn, nhưng một tệp cấu hình chỉ khai `olist_csv` + `partner_simulated` vẫn nạp thành công: nguồn thiếu biến mất khỏi C7 mà không có lỗi, trái FR4.2 ("bảng đầy đủ các nguồn ứng viên"). Bộ test không có ca "thiếu một nguồn", và bước smoke trong CI chỉ in `3 3` chứ không khẳng định, nên CI vẫn xanh với `2 3`. | Thêm phép kiểm đủ ba tên trong `_checked_source_set` (SchemaError nêu nguồn thiếu), thêm ca âm "cấu hình chỉ khai hai nguồn" vào `tests/unit/test_integration_selector.py`, và cho bước smoke của CI khẳng định giá trị `3 3` thay vì chỉ in. | New |
| R-02 | Major | aidlc/spaces/default/intents/261105-doc-knowledge-upgrade/inception/contract-design/contract-summary.md > C7 — errors | C7 chỉ khai `NoSourceAvailableError`, trong khi `load_source_catalogue` — đúng hàm mà U6 gọi để lấy C7 — ném `ConfigurationError` khi thiếu tệp cấu hình và `SchemaError` khi định danh sai (cả hai nhánh đã có test và đã ghi ở bề mặt lỗi của entities.md). C3 cũng thiếu `SchemaError` mà `select_source` ném khi `query_id` lạ. Consumer dựng theo hợp đồng sẽ để hai lớp lỗi này thoát ra ngoài ranh giới giao diện; quy tắc sở hữu hợp đồng chỉ áp quy ước "khai hai kiểu lỗi" cho C1/C2/C6 nên C7 không được che. | Thêm `SchemaError` và `ConfigurationError` vào mục `errors` của C7 (và `SchemaError` vào C3) trong `contract-summary.md`, kèm ghi chú consumer phải bắt cả ba lớp; giữ nguyên `NoSourceAvailableError`. | New |
| R-03 | Minor | src/integration/selector.py > _choice | `missing_fields` được gán cho mọi dòng bị loại, kể cả dòng bị loại vì `is_simulated` hoặc `has_data = false`; entities.md nói trường này "chỉ có khi nguồn bị loại vì thiếu trường". Với tệp cấu hình đang phát hành, dòng `partner_simulated` của cả ba truy vấn vừa mang lý do "nguồn mô phỏng, chỉ dùng để so sánh" vừa mang danh sách trường thiếu, nên U6 có thể hiển thị hai thông điệp mâu thuẫn trên cùng một dòng. | Chỉ gán `missing_fields` khi lý do loại là nhánh thiếu trường, hoặc sửa entities.md để nói rõ trường này luôn là phần thiếu đã tính; chọn một cách và thêm test khẳng định. | New |
| R-04 | Minor | src/integration/models.py > SourceCatalogue.query_fields | Payload trả `dict[str, tuple[str, ...]]` trong khi C7 khai `dict[str, list[str]]`. Consumer viết đúng theo hợp đồng có thể so sánh với list hoặc gọi `.append` và nhận kiểu sai; C2 đã có cùng kiểu lệch trước đây nên không ai sửa giúp. | Khai đúng kiểu `tuple` trong C7 cho `query_fields`, hoặc chuyển sang list ở biên trả payload; ghi lựa chọn vào contract để U6 không phải đoán. | New |
| R-05 | Minor | aidlc/spaces/default/intents/261105-doc-knowledge-upgrade/construction/u5-source-selector/code-generation/traceability.json > coverage NFR6.2 | Dòng NFR6.2 đánh `OK` với target `unit-test-instructions.md`. Tệp này không tồn tại ở gốc workspace (nó chỉ nằm trong thư mục record) và không phải tệp mã hay test, trái quy định mỗi target `OK` phải là một tệp triển khai hoặc test workspace-relative có thật. | Trỏ NFR6.2 tới một tệp mã/test có thật (ví dụ `tests/unit/test_integration_selector.py`), hoặc đổi sang `N/A` kèm lý do nếu chỉ tiêu này do quy trình chứ không do mã đơn vị bảo đảm. | New |
| R-06 | Minor | aidlc/spaces/default/intents/261105-doc-knowledge-upgrade/construction/u5-source-selector/functional-design/functional-spec.md > W2 bước 5 | Tài liệu khẳng định "khi U3 đổi tập trường của một truy vấn ... bộ test của U5 đỏ nếu lệch", nhưng không test nào của U5 đọc định nghĩa truy vấn của U3: ánh xạ `query_fields` là bản sao độc lập trong `config/integration-sources.yaml`. Hôm nay chưa lộ vì `olist_csv` phủ cả 11 trường, nhưng khi có nguồn thật thứ hai thì lệch sẽ chọn sai nguồn mà không cổng nào báo — tức biện pháp giảm thiểu được viện dẫn không tồn tại. | Thêm một phép đối chiếu tự động (test so tập trường của ba `query_id` với định nghĩa truy vấn của U3, hoặc một mục hợp đồng chung cho ánh xạ này), hoặc sửa câu trong functional-spec thành rủi ro chưa có cổng kèm người sở hữu. | New |

### Validation Tool Results

| Tool | Result | Interpretation |
|---|---|---|
| pytest tests/unit/test_integration_selector.py | PASS — 48 passed in 0.52s | Khớp đúng con số 48 ca trong code-summary; lệnh chạy của đơn vị chạy được, không cần dữ liệu thật. |
| pytest ... --cov=src.integration.selector --cov-fail-under=90 | PASS — 48 passed; selector.py 199 câu lệnh, 1 bỏ sót, 99,50% | Xác nhận con số 99,50% trong code-summary; câu lệnh không phủ là guard mô phỏng đã được ghi ở §3 của code-summary, không phải test hình thức. |
| pytest -m "not slow" | PASS — 268 passed, 7 deselected in 11.32s | Khớp lời khai "268 passed, 7 deselected"; U5 không gây hồi quy trên bộ nhanh. |
| pytest --cov=src --cov-fail-under=80 (lệnh xác nhận đã ghi của intent) | PASS — 275 passed; toàn bộ src/ 91,73%, ngưỡng 80% đạt | Chỉ tiêu NFR2.1 mà code-summary hoãn sang Build and Test nay đã đo được và xanh; không có phát hiện về độ phủ. |
| ruff check (5 tệp Python của đơn vị) | PASS — All checks passed | NFR3.1 nửa lint đạt. |
| ruff format --check (5 tệp) | PASS — 5 files already formatted | NFR3.1 nửa định dạng đạt; việc format `src/config.py` chỉ gộp khối nhiều dòng, đúng phạm vi tệp được sửa. |
| Smoke nạp config/integration-sources.yaml bằng C2 thật | PASS — in `3 3` | Tệp cấu hình đang phát hành nạp được thật, ba nguồn và ba ánh xạ truy vấn, như lời khai §2 của code-summary. |

### Summary

Đơn vị đã giao đúng C3 và C7 và mọi cổng đã chạy đều xanh (48 ca, 99,50% mô-đun; 275 ca toàn bộ, 91,73%); vòng phá chính tập trung vào bộ nạp cấu hình và hợp đồng chuyển giao. Hai phát hiện Major còn mở: bộ nạp không kiểm bộ hồ sơ có đủ ba nguồn (một nguồn có thể biến mất im lặng khỏi bảng), và C7 chưa khai hai lớp lỗi mà chính hàm nạp ném ra cho U6. Với 0 Critical và 2 Major, kết luận READY theo ngưỡng; nên sửa hai mục đó trước khi U6 dựng theo hợp đồng.
