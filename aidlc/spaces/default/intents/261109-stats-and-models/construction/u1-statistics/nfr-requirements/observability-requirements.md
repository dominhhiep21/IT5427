# Observability Requirements — u1-statistics

Nguồn: `../functional-design/rules.md` (BR1.6, BR1.11), `../../../inception/requirements-analysis/requirements.md` (NFR3), và quy ước nhật ký JSONL sẵn có của repo (`logs/`, mỗi dòng một sự kiện).

Chốt ở Q3 = A: **chỉ dùng đúng các trường mà hàm ghi nhật ký hiện có phát ra**, không thêm trường riêng cho tầng `stats`.

Các mục dưới đây không mang mã `NFRx.y`: chúng không phải yêu cầu phi chức năng có nguồn trong Requirements Analysis, mà là cách hiện thực quyết định Q3 = A.

| Mã | Sự kiện | Nội dung | Trường dùng |
|---|---|---|---|
| OBS-1 | Bắt đầu tầng | Một dòng khi tầng `stats` khởi động | đúng bộ trường hàm ghi hiện có (`timestamp`, `level`, `run_id`, `stage`, `event`) |
| OBS-2 | Kết thúc tầng | Một dòng khi tầng xong, kèm thời lượng trong `event` | như trên |
| OBS-3 | Kiểm định bị bỏ | Một dòng cho mỗi phần tử của `skipped`; tên phép và lý do nằm trong `event` | như trên |
| OBS-4 | Ghi tệp hỏng | Một dòng mức lỗi trước khi ném ở biên CLI, dùng đúng hàm ghi lỗi sẵn có (hàm này có trường `error_code` riêng — không tự thêm trường mới) | đúng bộ trường hàm ghi lỗi phát ra |

## Vì sao không thêm trường

Thêm trường riêng nghĩa là mọi công cụ đọc nhật ký hiện có phải biết thêm một hình dạng. Ba thứ cần biết — thời lượng, tên phép bị bỏ, lý do — đều là văn bản ngắn, đặt trong `event` là đủ. Lý do bỏ qua còn có chỗ đứng chính thức trong chính tệp báo cáo (`StatsBlock.skipped`), nên nhật ký chỉ cần chỉ đường chứ không phải chở dữ liệu.

## Không đặt

- Không có metric, không có tracing, không có dashboard cho tầng này: nó là một tiến trình chạy theo lệnh, và thứ người đọc quan tâm là tệp báo cáo, không phải biểu đồ thời gian chạy.
- Không tạo tệp nhật ký mới; dùng đúng tệp JSONL của lần chạy, phân biệt bằng `run_id`.
- Không đặt mốc thời gian riêng cho từng phép kiểm định ở đây — mốc đó thuộc NFR1.2 và được đo trong test, không qua nhật ký.

## Điều phải kiểm khi viết mã

- Một test khẳng định mỗi lần chạy sinh đúng một sự kiện bắt đầu và một sự kiện kết thúc, cùng `run_id`.
- Một test khẳng định số sự kiện "kiểm định bị bỏ" bằng `len(skipped)`.
