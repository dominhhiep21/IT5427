# Performance Test Instructions

## 1. Ngân sách đang áp

| ID | Hạng mục | Ngưỡng | Nơi kiểm | Trạng thái |
|---|---|---|---|---|
| NFR1 | Tầng `stats` trên dữ liệu thật | < 300 s | `test_u2_model_end_to_end.py` (`STAGE_BUDGET_SECONDS`) | xanh |
| NFR2 | Bước huấn luyện hai mô hình | < 240 s | cùng tệp (`TRAIN_BUDGET_SECONDS`) | xanh |
| PR3.1 | `score_item` một dòng hàng | < 200 ms (đo 10,5 ms) | `test_u3_prediction_section.py` | xanh |
| PR3.2 | `load_model` | < 2 s (đo 0,3 ms) | cùng tệp | xanh |
| PR3.3 | `build_prediction_body` | < 300 ms (đo ~2 ms) | cùng tệp | xanh |
| PR3.4 | Mở tab | không quá +20% | **đo tay** trước/sau, ghi vào `code-summary.md` | ghi nhận |

## 2. Cách đo

Ba ngưỡng PR3.1–PR3.3 là **ngưỡng bắt thoái hoá**, không phải mục tiêu: ngưỡng rộng 19–6.000 lần so với số đo thật để không đỏ vì runner chậm. Đo bằng `time.perf_counter()`: gọi nóng một lần, rồi trung bình 20 lần (riêng `load_model` 5 lần).

```
python -X utf8 -m pytest tests/unit/test_u3_prediction_section.py -q -k budget
```

Đo tay PR3.4: mở dashboard trên cây **trước** thay đổi và **sau**, ghi hai số. Không tự động hoá vì nó phụ thuộc máy và không đáng một test dễ nhiễu.

## 3. Khi một ngưỡng đỏ

1. Chạy lại **riêng** test đó khi máy rảnh — phân biệt nhiễu tải với thoái hoá thật.
2. Nếu vẫn đỏ: ghi số đo, tìm nguyên nhân (thêm I/O trong callback? nạp mô hình lặp?).
3. Nới ngưỡng chỉ khi có lý do ghi lại — cùng luật với ngân sách 300/240 trong `team.md`: "phải đo lại và sửa ngân sách **có chủ đích**, không nới ngầm".

## 4. Điều không đo trong đợt này

- Không có load test nhiều người dùng: dashboard bind `127.0.0.1`, một người dùng.
- Không có benchmark bộ nhớ: khối dựng một cây Dash nhỏ; tệp mô hình 4,8 KB.
- Không có SLO phần trăm độ khả dụng: công cụ chạy tay, không có dịch vụ nền.
