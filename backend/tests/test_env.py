"""Test environment configuration and API keys"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Get the backend directory path
BACKEND_DIR = Path(__file__).resolve().parent.parent


def test_environment():
    """Test environment variables and API keys"""
    # Load environment variables
    load_dotenv(BACKEND_DIR / ".env")

    # Debug: Print environment variables (masked for security)
    for key in ["ANTHROPIC_API_KEY", "OPENAI_API_KEY", "PERPLEXITY_API_KEY"]:
        value = os.getenv(key, "Not found")
        masked_value = (
            value[:8] + "..." + value[-4:]
            if value != "Not found" and len(value) > 12
            else value
        )
        print(f"{key}: {masked_value}")

    # Verify required API keys
    required_keys = ["ANTHROPIC_API_KEY"]  # Only check for Anthropic key for now
    missing_keys = [key for key in required_keys if not os.getenv(key)]

    if missing_keys:
        print(f"Error: Missing required API keys: {', '.join(missing_keys)}")
        print("Please ensure your .env file is properly configured.")
        return False

    return True


if __name__ == "__main__":
    print("Testing environment configuration...")
    print("Backend directory:", BACKEND_DIR)
    test_environment()
