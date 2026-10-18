import os

from dotenv import load_dotenv
from google import genai

load_dotenv()


def generate_gemini_response(prompt: str) -> str:
    """Generate a response from Gemini using the project environment config."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not found in .env")

    model = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")

    try:
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(model=model, contents=prompt)
    except Exception as exc:
        message = str(exc).lower()
        if any(
            marker in message
            for marker in ["api key", "invalid", "expired", "401", "403"]
        ):
            raise ValueError(
                "GEMINI_API_KEY is invalid or expired. Update it in .env with a valid Gemini API key."
            ) from exc
        raise

    return response.text


if __name__ == "__main__":
    try:
        print("Gemini says:")
        print(generate_gemini_response("Say 'Hello Amhan' in Arabic."))
    except ValueError as exc:
        print(f"❌ {exc}")
        raise SystemExit(1)

