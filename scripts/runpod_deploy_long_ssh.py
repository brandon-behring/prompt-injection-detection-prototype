"""Stopgap shim — extends runpod-deploy's SSH-ready timeout from 240s to 600s.

Pending upstream brandon-behring/runpod-deploy issue #88 — make the SSH-ready
timeout configurable (and bump default to 600s). Cold pulls of cudnn-devel
images regularly exceed the hardcoded 4-min deadline in v0.7.7's
`provider._wait_for_pod_ready` (observed 2026-05-17 on US-MD-1 SECURE
A100-SXM4-80GB with `runpod/pytorch:2.5.0-py3.13-cuda12.4.1-cudnn9-devel`).

Usage
-----
.. code-block:: bash

    # Anywhere a Makefile would `uv run runpod-deploy <subcommand>`, use:
    uv run python scripts/runpod_deploy_long_ssh.py <subcommand> [...args]

Mechanism
---------
Module-level monkey-patch of ``runpod_deploy.provider._wait_for_pod_ready``
re-bound with a 600s deadline (10 min). Identical logic otherwise — same
PodConnection construction, same polling loop, same logger. Removed when
upstream #88 lands + we bump the runpod-deploy pin.

Removal trigger (per decisions/upstream_issues.md)
--------------------------------------------------
- runpod-deploy version bumped to a release containing the fix
- `budget.ssh_ready_timeout_sec` field added to all configs/runpod/headline-*.yaml
- This file deleted; Makefile reverts to `uv run runpod-deploy ...`
"""

from __future__ import annotations

import sys
import time
from typing import Any

from runpod_deploy import provider
from runpod_deploy.cli import main

# Keep references to upstream primitives we need verbatim.
_run_json = provider.run_json
_PodConnection = provider.PodConnection
_logger = provider.logger

# Upstream default: 240s (4 min). Bumped to 600s (10 min) here.
_SSH_READY_DEADLINE_SEC = 600


def _wait_for_pod_ready_extended(pod_id: str, *, gpu_id: str) -> "provider.PodConnection":
    """Inline rebind of provider._wait_for_pod_ready with 600s deadline.

    Logic mirrored verbatim from v0.7.7 except for the deadline constant —
    keep the diff minimal so re-syncing with upstream is trivial.
    """
    deadline = time.time() + _SSH_READY_DEADLINE_SEC
    last_payload: dict[str, Any] = {}
    while time.time() < deadline:
        payload = _run_json(["runpodctl", "pod", "get", pod_id, "-o", "json"])
        if isinstance(payload, dict):
            last_payload = payload
            status = payload.get("desiredStatus") or payload.get("status")
            ssh_payload = payload.get("ssh")
            ssh_info = ssh_payload if isinstance(ssh_payload, dict) else {}
            host = str(ssh_info.get("ip") or payload.get("publicIp") or "")
            port_raw = ssh_info.get("port")
            port = int(port_raw or 0)
            if status == "RUNNING" and host and port:
                _logger.info(f"[pod] {pod_id} RUNNING ssh={host}:{port} gpu={gpu_id}")
                return _PodConnection(pod_id=pod_id, host=host, port=port, gpu_id=gpu_id)
        time.sleep(5)
    raise RuntimeError(f"pod {pod_id} did not become SSH-ready; last={last_payload}")


# Install the monkey-patch BEFORE invoking the CLI; the CLI imports
# orchestrator -> provider lazily via the call chain and picks up our rebind.
provider._wait_for_pod_ready = _wait_for_pod_ready_extended


if __name__ == "__main__":
    sys.exit(main())
