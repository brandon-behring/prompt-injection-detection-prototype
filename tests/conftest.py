"""Pytest configuration: marker registration + shared fixtures."""


def pytest_configure(config):
    """Register custom pytest markers (mirrors pyproject.toml)."""
    config.addinivalue_line("markers", "unit: fast, deterministic unit tests")
    config.addinivalue_line("markers", "smoke: end-to-end smoke tests (~5 min)")
    config.addinivalue_line(
        "markers", "integration: integration tests (may need network or GPU)"
    )
    config.addinivalue_line("markers", "network: tests that require network access")


# Common fixtures populated at Phase 1.
