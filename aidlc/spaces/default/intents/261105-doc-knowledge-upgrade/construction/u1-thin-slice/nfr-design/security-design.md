# Security Design — u1-thin-slice

Nguồn: `nfr-requirements/` (`security-requirements.md`, `performance-requirements.md`, `scalability-requirements.md`, `reliability-requirements.md`, `observability-requirements.md`, `tech-stack-decisions.md`), `functional-design/functional-spec.md`, `contract-design/contract-summary.md` (C4, C8, C9).

Đơn vị: `u1-thin-slice`. Bề mặt tấn công của lát cắt rất nhỏ nhưng **không bằng không**: tên bảng và tên cột nguồn đi từ tệp khai báo lược đồ vào câu SQL, nên đó là chỗ duy nhất cần thiết kế cẩn thận.

## 1. Phạm vi và mô hình mối đe doạ

Hệ chạy local, một người dùng, không có xác thực, không có dữ liệu cá nhân thật (`security-requirements.md` SR-U1-1, SR-U1-4). Vì vậy mô hình mối đe doạ chỉ gồm ba tình huống có thật:

| Tài sản | Mối đe doạ | Khả năng | Tác động | Kiểm soát |
|---|---|---|---|---|
| Dữ liệu nguồn trong `dataset/` | Bị ghi đè hoặc "làm sạch tại chỗ" bởi chính pipeline | Thấp | Mất dữ liệu gốc, phải tải lại | Đơn vị chỉ mở tệp ở chế độ đọc; không có lời gọi ghi nào vào `dataset/`; ràng buộc đã có trong luật dự án |
| Câu SQL chạy trên DuckDB | Tên bảng/cột trong tệp lược đồ chứa cú pháp SQL, biến một câu `SELECT` thành nhiều câu | Trung bình — tệp YAML là tệp người sửa được | Chạy câu SQL ngoài ý muốn trên dữ liệu cục bộ | Kiểm danh tính trước khi nội suy (§3, ADR-U1-S2) |
| Nhật ký trong `logs/` | Ghi dữ liệu vượt mức cần thiết (giá trị cột, nội dung tệp) | Trung bình — dễ log cả dòng | Sao chép dữ liệu sang nơi ít kiểm soát hơn | Chỉ log số đếm, tên tệp, mã lỗi; không log giá trị bản ghi (§4) |

Ngoài ba tình huống trên, các mối đe doạ quen thuộc không áp dụng và được ghi rõ để người đọc sau không thiết kế thừa:

| Không áp dụng | Vì sao |
|---|---|
| Xác thực, phân quyền, phiên | Không có người dùng từ xa; bind loopback (SR-U1-1) |
| Mã hoá khi truyền | Không có lưu lượng mạng ra ngoài |
| Mã hoá khi lưu | Không có dữ liệu cá nhân, không có bí mật (SR-U1-2, SR-U1-5) |
| CSRF/XSS | Không có biểu mẫu ghi; mọi chuỗi hiển thị đi qua `html.Div` của Dash, không dựng HTML từ chuỗi người dùng |
| Header bảo mật (CSP, HSTS, X-Frame-Options) | Trang chỉ phục vụ loopback, không TLS, không nhúng ngoài; HSTS vô nghĩa khi không có HTTPS. Đã cân nhắc và loại — nếu mở ra mạng LAN thì phải thêm TLS và bộ header trước |
| Tuân thủ quy định (GDPR, PCI-DSS, …) | Không có dữ liệu cá nhân thật và không có dữ liệu thanh toán; dữ liệu Olist là bộ công khai đã ẩn danh (SR-U1-4). Đã cân nhắc và loại |
| Quản lý bí mật | Không có API key, token hay mật khẩu (SR-U1-2) |

## 2. Quyết định thiết kế

### ADR-U1-S1 — Chỉ bind loopback, không thêm xác thực

**Quyết định:** dashboard bind `127.0.0.1:8050` lấy từ `config.yaml`; không thêm đăng nhập, không thêm token, không mở `0.0.0.0`.

**Hệ quả:** người khác dùng chung máy vẫn xem được số liệu nếu họ ngồi vào máy đó. Đây là rủi ro đã được chấp nhận ở `security-requirements.md` (dữ liệu Olist công khai). Nếu sau này cần nhiều người xem, đó là thay đổi phạm vi phải chốt lại và kéo theo xác thực — không được lặng lẽ đổi `host` trong `config.yaml`.

### ADR-U1-S2 — Kiểm danh tính trước khi đưa tên vào SQL

Đây là kiểm soát quan trọng nhất của đơn vị. Đường đi của một câu SQL là: tệp lược đồ (YAML) → tên bảng nguồn, tên cột nguồn → câu SQL. Nếu nội suy thẳng, một dòng `source_column: "order_id FROM orders; DROP TABLE x --"` sẽ thoát khỏi ý định của câu truy vấn.

Ba lớp, áp dụng cùng lúc:

1. **Danh sách cho phép từ dữ liệu thật, không từ chuỗi người dùng.** Tên bảng chỉ được là một trong chín bảng nguồn đã khai trong `src/ingest/schemas.py`; tên cột chỉ được là cột có thật trong tiêu đề CSV đã đọc. Đối chiếu bằng phép so sánh tập hợp, không bằng regex "trông có vẻ ổn".
2. **Kiểm hình dạng danh tính** trước khi so tập hợp, để câu lỗi nêu đúng chỗ sai: `^[a-z][a-z0-9_]*$`, tối đa 64 ký tự.
3. **Giá trị truyền qua placeholder `?`**, tên cột trong `GROUP BY`/`SELECT` lấy từ dict hằng của mã, không ghép từ tham số hàm (ràng buộc đã có trong luật dự án).

```python
IDENTIFIER = re.compile(r"^[a-z][a-z0-9_]{0,63}$")

def checked_identifier(name: str, allowed: frozenset[str], kind: str) -> str:
    if not IDENTIFIER.fullmatch(name) or name not in allowed:
        raise SchemaError(f"{kind} không hợp lệ: {name!r}")
    return name
```

**Hệ quả:** một tệp lược đồ bị sửa sai sẽ **từ chối phục vụ** thay vì chạy câu SQL lạ. Test bắt buộc: một ca với tên cột chứa `;` và một ca với tên bảng không có trong danh sách, cả hai phải ném `SchemaError` trước khi mở kết nối DuckDB.

**Điều không làm:** không tự "làm sạch" tên bằng cách xoá ký tự lạ. Làm sạch ngầm biến một tệp sai thành một câu SQL chạy được trên cột khác — sai lặng lẽ, khó tìm hơn một lỗi rõ ràng.

### ADR-U1-S3 — Không có đầu vào người dùng dựng thành SQL

Lát cắt chỉ chạy **một** truy vấn cố định (đếm đơn theo tháng × trạng thái). Không có ô nhập SQL, không có tham số tự do từ giao diện. Bộ lọc trạng thái của tab mới là danh sách tám giá trị cố định đã có trong `app.py`, không phải chuỗi tự do.

**Hệ quả:** bề mặt injection từ phía giao diện bằng không. Khi Bolt sau thêm truy vấn mẫu có tham số, tham số đó phải đi qua placeholder `?` và một bộ kiểm kiểu — ghi ở `scalability-design.md` §3 như điều kiện xem lại.

### ADR-U1-S4 — Thông báo lỗi cho người dùng và chi tiết cho nhật ký

**Quyết định:** giao diện chỉ hiện câu tiếng Việt nêu việc gì hỏng và nút thử lại; tên tệp, tên cột, mã lỗi và stack trace chỉ vào nhật ký.

**Hệ quả:** người dùng không phải đọc traceback, và đường dẫn tuyệt đối của máy không bị đưa lên màn hình. Đổi lại, chẩn đoán cần mở `logs/` — chấp nhận được vì đây là công cụ một người.

### ADR-U1-S5 — Không thêm thư viện; đọc lược đồ bằng gói đã ghim

`requirements.txt` đã ghim 8 gói, trong đó có `PyYAML==6.0.2` và `src/config.py` đang dùng `yaml.safe_load` cho `config.yaml`. Đơn vị này chỉ thêm `ruff` (đã chốt ở `tech-stack-decisions.md` TS-U1-3) và **không** thêm gói nào khác.

**Quyết định:** tệp `config/mediated-schema.yaml` là YAML (đúng C8) và được đọc bằng `yaml.safe_load` của `PyYAML` đã ghim — cùng cơ chế đọc cấu hình hiện có, không mở thêm đường đọc tệp thứ hai.

**Hệ quả:** bề mặt chuỗi cung ứng không tăng, và định dạng tệp không còn là câu hỏi mở. `yaml.safe_load` (không phải `load`) là bắt buộc vì tệp là đầu vào người sửa được. Mọi gói thêm sau này phải ghim phiên bản kèm lý do.

## 3. Đối chiếu yêu cầu bảo mật

| Mã | Cách đáp ứng trong thiết kế |
|---|---|
| SR-U1-1 | ADR-U1-S1; `host` đọc từ `config.yaml`, test khẳng định giá trị là `127.0.0.1` |
| SR-U1-2 | Không có bí mật trong mã, trong `config.yaml` hay trong lược đồ; không đọc biến môi trường |
| SR-U1-3 | ADR-U1-S2 (ba lớp) + ADR-U1-S3 (không đầu vào tự do) |
| SR-U1-4 | Không đọc cột nào ngoài 5 trường của `don_hang`; `ma_khach` chỉ dùng làm khoá đếm, không hiển thị, không log |
| SR-U1-5 | `config.yaml` chỉ chứa đường dẫn và `host`/`port`; test khẳng định không có khoá nào tên `password`, `token`, `secret`, `key` |

## 4. Nhật ký và dữ liệu

- **Nguồn sự thật duy nhất cho lược đồ nhật ký là `observability-design.md` §2** (danh mục sự kiện kèm đúng các trường của từng sự kiện). Mục này không lặp lại danh sách trường; nó chỉ đặt ra ba giới hạn mà danh mục kia phải tuân.
- **Giới hạn 1 — không ghi giá trị bản ghi.** Không ghi nội dung của bất kỳ bản ghi nào, không ghi `ma_khach`, không ghi nội dung tệp. Chỉ số đếm, tên tệp, tên bảng/cột, mã lỗi và thời gian.
- **Giới hạn 2 — câu SQL nguồn chỉ xuất hiện ở đúng một sự kiện.** `integration.query.started` mang trường `source_sql`, vì câu SQL do mã sinh ra từ lược đồ đã kiểm (ADR-U1-S2), không chứa dữ liệu, và cần cho việc đối chiếu "hai bản truy vấn" của Workflow 2. Không sự kiện nào khác mang câu SQL.
- **Giới hạn 3 — `error_code` là tập giá trị đóng**, khai một lần trong mã: `file_not_found`, `permission_denied`, `decode_error`, `column_missing`, `identifier_invalid`, `sql_error`, `result_unreadable`. Giá trị lạ không được ghi ra nhật ký; nếu gặp, ghi `error_code="unknown"` kèm thông điệp đã cắt ngắn.

Ba giới hạn này chỉ chặt hơn danh mục sự kiện, không mâu thuẫn với nó: `field` và `column` là cách duy nhất đáp ứng OB-U1-2 nên chúng nằm trong danh mục; `attempt`, `template_id`, `message`, `log_path`, `reason` cũng vậy; `source_sql` được khai đúng ở sự kiện `integration.query.started`.

## 5. Kiểm chứng

| Kiểm chứng | Cách làm |
|---|---|
| Bind loopback | Test đọc `config.yaml` và khẳng định `host == "127.0.0.1"` |
| Chặn tên bảng/cột lạ | Hai test âm: tên cột chứa `;`, tên bảng ngoài danh sách → `SchemaError`, và khẳng định **không** có kết nối DuckDB nào được mở |
| Không có bí mật trong cấu hình | Test quét `config.yaml` theo bốn khoá ở §3 |
| Lint | `ruff check` + `ruff format --check` sạch trước khi coi là xong |
| Không ghi vào dữ liệu gốc | Rà soát: chỉ `Path.open("r")` và `pd.read_csv` trên `dataset/`; không có `to_csv`, `to_parquet`, `os.replace` trỏ vào `dataset/` |

## 6. Giả định và câu hỏi mở

| # | Nội dung | Trạng thái |
|---|---|---|
| A1 | Tệp lược đồ do chính người dùng sửa, không đến từ nguồn ngoài | Giả định — vì vậy kiểm soát là "từ chối phục vụ", không phải cách ly tiến trình |
| A2 | Máy chạy không có phần mềm độc hại đọc `logs/` | Giả định — ngoài phạm vi đơn vị |

Không còn câu hỏi mở. Định dạng tệp lược đồ đã chốt ở ADR-U1-S5: YAML theo C8, đọc bằng `yaml.safe_load` của `PyYAML==6.0.2` đã ghim.
