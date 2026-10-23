"""Reusable dashboard components."""

from __future__ import annotations

from dash import dcc, html
import plotly.graph_objects as go

from src.dashboard.formatting import format_brl, format_number, format_percent


def kpi_card(
    label: str,
    value: str,
    detail: str = "",
    tone: str = "ink",
) -> html.Div:
    return html.Div(
        [
            html.P(label, className="kpi-label"),
            html.P(value, className=f"kpi-value kpi-{tone}"),
            html.P(detail, className="kpi-detail") if detail else None,
        ],
        className="kpi-card",
    )


def kpi_strip(summary: dict) -> html.Div:
    return html.Div(
        [
            kpi_card(
                "Doanh thu",
                format_brl(summary.get("revenue")),
                "Đơn đã giao",
                "ochre",
            ),
            kpi_card(
                "Số đơn",
                format_number(summary.get("orders")),
                "Đơn duy nhất",
            ),
            kpi_card(
                "Giá trị đơn TB",
                format_brl(summary.get("aov")),
                "AOV",
            ),
            kpi_card(
                "Giao trễ",
                format_percent(summary.get("late_rate_pct")),
                f"{format_number(summary.get('late_orders'))} đơn",
                "clay",
            ),
        ],
        className="kpi-strip",
    )


def chart_card(title: str, graph_id: str, subtitle: str = "") -> html.Section:
    return html.Section(
        [
            html.Header(
                [
                    html.H3(title),
                    html.P(subtitle, className="chart-subtitle") if subtitle else None,
                ],
                className="chart-header",
            ),
            dcc.Graph(id=graph_id, config={"displayModeBar": False}),
        ],
        className="chart-card",
    )


def empty_figure(message: str = "Không có dữ liệu với bộ lọc hiện tại.") -> go.Figure:
    figure = go.Figure()
    figure.add_annotation(
        text=message,
        x=0.5,
        y=0.5,
        xref="paper",
        yref="paper",
        showarrow=False,
        font={"size": 14, "color": "#5B6B63"},
    )
    figure.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis={"visible": False},
        yaxis={"visible": False},
        margin={"l": 20, "r": 20, "t": 20, "b": 20},
    )
    return figure


def error_banner(message: str) -> html.Div:
    return html.Div(
        [
            html.Strong("Không đọc được dữ liệu. "),
            html.Span(message),
            html.Button("Thử lại", id="retry-button", className="retry-button"),
        ],
        className="error-banner",
        role="alert",
    )


def sparse_badge() -> html.Div:
    return html.Div(
        "Dữ liệu 2016 chưa đầy đủ — chỉ có 329 đơn.",
        className="sparse-badge",
        role="status",
    )
