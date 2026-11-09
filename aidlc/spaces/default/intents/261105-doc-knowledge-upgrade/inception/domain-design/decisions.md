# Architecture Decisions — Domain Design

## ADR-001: Tách bốn nhóm chủ đề thành bốn component độc lập trong `src/integration/`

**Context.** Bốn nhóm chủ đề (lược đồ trung gian, viết lại truy vấn, ghép bản ghi, chọn nguồn) có thể nằm chung một khối hoặc rải vào các package sẵn có (`ingest`, `analytics`, `clean`, `pipeline`). Mã hiện tại đã có ranh giới rõ theo tầng dữ liệu, nên đặt sai chỗ sẽ làm lẫn trách nhiệm.

**Decision.** Bốn component độc lập (`MediatedSchema`, `QueryRewriter`, `RecordLinkage`, `SourceSelector`) cùng `SemanticLayer`, đặt trong package mới `src/integration/`, mỗi component một thư mục. `IntegrationUI` không nằm trong package này mà thêm vào dashboard hiện có (xem ADR-004).

**Consequences.**
- Tích cực: mỗi component thay đổi độc lập, kiểm thử riêng được, thư mục mới không lẫn với tầng dữ liệu cũ; người chấm nhìn thấy bốn nhóm tương ứng bốn thư mục.
- Tiêu cực: thêm một package và một lớp cấu trúc nữa bên cạnh `src/clean`, `src/integrate`; phải giữ kỷ luật không import chéo lung tung.
- Neutral: tổng số file tăng so với gộp một khối.

**Alternatives Rejected.**
- Một khối `Integration` duy nhất: ít file hơn nhưng bốn nhóm dùng chung một vòng đời, sửa một nhóm phải chạy lại test của cả khối, khó chỉ ra ranh giới khi trình bày.
- Rải vào các package sẵn có: tận dụng cấu trúc cũ nhưng trộn khái niệm tích hợp với tầng clean/integrate, và làm khó việc chỉ rõ "đây là phần thể hiện lý thuyết".

## ADR-002: Khai báo lược đồ trung gian bằng tệp YAML/JSON

**Context.** Lược đồ trung gian cần dễ đọc cho người chấm và dễ kiểm tra tự động; ba cách khả dĩ là tệp khai báo, mã Python, hoặc bảng trong DuckDB.

**Decision.** Khai báo bằng tệp dữ liệu (YAML/JSON) đọc lúc chạy, đặt cạnh `config.yaml`. Mã chỉ đọc và kiểm tra, không sinh lược đồ từ mã.

**Consequences.**
- Tích cực: người không đọc mã vẫn xem được ánh xạ; thêm thực thể chỉ là sửa dữ liệu; kiểm tra cột nguồn chạy được trên tệp khai báo.
- Tiêu cực: mất kiểm tra kiểu của Python ở thời điểm viết; phải tự kiểm tra cấu trúc khi đọc.
- Neutral: cần thêm một bước kiểm tra hợp lệ khi nạp.

**Alternatives Rejected.**
- Khai báo bằng dataclass Python: có kiểu nhưng trộn dữ liệu vào mã, sửa ánh xạ thành sửa mã.
- Bảng trong DuckDB: truy vấn được nhưng phải chạy pipeline trước khi xem được lược đồ, và người chấm không đọc được khi chưa có dữ liệu.

## ADR-003: Tách lớp ngữ nghĩa KPI thành module dùng chung

**Context.** KPI hiện được tính trong `src/analytics` và dashboard đọc lại; phần viết lại truy vấn mới cũng cần cùng con số để đối chiếu. Nếu mỗi nơi tự định nghĩa, số liệu sẽ lệch.

**Decision.** Tạo `SemanticLayer` giữ định nghĩa KPI (mã, công thức, định nghĩa doanh thu, đơn vị). `analytics`, `QueryRewriter` và dashboard đọc từ đó.

**Consequences.**
- Tích cực: một định nghĩa duy nhất; đối chiếu FR2.5 có chỗ dựa; dashboard và truy vấn không lệch số.
- Tiêu cực: phải sửa `src/analytics` để đọc từ module mới, chạm vào mã đang chạy ổn — cần làm cẩn thận để không hồi quy KPI.
- Neutral: thêm một lớp gián tiếp nhỏ.

**Alternatives Rejected.**
- Giữ KPI trong `src/analytics` và thêm lớp mỏng: ít rủi ro hơn nhưng truy vấn mới phải import từ tầng analytics, tạo phụ thuộc ngược chiều với kiến trúc hiện có.
- Lưu KPI trong bảng DuckDB: truy vấn được nhưng phải chạy pipeline mới xem được định nghĩa, và định nghĩa trở thành dữ liệu sinh ra thay vì tài liệu đọc được.

## ADR-004: Mã giao diện tab mới nằm trong các tệp dashboard hiện có

**Context.** Tab mới cần thêm vào dashboard đang dựng bằng `dcc.Tabs`; có thể tách package riêng hoặc thêm trực tiếp.

**Decision.** Thêm trực tiếp vào `src/dashboard/app.py` và các tệp hiện có, dùng `dcc.Tab` mới với nội dung dựng bằng `dmc`.

**Consequences.**
- Tích cực: không phải đổi khung tab hiện có, ba tab cũ không bị chạm markup; ít file mới.
- Tiêu cực: `app.py` to hơn; khi tab mới phình ra sẽ phải tách sau.
- Neutral: phải cập nhật đồng thời các test khẳng định hình dạng dashboard (số tab, số callback, số output).

**Alternatives Rejected.**
- Package riêng `src/dashboard/integration/`: gọn hơn về lâu dài nhưng thêm một lớp gián tiếp ngay từ đầu, trong khi tab mới chỉ có năm màn hình.
- Đổi toàn bộ dashboard sang `dmc.Tabs`: giao diện đồng nhất hơn nhưng chạm markup ba tab cũ, trái với cam kết giữ nguyên hành vi ba tab trong đợt này.

## ADR-005: Ghép bản ghi đọc trực tiếp bảng nguồn, không qua lược đồ trung gian

**Context.** Lược đồ trung gian của đợt này chỉ có ba thực thể (đơn, mặt hàng, sản phẩm), trong khi ghép bản ghi cần khách hàng và người bán.

**Decision.** `RecordLinkage` đọc trực tiếp `olist_customers_dataset` và `olist_sellers_dataset`, không phụ thuộc `MediatedSchema`.

**Consequences.**
- Tích cực: không phải mở rộng lược đồ trung gian ngoài phạm vi; ghép bản ghi kiểm thử độc lập.
- Tiêu cực: khi thêm thực thể khách/người bán ở đợt sau, phải sửa `RecordLinkage` để đọc qua lược đồ; đây là nợ kỹ thuật có chủ đích.
- Neutral: hai đường đọc dữ liệu song song trong cùng đợt.

**Alternatives Rejected.**
- Thêm `khach_hang` và `nguoi_ban` vào lược đồ trung gian ngay: sạch hơn về dài hạn nhưng vượt phạm vi ba thực thể đã chốt và đội thời gian 1–2 tuần.
- Bỏ hẳn ghép bản ghi khỏi đợt này: giảm khối lượng nhưng mất một trong bốn nhóm chủ đề bắt buộc.
