# Contract Summary — Nâng cấp tích hợp dữ liệu Olist

Nguồn: `inception/units-generation/unit-of-work.md`, `unit-of-work-dependency.md`, `inception/domain-design/components.md`, `inception/requirements-analysis/requirements.md`.

Mọi trao đổi đều là gọi hàm Python trong cùng tiến trình, dữ liệu đi qua dataclass. Không có REST, không có event bus. Hợp đồng vì vậy là **lược đồ dùng chung** (shared-schema). Kết quả ghép bản ghi là ngoại lệ duy nhất: bàn giao qua tệp trong `data/`.

## Contracts table

| # | Provider Unit | Consumer | Mechanism | Owner |
|---|---|---|---|---|
| C1 | U2 `u2-mediated-schema` | U3 `u3-query-rewriter` | shared-schema: hàm + dataclass | U2 |
| C2 | U2 `u2-mediated-schema` | U5 `u5-source-selector` | shared-schema: hàm + dataclass | U2 |
| C3 | U5 `u5-source-selector` | U3 `u3-query-rewriter` | shared-schema: hàm + dataclass | U5 |
| C4 | U3 `u3-query-rewriter` | U6 `u6-integration-ui` | shared-schema: hàm + dataclass | U3 |
| C5 | U4 `u4-record-linkage` | U6 `u6-integration-ui` | shared-schema: tệp trong `data/` | U4 |
| C6 | U2 `u2-mediated-schema` | U6 `u6-integration-ui` | shared-schema: hàm + dataclass | U2 |
| C7 | U5 `u5-source-selector` | U6 `u6-integration-ui` | shared-schema: hàm + dataclass | U5 |
| C8 | U1 `u1-thin-slice` | U2 `u2-mediated-schema` | shared-schema: tệp khai báo lược đồ đầu tiên | U1 |
| C9 | U1 `u1-thin-slice` | U6 `u6-integration-ui` | shared-schema: khung tab và tệp cấu hình đầu tiên | U1 |

Không có hợp đồng công khai bên ngoài: dashboard chỉ chạy localhost.

## C1 — U2 cung cấp lược đồ cho U3

```yaml
shared-schema:
  name: MediatedSchemaView
  provider: u2-mediated-schema
  consumer: u3-query-rewriter
  payload:
    entities:
      - name: str            # don_hang | mat_hang | san_pham
        description: str
        source_tables: list[str]
    mappings:
      - type: dict[str, list[FieldMapping]]
        key: entity_name
        value_fields:
          field_name: str
          source_table: str
          source_column: str
          data_type: str     # string | integer | decimal | timestamp
    schema_kind: str         # hằng "GAV"
    elapsed_ms: int          # thời lượng nạp + kiểm, do chính bộ nạp đo (thêm 2026-11-07, cộng thêm)
  errors:
    - SchemaError            # nội dung khai báo sai: thiếu trường bắt buộc, định danh sai, trùng tên trường, sai schema_kind, sai data_type, hoặc cột nguồn không tồn tại
    - ConfigurationError     # thiếu tệp: tệp lược đồ hoặc tệp CSV nguồn không có mặt (thêm 2026-11-07, cộng thêm)
  partial:
    when: chỉ một phần thực thể nạp được
    carries: danh sách thực thể thiếu và lý do
  change_policy: chỉ thêm trường; không đổi nghĩa hay xoá trường đang có
```

## C2 — U2 cung cấp danh mục trường cho U5

```yaml
shared-schema:
  name: MediatedFieldCatalogue
  provider: u2-mediated-schema
  consumer: u5-source-selector
  payload:
    fields_by_entity:
      - type: dict[str, list[str]]
        key: entity_name
        value: danh sách "entity.field" có trong lược đồ
  errors:
    - SchemaError            # lược đồ không nạp được (nội dung khai báo sai)
    - ConfigurationError     # thiếu tệp lược đồ hoặc tệp CSV nguồn (thêm 2026-11-07, cộng thêm)
  change_policy: chỉ thêm trường; không bỏ tên trường đang có
```

Ghi chú: U2 **không** biết truy vấn nào cần trường nào — tri thức đó thuộc U3. U5 nhận `query_id` từ lời gọi của nó và tự tra danh mục trường.

## C3 — U5 cung cấp nguồn đã chọn cho U3

```yaml
shared-schema:
  name: SourceSelection
  provider: u5-source-selector
  consumer: u3-query-rewriter
  payload:
    query_id: str
    selected_sources:
      - source_name: str
        tables: list[str]
        reason: str          # lý do chọn, tiếng Việt
    rejected_sources:
      - source_name: str
        reason: str          # lý do loại, tiếng Việt
    catalogue: SourceCatalogue  # thêm 2026-11-08, cộng thêm: bản C7 sau lần đề xuất, để U6 vẽ bảng
    missing_fields: list[str]   # thêm 2026-11-08, cộng thêm: chỉ có khi không chọn được nguồn
  errors:
    - NoSourceAvailableError # không nguồn nào đủ trường; mang thuộc tính catalogue và missing_fields
    - SchemaError            # thêm 2026-11-08: query_id không có trong ánh xạ; cấu hình sai ngay từ lần nạp
  change_policy: chỉ thêm trường; danh sách đã chọn không rỗng khi không có lỗi
```

## C4 — U3 cung cấp kết quả truy vấn cho U6

```yaml
shared-schema:
  name: QueryRunResult
  provider: u3-query-rewriter
  consumer: u6-integration-ui
  payload:
    plan_id: str
    template_id: str
    template_title: str        # nhãn hiển thị của truy vấn mẫu
    mediated_query_text: str
    rewrite_plan:
      - step: int
        mediated_entity: str
        source_table: str
        join_condition: str
    source_sql: str
    rows: list[dict[str, object]]
    row_count: int
    elapsed_ms: int
    kpi_definitions:          # để U6 hiển thị định nghĩa KPI dùng chung
      - kpi_id: str
        title: str
        formula: str
        revenue_definition: str
        unit: str
    kpi_comparison:
      - kpi_id: str
        group_key: str        # thêm 2026-11-08: khoá nhóm (danh mục/tháng/bang), "__all__" cho dòng tổng
        expected_value: float
        actual_value: float
        delta: float          # thêm 2026-11-08: expected - actual
        tolerance: float      # 0,01 cho tiền tệ; 0 cho số dòng; 0,01 cho phần trăm (thay 0.0 cũ)
        matches: bool
  errors:
    - QueryExecutionError    # SQL nguồn lỗi hoặc không chạy được
    - KpiMismatchError       # kết quả lệch quá dung sai
  partial:
    when: truy vấn chạy được nhưng một phần nguồn thiếu dữ liệu
    carries: phần thiếu và lý do; không hiển thị 0 thay cho dữ liệu thiếu
  change_policy: chỉ thêm trường; `rows`, `kpi_definitions`, `kpi_comparison` luôn có mặt, có thể rỗng
```

## C5 — U4 bàn giao kết quả ghép qua tệp

```yaml
shared-schema:
  name: LinkageResultFile
  provider: u4-record-linkage
  consumer: u6-integration-ui
  mechanism: tệp JSON trong data/, ghi ở tầng pipeline
  path: data/integration/linkage-<customer|seller>.json   # một tệp cho mỗi đối tượng
  payload:
    target_entity: str
    run_id: str
    computed_at: str           # ISO-8601 UTC
    threshold: 0.85
    summary:
      pairs_scored: int
      pairs_matched: int
      pairs_review: int
      pairs_skipped: int
      duplicate_groups: int    # số nhóm trùng — FR3.3
      correct_rate: float      # tỉ lệ ghép đúng so với customer_unique_id / seller_id
    pairs:
      - pair_id: str
        record_a: str
        record_b: str
        score: float
        decision: str          # Ghép | Xem lại
        is_correct: bool
    skipped:
      - skip_id: str
        record_a: str
        record_b: str
        missing_fields: list[str]
        reason: str
  errors:
    - LinkageResultMissingError  # tệp chưa được sinh — consumer hiện trạng thái rỗng kèm hướng dẫn chạy pipeline
    - LinkageResultInvalidError  # tệp không đọc được hoặc thiếu trường bắt buộc — consumer hiện trạng thái lỗi
  partial:
    when: một đối tượng có kết quả, đối tượng kia chưa
    carries: đối tượng thiếu và lý do
  change_policy: chỉ thêm trường; `summary` luôn có mặt
```

## C6 — U2 cung cấp dữ liệu lược đồ cho U6

```yaml
shared-schema:
  name: MediatedSchemaViewForUi
  provider: u2-mediated-schema
  consumer: u6-integration-ui
  payload:
    entities: list[MediatedEntity]
    mappings: dict[str, list[FieldMapping]]
    schema_kind: str
    elapsed_ms: int
  errors:
    - SchemaError
    - ConfigurationError     # thiếu tệp lược đồ hoặc tệp CSV nguồn (thêm 2026-11-07, cộng thêm)
  partial:
    when: thiếu một phần ánh xạ
    carries: thực thể thiếu và lý do
  change_policy: chỉ thêm trường
```

## C7 — U5 cung cấp bảng nguồn cho U6

```yaml
shared-schema:
  name: SourceCatalogueForUi
  provider: u5-source-selector
  consumer: u6-integration-ui
  payload:
    sources:
      - source_name: str
        coverage: str          # mô tả ngắn khả năng đáp ứng
        has_data: bool
        cost_level: int        # 1..5, thang tương đối
        latency_ms: int
        is_simulated: bool
    choices:                   # SourceChoice — FR4.2
      - query_id: str
        source_name: str
        is_selected: bool
        reason: str            # lý do chọn/loại, tiếng Việt
    partial_reason: str        # thêm 2026-11-08, cộng thêm: lý do danh mục đang "một phần"
    pending_query_id: str      # thêm 2026-11-08, cộng thêm: truy vấn đang chờ đề xuất
    query_fields: dict[str, tuple[str, ...]]  # thêm 2026-11-08, cộng thêm: truy vấn → trường cần (tuple giữ thứ tự)
  errors:
    - NoSourceAvailableError  # không nguồn nào đủ trường cho truy vấn đang chọn
    - SchemaError             # thêm 2026-11-08: hồ sơ cấu hình sai nội dung
    - ConfigurationError      # thêm 2026-11-08: thiếu tệp cấu hình hoặc khoá sai kiểu
  partial:
    when: chưa có kết quả đề xuất cho truy vấn đang chọn
    carries: lý do và truy vấn cần đề xuất
  change_policy: chỉ thêm trường; `is_simulated` luôn có để giao diện ghi chú nguồn mô phỏng
```

## C8 — U1 bàn giao tệp lược đồ đầu tiên cho U2

```yaml
shared-schema:
  name: InitialSchemaFile
  provider: u1-thin-slice
  consumer: u2-mediated-schema
  mechanism: tệp khai báo YAML trong config
  path: config/mediated-schema.yaml
  payload:
    schema_kind: GAV
    entities:                    # danh sách bản ghi, KHÔNG phải danh sách chuỗi
      - name: don_hang           # tên thực thể trung gian; lớp mã tương ứng là DonHang
        description: str
        source_tables: list[str]
        fields:                  # danh sách bản ghi, KHÔNG phải danh sách chuỗi
          - field_name: str      # tên trường trung gian
            source_table: str
            source_column: str
            data_type: str
            loaded: bool         # false = có ánh xạ nhưng lát cắt này không nạp
  change_policy: chỉ thêm thực thể/trường; không đổi tên thực thể hay tên khoá đang có
```

## C9 — U1 bàn giao khung tab cho U6

```yaml
shared-schema:
  name: InitialTabContract
  provider: u1-thin-slice
  consumer: u6-integration-ui
  mechanism: hàm dựng khung tab + tệp cấu hình
  payload:
    tab_id: "tich-hop"
    tab_label: "Tích hợp"
    card_ids: list[str]        # bốn thẻ, id ổn định để U6 mở rộng
    callback_ids: list[str]
    result_region_ids: list[str]   # vùng kết quả nằm trong thân tab, không phải thẻ
                                   # ("don-theo-thang": số đơn theo tháng của lát cắt)
  change_policy: chỉ thêm thẻ/callback/vùng; không đổi tên `tab_id`, `card_ids` hay `result_region_ids` đang có
```

**Bàn giao bắt buộc của C9:** U6 phải dựng **mọi** `result_region_ids` bên trong thân tab, phía trên lưới thẻ, và giữ chúng khi dựng lại phần thân tab. Một vùng kết quả không phải một `card_id`: nó không được đếm vào `card_ids` và không được thay bằng một thẻ thứ năm.

## Quy tắc sở hữu hợp đồng

- Mỗi hợp đồng do đơn vị **cung cấp** sở hữu; chỉ đơn vị đó sửa phần định nghĩa của mình. C6 và C7 tách riêng vì vậy, dù cùng phục vụ U6.
- Thay đổi phá vỡ (đổi nghĩa trường, xoá trường) không được phép trong đợt này; nếu buộc phải làm thì phải sửa cả consumer và test trong cùng thay đổi.
- Thay đổi cộng thêm (thêm trường) an toàn: consumer bỏ qua trường không biết.
- Mọi lỗi được ném bằng exception có kiểu và hậu tố `Error`, đặt trong `src/common/exceptions.py` cùng các exception hiện có; giao diện bắt và hiện trạng thái tương ứng, không hiện mã lỗi thô.
- C1, C2, C6 (do U2 sở hữu) khai hai kiểu lỗi: `SchemaError` cho nội dung khai báo sai và `ConfigurationError` cho tệp thiếu; consumer bắt **cả hai** và hiện trạng thái lỗi, không để ngoại lệ thoát ra ngoài ranh giới giao diện. Thay đổi này cộng thêm vào hợp đồng ngày 2026-11-07, không đổi nghĩa lỗi cũ.
- Mọi hợp đồng có kênh `partial`: khi chỉ có một phần dữ liệu, bên cung cấp nói rõ phần thiếu và lý do; bên nhận hiện trạng thái "một phần" và không thay dữ liệu thiếu bằng số 0.
- Tệp kết quả ghép (C5) là hợp đồng dữ liệu có phiên bản ngầm qua `run_id`; consumer không được giả định tệp tồn tại.

## Open questions

| Contract | Question | Blocks |
|---|---|---|
| C4 | `kpi_comparison` hiển thị trên màn hình viết lại truy vấn hay chỉ dùng trong test? | U6 |
| C1 | Khi thêm thực thể thứ tư ở đợt sau, `schema_kind` giữ `GAV` hay đổi sang `GLAV`? | U2 |
| C8 | Tệp lược đồ đặt trong `config/` hay cạnh `config.yaml` ở gốc repo? | U1, U2 |
