"""Unit tests for scripts/audit_*.py pure-function primitives.

Each test targets a load-bearing primitive function (typically the validator
or analyzer logic, separate from the CLI wrapper). Tests use synthetic input
data or `tmp_path` fixtures; no live filesystem dependency on the project
source tree.

Per v1.3.5 (2026-05-24): added as upstream-port-readiness signal for
eval-toolkit #71 / #72 / #73 (`src/eval_toolkit/audit/` subpackage).
"""
