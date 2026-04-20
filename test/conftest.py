import os
import pytest
from pathlib import Path
from nbmake.nb_run import NotebookRun

REPO_ROOT = Path(__file__).parent.parent


@pytest.fixture
def repo_root():
    """Return the repository root directory."""
    return REPO_ROOT


@pytest.fixture
def nbmake(request):
    """Run a notebook by path (relative to repo root) and raise on error."""
    timeout = int(request.config.getoption("--nbmake-timeout", default=300))
    kernel = request.config.getoption("--nbmake-kernel") or "test_mlfemotcps"

    def _run(notebook, **kwargs):
        nb_path = REPO_ROOT / notebook
        runner = NotebookRun(
            filename=nb_path,
            default_timeout=timeout,
            kernel=kernel,
        )
        result = runner.execute()
        if result.error:
            raise AssertionError(
                f"Notebook {notebook} failed:\n{result.error.trace}"
            )

    return _run
