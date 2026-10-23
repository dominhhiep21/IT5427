"""Plotly Dash dashboard for the Olist pipeline."""

from __future__ import annotations

from datetime import date

import pandas as pd
import plotly.graph_objects as go
from dash import Dash, Input, Output, dcc, html

from src.analytics.service import AnalyticsService
from src.common.types import KpiFilters
from src.dashboard.components import (
    chart_card,
    empty_figure,
    error_banner,
    kpi_strip,
    sparse_badge,
)
from src.dashboard.formatting import format_brl, format_number, format_percent
from src.integrate.connections import ConnectionFactory

STATUS_OPTIONS = [
    {"label": "Đã giao", "value": "delivered"},
    {"label": "Đang giao", "value": "shipped"},
    {"label": "Đã hủy", "value": "canceled"},
    {"label": "Không có hàng", "value": "unavailable"},
    {"label": "Đã xuất hóa đơn", "value": "invoiced"},
    {"label": "Đang xử lý", "value": "processing"},
    {"label": "Đã tạo", "value": "created"},
    {"label": "Đã duyệt", "value": "approved"},
    {"label": "Tất cả", "value": "all"},
]


def _options(config) -> tuple[list[dict], list[dict], list[dict]]:
    try:
        conn = ConnectionFactory(config).read_only()
        try:
            states = [
                row[0]
                for row in conn.execute(
                    "SELECT DISTINCT state FROM v_dim_customer ORDER BY state"
                ).fetchall()
                if row[0]
            ]
            regions = [
                row[0]
                for row in conn.execute(
                    "SELECT DISTINCT region FROM v_dim_customer ORDER BY region"
                ).fetchall()
                if row[0]
            ]
            categories = [
                row[0]
                for row in conn.execute(
                    "SELECT DISTINCT category FROM v_dim_product ORDER BY category"
                ).fetchall()
                if row[0]
            ]
        finally:
            conn.close()
        return (
            [{"label": value, "value": value} for value in states],
            [{"label": value, "value": value} for value in regions],
            [{"label": value, "value": value} for value in categories],
        )
    except Exception:
        return [], [], []


def _base_layout() -> dict:
    return {
        "paper_bgcolor": "rgba(0,0,0,0)",
        "plot_bgcolor": "rgba(0,0,0,0)",
        "font": {"family": "Segoe UI, sans-serif", "color": "#0B1F1A", "size": 12},
        "margin": {"l": 44, "r": 18, "t": 18, "b": 42},
        "xaxis": {"gridcolor": "#DCE8E0", "zeroline": False},
        "yaxis": {"gridcolor": "#DCE8E0", "zeroline": False},
        "hoverlabel": {"bgcolor": "#0B1F1A", "font": {"color": "#F6F7F2"}},
    }


def _line_chart(
    frame: pd.DataFrame,
    x: str,
    y: str,
    name: str,
    currency: bool = True,
) -> go.Figure:
    figure = go.Figure()
    if frame.empty:
        return empty_figure()
    figure.add_trace(
        go.Scatter(
            x=frame[x],
            y=frame[y],
            mode="lines+markers",
            name=name,
            line={"color": "#B5532F", "width": 2},
            marker={"size": 5, "color": "#D9A441"},
        )
    )
    figure.update_layout(**_base_layout())
    if currency:
        figure.update_yaxes(tickprefix="R$ ", separatethousands=True)
    else:
        figure.update_yaxes(ticksuffix="%")
    return figure


def _bar_chart(
    frame: pd.DataFrame,
    x: str,
    y: str,
    name: str,
    horizontal: bool = False,
    currency: bool = True,
) -> go.Figure:
    figure = go.Figure()
    if frame.empty:
        return empty_figure()
    if horizontal:
        figure.add_trace(
            go.Bar(
                x=frame[x],
                y=frame[y],
                orientation="h",
                marker_color="#2F7D6A",
                name=name,
            )
        )
        figure.update_layout(**_base_layout())
        if currency:
            figure.update_xaxes(tickprefix="R$ ", separatethousands=True)
        else:
            figure.update_xaxes(ticksuffix="%")
    else:
        figure.add_trace(
            go.Bar(
                x=frame[x],
                y=frame[y],
                marker_color="#2F7D6A",
                name=name,
            )
        )
        figure.update_layout(**_base_layout())
        if currency:
            figure.update_yaxes(tickprefix="R$ ", separatethousands=True)
    return figure


def _table(frame: pd.DataFrame) -> html.Div:
    if frame.empty:
        return html.Div("Không có dữ liệu.", className="empty-state")
    rows = []
    for _, row in frame.iterrows():
        rows.append(
            html.Tr(
                [
                    html.Td(str(row["entity_id"])[:18]),
                    html.Td(str(row.get("category", ""))),
                    html.Td(format_brl(row["revenue"])),
                    html.Td(format_number(row["orders"])),
                ]
            )
        )
    return html.Table(
        [
            html.Thead(
                html.Tr(
                    [
                        html.Th("Sản phẩm / người bán"),
                        html.Th("Danh mục"),
                        html.Th("Doanh thu"),
                        html.Th("Đơn"),
                    ]
                )
            ),
            html.Tbody(rows),
        ],
        className="data-table",
    )


def build_layout(config) -> html.Div:
    states, regions, categories = _options(config)
    return html.Div(
        [
            html.Header(
                [
                    html.Div(
                        [
                            html.P("Olist / Bảng điều hành", className="eyebrow"),
                            html.H1("Dòng tiền và giao vận"),
                        ]
                    ),
                    html.P(
                        f"Cập nhật {date.today().strftime('%d/%m/%Y')}",
                        className="dateline",
                    ),
                ],
                className="masthead",
            ),
            html.Div(
                [
                    html.Div(
                        [
                            html.Label("Khoảng ngày"),
                            dcc.DatePickerRange(
                                id="date-range",
                                display_format="DD/MM/YYYY",
                                start_date_placeholder_text="Từ ngày",
                                end_date_placeholder_text="Đến ngày",
                                minimum_nights=0,
                                clearable=True,
                            ),
                        ],
                        className="filter-field",
                    ),
                    html.Div(
                        [
                            html.Label("Bang"),
                            dcc.Dropdown(
                                id="state-filter",
                                options=states,
                                placeholder="Tất cả bang",
                                clearable=True,
                            ),
                        ],
                        className="filter-field",
                    ),
                    html.Div(
                        [
                            html.Label("Vùng"),
                            dcc.Dropdown(
                                id="region-filter",
                                options=regions,
                                placeholder="Tất cả vùng",
                                clearable=True,
                            ),
                        ],
                        className="filter-field",
                    ),
                    html.Div(
                        [
                            html.Label("Danh mục"),
                            dcc.Dropdown(
                                id="category-filter",
                                options=categories,
                                placeholder="Tất cả danh mục",
                                clearable=True,
                            ),
                        ],
                        className="filter-field",
                    ),
                    html.Div(
                        [
                            html.Label("Trạng thái"),
                            dcc.Dropdown(
                                id="status-filter",
                                options=STATUS_OPTIONS,
                                value="delivered",
                                clearable=False,
                            ),
                        ],
                        className="filter-field",
                    ),
                ],
                className="filter-bar",
            ),
            dcc.Store(id="filters-store", data={}),
            html.Div(id="sparse-warning"),
            html.Div(id="kpi-cards"),
            dcc.Tabs(
                id="tabs",
                value="overview",
                className="tab-rail",
                children=[
                    dcc.Tab(
                        label="Tổng quan",
                        value="overview",
                        children=html.Div(
                            [
                                html.Div(
                                    chart_card(
                                        "Doanh thu theo tháng",
                                        "revenue-trend",
                                        "Đơn đã giao; đơn vị BRL",
                                    ),
                                    className="chart-span-2",
                                ),
                                chart_card(
                                    "Top danh mục",
                                    "category-bar",
                                    "Doanh thu theo danh mục",
                                ),
                            ],
                            className="chart-grid",
                        ),
                    ),
                    dcc.Tab(
                        label="Danh mục",
                        value="category",
                        children=html.Div(
                            [
                                chart_card(
                                    "Doanh thu theo danh mục",
                                    "category-detail-bar",
                                    "So sánh danh mục",
                                ),
                                html.Section(
                                    [
                                        html.Header(
                                            html.H3("Top sản phẩm"),
                                            className="chart-header",
                                        ),
                                        html.Div(id="top-products"),
                                    ],
                                    className="chart-card",
                                ),
                            ],
                            className="chart-grid",
                        ),
                    ),
                    dcc.Tab(
                        label="Giao vận",
                        value="delivery",
                        children=html.Div(
                            [
                                chart_card(
                                    "Tỷ lệ giao trễ theo bang",
                                    "delivery-state",
                                    "% đơn đã giao",
                                ),
                                chart_card(
                                    "Tỷ lệ giao trễ theo danh mục",
                                    "delivery-category",
                                    "Top danh mục",
                                ),
                                chart_card(
                                    "Tỷ lệ giao trễ theo tháng",
                                    "delivery-month",
                                    "% đơn đã giao",
                                ),
                            ],
                            className="chart-grid",
                        ),
                    ),
                ],
            ),
        ],
        className="app-shell",
    )


def create_app(config) -> Dash:
    app = Dash(
        __name__,
        assets_folder=str(config.workspace_root / "assets"),
        title="Olist | Bảng điều hành",
    )
    app.layout = build_layout(config)

    @app.callback(
        Output("filters-store", "data"),
        Input("date-range", "start_date"),
        Input("date-range", "end_date"),
        Input("state-filter", "value"),
        Input("region-filter", "value"),
        Input("category-filter", "value"),
        Input("status-filter", "value"),
    )
    def sync_filters(start_date, end_date, state, region, category, status):
        return {
            "start_date": start_date,
            "end_date": end_date,
            "state": state,
            "region": region,
            "category": category,
            "order_status": status or "delivered",
        }

    @app.callback(
        [
            Output("kpi-cards", "children"),
            Output("sparse-warning", "children"),
            Output("revenue-trend", "figure"),
            Output("category-bar", "figure"),
            Output("category-detail-bar", "figure"),
            Output("top-products", "children"),
            Output("delivery-state", "figure"),
            Output("delivery-category", "figure"),
            Output("delivery-month", "figure"),
        ],
        Input("filters-store", "data"),
    )
    def render_dashboard(data):
        return build_dashboard_outputs(config, data)

    return app


def build_dashboard_outputs(config, data):
    data = data or {}
    filters = KpiFilters(
        start_date=data.get("start_date"),
        end_date=data.get("end_date"),
        state=data.get("state"),
        region=data.get("region"),
        category=data.get("category"),
        order_status=data.get("order_status") or "delivered",
    )
    service = AnalyticsService(config)
    try:
        summary = service.kpi_summary(filters)
        monthly = service.revenue_by_period(filters, "month")
        category_frame = service.revenue_by_dimension(filters, "category")
        top = service.top_entities(filters, "product", 10)
        delivery_state = service.delivery_kpis(filters, "state")
        delivery_category = service.delivery_kpis(filters, "category")
        delivery_month = service.delivery_kpis(filters, "month")
        delivery_month = delivery_month[delivery_month["dimension"] >= "2017-01"]
    except Exception as exc:
        message = str(exc)[:220]
        empty = empty_figure()
        return (
            error_banner(message),
            None,
            empty,
            empty,
            empty,
            html.Div("Không đọc được dữ liệu.", className="empty-state"),
            empty,
            empty,
            empty,
        )

    sparse = None
    if not monthly.empty and bool(monthly["is_sparse_period"].any()):
        sparse = sparse_badge()

    monthly = monthly.copy()
    monthly["period"] = monthly.apply(
        lambda row: f"{int(row['year'])}-{int(row['month']):02d}", axis=1
    )
    category_frame = category_frame.head(12)
    delivery_state = delivery_state.sort_values("late_rate_pct", ascending=False).head(12)
    delivery_category = delivery_category.sort_values(
        "late_rate_pct", ascending=False
    ).head(12)
    delivery_month = delivery_month.sort_values("dimension")

    return (
        kpi_strip(summary),
        sparse,
        _line_chart(monthly, "period", "revenue", "Doanh thu"),
        _bar_chart(category_frame, "revenue", "dimension", "Danh mục", True),
        _bar_chart(category_frame, "revenue", "dimension", "Danh mục", True),
        _table(top),
        _bar_chart(
            delivery_state,
            "late_rate_pct",
            "dimension",
            "Giao trễ",
            True,
            currency=False,
        ),
        _bar_chart(
            delivery_category,
            "late_rate_pct",
            "dimension",
            "Giao trễ",
            True,
            currency=False,
        ),
        _line_chart(
            delivery_month,
            "dimension",
            "late_rate_pct",
            "Tỷ lệ trễ",
            currency=False,
        ),
    )
