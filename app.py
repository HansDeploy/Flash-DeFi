import math
from typing import Any

import requests
import streamlit as st
from google.genai.errors import APIError

from src.ai_advisor import ask_gemini_about_halal_yields, is_halal
from src.yield_fetcher import _parse_vault, get_yields

TEXT: dict[str, dict[str, str]] = {
    "en": {
        "title": "Halal DeFi Yield Assistant",
        "subtitle": (
            "Explore DeFi yield opportunities with an initial Sharia screening "
            "and clear risk-aware guidance."
        ),
        "eyebrow": "THE NEXT GENERATION OF RESPONSIBLE DEFI",
        "hero_badge": "AI-ASSISTED • MULTI-CHAIN • RISK-AWARE",
        "hero_caption": "Discover on-chain opportunities with clarity and confidence.",
        "hero_tagline": "Yield discovery, with purpose.",
        "results_kicker": "DISCOVERED OPPORTUNITIES",
        "sidebar_title": "Preferences",
        "brand": "NŪR / YIELD INTELLIGENCE",
        "language": "Language",
        "english": "English",
        "arabic": "العربية",
        "vault_limit": "Vaults to review",
        "search": "🔍 Find halal opportunities",
        "fetching": "Fetching opportunities from LI.FI…",
        "search_error": (
            "We couldn’t retrieve yield data. Please check your connection or "
            "API settings, then try again."
        ),
        "empty_results": (
            "LI.FI returned no yield data. Please try again in a moment."
        ),
        "key_error": (
            "The LI.FI API key is missing or invalid. Add a valid "
            "`LIFI_API_KEY` to your `.env` file, then try again."
        ),
        "found": "Found {count} opportunities that passed the initial screening.",
        "none": "No opportunities passed the initial screening this time.",
        "total_metric": "Screened opportunities",
        "highest_metric": "Highest listed APY",
        "no_apy": "No APY data",
        "opportunities": "Yield opportunities",
        "protocol": "Protocol",
        "apy": "APY",
        "network": "Network",
        "advisor": "🤖 AI advisor",
        "advisor_expander": (
            "🤖 View the AI advisor’s guidance  |  عرض إرشادات المستشار الذكي"
        ),
        "advisor_intro": (
            "An AI-generated overview based on the opportunities shown above. "
            "Use it as a starting point for your own research."
        ),
        "advisor_loading": "Preparing the advisor’s guidance…",
        "advisor_error": "The opportunities loaded, but AI guidance is unavailable.",
        "advisor_empty": "The AI advisor returned no guidance.",
        "malformed_records": (
            "Skipped {count} records with an unsupported or incomplete format."
        ),
        "risk_note": (
            "Initial screening is not a religious ruling or investment advice. "
            "Yields can change, and DeFi carries smart-contract, liquidity, "
            "and market risks."
        ),
        "error_details": "Technical details",
        "footer": "Built for thoughtful exploration of on-chain yield.",
        "direction": "ltr",
    },
    "ar": {
        "title": "مساعد العوائد الحلال في DeFi",
        "subtitle": (
            "اكتشف فرص العائد في التمويل اللامركزي مع فحص شرعي أولي "
            "وإرشادات تراعي المخاطر."
        ),
        "eyebrow": "الجيل الجديد من التمويل اللامركزي المسؤول",
        "hero_badge": "مدعوم بالذكاء الاصطناعي • متعدد الشبكات • يراعي المخاطر",
        "hero_caption": "اكتشف فرص البلوكتشين بوضوح وثقة.",
        "hero_tagline": "اكتشاف العوائد بهدف ووعي.",
        "results_kicker": "الفرص المكتشفة",
        "sidebar_title": "التفضيلات",
        "brand": "نور / ذكاء العوائد",
        "language": "اللغة",
        "english": "English",
        "arabic": "العربية",
        "vault_limit": "عدد الفرص المطلوب فحصها",
        "search": "🔍 ابحث عن فرص حلال",
        "fetching": "جارٍ جلب الفرص من LI.FI…",
        "search_error": (
            "تعذّر جلب بيانات العوائد. تحقّق من الاتصال أو إعدادات واجهة "
            "البرمجة، ثم حاول مجدداً."
        ),
        "empty_results": "لم تُرجع LI.FI بيانات للعوائد. يرجى المحاولة بعد قليل.",
        "key_error": (
            "مفتاح LI.FI مفقود أو غير صالح. أضف مفتاحاً صالحاً باسم "
            "`LIFI_API_KEY` إلى ملف `.env`، ثم حاول مجدداً."
        ),
        "found": "اجتازت {count} فرصة الفحص الشرعي الأولي.",
        "none": "لم تجتز أي فرصة الفحص الأولي هذه المرة.",
        "total_metric": "الفرص التي اجتازت الفحص",
        "highest_metric": "أعلى عائد سنوي معلن",
        "no_apy": "لا تتوفر بيانات العائد",
        "opportunities": "فرص العائد",
        "protocol": "البروتوكول",
        "apy": "العائد السنوي (APY)",
        "network": "الشبكة",
        "advisor": "🤖 المستشار الذكي",
        "advisor_expander": (
            "🤖 عرض إرشادات المستشار الذكي  |  View the AI advisor’s guidance"
        ),
        "advisor_intro": (
            "ملخص مولّد بالذكاء الاصطناعي للفرص المعروضة أعلاه. "
            "استخدمه كنقطة بداية لبحثك الخاص."
        ),
        "advisor_loading": "جارٍ إعداد إرشادات المستشار…",
        "advisor_error": "تم تحميل الفرص، لكن تعذّر الحصول على إرشادات الذكاء الاصطناعي.",
        "advisor_empty": "لم يُرجع المستشار الذكي أي إرشادات.",
        "malformed_records": "تم تجاهل {count} سجلّات بسبب تنسيق غير مدعوم أو بيانات ناقصة.",
        "risk_note": (
            "هذا الفحص أولي ولا يُعدّ فتوى شرعية أو نصيحة استثمارية. قد تتغير "
            "العوائد، وينطوي التمويل اللامركزي على مخاطر العقود الذكية "
            "والسيولة والسوق."
        ),
        "error_details": "التفاصيل التقنية",
        "footer": "صُمّم لاستكشاف عوائد البلوكتشين بوعي.",
        "direction": "rtl",
    },
}


def _apy_percent(value: Any) -> float | None:
    """Convert an API APY value into percentage points for display."""
    if value is None or isinstance(value, bool):
        return None

    includes_percent = isinstance(value, str) and value.strip().endswith("%")
    raw_value = value.strip().removesuffix("%").strip() if includes_percent else value
    try:
        apy = float(raw_value)
    except (TypeError, ValueError):
        return None

    if not math.isfinite(apy):
        return None
    if not includes_percent and abs(apy) <= 1:
        apy *= 100
    return apy


def _render_styles(direction: str) -> None:
    """Apply a futuristic, responsive visual theme for the selected language."""
    st.markdown(
        f"""
        <style>
            :root {{
                color-scheme: dark;
                --ink: #f3f6ff;
                --muted: #98a4c1;
                --mint: #6cf0c2;
                --violet: #a68bff;
                --panel: rgba(15, 22, 43, 0.78);
            }}
            html, body, [data-testid="stAppViewContainer"] {{
                background: #070b17;
                color: var(--ink);
            }}
            [data-testid="stAppViewContainer"] {{
                direction: {direction};
                background-image:
                    radial-gradient(ellipse at 14% 6%, rgba(65, 111, 255, 0.2), transparent 32%),
                    radial-gradient(ellipse at 87% 18%, rgba(88, 239, 196, 0.12), transparent 27%),
                    linear-gradient(rgba(112, 135, 190, 0.035) 1px, transparent 1px),
                    linear-gradient(90deg, rgba(112, 135, 190, 0.035) 1px, transparent 1px);
                background-size: auto, auto, 48px 48px, 48px 48px;
                background-position: center, center, center top, center top;
            }}
            [data-testid="stHeader"] {{
                background: rgba(7, 11, 23, 0.76);
            }}
            [data-testid="stMain"] {{
                background: transparent;
            }}
            .block-container {{
                max-width: 1180px;
                padding-top: 2rem;
                padding-bottom: 3.5rem;
            }}
            [data-testid="stSidebar"] {{
                direction: {direction};
                background: linear-gradient(180deg, rgba(12, 18, 37, 0.98), rgba(9, 14, 29, 0.98));
                border-inline-end: 1px solid rgba(139, 159, 214, 0.14);
            }}
            [data-testid="stSidebar"] > div:first-child {{
                background: transparent;
            }}
            [data-testid="stMarkdownContainer"] p,
            [data-testid="stMarkdownContainer"] li,
            [data-testid="stCaptionContainer"] {{
                color: #bdc7dc;
            }}
            div[data-testid="stMetric"] {{
                min-height: 132px;
                background: linear-gradient(145deg, rgba(19, 29, 55, 0.95), rgba(13, 20, 40, 0.92));
                border: 1px solid rgba(129, 158, 226, 0.21);
                border-radius: 18px;
                padding: 1.1rem 1.25rem;
                box-shadow: 0 14px 38px rgba(0, 0, 0, 0.18);
            }}
            [data-testid="stMetricLabel"] {{
                color: #aebbd6;
            }}
            [data-testid="stMetricValue"] {{
                color: var(--mint);
                font-weight: 750;
                letter-spacing: -0.04em;
            }}
            [data-testid="stDataFrame"] {{
                border: 1px solid rgba(139, 159, 214, 0.2);
                border-radius: 16px;
                overflow: hidden;
                background: rgba(13, 20, 40, 0.72);
            }}
            [data-testid="stExpander"] {{
                background: rgba(14, 21, 42, 0.82);
                border: 1px solid rgba(139, 159, 214, 0.2);
                border-radius: 16px;
            }}
            [data-testid="stExpander"] summary {{
                color: #eaf0ff;
                font-weight: 650;
            }}
            .hero {{
                position: relative;
                overflow: hidden;
                margin: 1rem 0 1.6rem;
                padding: clamp(1.7rem, 5vw, 3.4rem);
                border: 1px solid rgba(146, 167, 228, 0.24);
                border-radius: 28px;
                background:
                    radial-gradient(ellipse at 88% 10%, rgba(108, 240, 194, 0.17), transparent 30%),
                    radial-gradient(ellipse at 8% 100%, rgba(126, 101, 255, 0.22), transparent 38%),
                    linear-gradient(135deg, rgba(20, 31, 61, 0.96), rgba(11, 17, 35, 0.97));
                box-shadow: 0 30px 90px rgba(0, 0, 0, 0.34), inset 0 1px rgba(255, 255, 255, 0.06);
            }}
            .hero::after {{
                position: absolute;
                content: "◈";
                inset-inline-end: 5%;
                top: 50%;
                transform: translateY(-50%);
                color: rgba(108, 240, 194, 0.09);
                font-size: clamp(8rem, 22vw, 19rem);
                line-height: 1;
                pointer-events: none;
                text-shadow: 0 0 80px rgba(108, 240, 194, 0.12);
            }}
            .hero-content {{
                position: relative;
                z-index: 1;
                max-width: 780px;
            }}
            .hero-eyebrow {{
                margin: 0 0 0.85rem;
                color: var(--mint);
                font-size: 0.73rem;
                font-weight: 750;
                letter-spacing: 0.19em;
                text-transform: uppercase;
            }}
            .hero h1 {{
                margin: 0;
                color: #f5f7ff;
                font-size: clamp(2.2rem, 5.2vw, 4.4rem);
                font-weight: 780;
                letter-spacing: -0.065em;
                line-height: 1.05;
            }}
            .hero h1 span {{
                background: linear-gradient(95deg, #70f2c7 5%, #9ca6ff 62%, #d5a3ff 100%);
                background-clip: text;
                -webkit-text-fill-color: transparent;
            }}
            .hero-copy {{
                max-width: 610px;
                margin: 1rem 0 1.2rem;
                color: #b4c0da;
                font-size: 1.05rem;
                line-height: 1.75;
            }}
            .hero-badge {{
                display: inline-flex;
                align-items: center;
                gap: 0.45rem;
                padding: 0.48rem 0.8rem;
                border: 1px solid rgba(108, 240, 194, 0.28);
                border-radius: 999px;
                background: rgba(108, 240, 194, 0.075);
                color: #bdfbe5;
                font-size: 0.72rem;
                font-weight: 650;
                letter-spacing: 0.08em;
            }}
            .section-kicker {{
                margin: 1.7rem 0 0.3rem;
                color: #7e8eaf;
                font-size: 0.72rem;
                font-weight: 700;
                letter-spacing: 0.15em;
                text-transform: uppercase;
            }}
            .risk-note {{
                border-inline-start: 3px solid #e4b765;
                background: rgba(66, 51, 27, 0.3);
                border-radius: 10px;
                padding: 0.85rem 1rem;
                color: #e3d5b5;
                font-size: 0.92rem;
            }}
            .app-footer {{
                margin-top: 2.5rem;
                padding-top: 1rem;
                border-top: 1px solid rgba(139, 159, 214, 0.14);
                color: #73809c;
                font-size: 0.8rem;
                text-align: center;
            }}
            div.stButton > button[kind="primary"] {{
                min-height: 3.2rem;
                border: 1px solid rgba(141, 255, 218, 0.42);
                border-radius: 14px;
                background: linear-gradient(105deg, #12a982, #4972ec);
                color: #fff;
                font-weight: 750;
                box-shadow: 0 10px 30px rgba(41, 155, 178, 0.25);
                transition: transform 160ms ease, box-shadow 160ms ease;
            }}
            div.stButton > button[kind="primary"]:hover {{
                transform: translateY(-2px);
                box-shadow: 0 15px 36px rgba(41, 155, 178, 0.37);
            }}
            @media (max-width: 700px) {{
                .hero {{ border-radius: 20px; }}
                .hero::after {{ inset-inline-end: -9%; opacity: 0.55; }}
                .hero-badge {{ font-size: 0.62rem; letter-spacing: 0.04em; }}
            }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def _render_hero(language: dict[str, str]) -> None:
    """Render the bilingual crypto-themed landing banner."""
    st.markdown(
        f"""
        <section class="hero">
            <div class="hero-content">
                <div class="hero-eyebrow">{language["eyebrow"]}</div>
                <h1>🕌 {language["title"]}<br><span>{language["hero_tagline"]}</span></h1>
                <p class="hero-copy">{language["subtitle"]}<br>
                {language["hero_caption"]}</p>
                <div class="hero-badge">✦ &nbsp;{language["hero_badge"]}</div>
            </div>
        </section>
        """,
        unsafe_allow_html=True,
    )


def _render_results(
    language: dict[str, str],
    vaults: list[dict[str, Any]],
    source_count: int,
    skipped_count: int,
    advisor_text: str | None,
    advisor_error: str | None,
) -> None:
    """Render screened vaults, summary metrics, advisor output, and disclosures."""
    if vaults:
        st.success(language["found"].format(count=len(vaults)))
    else:
        st.warning(language["none"])
    if skipped_count:
        st.warning(language["malformed_records"].format(count=skipped_count))

    apy_values = [
        apy
        for vault in vaults
        if (apy := _apy_percent(vault.get("apy_raw"))) is not None
    ]
    highest_apy = max(apy_values) if apy_values else None
    first_metric, second_metric = st.columns(2)
    first_metric.metric(language["total_metric"], f"{len(vaults)} / {source_count}")
    second_metric.metric(
        language["highest_metric"],
        f"{highest_apy:.2f}%" if highest_apy is not None else language["no_apy"],
    )

    if not vaults:
        st.markdown(
            f'<div class="risk-note">{language["risk_note"]}</div>',
            unsafe_allow_html=True,
        )
        return

    st.markdown(
        f'<div class="section-kicker">{language["results_kicker"]}</div>',
        unsafe_allow_html=True,
    )
    st.subheader(language["opportunities"])
    rows = [
        {
            "protocol": vault["protocol"],
            "apy": _apy_percent(vault.get("apy_raw")),
            "network": vault["network"],
        }
        for vault in vaults
    ]
    st.dataframe(
        rows,
        use_container_width=True,
        hide_index=True,
        column_config={
            "protocol": st.column_config.TextColumn(language["protocol"]),
            "apy": st.column_config.ProgressColumn(
                language["apy"],
                format="%.2f%%",
                min_value=min(0.0, min(apy_values, default=0.0)),
                max_value=max(1.0, max(apy_values, default=0.0)),
                help=language["highest_metric"],
            ),
            "network": st.column_config.TextColumn(language["network"]),
        },
    )

    st.subheader(language["advisor"])
    with st.expander(language["advisor_expander"], expanded=False):
        st.caption(language["advisor_intro"])
        if advisor_error:
            st.warning(language["advisor_error"])
            with st.expander(language["error_details"]):
                st.caption(advisor_error)
        elif advisor_text:
            st.info(advisor_text)

    st.markdown(
        f'<div class="risk-note">{language["risk_note"]}</div>', unsafe_allow_html=True
    )


def main() -> None:
    """Run the bilingual Streamlit yield-discovery application."""
    st.set_page_config(
        page_title="Halal DeFi Yield | العوائد الحلال",
        page_icon="🕌",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    initial_language = st.session_state.get("ui_language", "en")
    language = TEXT[initial_language]
    with st.sidebar:
        st.markdown(f"### 🕌 {language['brand']}")
        st.subheader(language["sidebar_title"])
        selected_language = st.radio(
            language["language"],
            options=("en", "ar"),
            format_func=lambda code: (
                language["english"] if code == "en" else language["arabic"]
            ),
            key="ui_language",
            horizontal=True,
        )
        language = TEXT[selected_language]
        limit = st.slider(
            language["vault_limit"],
            min_value=5,
            max_value=50,
            value=20,
            step=5,
        )

    _render_styles(language["direction"])
    _render_hero(language)

    if st.button(language["search"], type="primary", use_container_width=True):
        st.session_state["yield_vaults"] = None
        st.session_state["yield_source_count"] = 0
        st.session_state["yield_fetch_error"] = None
        st.session_state["yield_advisor_text"] = None
        st.session_state["yield_advisor_error"] = None

        try:
            with st.spinner(language["fetching"]):
                raw_vaults = get_yields(limit=limit)
        except (requests.RequestException, ValueError) as error:
            st.session_state["yield_fetch_error"] = (
                "missing_key" if isinstance(error, ValueError) else str(error)
            )
        else:
            if not raw_vaults:
                st.session_state["yield_fetch_error"] = "empty"
            else:
                halal_vaults: list[dict[str, Any]] = []
                skipped_count = 0
                for vault in raw_vaults:
                    if not isinstance(vault, dict):
                        skipped_count += 1
                        continue
                    try:
                        parsed = _parse_vault(vault)
                    except (AttributeError, OverflowError, TypeError, ValueError):
                        skipped_count += 1
                        continue
                    protocol = parsed.get("protocol")
                    if isinstance(protocol, str) and is_halal(protocol):
                        halal_vaults.append(parsed)
                    elif not isinstance(protocol, str):
                        skipped_count += 1

                st.session_state["yield_vaults"] = halal_vaults
                st.session_state["yield_source_count"] = len(raw_vaults)
                st.session_state["yield_skipped_count"] = skipped_count

                if halal_vaults:
                    try:
                        with st.spinner(language["advisor_loading"]):
                            advisor_text = ask_gemini_about_halal_yields(halal_vaults)
                        if advisor_text:
                            st.session_state["yield_advisor_text"] = advisor_text
                        else:
                            st.session_state["yield_advisor_error"] = language[
                                "advisor_empty"
                            ]
                    except (APIError, ValueError) as error:
                        st.session_state["yield_advisor_error"] = str(error)

    fetch_error = st.session_state.get("yield_fetch_error")
    if fetch_error:
        if fetch_error == "missing_key":
            st.error(language["key_error"])
        elif fetch_error == "empty":
            st.error(language["empty_results"])
        else:
            st.error(language["search_error"])
            with st.expander(language["error_details"]):
                st.caption(fetch_error)
    elif st.session_state.get("yield_vaults") is not None:
        vaults = st.session_state["yield_vaults"]
        _render_results(
            language,
            vaults,
            st.session_state.get("yield_source_count", len(vaults)),
            st.session_state.get("yield_skipped_count", 0),
            st.session_state.get("yield_advisor_text"),
            st.session_state.get("yield_advisor_error"),
        )

    st.markdown(
        f'<div class="app-footer">{language["footer"]}</div>',
        unsafe_allow_html=True,
    )


main()
