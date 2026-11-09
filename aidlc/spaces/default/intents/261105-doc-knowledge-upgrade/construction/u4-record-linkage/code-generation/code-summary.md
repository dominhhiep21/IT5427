# Code Summary — u4-record-linkage

Nguồn: kế hoạch đã duyệt `code-generation-plan.md`, hướng dẫn test `unit-test-instructions.md`, và báo cáo build của đơn vị.

## 1. Đã dựng gì

| Lớp | Tệp | Nội dung |
|---|---|---|
| Data model | `src/linkage/models.py` | `BlockingRule`, `MatchPair`, `SkippedPair`, `LinkageResult`, `LinkageResultError`, `normalize_city`, `zip_prefix`, `blocking_rule`, `pair_id_for`; hằng `THRESHOLD=0.85`, `GEO_WEIGHT=0.40`, `ORDER_WEIGHT=0.60`, `MAX_PAIRS=10_000`, `BLOCKING_KEY_LENGTH=5` |
| Data access | `src/linkage/index.py` | `Evidence`, `EvidenceIndex`, `evidence_for` (thuần), `build_index` — đọc đủ bộ cột của `TableSpec` rồi chọn cột con, nên `SchemaError` nêu đúng cột thiếu |
| Business logic | `src/linkage/score.py` | `blocking_groups`, `string_ratio`/`city_similarity`/`order_similarity`/`payment_similarity`, `combined_score`, `decide`, `score_pairs`, `cap`, `summarise` |
| Ghi kết quả | `src/linkage/result.py` | `result_path`, `build_result`, `write_result` (ghi + đọc lại kiểm), `generate_linkage` (ba sự kiện `integration.linkage.*`) |
| Nối pipeline | `src/pipeline/stages.py` | `_run_linkage` gọi trong `_run_all` sau `integrate` và trong `run_stage("integrate")`; mỗi đối tượng độc lập; thêm dòng `StageResult("linkage", …)` vào `run-summary.json` |
| Cấu hình | `config.yaml`, `src/config.py` | `paths.integration_dir: data/integration` + trường `integration_dir` trong `AppConfig` |

## 2. Quyết định chính

| Quyết định | Vì sao |
|---|---|
| Đọc nguồn qua `read_csv(path, spec)` của `src/common/io.py` | `validate_columns` so theo **vị trí**, còn `pd.read_csv(usecols=…)` trả theo **thứ tự tệp**; đọc đủ bộ cột rồi chọn cột con vừa tránh lỗi thứ tự vừa dùng lại `SchemaError` nêu tên cột |
| `cap`/`summarise` nhận `limit=MAX_PAIRS` | Để test quy tắc cắt mà không phải dựng 10.000 cặp mỗi lần; đây là tham số của hàm, không phải đầu vào người dùng (SR-U4-3) |
| Ghép ghi một `StageResult("linkage")` riêng | `run-summary.json` nói được bước nào đã chạy; gộp vào `integrate` sẽ giấu mất bước mới |
| Rút gọn câu lý do trong `skipped` | Câu đầy đủ đẩy tệp lên 4,88 MB vì 12.613 cặp bỏ qua mỗi cặp mang một câu; câu ngắn giữ tệp 4,07 MB (xem §5) |

## 3. Kết quả kiểm chứng

| Cổng | Lệnh | Kết quả |
|---|---|---|
| Test đơn vị mới | `pytest tests/unit/test_linkage_*.py -m "not slow"` | 44 passed |
| Bộ nhanh toàn repo | `pytest -m "not slow"` | 177 passed, 6 deselected |
| Lint | `ruff check .` | sạch |
| Định dạng | `ruff format --check` trên phạm vi CI | sạch |

**Đầu ra đỏ đã ghi (TDD):** bước 3/6/9/15 lần lượt đỏ với `ModuleNotFoundError: No module named 'src.linkage.<module>'` trước khi có mã.

## 4. Chỉ tiêu đo được

| Mã | Ngưỡng | Đo được | Kết luận |
|---|---|---|---|
| NFR1.1 | ≤ 60 giây | dựng chỉ mục + chấm **794.092 cặp** (cộng 12.613 cặp bỏ qua = 806.705 cặp ứng viên) trong **3,5–5,5 giây** trên dữ liệu thật | đạt |
| NFR1.2 | tệp ≤ 5 MB (đo cả `pairs` lẫn `skipped`) | `linkage-customer.json` **4,07 MB**; `linkage-seller.json` 755 B; đọc lại kiểm 0,2 giây (tham khảo, không phải ngưỡng) | đạt, biên mỏng — xem §5 |
| NFR2.1 | ≥ 80% | toàn dự án **81%** trên bộ nhanh (cận dưới); gói mới 91–98% | đạt |
| NFR3.1 | 0 vi phạm | ruff check + format sạch | đạt |
| NFR6.1 | không mạng | không import mạng, không đọc biến môi trường | đạt |

**Số đo nghiệp vụ — giả thuyết A2 đã được kiểm:** `correct_rate` = **0,5301** với **388/732** cặp Ghép cùng `customer_unique_id`, so với **0,45%** của hướng chỉ-dùng-địa-lý. `duplicate_groups` = **2.997**, khớp BR4.9. Nói cách khác: đổi tín hiệu ghép đã nâng tỉ lệ đúng từ 0,45% lên 53%. Con số này vẫn **thấp hơn** 84,2% mà màn hình D hứa — cần người chốt lại ngưỡng hoặc kỳ vọng (xem §6).

## 5. Điểm lệch kế hoạch

| # | Lệch | Ghi chú |
|---|---|---|
| 1 | `build_index` dùng helper `read_csv(path, spec)` — đọc **đủ** bộ cột của `TableSpec` | TS-U4-4 (bản đã sửa 2026-11-09) chốt đúng cách này; `usecols` không dùng được qua helper và đọc đủ cột là chấp nhận được với ba bảng này |
| 2 | `evidence_for` nhận thêm frame bản ghi | Chữ ký trong kế hoạch không dựng được bằng chứng theo từng bản ghi; hàm vẫn thuần, test không cần đĩa |
| 3 | `cap`/`summarise` có `limit` | Để kiểm trần mà không dựng 10.000 cặp; vẫn có một test dựng 10.001 cặp thật |
| 4 | Thêm `StageResult("linkage")` vào `run-summary.json` | Làm bước mới hiện ra trong báo cáo lần chạy |
| 5 | Câu lý do trong `skipped` được rút gọn | Dung lượng: 4,88 MB → 4,07 MB |

**Cần chuyển sang Build and Test:** phần lớn dung lượng tệp đến từ kênh `skipped` (12.613 cặp, mỗi cặp một câu lý do), trong khi trần 10.000 cặp của BR4.10 chỉ áp cho `pairs`. Nếu số bản ghi thiếu đơn tăng, NFR1.2 (5 MB) sẽ vỡ trước khi BR4.10 có tác dụng. Đề xuất ở bước sau: hoặc đặt trần cho `skipped`, hoặc gộp lý do theo `missing_fields`.

## 6. Test viết nhưng chưa chạy

Bộ `slow` (6 test, gồm 3 test end-to-end trên dữ liệu thật) **không** chạy ở bước này — thuộc lần xác nhận trước phát hành và Build and Test, đúng như `unit-test-instructions.md` ghi.

## 7. Việc còn phải chốt ở cấp yêu cầu (không thuộc đơn vị này)

- FR3, AC3.2.3 (con số 84,2%) và màn hình D trong `mockups.md` cần được sửa theo hướng ghép mới: số đo thật là 53,01%, không phải 84,2%.
- `correct_rate` cho người bán vẫn là `null` kèm lý do vì nguồn không có khoá mốc (Q1 của `functional-spec.md`).
