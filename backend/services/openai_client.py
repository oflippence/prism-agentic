import os
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI


class OpenAIClient:
    def __init__(self):
        # Load environment variables with override
        env_path = Path(__file__).resolve().parent.parent / ".env"
        load_dotenv(env_path, override=True)

        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")

        # Debug: Print first and last 4 characters of API key
        print(
            f"Debug: API key starts with '{api_key[:4]}' and ends with '{api_key[-4:]}'"
        )

        self.client = OpenAI(api_key=api_key)

    def generate_response(self, prompt, system_prompt=None, model="gpt-4o"):
        """Generate a response using the OpenAI API

        Args:
            prompt (str): The user's input message
            system_prompt (str, optional): The system prompt to use. If None, no system prompt is used.
            model (str): The model to use for generation. Available models:
                - gpt-4o (Latest flagship model, 128k context)
                - gpt-4o-mini (Fast, affordable model, 128k context)
                - o1 (Complex reasoning model, 200k context)
                - o1-mini (Fast reasoning model, 128k context)
                - o3-mini (Latest fast reasoning model, 200k context)
        """
        try:
            print("\nDebug - OpenAIClient:")
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
            )
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"Error generating response: {str(e)}")
