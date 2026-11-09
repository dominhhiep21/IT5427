"""Cổng đúng đắn của lát cắt (NFR5.5, NFR5.6): số trên thẻ phải khớp một phép tính độc lập.

Phép tính ở đây cố ý **không** dùng `src.integration`: nó đọc thẳng CSV nguồn bằng pandas
và áp lại BR1.1/BR1.2, để một lỗi trong bộ nạp hoặc trong truy vấn không thể tự che mình.
Tệp này mang marker `slow` vì đọc dữ liệu thật (`dataset/olist_orders_dataset.csv`).
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

import pandas as pd
import pytest

from src.integration.load import clear_cache, load_don_hang
from src.integration.query import run_monthly_orders, rewrite_plan
from src.integration.schema import load_schema

# BR1.7 chốt cửa sổ 12 tháng; khai lại ở đây để cổng không mượn hằng số của mã đang kiểm.
WINDOW_MONTHS = 12

# Tám giá trị trạng thái của bảng nguồn, khai lại ở đây cho phép tính độc lập (BR1.2).
SOURCE_STATUSES = frozenset(
    {
        "created",
        "approved",
        "invoiced",
        "processing",
        "shipped",
        "delivered",
        "unavailable",
        "canceled",
    }
)


def _independent_counts(csv_path: Path) -> dict[tuple[str, str], int]:
    """Đếm đơn theo (tháng, trạng thái) trực tiếp từ CSV, không qua tầng tích hợp."""

    frame = pd.read_csv(
        csv_path,
        encoding="utf-8-sig",
        usecols=["order_id", "order_purchase_timestamp", "order_status"],
        dtype=str,
    )
    parsed = pd.to_datetime(frame["order_purchase_timestamp"], errors="coerce")
    valid = parsed.notna()
    valid &= parsed <= pd.Timestamp(datetime.now())
    valid &= frame["order_status"].isin(SOURCE_STATUSES)
    # Cùng thứ tự với `load.clean_rows`: kiểm hợp lệ trước, rồi mới bỏ trùng theo bản ghi hợp lệ đầu tiên.
    valid_frame = frame.loc[valid].assign(ngay_dat=parsed[valid])
    valid_frame = valid_frame.drop_duplicates(subset="order_id", keep="first")
    months = valid_frame["ngay_dat"].dt.strftime("%Y-%m")
    statuses = valid_frame["order_status"]
    counted = (
        pd.DataFrame({"thang": months, "trang_thai": statuses})
        .groupby(["thang", "trang_thai"], sort=True)
        .size()
    )
    return {(str(month), str(status)): int(total) for (month, status), total in counted.items()}


def _window(counts: dict[tuple[str, str], int]) -> set[str]:
    """12 tháng gần nhất tính từ tháng mới nhất có trong dữ liệu (BR1.7)."""

    months = sorted({month for month, _ in counts})
    if not months:
        return set()
    newest = pd.Period(months[-1], freq="M")
    return {str(newest - offset) for offset in range(WINDOW_MONTHS - 1, -1, -1)}


@pytest.mark.slow
def test_card_numbers_match_independent_pandas_count(real_config):
    """NFR5.5: từng nhóm (tháng, trạng thái) và tổng toàn kỳ khớp, sai lệch 0."""

    csv_path = Path(real_config.raw_csv_dir) / "olist_orders_dataset.csv"
    expected = _independent_counts(csv_path)
    window = _window(expected)

    clear_cache()
    schema = load_schema(Path(real_config.mediated_schema_path))
    plan = rewrite_plan(schema.entity("don_hang"))
    loaded = load_don_hang(real_config)
    result = run_monthly_orders(loaded.orders, plan)

    actual = {(str(row["thang"]), str(row["trang_thai"])): int(row["so_don"]) for row in result.rows}

    assert set(result.months or ()) <= window, "Thẻ không được hiển thị tháng ngoài cửa sổ 12 tháng."
    assert max(result.months or ()) == max(window), "Tháng mới nhất của thẻ phải khớp phép tính độc lập."

    keys = {key for key in expected if key[0] in window} | {key for key in actual if key[0] in window}
    mismatches = [
        (key, expected.get(key, 0), actual.get(key, 0))
        for key in sorted(keys)
        if expected.get(key, 0) != actual.get(key, 0)
    ]
    assert not mismatches, (
        f"Số trên thẻ lệch phép tính độc lập (tháng, trạng thái, mong đợi, thực tế): {mismatches[:10]}"
    )

    assert result.total_orders == sum(expected.values()), (
        "Tổng toàn kỳ trên thẻ phải bằng tổng đếm độc lập: "
        f"thẻ {result.total_orders}, độc lập {sum(expected.values())}."
    )


@pytest.mark.slow
def test_query_states_status_and_window_explicitly(real_config):
    """NFR5.6: SQL nêu rõ trạng thái và cửa sổ tháng được tính tường minh, không ngầm định."""

    clear_cache()
    schema = load_schema(Path(real_config.mediated_schema_path))
    plan = rewrite_plan(schema.entity("don_hang"))
    loaded = load_don_hang(real_config)
    result = run_monthly_orders(loaded.orders, plan)

    sql = " ".join(result.source_sql.split()).lower()
    select_part, group_part = sql.split("group by", maxsplit=1)
    assert "order_status as trang_thai" in select_part, "Trạng thái phải có trong SELECT dưới tên trung gian."
    assert "trang_thai" in group_part.split("order by", maxsplit=1)[0], (
        "Trạng thái phải là khoá nhóm, không gộp mờ mọi trạng thái."
    )
    assert len(result.months or ()) <= WINDOW_MONTHS
