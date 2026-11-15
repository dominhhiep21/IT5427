"""Kiểm định thống kê thuần Python cho phần phân tích (không cần scipy).

Dùng cho mục 20 của bảng phân công: mô tả mối liên hệ giữa giao trễ và điểm đánh giá
bằng một kiểm định, thay vì chỉ so hai số trung bình bằng mắt.
"""

from __future__ import annotations

import math
from collections.abc import Sequence
from dataclasses import dataclass

_MAX_ITERATIONS = 500
_EPSILON = 1e-14
_TINY = 1e-300


@dataclass(frozen=True)
class ChiSquareResult:
    """Kết quả kiểm định chi-bình-phương về tính độc lập trên một bảng chéo."""

    chi2: float
    dof: int
    p_value: float
    cramers_v: float
    n: int
    expected: tuple[tuple[float, ...], ...]

    def significant(self, alpha: float = 0.05) -> bool:
        return self.p_value < alpha


def _gamma_p_series(a: float, x: float) -> float:
    """Hàm gamma không đầy đủ chuẩn hóa P(a, x) bằng khai triển chuỗi (tốt khi x < a + 1)."""

    term = 1.0 / a
    total = term
    denominator = a
    for _ in range(_MAX_ITERATIONS):
        denominator += 1.0
        term *= x / denominator
        total += term
        if abs(term) < abs(total) * _EPSILON:
            break
    return total * math.exp(-x + a * math.log(x) - math.lgamma(a))


def _gamma_q_fraction(a: float, x: float) -> float:
    """Q(a, x) = 1 - P(a, x) bằng liên phân số Lentz (tốt khi x >= a + 1)."""

    b = x + 1.0 - a
    c = 1.0 / _TINY
    d = 1.0 / b
    h = d
    for i in range(1, _MAX_ITERATIONS + 1):
        an = -i * (i - a)
        b += 2.0
        d = an * d + b
        if abs(d) < _TINY:
            d = _TINY
        c = b + an / c
        if abs(c) < _TINY:
            c = _TINY
        d = 1.0 / d
        delta = d * c
        h *= delta
        if abs(delta - 1.0) < _EPSILON:
            break
    return math.exp(-x + a * math.log(x) - math.lgamma(a)) * h


def chi2_sf(x: float, dof: int) -> float:
    """Xác suất đuôi phải của phân phối chi-bình-phương: P(X >= x) với `dof` bậc tự do."""

    if dof <= 0:
        raise ValueError("dof phải là số nguyên dương")
    if x < 0:
        raise ValueError("x phải không âm")
    if x == 0:
        return 1.0
    a = dof / 2.0
    half_x = x / 2.0
    if half_x < a + 1.0:
        return max(0.0, 1.0 - _gamma_p_series(a, half_x))
    return min(1.0, _gamma_q_fraction(a, half_x))


def chi_square_independence(table: Sequence[Sequence[float]]) -> ChiSquareResult:
    """Kiểm định H0 "hai biến phân loại độc lập" trên bảng chéo r dòng x c cột.

    Trả thêm Cramér's V (0 = không liên hệ, 1 = liên hệ hoàn toàn) vì với mẫu rất lớn
    p-value gần như luôn nhỏ; độ mạnh của mối liên hệ mới là điều cần đọc.

    Dòng hoặc cột có tổng bằng 0 (ví dụ không đơn nào được 3 sao) không mang thông tin nên
    bị loại khỏi phép tính và khỏi bậc tự do; `expected` vẫn giữ nguyên hình dạng bảng gốc.
    """

    rows = [list(map(float, row)) for row in table]
    if len(rows) < 2 or len(rows[0]) < 2 or any(len(row) != len(rows[0]) for row in rows):
        raise ValueError("Bảng chéo phải có ít nhất 2 dòng, 2 cột và các dòng cùng độ dài")
    if any(value < 0 for row in rows for value in row):
        raise ValueError("Bảng chéo không được chứa tần số âm")

    row_totals = [sum(row) for row in rows]
    col_totals = [sum(column) for column in zip(*rows)]
    n = sum(row_totals)
    used_rows = sum(1 for total in row_totals if total > 0)
    used_cols = sum(1 for total in col_totals if total > 0)
    if used_rows < 2 or used_cols < 2:
        raise ValueError("Cần ít nhất 2 dòng và 2 cột có tổng dương để kiểm định tính độc lập")

    expected = tuple(tuple(row_total * col_total / n for col_total in col_totals) for row_total in row_totals)
    chi2 = sum(
        (observed - exp) ** 2 / exp
        for observed_row, expected_row in zip(rows, expected)
        for observed, exp in zip(observed_row, expected_row)
        if exp > 0
    )
    return ChiSquareResult(
        chi2=chi2,
        dof=(used_rows - 1) * (used_cols - 1),
        p_value=chi2_sf(chi2, (used_rows - 1) * (used_cols - 1)),
        cramers_v=math.sqrt(chi2 / (n * (min(used_rows, used_cols) - 1))),
        n=int(round(n)),
        expected=expected,
    )


def cramers_v_label(value: float) -> str:
    """Diễn giải quy ước của Cramér's V (ngưỡng Cohen cho bảng có cạnh nhỏ bằng 2)."""

    if value < 0.1:
        return "rất yếu"
    if value < 0.3:
        return "yếu"
    if value < 0.5:
        return "trung bình"
    return "mạnh"
