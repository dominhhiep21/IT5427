# Câu hỏi — Thiết kế chức năng cho u2-model

## Q1. [Tech] Chỗ ghi "cách chọn ngưỡng" và dấu "AUC dưới 0,70"

Bối cảnh: FR2.4 đòi báo cáo ghi ngưỡng, precision, recall **và cách chọn**; US2.1 đòi ghi rõ khi AUC dưới 0,70 là "không đạt, không ẩn đi". Hợp đồng C1 phiên bản 2 chỉ có bảy trường cho khối mô hình, không có chỗ cho hai thông tin đó.

A. Thêm hai trường vào khối mô hình và tăng `REPORT_VERSION` lên 3; U1 và U3 cập nhật cùng lúc
B. Đặt cả hai trong `counts` dưới hai khoá riêng — không đổi hợp đồng, nhưng `counts` thành chỗ chứa lẫn đếm và metadata
C. Không ghi trong báo cáo, chỉ ghi nhật ký — US2.1 chỉ đạt một nửa
X. Other (please specify)

[Answer]: B

## Q2. [Product] Tiêu chí chọn ngưỡng cảnh báo

Bối cảnh: kế hoạch nói ngưỡng "chọn từ đường cong precision/recall" nhưng chưa chốt tiêu chí. Mỗi tiêu chí cho một ngưỡng rất khác nhau, và ngưỡng là con số người đọc sẽ dùng để gắn cờ đơn.

A. Chọn ngưỡng làm F1 cao nhất trên tập kiểm tra
B. Chọn ngưỡng thấp nhất mà recall đạt tối thiểu 0,60 — ưu tiên không bỏ sót đơn trễ
C. Chọn ngưỡng thấp nhất mà precision đạt tối thiểu 0,50 — ưu tiên không báo nhầm
X. Other (please specify)

[Answer]: A

## Q3. [Tech] Xử lý mất cân bằng lớp

Bối cảnh: khoảng 8,11% đơn là trễ, tức khoảng 11 đơn đúng trên 1 đơn trễ. Mô hình không xử lý gì sẽ thiên về dự đoán "không trễ".

A. Dùng `class_weight="balanced"` của mô hình, không đổi dữ liệu
B. Lấy mẫu lại tập huấn luyện (giảm mẫu lớp đa số)
C. Không xử lý; để nguyên và báo cáo trung thực
X. Other (please specify)

[Answer]: A
