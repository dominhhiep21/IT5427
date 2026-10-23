"""CLI entrypoint for pipeline, micro-batch and replay."""

from __future__ import annotations

import argparse
import sys

from src.config import load_config
from src.pipeline.micro_batch import process_inbox
from src.pipeline.replay import generate
from src.pipeline.stages import run_all, run_stage


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m src.pipeline",
        description="Olist e-commerce pipeline",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    run = sub.add_parser("run", help="Run one stage or the full pipeline")
    run.add_argument(
        "--stage",
        choices=("all", "ingest", "clean", "integrate", "analyze"),
        default="all",
    )
    run.add_argument("--refresh-ibge", action="store_true")

    batch = sub.add_parser("micro-batch", help="Process inbox micro-batches")
    batch.add_argument("--inbox", default=None)

    replay = sub.add_parser("replay", help="Generate and process historical batches")
    replay.add_argument("--batches", type=int, default=3)

    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    config = load_config()
    try:
        if args.command == "run":
            if args.stage == "all":
                summary = run_all(config, refresh_ibge=args.refresh_ibge)
            else:
                summary = run_stage(
                    config, args.stage, refresh_ibge=args.refresh_ibge
                )
            print(f"run_id={summary.run_id} success={summary.success}")
            for stage in summary.stages:
                print(
                    f"  {stage.stage}: {stage.status} "
                    f"rows_in={stage.rows_in} rows_out={stage.rows_out} "
                    f"{stage.duration_seconds}s"
                )
            return 0 if summary.success else 1

        if args.command == "micro-batch":
            results = process_inbox(config, args.inbox)
            for result in results:
                print(
                    f"batch={result.batch_id} status={result.status} "
                    f"rows={result.rows_upserted} {result.duration_seconds}s"
                )
            return 0 if all(item.status in {"success", "skipped"} for item in results) else 1

        if args.command == "replay":
            batches = generate(config, args.batches)
            print(f"generated={len(batches)} batches")
            results = process_inbox(config, config.inbox_dir / "replay")
            for result in results:
                print(f"batch={result.batch_id} status={result.status}")
            return 0 if all(item.status in {"success", "skipped"} for item in results) else 1
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
