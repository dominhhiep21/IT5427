"""CLI của phần phân tích: `python -X utf8 -m src.analytics`.

- không tham số: chạy đối soát + toàn bộ phân tích, ghi báo cáo vào `docs/` và số liệu vào
  `data/reports/analysis/`;
- `--check`: chỉ chạy đối soát, trả mã thoát 1 nếu có kiểm tra không đạt (dùng làm cổng kiểm soát);
- `--list`: liệt kê các phân tích; `--show <mã>`: in kết quả một phân tích ra màn hình.
"""

from __future__ import annotations

import argparse
import sys

import pandas as pd

from src.analytics import insights
from src.analytics.connection import open_analysis_connection
from src.analytics.reconciliation import FAIL, run_reconciliation
from src.analytics.report import STATUS_LABELS, run_bundle, write_outputs
from src.config import load_config


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m src.analytics",
        description="Đối soát chỉ số và phân tích dữ liệu Olist trên star schema",
    )
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--check", action="store_true", help="chỉ chạy đối soát chỉ số")
    mode.add_argument("--list", action="store_true", help="liệt kê các phân tích")
    mode.add_argument("--show", metavar="MÃ", help="in kết quả một phân tích")
    parser.add_argument("--docs-dir", default=None, help="thư mục ghi báo cáo Markdown (mặc định: docs/)")
    return parser


def _print_reconciliation(result) -> None:
    for check in result.checks:
        print(f"[{STATUS_LABELS[check.status]:>9}] {check.check_id} {check.title}")
        if check.status == FAIL:
            print(f"            {check.conclusion}")
    counts = result.counts()
    print(
        f"Đối soát: {'ĐẠT' if result.passed else 'KHÔNG ĐẠT'} — "
        f"{counts['pass']} đạt, {counts['fail']} không đạt, {counts['info']} ghi nhận, {counts['skip']} bỏ qua"
    )


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    if args.list:
        for item in insights.ANALYSES.values():
            print(f"mục {item.task}  {item.key:<26} {item.title}")
        return 0

    config = load_config()
    try:
        conn = open_analysis_connection(config)
    except FileNotFoundError as exc:
        print(f"LỖI: {exc}", file=sys.stderr)
        return 1

    try:
        if args.show:
            try:
                frame = insights.run_analysis(conn, args.show)
            except KeyError as exc:
                print(f"LỖI: {exc.args[0]}", file=sys.stderr)
                return 1
            item = insights.analysis(args.show)
            print(f"{item.title}\n{item.question}\n")
            with pd.option_context("display.width", 250, "display.max_columns", 40, "display.max_rows", 200):
                print(frame.to_string(index=False))
            return 0

        if args.check:
            result = run_reconciliation(conn)
            _print_reconciliation(result)
            return 0 if result.passed else 1

        bundle = run_bundle(conn)
        docs_dir = args.docs_dir or (config.workspace_root / "docs")
        paths = write_outputs(bundle, config.reports_dir, docs_dir)
        _print_reconciliation(bundle.reconciliation)
        print(f"Đã chạy {len(bundle.frames)} phân tích.")
        for label, path in paths.items():
            print(f"  {label}: {path}")
        return 0 if bundle.reconciliation.passed else 1
    finally:
        conn.close()


if __name__ == "__main__":
    raise SystemExit(main())
