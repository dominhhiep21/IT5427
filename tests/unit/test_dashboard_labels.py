"""Nhãn tiếng Việt cho danh mục hàng và nhãn đích của mô hình."""

from __future__ import annotations

import pytest

from src.dashboard.labels import (
    CATEGORY_LABELS_VI,
    TARGET_LABELS_VI,
    category_label,
    target_label,
)


def test_every_category_label_is_vietnamese_and_non_empty() -> None:
    """Mọi nhãn đều có chữ và đều đã dịch, không để nguyên khoá Bồ Đào Nha."""

    for key, label in CATEGORY_LABELS_VI.items():
        assert label.strip()
        assert label != key
        assert "_" not in label


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("beleza_saude", "Sức khỏe & làm đẹp"),
        ("moveis_sala", "Nội thất phòng khách"),
        ("pc_gamer", "Máy tính chơi game"),
        ("unknown", "Không xác định"),
    ],
)
def test_known_categories_are_translated(raw: str, expected: str) -> None:
    assert category_label(raw) == expected


def test_unknown_category_falls_back_to_a_readable_form() -> None:
    """Giá trị lạ không bị bịa nghĩa: chỉ đổi gạch dưới thành khoảng trắng và viết hoa."""

    assert category_label("nova_categoria") == "Nova categoria"


def test_target_label_translates_the_late_flag() -> None:
    assert target_label("is_late") == "đơn giao trễ"
    assert TARGET_LABELS_VI["is_late"] == "đơn giao trễ"
    assert target_label("outro_alvo") == "outro_alvo"
