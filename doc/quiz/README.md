# Bộ câu hỏi Quizizz — Tích hợp dữ liệu

Bộ 500 câu hỏi tiếng Việt, đóng gói đúng định dạng spreadsheet của Quizizz
(`Question Text`, `Question Type`, `Option 1..5`, `Correct Answer`, `Time in seconds`,
`Image Link`, `Answer explanation`).

Nội dung bám sát `doc/Quiz_DI.md` và 6 tệp bài giảng trong `doc/`:

| Nhóm | Bài giảng tương ứng |
|---|---|
| Nền tảng & dị biệt | `1. Introduction.pdf` |
| Ánh xạ lược đồ, GAV/LAV/GLAV | `2_SchemaAlignment.pdf` |
| Sinh truy vấn trung gian | `2_mediationquery.pdf` |
| Record linkage & entity resolution | `3_RecordLinkage_ER.pdf` |
| Xử lý truy vấn thích ứng | `4_QueryProcessing.pdf` |
| Wrapper, profiling, chọn nguồn | `5_SourcesSelection.pdf` |

## Danh sách tệp

| Tệp | Số câu | Nội dung |
|---|---:|---|
| `Quiz_DI_01_NenTang_DiBiet_A.xlsx` | 43 | Định nghĩa, mục tiêu, 6 mức dị biệt, kiến trúc ảo/kho |
| `Quiz_DI_01_NenTang_DiBiet_B.xlsx` | 41 | Wrapper, mediation, deep web, PAYGO, thách thức dữ liệu lớn |
| `Quiz_DI_02_AnhXaLuocDo_A.xlsx` | 33 | Certain answers, GAV, LAV, GLAV, unfolding |
| `Quiz_DI_02_AnhXaLuocDo_B.xlsx` | 34 | Ngữ nghĩa mapping, ví dụ GAV/LAV, mô tả nguồn |
| `Quiz_DI_02_AnhXaLuocDo_C.xlsx` | 32 | Dị biệt dữ liệu, unfolding, tổng kết (có Checkbox) |
| `Quiz_DI_03_TruyVanTrungGian.xlsx` | 50 | Phân rã cây con, partial mapping, đồ thị join, XQuery (có Checkbox) |
| `Quiz_DI_04_RecordLinkage_A.xlsx` | 33 | Bài toán, edit distance, q-gram, Jaccard, overlap |
| `Quiz_DI_04_RecordLinkage_B.xlsx` | 32 | TF/IDF, generalized Jaccard, soft TF/IDF, Soundex |
| `Quiz_DI_04_RecordLinkage_C.xlsx` | 36 | Pipeline ER, blocking, LSH, clustering, crowdsourcing |
| `Quiz_DI_05_QueryProcessing_A.xlsx` | 45 | System R, join algorithms, mức thích ứng, ripple/SHJ/XJoin |
| `Quiz_DI_05_QueryProcessing_B.xlsx` | 47 | Kết quả từng phần, Juggle/Eddy, AQP, chọn kỹ thuật |
| `Quiz_DI_06_NguonDuLieu_A.xlsx` | 45 | Wrapper, HLRT, Stalker, RoadRunner, tương tác |
| `Quiz_DI_06_NguonDuLieu_B.xlsx` | 29 | Profiling, min-hash, tóm tắt lược đồ, chọn nguồn |
| `Quiz_DI_TatCa_500_Cau.xlsx` | 500 | Bản gộp để rà soát hoặc thi một lượt dài |

## Cách nhập vào Quizizz

1. Đăng nhập Quizizz → **Create** → **Import from spreadsheet** (hoặc kéo tệp vào).
2. Chọn một tệp `.xlsx` ở trên.
3. Kiểm tra lại số câu và đáp án đúng ở màn hình xem trước, sau đó lưu quiz.

Mỗi tệp 30–50 câu phù hợp cho một lượt chơi; tệp gộp dùng khi cần rà soát toàn bộ
hoặc chia lại theo chủ đề.

## Đặc điểm thiết kế

- **4 lựa chọn cho mọi câu**, không dùng "tất cả đáp án trên" hay "không đáp án nào".
- **Không lộ đáp án qua độ dài**: câu đúng và câu nhiễu được viết cùng cấp độ chi tiết,
  chênh lệch độ dài trung bình khoảng 6 ký tự; bộ kiểm tra tự động không còn cảnh báo nào.
- **Vị trí đáp án đúng được cân bằng** (~25% mỗi cột) nhờ hoán vị có kiểm soát khi xuất tệp.
- **7 câu Checkbox** (nhiều đáp án) nằm ở nhóm ánh xạ lược đồ và truy vấn trung gian.
- **28 câu có tính toán** (edit distance, Jaccard, TF/IDF, Soundex, chi phí join) với
  phương án số có cùng độ dài.
- **Câu nhiễu cùng miền** (ví dụ nhầm GAV với LAV, nhầm `FindCands` với ngưỡng so khớp,
  nhầm `3(M+N)` với `2(M+N)`), không phải phương án vô nghĩa.
- **Giải thích đáp án** ở cột cuối để dùng cho chế độ học hoặc ôn tập.
- Thời gian mặc định 30 giây, câu Checkbox và câu tính toán 45 giây.

## Chỉnh sửa và tái tạo

- Câu hỏi gốc nằm trong `data/*.py`, mỗi tệp là một danh sách tuple
  `(câu hỏi, [4 lựa chọn], chỉ số đáp án, giải thích)`.
- `build_quiz.py` chuẩn hóa, kiểm tra trùng câu/trùng phương án, kiểm tra độ dài,
  hoán vị đáp án rồi xuất `.xlsx`:

```bash
python -X utf8 build_quiz.py          # xuất toàn bộ tệp
python -X utf8 build_quiz.py --check  # chỉ chạy kiểm tra chất lượng
```

- Kết quả kiểm tra ghi ở `check_report.txt`. Muốn thêm câu, thêm tuple vào tệp
  tương ứng trong `data/` rồi chạy lại; số câu trong bảng trên sẽ thay đổi theo.
