# Units of Work — Nâng cấp tích hợp dữ liệu Olist

Sáu đơn vị, chia theo component (quyết định của người đặt yêu cầu), với đơn vị đầu là lát cắt chạy xuyên suốt theo thực hành đã chốt. Triển khai một khối duy nhất trong cùng repo; lịch thi công tuần tự.

Nguồn: `inception/domain-design/components.md` (sáu component, mười entity) và `inception/requirements-analysis/requirements.md` (sáu nhóm `FR`, sáu `NFR`).

| Unit ID | Directory | Tên | Kind | Độ phức tạp | Deploy |
|---|---|---|---|---|---|
| U1 | `u1-thin-slice` | Lát cắt xuyên suốt | service | M | monolith |
| U2 | `u2-mediated-schema` | Lược đồ trung gian | library | M | monolith |
| U3 | `u3-query-rewriter` | Viết lại truy vấn và ngữ nghĩa KPI | library | L | monolith |
| U4 | `u4-record-linkage` | Ghép bản ghi | library | M | monolith |
| U5 | `u5-source-selector` | Chọn nguồn dữ liệu | library | S | monolith |
| U6 | `u6-integration-ui` | Giao diện tab "Tích hợp" | ui | M | monolith |

Mọi đơn vị chạy trong cùng một app dashboard và cùng một lệnh pipeline. `U1` mang kind `service` vì nó là đường chạy được end-to-end khi mở app, không phải thư viện thuần.

## U1 — Lát cắt xuyên suốt

**Mục đích.** Chứng minh các mảnh khớp nhau trước khi làm rộng: một thực thể trung gian (`don_hang`) → một truy vấn viết lại (số đơn `delivered` theo tháng — chỉ cần bảng đơn) → một thẻ hiển thị trên tab mới.

**Sở hữu.** Đường đi tối thiểu xuyên `MediatedSchema`, `QueryRewriter` và `IntegrationUI`; phiên bản đầu của tệp khai báo lược đồ và của tệp cấu hình tab.

**Biên giới.** Chỉ một thực thể, một truy vấn, một thẻ, một trạng thái đầy đủ. Truy vấn của lát cắt cố ý chọn loại chỉ đọc bảng đơn để không cần `mat_hang`/`san_pham`; hai thực thể còn lại và hai truy vấn còn lại thuộc U2 và U3.

**Ghi chú.** Đơn vị này không phải tài liệu thiết kế; nó phải chạy được end-to-end bằng lệnh xác nhận của dự án. Vì U5 chưa tồn tại ở bước này, U1 đọc thẳng nguồn mặc định duy nhất là `olist_orders` và ghi rõ nguồn đó trên màn hình; U5 thay chỗ này khi được dựng.

## U2 — Lược đồ trung gian

**Mục đích.** Khai báo đủ ba thực thể (`don_hang`, `mat_hang`, `san_pham`) với ánh xạ tới cột nguồn, và kiểm tra mọi cột nêu trong ánh xạ tồn tại trong CSV thật.

**Sở hữu.** Tệp khai báo lược đồ (YAML/JSON), bộ nạp và kiểm tra hợp lệ, danh sách thực thể/ánh xạ cho các thành phần khác.

**Biên giới.** Không sinh SQL, không gọi DuckDB, không hiển thị gì.

## U3 — Viết lại truy vấn và ngữ nghĩa KPI

**Mục đích.** Ba truy vấn mẫu, sinh kế hoạch viết lại từng bước và SQL nguồn, chạy trên DuckDB, đối chiếu kết quả với định nghĩa KPI dùng chung.

**Sở hữu.** Truy vấn mẫu, kế hoạch viết lại, định nghĩa KPI và giá trị tham chiếu.

**Biên giới.** Không tự quyết định nguồn (nhận từ U5); không dựng giao diện.

**Ghi chú.** Lớp ngữ nghĩa KPI gộp vào đơn vị này vì định nghĩa và việc đối chiếu số liệu đi cùng nhau; tách ra sẽ tạo hai nơi phải sửa cùng lúc.

## U4 — Ghép bản ghi

**Mục đích.** Ghép khách hàng và người bán bằng khoá chặn và điểm tương đồng ở ngưỡng 0,85; ghi cặp ghép, cặp xem lại, và cặp bị bỏ qua kèm lý do.

**Sở hữu.** Luật chặn, cách tính điểm, danh sách cặp, tổng hợp cặp bị bỏ qua, tỉ lệ ghép đúng so với mốc `customer_unique_id`/`seller_id`.

**Biên giới.** Đọc trực tiếp bảng nguồn, không dùng lược đồ trung gian; không hiển thị.

**Ghi chú.** Kết quả tính một lần ở tầng pipeline và ghi ra `data/`; giao diện chỉ đọc lại.

## U5 — Chọn nguồn dữ liệu

**Mục đích.** Hồ sơ từng nguồn ứng viên và luật chọn nguồn cho một truy vấn, kèm lý do chọn/loại bằng chữ.

**Sở hữu.** Hồ sơ nguồn, kết quả chọn nguồn.

**Biên giới.** Không sinh SQL; không gọi mạng với nguồn mô phỏng.

## U6 — Giao diện tab "Tích hợp"

**Mục đích.** Tab mới với màn hình tổng quan bốn thẻ và bốn màn hình chi tiết, đủ bốn trạng thái, đạt WCAG 2.1 AA.

**Sở hữu.** Bố cục, điều hướng, trạng thái hiển thị, cách đọc dữ liệu từ năm đơn vị kia.

**Biên giới.** Không chứa logic tích hợp; ba tab cũ giữ nguyên.

**Ghi chú.** Thêm vào các tệp dashboard hiện có bằng `dcc.Tab` mới với nội dung `dmc`; phải cập nhật đồng thời các test khẳng định hình dạng dashboard.

## Ghi chú chung

- Mọi đơn vị nằm trong một khối duy nhất, chạy cùng một lệnh pipeline và một app dashboard.
- Ngôn ngữ hiển thị tiếng Việt, số theo định dạng Việt Nam.
- Mỗi đơn vị có test riêng; độ phủ `src/` giữ ≥ 80%.
- **NFR1 (dưới 2 giây mỗi tương tác)** do `U6` bảo đảm ở phía giao diện và `U4` bảo đảm ở phía dữ liệu (kết quả ghép tính sẵn ở tầng pipeline).
- **Việc sửa `src/analytics` để đọc định nghĩa KPI dùng chung** (ADR-003) thuộc `U3`.
