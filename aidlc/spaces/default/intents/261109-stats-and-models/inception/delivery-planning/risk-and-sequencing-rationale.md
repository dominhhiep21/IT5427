# Risk and Sequencing Rationale

Nguồn: `bolt-plan.md`, `../feasibility/raid-log.md`, `../units-generation/unit-of-work-dependency.md`.

## Vì sao gộp U1 và U2 vào một đợt

Hai đơn vị cùng sở hữu một bản hợp đồng: kiểu báo cáo, hàm ghi và hàm đọc. Tách thành hai đợt thì đợt đầu buộc phải chốt một bản hợp đồng chỉ có một nửa khối, rồi đợt sau lại sửa chính bản hợp đồng đó — đúng loại rework mà bước Contract Design muốn tránh. Gộp lại thì hợp đồng chỉ mở một lần. [Q1]

## Vì sao U3 đứng sau

Tab đọc báo cáo; không có báo cáo thật thì mọi kiểm tra giao diện chỉ là giả lập. Đặt U3 sau cùng cũng cho phép dùng chính báo cáo thật làm dữ liệu kiểm cho năm trạng thái. [Q2]

## Rủi ro theo đợt

| Đợt | Rủi ro chính | Cách giảm |
|---|---|---|
| Bolt 1 | Rò rỉ đặc trưng; mất cân bằng lớp; mốc chia tự chọn | Chốt danh sách đặc trưng trước khi huấn luyện; báo cáo AUC kèm cỡ mẫu; giữ mốc chia trong hợp đồng |
| Bolt 2 | Tab làm đỏ ba test hình dạng; bố cục vỡ ở 1280px | Sửa test trong cùng thay đổi; xem bằng mắt trước khi duyệt |

## Điều không đổi

Thứ tự đợt không được đảo: DAG là chuỗi U1 → U2 → U3, và Bolt 1 chứa cả U1 lẫn U2 nên không còn đường tắt nào. [Q2]

## Điều đã xảy ra so với dự tính

Hợp đồng vẫn phải mở lại một lần, ở giai đoạn thiết kế chức năng của U1: bản 1 thiếu chỗ cho lý do bỏ qua và thiếu trạng thái rỗng, nên nó được sửa lên bản 2 trước khi có dòng mã nào. Đó đúng là loại rework mà việc gộp U1 và U2 nhắm tránh, và nó dừng ở mức sửa tài liệu thay vì sửa mã — lý do gộp vẫn giữ nguyên hiệu lực.

## Điểm dừng

Người làm duyệt ở mỗi mốc trong đợt và ở cuối mỗi đợt, sau khi chuỗi xác nhận bốn bước xanh. [Q3][Q4]
