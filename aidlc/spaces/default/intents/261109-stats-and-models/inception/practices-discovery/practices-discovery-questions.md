# Câu hỏi — Xác nhận cách làm việc của nhóm

Bản nháp đã dựa trên bằng chứng trong repo tại commit `ea77bdf`. Dưới đây chỉ hỏi những điểm bằng chứng không tự trả lời được.

## Q1. [Product] Nhánh làm việc và cổng CI

Hiện `ci.yml` chỉ chạy khi push lên `main` và `feature/update-ui-ux`, trong khi đợt này làm trên nhánh mới nên chưa có cổng tự động.

A. Thêm nhánh đang làm vào danh sách trigger của `ci.yml`
B. Giữ nguyên, chấp nhận là đợt này không có CI tự động
C. Chuyển sang làm trực tiếp trên `main`
D. Not yet defined
X. Other (please specify)

[Answer]: A

## Q2. [Product] Có dựng một lát cắt mỏng chạy xuyên suốt trước không

Lát cắt mỏng là bản tối thiểu chạy hết đường đi, dựng trước để chứng minh các mảnh khớp nhau. Ở đợt này nó sẽ là: một phép kiểm định chạy được, ghi báo cáo, và hiện được trên tab mới.

A. Có, dựng lát cắt mỏng trước rồi mở rộng
B. Không, làm từng phần trọn vẹn theo thứ tự đã chốt
C. Not yet defined
X. Other (please specify)

[Answer]: B

## Q3. [Product] Cách viết test của đợt này

Bằng chứng tĩnh không phân biệt được thứ tự, nên đây là quyết định của bạn. Phần mô hình thường khó viết test trước hơn phần còn lại.

A. Giữ nguyên: viết test trước rồi mới viết mã (TDD)
B. Test trước cho phần thống kê và CLI, test sau cho phần mô hình
C. Test sau cho toàn bộ đợt này
D. Not yet defined
X. Other (please specify)

[Answer]: A

## Q4. [Product] Lệnh thống kê nằm ở đâu trong chuỗi xác nhận

Chuỗi hiện tại là: `pytest -m "not slow"` → `pipeline run --stage all` → mở dashboard.

A. Thêm lệnh thống kê thành bước thứ ba, trước khi mở dashboard
B. Chỉ chạy lệnh thống kê khi cần, không đưa vào chuỗi xác nhận
C. Gộp vào `run --stage all` như một tầng mới
D. Not yet defined
X. Other (please specify)

[Answer]: A

## Q5. [Tech] Hình dạng lệnh thống kê

A. Một lệnh con mới, ví dụ `python -m src.pipeline stats`
B. Một tầng mới trong chuỗi `run --stage`, ví dụ `run --stage stats`
C. Not yet defined
X. Other (please specify)

[Answer]: B

## Q6. [Product] Cổng phủ 80% chạy ở đâu

`ci.yml` tính phủ trên toàn bộ bộ test (gồm cả test chậm); README lại nói cổng đó chỉ chạy tay.

A. Giữ như CI hiện tại: phủ tính trên toàn bộ, chạy trong CI
B. Chỉ tính phủ trên bộ nhanh, chạy trong CI
C. Chỉ chạy tay, không đặt trong CI
D. Not yet defined
X. Other (please specify)

[Answer]: A

## Consolidated Summary Confirmation

- Q1: thêm nhánh đang làm vào danh sách trigger của `ci.yml`
- Q2: không dựng lát cắt mỏng trước; làm từng phần trọn vẹn theo thứ tự đã chốt
- Q3: giữ nguyên cách viết test trước rồi mới viết mã (TDD)
- Q4: thêm lệnh thống kê thành bước thứ ba trong chuỗi xác nhận, trước khi mở dashboard
- Q5: hình dạng là một tầng mới trong chuỗi `run --stage`, không phải lệnh con riêng
- Q6: giữ như CI hiện tại — phủ tính trên toàn bộ bộ test, chạy trong CI

- Looks correct
- Request changes

[Answer]: Looks correct

