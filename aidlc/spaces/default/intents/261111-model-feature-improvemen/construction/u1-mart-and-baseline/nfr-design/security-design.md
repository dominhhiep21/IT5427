# Security Design — u1-mart-and-baseline

Đơn vị: `u1-mart-and-baseline` (kind `library`). Nguồn: `../nfr-requirements/security-requirements.md`, `../functional-design/functional-spec.md`, `../../../inception/contract-design/contract-summary.md` (C1), mã thật `src/integrate/`, `src/common/`.

Đây là **thiết kế**, không phải mã. Mục tiêu là nói rõ từng kiểm soát nằm ở đâu trong luồng chạy, **cái gì chặn**, và khi nó chặn thì chuyện gì xảy ra — để Code Generation không phải tự quyết.

## Bối cảnh: không có chu vi mạng để bảo vệ

Đơn vị chạy trong tiến trình CLI trên máy người dùng. Không endpoint, không người dùng thứ hai, không vai trò. Có **một** lời gọi ra ngoài: HTTPS tới API IBGE ở tầng `integrate`, có cache trên đĩa và fallback. Vì thế "an toàn" ở đây nghĩa là **tính toàn vẹn dữ liệu dẫn xuất** và **không mở bề mặt mới**, không phải xác thực/phân quyền.

## SD1 — Không có lớp xác thực, và điều đó là thiết kế

**Kế thừa:** `SEC1`.

**Thiết kế:** không thêm middleware, decorator, hay kiểm tra quyền nào. Không có "chỗ cắm" cho xác thực.

**Vì sao không để chỗ cắm sẵn:** một điểm nối xác thực không có ai gọi là bề mặt tấn công không được kiểm, và nó tạo cảm giác sai rằng hệ thống có phân quyền. Khi nào dự án có người dùng thứ hai, đó là quyết định kiến trúc riêng, không phải hook để sẵn.

**Ranh giới:** nếu sau này có endpoint, việc thêm xác thực thuộc đơn vị mở endpoint đó, không thuộc đơn vị dựng mart.

## SD2 — Bất biến của dữ liệu gốc: kiểm bằng hash, sau khi chạy

**Kế thừa:** `SEC2`.

**Thiết kế:** trước và sau `run --stage all`, tính SHA-256 của **9 CSV gốc** trong `dataset/` (không tính `dataset/external/ibge/`) và so. Lệch ⇒ test đỏ.

**Đây là kiểm soát phát hiện, không phải kiểm soát chặn.** Nó chạy **sau** khi mart đã ghi, nên nếu CSV gốc bị sửa thì mart dựng từ dữ liệu đã sửa vẫn nằm trên đĩa — test đỏ nhưng không dọn hộ. Nói đúng điều đó quan trọng hơn là làm nó trông chắc chắn hơn thực tế.

**Vì sao hash chứ không phải "đọc mã và tin":** một lần ghi đè lên CSV gốc không phát hiện được bằng test số dòng — số dòng vẫn đúng, nội dung mới là thứ đổi.

**Ngoại lệ đã biết, thiết kế phải nói ra:** `dataset/external/ibge/` là **cache** do `IbgeClient` ghi (`estados.json`, `metadata.json`). Nó là dữ liệu sinh ra, không phải dữ liệu gốc, và nằm ngoài phép kiểm hash. Một thiết kế nói "không ghi gì vào `dataset/`" sẽ sai ngay ở đơn vị đầu tiên — và sai theo hướng nguy hiểm: người thi công có thể "sửa" cache thành ghi vào `data/` để làm test xanh, đổi hành vi đã có của `integrate`.

## SD3 — Không có bí mật, và cấu hình là nơi duy nhất khai đường dẫn

**Kế thừa:** `SEC3`, `SEC5`.

**Thiết kế:** mọi đường dẫn đi qua `AppConfig` (frozen dataclass, 34 trường, nạp từ `config.yaml` một lần). Không nhận đường dẫn từ tham số dòng lệnh; không dựng `Path(...)` từ dữ liệu.

**Vì sao gộp SEC3 và SEC5:** cả hai cùng một cơ chế — **cấu hình là biên giới tin cậy duy nhất**. Tách thành hai thiết kế riêng sẽ là hai chỗ phải sửa cho cùng một lý do.

**Hệ quả phải biết:** `load_config` **không ném** khi một khoá vắng — nó dùng giá trị mặc định, rồi tạo sẵn thư mục đầu ra. Vì vậy "cấu hình là biên giới" nghĩa là *đường dẫn không đến từ người dùng*, **không** phải *cấu hình sai sẽ bị chặn*. Một thiết kế nói "thiếu khoá ⇒ `ConfigurationError`" là mô tả một `load_config` khác với cái đang có.

## SD4 — Ba cột mới không mở rộng dữ liệu định danh, và chỗ kiểm phải nói thật

**Kế thừa:** `SEC4`, một phần `SEC6` của `rules.md` BR1.6.

**Thiết kế:** ba cột khai kiểu chặt — hai mốc thời gian là timestamp nullable; `seller_state` là chuỗi hai chữ hoa thuộc tập đóng (23 giá trị trên dữ liệu thật). Không cột nào là tên, địa chỉ, hay mã bưu chính.

**Chỗ kiểm, nói đúng sự thật:** kiểu dữ liệu và tính nullable của ba cột **không có cổng runtime nào** kiểm; còn **miền giá trị** của `seller_state` thì **có**, nhưng không phải ở `StarSchemaValidator`:

| Điều kiện | Kiểm ở đâu | Chặn runtime? |
|---|---|---|
| Tập bang hợp lệ (khách ∪ người bán) | `RegionMapper.validate` (`src/external/region.py:14-33`), gọi ở `pipeline.py:72-76`, ném `ExternalSourceError` | **Có** — trước mọi bước ghi |
| Ba cột tồn tại, đúng dtype, nullable | test đơn vị của U1 trên khung dựng trong `tmp_path` | Không |
| `seller_state` đúng 23 giá trị, hai chữ hoa trên dữ liệu thật | `tests/data_quality/test_real_dataset.py` (bộ `slow`) | Không |
| Số dòng và 5 KPI | `StarSchemaValidator`, `KpiReconciler` | **Có** |

Điều này **sửa một khẳng định sai ở bản trước** của chính mục này: tôi đã viết "không có cổng runtime nào kiểm kiểu dữ liệu hay miền giá trị". Vế đầu đúng, vế sau sai — `RegionMapper.validate` kiểm miền bang và chặn trước khi ghi. Và nó kiểm **rộng hơn** ba cột: nó kiểm tập bang của cả khách lẫn người bán, nên `seller_state` được bảo vệ như một hệ quả chứ không phải một kiểm soát riêng.

`rules.md` BR1.6 ghi vi phạm là "`QualityGateError` ở tầng mart" — chỗ đó vẫn chưa đúng: không cổng nào kiểm dtype. BR1.6 được cưỡng chế bằng **test**, và một phần miền giá trị được cưỡng chế bởi `RegionMapper.validate` với lớp lỗi `ExternalSourceError`, không phải `QualityGateError`.

**Vì sao không thêm cổng runtime cho dtype:** thêm một cổng kiểm dtype cho ba cột sẽ là cổng chỉ kiểm ba cột trong khi 12 cột còn lại không được kiểm — một kiểm soát không đối xứng, tạo cảm giác an toàn giả. Nếu muốn kiểm dtype cho cả mart, đó là thay đổi của `StarSchemaValidator` cho **toàn bộ** 9 bảng, không phải việc của đơn vị này.

## SD5 — Thông điệp lỗi chỉ mang số, không mang dòng dữ liệu

**Kế thừa:** `SEC6`.

**Thiết kế:** `QualityGateError` của kiểm star schema nêu `check_id`, `expected`, `actual` — định danh và số đếm. Thiết kế **giữ nguyên** tính chất đó và cấm thêm giá trị ô dữ liệu vào thông điệp.

**Vì sao quan trọng dù không có kẻ tấn công:** log ghi ra `logs/` và thường được dán vào báo lỗi. Một thông điệp chứa cả dòng dữ liệu là rò rỉ ngoài ý muốn, kể cả khi chỉ chia sẻ trong nhóm.

## Miền lỗi và bán kính ảnh hưởng

| Kiểm soát | Ở đâu | Chặn trước khi ghi? | Khi vi phạm |
|---|---|---|---|
| Số dòng mart | `StarSchemaValidator`, `pipeline.py:84` | **Có** | `QualityGateError`; mart cũ còn nguyên |
| 5 KPI | `KpiReconciler`, `pipeline.py:88` | **Có** | `QualityGateError`; mart cũ còn nguyên |
| Miền bang của khách và người bán | `RegionMapper.validate`, `pipeline.py:72-76` | **Có** | `ExternalSourceError`; chưa có gì được ghi |
| dtype / nullable ba cột | test đơn vị | **Không** | test đỏ |
| Hash 9 CSV gốc | test `slow`, **sau** khi chạy | **Không** | test đỏ; mart đã ghi vẫn nằm trên đĩa |
| Đường dẫn từ cấu hình | `AppConfig` | **Có**, bằng cách *không có đường nào khác* — không phải bằng kiểm tra | — |

**Bốn kiểm soát chặn thật (ba cổng runtime + cấu hình), hai kiểm soát phát hiện.** Bản trước của mục này nói "ba kiểm soát đầu đều chặn trước khi ghi" — sai cả về số lẫn về bản chất, và sai theo hướng làm yên tâm quá sớm: một mart dựng từ CSV bị sửa vẫn tồn tại cho tới khi có người đọc test đỏ.

Điểm đáng chú ý khác: mart được ghi theo **từng bảng, mỗi bảng một `os.replace`** (`pipeline.py:93-98`), rồi 11 view được tạo lại (`:100`). Vì view là `read_parquet` trên đúng đường dẫn tuyệt đối đó, một view "cũ" vẫn đọc nội dung **mới** — nên trạng thái nửa vời chỉ có thể là: một số bảng mart đã mới, một số còn cũ, nếu lần ghi hỏng giữa vòng lặp. Đó là rủi ro thật, và nó **không** do đơn vị này tạo ra.

## Điều tài liệu này không thiết kế

Không mã hoá at-rest, không TLS, không audit log truy cập, không quản lý khoá. Không thành phần nào cần chúng, và vẽ ra chúng sẽ là mô tả một hệ thống khác — đúng lỗi mà `security-requirements.md` đã từ chối ở bước trước.
