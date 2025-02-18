"""Universal Agents chatbot implementation"""

import os
from pathlib import Path
from dotenv import load_dotenv
from services.anthropic_client import AnthropicClient
from services.openai_client import OpenAIClient
from services.perplexity_client import PerplexityClient
from config.system_prompts import UNIVERSAL_AGENTS_PROMPT

# Get the directory containing this file
BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables from .env file in the backend directory
load_dotenv(BASE_DIR / ".env")


class UniversalAgents:
    """Main chatbot class that manages different AI provider clients"""

    def __init__(self):
        self.system_prompt = UNIVERSAL_AGENTS_PROMPT
        self._initialize_clients()

    def _initialize_clients(self):
        """Initialize available AI clients based on API keys"""
        self.available_clients = {}

        if os.getenv("ANTHROPIC_API_KEY"):
            # Latest Claude models
            self.available_clients["claude-3-5-sonnet-20240620"] = AnthropicClient()
            self.available_clients["claude-3-opus-20240229"] = AnthropicClient()
            self.available_clients["claude-3-5-haiku-20241022"] = AnthropicClient()

        if os.getenv("OPENAI_API_KEY"):
            # Latest GPT and Reasoning Models
            self.available_clients["gpt-4o"] = OpenAIClient()  # Latest GPT-4o flagship
            self.available_clients["gpt-4o-mini"] = OpenAIClient()
            # Fast, affordable GPT-4o
            self.available_clients["o1"] = OpenAIClient()  # Complex reasoning
            self.available_clients["o1-mini"] = OpenAIClient()  # Fast reasoning
            self.available_clients["o3-mini"] = OpenAIClient()  # Latest fast reasoning

        if os.getenv("PERPLEXITY_API_KEY"):
            self.available_clients["sonar-reasoning-pro"] = PerplexityClient()
            self.available_clients["sonar-reasoning"] = PerplexityClient()
            self.available_clients["sonar-pro"] = PerplexityClient()
            self.available_clients["sonar"] = PerplexityClient()

    def get_response(self, user_input, model="claude-3-5-sonnet-20240620"):
        """Get response from selected AI provider"""
        try:
            if model not in self.available_clients:
                raise ValueError(
                    f"Model {model} not available. Available models: {list(self.available_clients.keys())}"
                )

            client = self.available_clients[model]

            print("\nDebug - Sending to AI provider:")
            print(f"System Prompt (first 100 chars): {self.system_prompt[:100]}...")
            print(f"User Input: {user_input}")

            response = client.generate_response(
                user_input, system_prompt=self.system_prompt
            )
            return response

        except Exception as e:
            return f"Error generating response: {str(e)}"
