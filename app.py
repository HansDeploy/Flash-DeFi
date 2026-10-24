import json
import re
from html import escape
from typing import Any

import streamlit as st

from src.ai_advisor import ask_gemini_about_halal_yields

# --- CONFIGURATION ---
HALAL_PROTOCOLS = [
    {
        "protocol": "Nawa Finance",
        "network": "Polygon",
        "apy": "10.5%",
        "link": "https://nawa.finance",
    },
    {
        "protocol": "Goldsand",
        "network": "Ethereum",
        "apy": "8.2%",
        "link": "https://goldsand.fi/",
    },
    {
        "protocol": "MRHB Network (EmplifAI)",
        "network": "Multi-chain",
        "apy": "12.0%",
        "link": "https://emplifai.mrhb.network/",
    },
]

GENERIC_DISCLAIMER = (
    "This information is for general purposes only and is not religious "
    "or investment advice. DeFi carries smart-contract, liquidity, and market risks."
)


def _parse_ai_response(
    response_text: str, protocols: list[str]
) -> tuple[dict[str, str], str]:
    """Parse Gemini JSON, with a protocol-labeled text fallback."""
    cleaned_response = response_text.replace("```json", "").replace("```", "").strip()
    try:
        payload = json.loads(cleaned_response)
    except (json.JSONDecodeError, TypeError):
        payload = None

    analyses: dict[str, str] = {}
    disclaimer = GENERIC_DISCLAIMER
    has_disclaimer = False
    if isinstance(payload, dict):
        for key, value in payload.items():
            if not isinstance(key, str) or not isinstance(value, str):
                continue
            normalized_key = key.strip().casefold()
            if normalized_key == "disclaimer":
                disclaimer = value.strip() or GENERIC_DISCLAIMER
                has_disclaimer = True
            elif normalized_key in {protocol.casefold() for protocol in protocols}:
                analyses[normalized_key] = value.strip()

    if analyses or has_disclaimer:
        return analyses, disclaimer

    protocol_keys = {protocol.casefold() for protocol in protocols}
    current_key: str | None = None
    text_sections: dict[str, list[str]] = {}
    text_disclaimer: list[str] = []
    for line in cleaned_response.splitlines():
        stripped_line = line.strip().lstrip("-* ").strip()
        match = re.match(r"^([^:]+):\s*(.*)$", stripped_line)
        if match:
            label, content = match.groups()
            normalized_label = label.strip().casefold()
            if normalized_label in protocol_keys:
                current_key = normalized_label
                text_sections.setdefault(current_key, []).append(content)
                continue
            if normalized_label == "disclaimer":
                current_key = "disclaimer"
                text_disclaimer.append(content)
                continue
        if current_key == "disclaimer":
            text_disclaimer.append(stripped_line)
        elif current_key is not None:
            text_sections[current_key].append(stripped_line)

    analyses = {
        key: "\n".join(part for part in parts if part).strip()
        for key, parts in text_sections.items()
    }
    if text_disclaimer:
        disclaimer = "\n".join(text_disclaimer).strip() or GENERIC_DISCLAIMER
    if not analyses and cleaned_response:
        analyses = {protocol.casefold(): cleaned_response for protocol in protocols}
    return analyses, disclaimer


# --- STYLING (SOLANA THEME) ---
def _render_styles() -> None:
    st.markdown(
        """
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&display=swap');
            
            :root {
                --sol-purple: #9945FF;
                --sol-green: #14F195;
                --sol-cyan: #00C2FF;
                --bg-dark: #0a0a0a;
                --card-bg: #141414;
                --text-main: #ffffff;
                --text-muted: #a0a0a0;
            }
            
            html, body, [data-testid="stAppViewContainer"] {
                background-color: var(--bg-dark);
                color: var(--text-main);
                font-family: 'Inter', sans-serif;
            }
            
            /* Hide Sidebar completely */
            [data-testid="stSidebar"] { display: none; }
            [data-testid="stHeader"] { background: transparent; }
            
            .block-container {
                max-width: 1000px;
                padding-top: 4rem;
                padding-bottom: 4rem;
            }

            /* Hero Section */
            .hero-section {
                text-align: center;
                padding: 2rem 0 4rem 0;
            }
            .hero-title {
                font-size: 3.5rem;
                font-weight: 800;
                margin: 0;
                background: linear-gradient(90deg, var(--sol-purple), var(--sol-green), var(--sol-cyan));
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                letter-spacing: -0.05em;
            }
            .hero-subtitle {
                color: var(--text-muted);
                font-size: 1.2rem;
                margin-top: 1rem;
                font-weight: 300;
            }

            /* Protocol Cards */
            .protocol-card {
                background: linear-gradient(145deg, #181818, #111111);
                border: 1px solid #2a2a2a;
                border-radius: 16px;
                padding: 1.5rem;
                margin-bottom: 1rem;
                transition: all 0.3s ease;
            }
            .protocol-card:hover {
                border-color: var(--sol-purple);
                box-shadow: 0 0 20px rgba(153, 69, 255, 0.15);
                transform: translateY(-2px);
            }
            .protocol-name {
                font-size: 1.4rem;
                font-weight: 600;
                color: #fff;
                margin-bottom: 0.5rem;
                text-transform: capitalize;
            }
            .protocol-meta {
                display: flex;
                gap: 1.5rem;
                font-size: 0.9rem;
                color: var(--text-muted);
            }
            .apy-value {
                color: var(--sol-green);
                font-weight: 600;
                font-size: 1.1rem;
            }
            
            /* Styling Streamlit Expander to look like a modern card */
            [data-testid="stExpander"] {
                background-color: transparent;
                border: none;
                border-radius: 16px;
                margin-bottom: 1rem;
            }
            [data-testid="stExpander"] details {
                background: linear-gradient(145deg, #181818, #111111);
                border: 1px solid #2a2a2a;
                border-radius: 16px;
            }
            [data-testid="stExpander"] summary {
                padding: 1rem 1.5rem;
            }
            [data-testid="stExpander"] summary:hover {
                color: var(--sol-cyan);
            }
            
            .ai-response {
                background: rgba(20, 241, 149, 0.05);
                border-left: 3px solid var(--sol-green);
                padding: 1.5rem;
                border-radius: 0 12px 12px 0;
                color: #e0e0e0;
                font-size: 0.95rem;
                line-height: 1.6;
                margin-top: 1rem;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


def _render_hero() -> None:
    st.markdown(
        """
        <div class="hero-section">
            <h1 class="hero-title">Sharia Compliant DeFi</h1>
            <p class="hero-subtitle">Discover halal yields, powered by AI and live on-chain data.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


# --- MAIN APP ---
def main() -> None:
    st.set_page_config(
        page_title="Sharia Compliant DeFi by HansDeploy",
        layout="wide",
        initial_sidebar_state="collapsed",
    )

    _render_styles()
    _render_hero()

    analysis_placeholders: dict[str, Any] = {}
    for vault in HALAL_PROTOCOLS:
        protocol = vault["protocol"]
        network = vault["network"]
        apy = vault["apy"]

        # Modern Expander acting as a Card
        with st.expander(f"**{protocol}** — {apy} APY on {network}"):
            col1, col2 = st.columns([2, 1])
            with col1:
                st.markdown(f"### {protocol}")
                st.markdown(f"**Network:** {network}")
                st.markdown(
                    f'**APY:** <span style="color:#14F195; '
                    f'font-size:1.2rem; font-weight:bold;">{escape(apy)}</span>',
                    unsafe_allow_html=True,
                )
            with col2:
                analysis_placeholders[protocol.casefold()] = st.empty()

    ai_analyses = {
        vault["protocol"].casefold(): "AI analysis is currently unavailable."
        for vault in HALAL_PROTOCOLS
    }
    disclaimer = GENERIC_DISCLAIMER
    try:
        with st.spinner("AI analyzing Sharia compliance..."):
            advice_result = ask_gemini_about_halal_yields(HALAL_PROTOCOLS)
        if not isinstance(advice_result, str) or not advice_result:
            raise ValueError("Gemini returned an empty response.")
        ai_analyses, disclaimer = _parse_ai_response(
            advice_result, [vault["protocol"] for vault in HALAL_PROTOCOLS]
        )
        for vault in HALAL_PROTOCOLS:
            ai_analyses.setdefault(vault["protocol"].casefold(), advice_result)
    except Exception as e:  # noqa: BLE001
        print(e)

    for vault in HALAL_PROTOCOLS:
        protocol_key = vault["protocol"].casefold()
        analysis = ai_analyses.get(
            protocol_key, "AI analysis is currently unavailable."
        )
        analysis_html = escape(analysis).replace("\n", "<br>")
        with analysis_placeholders[protocol_key].container():
            st.markdown(
                f'<div class="ai-response">{analysis_html}</div>',
                unsafe_allow_html=True,
            )
            st.link_button("Visit Protocol ↗", vault["link"])

    st.caption(disclaimer)

    # Footer
    st.markdown(
        '<div style="text-align: center; margin-top: 4rem; color: #666; font-size: 0.8rem;">Published by HansDeploy. Not financial advice.</div>',
        unsafe_allow_html=True,
    )


main()
