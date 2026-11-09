# Security Design — u5-source-selector

Nguồn: `nfr-requirements/security-requirements.md` (SR-U5-1..14, bảng ánh xạ lỗi §1.1), `nfr-requirements/tech-stack-decisions.md` (TS-U5-1..13, NFR1.1–NFR6.2), `functional-design/functional-spec.md` (W1–W4), `functional-design/entities.md` (bề mặt lỗi), `inception/contract-design/contract-summary.md` (C2, C3, C7).

Đơn vị không có đăng nhập, không mở cổng, không có bí mật. Toàn bộ bề mặt tấn công của nó là **một tệp cấu hình do người sửa tay** và **hai payload nó trả ra** (C3 cho U3, C7 cho U6). Tám quyết định dưới đây là toàn bộ cách đơn vị tự bảo vệ.

Hai chủ đề **không áp dụng** và vì sao: **mã hoá** — đơn vị không lưu và không truyền dữ liệu ra ngoài tiến trình, không có tệp riêng, không có kênh mạng; **tuân thủ dữ liệu cá nhân** — đơn vị không đọc giá trị ô nào (`SR-U5-9`), nên không có mã khách hay mã người bán đi qua nó hay xuất hiện trong chuỗi nó sinh ra.

## ADR-U5-S1 — Kiểm toàn bộ cấu hình trước khi dùng bất cứ thứ gì

**Bối cảnh.** Cấu hình gồm ba nguồn và ba ánh xạ truy vấn. Nếu vừa kiểm vừa dùng, một nguồn hợp lệ có thể đã đi vào danh mục trước khi nguồn thứ ba hỏng, và consumer nhận một danh mục nửa đúng.

**Quyết định.** `load_source_catalogue` chạy **hết** các phép kiểm rồi mới dựng `SourceCatalogue`. Không có danh mục nào được trả về khi còn một phép kiểm chưa qua. Thứ tự kiểm cố định: tệp → kiểu từng khoá (ADR-U5-S7) → cấu trúc từng nguồn → tập tên nguồn và số nguồn mô phỏng → `covered_fields` với C2 → `tables` với `SOURCE_TABLES` → ánh xạ truy vấn (**đúng ba `query_id`** và **mọi mã trường trong ánh xạ phải có trong C2**, cùng phép kiểm với `covered_fields` — thiếu vế thứ hai, một mã trường gõ sai sẽ lộ ra thành `NoSourceAvailableError` thay vì `SchemaError`).

**Hệ quả.** Danh mục trả ra luôn nhất quán toàn bộ; chi phí là phải đọc hết cấu hình trước khi có kết quả đầu tiên (không đáng kể: một tệp YAML nhỏ). Lỗi thuộc đúng lớp trong bảng §1.1 của `security-requirements.md`, không có nhánh nào trả danh mục một phần. Lỗi của C2 lan truyền **nguyên vẹn** — cùng lớp, cùng `error_code`; U5 không đổi lớp và không bọc lại, chỉ để ngữ cảnh ở dòng log.

**Phương án đã loại.** *Kiểm lười theo từng nguồn khi dùng*: nhanh hơn nhưng cho phép danh mục nửa đúng tới tay U6. *Bọc mọi lỗi thành một lớp chung*: làm mất khả năng phân biệt "thiếu tệp" với "nội dung sai", thứ mà CLI và U6 cần.

## ADR-U5-S2 — Tên bảng được kiểm bằng danh sách đóng của dự án

**Bối cảnh.** `tables` đi thẳng vào C3, rồi U3 dùng để dựng SQL. Một tên bảng gõ sai hoặc bị sửa xấu là một chuỗi lạ đi vào câu SQL.

**Quyết định.** Mỗi phần tử của `tables` phải nằm trong `SOURCE_TABLES` của `src/integration/schema.py` — tập chín tên tệp đã bỏ `.csv`. So theo dạng tên đó, không so với khoá logic của `TABLE_SPECS`. Tên lạ ném `SchemaError` nêu tên bảng và tên nguồn.

**Hệ quả.** Đơn vị chặn được lớp lỗi "tên bảng lạ" mà không cần C1. Nó **không** kiểm được "trường này thuộc bảng nào" — việc đó cần ánh xạ thực thể → bảng, chỉ C1 có, và C1 không nằm trong hợp đồng của U5. Khoảng trống đó được ghi thành rủi ro chuyển giao ở §4 của `security-requirements.md`; U3 vẫn phải kiểm định danh trước khi dựng SQL.

Bốn artifact chốt cùng một tập: `functional-design/rules.md` BR5.3 và `functional-design/entities.md` (ràng buộc của `SourceProfile`) nói `SOURCE_TABLES`; `functional-design/functional-spec.md` W1 bước 4 nói cùng phép kiểm; `nfr-requirements/security-requirements.md` SR-U5-14 là nơi phát biểu đầy đủ. Không còn chỗ nào nói `TABLE_SPECS` cho `tables` — `TABLE_SPECS` khoá bằng tên logic, khác dạng tên đi trong `tables`.

**Phương án đã loại.** *Mở rộng C2 để mang ánh xạ thực thể → bảng*: mở hợp đồng chỉ để phục vụ một phép kiểm là thay đổi lớn hơn nhu cầu. *Không kiểm gì*: để chuỗi lạ đi thẳng vào SQL của U3.

## ADR-U5-S3 — Nguồn mô phỏng bị loại bằng cấu trúc, không bằng một cờ rải rác

**Bối cảnh.** Nguồn mô phỏng rẻ nhất và nhanh nhất; nếu luật xếp hạng chạy trước, nó thắng mọi truy vấn và U3 nhận một nguồn không tồn tại để sinh SQL.

**Quyết định.** Tách **vị từ ứng viên** khỏi **luật xếp hạng**. Vị từ ứng viên là một hàm riêng: một nguồn là ứng viên khi `has_data` đúng, `missing_fields` rỗng, **và** `is_simulated` sai. Luật xếp hạng chỉ chạy trên danh sách ứng viên. Không có nhánh nào khác được đọc `is_simulated`.

**Hệ quả.** Nguồn mô phỏng không thể thắng bằng cách sửa chi phí hay độ trễ; nó vẫn xuất hiện trong `rejected_sources` với lý do "nguồn mô phỏng, chỉ dùng để so sánh". Nếu một nguồn mô phỏng vẫn lọt vào `selected_sources` do lỗi lập trình, `select_source` ném `SchemaError` (BR5.11) thay vì trả kết quả sai. Muốn đổi luật này phải sửa đúng một hàm.

**Phương án đã loại.** *Kiểm `is_simulated` sau khi xếp hạng*: dễ quên ở một nhánh mới. *Bỏ nguồn mô phỏng khỏi danh mục*: mất luôn khả năng minh hoạ việc loại nguồn mà FR4.2 đòi.

## ADR-U5-S4 — Danh mục cập nhật đi trong payload C3, không qua kênh thứ hai

**Bối cảnh.** Nhánh "không nguồn nào đủ trường" vẫn phải ghi các dòng `SourceChoice` với `is_selected = false` để bảng nguồn giải thích được vì sao không có kết quả. Nếu bản C7 đã cập nhật không có đường tới U6, bảng nguồn sẽ hiển thị trạng thái trước lần đề xuất.

**Quyết định.** `select_source` trả **`SourceSelection`** (C3) mang thêm trường `catalogue` là bản C7 đã cập nhật; khi thất bại, `NoSourceAvailableError` mang thuộc tính `catalogue` cùng bản đó. Hai trường cộng thêm này đã được ghi vào C3/C7 ngày 2026-11-08 trong `contract-summary.md`, đúng change policy "chỉ thêm trường". Cả hai nhánh dùng chung một hàm dựng danh mục mới (`dataclasses.replace`).

**Hệ quả.** U6 đọc bản C7 mới từ đúng một chỗ ở mỗi nhánh: `selection.catalogue` khi thành công, `error.catalogue` khi thất bại. Ngoại lệ còn mang `missing_fields` — hợp các trường không nguồn nào phủ, cùng giá trị với trường `missing_fields` của C3 — vì khi ném lỗi thì không có payload C3 nào được trả, và W3 bước 5 vẫn cần danh sách đó để hiển thị. Kiểu trả về của hàm vẫn là C3 đã công bố, nên U3 không phải đổi cách gọi.

**Phương án đã loại.** *Trả bộ đôi `(SourceSelection, SourceCatalogue)`*: làm lệch kiểu trả về so với C3 mà không có ghi chú hợp đồng. *Trả `SourceSelection` rỗng thay vì ném lỗi*: C3 khai `NoSourceAvailableError`, và U3 cần phân biệt "không có nguồn" với "chạy được nhưng rỗng".

## ADR-U5-S5 — Nội dung được ghi log là danh sách trắng

**Bối cảnh.** Đơn vị không đọc dữ liệu ô nào, nhưng tên nguồn, mã trường và thông điệp lỗi vẫn đi qua log và qua giao diện.

**Quyết định.** Chỉ bốn sự kiện ở `security-requirements.md` §3, và chỉ các trường: `source_count`, `query_count`, `simulated_count`, `query_id`, `source_name`, `rejected_count`, `pending_query_id`, `partial_reason`, `error_code`, `message`. Chuỗi tự do duy nhất là `message` của lỗi, và nó chỉ chứa tên nguồn, tên bảng, mã trường, mã truy vấn và **nhãn tương đối cố định** `config/integration-sources.yaml`.

**Hệ quả.** Không có giá trị ô dữ liệu, không có nội dung thô của YAML, không có đường dẫn tuyệt đối ngoài repo trong log hay trong thông điệp U6 hiển thị. Cách này khác `src/config.py` (đang nhúng đường dẫn tuyệt đối); với mã mới của U5, đường dẫn tương đối là chuẩn.

**Phương án đã loại.** *Ghi cả khối cấu hình đã nạp để dễ chẩn đoán*: chép toàn bộ tệp vào log, và log là tệp dùng chung với các đơn vị khác.

## ADR-U5-S6 — Kết quả tất định: khoá sắp xếp tường minh, không dựa vào thứ tự khai báo

**Bối cảnh.** Kết quả chọn nguồn được đối chiếu trong test và hiển thị trên màn hình. Nếu hai nguồn hoà nhau mà thứ tự phụ thuộc thứ tự dict hay thứ tự khai báo, kết quả đổi giữa các lần chạy và test thành không ổn định.

**Quyết định.** Sắp xếp bằng khoá `(cost_level, latency_ms, source_name)`; `source_name` là chốt chặn cuối. Không dùng `dict` để biểu diễn danh sách nguồn; dùng `tuple` giữ thứ tự khai báo cho phần trình bày, và luôn sắp lại trước khi chọn.

**Hệ quả.** Test có thể khẳng định kết quả chính xác, kể cả khi đảo thứ tự khai báo trong tệp cấu hình. Đổi luật xếp hạng là đổi đúng một biểu thức khoá.

**Phương án đã loại.** *Dựa vào thứ tự khai báo*: kết quả phụ thuộc tệp, không phải luật. *Sắp theo tên nguồn trước*: che mất tiêu chí chi phí mà FR4.1 đòi.

## ADR-U5-S7 — Kiểm kiểu tường minh, vì YAML không có kiểu

**Bối cảnh.** `yaml.safe_load` trả về đúng kiểu chữ người viết. `has_data: "false"` là chuỗi truthy, nên một nguồn "không có dữ liệu" vẫn qua vị từ ứng viên; `latency_ms: "800"` làm phép so sánh ném `TypeError`, tức một lỗi không thuộc ba lớp mà U6/U3 được dặn bắt.

**Quyết định.** Mỗi khoá có kiểu và miền mong đợi, được kiểm trước khi dùng: `has_data`/`is_simulated` phải là `bool` thật (không nhận `0/1`, không nhận chuỗi), `cost_level` phải là `int` trong 1..5 và **không** phải `bool` (`bool` là lớp con của `int` trong Python), `latency_ms` phải là `int >= 0`, `covered_fields`/`tables` phải là danh sách chuỗi, `source_name`/`label` phải là chuỗi. Sai kiểu hoặc ngoài miền → `ConfigurationError` nêu nguồn và khoá.

**Hệ quả.** Không còn đường nào để giá trị "gần đúng" lọt vào vị từ ứng viên hay phép sắp xếp. Người sửa cấu hình nhận thông điệp nêu đúng khoá sai, thay vì một `TypeError` ở giữa luồng.

**Phương án đã loại.** *Ép kiểu ngầm (`bool(...)`, `int(...)`)*: biến `"false"` thành `True` và `"abc"` thành lỗi khó hiểu. *Chỉ kiểm khi dùng*: lỗi xuất hiện ở nơi không còn ngữ cảnh để nêu tên khoá.

## ADR-U5-S8 — Ánh xạ truy vấn → trường đi trong danh mục, không qua tham số thứ hai

**Bối cảnh.** L1 nạp và kiểm ánh xạ truy vấn → trường cần, còn L3 cần chính ánh xạ đó để biết truy vấn đòi gì. Nếu nó chỉ tồn tại trong hàm nạp, hoặc phải truyền lại qua tham số thứ hai của `select_source`, thì hoặc L3 không có dữ kiện, hoặc người gọi phải giữ và truyền lại một dữ kiện nội bộ.

**Quyết định.** Ánh xạ đi trong `SourceCatalogue.query_fields` — một trường **cộng thêm** của C7 (ghi ngày 2026-11-08 trong `contract-summary.md`). `select_source` chỉ nhận danh mục và `query_id`; nó đọc ánh xạ từ danh mục.

**Hệ quả.** Chỉ một đường đi cho dữ kiện này, và nó đã được kiểm ở L1 trước khi tới L3. Đổi ánh xạ là đổi một chỗ trong tệp cấu hình. Payload C7 lớn thêm ba dòng chữ — không đáng kể.

**Phương án đã loại.** *Tham số `query_fields` riêng cho `select_source`*: người gọi phải giữ một mẩu trạng thái nội bộ, và hai nguồn sự thật có thể lệch nhau. *Đọc lại tệp cấu hình trong `select_source`*: hai lần đọc cho một thao tác và bỏ qua kết quả kiểm đã có.

## Bảng truy vết quyết định → yêu cầu

| Quyết định | Yêu cầu bảo mật | Chỉ tiêu |
|---|---|---|
| ADR-U5-S1 | SR-U5-11, SR-U5-13 | NFR1.1 |
| ADR-U5-S2 | SR-U5-14 | NFR3.1 |
| ADR-U5-S3 | SR-U5-6 | NFR5.1 |
| ADR-U5-S4 | SR-U5-11, SR-U5-12 | NFR1.1 |
| ADR-U5-S5 | SR-U5-7, SR-U5-8, SR-U5-16 | NFR3.1 |
| ADR-U5-S6 | SR-U5-12 | NFR1.1 |
| ADR-U5-S7 | SR-U5-15, SR-U5-11 | NFR2.1 |
| ADR-U5-S8 | SR-U5-5 | NFR1.1 |
