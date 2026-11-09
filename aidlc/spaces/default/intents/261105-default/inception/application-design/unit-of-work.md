# Đơn vị công việc (Units of Work)

## 1. Tổng quan

Dự án là **một ứng dụng cục bộ** chạy trên Windows, không phải microservices. Các unit dưới đây là nhóm công việc logic để triển khai tuần tự và kiểm chứng; chúng dùng chung một package `src/` và một workspace.

- **Tổng unit**: 3.
- **Tổng story**: 22.
- **Thứ tự**: U1 → U2 → U3.
- **Mô hình**: monolith module hóa, entrypoint CLI + dashboard.

## 2. U1 — Data Foundation

**Mục đích**: Biến 9 CSV thô thành dữ liệu sạch, có kiểm chứng, sẵn sàng tích hợp.

**Thành phần**: `config`, `common`, `ingest`, `quality`, `clean`.

**Trách nhiệm**
- Nạp cấu hình và tạo run context.
- Đọc 9 CSV, kiểm tra schema/encoding, tính hash, ghi raw Parquet.
- Kiểm tra khóa, orphan, số dòng, null bắt buộc.
- Làm sạch timestamp, city, geolocation, category, payment/review grain, cờ ngoại lai.

**Đầu vào**: `dataset/*.csv`.

**Đầu ra**
- `data/raw/*.parquet`
- `data/cleaned/*.parquet`
- `cleaning-report.json`, `quality-report.json`

**Story**: US-01, US-02, US-03, US-04, US-05, US-06, US-07.

**Thứ tự trong unit**: US-01 → US-02 → US-04 → US-05 → US-06 → US-07 → US-03 (quality gate chạy sau cleaning).

**Definition of Done**
- Code + unit test cho cleaning/quality.
- 9/9 tệp ingest; số dòng raw khớp CSV.
- Join geolocation không bùng nổ.
- Không sửa `dataset/`.
- Log có run_id và hash.

## 3. U2 — Integration & Analytics

**Mục đích**: Tạo star schema và các KPI phân tích ổn định.

**Thành phần**: `external`, `integrate`, `analytics`.

**Trách nhiệm**
- Tải/cache IBGE; ánh xạ 27 bang → 5 vùng.
- Xây dimension/fact từ cleaned data.
- Ghi mart Parquet, tạo DuckDB catalog/view.
- Tính doanh thu, AOV, tăng trưởng, danh mục, vùng, top product/seller, giao trễ.

**Đầu vào**: `data/cleaned/*.parquet`, IBGE cache.

**Đầu ra**
- `data/marts/*.parquet`
- `warehouse/olist.duckdb`
- Analytics API nội bộ (hàm Python).

**Story**: US-08, US-09, US-10, US-11, US-12, US-13, US-14, US-19.

**Thứ tự trong unit**: US-19 (IBGE) → US-08 → US-09 → US-10 → US-11 → US-12 → US-13 → US-14.

**Definition of Done**
- Star schema đúng grain, số dòng khớp.
- `dim_geography` đủ 19.015 zip và 5 vùng.
- KPI baseline khớp: 8,11% giao trễ; doanh thu `price + freight` 15.843.553,24 BRL.
- Analytics không ghi dữ liệu, không đọc CSV.
- Unit test cho KPI và join.

## 4. U3 — Dashboard & Operations

**Mục đích**: Cung cấp sản phẩm sử dụng được và quy trình vận hành/tái lập.

**Thành phần**: `dashboard`, `pipeline`, `tests`.

**Trách nhiệm**
- Plotly Dash: KPI, bộ lọc, biểu đồ, định dạng tiếng Việt, trạng thái lỗi/rỗng.
- CLI orchestration, micro-batch `inbox/`, replay.
- README, data dictionary, hướng dẫn chạy.
- Test tích hợp end-to-end và test hồi quy KPI.
- ML dự báo giao trễ (tùy chọn).

**Đầu vào**: marts + DuckDB từ U2.

**Đầu ra**
- Dashboard chạy cục bộ.
- `python -m src.pipeline run --stage all`.
- Manifest micro-batch.
- README + data dictionary.
- Test suite.

**Story**: US-15, US-16, US-17, US-18, US-20, US-21, US-22.

**Thứ tự trong unit**: US-20 (CLI skeleton) → US-15 → US-16 → US-17 → US-18 → US-21 → US-22.

**Definition of Done**
- Dashboard phản hồi ≤ 3 giây, nhãn tiếng Việt.
- Một lệnh chạy toàn bộ pipeline.
- `pytest` pass, có test tích hợp.
- Chạy lại từ đầu ≤ 15 phút sau khi cài dependency.
- ML (nếu làm) không ảnh hưởng KPI mặc định.

## 5. Chiến lược tổ chức mã (greenfield)

```
config.yaml
requirements.txt
README.md
src/
  config.py
  common/
  ingest/
  quality/
  clean/
  external/
  integrate/
  analytics/
  dashboard/
  pipeline/
tests/
  unit/
  data_quality/
  integration/
data/
  raw/
  cleaned/
  marts/
  external/ibge/
warehouse/
  olist.duckdb
inbox/
```

**Quy ước**
- Một package `src/`, import tuyệt đối `from src.clean import ...`.
- Entrypoint: `python -m src.pipeline`, `python -m src.dashboard`.
- Cấu hình: `config.yaml`, override bằng biến môi trường nếu cần.
- Test: `tests/unit` cho hàm, `tests/data_quality` cho kiểm tra dữ liệu, `tests/integration` cho end-to-end.
- Không commit `data/`, `warehouse/` sinh ra; có thể commit file mẫu nhỏ nếu cần.

## 6. Thứ tự và mốc tích hợp

1. **U1** hoàn tất → kiểm tra cleaned Parquet + quality report.
2. **U2** hoàn tất → kiểm tra marts + DuckDB + KPI baseline.
3. **U3** hoàn tất → kiểm tra dashboard + CLI + test end-to-end.

**Mốc tích hợp**
- Sau U1: join thử customers × geolocation phải trả 99.441 dòng.
- Sau U2: tỷ lệ giao trễ 8,11%; tổng doanh thu khớp.
- Sau U3: dashboard lọc được; pipeline chạy lại idempotent.

## 7. Quy ước dùng chung

- Mọi component nhận `AppConfig` và `RunContext`.
- Lỗi dùng `PipelineError` và lớp con.
- Ghi Parquet qua `common.write_parquet`.
- Không đọc CSV ngoài `ingest`.
- Không ghi vào `dataset/`.
- Log JSON hoặc text có timestamp, run_id, stage, rows_in/rows_out.
