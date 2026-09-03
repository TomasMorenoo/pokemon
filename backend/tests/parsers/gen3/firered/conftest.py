import pytest
from pathlib import Path

FIXTURES_DIR = Path(__file__).parent.parent.parent.parent / "fixtures"


def load_fixture(name: str) -> bytes:
    path = FIXTURES_DIR / name
    if not path.exists():
        pytest.skip(f"Fixture {name} not found — add a real .sav to tests/fixtures/")
    return path.read_bytes()
