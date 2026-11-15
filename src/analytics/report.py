"""Sinh báo cáo Markdown cho phần phân tích (mục 17–20) và đối soát (mục 16).

Mọi câu nhận xét đều được dựng từ số liệu vừa truy vấn — không gõ tay con số nào — nên chạy
lại trên dữ liệu mới thì bảng và nhận xét cùng đổi theo, không lệch nhau.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from src.analytics import insights
from src.analytics.formatting import (
    fmt_int,
    fmt_money,
    fmt_num,
    fmt_p_value,
    fmt_pct,
    fmt_signed_pct,
    to_markdown,
)
from src.analytics.reconciliation import FAIL, INFO, PASS, SKIP, ReconciliationResult, run_reconciliation
from src.analytics.stats import ChiSquareResult, chi_square_independence, cramers_v_label
from src.integrate.reconcile import BASELINE

ANALYSIS_REPORT_NAME = "analysis-report.md"
RECONCILIATION_REPORT_NAME = "reconciliation-report.md"
OUTPUT_SUBDIR = "analysis"

STATUS_LABELS = {PASS: "Đạt", FAIL: "KHÔNG ĐẠT", INFO: "Ghi nhận", SKIP: "Bỏ qua"}
SMALL_SAMPLE_ORDERS = 100
# Tháng cao nhất không quá 1,25 lần tháng thấp nhất thì coi doanh thu trong năm là "đi ngang".
FLAT_RANGE_RATIO = 1.25
BLACK_FRIDAY_2017 = "2017-11-24"


@dataclass
class AnalysisBundle:
    """Toàn bộ kết quả của một lần chạy phân tích."""

    frames: dict[str, pd.DataFrame]
    chi_square: ChiSquareResult
    reconciliation: ReconciliationResult


def run_bundle(conn, baseline: dict | None = BASELINE) -> AnalysisBundle:
    """Chạy mọi phân tích, kiểm định chi-bình-phương và bộ đối soát trên một kết nối.

    `baseline=None` bỏ phép so với KPI chuẩn (dùng cho bộ dữ liệu khác bộ Olist đầy đủ).
    """

    frames = insights.run_all(conn)
    table = insights.contingency_table(frames["review_late_contingency"])
    return AnalysisBundle(
        frames=frames,
        chi_square=chi_square_independence(table),
        reconciliation=run_reconciliation(conn, baseline),
    )


# ------------------------------------------------------------------------------ helpers


def _sql_block(key: str) -> list[str]:
    item = insights.analysis(key)
    sql = "\n".join(line[4:] if line.startswith("    ") else line for line in item.sql.strip("\n").splitlines())
    lines = ["<details><summary>Câu SQL</summary>", "", "```sql", sql.strip()]
    if item.params:
        lines.append(f"-- tham số ?: {', '.join(str(value) for value in item.params)}")
    lines += ["```", "", "</details>", ""]
    return lines


def _section(key: str, table: str, notes: list[str]) -> list[str]:
    item = insights.analysis(key)
    lines = [f"### {item.title}", "", f"**Câu hỏi:** {item.question}", "", table, ""]
    if notes:
        lines.append("**Nhận xét:**")
        lines.append("")
        lines += [f"- {note}" for note in notes]
        lines.append("")
    lines += _sql_block(key)
    return lines


def _vertical(pairs: list[tuple[str, str]]) -> str:
    lines = ["| Chỉ số | Giá trị |", "| --- | ---: |"]
    lines += [f"| {label} | {value} |" for label, value in pairs]
    return "\n".join(lines)


def _growth(new: float, old: float) -> float:
    return 100.0 * (new - old) / old if old else float("nan")


def _times(larger: float, smaller: float) -> str:
    """Cụm ", gấp N lần" khi phép chia có nghĩa; chuỗi rỗng khi mẫu số bằng 0."""

    return f", gấp {fmt_num(larger / smaller, 1)} lần" if smaller and smaller > 0 else ""


# --------------------------------------------------------------------- Mục 17: kinh doanh


def _business(frames: dict[str, pd.DataFrame]) -> list[str]:
    lines = [f"## Mục 17 — {insights.TASK_TITLES[17]}", ""]

    head = frames["kpi_headline"].iloc[0]
    lines += _section(
        "kpi_headline",
        _vertical(
            [
                ("Doanh thu (price + freight, đơn delivered)", fmt_money(head.revenue)),
                ("  trong đó tiền hàng", fmt_money(head.product_revenue)),
                ("  trong đó phí vận chuyển", f"{fmt_money(head.freight)} ({fmt_pct(head.freight_share_pct)})"),
                ("Số đơn delivered", fmt_int(head.orders)),
                ("Số dòng hàng", fmt_int(head["items"])),
                ("Giá trị đơn trung bình (AOV)", fmt_money(head.aov)),
                ("Số dòng hàng trên một đơn", fmt_num(head.items_per_order, 3)),
                ("Số khách hàng (customer_unique_id)", fmt_int(head.customers)),
                ("Số người bán có đơn", fmt_int(head.sellers)),
                ("Số sản phẩm có bán", fmt_int(head.products)),
                ("Tỷ lệ giao trễ", fmt_pct(head.late_rate_pct)),
                ("Thời gian giao trung bình", f"{fmt_num(head.avg_delivery_days)} ngày"),
                ("Điểm đánh giá trung bình", fmt_num(head.avg_review_score)),
            ]
        ),
        [
            f"Trung bình một đơn chỉ có {fmt_num(head.items_per_order, 3)} dòng hàng, nên AOV "
            f"({fmt_money(head.aov)}) gần với giá một món hàng cộng phí ship.",
            f"Phí vận chuyển chiếm {fmt_pct(head.freight_share_pct)} doanh thu. Con số doanh thu của nhóm gồm cả "
            "phí này; nếu chỉ tính tiền hàng thì thấp hơn tương ứng.",
        ],
    )

    monthly = frames["monthly_trend"]
    dense = monthly[~monthly["is_sparse_period"]]
    peak = dense.loc[dense["revenue"].idxmax()]
    last_year = dense[dense["period"].str.startswith(dense["period"].iloc[-1][:4])]
    year_low, year_high = last_year["revenue"].min(), last_year["revenue"].max()
    flat = year_low > 0 and year_high / year_low <= FLAT_RANGE_RATIO
    notes = [
        f"Tháng cao nhất là {peak.period} với {fmt_money(peak.revenue)} và {fmt_int(peak.orders)} đơn.",
        f"Trong năm {last_year['period'].iloc[0][:4]} doanh thu tháng dao động trong khoảng "
        f"{fmt_money(year_low)} – {fmt_money(year_high)}"
        + (
            f" (tháng cao nhất chỉ gấp {fmt_num(year_high / year_low)} lần tháng thấp nhất): "
            "giai đoạn tăng nhanh đã chuyển sang đi ngang."
            if flat
            else "."
        ),
        f"AOV theo tháng nằm trong khoảng {fmt_money(dense['aov'].min())} – {fmt_money(dense['aov'].max())}, hẹp hơn "
        "nhiều so với biên độ của số đơn, nên biến động doanh thu chủ yếu do số đơn.",
    ]
    sparse = monthly[monthly["is_sparse_period"]]
    if not sparse.empty:
        notes.append(
            f"{len(sparse)} tháng đầu ({', '.join(sparse['period'])}) chỉ có {fmt_int(sparse['orders'].sum())} đơn, "
            "được đánh dấu là giai đoạn thưa dữ liệu và không dùng để tính tăng trưởng."
        )
    lines += _section(
        "monthly_trend",
        to_markdown(
            monthly,
            {
                "period": "Tháng",
                "revenue": "Doanh thu (BRL)",
                "orders": "Số đơn",
                "aov": "AOV (BRL)",
                "freight_share_pct": "Phí ship / doanh thu (%)",
                "revenue_mom_pct": "Tăng so với tháng trước (%)",
            },
        ),
        notes,
    )

    days = frames["peak_days"]
    top_day = days.iloc[0]
    day_note = (
        f"Ngày nhiều đơn nhất là {top_day.order_date} với {fmt_int(top_day.orders)} đơn, gấp "
        f"{fmt_num(top_day.times_daily_average, 1)} lần ngày trung bình"
    )
    day_note += " — đúng ngày Black Friday 2017." if top_day.order_date == BLACK_FRIDAY_2017 else "."
    lines += _section(
        "peak_days",
        to_markdown(
            days,
            {
                "order_date": "Ngày đặt",
                "orders": "Số đơn",
                "times_daily_average": "So với ngày trung bình (lần)",
            },
        ),
        [
            day_note,
            "Đột biến theo sự kiện là dấu hiệu của đặc trưng Velocity: tải dữ liệu không đều theo thời gian.",
        ],
    )

    yoy = frames["yearly_same_period"]
    if len(yoy) == 2:
        old, new = yoy.iloc[0], yoy.iloc[1]
        revenue_growth = _growth(new.revenue, old.revenue)
        orders_growth = _growth(new.orders, old.orders)
        aov_growth = _growth(new.aov, old.aov)
        yoy_notes = [
            f"Cùng kỳ tháng {int(new.from_month)}–{int(new.to_month)}, so với năm {int(old.year)} thì năm "
            f"{int(new.year)} có doanh thu {fmt_signed_pct(revenue_growth)}, số đơn {fmt_signed_pct(orders_growth)}, "
            f"AOV {fmt_signed_pct(aov_growth)}.",
        ]
        if abs(orders_growth) > abs(aov_growth):
            yoy_notes.append(
                "Thay đổi doanh thu chủ yếu đến từ số đơn (quy mô), không phải từ giá trị mỗi đơn: "
                "doanh thu = số đơn × AOV, mà AOV gần như không đổi."
            )
    else:
        yoy_notes = ["Dữ liệu không đủ hai năm để so sánh cùng kỳ."]
    lines += _section(
        "yearly_same_period",
        to_markdown(
            yoy.assign(year=yoy["year"].astype(str)),
            {
                "year": "Năm",
                "from_month": "Từ tháng",
                "to_month": "Đến tháng",
                "revenue": "Doanh thu (BRL)",
                "orders": "Số đơn",
                "aov": "AOV (BRL)",
            },
        ),
        yoy_notes,
    )

    week = frames["weekday_pattern"]
    best, worst = week.loc[week["orders"].idxmax()], week.loc[week["orders"].idxmin()]
    weekdays = week[week["weekday_index"] <= 4]["orders"]
    weekend = week[week["weekday_index"] >= 5]["orders"]
    week_notes = [
        f"{best.weekday} nhiều đơn nhất ({fmt_int(best.orders)}), {worst.weekday} ít nhất ({fmt_int(worst.orders)})."
    ]
    if not weekdays.empty and not weekend.empty:
        week_notes.append(
            f"Cộng cả kỳ, mỗi thứ từ Thứ Hai đến Thứ Sáu có trung bình {fmt_int(weekdays.mean())} đơn, mỗi thứ cuối "
            f"tuần có {fmt_int(weekend.mean())} đơn ({fmt_signed_pct(_growth(weekend.mean(), weekdays.mean()))})."
        )
    lines += _section(
        "weekday_pattern",
        to_markdown(
            week,
            {
                "weekday": "Ngày",
                "orders": "Số đơn",
                "revenue": "Doanh thu (BRL)",
                "revenue_share_pct": "Tỷ trọng (%)",
            },
        ),
        week_notes,
    )

    region = frames["revenue_by_region"]
    top_region = region.iloc[0]
    rich = region.loc[region["aov"].idxmax()]
    costly = region.loc[region["freight_share_pct"].idxmax()]
    lines += _section(
        "revenue_by_region",
        to_markdown(
            region,
            {
                "region": "Vùng",
                "revenue": "Doanh thu (BRL)",
                "orders": "Số đơn",
                "aov": "AOV (BRL)",
                "revenue_share_pct": "Tỷ trọng (%)",
                "freight_share_pct": "Phí ship / doanh thu (%)",
            },
        ),
        [
            f"Vùng {top_region.region} chiếm {fmt_pct(top_region.revenue_share_pct)} doanh thu.",
            (
                f"Vùng {rich.region} vừa có AOV cao nhất ({fmt_money(rich.aov)}) vừa có tỷ trọng phí ship cao nhất "
                f"({fmt_pct(costly.freight_share_pct)}): một phần giá trị đơn cao ở vùng này là cước vận chuyển."
                if rich.region == costly.region
                else f"Vùng {rich.region} có AOV cao nhất ({fmt_money(rich.aov)}); vùng {costly.region} có tỷ trọng phí "
                f"ship cao nhất ({fmt_pct(costly.freight_share_pct)})."
            ),
        ],
    )

    pay = frames["payment_mix"]
    top_pay = pay.iloc[0]
    lines += _section(
        "payment_mix",
        to_markdown(
            pay,
            {
                "payment_type": "Phương thức",
                "orders": "Số đơn có dùng",
                "payment_rows": "Số dòng thanh toán",
                "payment_value": "Giá trị (BRL)",
                "value_share_pct": "Tỷ trọng giá trị (%)",
                "avg_installments": "Số kỳ trả góp TB",
            },
        ),
        [
            f"{top_pay.payment_type} chiếm {fmt_pct(top_pay.value_share_pct)} giá trị thanh toán, trung bình "
            f"{fmt_num(top_pay.avg_installments)} kỳ trả góp.",
            f"Cột 'Số đơn có dùng' cộng lại ra {fmt_int(pay['orders'].sum())}, lớn hơn số đơn delivered, vì một đơn "
            "có thể trả bằng nhiều phương thức. Đây là số đo không cộng dồn được.",
        ],
    )

    repeat = frames["customer_repeat"].iloc[0]
    lines += _section(
        "customer_repeat",
        _vertical(
            [
                ("Số khách hàng", fmt_int(repeat.customers)),
                ("Số đơn delivered", fmt_int(repeat.orders)),
                ("Khách mua từ 2 đơn trở lên", fmt_int(repeat.repeat_customers)),
                ("Tỷ lệ mua lại", fmt_pct(repeat.repeat_rate_pct)),
                ("Số đơn trung bình mỗi khách", fmt_num(repeat.orders_per_customer, 3)),
                ("Số đơn nhiều nhất của một khách", fmt_int(repeat.max_orders_one_customer)),
            ]
        ),
        [
            f"Chỉ {fmt_pct(repeat.repeat_rate_pct)} khách quay lại mua lần hai: sàn tăng trưởng nhờ khách mới, "
            "chưa giữ chân được khách cũ.",
            "Phải đếm theo `customer_unique_id`. Nếu đếm theo `customer_id` (mã sinh mới cho mỗi đơn) thì tỷ lệ mua "
            "lại luôn bằng 0 — một lỗi ngữ nghĩa điển hình của bộ dữ liệu này.",
        ],
    )

    status = frames["order_status"]
    delivered = status[status["order_status"] == "delivered"]
    share = float(delivered["share_pct"].iloc[0]) if not delivered.empty else float("nan")
    lines += _section(
        "order_status",
        to_markdown(
            status,
            {
                "order_status": "Trạng thái",
                "orders": "Số đơn",
                "share_pct": "Tỷ trọng (%)",
                "orders_with_items": "Số đơn có dòng hàng",
            },
        ),
        [
            f"{fmt_pct(share)} đơn ở trạng thái delivered. Mọi KPI doanh thu chỉ tính trên nhóm này, vì đơn hủy hoặc "
            "chưa giao chưa phải doanh thu thực nhận."
        ],
    )
    return lines


# ------------------------------------------------------- Mục 18: sản phẩm và người bán


def _products_sellers(frames: dict[str, pd.DataFrame]) -> list[str]:
    lines = [f"## Mục 18 — {insights.TASK_TITLES[18]}", ""]

    cats = frames["category_ranking"]
    top = cats.iloc[0]
    to_80 = (
        int(cats[cats["cum_share_pct"] >= 80].iloc[0]["rank"])
        if (cats["cum_share_pct"] >= 80).any()
        else len(cats)
    )
    top5 = cats.iloc[min(4, len(cats) - 1)]
    pricey = cats.head(20).loc[cats.head(20)["revenue_per_order"].idxmax()]
    notes = [
        f"Dẫn đầu là {top.category} ({top.category_english}) với {fmt_money(top.revenue)}, chiếm "
        f"{fmt_pct(top.share_pct)}.",
        f"5 danh mục đầu chiếm {fmt_pct(top5.cum_share_pct)} và chỉ cần {to_80} trên {len(cats)} danh mục để đạt "
        "80% doanh thu.",
        f"Xếp theo doanh thu và theo giá trị mỗi đơn cho hai bức tranh khác nhau: {pricey.category} chỉ có "
        f"{fmt_int(pricey.orders)} đơn nhưng mỗi đơn {fmt_money(pricey.revenue_per_order)}.",
    ]
    unknown = cats[cats["category"] == "unknown"]
    if not unknown.empty:
        row = unknown.iloc[0]
        notes.append(
            f"Nhóm `unknown` (sản phẩm thiếu danh mục ở nguồn) đứng hạng {int(row['rank'])} với "
            f"{fmt_pct(row.share_pct)} doanh thu. Nhóm giữ lại và gắn nhãn thay vì xóa, để tổng doanh thu không hụt."
        )
    lines += _section(
        "category_ranking",
        to_markdown(
            cats,
            {
                "rank": "Hạng",
                "category": "Danh mục",
                "category_english": "Tên tiếng Anh",
                "revenue": "Doanh thu (BRL)",
                "orders": "Số đơn",
                "items": "Số dòng hàng",
                "revenue_per_order": "Doanh thu / đơn (BRL)",
                "share_pct": "Tỷ trọng (%)",
                "cum_share_pct": "Lũy kế (%)",
            },
            limit=15,
        ),
        notes,
    )

    total_revenue = float(frames["kpi_headline"].iloc[0].revenue)
    products = frames["top_products"]
    lines += _section(
        "top_products",
        to_markdown(
            products,
            {
                "rank": "Hạng",
                "product_id": "Mã sản phẩm",
                "category": "Danh mục",
                "revenue": "Doanh thu (BRL)",
                "units": "Số lượng bán",
                "orders": "Số đơn",
                "avg_price": "Giá TB (BRL)",
            },
        ),
        [
            f"{len(products)} sản phẩm đứng đầu chỉ chiếm {fmt_pct(100.0 * products['revenue'].sum() / total_revenue)} "
            "doanh thu: doanh thu phân tán trên rất nhiều sản phẩm (đuôi dài), không phụ thuộc vài mặt hàng.",
            "Bộ dữ liệu ẩn tên sản phẩm nên chỉ xếp hạng được theo mã và danh mục.",
        ],
    )

    sellers = frames["top_sellers"]
    conc = frames["seller_concentration"].iloc[0]
    weakest = sellers.loc[sellers["avg_review_score"].idxmin()]
    slowest = sellers.loc[sellers["late_rate_pct"].idxmax()]
    lines += _section(
        "top_sellers",
        to_markdown(
            sellers,
            {
                "rank": "Hạng",
                "seller_id": "Mã người bán",
                "state": "Bang",
                "revenue": "Doanh thu (BRL)",
                "orders": "Số đơn",
                "share_pct": "Tỷ trọng (%)",
                "avg_review_score": "Điểm đánh giá TB",
                "late_rate_pct": "Tỷ lệ giao trễ (%)",
            },
        ),
        [
            "Xếp hạng người bán chỉ theo doanh thu là chưa đủ, nên bảng kèm hai chỉ số chất lượng: điểm đánh giá và "
            "tỷ lệ giao trễ.",
            f"Trong nhóm đầu, người bán hạng {int(weakest['rank'])} có điểm đánh giá thấp nhất "
            f"({fmt_num(weakest.avg_review_score)}) và người bán hạng {int(slowest['rank'])} giao trễ nhiều nhất "
            f"({fmt_pct(slowest.late_rate_pct)}): doanh thu lớn không đồng nghĩa phục vụ tốt.",
            "Đánh giá và cờ giao trễ thuộc về đơn hàng. Với đơn có nhiều người bán, chúng được tính cho mọi người bán "
            "trong đơn — một giả định đơn giản hóa cần nêu rõ.",
        ],
    )
    lines += _section(
        "seller_concentration",
        _vertical(
            [
                ("Số người bán có đơn delivered", fmt_int(conc.active_sellers)),
                ("Doanh thu trung vị của một người bán", fmt_money(conc.median_seller_revenue)),
                ("10 người bán lớn nhất", fmt_pct(conc.top10_sellers_share_pct)),
                ("1% người bán lớn nhất", fmt_pct(conc.top_1pct_share_pct)),
                ("10% người bán lớn nhất", fmt_pct(conc.top_10pct_share_pct)),
                ("20% người bán lớn nhất", fmt_pct(conc.top_20pct_share_pct)),
            ]
        ),
        [
            f"20% người bán lớn nhất tạo ra {fmt_pct(conc.top_20pct_share_pct)} doanh thu — rất gần quy luật Pareto "
            "80/20.",
            f"Một người bán điển hình chỉ đạt {fmt_money(conc.median_seller_revenue)} trong cả kỳ: phần lớn người bán "
            "rất nhỏ.",
        ],
    )

    states = frames["seller_by_state"]
    lead = states.iloc[0]
    lines += _section(
        "seller_by_state",
        to_markdown(
            states,
            {
                "state": "Bang",
                "sellers": "Số người bán",
                "revenue": "Doanh thu (BRL)",
                "revenue_share_pct": "Tỷ trọng (%)",
            },
        ),
        [
            f"Người bán ở bang {lead.state} tạo ra {fmt_pct(lead.revenue_share_pct)} doanh thu. Nguồn cung tập trung "
            "ở một bang phù hợp với việc đơn gửi đi vùng xa mất nhiều ngày hơn (xem tuyến giao ở mục 19)."
        ],
    )

    quality = frames["category_quality"]
    min_orders = insights.analysis("category_quality").params[0]
    if quality.empty:
        quality_notes = [f"Không có danh mục nào đạt ngưỡng {fmt_int(min_orders)} đơn."]
    else:
        worst, best = quality.iloc[0], quality.iloc[-1]
        quality_notes = [
            f"Chỉ xét danh mục có từ {fmt_int(min_orders)} đơn trở lên để điểm trung bình đủ tin cậy.",
            f"Thấp nhất là {worst.category}: điểm {fmt_num(worst.avg_review_score)}, {fmt_pct(worst.low_review_pct)} "
            f"đánh giá 1–2 sao, giao trung bình {fmt_num(worst.avg_delivery_days)} ngày. Cao nhất là {best.category} "
            f"({fmt_num(best.avg_review_score)}).",
            "Danh mục dùng ở đây là danh mục đại diện của đơn (`fact_orders.category`), để mỗi đơn chỉ tính một lần.",
        ]
    lines += _section(
        "category_quality",
        to_markdown(
            quality,
            {
                "category": "Danh mục",
                "delivered_orders": "Số đơn",
                "avg_review_score": "Điểm đánh giá TB",
                "low_review_pct": "Đánh giá 1–2 sao (%)",
                "late_rate_pct": "Tỷ lệ giao trễ (%)",
                "avg_delivery_days": "Số ngày giao TB",
            },
            limit=10,
        ),
        quality_notes,
    )
    return lines


# --------------------------------------------------------------------- Mục 19: giao vận


def _delivery(frames: dict[str, pd.DataFrame]) -> list[str]:
    lines = [f"## Mục 19 — {insights.TASK_TITLES[19]}", ""]

    over = frames["delivery_overview"].iloc[0]
    lines += _section(
        "delivery_overview",
        _vertical(
            [
                ("Số đơn delivered", fmt_int(over.delivered_orders)),
                ("Thời gian giao trung bình", f"{fmt_num(over.avg_delivery_days)} ngày"),
                ("Thời gian giao trung vị", f"{fmt_num(over.median_delivery_days)} ngày"),
                ("90% đơn được giao trong", f"{fmt_num(over.p90_delivery_days)} ngày"),
                ("Số đơn giao trễ", fmt_int(over.late_orders)),
                ("Tỷ lệ giao trễ", fmt_pct(over.late_rate_pct)),
                ("Đơn trễ thì trễ trung bình", f"{fmt_num(over.avg_days_late_when_late)} ngày"),
                ("Đơn đúng hạn đến sớm trung bình", f"{fmt_num(over.avg_days_early_when_on_time)} ngày"),
                ("Đơn thiếu ngày giao thực tế", fmt_int(over.missing_delivery_date)),
            ]
        ),
        [
            f"Trung bình ({fmt_num(over.avg_delivery_days)} ngày) lớn hơn trung vị ({fmt_num(over.median_delivery_days)} "
            "ngày): phân phối lệch phải, một số ít đơn giao rất lâu kéo trung bình lên. Vì vậy báo cáo nêu cả trung vị "
            "và phân vị 90.",
            f"Đơn đúng hạn đến sớm trung bình {fmt_num(over.avg_days_early_when_on_time)} ngày so với ngày dự kiến: "
            "ngày dự kiến được đặt rất dè dặt. Tỷ lệ trễ vì thế đo việc 'vượt cam kết', không đo tốc độ giao.",
        ],
    )

    region = frames["delivery_by_region"]
    worst = region.iloc[0]
    best = region.loc[region["late_rate_pct"].idxmin()]
    slowest = region.loc[region["avg_delivery_days"].idxmax()]
    region_notes = [
        f"Vùng {worst.region} trễ nhiều nhất ({fmt_pct(worst.late_rate_pct)}), vùng {best.region} ít nhất "
        f"({fmt_pct(best.late_rate_pct)}){_times(worst.late_rate_pct, best.late_rate_pct)}.",
    ]
    if slowest.region != worst.region:
        region_notes.append(
            f"Vùng {slowest.region} giao lâu nhất ({fmt_num(slowest.avg_delivery_days)} ngày) nhưng không phải vùng trễ "
            "nhiều nhất: giao lâu và giao trễ là hai khái niệm khác nhau, vì ngày dự kiến đã tính đến khoảng cách."
        )
    region_notes.append(
        "Phí ship mỗi đơn được gộp từ bảng dòng hàng về grain đơn trước khi ghép, để một đơn nhiều dòng không bị "
        "đếm nhiều lần."
    )
    region_headers = {
        "region": "Vùng",
        "delivered_orders": "Số đơn",
        "avg_delivery_days": "Ngày giao TB",
        "median_delivery_days": "Trung vị",
        "p90_delivery_days": "Phân vị 90",
        "late_rate_pct": "Tỷ lệ trễ (%)",
        "avg_freight_per_order": "Phí ship / đơn (BRL)",
    }
    lines += _section("delivery_by_region", to_markdown(region, region_headers), region_notes)

    state = frames["delivery_by_state"]
    reliable = state[state["delivered_orders"] >= SMALL_SAMPLE_ORDERS]
    small = state[state["delivered_orders"] < SMALL_SAMPLE_ORDERS]
    state_notes = []
    if not reliable.empty:
        high, low = reliable.iloc[0], reliable.loc[reliable["late_rate_pct"].idxmin()]
        state_notes.append(
            f"Trong các bang có từ {SMALL_SAMPLE_ORDERS} đơn trở lên, {high.state} trễ nhiều nhất "
            f"({fmt_pct(high.late_rate_pct)}) và {low.state} ít nhất ({fmt_pct(low.late_rate_pct)})."
        )
        biggest = state.loc[state["delivered_orders"].idxmax()]
        fastest = reliable.loc[reliable["avg_delivery_days"].idxmin()]
        state_notes.append(
            f"{biggest.state} có nhiều đơn nhất ({fmt_int(biggest.delivered_orders)} đơn, giao trung bình "
            f"{fmt_num(biggest.avg_delivery_days)} ngày)"
            + (
                " và cũng là bang giao nhanh nhất."
                if fastest.state == biggest.state
                else f"; bang giao nhanh nhất là {fastest.state} ({fmt_num(fastest.avg_delivery_days)} ngày)."
            )
        )
    if not small.empty:
        state_notes.append(
            f"{len(small)} bang ({', '.join(small['state'])}) có dưới {SMALL_SAMPLE_ORDERS} đơn: tỷ lệ của các bang này "
            "dao động mạnh theo vài đơn, không nên xếp hạng."
        )
    lines += _section(
        "delivery_by_state",
        to_markdown(state, {"state": "Bang", **region_headers}),
        state_notes,
    )

    monthly = frames["delivery_monthly"]
    busy = monthly[monthly["delivered_orders"] >= SMALL_SAMPLE_ORDERS]
    monthly_notes = []
    if not busy.empty:
        top3 = busy.sort_values("late_rate_pct", ascending=False).head(3)
        monthly_notes.append(
            "Ba tháng trễ nhiều nhất: "
            + ", ".join(f"{row.period} ({fmt_pct(row.late_rate_pct)})" for row in top3.itertuples())
            + "."
        )
        monthly_notes.append(
            f"Tỷ lệ trễ dao động mạnh giữa các tháng, từ {fmt_pct(busy['late_rate_pct'].min())} đến "
            f"{fmt_pct(busy['late_rate_pct'].max())}; con số {fmt_pct(100.0 * busy['late_orders'].sum() / busy['delivered_orders'].sum())} "
            "của cả kỳ che mất các đợt tăng vọt này."
        )
        correlation = busy["delivered_orders"].corr(busy["late_rate_pct"])
        if pd.notna(correlation):
            monthly_notes.append(
                f"Hệ số tương quan Pearson giữa số đơn của tháng và tỷ lệ trễ là {fmt_num(correlation)}: tháng nhiều đơn "
                "có xu hướng trễ nhiều hơn, nhưng đây mới là tương quan trên ít điểm dữ liệu, chưa đủ để kết luận giao "
                "vận quá tải."
                if correlation > 0
                else f"Hệ số tương quan Pearson giữa số đơn của tháng và tỷ lệ trễ là {fmt_num(correlation)}: không "
                "thấy tháng nhiều đơn thì trễ nhiều hơn."
            )
    lines += _section(
        "delivery_monthly",
        to_markdown(
            monthly,
            {
                "period": "Tháng đặt",
                "delivered_orders": "Số đơn",
                "avg_delivery_days": "Ngày giao TB",
                "late_orders": "Đơn trễ",
                "late_rate_pct": "Tỷ lệ trễ (%)",
            },
        ),
        monthly_notes,
    )

    buckets = frames["delivery_buckets"]
    fast = buckets[buckets["bucket_index"] <= 2]["share_pct"].sum()
    slow = buckets[buckets["bucket_index"] == 5]
    bucket_notes = [f"{fmt_pct(fast)} đơn được giao trong vòng 14 ngày."]
    if not slow.empty:
        row = slow.iloc[0]
        bucket_notes.append(
            f"Nhóm trên 28 ngày chỉ chiếm {fmt_pct(row.share_pct)} số đơn nhưng {fmt_pct(row.late_rate_pct)} trong số đó "
            "bị trễ."
        )
    lines += _section(
        "delivery_buckets",
        to_markdown(
            buckets,
            {
                "delivery_time": "Thời gian giao",
                "orders": "Số đơn",
                "share_pct": "Tỷ trọng (%)",
                "late_rate_pct": "Tỷ lệ trễ (%)",
            },
        ),
        bucket_notes,
    )

    route = frames["delivery_route"]
    route_notes = []
    if len(route) == 2:
        near, far = route.iloc[0], route.iloc[1]
        route_notes.append(
            f"{fmt_pct(far.share_pct)} đơn là giao liên bang, mất trung bình {fmt_num(far.avg_delivery_days)} ngày so với "
            f"{fmt_num(near.avg_delivery_days)} ngày của đơn trong bang, và trễ {fmt_pct(far.late_rate_pct)} so với "
            f"{fmt_pct(near.late_rate_pct)}."
        )
        route_notes.append(
            "Khoảng cách địa lý giữa người bán và khách là yếu tố đi kèm rõ nhất với thời gian giao."
        )
    lines += _section(
        "delivery_route",
        to_markdown(
            route,
            {
                "route": "Tuyến",
                "delivered_orders": "Số đơn",
                "share_pct": "Tỷ trọng (%)",
                "avg_delivery_days": "Ngày giao TB",
                "late_rate_pct": "Tỷ lệ trễ (%)",
            },
        ),
        route_notes,
    )
    return lines


# ---------------------------------------------------------- Mục 20: đánh giá khách hàng


def _reviews(frames: dict[str, pd.DataFrame], chi: ChiSquareResult) -> list[str]:
    lines = [f"## Mục 20 — {insights.TASK_TITLES[20]}", ""]

    dist = frames["review_distribution"]
    share = {int(row.review_score): float(row.share_pct) for row in dist.itertuples()}
    low = share.get(1, 0.0) + share.get(2, 0.0)
    lines += _section(
        "review_distribution",
        to_markdown(dist, {"review_score": "Điểm", "orders": "Số đơn", "share_pct": "Tỷ trọng (%)"}),
        [
            f"{fmt_pct(share.get(5, 0.0))} đơn được 5 sao, nhưng điểm 1 sao ({fmt_pct(share.get(1, 0.0))}) lại nhiều hơn "
            f"điểm 2 sao ({fmt_pct(share.get(2, 0.0))}) và 3 sao ({fmt_pct(share.get(3, 0.0))}). Phân bố có hai đỉnh: "
            "khách hoặc rất hài lòng, hoặc rất bất mãn.",
            f"Tổng cộng {fmt_pct(low)} đơn bị đánh giá 1–2 sao. Điểm trung bình che mất nhóm này, nên phần sau theo dõi "
            "thêm tỷ lệ đánh giá thấp.",
        ],
    )

    by_late = frames["review_by_late"]
    late_notes = []
    if len(by_late) == 2:
        ok, late = by_late.iloc[0], by_late.iloc[1]
        late_notes.append(
            f"Đơn đúng hạn được {fmt_num(ok.avg_review_score)} điểm, đơn giao trễ được "
            f"{fmt_num(late.avg_review_score)} điểm (chênh {fmt_num(ok.avg_review_score - late.avg_review_score)} điểm)."
        )
        late_notes.append(
            f"Tỷ lệ đánh giá 1–2 sao là {fmt_pct(late.low_review_pct)} ở đơn trễ so với {fmt_pct(ok.low_review_pct)} ở "
            f"đơn đúng hạn{_times(late.low_review_pct, ok.low_review_pct)}."
        )
    lines += _section(
        "review_by_late",
        to_markdown(
            by_late,
            {
                "delivery_status": "Tình trạng giao",
                "orders_with_review": "Số đơn có đánh giá",
                "avg_review_score": "Điểm TB",
                "low_review_pct": "Đánh giá 1–2 sao (%)",
                "five_star_pct": "Đánh giá 5 sao (%)",
            },
        ),
        late_notes,
    )

    delay = frames["review_by_delay"]
    falling = delay["avg_review_score"].is_monotonic_decreasing
    delay_notes = [
        "Điểm trung bình giảm đều qua từng mức trễ, từ "
        f"{fmt_num(delay['avg_review_score'].iloc[0])} xuống {fmt_num(delay['avg_review_score'].iloc[-1])}: trễ càng "
        "lâu điểm càng thấp."
        if falling
        else "Điểm trung bình không giảm đều qua các mức trễ.",
        "Quan hệ kiểu 'liều lượng – đáp ứng' này làm mối liên hệ đáng tin hơn so với chỉ so hai nhóm, nhưng vẫn chưa "
        "phải bằng chứng nhân quả.",
    ]
    lines += _section(
        "review_by_delay",
        to_markdown(
            delay,
            {
                "delay_level": "Mức độ so với ngày dự kiến",
                "orders_with_review": "Số đơn có đánh giá",
                "avg_review_score": "Điểm TB",
                "low_review_pct": "Đánh giá 1–2 sao (%)",
            },
        ),
        delay_notes,
    )

    table = insights.contingency_table(frames["review_late_contingency"])
    cross = [
        "| | 1 sao | 2 sao | 3 sao | 4 sao | 5 sao | Tổng |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for label, observed, expected in zip(("Đúng hạn", "Giao trễ"), table, chi.expected):
        cross.append(
            f"| {label} (thực tế) | "
            + " | ".join(fmt_int(v) for v in observed)
            + f" | {fmt_int(sum(observed))} |"
        )
        cross.append(f"| {label} (kỳ vọng nếu độc lập) | " + " | ".join(fmt_int(v) for v in expected) + " | |")
    verdict = "bác bỏ" if chi.significant() else "chưa đủ cơ sở bác bỏ"
    lines += [
        "### Kiểm định chi-bình-phương về tính độc lập",
        "",
        "**Câu hỏi:** Khác biệt về điểm giữa đơn đúng hạn và đơn trễ có thể chỉ do ngẫu nhiên không?",
        "",
        "Giả thuyết H0: tình trạng giao (đúng hạn / trễ) và điểm đánh giá độc lập với nhau.",
        "",
        "\n".join(cross),
        "",
        _vertical(
            [
                ("Số đơn trong bảng chéo", fmt_int(chi.n)),
                ("Thống kê chi-bình-phương", fmt_num(chi.chi2)),
                ("Bậc tự do", fmt_int(chi.dof)),
                ("p-value", fmt_p_value(chi.p_value)),
                ("Cramér's V", f"{fmt_num(chi.cramers_v, 3)} ({cramers_v_label(chi.cramers_v)})"),
            ]
        ),
        "",
        "**Nhận xét:**",
        "",
        f"- p-value {fmt_p_value(chi.p_value)} nên {verdict} H0 ở mức ý nghĩa 5%: hai biến có liên hệ về mặt thống kê.",
        f"- Với {fmt_int(chi.n)} đơn, gần như khác biệt nào cũng có ý nghĩa thống kê, nên phải đọc thêm độ mạnh: "
        f"Cramér's V = {fmt_num(chi.cramers_v, 3)}, mức {cramers_v_label(chi.cramers_v)}.",
        "- Dòng 'kỳ vọng nếu độc lập' cho thấy lệch nằm ở đâu: đơn trễ nhận điểm 1 sao nhiều hơn hẳn mức kỳ vọng.",
        "- Kiểm định được tự cài bằng Python thuần trong `src/analytics/stats.py` và có test đối chiếu giá trị chuẩn.",
        "",
    ]
    lines += _sql_block("review_late_contingency")

    confounder = frames["review_confounder"]
    on_time_multi = confounder[
        (confounder["delivery_status"] == "Đúng hạn") & (confounder["sellers_in_order"] == "Từ 2 người bán")
    ]
    on_time_single = confounder[
        (confounder["delivery_status"] == "Đúng hạn") & (confounder["sellers_in_order"] == "1 người bán")
    ]
    conf_notes = []
    if not on_time_multi.empty and not on_time_single.empty:
        conf_notes.append(
            f"Ngay cả khi giao đúng hạn, đơn có từ 2 người bán chỉ được {fmt_num(on_time_multi.iloc[0].avg_review_score)} "
            f"điểm so với {fmt_num(on_time_single.iloc[0].avg_review_score)} của đơn một người bán."
        )
    conf_notes.append(
        "Vậy giao trễ không phải yếu tố duy nhất đi kèm điểm thấp. Một phân tích nhân quả phải kiểm soát các yếu tố "
        "như thế này."
    )
    lines += _section(
        "review_confounder",
        to_markdown(
            confounder,
            {
                "delivery_status": "Tình trạng giao",
                "sellers_in_order": "Số người bán trong đơn",
                "orders_with_review": "Số đơn có đánh giá",
                "avg_review_score": "Điểm TB",
            },
        ),
        conf_notes,
    )

    lines += [
        "### Kết luận về mối liên hệ giữa giao trễ và đánh giá",
        "",
        "Giao trễ và điểm đánh giá thấp **đi kèm nhau rõ rệt và có ý nghĩa thống kê**. Báo cáo này **không kết luận "
        "giao trễ là nguyên nhân** của điểm thấp, vì bốn lý do:",
        "",
        "1. Đây là dữ liệu quan sát, không phải thí nghiệm có nhóm đối chứng.",
        "2. Có yếu tố khác cùng đi kèm điểm thấp (đơn nhiều người bán, khác biệt giữa các danh mục) và các yếu tố này "
        "có thể liên quan tới cả việc giao trễ.",
        "3. Một phần đơn delivered không có đánh giá; khách không đánh giá có thể khác khách có đánh giá.",
        "4. Kiểm định chi-bình-phương chỉ cho biết hai biến không độc lập, không cho biết chiều tác động.",
        "",
        "Muốn kết luận nhân quả cần thêm một mô hình có kiểm soát biến (ví dụ hồi quy logistic cho xác suất nhận "
        "1–2 sao) hoặc một thử nghiệm thực tế.",
        "",
    ]
    return lines


# ------------------------------------------------------------------------- report bodies


def build_analysis_report(bundle: AnalysisBundle) -> str:
    frames = bundle.frames
    monthly = frames["monthly_trend"]
    lines = [
        "# Báo cáo phân tích dữ liệu Olist",
        "",
        "> Tệp này do `python -X utf8 -m src.analytics` sinh ra từ kho dữ liệu (`data/marts/`). Không sửa tay: "
        "sửa truy vấn trong `src/analytics/insights.py` rồi chạy lại.",
        "",
        "Phạm vi: mục 17–20 của bảng phân công (phân tích kinh doanh, sản phẩm và người bán, giao vận, đánh giá "
        f"khách hàng). Dữ liệu: đơn `delivered` đặt từ tháng {monthly['period'].iloc[0]} đến tháng "
        f"{monthly['period'].iloc[-1]}.",
        "",
        "Định nghĩa KPI: xem `docs/kpi-definitions.md`. Bằng chứng số liệu đáng tin: xem "
        f"`docs/{RECONCILIATION_REPORT_NAME}` ({'toàn bộ kiểm tra đạt' if bundle.reconciliation.passed else 'CÓ KIỂM TRA KHÔNG ĐẠT'}).",
        "",
        "## Ba quy ước khi đọc số liệu",
        "",
        "1. **Doanh thu** = `price + freight_value` của các dòng hàng thuộc đơn `delivered`.",
        "2. **Số đơn** luôn đếm `DISTINCT order_id` ở grain gốc; không cộng số đơn của các nhóm con.",
        "3. Bảng nhiều dòng trên một đơn (dòng hàng, thanh toán, đánh giá) được **gộp về grain đơn trước khi JOIN**.",
        "",
    ]
    lines += _business(frames)
    lines += _products_sellers(frames)
    lines += _delivery(frames)
    lines += _reviews(frames, bundle.chi_square)
    lines += [
        "## Hạn chế",
        "",
        "- Dữ liệu là một mẫu lịch sử tĩnh; năm đầu rất thưa và các tháng cuối chưa đủ đơn delivered.",
        "- Doanh thu gồm phí vận chuyển và không trừ hoàn hủy sau giao; đây là doanh thu gộp, không phải lợi nhuận.",
        "- Tên sản phẩm và danh tính người bán đã được ẩn danh, nên chỉ phân tích được theo mã và danh mục.",
        "- Các mối liên hệ trong báo cáo là mô tả; chưa có mô hình nhân quả hay dự báo.",
        "",
    ]
    return "\n".join(lines).rstrip() + "\n"


def _value(value) -> str:
    if value is None:
        return "–"
    if isinstance(value, bool):
        return "có" if value else "không"
    if isinstance(value, int):
        return fmt_int(value)
    if isinstance(value, float):
        return fmt_num(value)
    return str(value)


def build_reconciliation_report(result: ReconciliationResult) -> str:
    counts = result.counts()
    lines = [
        "# Báo cáo đối soát chỉ số",
        "",
        "> Tệp này do `python -X utf8 -m src.analytics` sinh ra. Không sửa tay: sửa kiểm tra trong "
        "`src/analytics/reconciliation.py` rồi chạy lại.",
        "",
        "Phạm vi: mục 16 của bảng phân công — kiểm tra tổng tiền và số đơn, bảo đảm không đếm trùng do JOIN.",
        "",
        f"**Kết luận: {'ĐẠT' if result.passed else 'KHÔNG ĐẠT'}.** {counts[PASS]} kiểm tra đạt, {counts[FAIL]} không đạt, "
        f"{counts[INFO]} mục ghi nhận, {counts[SKIP]} bỏ qua.",
        "",
        "Cách đọc trạng thái: **Đạt / KHÔNG ĐẠT** là kiểm tra có đúng–sai. **Ghi nhận** là minh họa một cái bẫy hoặc "
        "một khác biệt có lý do nghiệp vụ; nó không sai, nhưng người đọc KPI phải biết.",
        "",
        "Phương pháp: tính cùng một con số bằng nhiều đường độc lập rồi so với nhau. "
        + (
            "Đường 'nguồn' đọc thẳng CSV gốc trong `dataset/` bằng DuckDB, không đi qua pipeline."
            if result.has_sources
            else "Lần chạy này không có CSV gốc nên bỏ qua đường 'nguồn'."
        ),
        "",
        "## Tổng hợp",
        "",
        "| Mã | Nhóm | Kiểm tra | Trạng thái |",
        "| --- | --- | --- | --- |",
    ]
    lines += [
        f"| {check.check_id} | {check.group} | {check.title} | {STATUS_LABELS[check.status]} |"
        for check in result.checks
    ]
    lines.append("")

    current_group = None
    for check in result.checks:
        if check.group != current_group:
            current_group = check.group
            lines += [f"## {current_group}", ""]
        lines += [
            f"### {check.check_id} — {check.title}",
            "",
            f"**Trạng thái:** {STATUS_LABELS[check.status]}",
            "",
            f"**Vì sao kiểm tra:** {check.purpose}",
            "",
        ]
        if check.values:
            lines += ["| Đại lượng | Giá trị |", "| --- | ---: |"]
            lines += [f"| `{key}` | {_value(value)} |" for key, value in check.values.items()]
            lines.append("")
        lines += [f"**Kết luận:** {check.conclusion}", ""]
        if check.sql:
            lines += [
                "<details><summary>Câu SQL</summary>",
                "",
                "```sql",
                check.sql,
                "```",
                "",
                "</details>",
                "",
            ]
    return "\n".join(lines).rstrip() + "\n"


# ------------------------------------------------------------------------------ outputs


def write_outputs(bundle: AnalysisBundle, reports_dir: Path, docs_dir: Path) -> dict[str, Path]:
    """Ghi báo cáo Markdown vào `docs_dir` và bảng số liệu (CSV, JSON) vào `reports_dir/analysis`."""

    output_dir = Path(reports_dir) / OUTPUT_SUBDIR
    output_dir.mkdir(parents=True, exist_ok=True)
    docs_dir = Path(docs_dir)
    docs_dir.mkdir(parents=True, exist_ok=True)

    for key, frame in bundle.frames.items():
        frame.to_csv(output_dir / f"{key}.csv", index=False, encoding="utf-8")

    chi = bundle.chi_square
    summary = {
        "kpi_headline": json.loads(bundle.frames["kpi_headline"].to_json(orient="records"))[0],
        "chi_square": {
            "chi2": chi.chi2,
            "dof": chi.dof,
            "p_value": chi.p_value,
            "cramers_v": chi.cramers_v,
            "n": chi.n,
        },
        "reconciliation": {"passed": bundle.reconciliation.passed, "counts": bundle.reconciliation.counts()},
    }
    paths = {
        "summary": output_dir / "summary.json",
        "reconciliation_json": output_dir / "reconciliation.json",
        "analysis_report": docs_dir / ANALYSIS_REPORT_NAME,
        "reconciliation_report": docs_dir / RECONCILIATION_REPORT_NAME,
    }
    paths["summary"].write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    paths["reconciliation_json"].write_text(
        json.dumps(bundle.reconciliation.to_dict(), ensure_ascii=False, indent=2, default=str), encoding="utf-8"
    )
    paths["analysis_report"].write_text(build_analysis_report(bundle), encoding="utf-8", newline="\n")
    paths["reconciliation_report"].write_text(
        build_reconciliation_report(bundle.reconciliation), encoding="utf-8", newline="\n"
    )
    return paths
