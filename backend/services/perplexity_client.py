import os
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI


class PerplexityClient:
    def __init__(self):
        # Load environment variables with override
        env_path = Path(__file__).resolve().parent.parent / ".env"
        load_dotenv(env_path, override=True)

        api_key = os.getenv("PERPLEXITY_API_KEY")
        if not api_key:
            raise ValueError("PERPLEXITY_API_KEY not found in environment variables")

        # Debug: Print first and last 4 characters of API key
        print(
            f"Debug: API key starts with '{api_key[:4]}' and ends with '{api_key[-4:]}'"
        )

        # Initialize OpenAI client with Perplexity base URL
        self.client = OpenAI(api_key=api_key, base_url="https://api.perplexity.ai")

    def generate_response(self, prompt, system_prompt=None, model="sonar"):
        """Generate a response using the Perplexity API

        Args:
            prompt (str): The user's input message
            system_prompt (str, optional): The system prompt to use. If None, no system prompt is used.
            model (str): The model to use for generation. Available models:
                - sonar-reasoning-pro (127k context)
                - sonar-reasoning (127k context)
                - sonar-pro (200k context)
                - sonar (127k context)
        """
        try:
            print("\nDebug - PerplexityClient:")
            print(f"Received system_prompt: {'Yes' if system_prompt else 'No'}")
            if system_prompt:
                print(f"System prompt length: {len(system_prompt)} chars")

            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})

            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=1024,
                temperature=0.7,
            )
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"Error generating response: {str(e)}")
