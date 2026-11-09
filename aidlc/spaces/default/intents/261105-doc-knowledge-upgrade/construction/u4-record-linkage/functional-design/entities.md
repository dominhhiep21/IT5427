# Entities — u4-record-linkage

Nguồn: `inception/domain-design/components.md` (khối `RecordLinkage`, ba thực thể `BlockingRule`, `MatchPair`, `SkippedPair`), `inception/contract-design/contract-summary.md` (C5 — payload `LinkageResultFile`), `inception/units-generation/unit-of-work.md` §U4, `inception/requirements-analysis/requirements.md` (FR3).

```yaml
entities:
  - name: BlockingRule
    description: Luật chia lô ứng viên trước khi chấm điểm, tránh so mọi cặp với mọi cặp
    attributes:
      - name: rule_id
        type: string
        required: true
        unique: true
      - name: target_entity
        type: enum
        required: true
        allowed: [customer, seller]
      - name: blocking_field
        type: string
        required: true
        description: Trường dùng để chặn; với cả hai đối tượng là mã bưu chính đầy đủ
      - name: blocking_key_length
        type: integer
        required: true
        description: Số chữ số dùng làm khoá chặn — hằng số 5, không phải tham số cấu hình
      - name: match_fields
        type: list[string]
        required: true
        description: >
          Bằng chứng dùng để tính điểm: [city đã chuẩn hoá, product_id của các đơn của bản ghi,
          payment_value của các đơn đó]
      - name: threshold
        type: decimal
        required: true
        description: Ngưỡng cố định 0,85 — không đổi được từ giao diện
    constraints:
      - Cặp ứng viên chỉ sinh giữa hai bản ghi **khác nhau** trong cùng một bảng nguồn
      - Hai bản ghi cùng khoá chính (cùng customer_id / cùng seller_id) không phải cặp ứng viên
      - Bản ghi thiếu mã bưu chính không vào nhóm chặn nào; số lượng được đếm ở `summary.records_missing_match_fields`

  - name: MatchPair
    description: Một cặp bản ghi đã được chấm điểm, kèm quyết định
    attributes:
      - name: pair_id
        type: string
        required: true
        unique: true
        description: Sinh ổn định từ (target_entity, record_a, record_b) để chạy lại cho cùng id
      - name: target_entity
        type: enum
        required: true
        allowed: [customer, seller]
      - name: record_a
        type: string
        required: true
      - name: record_b
        type: string
        required: true
      - name: score
        type: decimal
        required: true
        description: 0,40 × geo_ratio + 0,60 × order_ratio, ghi 4 chữ số thập phân
      - name: geo_ratio
        type: decimal
        required: true
        description: Tỉ lệ khớp ký tự của hai city đã chuẩn hoá (BR4.3)
      - name: order_ratio
        type: decimal
        required: true
        description: Jaccard hai tập product_id (BR4.4)
      - name: payment_similarity
        type: decimal
        required: true
        description: Tỉ lệ đơn của hai bên có cùng payment_value — bằng chứng phụ, không tham gia điểm
      - name: zip_prefix
        type: string
        required: true
        description: Năm chữ số mã bưu chính dùng làm khoá chặn, ghi để người đọc đối chiếu
      - name: decision
        type: enum
        required: true
        allowed: [Ghép, Xem lại]
      - name: is_correct
        type: boolean
        required: false
        description: Chỉ có nghĩa với target customer (so với customer_unique_id); null với seller
    constraints:
      - record_a < record_b theo thứ tự chuỗi, để một cặp không xuất hiện hai lần
      - quyết định Ghép khi score > 0,85; Xem lại khi score bằng đúng ngưỡng trong dung sai 1e-9

  - name: SkippedPair
    description: Cặp ứng viên không chấm được vì thiếu trường so khớp
    attributes:
      - name: skip_id
        type: string
        required: true
        unique: true
      - name: target_entity
        type: enum
        required: true
        allowed: [customer, seller]
      - name: record_a
        type: string
        required: true
      - name: record_b
        type: string
        required: true
      - name: missing_fields
        type: list[string]
        required: true
        description: Tập con của {city, zip_code_prefix}
      - name: reason
        type: string
        required: true
        description: Câu tiếng Việt nêu trường nào thiếu, để hiện thẳng trên giao diện

  - name: LinkageResult
    description: Toàn bộ kết quả của một đối tượng, đúng payload C5 ghi ra tệp
    attributes:
      - name: target_entity
        type: string
        required: true
      - name: run_id
        type: string
        required: true
      - name: computed_at
        type: string
        required: true
        description: ISO-8601 UTC
      - name: threshold
        type: decimal
        required: true
        description: Luôn 0.85, ghi vào tệp để người đọc biết ngưỡng đã dùng
      - name: summary
        type: object
        required: true
        description: >
          pairs_scored, pairs_matched, pairs_review, pairs_skipped, pairs_total, pairs_truncated,
          records_scored, records_missing_match_fields, duplicate_groups, correct_rate,
          correct_rate_sample, và các trường lý do khi áp dụng
          (correct_rate_reason, duplicate_groups_reason)
      - name: pairs
        type: list[MatchPair]
        required: true
      - name: skipped
        type: list[SkippedPair]
        required: true
    constraints:
      - `summary` luôn có mặt kể cả khi mọi danh sách rỗng (C5)
      - `correct_rate` là số thực với target customer, là null với target seller kèm `correct_rate_reason`
      - `pairs_total` là tổng số cặp đạt ngưỡng, `pairs_truncated` cho biết `pairs` đã bị cắt theo BR4.10 — cả hai thay cho kênh `partial` của C5, vốn có nghĩa "một đối tượng chưa có kết quả"
```

## Ghi chú thiết kế

- **Bốn thực thể, ba trong `components.md`.** `BlockingRule`, `MatchPair`, `SkippedPair` là ba thực thể `components.md` giao cho khối `RecordLinkage`. `LinkageResult` là **payload của hợp đồng C5**, không phải thực thể miền mới: nó chỉ gói ba thực thể kia lại thành đúng hình dạng tệp mà U6 đọc, và tồn tại để hai bên có một hình dạng chung thay vì U6 tự đoán. Nếu C5 đổi, `LinkageResult` đổi theo.
- **Hai đối tượng, hai tệp**: C5 đặt `data/integration/linkage-<customer|seller>.json`; mỗi tệp là một `LinkageResult` độc lập, không gộp. Một đối tượng lỗi không ngăn đối tượng kia ghi tệp.
- **`is_correct` chỉ có nghĩa với khách hàng.** `customer_unique_id` là khoá mốc thật cho người; với người bán, nguồn chỉ có `seller_id` và mỗi người bán xuất hiện đúng một dòng, nên "cùng `seller_id`" luôn sai với mọi cặp khác khoá. Vì vậy trường này để null và `correct_rate` là null kèm lý do — thay vì ghi 0,0 như một sự thật.
- **`pair_id` ổn định** để chạy lại trên cùng dữ liệu cho ra cùng id; người xem và test đều dựa vào đó.
- **`zip_ratio` không còn là biến số** — mã bưu chính bằng nhau do cách chặn, nên nó chỉ được ghi lại dưới dạng `zip_prefix`; biến tham gia điểm là `geo_ratio` (thành phố) và `order_ratio` (hành vi mua).
- **`pairs_truncated` thay cho `partial`.** C5 dùng `partial` cho nghĩa "một đối tượng chưa có kết quả"; dùng nó cho việc cắt danh sách sẽ đổi nghĩa hợp đồng. Hai trường `pairs_total` và `pairs_truncated` trong `summary` nói đúng điều xảy ra.
