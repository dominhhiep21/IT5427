# Contract Summary — Báo cáo phân tích dùng chung

Nguồn: `../units-generation/unit-of-work.md`, `../units-generation/unit-of-work-dependency.md`, `../domain-design/components.md`, `../requirements-analysis/requirements.md`, và `contract-design-questions.md`.

Phiên bản hợp đồng: **2**. Bản 1 đã bị thay thế bởi cùng tệp này; lý do đổi ở mục "Chính sách thay đổi".

## Bảng hợp đồng

| Mã | Biên | Bên cung cấp | Bên dùng | Cơ chế | Chủ sở hữu |
|---|---|---|---|---|---|
| C1 | U1 → U2 | U1 | U2 | Mô-đun Python dùng chung (kiểu dữ liệu + hàm ghi) | U1 giữ khung và khối thống kê [Q2] |
| C2 | U1 → U3 | U1 | U3 | Mô-đun Python dùng chung (hàm đọc + kiểu kết quả) | U1 [Q2] |
| C3 | U2 → U3 | U2 | U3 | Khối mô hình trong cùng kiểu báo cáo | U2 [Q2] |

## C1 — Kiểu báo cáo và hàm ghi

```python
# src/analytics/report.py (U1 sở hữu khung, U2 bổ sung kiểu khối mô hình)
REPORT_VERSION = 2

@dataclass(frozen=True)
class SkipEntry:
    test: str      # "late_rate" | "state_comparison" | "correlation" | "group_test" | "seasonal"
    reason: str

@dataclass(frozen=True)
class ComparisonResult:
    first: str
    second: str
    difference: float
    z: float
    p_value: float
    ci_low: float
    ci_high: float
    significant: bool
    excluded: int          # tổng số đơn đã giao của các bang bị loại

@dataclass(frozen=True)
class StatsBlock:
    generated_at: str
    alpha: float
    confidence: float
    late_rate: dict
    comparisons: list[ComparisonResult]
    correlation: dict | None
    group_test: dict | None
    seasonal: dict | None
    skipped: list[SkipEntry]

@dataclass(frozen=True)
class ModelBlock:
    target: str
    split: dict
    auc: float
    threshold: float
    precision: float
    recall: float
    counts: dict

@dataclass(frozen=True)
class AnalysisReport:
    version: int
    generated_at: str
    stats: StatsBlock | None
    model: ModelBlock | None

def write_report(config: AppConfig, report: AnalysisReport, writer: AtomicWriter | None = None) -> Path: ...
```

Hợp đồng:

- `version` là số nguyên, tăng khi cấu trúc đổi; giá trị hiện hành là `2`.
- Thiếu một khối thì trường đó là `null`, không bỏ trường. [Q3]
- `skipped` là **danh sách**, không phải dict, và mỗi phần tử là một cặp `{test, reason}`. `test` dùng đúng một trong năm tên cố định ở trên, nên cùng một tên không xuất hiện hai lần; danh sách rỗng nghĩa là mọi kiểm định đều chạy được. [Q4][Q6]
- `excluded` nằm trong từng `ComparisonResult`: đó là **tổng số đơn đã giao** của các bang không đạt ngưỡng 100 đơn và vì thế không tham gia so sánh. Trường này luôn có mặt, kể cả khi không bang nào bị loại (giá trị `0`). [Q7]
- `late_rate` là trường bắt buộc, nên một báo cáo chỉ tồn tại khi có ít nhất một đơn đã giao; không có đơn nào thì tầng `stats` thất bại và không ghi tệp.
- Mọi trường số thực đã được làm tròn theo quy tắc của U1 trước khi ghi.

### Điều chỉnh sau khi thi công

Khi dựng `src/analytics/report.py`, bốn trường mà bản đặc tả khai là `dict` được viết thành dataclass cụ thể (`ProportionResult`, `ComparisonResult`, `CorrelationResult`, `GroupTestResult`) và `seasonal` thành `SeasonalResult`. Đây là **cùng một hình dạng dữ liệu**, chỉ khác cách khai kiểu; không thêm hay bớt trường nào trong tệp JSON. `ModelBlock` giữ đúng bảy trường C1 khai.

`write_report` nhận `config` để lấy `reports_dir` từ `AppConfig` — yêu cầu SEC-5 cấm nhận đường dẫn từ dòng lệnh — và trả `Path` của tệp vừa ghi. Bản đặc tả đầu tiên khai `write_report(report, path) -> None`; chữ ký đã đổi trước khi U2 hay U3 viết dòng nào, nên `REPORT_VERSION` giữ nguyên `2` thay vì tăng lên `3` cho một hình dạng chưa ai đọc.

## C2 — Hàm đọc và bốn trạng thái

```python
@dataclass(frozen=True)
class ReportView:
    status: str          # "rong" | "day-du" | "mot-phan" | "loi"
    report: AnalysisReport | None
    missing: tuple[str, ...]
    message: str

def read_report(path: Path) -> ReportView: ...
```

Hợp đồng:

| Trạng thái | Điều kiện | `report` | `missing` |
|---|---|---|---|
| `rong` | Tệp chưa tồn tại | `None` | `()` |
| `day-du` | Đọc được và có đủ hai khối `stats` và `model` | báo cáo | `()` |
| `mot-phan` | Đọc được nhưng thiếu ít nhất một khối (`"stats"`, `"model"`) | báo cáo | tên khối thiếu |
| `loi` | Tệp hỏng, không đọc được, thiếu trường bắt buộc, hoặc `version` khác `REPORT_VERSION` | `None` | `()` |

- `rong` là trạng thái **rỗng**, không phải lỗi: nó là giá trị máy đọc được để tab dựng vùng "chưa có báo cáo". [Q4][Q8]
- `loi` dành riêng cho tệp có mà không dùng được. Tệp phiên bản 1 trả `loi` với thông điệp nêu rõ phải chạy lại tầng `stats`. [Q8]
- Hàm đọc không ném ngoại lệ ra ngoài: mọi hỏng hóc biểu hiện thành `ReportView`. [Q4]

## C3 — Khối mô hình

Hợp đồng: `split` gồm `train_start`, `train_end`, `test_start`, `test_end`, `train_n`, `test_n`; `counts` gồm `flagged`, `not_flagged`, `total`, `threshold_method`, `auc_below_target`; `threshold` là số thực trong (0, 1); `target` nêu tên cột mục tiêu dạng chuỗi. U2 chịu trách nhiệm các trường này; U3 chỉ đọc và không suy diễn thêm. [Q2]

Hai khoá cuối của `counts` không phải số đếm mà là metadata bắt buộc: `threshold_method` cho biết ngưỡng đến từ đâu (FR2.4 đòi), `auc_below_target` cho biết mô hình có đạt mốc 0,70 hay không (US2.1 đòi). Chúng nằm trong `counts` thay vì hai trường mới để `REPORT_VERSION` giữ nguyên 2 — U3 phải đọc hai khoá này chứ không được tính lại.

## Hành vi lỗi ở biên

Các đơn vị gọi hàm trong cùng tiến trình, không có mạng, nên không có thời gian chờ hay thử lại. [Q5] Lỗi ghi tệp ném ra ở biên CLI của tầng `stats`; lỗi đọc tệp biểu hiện thành `loi` trong `ReportView`, không ném.

## Chính sách thay đổi

- **Ai sở hữu:** C1 và C2 thuộc U1; C3 thuộc U2 (phần khối mô hình trong C1 do U2 bổ sung). U3 là bên đọc, không sở hữu đặc tả nào. [Q2]
- **Thay đổi phá vỡ:** đổi tên, bỏ, hoặc đổi kiểu một trường; đổi nghĩa của một trạng thái — phải tăng `REPORT_VERSION` và cập nhật đồng thời ba nơi: kiểu trong `report.py`, hàm đọc, và test của U3. Một thay đổi phá vỡ không tăng phiên bản bị coi là lỗi hợp đồng. [Q3]
- **Thay đổi cộng thêm:** thêm một trường **tuỳ chọn** (có giá trị mặc định, hoặc `None` được chấp nhận) thì không cần tăng phiên bản; bên đọc bỏ qua trường lạ. Thêm một trường **bắt buộc** thì phải tăng phiên bản, vì tệp cũ không thoả hợp đồng mới.
- **Vì sao lên 2:** `skipped` và `excluded` là trường bắt buộc, nên tệp phiên bản 1 không còn hợp lệ và `REPORT_VERSION` phải là `2`. [Q6][Q7][Q8]

## Câu hỏi mở

Không còn điểm hợp đồng nào chưa chốt. Hai điểm từng chặn Functional Design của U1 — chỗ ghi lý do bỏ qua và trạng thái rỗng — đã được giải bằng `skipped`/`excluded` ở C1 và `rong` ở C2.
