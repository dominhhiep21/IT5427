# NFR Design Patterns — U1 Data Foundation

## 1. Atomic Write Pattern

**Mục tiêu**: Không để tệp Parquet/JSON dở dang; không làm hỏng output cũ khi lỗi.

**Cách làm**
1. Tạo tệp tạm cùng thư mục đích: `{name}.parquet.tmp-{run_id}`.
2. Ghi bằng PyArrow/pandas.
3. `flush` + `os.fsync` (nếu khả dụng).
4. Đọc lại metadata để xác nhận số dòng.
5. `os.replace(tmp, final)` — atomic trên cùng ổ đĩa.
6. Xóa tệp tạm sau khi replace.

```python
def write_parquet_atomic(df, final_path, run_id):
    tmp = final_path.with_suffix(f".parquet.tmp-{run_id}")
    df.to_parquet(tmp, engine="pyarrow", compression="snappy", index=False)
    check = pd.read_parquet(tmp)
    assert len(check) == len(df)
    os.replace(tmp, final_path)
```

**Khi lỗi**: giữ tệp tạm, log đường dẫn, không replace.

**NFR**: NFR-U1-03, NFR-U1-10.

## 2. Fail-Fast Pattern

- Kiểm tra schema ngay sau khi đọc.
- Kiểm tra khóa/orphan sau cleaning, trước khi ghi đè mart.
- Không retry cho lỗi dữ liệu; retry không làm dữ liệu sai thành đúng.
- Exception chuyên biệt:
  - `SchemaError` — thiếu cột/sai kiểu/encoding.
  - `QualityGateError` — khóa trùng, orphan, vượt allowlist.
  - `ConfigurationError` — thiếu config/thư mục.
- CLI trả mã 1; log có `error_code`.

**NFR**: NFR-U1-03.

## 3. Deterministic Processing Pattern

- Sắp xếp ổn định trước khi chọn mode:
  `sort_values(["zip", "count", "city"], ascending=[True, False, True])`.
- Tie-break alphabet rõ ràng.
- Không dùng random, không phụ thuộc thứ tự dictionary.
- Ghi Parquet với thứ tự cột cố định.
- Hash input SHA-256.

**NFR**: NFR-U1-05.

## 4. Structured Logging Pattern

**Định dạng**: JSON lines, mỗi dòng một object.

```json
{
  "timestamp": "2026-10-22T15:00:00Z",
  "level": "INFO",
  "run_id": "20261022T150000-ab12",
  "stage": "clean",
  "table": "geolocation",
  "rows_in": 1000163,
  "rows_out": 19015,
  "duration_ms": 4200,
  "status": "success",
  "message": "geolocation aggregated"
}
```

- Console: summary text ngắn (stage, rows, duration, status).
- Không log nội dung từng dòng.
- Lỗi: thêm `error_code`, `exception`, `traceback` (nếu debug).

**NFR**: NFR-U1-04.

## 5. Memory Control Pattern

- `tracemalloc.start()` đầu run; `reset_peak()` trước stage lớn.
- Sau stage: `current, peak = tracemalloc.get_traced_memory()`.
- Log `peak_mb` vào run summary.
- Nếu `peak_mb > 1536` → warning; > 2048 → fail cấu hình (có thể tắt bằng config).
- RSS thực được kiểm tra thủ công trong acceptance test (Task Manager), vì `tracemalloc` chỉ đo allocation Python.

**NFR**: NFR-U1-02.

## 6. Vectorized Geolocation Pattern

**Mục tiêu**: Tránh loop 1.000.163 dòng.

```text
1. drop_duplicates() toàn bộ 5 cột.
2. Tạo valid_coord bằng vectorized between().
3. valid = df[valid_coord]
4. coord = valid.groupby("zip")[["lat","lng"]].median()
5. city_counts = df.groupby(["zip","city_norm"]).size().reset_index(name="count")
6. city_mode = city_counts.sort_values(
       ["zip","count","city_norm"],
       ascending=[True, False, True]
   ).drop_duplicates("zip")
7. state_mode tương tự.
8. all_zips = df[["zip"]].drop_duplicates()
9. result = all_zips.merge(coord, how="left").merge(city_mode, how="left")...
```

**Không** dùng `apply`/loop theo zip.

**NFR**: NFR-U1-01, NFR-U1-02.

## 7. Temp Retention Pattern

- Tệp tạm nằm trong `data/.tmp/{run_id}/`.
- Khi thành công: xóa thư mục tạm.
- Khi lỗi: giữ nguyên, log `temp_dir` để debug.
- Không đưa tệp tạm vào dashboard/mart.

**NFR**: NFR-U1-03, NFR-U1-04.

## 8. Test Strategy Pattern

- **Unit test**: fixture tổng hợp nhỏ (5-20 dòng) cho cleaning/quality/geo.
- **Integration test**: dùng CSV thật, đánh dấu `@pytest.mark.slow`.
- **Lệnh nhanh**: `pytest -m "not slow"`.
- **Lệnh đầy đủ**: `pytest`.
- **Coverage**: `pytest --cov=src.clean --cov=src.quality`.
- **Không** để test phụ thuộc output cũ; tạo dữ liệu trong `tmp_path`.

**NFR**: NFR-U1-07.

## 9. Security Pattern

- U1 không import `requests`/`httpx`.
- Không đọc biến môi trường chứa secret.
- Không ghi dữ liệu chi tiết khách hàng vào log.
- Chỉ ghi trong workspace.

**NFR**: NFR-U1-06.

## 10. Parquet Pattern

- Engine: PyArrow.
- Compression: Snappy.
- `index=False`.
- Một tệp/bảng; không partition ở U1.
- Tên cột snake_case, giữ tên gốc cho cột nguồn.

**NFR**: NFR-U1-10.

## 11. Pattern → NFR mapping

| Pattern | NFR |
|---|---|
| Atomic write | U1-03, U1-10 |
| Fail-fast | U1-03 |
| Deterministic | U1-05 |
| Structured logging | U1-04 |
| Memory control | U1-02 |
| Vectorized geo | U1-01, U1-02 |
| Temp retention | U1-03, U1-04 |
| Test strategy | U1-07 |
| Local-only | U1-06 |
| Snappy Parquet | U1-10 |
