"""CLI parser tests."""

from __future__ import annotations

from src.pipeline.cli import build_parser, main


def test_run_stage_defaults_to_all():
    args = build_parser().parse_args(["run"])
    assert args.stage == "all"


def test_micro_batch_and_replay_parse():
    args = build_parser().parse_args(["micro-batch", "--inbox", "inbox"])
    assert args.inbox == "inbox"
    args = build_parser().parse_args(["replay", "--batches", "2"])
    assert args.batches == 2


def test_main_analyze_stage():
    assert main(["run", "--stage", "analyze"]) == 0
