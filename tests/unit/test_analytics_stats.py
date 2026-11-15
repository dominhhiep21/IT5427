"""Kiểm định chi-bình-phương tự cài phải khớp các giá trị chuẩn của bảng phân phối."""

from __future__ import annotations

import math

import pytest

from src.analytics.stats import chi2_sf, chi_square_independence, cramers_v_label


@pytest.mark.parametrize(
    ("critical_value", "dof"),
    [(3.841458820694124, 1), (5.991464547107979, 2), (9.487729036781154, 4), (18.307038053275146, 10)],
)
def test_chi2_sf_matches_five_percent_critical_values(critical_value, dof):
    # Giá trị tới hạn 5% trong mọi bảng chi-bình-phương: đuôi phải đúng bằng 0,05.
    assert chi2_sf(critical_value, dof) == pytest.approx(0.05, abs=1e-9)


@pytest.mark.parametrize("x", [0.1, 1.0, 5.0, 30.0])
def test_chi2_sf_matches_closed_forms_for_even_dof(x):
    assert chi2_sf(x, 2) == pytest.approx(math.exp(-x / 2), rel=1e-10)
    assert chi2_sf(x, 4) == pytest.approx(math.exp(-x / 2) * (1 + x / 2), rel=1e-10)


def test_chi2_sf_edges():
    assert chi2_sf(0, 3) == 1.0
    assert chi2_sf(100, 60) == pytest.approx(0.000916828861, rel=1e-6)
    assert chi2_sf(14_218.96, 4) == 0.0
    with pytest.raises(ValueError):
        chi2_sf(1.0, 0)
    with pytest.raises(ValueError):
        chi2_sf(-1.0, 2)


def test_chi_square_independence_textbook_two_by_two():
    result = chi_square_independence([[10, 20], [20, 10]])
    assert result.chi2 == pytest.approx(20 / 3)
    assert result.dof == 1
    assert result.p_value == pytest.approx(0.009823274507, rel=1e-8)
    assert result.cramers_v == pytest.approx(1 / 3)
    assert result.n == 60
    assert result.expected == ((15.0, 15.0), (15.0, 15.0))
    assert result.significant()


def test_chi_square_independence_of_proportional_rows_is_zero():
    result = chi_square_independence([[10, 20, 30], [20, 40, 60]])
    assert result.chi2 == pytest.approx(0.0, abs=1e-12)
    assert result.p_value == pytest.approx(1.0)
    assert result.cramers_v == pytest.approx(0.0, abs=1e-6)
    assert not result.significant()


def test_chi_square_ignores_empty_columns_but_keeps_table_shape():
    # Không đơn nào được 3 sao: cột rỗng không được làm hỏng phép tính hay bậc tự do.
    result = chi_square_independence([[0, 0, 0, 1, 0], [1, 1, 0, 0, 1]])
    assert result.dof == 3
    assert result.chi2 == pytest.approx(4.0)
    assert len(result.expected[0]) == 5
    assert result.expected[0][2] == 0.0


@pytest.mark.parametrize(
    "table",
    [
        [[1, 2]],
        [[1], [2]],
        [[1, 2], [3]],
        [[1, -2], [3, 4]],
        [[0, 0], [3, 4]],
        [[0, 5], [0, 4]],
    ],
)
def test_chi_square_rejects_degenerate_tables(table):
    with pytest.raises(ValueError):
        chi_square_independence(table)


@pytest.mark.parametrize(
    ("value", "label"),
    [(0.05, "rất yếu"), (0.2, "yếu"), (0.385, "trung bình"), (0.7, "mạnh")],
)
def test_cramers_v_label(value, label):
    assert cramers_v_label(value) == label
