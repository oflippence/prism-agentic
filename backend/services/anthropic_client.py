import os
from anthropic import Anthropic


class AnthropicClient:
    def __init__(self):
        self.client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    def generate_response(self, prompt, model="claude-3-opus-20240229"):
        response = self.client.messages.create(
            max_tokens=1024, messages=[{"role": "user", "content": prompt}], model=model
        )
        return response.content
