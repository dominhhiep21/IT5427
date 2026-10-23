"""Dashboard layout smoke tests (no browser)."""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path

from dash import dcc

from src.config import load_config
from src.dashboard.app import build_dashboard_outputs, create_app


def test_dashboard_builds_with_three_tabs():
    app = create_app(load_config())
    tabs = [child for child in app.layout.children if isinstance(child, dcc.Tabs)]
    assert len(tabs) == 1
    assert len(tabs[0].children) == 3
    assert len(app.callback_map) == 2


def test_dashboard_outputs_with_real_data():
    outputs = build_dashboard_outputs(load_config(), {})
    assert len(outputs) == 9
    assert outputs[0] is not None
    assert outputs[1] is not None


def test_dashboard_outputs_error_state():
    config = replace(load_config(), duckdb_path=Path("missing.duckdb"))
    outputs = build_dashboard_outputs(config, {})
    assert "error-banner" in outputs[0].className
