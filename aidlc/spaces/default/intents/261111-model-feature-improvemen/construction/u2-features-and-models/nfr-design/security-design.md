# Security Design — u2-features-and-models

Đơn vị: `u2-features-and-models` (kind `library`). Nguồn: `../nfr-requirements/security-requirements.md` (SEC2.1–SEC2.7), `../functional-design/{functional-spec,rules,entities}.md` (W1–W6, `feature_contract`, BR2.1–BR2.12), `../../../inception/contract-design/contract-summary.md` (C2, C2b, C3), mã thật `src/analytics/{model,service,report}.py`, `src/pipeline/{stages,cli}.py`, `src/config.py`, `src/common/io.py`.

Đây là **thiết kế**, không phải mã. Mỗi mục nói ba thứ: kiểm soát nằm ở đâu trong luồng W1–W6, **cái gì chặn**, và khi nó bị vi phạm thì chuyện gì xảy ra trên đĩa.

## Bối cảnh: bề mặt của U2 là hai tệp và một chữ ký hàm

U1 có một lời gọi HTTPS ra IBGE. U2 **không có lời gọi mạng nào**. Bề mặt thật của nó gồm: một hàm gọi **trong cùng tiến trình** (`score_item`, C3), và **hai** tệp trên đĩa — `data/reports/analysis.json` (U2 ghi, U3 đọc, C2) và `data/models/logistic.pkl` (U2 ghi, U3 nạp, C2b). Vì thế "an toàn" ở đây không phải xác thực hay phân quyền, mà là ba thứ: **mart chỉ đọc**, **biên tin cậy của `pickle`**, và **dòng dữ liệu không đi vào log**.

## SD2.1 — Mart chỉ đọc: hàng rào ở kết nối, không ở lời hứa (NFR4)

**Vị trí:** W1 bước 1, `AnalyticsService.training_frame` (`service.py:377-387`) — mọi lần đọc mart của tầng `stats`.

**Thiết kế:** `_connect()` (`service.py:84-85`) trả `ConnectionFactory(self.config).read_only()`; `read_only=True` ở `connections.py:25`. Đơn vị này không thêm câu ghi, không DDL, không gọi `integrate_all`, không sửa tệp nào dưới `src/integrate/`, `src/clean/`, `src/ingest/`, `src/quality/`.

**Cái gì chặn:** DuckDB từ chối lệnh ghi trên kết nối `read_only`. Ai thêm `INSERT`/`CREATE` vào `src/analytics/` sẽ nhận lỗi **lúc chạy** — ồn ào, và đó chính là điều muốn có: một lỗi rõ ràng thay vì một mart lặng lẽ khác.

**Giới hạn phải nói:** `read_only=True` là thuộc tính **của kết nối**, không phải của tệp. Nó không ngăn tiến trình khác ghi, không ngăn U2 mở một kết nối thứ hai có quyền ghi, và không ngăn `pandas.to_parquet` ghi đè `data/marts/*.parquet`. Hàng rào thứ hai là **không tồn tại đường nào**: không mô-đun nào trong `src/analytics/` tham chiếu `config.marts_dir` (chỉ `integrate` dùng).

**Kiểm:** `grep -rn "marts_dir" src/analytics/` rỗng; `grep -rn "read_only=False\|INSERT\|CREATE\|DELETE\|UPDATE" src/analytics/` rỗng; `git diff --stat` không chạm `src/{integrate,clean,ingest,quality}/`.

**Cổng của NFR4 không phải cổng của U2.** `StarSchemaValidator` và `KpiReconciler` chạy trong `integrate` (`pipeline.py:84,88`), **không** chạy trong `stats`. Chúng chỉ được chạm tới gián tiếp khi test `slow` của U2 chạy `run --stage all` trước `run --stage stats`. Nghĩa là: nếu U2 làm hỏng mart, chính `run --stage stats` **không** phát hiện — phát hiện nằm ở test.

## SD2.2 — Tệp mô hình là sản phẩm sinh ra; `.gitignore` là kiểm soát, không phải quy ước

**Vị trí:** W5 bước 4 (`ModelPersistence.save`).

**Thiết kế:** `data/models/` thừa hưởng `.gitignore:7` (`data/`). Không thêm ngoại lệ cho `data/models/`, không `git add -f`, không coi tệp mô hình là artefact phát hành.

**Cái gì chặn:** không có gì lúc chạy. Đây là kiểm soát **phát hiện**: `git check-ignore -v data/models/logistic.pkl` in ra `.gitignore:7:data/`; `git ls-files data/models` rỗng.

**Vì sao không chỉ là chuyện thẩm mỹ:** một tệp `pickle` nằm trong git là một tệp `pickle` **có nguồn khác pipeline này** khi người khác clone — mở đúng cái lỗ mà SD2.3 phải đóng. Ba lý do còn lại (gắn phiên bản thư viện, là đầu ra cùng loại với `data/marts/`, tạo nguồn sự thật thứ hai) ở `security-requirements.md` SEC2.2.

## SD2.3 — Biên tin cậy của `pickle`, và bốn thứ nó không có

**Vị trí:** W5 bước 4 (ghi) và bước 5 (nạp lại để kiểm) trong `run --stage stats`; và ở **tiến trình khác** khi U3 nạp qua C2b cho W6.

**Rủi ro, không giảm nhẹ:** `pickle.load` không phải bộ đọc dữ liệu — nó dựng lại đối tượng Python theo chỉ dẫn ghi trong tệp, nên nạp một tệp không rõ nguồn là **thực thi mã** với quyền của tiến trình đang nạp. Không có bước "kiểm nội dung trước khi nạp": cái giá của việc kiểm là đã nạp rồi.

**Thiết kế — bốn điều, đúng bốn:**

1. **Một chỗ nạp.** `pickle.load` chỉ có trong `ModelPersistence`; `grep -rn "pickle.load" src/` trả về đúng một kết quả. W5 bước 5 và U3 dùng **cùng** hàm đó, không có đường nạp thứ hai.
2. **Một chỗ ghi.** `save` chỉ được gọi từ W5 bước 4 của `run --stage stats`. Không lệnh con, không cờ, không script phụ (`TS2.10`).
3. **Thư mục đến từ tham số, tham số đến từ cấu hình.** `load_model(models_dir) -> FittedModel | None` đúng C2b; `models_dir` do `stages.py` truyền từ `AppConfig.models_dir`. `ModelPersistence` **không** đọc `AppConfig`, không dựng `Path` từ dòng lệnh, biến môi trường, nội dung tệp hay dữ liệu biểu mẫu.
4. **Không có đường mạng.** `src/analytics/` không import `requests`/`urllib`/`http`, không có URL nào.

**Trạng thái lỗi:** thư mục hoặc tệp vắng ⇒ `None`, không ném (A-04; máy mới clone là trạng thái bình thường). Tệp có mà nạp lỗi ⇒ `ModelError`.

**Một quyết định nhỏ nhưng thuộc mục này:** thông điệp **không** nội suy `str(exc)` của `pickle`. Nó ghi `type(exc).__name__` và tên tệp; ngoại lệ gốc giữ ở `__cause__` cho người gỡ lỗi tại chỗ. Lý do: payload là dữ liệu không tin cậy, và một chuỗi bên trong nó có thể chảy thẳng vào `logs/` (SD2.6) — tức là một tệp mô hình độc có thể điều khiển nội dung log.

**Giới hạn, nói thẳng:** **không** sandbox tiến trình nạp, **không** chữ ký số, **không** kiểm hash, **không** cách ly quyền. Trong phạm vi hiện tại — một người, một máy, một pipeline vừa ghi vừa đọc — ba thứ đầu không mua được gì. Chúng thành **bắt buộc** ngay khi xuất hiện một trong bốn điều:

- tệp mô hình đến từ **nguồn thứ hai** (tải về, chia sẻ giữa máy, đính kèm trong issue);
- có **tiến trình thứ hai** ghi `data/models/` (ví dụ một lệnh "train lại" riêng);
- `data/models/` nằm ở thư mục mà tài khoản khác ghi được;
- có đường **nhận đường dẫn mô hình từ ngoài** (CLI, API, biến môi trường).

Khi đó mục này phải được **viết lại**, không được nới bằng cách giữ nguyên câu chữ.

## SD2.4 — Không có bí mật nào trong đường mô hình

**Vị trí:** toàn bộ `src/analytics/`, `config.yaml`, `requirements.txt`.

**Thiết kế:** không khoá API, không token, không chuỗi kết nối có mật khẩu, không `.env`, không lần đọc `os.environ`. `scikit-learn` và `pickle` không cần khoá; mart là tệp cục bộ.

**Vì sao phải nói:** một mô hình học máy thường kéo theo thói quen "lấy khoá từ biến môi trường cho tiện". Ở đây không có dịch vụ nào để xác thực, nên thêm biến môi trường là thêm bề mặt cấu hình không có người dùng.

**Cái gì chặn:** không có cổng runtime, và đúng là không cần — không có gì để xác thực. Kiểm bằng phép đếm: `grep -rniE "(api[_-]?key|secret|password|token|bearer)" src/analytics/` rỗng; `requirements.txt` vẫn đúng **12** gói ghim, không có gói xác thực hay gói gọi mạng.

## SD2.5 — Không mở bề mặt mạng; bề mặt của U2 là một chữ ký hàm

**Vị trí:** W6, và toàn bộ `src/analytics/`.

**Thiết kế:** `src/analytics/` không import `dash`, không đăng ký callback, không bind cổng. W6 chạy **trong tiến trình dashboard** như một lời gọi hàm (C3), nên nó không thêm endpoint nào. `config.yaml` giữ `dashboard.host: 127.0.0.1`.

**Cái gì chặn:** không có gì — kiểm soát là phép đếm. `grep -rn "from dash\|import dash\|callback" src/analytics/` rỗng; hình dạng dashboard (số tab/callback/output, do U3 sở hữu và `tests/unit/test_dashboard_smoke.py` canh) không được đổi bởi U2.

**Vì sao không để chỗ cắm sẵn:** một route dự đoán là quyết định phạm vi đã bị loại (`requirements.md` `## Out of scope`: "API dự đoán (endpoint gọi từ ngoài)"). Thêm nó ở đây vừa ra ngoài phạm vi, vừa tạo một bề mặt không ai kiểm — cùng lập luận đã dùng cho xác thực ở U1 SD1.

## SD2.6 — Lỗi không rò dòng dữ liệu: chặn ở chỗ dựng chuỗi, không ở chỗ lọc

**Vị trí:** mọi `ModelError` của W1–W6.

**Thiết kế:** thông điệp chỉ chứa **tên trường**, **tên cột**, **số đếm**, **mã luật** (`BR2.x`). Không giá trị ô, không `order_id`, không mã bưu chính, không dán cả dòng.

**Vì sao chặn ở chỗ dựng chuỗi:** `str(exc)` đi **hai** đường ra — `cli.main` in `ERROR: {exc}` ra stderr (`cli.py:72-74`), và `stages.py:268` ghi `logger.error("stage_failed", ...)` vào `logs/*.jsonl`. Không bộ lọc nào ở hai đầu ra đó, nên chỗ duy nhất kiểm được là nơi tạo thông điệp.

**Ba hình dạng cụ thể:**

| Chỗ | Thông điệp mang | Test canh |
|---|---|---|
| W6 `score_item` thiếu trường | tên trường (`customer_state`), không giá trị | khẳng định **có** tên trường **và không** có giá trị của mười trường còn lại — vế thứ hai mới là vế canh rò rỉ |
| W1b `validate_counts` | tên check + các số (`model.py:299-305` đang đúng hình dạng này, hiện kiểm ba số của tập kiểm tra) | khẳng định chuỗi chỉ gồm tên check và số |
| W1 `training_frame` nhân dòng | câu cố định, không số dòng dữ liệu | đổi `ValueError` (`service.py:385-386`) sang `ModelError` — **cùng câu, khác lớp** (BR2.1) |

**Giới hạn:** văn bản của thư viện bên thứ ba (duckdb, sklearn, pandas) không do U2 dựng. Chỗ nào U2 bọc thì bọc bằng câu của mình và chỉ nêu `type(exc).__name__`; chỗ nào chưa bọc thì văn bản thô đi thẳng vào log. W1 hiện **chưa** bọc (`service.py:377-387` để ngoại lệ duckdb lọt ra), nên `QueryExecutionError` ở W1 bước 1 là việc Code Generation phải làm — tài liệu này không giả vờ nó đã có.

## SD2.7 — Đường dẫn từ `AppConfig`: một trường mới, một chỗ dựng

**Vị trí:** `AppConfig` (`src/config.py:15-52`), `load_config` (`:142-155`), W5 bước 4.

**Thiết kế:** `models_dir` là trường **mới**, kiểu `Path`, đọc từ khoá `models_dir` của `config.yaml`, mặc định `data/models`; thêm vào vòng `mkdir` (`:142-155`) để "thư mục vắng" là trạng thái bình thường của máy mới clone. Đường dẫn tệp dựng đúng hình dạng `report_path` (`report.py:242-245`): `Path(models_dir) / MODEL_FILE_NAME`, với tên tệp là hằng của mô-đun (ADR-001) — không phải tên do người gọi truyền.

**Cái gì chặn:** không có kiểm tra runtime. Kiểm soát là **không tồn tại đường khác**: không cờ CLI (`grep -rn "models_dir" src/pipeline/cli.py` rỗng), không đọc từ dữ liệu, không đọc biến môi trường. Một đường dẫn nhận từ dòng lệnh có thể trỏ vào `dataset/` hoặc ra ngoài workspace; đường dẫn cố định trong cấu hình thì không — và đó là điều kiện để SD2.3 (3) đứng vững.

**Hai điều dễ làm sai, ghi để Code Generation không phải tự quyết:**

- `load_config` **không ném** khi thiếu khoá — nó lấy mặc định rồi tạo thư mục. "Cấu hình là biên giới" nghĩa là *đường dẫn không đến từ người dùng*, **không** nghĩa là *cấu hình sai thì bị chặn*.
- Phép kiểm phải nhắm **đường dẫn mô hình**, không `grep "Path("`. `report.py` có tám chỗ `Path(` hợp lệ (`:245`, `:255`, `:273`, `:314`, `:322`, `:324`, `:326`, `:328`), trong đó `:255`/`:273`/`:322` dựng từ tham số hàm — `grep -n "Path(" src/analytics/` sẽ đỏ trên mã đúng, ngay lần đầu.

## SD2.8 — Miền lỗi và bán kính ảnh hưởng

| # | Hỏng ở | Ai ném | Cổng nào bắt | Còn nguyên trên đĩa |
|---|---|---|---|---|
| 1 | W1.1 truy vấn dựng khung sai (join nở dòng, sai view) | ngoại lệ duckdb thô (chưa bọc) | **không cổng nào trong `stats`**; test `slow` | báo cáo cũ + tệp mô hình cũ |
| 2 | W1.3 bốn bộ đếm lệch 110.195 / 96.476 / 8.713 / 2 | `ModelError` (BR2.1) | chặn trước khi ghi | cả hai tệp cũ |
| 3 | W2 giao hai tập `order_id` khác rỗng, hoặc tổng lệch `cohort_rows` | `ModelError` (BR2.2) | chặn trước khi ghi | cả hai tệp cũ |
| 4 | W3 sai 14 tên hợp đồng / sai thứ tự của chúng / có cột cấm (thứ tự **cột one-hot** không thuộc dòng này) | `ModelError` (BR2.3) | chặn trước khi ghi | cả hai tệp cũ |
| 5 | W3 không hội tụ, hoặc ngưỡng ngoài (0,1) | `ModelError` | chặn trước khi ghi | cả hai tệp cũ |
| 6 | W4 baseline lệch mốc, hai cờ không khớp phép so | `ModelError` (BR2.6) | chặn trước khi ghi | cả hai tệp cũ |
| 7 | W5.3 ghi báo cáo lỗi — **hai nhánh khác lớp**: parse/phiên bản/khối rỗng, và lỗi ghi đĩa (thư mục tạm, đĩa đầy, quyền) | `ReportError` cho nhánh parse/phiên bản (`report.py:318-328`); `OSError` **không bọc** cho nhánh ghi đĩa (`io.py:77-83`) | **chặn thay tệp** ở cả hai nhánh — `os.replace` chỉ chạy sau `_verify_pending` (`report.py:256-263`) | báo cáo cũ; tệp mô hình chưa bị chạm (bước 4 chưa chạy) |
| 8 | W5.4 lưu tệp mô hình lỗi | `ModelError` | **không chặn** — báo cáo đã thay ở bước 3 | báo cáo v3 **mới** + tệp mô hình cũ/chưa có |
| 9 | W5.5 nạp lại lệch trạng thái tiền xử lý | `ModelError` | phát hiện **sau** khi cả hai tệp đã ghi | cả hai tệp mới; chỉ test/người đọc biết |
| 10 | W6 thiếu hay sai một trường nhập | `ModelError` nêu tên trường | — | không chạm đĩa |

**Dòng 7 có hai lớp vì có hai loại hỏng.** `ReportError` chỉ đúng cho nhánh **kiểm lại** tệp tạm (parse, `version`, hai khối cùng rỗng) — `report.py:318-328` tự ném nó. Lỗi **ghi** thật (thư mục tạm không tạo được, đĩa đầy, quyền) phát ra từ `AtomicWriter.write_json` (`io.py:77-83`), nơi không bọc gì, nên nổi lên là `OSError` thô; `report.py` không bắt lại, và `stages.run_stage` (`stages.py:267-268`) chỉ ghi `str(exc)` rồi ném tiếp. Kết luận thực hành: **không** được viết `except ReportError` ở chỗ gọi `write_report` rồi coi như đã phủ hết — câu "chặn thay tệp, tệp cũ còn nguyên" thì đúng cho cả hai lớp, vì `os.replace` nằm sau cả hai.

**Vì sao thứ tự ghi là báo cáo trước, mô hình sau — và cái nó KHÔNG đóng.** Đảo thứ tự không đóng được lỗ này: cả hai chiều đều để lại một **cặp lệch thế hệ**, chỉ khác nửa nào cũ. Với thứ tự hiện tại, khi bước 4 hỏng mà lần chạy trước đã để lại tệp trong `data/models/`, trạng thái trên đĩa đúng là **báo cáo v3 mới cạnh tệp mô hình cũ** — dòng 8 của bảng, **không** phải "có báo cáo, không có mô hình". `data/models/` tồn tại qua các lần chạy; chỉ máy mới clone mới thật sự vắng tệp, và đó là trạng thái duy nhất U3 nhận ra được (`absent_behaviour` của C2 chỉ phủ trường hợp **vắng**). Khi cặp lệch, U3 nạp `FittedModel` cũ (C2b) nhưng đọc `threshold` mới từ báo cáo (C2), nên kết luận trễ/sớm sai **im lặng** — đúng thứ BR2.5 ("ngưỡng là nguồn duy nhất") dựng ra để không xảy ra, mà lần này không có gì chặn: `_verify_pending` chỉ kiểm tệp tạm của báo cáo, không trường nào trong `ModelBlock` hay trong metadata mô hình buộc hai tệp phải cùng một lần chạy, và không validator nào trong dự án biết hai tệp này là một cặp.

**Biện pháp thật, xếp theo thứ tự làm được ngay:**

1. **Kiểm dấu thời gian lúc ghép hai tệp (U2 làm được ngay, không cần đổi C2).** Metadata `data/models/logistic.json` ghi `trained_at` cạnh phiên bản định dạng; báo cáo đã có `generated_at`. `load_model` trả `FittedModel` mang thêm `trained_at` (**chữ ký C2b giữ nguyên**: vẫn `load_model(models_dir) -> FittedModel | None`), rồi nơi ghép cặp từ chối khi mô hình **cũ hơn** báo cáo — đó đúng là chữ ký của trạng thái dòng 8. Chỗ ghép có **hai**: W5.5 trong lần chạy, và U3 lúc nạp cho W6.
2. **Ghi mô hình trước, báo cáo sau** (đảo W5 bước 4 lên trước bước 3). Một mình nó **không** đóng lỗ — vẫn là cặp lệch, chỉ ngược chiều (mô hình mới cạnh ngưỡng cũ) — nên chỉ đáng làm khi đi kèm (1); khi đó phép kiểm ở (1) phải phát biểu thành "hai dấu thời gian phải cùng một lần chạy", không phải "mô hình không được cũ hơn báo cáo".
3. **Một id thế hệ có mặt trong cả hai tệp.** Đây là biện pháp duy nhất đóng hẳn, và nó là thay đổi **hợp đồng** (thêm trường vào C2 và C2b), nên thuộc **chủ hợp đồng C2** quyết — ghi thành mục mở ở đoạn cuối mục này, không phải việc NFR Design tự thêm.

**Cổng thật của U2 là test, không phải cổng runtime.** `StarSchemaValidator` và `KpiReconciler` **không kiểm gì ở tầng mô hình**: chúng chạy trong `integrate`, chỉ đọc số dòng và 5 KPI của mart, không biết `ModelBlock` là gì, không biết tệp mô hình tồn tại hay không. `run --stage stats` không gọi validator nào. Vì vậy cột "cổng nào bắt" ở trên **không** có nghĩa "một validator"; nó có nghĩa "ném trước khi ghi" hoặc "test". Mốc sàn AUC của NFR5 cũng **không** phải cổng runtime: U2 giao hằng `MODEL_AUC_FLOOR` và hàm `beats_floor` (LC2.11), test `slow` trên báo cáo thật do **U3** viết (TS2.5(c)).

**Giới hạn cuối, thuộc C2 chứ không thuộc U2:** hai tệp được thay **nguyên tử từng tệp**, không có khoá giữa hai tệp và không có id thế hệ chung. U3 đọc báo cáo ở thời điểm T1 rồi nạp mô hình ở T2 có thể thấy **hai thế hệ khác nhau** nếu `run --stage stats` chạy chen giữa. Đóng lỗ này cần một id phiên bản có mặt trong cả hai tệp — đó là thay đổi hợp đồng do chủ C2 quyết, không phải việc NFR Design tự thêm.

## Điều tài liệu này không thiết kế

Không mã hoá at-rest, không TLS, không audit log truy cập, không quản lý khoá, không sandbox tiến trình, không chống thay đổi tệp, không sao lưu, không giới hạn tần suất. Không thành phần nào của đơn vị này cần chúng, và vẽ ra chúng sẽ là mô tả một hệ thống khác — đúng lỗi mà `security-requirements.md` đã từ chối ở bước trước.

## Ánh xạ NFR gốc sang thiết kế của đơn vị

| NFR gốc | Mã con | Thiết kế tương ứng |
|---|---|---|
| `NFR1` | `NFR1.1` | `LC2.16` — điểm đo ngân sách 300 s của tầng `stats`. |
| `NFR2` | `NFR2.1` | `LC2.16` — 240 s cho toàn bộ bước mô hình, gồm cả lượt đọc mart. |
| `NFR3` | `NFR3.1` | `LC2.17` — cổng phủ 80% giữ nguyên, không tách sang bộ nhanh. |
| `NFR4` | `NFR4.1` | `SD2.1` (mart chỉ đọc qua kết nối) và `SD2.8` (bán kính ảnh hưởng khi ghi hỏng). |
| `NFR5` | `NFR5.1` | `LC2.11` (hằng `MODEL_AUC_FLOOR` + hàm `beats_floor`) và `LC2.17`; test `slow` mốc sàn do **U3** viết. |
| `NFR6` | `NFR6.1` | `N/A` — đơn vị không có bề mặt giao diện. |
