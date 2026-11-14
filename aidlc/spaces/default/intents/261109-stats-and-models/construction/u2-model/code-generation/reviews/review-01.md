## Review

**Verdict:** READY
**Reviewer:** aidlc-architecture-reviewer-agent
**Date:** 2026-11-11T03:14:39Z
**Iteration:** 1
**Verdict Dictated:** no

### Findings

| ID | Severity | Location | Finding | Required action | Status |
|---|---|---|---|---|---|
| R-01 | Major | tests/integration/test_u2_model_end_to_end.py > dòng 86, khẳng định `0 <= block.auc <= 1` (cùng tests/unit/test_analytics_model.py > dòng 511) | Không có khẳng định nào về chất lượng mô hình, nên một mô hình không học được gì vẫn qua mọi cổng. Tôi chạy lại đúng đường mã trên mart thật: `train_n 64322`, `test_n 32156`, `late_test 1936`, `full_model_auc 0.5133` — tái lập chính xác `0.5133` trong `data/reports/analysis.json`, tức con số được ghi là trung thực. Nhưng cùng tập kiểm tra đó, nếu chỉ dùng `customer_state` (một cột đã nằm trong danh sách 11) thì AUC là `0.5333`, cao hơn mô hình 11 cột; FR2.3 đặt mốc "đạt tối thiểu 0,70" và TS-3 biện luận chọn hồi quy logistic đúng vì "mục tiêu chỉ là AUC ≥ 0,70". Artifact chỉ ghi cơ chế `auc_below_target`, không nơi nào (code-summary, README, CHANGELOG) nói rõ mốc 0,70 của FR2.3 đang không đạt và mô hình đang kém hơn baseline một đặc trưng, nên đơn vị được trình như đã xong trong khi năng lực dự báo gần như không có. | Thêm một phép so sánh mức sàn (ví dụ AUC phải cao hơn baseline `customer_state`-đơn hoặc một ngưỡng tối thiểu) mà chỉ ghi log và vào khối `counts`/log sự kiện, **không** làm hỏng BR2.6 "vẫn ghi"; đồng thời ghi rõ trong code-summary và README con số `0.5133` so với mốc 0,70 của FR2.3 kèm kết quả so baseline, để người làm quyết định có phải mở lại danh sách đặc trưng hay không. | New |
| R-02 | Minor | aidlc/spaces/default/intents/261109-stats-and-models/construction/u2-model/code-generation/traceability.json > mục `BR2.6`, trường `evidence` | Traceability khẳng định cờ `auc_below_target` "đúng khi và chỉ khi AUC dưới 0,70", trong khi `src/analytics/model.py` (dòng 275-282) so sánh trên AUC **đã làm tròn 4 chữ số**; sai lệch đã được khai ở code-summary nhưng văn bản traceability (và `rules.md` BR2.6) vẫn phát biểu dạng chưa làm tròn, nên hai artifact nói hai điều khác nhau ở dải biên 0,6950–0,6999. | Sửa câu chữ trong traceability (và nếu được, ghi chú ở `rules.md`) rằng phép so sánh dùng đúng giá trị đã ghi vào tệp, hoặc tính cờ trên AUC thô rồi mới làm tròn khi ghi — chọn một và nói rõ ở cả hai nơi. | New |
| R-03 | Minor | aidlc/spaces/default/intents/261109-stats-and-models/construction/u2-model/code-generation/traceability.json > `upstream_ids` và `coverage` | Traceability chỉ phủ BR2.1–BR2.9, bỏ sót TS-6, TS-8, TS-9 và NFR1.1, NFR1.3 mà `unit-test-instructions.md` liệt kê thành hàng bắt buộc có ca kiểm; các ca đó có thật trong test nhưng không xuất hiện trong bản trace, nên bản trace không chứng minh được phần kiểm soát công nghệ mà kế hoạch cam kết. | Thêm các mục TS-6, TS-8, TS-9, NFR1.1, NFR1.3 vào `coverage` (kèm đích và bằng chứng test tương ứng). | New |
| R-04 | Minor | src/analytics/model.py > `build_model_block`, dòng 274-284 | `not_flagged` được suy ra bằng `total - flagged` và `total` lấy từ `split["test_n"]`, nên `validate_counts` (BR2.7) không thể phát hiện lệch trên đường sản xuất, và nó chấp nhận cả số vô lý: `flagged` lớn hơn `total` sẽ cho `not_flagged` âm mà vẫn thoả `flagged + not_flagged = total`, rồi được ghi thẳng vào báo cáo. | Kiểm thêm `0 <= flagged <= total` (hoặc đếm thẳng từ `scores` và cỡ mẫu tập kiểm tra) trước khi dựng khối, để phép kiểm BR2.7 có thứ để bắt. | New |

### Validation Tool Results

| Tool | Result | Interpretation |
|---|---|---|
| `python -X utf8 -m pytest -m "not slow" -q` | `485 passed, 11 deselected in 16.67s` | Khớp báo cáo của người làm (485 nhanh, 496 tổng); bộ nhanh xanh trên cây làm việc hiện tại. |
| `python -X utf8 -m ruff check .` | `All checks passed!` | Khớp tuyên bố; không có `per-file-ignores` mới. |
| `ruff format --check` trên 10 tệp đã chạm | `10 files already formatted` | Khớp tuyên bố "8 files" (tôi chạy rộng hơn, gồm cả tệp U1); danh sách khai tay trong `ci.yml:35` phủ `model.py`, `service.py` và hai test mới. |
| Chạy lại bước mô hình trên mart thật (`TRAINING_FRAME_SQL` → `train_from_frame` path) | `train_n 64322`, `test_n 32156`, `late_train 5890`, `late_test 1936`, `full_model_auc 0.5133`; baseline `customer_state`-đơn `0.5333`; độ rộng ma trận `66` | Tái lập chính xác cỡ mẫu và `auc 0.5133`; khối trong `data/reports/analysis.json` (auc 0.5133, threshold 0.4, precision 0.0866, recall 0.2645, 5910 + 26246 = 32156) tự khớp số học (TP ≈ 512, 512/5910 = 0,0866; 512/1936 = 0,2645). Con số được ghi là trung thực, không bị ẩn; đồng thời lộ ra mô hình thua baseline một đặc trưng (xem finding Major). |
| `python -m coverage report --include="src/analytics/*"` (trên `.coverage` có sẵn của lần chạy của người làm) | `src\analytics\model.py 174 0 100%`, `service.py 151 6 96%` | Khớp code-summary; tôi **không** chạy lại cổng phủ đầy đủ vì bộ `slow` sẽ ghi đè `data/reports/analysis.json` và brief cấm sửa tệp. |

### Summary

Sáu sai lệch đều ở mức chấp nhận được và đã khai báo trung thực: ba tệp test ngoài manifest chỉ bị sửa vì hình dạng chúng khẳng định đổi theo kế hoạch (không nới khẳng định nào — `test_u1_stats_end_to_end.py` còn chặt hơn), việc thêm `service.py` vào danh sách format là đúng quy tắc nhóm, `train_from_frame` nhận cỡ mẫu kỳ vọng vẫn giữ mặc định 96.478/7.826 trên đường sản xuất (có test chứng minh `train_model` từ chối mart lệch baseline), ca `stats` ở bộ nhanh gọi thật `train_from_frame` chứ không mock, nhãn `str()` của `purchase_month`/`purchase_weekday` chỉ sống trong ma trận đặc trưng, và tính `auc_below_target` trên AUC đã làm tròn là cách duy nhất giữ tệp không tự mâu thuẫn — chỉ cần đồng bộ lại câu chữ traceability.

Mối lo chính không phải là gian lận số liệu mà là chất lượng: code implement BR2.1–BR2.9, TS-6/TS-8/TS-9 đúng như viết (chia tập trước khi mã hoá, phạm trù và scaler khớp chỉ trên tập huấn luyện, 11 cột đặc trưng rời 10 cột cấm, không bỏ dòng nào), nhưng kết quả thật AUC 0,5133 thấp hơn cả baseline một đặc trưng và không có cổng nào phát hiện được điều đó — cần người quyết định trước khi U3 đưa mô hình này lên dashboard.
