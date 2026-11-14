# Rules — u3-display

Nguồn: `../../../inception/requirements-analysis/requirements.md` (FR4.1–FR4.3, NFR5), `../../../inception/contract-design/contract-summary.md` (C2), `../../../inception/user-stories/stories.md` (US4.1), `functional-design-questions.md`, và `entities.md`.

`category` chỉ dùng năm giá trị: `validation`, `authorization`, `constraint`, `calculation`, `policy`.

```yaml
rules:
  - id: BR3.1
    category: policy
    statement: Tab ánh xạ thẳng ReportView.status thành token giao diện, không tự suy diễn
    applies_to: ResultTabState.token
    trigger: Mỗi lần đọc báo cáo
    logic: "IF status = rong THEN token = rong; day-du → day-du; mot-phan → mot-phan; loi → loi. Chỉ chua-chay do giao diện tự sinh khi đang đọc"
    violation: "Không được tự đặt token khác với status; không dò chuỗi thông điệp để đoán trạng thái"
    source: FR4.2

  - id: BR3.2
    category: policy
    statement: Thứ tự đọc cố định — tóm tắt, rồi thống kê, rồi mô hình
    applies_to: ReportSection
    trigger: Khi dựng tab ở trạng thái day-du hoặc mot-phan
    logic: "IF dựng tab THEN thứ tự section_id là tom-tat, thong-ke, mo-hinh, không đổi theo dữ liệu"
    violation: "Không được đảo thứ tự hay ẩn mục thống kê để làm nổi mô hình"
    source: FR4.1

  - id: BR3.3
    category: constraint
    statement: Dải tóm tắt có đúng bốn thẻ, thẻ AUC luôn kèm dấu đạt hay không đạt
    applies_to: SummaryCard
    trigger: Khi dựng dải tóm tắt
    logic: "IF token là day-du hoặc mot-phan THEN dựng các thẻ có nguồn dữ liệu, theo thứ tự ti-le-tre, so-don, so-bo-qua, auc. Nguồn: ti-le-tre từ late_rate.rate (phân số 0–1, nhân 100 khi hiện phần trăm) và late_rate.total; so-don từ late_rate.total; so-bo-qua từ len(skipped); auc từ model.auc. IF thiếu khối model THEN bỏ thẻ auc, hoặc ghi 'chưa có' nếu vẫn giữ chỗ. IF thiếu khối stats THEN chỉ còn thẻ auc"
    violation: "Không được dựng thẻ không có nguồn; không được tính doanh thu hay bất kỳ số nào không có trong tệp"
    source: FR4.1, Q2

  - id: BR3.4
    category: policy
    statement: Thiếu một khối thì vẫn hiện phần có, và ghi rõ phần thiếu kèm lệnh cần chạy
    applies_to: ResultTabState.notice và ReportSection
    trigger: Khi status = mot-phan
    logic: "IF 'model' trong missing THEN dựng khối thống kê đầy đủ; ở chỗ khối mô hình ghi 'chưa chạy bước mô hình' + lệnh. IF 'stats' trong missing THEN dựng khối mô hình đầy đủ; ở chỗ khối thống kê ghi 'chưa chạy bước thống kê' + cùng lệnh; dải tóm tắt chỉ còn thẻ auc — `skipped` nằm trong chính khối thống kê đang thiếu"
    violation: "Không được coi mot-phan là lỗi, và không được ẩn phần đang có vì phần kia thiếu"
    source: FR4.2, Q3

  - id: BR3.5
    category: policy
    statement: rong, mot-phan và loi có câu chữ khác nhau, không dùng chung một thông điệp
    applies_to: ResultTabState.notice
    trigger: Khi dựng tab ở ba trạng thái đó
    logic: "IF rong THEN nêu chưa có báo cáo + lệnh; IF mot-phan THEN nêu phần thiếu; IF loi THEN nêu lý do + đường dẫn tệp"
    violation: "Một câu chữ dùng cho hai trạng thái là gộp mất thông tin người đọc cần"
    source: FR4.2

  - id: BR3.6
    category: constraint
    statement: Kiểm định bị bỏ qua được liệt kê, không bị ẩn
    applies_to: SkippedBanner
    trigger: Khi dựng tab ở day-du hoặc mot-phan
    logic: "IF len(skipped) > 0 THEN dựng dải, mỗi phần tử một dòng (tên phép, lý do); ELSE không dựng"
    violation: "Ẩn skipped là trình bày một báo cáo đầy đủ hơn thực tế"
    source: FR1.4, FR5.1

  - id: BR3.7
    category: constraint
    statement: Ngưỡng cảnh báo được hiển thị nhưng không sửa được
    applies_to: Khối mô hình
    trigger: Khi dựng mục mô hình
    logic: "IF có khối model THEN hiện threshold, precision, recall như số đọc; không dựng thanh trượt hay ô nhập"
    violation: "Không được tính lại precision/recall ở ngưỡng khác trong trình duyệt — hợp đồng C3 không mang dữ liệu để làm việc đó"
    source: FR4.1, Q1

  - id: BR3.8
    category: validation
    statement: Mọi vùng có nhãn cho trình đọc màn hình, đi được bằng bàn phím, tương phản đạt như các tab hiện có, và bố cục không vỡ ở 1280px
    applies_to: Toàn tab
    trigger: Khi dựng và khi kiểm
    logic: "IF dựng vùng THEN mỗi vùng mang aria-label; mọi phần tử tương tác nhận focus theo thứ tự đọc; màu chữ và nền lấy từ token đã có nên tương phản giữ nguyên mức hiện tại; IF chiều rộng 1280px THEN không tràn ngang, không cắt chữ"
    violation: "Thiếu nhãn hoặc vỡ bố cục ở 1280px là không đạt NFR5"
    source: NFR5, FR4.3

  - id: BR3.9
    category: constraint
    statement: Chỉ dùng token và thành phần sẵn có trong assets/style.css
    applies_to: Toàn tab
    trigger: Khi dựng
    logic: "IF cần màu, khoảng cách, cỡ chữ THEN lấy từ token đã có; không thêm bộ thành phần mới"
    violation: "Thêm bộ thành phần mới là mở một hệ thiết kế thứ hai trong cùng dashboard"
    source: FR4.3
  - id: BR3.10
    category: constraint
    statement: Mục con có thể null được hiện bằng câu chữ, không bỏ trống và không hiện ô rỗng
    applies_to: Mục thống kê
    trigger: Khi dựng mục thống kê ở day-du hoặc mot-phan có khối stats
    logic: "IF correlation, group_test hoặc seasonal là null THEN hiện tên phép kèm 'không chạy được' và lý do lấy từ SkippedBanner cùng tên phép; IF comparisons rỗng THEN hiện câu nêu không đủ hai bang đạt ngưỡng 100 đơn; không vẽ khung rỗng cho mục thiếu"
    violation: "Bỏ trống một mục là trình bày báo cáo đầy đủ hơn thực tế; hiện ô rỗng là để người đọc đoán"
    source: FR1.4
```

## Tóm tắt quy tắc

| Mã | Loại | Một dòng |
|---|---|---|
| BR3.1 | policy | Ánh xạ thẳng `status` thành token, không suy diễn |
| BR3.2 | policy | Thứ tự tóm tắt → thống kê → mô hình |
| BR3.3 | constraint | Bốn thẻ, thẻ AUC luôn có dấu đạt/không đạt |
| BR3.4 | policy | Thiếu khối mô hình vẫn hiện thống kê, ghi rõ phần thiếu |
| BR3.5 | policy | Ba trạng thái ba câu chữ khác nhau |
| BR3.6 | constraint | Kiểm định bị bỏ được liệt kê |
| BR3.7 | constraint | Ngưỡng chỉ đọc, không sửa |
| BR3.8 | validation | Nhãn, bàn phím, 1280px |
| BR3.9 | constraint | Chỉ dùng token sẵn có |

## Kiểm tra ràng buộc

| Mã | Kiểm bằng |
|---|---|
| BR3.1 | Năm `ReportView` mẫu → năm token đúng |
| BR3.2 | Danh sách `section_id` theo đúng thứ tự |
| BR3.3 | Bốn thẻ; `auc_below_target` true/false → hai câu chữ khác nhau |
| BR3.4 | `mot-phan` có `stats`, thiếu `model` → khối thống kê vẫn dựng |
| BR3.5 | Ba câu chữ đôi một khác nhau |
| BR3.6 | `skipped` rỗng → không dải; hai phần tử → hai dòng |
| BR3.7 | Không có `dcc.Slider`/`Input` trong mục mô hình |
| BR3.8 | Kiểm nhãn trên cây thành phần; xem bằng mắt ở 1280px |
| BR3.9 | Không có lớp CSS mới ngoài `assets/style.css` |
