import pytest

from src.ai_advisor import is_halal
from src.yield_fetcher import get_yields, run_yield_analysis


class DummyResponse:
    def __init__(self, payload: dict, status_code: int = 200):
        self.payload = payload
        self.status_code = status_code

    def raise_for_status(self):
        if self.status_code >= 400:
            raise RuntimeError(f"HTTP {self.status_code}")

    def json(self):
        return self.payload


def test_get_yields_requires_lifi_api_key(monkeypatch):
    monkeypatch.delenv("LIFI_API_KEY", raising=False)
    monkeypatch.delenv("LI_FI_API_KEY", raising=False)

    with pytest.raises(ValueError, match="LIFI_API_KEY"):
        get_yields("USDC", limit=5)

