# External Dependency Map

Nguồn: `../requirements-analysis/requirements.md`, `../feasibility/constraint-register.md`, `../market-research/build-vs-buy.md`.

| Phụ thuộc | Loại | Dùng ở | Trạng thái | Rủi ro nếu thiếu |
|---|---|---|---|---|
| `scipy` hoặc `statsmodels` | Thư viện PyPI | Kiểm định thống kê (U1) | Chưa ghim; phải thêm vào `requirements.txt` kèm lý do | Không có kiểm định; phải tự viết công thức |
| `scikit-learn` | Thư viện PyPI | Mô hình (U2) | Chưa ghim; phải thêm vào `requirements.txt` kèm lý do | Không huấn luyện được mô hình |
| `numpy` | Đi kèm `pandas` | Cả hai đơn vị | Có gián tiếp | Không ảnh hưởng |
| DuckDB và Parquet | Đã có | Đọc mart | Có | Không chạy được |
| GitHub Actions | Dịch vụ ngoài | CI | Có, `windows-2022` | Không có cổng tự động |
| PyPI | Mạng | Cài hai thư viện mới | Có; máy cài trực tiếp được | Phải tìm phương án khác |

## Thời điểm cần

- Hai thư viện mới phải được ghim và cài **trước khi** bắt đầu Bolt 1, vì cả hai đơn vị trong đợt đều cần.
- Không có phụ thuộc ngoài nào khác cho Bolt 2.

## Không phải phụ thuộc ngoài

- Dữ liệu `dataset/` là đầu vào bất biến, không phải dịch vụ.
- Ba hợp đồng YAML trong `config/` là tệp trong repo.
