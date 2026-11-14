# Reliability Design — u1-statistics

Nguồn: `../nfr-requirements/reliability-requirements.md`, `../functional-design/rules.md` (BR1.6, BR1.9–BR1.11), `../../../inception/contract-design/contract-summary.md` (C1, C2).

## Phạm vi

Đơn vị chạy theo lệnh và kết thúc. Không có dịch vụ thường trực nên **không** có circuit breaker, retry, health check hay failover — chúng bảo vệ một thứ không tồn tại ở đây. Độ tin cậy nằm ở ba chỗ: không làm hỏng tệp đang có, không để một phép hỏng kéo cả tầng xuống, và không làm đổi kết quả giữa hai lần chạy.

## Quyết định

| # | Quyết định | Phục vụ | Vì sao |
|---|---|---|---|
| RD-1 | Ghi theo trình tự **tệp tạm → đọc lại kiểm → thay tệp**, với bước đọc lại do U1 tự thêm | REL-2, NFR3.4 | `AtomicWriter.write_json` hiện chỉ ghi tệp tạm rồi `os.replace`, **không** đọc lại (chỉ `write_parquet` kiểm số dòng), nên bước kiểm của BR1.11 phải nằm trong `report-writer` chứ không có sẵn trong lớp ghi |
| RD-2 | Mỗi phép kiểm định bọc trong một khối riêng; lỗi điều kiện thành `SkipEntry`, không phải ngoại lệ | REL-3 | BR1.6; một phép không đủ điều kiện không phải sự cố của cả tầng |
| RD-3 | Hàm đọc không ném; mọi hỏng hóc thành `ReportView` | REL-1 | U3 luôn có một giá trị để dựng giao diện, kể cả khi tệp hỏng |
| RD-4 | Thứ tự kiểm cố định khi đọc: tồn tại → parse → phiên bản → trường → khối | NFR3.4 | Hai lần đọc cùng một tệp cho cùng một trạng thái, không phụ thuộc thứ tự kiểm |
| RD-5 | Không dùng đồng hồ trong nội dung so sánh được; `generated_at` là trường duy nhất được phép khác giữa hai lần chạy | NFR3.4 | Điều kiện để phép so hai lần chạy có nghĩa |

## Lỗi ở đâu, bắt ở đâu

| Lỗi | Nơi phát sinh | Nơi bắt | Kết quả |
|---|---|---|---|
| Không đọc được mart | lớp đọc | biên CLI | mã thoát 1, không ghi tệp |
| Không có đơn đã giao | BR1.1 | biên CLI | mã thoát 1, không ghi tệp |
| Một phép không đủ điều kiện | BR1.2–BR1.5 | trong tầng | `null` + `SkipEntry`, chạy tiếp |
| Ghi hoặc đọc lại hỏng | BR1.11 | biên CLI | mã thoát 1, tệp cũ nguyên |
| Tệp báo cáo hỏng khi đọc | BR1.9 | trong hàm đọc | `loi`, không ném |

## Điều không làm

- Không thử lại khi đọc mart: một lần đọc hỏng là lỗi cấu hình hoặc lỗi dữ liệu, thử lại chỉ làm chậm việc báo lỗi.
- Không có bản sao lưu riêng: báo cáo sinh lại được từ mart bằng một lệnh, nên bản sao lưu là thứ thừa.
