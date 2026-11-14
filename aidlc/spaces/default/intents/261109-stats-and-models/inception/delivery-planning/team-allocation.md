# Team Allocation

Bối cảnh: dự án một người; bước Team Formation đã bỏ qua vì không có nhóm. [Q1]

| Vai | Người | Đợt | Ghi chú |
|---|---|---|---|
| Người làm dự án | 1 | Cả hai đợt | Quyết định phạm vi, viết mã, duyệt từng mốc |
| Trợ lý AI | 1 phiên | Cả hai đợt | Sinh mã và test theo hợp đồng đã duyệt, không tự đổi phạm vi |

## Nhịp duyệt

- Dừng ở mỗi mốc trong đợt để người làm duyệt. [Q3]
- Cuối mỗi đợt, người làm chạy chuỗi xác nhận bốn bước và quyết định sang đợt kế. [Q4]

## Điều không có

- Không có review chéo, không có người phê duyệt thứ hai — theo thực hành đã chốt của nhóm.
- Không có nhóm trực ca; mọi việc nằm ở một người.

## Rủi ro nhân sự

Một người làm cả hai đợt nghĩa là không có ai kiểm độc lập ngoài kiểm tra tự động. Bù bằng: test end-to-end trên dữ liệu thật và rà soát của kiến trúc sư ở các stage thiết kế.
