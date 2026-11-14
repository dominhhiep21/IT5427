# Security Requirements — u2-features-and-models

Đơn vị: `u2-features-and-models` (kind `library`). Nguồn: `../functional-design/{functional-spec,rules,entities}.md`, `../../../inception/requirements-analysis/requirements.md`, `../../../inception/contract-design/contract-summary.md` (C1, C2, C2b, C3), mã thật `src/analytics/{model,service,report}.py`, `src/config.py`, `config.yaml`, `.gitignore`.

Đơn vị này không có bề mặt mạng, không xác thực người dùng, không thêm thông tin định danh cá nhân nào. Ba thứ nó thực sự phải bảo vệ là: **mart chỉ đọc** (đơn vị này đổi câu truy vấn dựng khung, nên một phép join sai là cách phá dữ liệu gần nhất), **ranh giới tin cậy của tệp `pickle`** (định dạng nạp được mã, không phải định dạng dữ liệu), và **nội dung dòng dữ liệu không rò ra thông điệp lỗi hay log**.

Bảy mục dưới đây là kiểm soát riêng của dự án này. Chúng không mang mã `NFRx.y`, trừ `SEC2.1` — mục đó là cách đơn vị này giữ `NFR4`, nên nó dẫn mã NFR gốc.

## SEC2.1 — Mart chỉ đọc; đơn vị này không đổi một dòng nào của mart (NFR4)

**NFR gốc:** NFR4 — "5 KPI baseline, 9 bảng nguồn, 9 bảng mart, 11 view, khớp tuyệt đối".

**Yêu cầu:** mọi lần đọc mart của đơn vị này đi qua `AnalyticsService._connect()` → `ConnectionFactory.read_only()` (`src/integrate/connections.py:24-25`), tức kết nối DuckDB mở với `read_only=True`. Đơn vị này **không** thêm câu ghi, không thêm DDL, không gọi `integrate_all`, và không sửa một tệp nào dưới `src/integrate/`, `src/clean/`, `src/ingest/`, `src/quality/`.

**Vì sao đây là yêu cầu an toàn của riêng U2:** đơn vị này là đơn vị **đổi câu truy vấn dựng khung** — thêm ba cột nguồn, đổi grain từ `order_id` sang `order_id + order_item_id`. Một phép join 1:N không gộp trước sẽ nhân dòng, và hệ quả không phải một con số xấu mà là **một mart khác**. Kết nối chỉ đọc là hàng rào vật lý: nó biến "đừng ghi vào mart" từ một quy ước thành một lỗi `duckdb` nếu ai đó thử.

**Kiểm:**
- `grep -rn "read_only=False" src/analytics/` không có kết quả; `grep -rn "INSERT\|CREATE\|DELETE\|UPDATE" src/analytics/` không có kết quả.
- `git diff --stat` của đơn vị này không chạm tệp nào dưới `src/integrate/`, `src/clean/`, `src/ingest/`, `src/quality/`.
- Test `slow` `tests/integration/test_u2_model_end_to_end.py` chạy `run --stage all` rồi `run --stage stats`; trong lần chạy đó `KpiReconciler` (5 KPI) và `StarSchemaValidator` (9 check số dòng) phải xanh. Hai cổng này là phép kiểm của NFR4, không phải của U2 — nhưng một mart bị U2 làm hỏng sẽ đỏ ở đúng đó.

**Phép kiểm quần thể không thay phép kiểm mart.** Bốn bộ đếm `CohortCounts` — 110.195 dòng hàng / 96.476 đơn / 8.713 dòng trễ / 2 đơn thiếu carrier date — khẳng định **khung huấn luyện** đếm đúng quần thể (BR2.1). Chúng không nói gì về số dòng của 9 bảng mart và 11 view; hai sự thật đó vẫn do `StarSchemaValidator` giữ. Gộp chúng thành một phép kiểm là tự bỏ một cổng.

## SEC2.2 — Tệp mô hình là sản phẩm sinh ra, nằm ngoài git

**Yêu cầu:** tệp mô hình (`data/models/logistic.pkl` và `logistic.json`) **không** được commit. Không thêm ngoại lệ nào cho `data/models/` vào `.gitignore` và không dùng `git add -f`.

**Vì sao:** `data/` đã bị chặn ở `.gitignore:7`, nên `data/models/` thừa hưởng đúng quy tắc đó — việc phải làm ở đây là **giữ** nó, không phải tạo nó. Ba lý do cụ thể:
1. Tệp gắn với phiên bản thư viện đã sinh ra nó (C2b), nên nó không phải định dạng trao đổi giữa các máy; commit nó là biến một artefact cục bộ thành thứ người khác tưởng dùng được.
2. Nó là **đầu ra**, cùng loại với `data/marts/` và `data/reports/`; đưa đầu ra vào git là tạo nguồn sự thật thứ hai cho cùng một mô hình.
3. Một tệp `pickle` đi qua git là một tệp `pickle` **có nguồn khác ngoài pipeline này** — đúng thứ mà SEC2.3 phải chặn.

**Kiểm:**
- `git check-ignore -v data/models/logistic.pkl` in ra một quy tắc khớp (`.gitignore:7:data/`).
- `git ls-files data/models` không in gì.
- Test cấu hình khẳng định `config.models_dir` nằm dưới `config.data_dir`, và `load_config` tạo thư mục đó rỗng (A-04: thư mục vắng là trạng thái bình thường, không phải lỗi).

## SEC2.3 — `pickle` là định dạng tin cậy nội bộ, và rủi ro được nêu thẳng

**Rủi ro, nói không giảm nhẹ:** `pickle.load` không phải bộ đọc dữ liệu. Nó **dựng lại đối tượng Python** theo chỉ dẫn ghi trong tệp, nên nạp một tệp `pickle` không rõ nguồn là **thực thi mã tuỳ ý** với quyền của tiến trình đang nạp. Không có bước "kiểm nội dung trước khi nạp": cái giá của việc kiểm là đã nạp rồi.

**Biện pháp — bốn điều, và chỉ bốn điều này:**
1. Chỉ nạp tệp do **chính pipeline này** sinh ra, trong `data/models/`. `load_model(models_dir)` **nhận thư mục qua tham số** đúng như C2b (`load_model(models_dir) -> FittedModel | None`), và tham số đó do `stages.py` truyền vào từ `AppConfig.models_dir` (SEC2.7) — `ModelPersistence` **không** tự đọc `AppConfig`, không tự dựng đường dẫn. Điều bị cấm là nhận đường dẫn từ **nguồn khác** cấu hình, không phải việc có tham số.
2. `load_model` **không** nhận đường dẫn từ dòng lệnh, từ biểu mẫu dự phòng của C3, từ nội dung tệp, hay từ biến môi trường.
3. Không tải từ mạng: đường mô hình không import `requests`/`urllib`/`http`, không có URL nào trong `src/analytics/`.
4. Tệp vắng → `None` (không ném, A-04); tệp có nhưng nạp lỗi → `ModelError` với thông điệp của mình, không để ngoại lệ thô của `pickle` lọt ra giao diện.

**Điều mục này không làm, và không nên làm:** không sandbox tiến trình nạp, không ký tệp, không kiểm hash. Trong phạm vi hiện tại — một người, một máy, một pipeline vừa ghi vừa đọc — ba thứ đó là nghi thức không mua được gì. Chúng trở thành bắt buộc ngay khi có **nguồn tệp thứ hai** (tải về, chia sẻ giữa máy, đính kèm trong issue); lúc đó mục này phải được viết lại, không được nới bằng cách giữ nguyên câu chữ.

**Kiểm:**
- `grep -rn "pickle.load" src/` trả về đúng **một** chỗ, trong mô-đun `ModelPersistence`.
- `grep -rn "requests\|urllib\|http" src/analytics/` không có kết quả.
- Unit test: `load_model` với thư mục vắng → `None`; với tệp chứa byte rác → `ModelError` (kiểm cả kiểu ngoại lệ, không chỉ "có ném").

## SEC2.4 — Không có bí mật nào trong mã, cấu hình hay báo cáo

**Yêu cầu:** không thêm khoá API, token, chuỗi kết nối có mật khẩu, tệp `.env`, hay lần đọc `os.environ` nào cho đường mô hình. `scikit-learn` và `pickle` không cần khoá; mart là tệp cục bộ.

**Vì sao phải nói:** một mô hình học máy thường kéo theo thói quen "lấy khoá từ biến môi trường cho tiện". Ở đây không có dịch vụ nào để xác thực, nên thêm biến môi trường là thêm bề mặt cấu hình không có người dùng.

**Kiểm:** `grep -rniE "(api[_-]?key|secret|password|token|bearer)" src/analytics/` không có kết quả; `requirements.txt` vẫn đúng **12** gói ghim, không có gói xác thực hay gói gọi mạng.

## SEC2.5 — Không có bề mặt mạng: U2 không thêm route, không mở cổng

**Yêu cầu:** `src/analytics/` không import `dash`, không đăng ký callback, không bind cổng. Đơn vị này được gọi **trong cùng tiến trình** theo C3, nên "bề mặt" của nó là một chữ ký hàm, không phải một endpoint. `config.yaml` giữ `dashboard.host: 127.0.0.1`.

**Vì sao:** một route dự đoán là quyết định phạm vi đã bị loại (`requirements.md` `## Out of scope`: "API dự đoán (endpoint gọi từ ngoài)"). Thêm nó ở đây sẽ vừa ra ngoài phạm vi, vừa tạo một bề mặt không ai kiểm.

**Kiểm:** `grep -rn "from dash\|import dash\|callback" src/analytics/` không có kết quả; số callback của dashboard do U3 sở hữu và test `tests/unit/test_dashboard_smoke.py` canh — đơn vị này không được làm con số đó đổi.

## SEC2.6 — Thông điệp lỗi và log không mang nội dung dòng dữ liệu

**Yêu cầu:** `ModelError` chỉ nêu **tên trường**, **tên cột**, **số đếm**, hoặc **mã luật** (`BR2.x`). Không nêu giá trị ô, không nêu `order_id`, không nêu mã bưu chính, không dán cả dòng dữ liệu.

**Vì sao:** log JSONL ghi ra `logs/` và thường được chia sẻ nguyên tệp khi báo lỗi. Một thông điệp chứa giá trị người dùng vừa nhập ở biểu mẫu, hoặc một dòng hàng thật, là rò rỉ ra ngoài tab — nơi duy nhất được phép hiện dữ liệu đó.

**Kiểm:**
- `score_item` thiếu `customer_state` → thông điệp chứa `customer_state` và **không** chứa giá trị của mười trường còn lại. Test đơn vị khẳng định cả hai vế; vế thứ hai mới là vế canh rò rỉ.
- `validate_counts` và các kiểm quần thể: test đơn vị khẳng định thông điệp chỉ gồm tên check và các số (`model.py:299-305` đang đúng hình dạng này).
- Chỗ duy nhất hôm nay ném ngoại lệ trần trong đường này là `service.py:386` (`ValueError("Bảng huấn luyện nhân dòng…")`) — thông điệp không mang dữ liệu, nhưng đơn vị này đổi sang `ModelError` (BR2.1) để giao diện bắt được; đổi kiểu, **không** thêm nội dung vào chuỗi.

## SEC2.7 — Đường dẫn lấy từ `AppConfig`, không từ đầu vào người dùng

**Yêu cầu:** `models_dir` là trường **mới** của `AppConfig` (frozen dataclass), đọc từ khoá `models_dir` trong `config.yaml`, mặc định `data/models`; thêm vào danh sách thư mục mà `load_config` tạo sẵn. Đường dẫn mô hình được dựng theo đúng hình dạng của `report_path` (`report.py:242-245`): `Path(config.models_dir) / <tên tệp cố định>`.

**Vì sao:** đây là kiểm soát chống ghi/đọc ngoài ý muốn. Một đường dẫn nhận từ dòng lệnh có thể trỏ vào `dataset/` hoặc ra ngoài workspace; đường dẫn cố định trong cấu hình thì không — và nó là điều kiện để SEC2.3 (1) đứng vững.

**Kiểm:**
- Mọi đường dẫn của U2 lấy từ `AppConfig`: `grep -n "models_dir" src/analytics/` chỉ ra **đúng** chỗ dựng `Path(models_dir) / <tên tệp cố định>` trong `ModelPersistence`, và `models_dir` đến từ `AppConfig.models_dir` do `stages.py` truyền vào (SEC2.3). Không có chỗ nào trong `src/analytics/` dựng đường dẫn từ tham số dòng lệnh hay từ dữ liệu.
- `Path(...)` đang có trong `report.py` là **hợp lệ**, không phải vi phạm: `:245` `Path(config.reports_dir) / REPORT_FILE_NAME`, `:255` `Path(writer.run.temp_dir) / …`, `:314` `Path(config.logs_dir)` / `Path(config.temp_dir)`, và `:273`/`:322` `Path(path)` trên tệp tạm do chính `report.py` tạo ra rồi đọc lại để kiểm. Vì vậy phép kiểm ở đây nhắm **đường dẫn mô hình**, không `grep Path(` toàn thư mục — làm vậy sẽ đỏ trên mã đúng.
- Test cấu hình: `load_config()` cho `config.models_dir == workspace_root / "data" / "models"`; `AppConfig` vẫn frozen (gán thuộc tính ném `FrozenInstanceError`).
- `grep -rn "models_dir" src/pipeline/cli.py` không có kết quả — không có cờ dòng lệnh nào cho đường dẫn mô hình.

## Điều tài liệu này không hứa

Không có mã hoá at-rest, không có kiểm toán truy cập, không có cách ly tiến trình, không có chống thay đổi tệp (tamper detection), không có sao lưu. Dự án chạy từ mã nguồn trên máy một người, không có dịch vụ công khai và không có người dùng thứ hai; ba thứ trên chỉ có nghĩa trong một hệ thống khác. Điều duy nhất tài liệu này hứa là: mart không bị ghi, tệp mô hình chỉ đến từ pipeline này, và thông điệp lỗi không mang dữ liệu.

## Ánh xạ NFR gốc sang yêu cầu chi tiết của đơn vị

Mỗi NFR của Requirements Analysis được chi tiết hoá thành một yêu cầu con; cột giữa là mã con dùng cho truy vết của các stage sau.

| NFR gốc | Mã con | Yêu cầu chi tiết |
|---|---|---|
| `NFR1` | `NFR1.1` | Tầng `stats` trong **300 s**; `STAGE_BUDGET_SECONDS` giữ 300, không nới. |
| `NFR2` | `NFR2.1` | Bước huấn luyện hai mô hình **< 240 s**; `TRAIN_BUDGET_SECONDS` từ 900 xuống **240**. |
| `NFR3` | `NFR3.1` | Cổng phủ `--cov-fail-under=80` tại `ci.yml:53` giữ nguyên trên toàn bộ bộ test. |
| `NFR4` | `NFR4.1` | U2 **không** đổi mart: 5 KPI, 9 bảng mart, 11 view giữ nguyên; mart chỉ đọc — xem `SEC2.1`. |
| `NFR5` | `NFR5.1` | Mốc sàn `max(MODEL_AUC_FLOOR, baseline_auc)`: U2 giao hằng `MODEL_AUC_FLOOR` (**0,55**) và hàm thuần `beats_floor`; test `slow` do **U3** viết. Ngoại lệ có chủ đích với luật "không đặt AUC làm kỳ vọng test" — phải ghi qua nghi thức learnings và sửa `project.md` `## Forbidden`, nếu không thì mốc sàn **không hợp lệ**. |
| `NFR6` | `NFR6.1` | `N/A` — đơn vị không có bề mặt giao diện; tiếp cận thuộc `u3-prediction-ui`. |
