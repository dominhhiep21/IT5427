"""Unit test cho `.github/workflows/ci.yml`: nhánh trigger và danh sách `ruff format --check` (NFR4.2)."""

from __future__ import annotations

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = ROOT / ".github" / "workflows" / "ci.yml"
BRANCH = "feature/analysis-and-models"

# Mọi tệp nguồn và tệp test mới của đơn vị này, phải có mặt trong danh sách format khai tay.
NEW_FILES = (
    "src/analytics/report.py",
    "src/analytics/statistics.py",
    "src/analytics/model.py",
    "src/analytics/service.py",
    "src/dashboard/analysis_tab.py",
    "tests/unit/test_analytics_report.py",
    "tests/unit/test_analytics_statistics.py",
    "tests/unit/test_analytics_model.py",
    "tests/unit/test_pipeline_stages.py",
    "tests/unit/test_ci_config.py",
    "tests/unit/test_dashboard_analysis_tab.py",
    "tests/unit/test_analysis_tab_contrast.py",
    "tests/integration/test_u1_stats_end_to_end.py",
    "tests/integration/test_u2_model_end_to_end.py",
    "src/analytics/persistence.py",
    "tests/unit/test_analytics_training_frame.py",
    "tests/unit/test_analytics_features.py",
    "tests/unit/test_analytics_split.py",
    "tests/unit/test_analytics_threshold.py",
    "tests/unit/test_analytics_baseline_block.py",
    "tests/unit/test_analytics_report_v3.py",
    "tests/unit/test_analytics_persistence.py",
    "tests/unit/test_analytics_score_item.py",
    "src/dashboard/prediction_section.py",
    "tests/unit/test_u3_prediction_section.py",
    "tests/integration/test_u3_floor_end_to_end.py",
)


def workflow() -> dict:
    return yaml.safe_load(WORKFLOW.read_text(encoding="utf-8"))


def triggers() -> dict:
    data = workflow()
    # PyYAML đọc khoá `on` thành True theo YAML 1.1, nên phải thử cả hai khoá.
    return data.get("on", data.get(True))


def steps() -> list[dict]:
    return workflow()["jobs"]["ci"]["steps"]


def test_both_trigger_lists_include_the_branch_of_this_round():
    data = triggers()

    assert BRANCH in data["push"]["branches"]
    assert BRANCH in data["pull_request"]["branches"]


def test_both_trigger_lists_keep_the_existing_branches():
    data = triggers()

    assert {"main", "feature/update-ui-ux"} <= set(data["push"]["branches"])
    assert {"main", "feature/update-ui-ux"} <= set(data["pull_request"]["branches"])


def format_targets() -> list[str]:
    for step in steps():
        for line in str(step.get("run", "")).splitlines():
            stripped = line.strip()
            if stripped.startswith("ruff format --check"):
                return stripped.split()[3:]
    raise AssertionError("ci.yml không còn bước `ruff format --check`")


def test_every_new_file_is_in_the_manual_format_list():
    targets = set(format_targets())

    assert set(NEW_FILES) <= targets


def test_format_list_still_covers_the_previous_round_files():
    targets = set(format_targets())

    assert "src/integration/tab.py" in targets
    assert "src/common/kpis.py" in targets


def test_the_format_list_has_no_entry_pointing_outside_the_repository():
    for target in format_targets():
        assert not Path(target).is_absolute()
        assert (ROOT / target).exists()


def test_stats_stage_runs_after_the_data_build_and_before_the_tests():
    commands = [str(step.get("run", "")) for step in steps()]

    all_index = next(index for index, command in enumerate(commands) if "run --stage all" in command)
    stats_index = next(index for index, command in enumerate(commands) if "run --stage stats" in command)
    test_index = next(index for index, command in enumerate(commands) if 'pytest -m "not slow"' in command)

    assert all_index < stats_index < test_index


def test_the_coverage_gate_is_not_weakened():
    commands = [str(step.get("run", "")) for step in steps()]

    assert any("--cov-fail-under=80" in command and '-m "not slow"' not in command for command in commands)


def test_scikit_learn_is_pinned_with_an_exact_version():
    requirements = (ROOT / "requirements.txt").read_text(encoding="utf-8").splitlines()
    pinned = [line for line in requirements if line.startswith("scikit-learn==")]

    assert pinned == ["scikit-learn==1.6.1"]
