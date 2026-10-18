import math
import os
import sys
from typing import Any

import requests
from dotenv import load_dotenv

if __package__:
    from .ai_advisor import ask_gemini_about_halal_yields, is_halal
else:
    from ai_advisor import ask_gemini_about_halal_yields, is_halal

load_dotenv()

LIFI_VAULTS_URL = "https://earn.li.fi/v1/vaults"


def _extract_vaults(payload: Any) -> list[dict[str, Any]]:
    """Extract vault records from supported API response shapes."""
    if isinstance(payload, list):
        return [item for item in payload if isinstance(item, dict)]
    if not isinstance(payload, dict):
        return []
    for key in ("vaults", "data", "items", "results"):
        nested = payload.get(key)
        vaults = _extract_vaults(nested)
        if vaults:
            return vaults
    return []


def _first_value(*values: Any) -> Any:
    """Return the first value that is neither null nor an empty string."""
    return next((value for value in values if value is not None and value != ""), None)


def _nested_value(value: Any, *keys: str) -> Any:
    """Get a nested dictionary value, returning None if a key is absent."""
    for key in keys:
        if not isinstance(value, dict):
            return None
        value = value.get(key)
    return value


def _format_apy(value: Any) -> str:
    """Format an APY value as a percentage, or N/A when it is invalid."""
    if value is None or isinstance(value, bool):
        return "N/A"
    includes_percent = isinstance(value, str) and value.strip().endswith("%")
    raw_value = value.strip().removesuffix("%").strip() if includes_percent else value
    try:
        apy = float(raw_value)
    except (TypeError, ValueError):
        return "N/A"
    if not math.isfinite(apy):
        return "N/A"
    if not includes_percent and abs(apy) <= 1:
        apy *= 100
    return f"{apy:.2f}%"


def get_yields(asset: str = "USDC", limit: int = 20) -> list[dict[str, Any]]:
    """Fetch yield vaults from LI.FI, returning an empty list on request errors."""
    lifi_api_key = os.getenv("LIFI_API_KEY")
    if not lifi_api_key or lifi_api_key.strip().lower() in {
        "your_lifi_api_key_here",
        "your_lifi_api_key",
    }:
        raise ValueError("LIFI_API_KEY is missing. Add it to your .env file.")

    try:
        response = requests.get(
            LIFI_VAULTS_URL,
            headers={"x-lifi-api-key": lifi_api_key},
            params={"asset": asset, "sortBy": "apy", "limit": limit},
            timeout=15,
        )
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as error:
        print(f"Unable to fetch yield data from LI.FI: {error}", file=sys.stderr)
        return []

    return _extract_vaults(data)


def _parse_vault(vault: dict[str, Any]) -> dict[str, Any]:
    """Normalize protocol, network, and APY fields from a vault record."""
    protocol = vault.get("protocol")
    protocol_name = (
        _first_value(
            vault.get("protocolName"),
            _nested_value(protocol, "name"),
            protocol if isinstance(protocol, str) else None,
            vault.get("name"),
        )
        or "Unknown"
    )

    chain_names = {
        1: "Ethereum",
        8453: "Base",
        42161: "Arbitrum",
    }
    chain_name = _first_value(
        vault.get("chainName"),
        _nested_value(vault.get("chain"), "name"),
    )
    chain_id = vault.get("chainId")
    if chain_name is None and chain_id is not None:
        try:
            chain = chain_names.get(int(chain_id), chain_id)
        except (TypeError, ValueError):
            chain = chain_id
    else:
        chain = chain_name or "Unknown"

    apy_raw = _first_value(
        _nested_value(vault.get("apy"), "total"),
        vault.get("apy"),
        _nested_value(vault, "analytics", "apy", "total"),
    )

    return {
        "protocol": protocol_name,
        "network": chain,
        "apy": _format_apy(apy_raw),
        "apy_raw": apy_raw,
    }


def run_yield_analysis() -> None:
    """Fetch yields, filter halal protocols, and print results and advice."""
    print("🔍 جاري جلب البيانات من LI.FI...")
    raw_vaults = get_yields()

    halal_vaults = []

    # 1. الفلترة
    for vault in raw_vaults:
        parsed = _parse_vault(vault)
        if is_halal(parsed["protocol"]):
            halal_vaults.append(parsed)

    print(
        f"✅ تم العثور على {len(halal_vaults)} بروتوكول حلال من أصل {len(raw_vaults)}.\n"
    )

    # 2. عرض النتائج وسؤال Gemini
    if halal_vaults:
        for v in halal_vaults:
            print(f"- {v['protocol']} | APY: {v['apy']} | Network: {v['network']}")

        print("\n🤖 جاري سؤال الذكاء الاصطناعي (Gemini) عن رأيه الشرعي...")
        advice = ask_gemini_about_halal_yields(halal_vaults)
        print("\n--- نصيحة المستشار ---")
        print(advice)
    else:
        print("❌ لم يتم العثور على بروتوكولات حلال في أعلى القائمة حالياً.")


if __name__ == "__main__":
    run_yield_analysis()
