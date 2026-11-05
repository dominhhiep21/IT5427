"""Build Quizizz-format .xlsx files from the Python question banks in ./data.

Usage:
    python -X utf8 build_quiz.py          # build every workbook + run checks
    python -X utf8 build_quiz.py --check  # only run the quality checks

Each bank module exposes QUESTIONS = [(stem, [options], answer, explanation), ...]
where answer is an int (single choice) or a list of ints (checkbox).
"""

from __future__ import annotations

import hashlib
import importlib.util
import random
import statistics
import sys
from pathlib import Path

import openpyxl
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter

BASE = Path(__file__).resolve().parent
DATA = BASE / "data"

HEADER = [
    "Question Text",
    "Question Type",
    "Option 1",
    "Option 2",
    "Option 3",
    "Option 4",
    "Option 5",
    "Correct Answer",
    "Time in seconds",
    "Image Link",
    "Answer explanation",
]

# (module name, output file stem, topic label)
BATCHES = [
    ("b1a", "Quiz_DI_01_NenTang_DiBiet_A", "Nền tảng tích hợp dữ liệu & dị biệt (phần A)"),
    ("b1b", "Quiz_DI_01_NenTang_DiBiet_B", "Nền tảng tích hợp dữ liệu & dị biệt (phần B)"),
    ("b2a", "Quiz_DI_02_AnhXaLuocDo_A", "Ánh xạ lược đồ GAV/LAV/GLAV (phần A)"),
    ("b2b", "Quiz_DI_02_AnhXaLuocDo_B", "Ánh xạ lược đồ & viết lại truy vấn (phần B)"),
    ("b2c", "Quiz_DI_02_AnhXaLuocDo_C", "Ánh xạ lược đồ & viết lại truy vấn (phần C)"),
    ("b3", "Quiz_DI_03_TruyVanTrungGian", "Sinh truy vấn trung gian từ lược đồ"),
    ("b4a", "Quiz_DI_04_RecordLinkage_A", "Record linkage & entity resolution (phần A)"),
    ("b4b", "Quiz_DI_04_RecordLinkage_B", "Record linkage & entity resolution (phần B)"),
    ("b4c", "Quiz_DI_04_RecordLinkage_C", "Record linkage & entity resolution (phần C)"),
    ("b5a", "Quiz_DI_05_QueryProcessing_A", "Xử lý truy vấn thích ứng (phần A)"),
    ("b5b", "Quiz_DI_05_QueryProcessing_B", "Xử lý truy vấn thích ứng (phần B)"),
    ("b6a", "Quiz_DI_06_NguonDuLieu_A", "Wrapper & kỹ thuật trích xuất dữ liệu (phần A)"),
    ("b6b", "Quiz_DI_06_NguonDuLieu_B", "Profiling & chọn nguồn dữ liệu (phần B)"),
]


def load(name: str):
    path = DATA / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module.QUESTIONS


def normalise(raw, where: str):
    if len(raw) == 4:
        stem, options, answer, explanation = raw
        time = 45 if isinstance(answer, list) else 30
    elif len(raw) == 5:
        stem, options, answer, explanation, time = raw
    else:
        raise ValueError(f"{where}: tuple must have 4 or 5 items")
    options = [str(o).strip() for o in options]
    answer = list(answer) if isinstance(answer, (list, tuple)) else answer
    return {
        "stem": str(stem).strip(),
        "options": options,
        "answer": answer,
        "explanation": str(explanation).strip(),
        "time": int(time),
        "where": where,
    }


def arrange(item, k: int):
    """Shuffle distractors, then park the correct option on a balanced slot."""
    options = item["options"]
    seed = hashlib.md5(item["stem"].encode("utf-8")).hexdigest()
    rng = random.Random(seed)

    if isinstance(item["answer"], list):
        order = list(range(len(options)))
        rng.shuffle(order)
        new_options = [options[i] for i in order]
        new_answer = sorted(order.index(i) + 1 for i in item["answer"])
        return new_options, ",".join(str(x) for x in new_answer)

    correct = item["answer"]
    assert isinstance(correct, int) and 0 <= correct < len(options)
    target = (k % 4) if (k // 4) % 2 == 0 else (3 - k % 4)
    others = [i for i in range(len(options)) if i != correct]
    rng.shuffle(others)
    layout = [None] * len(options)
    layout[target] = correct
    slots = [i for i in range(len(options)) if i != target]
    for slot, idx in zip(slots, others):
        layout[slot] = idx
    new_options = [options[i] for i in layout]
    return new_options, target + 1


def check(items):
    problems, cues = [], []
    seen = {}
    for item in items:
        where = item["where"]
        stem, opts, ans = item["stem"], item["options"], item["answer"]
        if not 20 <= len(stem) <= 320:
            problems.append(f"{where}: stem length {len(stem)}")
        if len(opts) != 4:
            problems.append(f"{where}: needs exactly 4 options")
        if len({o.lower() for o in opts}) != len(opts):
            problems.append(f"{where}: duplicate option text")
        if isinstance(ans, list):
            if not 2 <= len(ans) <= 3:
                problems.append(f"{where}: checkbox needs 2-3 correct options")
            if any(not 0 <= a < len(opts) for a in ans):
                problems.append(f"{where}: bad checkbox index")
        else:
            if not 0 <= ans < len(opts):
                problems.append(f"{where}: bad answer index")
        if len({o.lower() for o in opts}) < 4:
            problems.append(f"{where}: fewer than 4 distinct options")
        if stem.lower() in seen:
            problems.append(f"{where}: duplicate stem of {seen[stem.lower()]}")
        seen[stem.lower()] = where

        if not isinstance(ans, list):
            correct_len = len(opts[ans])
            other_lengths = [len(o) for i, o in enumerate(opts) if i != ans]
            mean_other = statistics.mean(other_lengths)
            spread = max(len(o) for o in opts) - min(len(o) for o in opts)
            if correct_len - mean_other > 7 or mean_other - correct_len > 9:
                cues.append(
                    f"{where}: correct={correct_len} others~{mean_other:.0f} "
                    f"spread={spread} | {stem[:70]}"
                )
            elif correct_len == max(len(o) for o in opts) and spread > 26:
                cues.append(
                    f"{where}: correct is the longest, spread={spread} | {stem[:70]}"
                )
    return problems, cues


def write_workbook(path: Path, items):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Create a Quiz"
    ws.append(HEADER)

    head_fill = PatternFill("solid", fgColor="1F4E79")
    for cell in ws[1]:
        cell.font = Font(bold=True, color="FFFFFF", size=11)
        cell.fill = head_fill
        cell.alignment = Alignment(wrap_text=True, vertical="center")

    for k, item in enumerate(items):
        options, answer = arrange(item, k)
        ws.append(
            [
                item["stem"],
                "Checkbox" if isinstance(item["answer"], list) else "Multiple Choice",
                *options,
                None,
                answer,
                item["time"],
                None,
                item["explanation"],
            ]
        )

    widths = [46, 16, 30, 30, 30, 30, 10, 13, 9, 11, 52]
    for i, width in enumerate(widths, start=1):
        ws.column_dimensions[get_column_letter(i)].width = width
    for row in ws.iter_rows(min_row=2, max_row=ws.max_row):
        for cell in row:
            cell.alignment = Alignment(wrap_text=True, vertical="top")
    ws.freeze_panes = "A2"
    ws.auto_filter.ref = f"A1:K{ws.max_row}"
    wb.save(path)


def main():
    check_only = "--check" in sys.argv
    all_items = []
    per_batch = {}

    for name, out, topic in BATCHES:
        if not (DATA / f"{name}.py").exists():
            print(f"[skip] {name}: data file missing")
            continue
        raw = load(name)
        items = [normalise(r, f"{name}[{i}]") for i, r in enumerate(raw)]
        per_batch[name] = (out, topic, items)
        all_items.extend(items)

    problems, cues = check(all_items)
    print(f"Loaded {len(all_items)} questions from {len(per_batch)} banks.")
    for name, (out, topic, items) in per_batch.items():
        print(f"  {name:4s} {len(items):3d}  {topic}")

    if problems:
        print("\nHARD PROBLEMS")
        for p in problems:
            print("  -", p)
    if cues:
        print(f"\nLENGTH CUES ({len(cues)})")
        for c in cues:
            print("  -", c)

    if not check_only:
        outdir = BASE / "xlsx"
        outdir.mkdir(exist_ok=True)
        for name, (out, topic, items) in per_batch.items():
            path = outdir / f"{out}.xlsx"
            write_workbook(path, items)
            print(f"[write] {path.name}  ({len(items)} câu)")
        merged = outdir / "Quiz_DI_TatCa_500_Cau.xlsx"
        write_workbook(merged, all_items)
        print(f"[write] {merged.name}  ({len(all_items)} câu)")

    report = BASE / "check_report.txt"
    with report.open("w", encoding="utf-8") as fh:
        fh.write(f"Tổng số câu: {len(all_items)}\n\n")
        for name, (out, topic, items) in per_batch.items():
            fh.write(f"{name}: {len(items)} câu - {topic}\n")
        fh.write("\nHARD PROBLEMS\n")
        fh.writelines(f"- {p}\n" for p in problems) if problems else fh.write("- none\n")
        fh.write("\nLENGTH CUES\n")
        fh.writelines(f"- {c}\n" for c in cues) if cues else fh.write("- none\n")
    print(f"\nReport: {report}")

    if problems:
        sys.exit(1)


if __name__ == "__main__":
    main()
