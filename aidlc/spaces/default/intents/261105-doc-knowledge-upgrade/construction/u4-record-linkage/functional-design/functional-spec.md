# Functional Spec — u4-record-linkage

Đơn vị: `u4-record-linkage` (Ghép bản ghi). Phục vụ US3.1–US3.3 và phần dữ liệu của US6.1. Đọc trực tiếp bảng nguồn, **không** dùng lược đồ trung gian; không hiển thị gì — kết quả ghi ra `data/` để U6 đọc lại (C5).

**Đổi hướng theo quyết định của người làm (2026-11-06):** bằng chứng ghép gồm **địa lý + hành vi mua**. Bản chỉ-dùng-địa-lý đo được **0,45%** cặp đúng trên dữ liệu thật, không thể đạt con số 84,2% mà màn hình D hứa; hành vi mua là tín hiệu phân biệt được hai người khác nhau.

## Nguồn vào

| Đối tượng | Bảng nguồn | Khoá chính | Khoá mốc | Bằng chứng địa lý | Bằng chứng mua |
|---|---|---|---|---|---|
| `customer` | `olist_customers_dataset` (99.441 dòng) | `customer_id` | `customer_unique_id` (96.096 giá trị, 2.997 nhóm trùng) | `customer_city`, `customer_zip_code_prefix` | `olist_orders_dataset` → `olist_order_items_dataset.product_id`; `olist_order_payments_dataset.payment_value` |
| `seller` | `olist_sellers_dataset` (3.095 dòng) | `seller_id` | **không có** | `seller_city`, `seller_zip_code_prefix` | `olist_order_items_dataset` theo `seller_id` → `product_id`; `payment_value` của đơn chứa món đó |

Bảng nguồn và cột lấy từ `src/ingest/schemas.py` — một nguồn sự thật duy nhất, không khai lại tên bảng ở chỗ khác.

## Workflow 1 — Chặn và sinh cặp ứng viên

1. Đọc bảng khách/người bán và bảng đơn/món/thanh toán cần cho đối tượng đang tính.
2. Kiểm cột nguồn có thật; thiếu thì dừng **đối tượng đó** với `SchemaError` nêu tên trường và tên cột.
3. Dựng tập `product_id` và tập `payment_value` cho mỗi bản ghi (BR4.4). Bản ghi không có đơn nào vẫn được giữ và sẽ thành cặp bị bỏ qua, không bị loại im lặng.
4. Gom theo **đủ năm chữ số** mã bưu chính (BR4.1). Bản ghi thiếu mã bưu chính không vào nhóm nào; đếm vào `summary.records_missing_match_fields`.
5. Trong mỗi nhóm, sinh mọi cặp khác khoá chính, mỗi cặp một lần (BR4.7).

Trên dữ liệu thật, bước này cho **806.705** cặp khách và vài nghìn cặp người bán. Ba chữ số đầu sẽ cho 14.801.253 cặp — không chạy được, nên khoá chặn là hằng số 5.

## Workflow 2 — Chấm điểm và quyết định

1. `geo_ratio` = `difflib.SequenceMatcher(None, city_a, city_b).ratio()` trên hai city đã chuẩn hoá (BR4.2, BR4.3).
2. `order_ratio` = Jaccard hai tập `product_id` (BR4.4). Một bên rỗng → cặp vào `skipped`, không chấm.
3. `score = 0.40 * geo_ratio + 0.60 * order_ratio`, giữ 6 chữ số khi so (BR4.5).
4. Áp ngưỡng trên `score` chưa làm tròn: `> 0,85` → **Ghép**; `|score − 0,85| ≤ 1e-9` → **Xem lại**; nhỏ hơn → không ghi (BR4.6).
5. Ghi vào mỗi cặp: `geo_ratio`, `order_ratio`, `payment_similarity`, `zip_prefix` — người đọc thấy vì sao cặp được ghép.
6. Với `customer`, `is_correct` = hai bản ghi cùng `customer_unique_id`; với `seller`, `null`.

**Lỗi:** một cặp dị dạng không làm hỏng cả lô — cặp đó vào `skipped` với lý do.

## Workflow 3 — Bỏ qua cặp thiếu bằng chứng

| Trường hợp | Ghi vào đâu |
|---|---|
| Bản ghi thiếu mã bưu chính | Không sinh cặp; đếm vào `summary.records_missing_match_fields` (BR4.1) |
| Bản ghi không có đơn nào | Cặp vào `skipped` với `missing_fields = ["orders"]` và lý do tiếng Việt |
| Cặp mà một bên thiếu city | Cặp vào `skipped` với `missing_fields = ["city"]` |

Cặp bị bỏ qua không vào `pairs` và không tính vào `pairs_scored`. Tổng bản ghi không chấm được = `records_missing_match_fields` + số bản ghi trong các cặp `skipped` (không trùng nhau, vì bản ghi thiếu zip không vào nhóm nào).

## Workflow 4 — Tổng hợp và ghi kết quả

1. `summary`: `pairs_scored`, `pairs_matched`, `pairs_review`, `pairs_skipped`, `pairs_total`, `pairs_truncated`, `records_scored`, `records_missing_match_fields`, `duplicate_groups` (BR4.9), `correct_rate` + `correct_rate_sample` (BR4.8), và `correct_rate_reason` khi áp dụng.
2. Áp trần BR4.10: quá 10.000 cặp thì ghi 10.000 cặp điểm cao nhất, `pairs_total` giữ tổng thật.
3. Ghi `LinkageResult` bằng `AtomicWriter.write_json` ra `data/integration/linkage-<entity>.json` đúng payload C5; `run_id`, `computed_at` lấy từ `RunContext`.
4. **Kiểm sau khi ghi:** đọc lại tệp vừa ghi; khẳng định có `summary`, `len(pairs) == min(pairs_total, 10000)`, và `len(skipped)` bằng `pairs_skipped`; lệch thì ném lỗi — `write_json` không tự kiểm như `write_parquet`.
5. Ghi sự kiện `integration.linkage.completed`: `target_entity`, `pairs_scored`, `pairs_matched`, `pairs_review`, `pairs_skipped`, `pairs_truncated`, `elapsed_ms`.
6. **Ghi tách theo từng đối tượng:** một đối tượng lỗi không ngăn đối tượng kia; đối tượng lỗi được nêu trong sự kiện `integration.linkage.failed` và lỗi nổi lên tầng pipeline sau khi đối tượng còn lại đã xong.
7. Chạy **một lần** ở tầng pipeline (sau `integrate`), không theo mỗi tương tác giao diện.

## Hệ quả phải xử lý ở nơi khác (không sửa trong đơn vị này)

| Artifact | Phải đổi gì | Vì sao |
|---|---|---|
| `inception/requirements-analysis/requirements.md` FR3 | Phát biểu lại bằng chứng ghép: địa lý + hành vi mua, kèm ngưỡng và tỉ lệ đúng đo được thay vì "0,85 là đủ" | Yêu cầu cũ chỉ nói địa lý, và tiền đề đó không đạt được độ chính xác mong muốn |
| `inception/user-stories/stories.md` AC3.2.3 | Bỏ con số "84,2%" cố định; thay bằng "tỉ lệ đúng đo được ở lần chạy gần nhất, kèm cỡ mẫu"; bỏ vế người bán hoặc định nghĩa khoá mốc cho người bán | Con số 84,2% không có nguồn và trái dữ liệu; người bán không có khoá mốc |
| `inception/refined-mockups/mockups.md` màn hình D | `84,2%` thành giá trị đo được, kèm cỡ mẫu | Cùng lý do |
| `inception/contract-design/contract-summary.md` C5 | Thêm các trường `pairs_total`, `pairs_truncated`, `correct_rate_sample`, `correct_rate_reason`, `duplicate_groups_reason`, `records_missing_match_fields` | Đây là thay đổi **cộng thêm** mà U6 cần biết trước |

Đơn vị này chỉ ghi nhận; việc sửa các artifact inception là thay đổi phạm vi phải chốt lại, không tự làm trong một đơn vị Construction.

## Giả định và câu hỏi mở

| # | Nội dung | Trạng thái |
|---|---|---|
| A1 | Chuẩn hoá thành phố bằng bỏ dấu là đủ | Giả định — nguồn có cả dạng có dấu và không dấu |
| A2 | Tập sản phẩm phân biệt được hai người khác nhau tốt hơn địa lý | **Chưa đo.** Đây là giả thuyết của hướng mới, phải kiểm bằng số đo ở Build and Test; nếu tỉ lệ đúng vẫn thấp, việc cần làm là **siết bằng chứng** (ví dụ đòi thêm trùng `payment_value`, đòi Jaccard ≥ 0,9), không phải hạ ngưỡng |
| A3 | Chạy xong trong khoảng 60 giây | Số cặp đã biết (806.705 cặp khách); chi phí chấm mỗi cặp là hai phép so chuỗi ngắn cộng một phép giao tập đã dựng sẵn. Chưa đo với bằng chứng mua; nếu vượt, giảm số cặp bằng cách chặn chặt hơn, không đổi ngưỡng |
| A4 | Chỉ dùng thư viện chuẩn (`difflib`, `unicodedata`, set) | Đúng ràng buộc "không thêm thư viện chưa ghim" |
| Q1 | Với người bán không có khoá mốc, `correct_rate` trả null kèm lý do và AC3.2.3 được đánh dấu **Deferred** cho vế người bán | **Cần bạn chốt** cùng lúc với việc sửa AC3.2.3 (bảng trên) |
| Q2 | Ngưỡng 0,85 giữ nguyên cho điểm tổng hợp mới, hay cần hiệu chỉnh sau khi đo A2? | Không chặn dựng mã: giữ 0,85 cho lần chạy đầu, ghi lại tỉ lệ đúng đo được, rồi mới bàn hiệu chỉnh — đổi ngưỡng là đổi yêu cầu, không phải đổi mã |
