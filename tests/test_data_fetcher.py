import json
from unittest.mock import Mock

import pytest

from src.data_fetcher import get_quote
from src.test_gemini import generate_gemini_response


class DummyResponse:
    def __init__(self, payload: dict):
        self.payload = payload

    def raise_for_status(self):
        return None

    def json(self):
        return self.payload


def test_get_quote_builds_valid_request(monkeypatch):
    captured = {}

    def fake_get(url, headers=None, params=None, timeout=None):
        captured["url"] = url
        captured["headers"] = headers
        captured["params"] = params
        captured["timeout"] = timeout
        return DummyResponse({"ok": True, "from": "ETH", "to": "USDC"})

    monkeypatch.setenv("FLASH_API_KEY", "test-key")
    monkeypatch.setattr("src.data_fetcher.requests.get", fake_get)

    result = get_quote("ETH", "USDC", 1.0)

    assert result == {"ok": True, "from": "ETH", "to": "USDC"}
    assert captured["url"] == "https://api.flash.xyz/quote"
    assert captured["headers"] == {"Authorization": "Bearer test-key"}
    assert captured["params"] == {
        "from_token": "ETH",
        "to_token": "USDC",
        "amount": 1.0,
    }


def test_get_quote_requires_flash_api_key(monkeypatch):
    monkeypatch.delenv("FLASH_API_KEY", raising=False)

    with pytest.raises(ValueError, match="FLASH_API_KEY"):
        get_quote("ETH", "USDC", 1.0)


def test_generate_gemini_response_handles_invalid_api_key(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "not-a-real-key")
    monkeypatch.setenv("GEMINI_MODEL", "gemini-2.0-flash")

    class FakeModels:
        def generate_content(self, **kwargs):
            raise RuntimeError("simulated invalid key")

    class FakeClient:
        def __init__(self, api_key):
            self.api_key = api_key
            self.models = FakeModels()

    monkeypatch.setattr("src.test_gemini.genai.Client", FakeClient)

    with pytest.raises(ValueError, match="GEMINI_API_KEY.*invalid|expired"):
        generate_gemini_response("hello")
