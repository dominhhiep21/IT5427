# Cost Analysis

## 1. Chi phí tiền

**0 đồng.** Không có cloud, không có dịch vụ trả phí: chạy trên máy phát triển, dữ liệu Olist công khai, không có API trả tiền. Lời gọi IBGE là API công khai, không tính phí, và chỉ xảy ra khi cache thiếu.

CI chạy trên GitHub Actions: nếu repo riêng tư, runner Windows tính gấp đôi phút Linux; với job ~3–5 phút và vài lần đẩy mỗi ngày, vẫn trong hạn mức miễn phí. Đây là chi phí **tiềm năng**, không phải chi phí đã phát sinh.

## 2. Chi phí thời gian (thứ thực sự đắt ở đây)

| Việc | Thời gian | Ghi chú |
|---|---|---|
| Pipeline đầy đủ | ~18,3 s | 6 tầng trên 1,55 triệu dòng |
| Bộ test nhanh | 13,9 s | phải xanh trước mỗi lần commit |
| Bộ test chậm | 52,3 s | chạy trước khi phát hành |
| Cổng phủ đầy đủ | 79,1 s | gộp cả hai bộ |
| Kiểm bằng mắt | vài phút | bước duy nhất cần người |

## 3. Chi phí lưu trữ

| Thư mục | Kích thước ước tính | Bị commit? |
|---|---|---|
| `dataset/` | ~120 MB | có (dữ liệu gốc, bất biến) |
| `data/cleaned` + `data/marts` | vài chục MB Parquet | không |
| `warehouse/olist.duckdb` | vài MB | không |
| `logs/` | 10 tệp JSONL gần nhất | không |

## 4. Nơi đáng tối ưu, theo thứ tự

1. **Bộ test nhanh chạy 13,9 s nhưng 5 test cần `warehouse/`** (`TD-09`). Sửa `TD-09` sẽ làm bộ nhanh hermetic và bỏ được bước dựng pipeline trong CI — tiết kiệm ~20 s mỗi lần chạy CI và bỏ một phụ thuộc ngầm.
2. **Tệp ghép 4,07 MB sát trần 5 MB**: tăng trần hoặc giảm số cặp lưu. Đây là biên mỏng nhất của hệ.
3. **`src/pipeline/stages.py` chỉ 52% phủ**: phần chưa phủ là đường chạy từng tầng, đúng loại dễ hỏng khi vận hành.

## 5. Không đáng tối ưu

- Thời gian pipeline 18 s: không phải nút thắt; tối ưu thêm không đổi trải nghiệm.
- Bộ nhớ: chưa lần nào chạm ngưỡng cảnh báo.
- Chi phí cloud: không có.
