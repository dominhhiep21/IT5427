# Câu hỏi — Delivery Planning

DAG đã ép thứ tự `U1 → u2 → u3`, nên các câu hỏi dưới đây không hỏi "cái nào trước" mà hỏi **vì sao thứ tự đó đúng**, **mỗi lần giao hàng lớn cỡ nào**, và **cái gì có thể làm hỏng kế hoạch**.

## Q1. Lập luận nào biện minh cho thứ tự (đã bị DAG ép)?

- A. **Rủi ro trước**: U1 chạm mart dùng chung — nơi một lỗi grain làm đỏ 5 KPI và toàn bộ test tích hợp cũ — nên làm và kiểm sớm nhất
- B. **Giá trị trước**: ưu tiên thứ người dùng thấy (U3) — nhưng DAG không cho, nên phải ghi là "mong muốn không thực hiện được"
- C. **Lát cắt mỏng trước** — đã bị loại ở Q2 của đợt (không dựng skeleton)
- X. Khác (vui lòng nêu rõ)

[Answer]: A

## Q2. Có chấm điểm kiểu WSJF không?

- A. **Không** — ba đơn vị trên một đường duy nhất thì chấm điểm chỉ là hợp thức hoá thứ tự đã có; dùng lập luận bằng lời
- B. Chấm WSJF đầy đủ (giá trị + tính cấp bách + giảm rủi ro ÷ kích cỡ)
- C. Chấm nhẹ ba tiêu chí, ghi bảng nhưng không dùng để đổi thứ tự
- X. Khác (vui lòng nêu rõ)

[Answer]: A

## Q3. Một Bolt lớn cỡ nào?

- A. **Mỗi Bolt = một đơn vị** → 3 Bolt
- B. Gộp U1+U2 thành một Bolt (nền dữ liệu + mô hình), U3 một Bolt → 2 Bolt
- C. Tách U3 thành hai Bolt (bề mặt / nối số + mốc sàn) → 4 Bolt
- X. Khác (vui lòng nêu rõ)

[Answer]: A

## Q4. Có gì bên ngoài chặn không?

- A. **Không** — chỉ có API IBGE (đã có cache + fallback), không có team ngoài, không có phê duyệt bên ngoài
- B. Có (nêu ra)
- X. Khác (vui lòng nêu rõ)

[Answer]: A

## Q5. Điều gì làm bạn lo nhất, để đẩy lên kiểm sớm?

- A. **Hồi quy mart/KPI ở U1** (chạm tầng dùng chung)
- B. **Thời gian huấn luyện vượt ngân sách 300 s ở U2** (grain dòng hàng ≈112.650 dòng)
- C. **Vỡ hình dạng bề mặt dashboard ở U3** (10 callback/10 output canh ở ba tệp test)
- D. Khác (nêu ra)
- X. Khác (vui lòng nêu rõ)

[Answer]: A

## Consolidated Summary Confirmation

Năm câu đã trả lời, và kế hoạch giao hàng mà chúng tạo ra:

- **Thứ tự biện minh bằng rủi ro** [Q1 = A]: DAG đã ép `U1 → U2 → U3`; lý do đúng để đi đúng thứ tự đó là **U1 chạm mart dùng chung** — nơi một lỗi grain làm đỏ 5 KPI và toàn bộ test tích hợp cũ. Giá trị người dùng thấy nằm ở U3, nhưng đẩy U3 lên trước là bất khả thi về dữ liệu, không phải một lựa chọn bị bỏ.
- **Không chấm điểm** [Q2 = A]: ba đơn vị trên một đường duy nhất thì WSJF chỉ hợp thức hoá thứ tự đã có. Lập luận viết bằng lời, không có bảng điểm giả.
- **Ba Bolt, mỗi Bolt một đơn vị** [Q3 = A]: mỗi đơn vị đã có điều kiện xong riêng kiểm được trên dữ liệu thật; gộp U1+U2 sẽ cho một Bolt hai "định nghĩa xong" chồng nhau.
- **Không có chặn bên ngoài** [Q4 = A]: chỉ API IBGE, đã có cache + fallback; không team ngoài, không phê duyệt ngoài. `external-dependency-map.md` sẽ ngắn và nói đúng điều đó.
- **Rủi ro số một là hồi quy mart/KPI ở U1** [Q5 = A], và nó trùng đúng Bolt đầu — nên rủi ro lớn nhất được kiểm sớm nhất mà không phải đổi thứ tự.
- **Bối cảnh đã chốt từ trước, không hỏi lại**: không dựng lát cắt mỏng (Q2 của đợt); làm trọn từng phần; nhánh `feature/analysis-and-models`; một người làm, CI là cổng tự động duy nhất.

- Looks correct
- Request changes

[Answer]: Looks correct
