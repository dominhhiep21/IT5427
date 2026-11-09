# Code Generation Plan Approval

AI-DLC writes this file when it asks you to approve the plan. To answer here
instead of in chat, write your answer after `[Answer]:` and tell me in chat when you are done.

## Plan Approval

Approve the code plan for u4-record-linkage?

- Builds: ghép bản ghi khách/người bán bằng hai bằng chứng (địa lý + hành vi mua), ngưỡng 0,85, ghi hai tệp JSON theo C5.
- Touches: `src/linkage/` (mới), `src/pipeline/stages.py` (gọi một lần), `config.yaml` + `src/config.py` (`paths.integration_dir`), `.github/workflows/ci.yml` (mở rộng phạm vi định dạng), `tests/unit...
- Tests: 4 tệp unit mới theo TDD (khoảng 28–34 test), gồm một test hiệu năng riêng cho phần chấm điểm.
- Already changed before you approved (10 files): assets/style.css, data/cleaned/orders.parquet, data/reports/cleaning-report.json, data/reports/ingest-report.json, data/reports/integration-report.json, data/reports/kpi-reconciliation.json, data/reports/quality-report.json, data/reports/run-summary.json, ruff.toml, tests/conftest.py.

Full plan: aidlc/spaces/default/intents/261105-doc-knowledge-upgrade/construction/u4-record-linkage/code-generation/code-generation-plan.md
Test instructions: aidlc/spaces/default/intents/261105-doc-knowledge-upgrade/construction/u4-record-linkage/code-generation/unit-test-instructions.md

[Approval Fingerprint]: sha256:v3:f1ea65b1ad101e865f4116067f01a30e60ce5be38c340e964d317c2638d8b10e
[Planned Source]: 6109bdf2c9dd5e12f497aaa26bc34f2f29887abf3986965730a2ac7e8ee91fed

- A. Approve Plan
- B. Request Changes
- C. I'll edit the files

[Answer]: A. Approve Plan
