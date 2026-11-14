"""Kiểm tương phản của tab phân tích theo token trong assets/style.css (NFR5.1)."""

from __future__ import annotations

import re
from pathlib import Path

STYLE_PATH = Path(__file__).resolve().parents[2] / "assets" / "style.css"

BACKGROUNDS = ("--surface", "--surface-sunken", "--paper")
FOREGROUNDS = ("--text", "--text-2")
MIN_RATIO = 4.5


def _tokens() -> dict[str, str]:
    text = STYLE_PATH.read_text(encoding="utf-8")
    return {
        name: value.lower() for name, value in re.findall(r"(--[a-z0-9-]+)\s*:\s*(#[0-9a-fA-F]{6})\s*;", text)
    }


def _channel(value: int) -> float:
    srgb = value / 255
    if srgb <= 0.03928:
        return srgb / 12.92
    return ((srgb + 0.055) / 1.055) ** 2.4


def _luminance(hex_colour: str) -> float:
    raw = hex_colour.lstrip("#")
    red, green, blue = (int(raw[i : i + 2], 16) for i in (0, 2, 4))
    return 0.2126 * _channel(red) + 0.7152 * _channel(green) + 0.0722 * _channel(blue)


def _contrast(first: str, second: str) -> float:
    light, dark = sorted((_luminance(first), _luminance(second)), reverse=True)
    return (light + 0.05) / (dark + 0.05)


def _analysis_tab_block() -> str:
    text = STYLE_PATH.read_text(encoding="utf-8")
    start = text.find(".analysis-tab")
    assert start != -1, "không tìm thấy khối .analysis-tab trong style.css"
    return text[start:]


def test_every_pair_the_tab_draws_reaches_wcag_aa() -> None:
    tokens = _tokens()

    for foreground in FOREGROUNDS:
        for background in BACKGROUNDS:
            ratio = _contrast(tokens[foreground], tokens[background])
            assert ratio >= MIN_RATIO, (
                f"{foreground} trên {background} chỉ đạt {ratio:.2f}:1, dưới {MIN_RATIO}:1"
            )


def test_text_3_is_below_the_floor_and_therefore_unused_by_the_tab() -> None:
    tokens = _tokens()
    ratio = _contrast(tokens["--text-3"], tokens["--surface"])
    assert ratio < MIN_RATIO, "--text-3 nay đã đạt mốc; hãy dùng lại nó thay vì --text-2 và cập nhật NFR5.1"


def test_analysis_tab_never_falls_back_to_text_3() -> None:
    block = _analysis_tab_block()
    assert "--text-3" not in block, "khối .analysis-tab dùng --text-3, vốn chỉ đạt 3,85:1 trên --surface"


def test_the_field_error_rule_exists_and_uses_text_2() -> None:
    """BR3.31 — lỗi tại ô của mục Dự đoán dùng đúng token --text-2, không thêm màu mới."""

    text = STYLE_PATH.read_text(encoding="utf-8")
    match = re.search(r"\.field-error[^{]*\{([^}]*)\}", text)

    assert match, "assets/style.css thiếu luật .field-error cho lỗi tại ô (BR3.19, BR3.31)"
    declarations = match.group(1)
    assert "var(--text-2)" in declarations
    assert not re.search(r"#[0-9a-fA-F]{3,6}", declarations)
