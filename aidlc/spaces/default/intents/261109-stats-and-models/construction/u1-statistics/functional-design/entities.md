# Entities — u1-statistics

Nguồn: `../../../inception/units-generation/unit-of-work.md`, `../../../inception/domain-design/components.md`, `../../../inception/contract-design/contract-summary.md` (C1, C2 — phiên bản hợp đồng 2), `../../../inception/requirements-analysis/requirements.md`, `../../../inception/user-stories/stories.md` (US1.1, US3.1, US5.1), `functional-design-questions.md`.

Các thực thể dưới đây hiện thực hoá C1 và C2. Trường nào trong hợp đồng khai là `dict` thì ở đây được chốt tên khoá cụ thể; U2 và U3 đọc đúng những tên khoá này, nên đổi tên khoá là thay đổi phá vỡ hợp đồng.

```yaml
entities:
  - name: AnalysisReport
    description: Tệp báo cáo dùng chung, gốc của cả hai khối kết quả
    owner: U1 (khung) — U2 sở hữu khối mô hình
    attributes:
      - { name: version, type: integer, required: true, constraint: "bằng REPORT_VERSION, hiện là 2" }
      - { name: generated_at, type: string, required: true, constraint: "ISO 8601 UTC" }
      - { name: stats, type: StatsBlock, required: false, default: null }
      - { name: model, type: ModelBlock, required: false, default: null, note: "do U2 ghi, U1 chỉ đọc để kiểm" }
    constraints:
      - "stats và model không được cùng null: tệp chỉ được ghi khi ít nhất một khối có mặt"
    relationships:
      - { to: StatsBlock, cardinality: "1 → 0..1", direction: "AnalysisReport chứa StatsBlock" }
      - { to: ModelBlock, cardinality: "1 → 0..1", direction: "AnalysisReport chứa ModelBlock" }

  - name: StatsBlock
    description: Toàn bộ kết quả kiểm định thống kê của một lần chạy
    attributes:
      - { name: generated_at, type: string, required: true }
      - { name: alpha, type: float, required: true, constraint: "0 < alpha < 1", default: 0.05 }
      - { name: confidence, type: float, required: true, constraint: "= 1 - alpha", default: 0.95 }
      - { name: late_rate, type: ProportionResult, required: true }
      - { name: comparisons, type: "list[ComparisonResult]", required: true, constraint: "rỗng khi chưa đủ hai bang, ngược lại đúng một phần tử" }
      - { name: correlation, type: "CorrelationResult | null", required: false, default: null }
      - { name: group_test, type: "GroupTestResult | null", required: false, default: null }
      - { name: seasonal, type: "SeasonalResult | null", required: false, default: null }
      - { name: skipped, type: "list[SkipEntry]", required: true, constraint: "rỗng nghĩa là mọi kiểm định đều chạy được" }
    constraints:
      - "alpha và confidence là một sự thật: confidence luôn bằng 1 - alpha, cả hai lấy từ một hằng số"
      - "mỗi tên trong SkipEntry.test xuất hiện tối đa một lần trong skipped"
    relationships:
      - { to: ProportionResult, cardinality: "1 → 1", direction: "StatsBlock chứa late_rate" }
      - { to: ComparisonResult, cardinality: "1 → 0..n", direction: "StatsBlock chứa comparisons" }
      - { to: SkipEntry, cardinality: "1 → 0..n", direction: "StatsBlock chứa skipped" }

  - name: ProportionResult
    description: Một tỉ lệ kèm khoảng tin cậy
    attributes:
      - { name: successes, type: integer, required: true, min: 0 }
      - { name: total, type: integer, required: true, min: 1 }
      - { name: rate, type: float, required: true, min: 0, max: 1, note: "phân số 0–1, không phải phần trăm" }
      - { name: ci_low, type: float, required: true, min: 0, max: 1 }
      - { name: ci_high, type: float, required: true, min: 0, max: 1 }
    constraints:
      - "ci_low <= rate <= ci_high"
      - "successes <= total"

  - name: ComparisonResult
    description: So sánh hai tỉ lệ giữa hai bang, kèm số đơn không tham gia được
    attributes:
      - { name: first, type: string, required: true, note: "mã bang 2 ký tự" }
      - { name: second, type: string, required: true }
      - { name: difference, type: float, required: true, min: -1, max: 1 }
      - { name: z, type: float, required: true }
      - { name: p_value, type: float, required: true, min: 0, max: 1 }
      - { name: ci_low, type: float, required: true }
      - { name: ci_high, type: float, required: true }
      - { name: significant, type: boolean, required: true, note: "= p_value < alpha" }
      - { name: excluded, type: integer, required: true, min: 0, note: "tổng số đơn đã giao của các bang không đạt ngưỡng 100 đơn" }
    constraints:
      - "first khác second"
      - "comparisons mang tối đa một phần tử ở đợt này: đúng cặp bang cao nhất và thấp nhất. Kiểu là danh sách vì C1 khai `list[dict]`, không phải để chứa nhiều cặp."
      - "excluded là con số toàn cục của lần chạy, nên khi chỉ có một phần tử thì không có chuyện lặp giá trị"

  - name: CorrelationResult
    description: Tương quan Pearson giữa giá hàng và phí vận chuyển
    attributes:
      - { name: r, type: float, required: true, min: -1, max: 1 }
      - { name: n, type: integer, required: true, min: 4, note: "tối thiểu 4 vì se = 1/sqrt(n-3) không xác định ở n = 3" }
      - { name: ci_low, type: float, required: true, min: -1, max: 1 }
      - { name: ci_high, type: float, required: true, min: -1, max: 1 }
    constraints:
      - "ci_low <= r <= ci_high"

  - name: GroupTestResult
    description: Kết quả một phép kiểm định nhóm trên bảng dự phòng
    attributes:
      - { name: test, type: string, required: true, allowed: ["chi_square_region_late"], note: "tên phép kiểm định đã dùng" }
      - { name: statistic, type: float, required: true }
      - { name: p_value, type: float, required: true, min: 0, max: 1 }
      - { name: dof, type: integer, required: true, min: 1 }
      - { name: min_expected, type: float, required: true, note: "ô kỳ vọng nhỏ nhất, để chứng minh điều kiện áp dụng đã đạt" }

  - name: SeasonalResult
    description: Phân rã mùa vụ chuỗi doanh thu theo tháng
    attributes:
      - { name: revenue_definition, type: string, required: true, note: "lấy nguyên văn từ REVENUE_DEFINITION" }
      - { name: method, type: string, required: true, allowed: ["classical_additive_12"], note: "tên phương pháp phân rã đã dùng" }
      - { name: period, type: integer, required: true, default: 12 }
      - { name: months, type: "list[str]", required: true, constraint: "YYYY-MM, liên tục, đã điền 0 cho tháng thiếu" }
      - { name: observed, type: "list[float]", required: true, constraint: "cùng độ dài với months" }
      - { name: trend, type: "list[float]", required: true, constraint: "cùng độ dài với months" }
      - { name: seasonal, type: "list[float]", required: true, constraint: "cùng độ dài với months" }
      - { name: residual, type: "list[float]", required: true, constraint: "cùng độ dài với months" }
    constraints:
      - "months có tối thiểu 24 phần tử và không thiếu tháng nào giữa hai đầu"
      - "trend được định nghĩa ở mọi vị trí, kể cả hai đầu chuỗi: trung bình động giữa có cửa sổ thu hẹp dần ở hai đầu thay vì bỏ trống"
      - "observed = trend + seasonal + residual tại mọi vị trí, và cả năm mảng cùng độ dài với months"

  - name: SkipEntry
    description: Một kiểm định không chạy được, kèm lý do
    attributes:
      - { name: test, type: string, required: true, allowed: ["state_comparison", "correlation", "group_test", "seasonal"] }
      - { name: reason, type: string, required: true, min_length: 1, note: "câu chữ tiếng Việt, nêu điều kiện không đạt" }
    constraints:
      - "C1 khai năm tên; U1 chỉ sinh bốn. `late_rate` không bao giờ xuất hiện vì BR1.1 dừng cả tầng thay vì ghi null — đây là thu hẹp có chủ đích, không phải thiếu sót, và U2/U3 chỉ cần xử lý bốn tên còn lại"

  - name: ReportView
    description: Kết quả một lần đọc báo cáo, luôn có trạng thái
    attributes:
      - { name: status, type: string, required: true, allowed: ["rong", "day-du", "mot-phan", "loi"] }
      - { name: report, type: "AnalysisReport | null", required: false, default: null }
      - { name: missing, type: "tuple[str, ...]", required: true, default: "()", allowed_items: ["stats", "model"] }
      - { name: message, type: string, required: true, note: "câu chữ tiếng Việt; rỗng khi day-du" }
    constraints:
      - "status = rong thì report là null và missing rỗng"
      - "status = day-du thì report khác null và missing rỗng"
      - "status = mot-phan thì report khác null và missing khác rỗng"
      - "status = loi thì report là null và message khác rỗng"
```

## Tóm tắt tập thực thể

| Thực thể | Vai | Ghi chú |
|---|---|---|
| `AnalysisReport` | Gốc của tệp báo cáo | U1 giữ khung, U2 ghi khối `model` |
| `StatsBlock` | Kết quả thống kê | Chứa đúng một `late_rate`, danh sách `comparisons`, ba kết quả tuỳ chọn, và `skipped` |
| `ProportionResult` | Tỉ lệ + khoảng tin cậy | Dùng cho `late_rate` |
| `ComparisonResult` | So sánh hai bang | Mang thêm `excluded` |
| `CorrelationResult` | Tương quan giá–phí | `r`, `n`, khoảng Fisher |
| `GroupTestResult` | Kiểm định nhóm | `dof` và `min_expected` chứng minh điều kiện áp dụng |
| `SeasonalResult` | Phân rã mùa vụ | Mang `revenue_definition` và `method` |
| `SkipEntry` | Lý do bỏ qua | Chỉ bốn kiểm định tuỳ chọn mới có mặt ở đây |
| `ReportView` | Kết quả đọc | Bốn trạng thái đóng, gồm `rong` |

## Quan hệ

- `AnalysisReport` chứa 0..1 `StatsBlock` và 0..1 `ModelBlock`, đúng C1.
- `StatsBlock` chứa đúng một `ProportionResult`, 0..n `ComparisonResult`, 0..1 của mỗi kết quả còn lại, và 0..n `SkipEntry`.
- `ReportView` trỏ tới 0..1 `AnalysisReport`.

## Ghi chú về hợp đồng

- Tên trường ở đây trùng C1/C2 từng chữ. Khác biệt duy nhất là các `dict` của hợp đồng được chốt khoá cụ thể (`late_rate` → `ProportionResult`, …), không thêm trường nào. [Q1]
- `revenue_definition` nằm trong `SeasonalResult` — nơi duy nhất có tiền — để mọi KPI tiền đều đi kèm định nghĩa doanh thu, đúng quy tắc đã chốt của dự án. [Q2]
- `ModelBlock` do U2 sở hữu; U1 chỉ đọc nó để kiểm `mot-phan` và để ghi tệp mà không làm mất khối của U2.
