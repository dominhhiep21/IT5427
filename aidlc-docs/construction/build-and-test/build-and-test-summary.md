# Build and Test Summary

## Build Status

- **Build Tool**: Python 3.13.5 + venv + `compileall`.
- **Build Status**: **Success**.
- **Build Artifacts**:
  - `data/raw/*.parquet`
  - `data/cleaned/*.parquet`
  - `data/marts/*.parquet`
  - `warehouse/olist.duckdb`
  - `data/reports/*.json`
- **Build Time**: pipeline đầy đủ ~12,2 giây.

## Test Execution Summary

### Unit Tests

- **Total Tests**: 45 (39 fast + 6 slow).
- **Passed**: 45.
- **Failed**: 0.
- **Coverage toàn dự án**: **87%**.
- **Coverage U1 cleaning/quality**: 100%.
- **Coverage U2 integrate/analytics**: ~89%.
- **Coverage U3 dashboard/pipeline**: 75%.
- **Status**: **Pass**.

### Integration Tests

- **Test Scenarios**: 6.
- **Passed**: 6.
- **Failed**: 0.
- **Bao gồm**:
  - U1 cleaned → U2 star schema.
  - U2 → DuckDB → analytics KPI.
  - U3 CLI `run --stage all`.
  - Micro-batch idempotency.
  - Replay theo tháng.
  - Dashboard layout/callback smoke.
- **Status**: **Pass**.

### Performance Tests

| Hạng mục | Mục tiêu | Thực tế | Kết quả |
|---|---|---|---|
| Pipeline đầy đủ | ≤ 10 phút | ~12,2 giây | Pass |
| Dashboard load | ≤ 3 giây | 1,81 giây | Pass |
| KPI query | ≤ 1 giây | 65-233 ms | Pass |
| Micro-batch 10k | ≤ 30 giây | 4,71 giây | Pass |

### Additional Tests

- **E2E Dashboard**: Pass (Playwright, 3 tab, 4 KPI, 0 console error).
- **Contract Tests**: N/A (không có API public).
- **Security Tests**: N/A/Pass (localhost-only, không auth, không upload dữ liệu).
- **ML Tests**: N/A (ML trì hoãn).

## Overall Status

- **Build**: **Success**.
- **All Tests**: **Pass**.
- **Ready for Operations**: **Yes** (Operations vẫn là placeholder).

## Ghi chú

- API IBGE không truy cập được từ máy này; dùng cache bootstrap 27 bang.
- Playwright dùng full Chromium do headless shell chưa tải xong.
- KPI baseline: 15.419.773,75 BRL; 96.478 đơn; AOV 159,83; 7.826 trễ; 8,11%.

## Next Steps

- Review summary và nghiệm thu.
- Operations phase là placeholder; nếu cần deploy thật, bổ sung hạ tầng/CI.
