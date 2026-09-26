# Project: Flash DeFi Intent Assistant

## Context
This project is a Python tool that helps users find Sharia-compliant yield opportunities in DeFi.
The Flash API is an intent-based execution layer. Users send intents (e.g., "swap 1 ETH for USDC")
and Flash handles gas, MEV, and retries.

## Tech Stack
- Python 3.13
- requests (HTTP calls to Flash API)
- python-dotenv (environment variable management)
- uv (package manager)

## Coding Standards
- Use type hints for all functions
- Use snake_case for variable and function names
- Prefer f-strings for formatting
- Never hardcode API keys; always use .env
- Always use `uv run python script.py` to run scripts

## Current Goal
Build a script that fetches quotes from Flash's /quote endpoint.
