import pytest

from src.yield_fetcher import get_yields


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


def test_get_yields_rejects_placeholder_api_key(monkeypatch):
    monkeypatch.setenv("LIFI_API_KEY", "your_lifi_api_key_here")

    with pytest.raises(ValueError, match="placeholder|LIFI_API_KEY"):
        get_yields("USDC", limit=5)


def test_get_yields_parses_valid_response(monkeypatch):
    captured = {}

    def fake_get(url, headers=None, params=None, timeout=None):
        captured["url"] = url
        captured["headers"] = headers
        captured["params"] = params
        captured["timeout"] = timeout
        return DummyResponse({"vaults": [{"name": "Vault A", "apy": 0.08}]})

    monkeypatch.setenv("LIFI_API_KEY", "test-key")
    monkeypatch.setattr("src.yield_fetcher.requests.get", fake_get)

    result = get_yields("USDC", limit=5)

    assert result == [{"name": "Vault A", "apy": 0.08}]
    assert captured["url"] == "https://earn.li.fi/v1/vaults"
    assert captured["headers"] == {"Authorization": "Bearer test-key"}
    assert captured["params"] == {"asset": "USDC", "sortBy": "apy", "limit": 5}
    assert captured["timeout"] == 15
