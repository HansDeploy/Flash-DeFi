# Flash-DeFi
Intent-based DeFi assistant for Sharia-compliant yield discovery.

## Setup

This project uses environment variables for both the Flash API and the Gemini API.

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```
2. Add your real keys to `.env`:
   ```env
   FLASH_API_KEY=your_flash_api_key_here
   GEMINI_API_KEY=your_gemini_api_key_here
   GEMINI_MODEL=gemini-3.8-flash
   ```

## Install dependencies

```bash
uv sync --extra dev
```

## Run the scripts

### Flash quote fetcher

```bash
uv run python src/data_fetcher.py
```

### Gemini smoke test

```bash
uv run python src/test_gemini.py
```

## Notes

- The app expects the environment file to live in the project root as `.env`.
- `src/data_fetcher.py` validates that `FLASH_API_KEY` is present before making a request.
- The Gemini script uses the current `google-genai` package and a supported model name.
