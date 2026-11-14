# User Stories Assessment

## Decision

Execute.

## Rationale

Đợt này thêm một bề mặt người dùng mới (tab kết quả) bên cạnh phần tính toán chạy nền, nên cần tiêu chí nghiệm thu nhìn thấy được. Yêu cầu FR4 mô tả trạng thái và thứ tự hiển thị, mà những thứ đó chỉ kiểm được qua hành vi người dùng.

## Factors considered

- Có giao diện người dùng mới, không chỉ thư viện hay CLI.
- Có ít nhất hai vai người dùng khác nhau: người chạy phân tích và người đọc báo cáo.
- Logic nghiệp vụ có điều kiện: trạng thái rỗng, trạng thái lỗi, báo cáo thiếu một phần.
- Không phải refactor thuần, không phải sửa lỗi đơn lẻ, không phải hạ tầng.

## Where stories add the most value

- Tab kết quả: mở tab, đọc tóm tắt, đọc từng mục, gặp trạng thái rỗng và lỗi.
- Phần mô hình: người đọc cần biết ngưỡng cảnh báo nghĩa là gì trước khi tin con số.
