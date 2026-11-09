# Business Rules — u4-record-linkage

Nguồn: `inception/domain-design/components.md` (khối `RecordLinkage`), `inception/user-stories/stories.md` (US3.1–US3.3, AC3.2.3), `inception/contract-design/contract-summary.md` (C5), `inception/requirements-analysis/requirements.md` (FR3.1–FR3.4).

**Thay đổi so với bản trước, theo quyết định của người làm:** bằng chứng ghép nay gồm **hai tín hiệu** — địa lý (như cũ) và **hành vi mua** lấy từ đơn hàng và thanh toán. Lý do đo được: chỉ dùng địa lý, trên dữ liệu thật có 805.778 cặp "Ghép" nhưng chỉ 3.631 cặp cùng `customer_unique_id` — tỉ lệ đúng khoảng **0,45%**, trong khi màn hình D hứa 84,2%. Hai trường địa lý không phân biệt được hai người khác nhau sống cùng thành phố và cùng mã bưu chính; hành vi mua thì phân biệt được.

```yaml
rules:
  - id: BR4.1
    statement: Chỉ những bản ghi trùng đủ năm chữ số mã bưu chính mới được so với nhau
    category: policy
    applies_to: BlockingRule
    trigger: trước khi chấm điểm
    logic: >
      Khoá chặn là TOÀN BỘ năm chữ số của customer_zip_code_prefix. Hai bản ghi khác khoá chặn
      không sinh cặp ứng viên. Độ dài khoá chặn là hằng số 5 trong mã, không phải tham số cấu hình:
      ba chữ số đầu sinh 14.801.253 cặp, bốn chữ số còn 2.553.000 cặp — đều không dùng được.
      Trên dữ liệu thật, chặn 5 chữ số còn 806.705 cặp khách.
    violation: không có — luật chặn
    source: FR3.1

  - id: BR4.2
    statement: Thành phố được chuẩn hoá trước khi so khớp
    category: calculation
    applies_to: MatchPair
    trigger: khi tính điểm
    logic: >
      Chuẩn hoá city: NFKD và bỏ dấu kết hợp, chữ thường, gộp khoảng trắng, cắt hai đầu.
      So khớp trên chuỗi đã chuẩn hoá.
    violation: không có
    source: FR3.1

  - id: BR4.3
    statement: Bằng chứng địa lý là tỉ lệ khớp ký tự của thành phố, định nghĩa chính xác
    category: calculation
    applies_to: MatchPair
    trigger: khi tính điểm
    logic: >
      geo_ratio = difflib.SequenceMatcher(None, city_a, city_b).ratio() = 2 * M / (len_a + len_b),
      bằng 1.0 khi bằng nhau, 0.0 khi một chuỗi rỗng. Mã bưu chính bằng nhau do cách chặn nên
      không tham gia (BR4.1); nó vẫn được ghi vào cặp dưới dạng zip_prefix.
    violation: không có
    source: FR3.1

  - id: BR4.4
    statement: Bằng chứng hành vi mua là độ trùng tập sản phẩm giữa hai khách
    category: calculation
    applies_to: MatchPair
    trigger: khi tính điểm
    logic: >
      Với mỗi customer_id, dựng tập product_id từ order_items của mọi đơn của khách đó
      (join orders theo order_id). order_ratio = |A ∩ B| / |A ∪ B| (Jaccard).
      Nếu một trong hai tập rỗng THEN cặp vào skipped với missing_fields = ["orders"], lý do
      "một trong hai khách không có đơn hàng"; không chấm điểm.
      Kèm theo, ghi payment_similarity = tỉ lệ đơn của A và B có cùng payment_value (đã làm tròn 2)
      để người đọc thấy bằng chứng thanh toán; trường này KHÔNG tham gia điểm.
    violation: cặp vào skipped; lần chạy tiếp tục
    source: FR3.1

  - id: BR4.5
    statement: Điểm cuối là trung bình có trọng số của hai bằng chứng, thiên về hành vi mua
    category: calculation
    applies_to: MatchPair
    trigger: khi tính điểm
    logic: >
      score = round(0.40 * geo_ratio + 0.60 * order_ratio, 6) — giữ 6 chữ số để phép so ngưỡng
      không bị ảnh hưởng bởi làm tròn; điểm ghi ra tệp làm tròn 4 chữ số.
      Thiên về hành vi mua vì đó là tín hiệu phân biệt được hai người khác nhau; địa lý chỉ còn
      vai trò bằng chứng phụ (và đã bị chặn theo mã bưu chính).
    violation: không có
    source: FR3.1

  - id: BR4.6
    statement: Quyết định theo ngưỡng cố định 0,85 trên điểm chưa làm tròn 4 chữ số
    category: policy
    applies_to: MatchPair
    trigger: sau khi có điểm
    logic: >
      IF score > 0.85 THEN decision = Ghép.
      IF |score - 0.85| <= 1e-9 THEN decision = Xem lại.
      IF score < 0.85 THEN cặp không được ghi vào kết quả.
      So trên score 6 chữ số (BR4.5), không so trên giá trị đã làm tròn khi ghi.
    violation: không có
    source: FR3.2

  - id: BR4.7
    statement: Mỗi cặp chỉ xuất hiện một lần, theo thứ tự chuỗi của hai mã
    category: calculation
    applies_to: MatchPair
    trigger: khi sinh cặp
    logic: >
      record_a = min(x, y), record_b = max(x, y) theo thứ tự chuỗi; không sinh cặp ngược,
      không sinh cặp của một bản ghi với chính nó.
    violation: không có
    source: FR3.1

  - id: BR4.8
    statement: Tỉ lệ ghép đúng chỉ tính cho khách hàng, theo customer_unique_id
    category: calculation
    applies_to: LinkageResult.summary.correct_rate
    trigger: khi tổng hợp kết quả
    logic: >
      correct_rate = số cặp Ghép có cùng customer_unique_id / tổng số cặp Ghép; làm tròn 4 chữ số;
      null nếu không có cặp Ghép nào. Kèm summary.correct_rate_sample = số cặp dùng làm tử số.
      Với target seller: correct_rate = null, summary.correct_rate_reason nêu lý do.
    violation: không có
    source: FR3.3

  - id: BR4.9
    statement: Số nhóm trùng đếm theo khoá mốc
    category: calculation
    applies_to: LinkageResult.summary.duplicate_groups
    trigger: khi tổng hợp kết quả
    logic: >
      duplicate_groups = số giá trị customer_unique_id xuất hiện từ hai dòng trở lên trong nguồn
      (2.997 nhóm trên dữ liệu thật), bất kể chúng có được ghép hay không.
    violation: không có
    source: FR3.3

  - id: BR4.10
    statement: Kết quả có trần 10.000 cặp và trần đó phải được nói ra
    category: policy
    applies_to: LinkageResult
    trigger: khi ghi kết quả
    logic: >
      IF số cặp vượt 10.000 THEN chỉ ghi 10.000 cặp có score cao nhất (hoà thì theo pair_id) và
      đặt summary.pairs_truncated = true, summary.pairs_total = tổng số cặp đạt ngưỡng.
      IF không cắt THEN pairs_truncated = false và pairs_total = số cặp đã ghi.
      Cắt danh sách KHÔNG làm sai các con số trong summary.
    violation: không có
    source: FR3.3
```

## Tóm tắt quy tắc

| Mã | Loại | Nội dung ngắn |
|---|---|---|
| BR4.1 | Chính sách | Chặn theo đủ năm chữ số mã bưu chính (hằng số) |
| BR4.2 | Tính toán | Chuẩn hoá thành phố trước khi so |
| BR4.3 | Tính toán | Bằng chứng địa lý: `SequenceMatcher.ratio()` của thành phố |
| BR4.4 | Tính toán | Bằng chứng mua: Jaccard tập `product_id`; thiếu đơn → bỏ qua |
| BR4.5 | Tính toán | Điểm = 0,40 × địa lý + 0,60 × mua (6 chữ số khi so) |
| BR4.6 | Chính sách | Ngưỡng 0,85; đúng ngưỡng (1e-9) là "Xem lại" |
| BR4.7 | Tính toán | Mỗi cặp một lần, theo thứ tự chuỗi |
| BR4.8 | Tính toán | Tỉ lệ đúng chỉ cho khách hàng, kèm cỡ mẫu |
| BR4.9 | Tính toán | Số nhóm trùng đếm theo `customer_unique_id` |
| BR4.10 | Chính sách | Trần 10.000 cặp, khai bằng `pairs_truncated`/`pairs_total` |
