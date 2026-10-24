import json
import logging
import os
from typing import Any

from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY"),
    http_options=types.HttpOptions(timeout=15_000),
)

HALAL_WHITELIST = [
    "zaynfi",
    "nawa",
    "qist",
    "quintes",
    "haqq",
    "ipor",
    "upshift",
    "auto-finance",
]


def is_halal(protocol_name: str | None) -> bool:
    """Check whether a protocol name exactly matches the halal whitelist."""
    if not protocol_name:
        return False
    return protocol_name.casefold() in HALAL_WHITELIST


def ask_gemini_about_halal_yields(
    halal_vaults: list[dict[str, Any]],
) -> str | dict[str, str] | None:
    """Send the filtered yield opportunities to Gemini for an explanation."""
    if not halal_vaults:
        return "No Sharia-compliant protocols were found at this time."

    # Prepare the opportunity list for Gemini.
    vaults_text = "\n".join(
        [
            f"- {v['protocol']} on {v['network']} with {v['apy']} APY"
            for v in halal_vaults
        ]
    )

    expected_format = {
        vault["protocol"]: "Short 2-sentence analysis."
        for vault in halal_vaults
    }
    expected_format["disclaimer"] = "Standard disclaimer."
    prompt = f"""
    You are an Islamic finance expert specializing in decentralized finance (DeFi).
    Review these protocols, which passed an initial Sharia screening:

    {vaults_text}

    Return only a valid JSON dictionary with exactly these keys and string values:
    {json.dumps(expected_format, ensure_ascii=False)}
    Keep each protocol analysis to exactly 2 concise sentences. Do not write
    essays or add nested objects. Mention relevant smart-contract, liquidity,
    or market risks briefly. Do not claim this is a definitive religious ruling.
    Reply in English only.
    """

    try:
        response = client.models.generate_content(
            model="gemini-3.8-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                max_output_tokens=300,
                thinking_config=types.ThinkingConfig(thinking_budget=0),
            ),
        )
    except Exception:
        logging.exception("Gemini Sharia analysis request failed.")
        return {
            **{
                vault["protocol"]: "AI analysis is currently unavailable."
                for vault in halal_vaults
            },
            "disclaimer": (
                "This information is general and is not religious or investment "
                "advice. DeFi carries smart-contract, liquidity, and market risks."
            ),
        }

    if response.text is None:
        return None
    return response.text.replace("```json", "").replace("```", "").strip()
