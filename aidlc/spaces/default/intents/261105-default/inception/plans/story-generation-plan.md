# Kế hoạch tạo User Stories

**Dự án**: Olist E-commerce Data Pipeline
**Giai đoạn**: INCEPTION - User Stories (Part 1: Planning)

## 1. Mục tiêu

Chuyển 11 yêu cầu chức năng trong `aidlc-docs/inception/requirements/requirements.md` thành:

- Persona đại diện cho các nhóm người dùng.
- Story theo INVEST, có tiêu chí chấp nhận kiểm thử được.
- Truy vết requirement → story → acceptance criteria.

## 2. Phương án phân rã

| Phương án | Ưu điểm | Hạn chế |
|---|---|---|
| **Feature-Based** | Bám sát FR-01…FR-11, dễ truy vết requirements | Có thể kém tự nhiên với luồng người dùng dashboard |
| **User Journey-Based** | Phản ánh cách analyst khám phá dữ liệu | Dễ bỏ sót yêu cầu hạ tầng/pipeline |
| **Persona-Based** | Rõ nhu cầu từng nhóm | Trùng lặp story giữa các persona |
| **Domain-Based** | Khớp miền nghiệp vụ (đơn hàng, giao vận, đánh giá) | Khó ánh xạ 1-1 sang FR |
| **Epic-Based** | Có cấu trúc lớn → nhỏ, phù hợp đồ án nhiều giai đoạn | Cần thêm bước tách story |

Đề xuất mặc định: **Epic-Based kết hợp Feature-Based** — epic theo miền nghiệp vụ, story bên dưới ánh xạ FR và persona.

## 3. Câu hỏi cần trả lời

Vui lòng điền chữ cái sau mỗi `[Answer]:`. Khi hoàn tất, trả lời `done`.

### Câu 1 — Persona
Bộ persona nào nên được tạo?

A) 2 persona: Chuyên viên phân tích dữ liệu và Giảng viên/người đánh giá
B) 3 persona: thêm Quản lý kinh doanh
C) 4 persona: thêm Kỹ sư dữ liệu/vận hành pipeline
D) Chỉ 1 persona: Chuyên viên phân tích dữ liệu
X) Khác (vui lòng mô tả sau thẻ [Answer]:)

[Answer]: A

### Câu 2 — Cách phân rã story
Chọn cách tổ chức story chính:

A) Feature-Based (bám FR-01…FR-11)
B) User Journey-Based (theo luồng khám phá của analyst)
C) Epic-Based (epic lớn, story con bên dưới)
D) Kết hợp Epic-Based + Feature-Based
X) Khác (vui lòng mô tả sau thẻ [Answer]:)

[Answer]: A

### Câu 3 — Độ chi tiết
Story nên ở mức nào?

A) Hai tầng: epic lớn + story nhỏ sẵn sàng triển khai
B) Chỉ story nhỏ, sẵn sàng triển khai
C) Chỉ epic lớn, không tách nhỏ
X) Khác (vui lòng mô tả sau thẻ [Answer]:)

[Answer]: A

### Câu 4 — Tiêu chí chấp nhận
Định dạng tiêu chí chấp nhận mong muốn?

A) Given/When/Then
B) Checklist gạch đầu dòng
C) Kết hợp Given/When/Then cho luồng chính + checklist cho kiểm tra dữ liệu
X) Khác (vui lòng mô tả sau thẻ [Answer]:)

[Answer]: A

### Câu 5 — Ưu tiên
Có cần gắn mức ưu tiên cho story không?

A) MoSCoW (Must/Should/Could/Won't)
B) P0/P1/P2
C) Không gắn ưu tiên
X) Khác (vui lòng mô tả sau thẻ [Answer]:)

[Answer]: A

### Câu 6 — Phạm vi story
Story nên bao phủ những gì?

A) Cả story người dùng dashboard và story kỹ thuật cho pipeline dữ liệu
B) Chỉ story người dùng dashboard
C) Chỉ story kỹ thuật pipeline/dữ liệu
X) Khác (vui lòng mô tả sau thẻ [Answer]:)

[Answer]: A

## 4. Checklist thực hiện

### Part 1 — Planning
- [x] Đánh giá nhu cầu User Stories
- [x] Tạo kế hoạch và câu hỏi
- [x] Thu thập câu trả lời
- [x] Phân tích mơ hồ/mâu thuẫn
- [x] Chốt phương án và được phê duyệt

### Part 2 — Generation
- [x] Tạo `personas.md`
- [x] Tạo `stories.md` với epic/story
- [x] Viết acceptance criteria cho từng story
- [x] Gắn persona với story
- [x] Kiểm tra INVEST
- [x] Cập nhật `aidlc-state.md`
- [ ] Trình bày để phê duyệt

## 5. Artifact bắt buộc

- `aidlc-docs/inception/user-stories/personas.md`
- `aidlc-docs/inception/user-stories/stories.md`
- Mỗi story có: ID, persona, câu chuyện, giá trị, acceptance criteria, requirement liên kết.

## 6. Quyết định đã chốt

| Hạng mục | Quyết định |
|---|---|
| Persona | 2 persona: Chuyên viên phân tích dữ liệu (P1) và Giảng viên/người đánh giá (P2) |
| Phân rã | Feature-Based; epic gom theo cụm chức năng, story bám FR |
| Độ chi tiết | Hai tầng: epic + story nhỏ sẵn sàng triển khai |
| Acceptance criteria | Given/When/Then cho mọi story |
| Ưu tiên | MoSCoW |
| Phạm vi | Cả story dashboard và story kỹ thuật pipeline |

**Cách xử lý story kỹ thuật với 2 persona**: story pipeline được viết dưới góc nhìn P1 (người hưởng lợi dữ liệu sạch) hoặc P2 (người kiểm chứng tính tái lập), không thêm persona kỹ sư. Phần triển khai kỹ thuật thuộc về story, không phải persona.

## 7. Cấu trúc epic đề xuất
| Epic | Tên | FR liên kết |
|---|---|---|
| E1 | Nền tảng ingestion và hợp đồng dữ liệu | FR-01, FR-08 |
| E2 | Làm sạch và chuẩn hóa dữ liệu Olist | FR-02 |
| E3 | Tích hợp star schema DuckDB/Parquet | FR-03 |
| E4 | Phân tích doanh thu và KPI | FR-04, FR-08 |
| E5 | Dashboard Plotly Dash | FR-05 |
| E6 | Micro-batch và dữ liệu IBGE | FR-06, FR-07 |
| E7 | Vận hành, tài liệu và ML tùy chọn | FR-09, FR-10, FR-11 |

**Ước lượng**: 7 epic, khoảng 18-22 story nhỏ. Mỗi story có ID `US-xx`, persona, MoSCoW, Given/When/Then và liên kết FR.

## 8. Tiêu chí hoàn thành giai đoạn

- [ ] `personas.md` có 2 persona đầy đủ mục tiêu, nỗi đau, nhu cầu.
- [ ] `stories.md` có 7 epic và toàn bộ story nhỏ.
- [ ] Mọi story có acceptance criteria Given/When/Then.
- [ ] Mọi story ánh xạ tới ít nhất một FR.
- [ ] Không có story nào vi phạm INVEST.
- [ ] Người dùng phê duyệt artifact.
