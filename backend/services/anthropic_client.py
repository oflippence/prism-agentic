import os
from pathlib import Path
from dotenv import load_dotenv
from anthropic import Anthropic


class AnthropicClient:
    def __init__(self):
        # Load environment variables with override
        env_path = Path(__file__).resolve().parent.parent / ".env"
        load_dotenv(env_path, override=True)

        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in environment variables")

        # Debug: Print first and last 4 characters of API key
        print(
            f"Debug: API key starts with '{api_key[:4]}' and ends with '{api_key[-4:]}'"
        )

        if not api_key.startswith("sk-ant"):
            raise ValueError(
                "Invalid API key format. Anthropic API keys should start with 'sk-ant'"
            )

        self.client = Anthropic(api_key=api_key)

    def generate_response(
        self, prompt, system_prompt=None, model="claude-3-5-sonnet-20240620"
    ):
        """Generate a response using the Anthropic API

        Args:
            prompt (str): The user's input message
            system_prompt (str, optional): The system prompt to use. If None, no system prompt is used.
            model (str): The model to use for generation. Available models:
                - claude-3-5-sonnet-20240620 (Most Intelligent)
                - claude-3-opus-20240229 (Complex Tasks)
                - claude-3-5-haiku-20241022 (Latest Fast Haiku)
        """
        try:
            print("\nDebug - AnthropicClient:")
            print(f"Received system_prompt: {'Yes' if system_prompt else 'No'}")
            if system_prompt:
                print(f"System prompt length: {len(system_prompt)} chars")

            # Create the API request with the correct system message format
            request_params = {
                "max_tokens": 1024,
                "messages": [{"role": "user", "content": prompt}],
                "model": model,
            }

            # Add system prompt if provided
            if system_prompt:
                request_params["system"] = system_prompt

            print(
                f"Sending request with system prompt: {'Yes' if system_prompt else 'No'}"
            )
            response = self.client.messages.create(**request_params)
            return response.content[0].text
        except Exception as e:
            raise Exception(f"Error generating response: {str(e)}")
