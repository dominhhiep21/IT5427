# Security Test Instructions

## 1. Kiểm soát và test tương ứng

| Yêu cầu | Kiểm soát trong mã | Test |
|---|---|---|
| SR3.1 | không thêm phụ thuộc; chỉ `dash`, `dash_mantine_components`, `pandas` | `test_prediction_module_imports_no_new_dependency` |
| SR3.2, SR3.9 | `validate_form` chặn trước khi chạm mô hình; miền số hữu hạn | `test_each_bad_field_reports_one_error_at_its_own_input`, `test_boundary_values_are_accepted`, `test_a_fractional_item_count_is_rejected` |
| SR3.3 | `score_item` thuần, không I/O, không random | `test_callback_is_deterministic_for_the_same_input` |
| SR3.4, SR3.10 | câu hướng dẫn cố định; `str(ModelError)` chỉ vào nhật ký | `test_missing_model_disables_the_button_and_shows_both_verbatim_strings`, `test_result_area_shows_no_filesystem_path` |
| SR3.5 | không có kênh nạp tệp từ ngoài | `test_prediction_module_has_no_remote_or_upload_path` |
| SR3.6 | không literal giống bí mật | `test_no_secret_like_literals_in_prediction_module` |
| SR3.7 | không log giá trị biểu mẫu | `test_callback_logs_no_form_values` |
| SR3.8 | không `dangerously_allow_html` | `test_no_html_injection_in_prediction_result` |
| SR3.11 | `prediction_section` không import `AnalyticsService`/`warehouse` | `test_prediction_module_imports_no_analytics_service_and_no_warehouse` |
| SR3.12 | vẫn bind `127.0.0.1`, không route mới | `test_dashboard_still_binds_localhost` |

## 2. Lệnh

```
python -X utf8 -m pytest tests/unit/test_u3_prediction_section.py -q -k "imports or secret or injection or path or logs or localhost"
```

## 3. Rủi ro còn lại (đã chấp nhận, có ghi)

| Rủi ro | Mức | Vì sao chấp nhận |
|---|---|---|
| `pickle` thực thi mã nếu tệp bị thay bằng tệp độc | Thấp | tệp do pipeline sinh trong `data/models/`, đường dẫn từ `AppConfig`, không có kênh nạp ngoài, không endpoint nhận tệp |
| Nhật ký cục bộ chứa đường dẫn tuyệt đối | Thấp | `logs/` không commit; giao diện **không** hiện đường dẫn đó |
| Người dùng nhập giá trị hợp lệ nhưng phi thực tế (giá 0) | Thấp | công cụ tham khảo; miền đã chặn giá trị phi vật lý rõ ràng |

## 4. Điều không kiểm (và vì sao)

- Không có test xác thực/phân quyền: không có người dùng, không có API, dashboard chỉ localhost.
- Không có DAST/SAST trong CI: repo không có bước bảo mật tự động; `ruff` bắt lỗi tĩnh cơ bản.
- Không có kiểm tra TLS: không có lưu lượng mạng ra ngoài ngoài API IBGE khi `--refresh-ibge`.
