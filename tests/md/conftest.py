from pathlib import Path

import pytest


@pytest.fixture
def write_script():
    """Return a helper that writes an executable script and returns its path."""

    def _write_script(path: Path, body: str) -> Path:
        path = Path(path)
        path.write_text(body)
        path.chmod(0o755)
        return path

    return _write_script
