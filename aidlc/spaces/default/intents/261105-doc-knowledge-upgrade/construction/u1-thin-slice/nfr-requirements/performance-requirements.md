# Performance Requirements — u1-thin-slice

Nguồn: `inception/requirements-analysis/requirements.md` (NFR1), `construction/u1-thin-slice/functional-design/functional-spec.md`, `construction/u1-thin-slice/nfr-requirements/nfr-requirements-questions.md` (Q1 = A, Q2 = B).

Hai câu hỏi đã hỏi và đã trả lời: Q1 = A (giữ ngưỡng chung 2 giây), Q2 = B (có kiểm thử hiệu năng tự động). Các ngưỡng dưới đây thực thi hai câu trả lời đó.

| Mã | Yêu cầu | Đo bằng | Ngưỡng |
|---|---|---|---|
| NFR1.1 | Mở tab khi dữ liệu **đã nạp sẵn trong bộ nhớ** (lần mở thứ hai trở đi) | thời gian từ lúc bấm tab đến khi vùng số liệu dựng xong khung | dưới 2 giây |
| NFR1.2 | Chạy truy vấn đếm đơn theo tháng | `elapsed_ms` của truy vấn | dưới 2 giây |
| NFR1.3 | Nạp thực thể `don_hang` từ CSV | thời gian đọc tệp và dựng bản ghi | dưới 5 giây cho 99.441 đơn; lần nạp xảy ra **trong lần bấm "Chạy truy vấn" đầu tiên**, không phải lúc mở tab (Workflow 3: mở tab thì truy vấn không chạy) |
| NFR1.4 | Kiểm thử hiệu năng tự động cho truy vấn đếm đơn | một test đo riêng phần thực thi truy vấn (không tính thời gian nạp) | chạy trong bộ nhanh, ngưỡng cứng 2 giây, thất bại nếu vượt |

## Ghi chú

- **Ngân sách theo từng lần bấm, không cộng dồn:** lần bấm "Chạy truy vấn" **đầu tiên** gồm nạp tối đa 5 giây cộng truy vấn tối đa 2 giây, tức **7 giây** cho lần đó; mọi lần bấm sau chỉ còn truy vấn trên dữ liệu đã nạp, ngân sách **2 giây**. Mở tab không chạy truy vấn nên không có ngân sách riêng cho việc mở.
- Không có yêu cầu về bộ nhớ riêng: dữ liệu đơn vừa một DataFrame, và `config.yaml` đã đặt `quality.memory_warn_mb: 1536` / `quality.memory_fail_mb: 2048` làm giới hạn của dự án — dùng đúng hai ngưỡng đó, không thêm con số nào khác.
- **Đường ghép "bấm Chạy truy vấn → thẻ hiện số" có ngân sách 2 giây tổng.** NFR1.1 và NFR1.2 là ngưỡng của **từng bước** và không cộng dồn: đo từ lúc bấm nút đến khi thẻ hiện số phải dưới 2 giây, nên một bước dùng gần hết ngân sách là tín hiệu phải tối ưu, không phải hai ngân sách riêng.
- NFR1.4 cố ý đo riêng phần truy vấn để không đỏ ngẫu nhiên vì thời gian đọc đĩa.
