import os
import requests
from dotenv import load_dotenv

load_dotenv()

FLASH_API_KEY = os.getenv("FLASH_API_KEY")
FLASH_BASE_URL = "https://api.flash.xyz"


def get_quote(from_token: str, to_token: str, amount: float) -> dict:
    """
    Fetch a quote from Flash API.

    Args:
        from_token: The token to swap from (e.g., "ETH")
        to_token: The token to swap to (e.g., "USDC")
        amount: The amount to swap

    Returns:
        The quote JSON response from Flash API
    """
    url = f"{FLASH_BASE_URL}/quote"
    headers = {"Authorization": f"Bearer {FLASH_API_KEY}"}
    params = {
        "from_token": from_token,
        "to_token": to_token,
        "amount": amount,
    }

    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    return response.json()


if __name__ == "__main__":
    quote = get_quote("ETH", "USDC", 1.0)
    print(quote)
