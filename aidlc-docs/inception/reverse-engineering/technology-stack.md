# Công nghệ sử dụng (Technology Stack)

## Ngôn ngữ lập trình

| Ngôn ngữ | Phiên bản | Sử dụng |
|---|---|---|
| Python | 3.13.5 | Ngôn ngữ khả dụng duy nhất cho pipeline |
| Markdown | — | Tài liệu AI-DLC và hướng dẫn |

## Framework / thư viện đã cài

| Thư viện | Phiên bản | Mục đích |
|---|---|---|
| pandas | 2.2.3 | Đọc, làm sạch, tích hợp CSV |
| numpy | Có cài | Tính toán số học |
| matplotlib | Có cài | Biểu đồ tĩnh |
| seaborn | Có cài | Biểu đồ thống kê |
| SQLAlchemy | Có cài | Truy cập SQLite/PostgreSQL nếu cần |
| openpyxl | Có cài | Xuất Excel |
| pdfplumber | Có cài | Trích xuất PDF |

## Thư viện **chưa** cài

`pyspark`, `duckdb`, `scikit-learn`, `pyarrow`, `jupyter`.

> Không viết import cho các thư viện này nếu chưa cài đặt và chưa được người dùng chấp thuận.

## Hạ tầng

| Thành phần | Trạng thái |
|---|---|
| Spark cluster | Không có |
| Database server | Không có |
| Object storage / data lake | Không có |
| Dashboard server | Không có |
| Docker | Chưa xác minh |
| Cloud account | Không có cấu hình trong repo |

## Công cụ build

Không có. Không có `requirements.txt`, `pyproject.toml`, venv hay lockfile.

## Công cụ kiểm thử

Không có. Không có pytest/unittest config, test data hay CI.

## Môi trường chạy

- Windows, đường dẫn workspace chứa ký tự tiếng Việt.
- Console mặc định cp1252 → phải dùng `python -X utf8` hoặc `PYTHONUTF8=1`.
- CSV UTF-8, không BOM, phân tách bằng dấu phẩy, toàn bộ trường được quote.
