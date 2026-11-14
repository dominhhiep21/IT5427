## Review

**Verdict:** READY
**Reviewer:** aidlc-architecture-reviewer-agent
**Date:** 2026-11-12T09:57:23Z
**Iteration:** 1
**Verdict Dictated:** no

### Findings

| ID | Severity | Location | Finding | Required action | Status |
|---|---|---|---|---|---|
| R-01 | Minor | aidlc/spaces/default/intents/261111-model-feature-improvemen/construction/u1-mart-and-baseline/code-generation/code-summary.md > mục "TDD — bằng chứng đỏ trước xanh", câu ngay sau bảng | Câu này ghi bộ nhanh là **543 passed** trong khi mục "Kiểm tra đã chạy" của cùng tệp ghi **545 passed**; lần chạy lại của pass này cho **545 passed, 14 deselected** | Sửa 543 thành 545 để hai chỗ trong cùng tệp khớp nhau và khớp lần chạy thật | New |
| R-02 | Minor | aidlc/spaces/default/intents/261111-model-feature-improvemen/construction/u1-mart-and-baseline/code-generation/code-summary.md > bảng "TDD — bằng chứng đỏ trước xanh", dòng "Logic nghiệp vụ" | Dòng này ghi **7 failed**, nhưng `tests/unit/test_analytics_baseline.py` hiện có **8** test và cả 8 đều gọi `measure_state_baseline`, nên một lần chạy đỏ trên tệp 8 test không thể ra 7 failed; bản ghi không nói test thứ 8 được thêm sau bước Red | Ghi rõ `test_extra_numeric_column_does_not_change_the_result` được thêm ở bước Refactor, hoặc ghi lại kết quả đỏ thật của lần chạy 8 test | New |
| R-03 | Minor | aidlc/spaces/default/intents/261111-model-feature-improvemen/construction/u1-mart-and-baseline/code-generation/code-generation-plan.md > bảng "Ánh xạ truyện → bước", dòng `NFR4.1` | Dòng này trỏ tới bước **19**, nhưng kế hoạch chỉ có 15 bước; `NFR4.1` thực tế được canh ở bước 13 (test `slow`) | Trỏ dòng này tới bước 13 thay vì một bước 19 không tồn tại | New |
| R-04 | Minor | aidlc/spaces/default/intents/261111-model-feature-improvemen/construction/u1-mart-and-baseline/code-generation/code-generation-plan.md > Step 11 | Bước 11 được tick `[x]` với nội dung "tách phần mã hoá one-hot thành hàm nội bộ để test đọc được ma trận", nhưng `measure_state_baseline` vẫn gọi thẳng `pd.get_dummies` + `reindex` và không có hàm nội bộ nào; không test nào đọc ma trận — test hiện so hai giá trị AUC | Sửa câu chữ bước 11 cho đúng việc đã làm, hoặc tách hàm nếu muốn giữ nguyên mô tả | New |
| R-05 | Minor | tests/integration/test_u1_mart_columns_end_to_end.py > các dòng 16, 26, 42 | Ba chỗ dùng `# noqa: ANN001` trong khi `ruff.toml` chỉ `select = ["E4", "E7", "E9", "F"]`, nên mã đó không bao giờ được dùng; đây là ba `# noqa` duy nhất trong `tests/`, tức mở rộng đúng thứ nhiễu mà `team.md` đã ghi là không phải tiền lệ | Bỏ ba `# noqa: ANN001` | New |
| R-06 | Minor | tests/unit/test_ci_config.py > hằng `NEW_FILES` | Danh sách vẫn canh 14 tệp của đợt trước, không có bốn tệp mới của U1; bốn đường dẫn U1 vừa thêm vào `.github/workflows/ci.yml` không được test nào canh — xoá chúng khỏi danh sách format sẽ không làm test nào đỏ | Thêm bốn tệp mới của U1 vào `NEW_FILES` | New |
| R-07 | Minor | aidlc/spaces/default/intents/261111-model-feature-improvemen/construction/u1-mart-and-baseline/code-generation/code-summary.md > mục "Kiểm tra đã chạy", dòng test `slow` | Dòng này khẳng định `2 passed` trên `dataset/` thật; pass này không chạy lại được lệnh đó (lý do: nó dựng lại `data/marts/` và `warehouse/olist.duckdb` đang dùng chung), nên đây là phần duy nhất của bản ghi chưa được kiểm lại | Không cần làm gì nếu lần chạy đó đã xảy ra; nếu chưa, ghi kèm ngày và lệnh đã chạy ngay tại dòng đó | New |

### Validation Tool Results

| Tool | Result | Interpretation |
|---|---|---|
| `.venv\Scripts\python.exe -X utf8 -m pytest tests/unit/test_integrate_facts_columns.py tests/unit/test_integrate_seller_state.py tests/unit/test_analytics_baseline.py -q` | `20 passed in 2.96s` | Khớp đúng 7 + 5 + 8 = 20 test của `unit-test-instructions.md` và của `code-summary.md`. `python` ngoài `.venv` không có pytest nên phải dùng `.venv` |
| `.venv\Scripts\python.exe -X utf8 -m ruff check .` | `All checks passed!` | Lint sạch, không có `F401`/`E4`/`E7`/`E9` mới |
| `.venv\Scripts\python.exe -X utf8 -m pytest -m "not slow" -q` | `545 passed, 14 deselected in 33.00s` | Không hồi quy; khớp con số 545 ở mục "Kiểm tra đã chạy", không khớp 543 ở mục TDD |
| `.venv\Scripts\python.exe -X utf8 -m ruff format --check` trên 6 tệp của U1 | `6 files already formatted` | Định dạng sạch trên cả `facts.py` dù tệp này không nằm trong danh sách format của `ci.yml` |
| `git diff -- src/integrate/facts.py` | Chỉ thêm ba cột, hai chú thích, và reflow của `ruff format` | Xác nhận "no regression": phép nối vẫn `rename` ngay tại chỗ nối rồi `how="left"`, không thêm/bớt phép lọc dòng nào, thứ tự cột cũ giữ nguyên (ba cột mới thêm ở cuối) |
| `git diff -- .github/workflows/ci.yml` | Phần U1 thêm chỉ là bốn đường dẫn tệp test trong dòng `ruff format --check` | Không đổi ngưỡng phủ, không đổi danh sách nhánh, không thêm bước CI |
| `pytest -m slow tests/integration/test_u1_mart_columns_end_to_end.py` | Không chạy lại trong pass này | Lệnh dựng lại `data/marts/` và `warehouse/olist.duckdb` trên cây đang dùng chung; xem finding Minor cuối. Ba `ModelError` của `measure_state_baseline` (`cut_date` khác `SPLIT_DATE`, thiếu cột, tập kiểm tra rỗng/một lớp) và chữ ký `-> float` khớp C1 đã kiểm bằng cách đọc mã, không cần lần chạy đó |

### Summary

Không có phát hiện Critical hay Major: ba cột vào mart đúng cách (rename tại chỗ nối, `left` join, không lọc dòng), `measure_state_baseline` khớp chữ ký và ba nhánh lỗi mà C1 đòi, test 20/20 xanh, bộ nhanh 545 xanh, ruff sạch, và `ci.yml` chỉ nhận thêm đường dẫn test. Các phát hiện còn lại đều là Minor về tính chính xác của bản ghi (một con số 543 lệch với lần chạy thật, bằng chứng đỏ không khớp số test cuối, một bước kế hoạch trỏ tới số bước không tồn tại, một bước mô tả refactor không có trong mã) và hai điểm vệ sinh nhỏ (`# noqa` không cần, danh sách canh `ci.yml` chưa phủ tệp mới) — không cái nào chặn người thi công.
