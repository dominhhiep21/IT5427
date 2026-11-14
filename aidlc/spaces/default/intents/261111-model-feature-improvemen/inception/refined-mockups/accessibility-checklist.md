# Accessibility Checklist — khối "Dự đoán"

Nguồn: `mockups.md`, `interaction-spec.md`, `../requirements-analysis/requirements.md` (NFR6, FR3.5), `../../ideation/rough-mockups/wireframes.md`, `assets/style.css`.

Mốc: **WCAG 2.1 AA**. Mỗi dòng có cách kiểm — không có mục nào là "đã xem xét".

| # | Yêu cầu | Mốc | Cách kiểm | Trạng thái |
|---|---|---|---|---|
| A1 | Mọi vùng nội dung có `aria-label` hoặc heading ngữ nghĩa | AA 1.3.1 | test đơn vị duyệt cây: mỗi `Section` có `aria-label` hoặc chứa `H3/H4` | phải đạt |
| A2 | Mỗi giá trị nhập có nhãn liên kết: `html.Label` bọc, hoặc `aria-label` cho `dcc.Dropdown`/`dcc.Checklist` | AA 1.3.1, 3.3.2 | test đơn vị đếm **nhãn truy cập được** = 11: `label[for]` cộng `aria-label` (dropdown và checklist không có `for` nên đếm riêng) | phải đạt |
| A3 | Không `tabIndex` dương; thứ tự tab = thứ tự đọc | AA 2.4.3 | test đơn vị trên danh sách `tabIndex` | phải đạt |
| A4 | Focus nhìn thấy được trên mọi phần tử tương tác | AA 2.4.7 | `outline` từ `--accent`; kiểm bằng mắt + ảnh | phải đạt |
| A5 | Tương phản chữ thường ≥ 4,5:1 trên mọi cặp (chữ, nền) dùng thật | AA 1.4.3 | `test_analysis_tab_contrast` mở rộng cho cặp mới; đọc token từ `assets/style.css` | phải đạt |
| A6 | **Không** dùng `--text-3` cho chữ < 16px | nội bộ (3,85:1) | test canh token: khối mới không tham chiếu `--text-3` | phải đạt |
| A7 | Hai kết quả phân biệt bằng **chữ**, không chỉ bằng màu — kể cả trạng thái **5** (chưa có ngưỡng) | AA 1.4.1 | test: trên ngưỡng chứa `CẢNH BÁO`; dưới ngưỡng chứa `KHÔNG cảnh báo`; **trạng thái 5 không được chứa cả hai** mà chứa "chưa có ngưỡng để so" | phải đạt |
| A8 | Kết quả mới được đọc lên **một lần**, không đọc lại cả tab | AA 4.1.3 | test: khối không có `aria-live` riêng; **và** nút con nhận kết quả là `div` không `aria-live` nằm trong `RESULT_BODY_ID` — nếu thay con trực tiếp của `RESULT_BODY_ID` (nó bọc cả panel, `analysis_tab.py:519-528`) thì cả tab bị đọc lại | phải đạt |
| A9 | Lỗi tại ô gắn với ô bằng `aria-describedby` | AA 3.3.1 | test: khi có lỗi, `id` phần tử lỗi xuất hiện trong `aria-describedby` của ô | phải đạt |
| A10 | Không mất nội dung khi phóng to 200% | AA 1.4.4 | mở dashboard ở 1280px và zoom 200%, xem bằng mắt | phải đạt |
| A11 | Không tràn ngang ở 1280px | NFR5.4 đợt trước | xem bằng mắt ở bước 4 của chuỗi xác nhận | phải đạt |
| A12 | Nhãn không phụ thuộc vị trí (nhãn đứng trước ô) | AA 1.3.2 | đọc cây thành phần | phải đạt |
| A13 | Ba đóng góp đọc được theo thứ tự có nghĩa: mỗi dòng có dấu `+`/`−` là **ký tự**, **tên trường**, **giá trị người dùng nhập** và **số log-odds** | AA 1.3.2 | test: mỗi `li` chứa đủ bốn phần; dấu là ký tự, không phải màu | phải đạt |
| A14 | Không có nội dung chỉ xuất hiện khi hover | AA 2.1.1 | duyệt spec: không tooltip | phải đạt |
| A15 | Trạng thái **3 (đang tính)**: có tín hiệu chờ nhìn thấy được và không đọc lại kết quả cũ | AA 4.1.3 | test: `dcc.Loading` có sẵn của thân tab bật trong lúc callback chạy; **không** kỳ vọng nút bị khoá (xem `design-system-mapping.md` — việc khoá nút cần output thứ 11 và đang là quyết định mở) | phải đạt |
| A16 | Trạng thái **5 (chưa có ngưỡng)**: chỉ hiện xác suất và "chưa có ngưỡng để so" | AA 3.3.1 | test: không có chuỗi `CẢNH BÁO` và không có chuỗi `KHÔNG cảnh báo` | phải đạt |
| A17 | Trạng thái **6 (mô hình chưa sẵn)**: câu hướng dẫn chứa nguyên văn lệnh và đường dẫn | AA 3.3.1 | test: chuỗi con `python -X utf8 -m src.pipeline run --stage stats` và `data/models/` | phải đạt |

## Ba chỗ dễ hỏng nhất khi viết mã

| Chỗ | Vì sao dễ hỏng |
|---|---|
| **A8** | Bản năng là bọc kết quả trong `aria-live` riêng. Hai vùng lồng nhau đọc hai lần, và không test nào bắt nếu chỉ kiểm "có aria-live". |
| **A7** | Bản năng là tô `--danger` cho kết quả cảnh báo. Nó đúng về cảm xúc nhưng sai về ngữ nghĩa (đỏ = lỗi hệ thống) và sai cho người mù màu. |
| **A5/A6** | Bản năng là dùng `--text-3` cho chú thích nhỏ vì các tab cũ đang dùng. Ở đây nó chỉ 3,85:1 — đã bị loại có ghi chép. |

## Điều checklist này không phủ

Không kiểm nội dung tiếng Việt có dễ đọc với người không phải người làm hay không — không có người dùng thứ hai để thử. Không kiểm với trình đọc màn hình thật: môi trường này không có, nên các mục A1/A2/A8/A9 kiểm bằng **cấu trúc cây thành phần**, không bằng trải nghiệm nghe. Đó là giới hạn thật, ghi lại thay vì bỏ qua.
