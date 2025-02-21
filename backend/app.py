"""Flask server for Universal Agents API"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from chatbot.universal_agents import UniversalAgents
from config.system_prompts import UNIVERSAL_AGENTS_PROMPT
import os
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import time

app = Flask(__name__)
CORS(
    app,
    resources={
        r"/*": {
            "origins": [
                "http://localhost:5173",  # Local development
                "http://localhost:4173",  # Local preview
                "https://prism-agentic.vercel.app",  # Vercel production
                "https://www.prism-agentic.vercel.app",  # Vercel production www
                os.getenv("FRONTEND_URL", "*"),  # Allow configuration via env var
            ],
            "methods": ["GET", "POST", "OPTIONS"],
            "allow_headers": ["Content-Type"],
        }
    },
)

# Initialize the chatbot
chatbot = UniversalAgents()

# Webhook secret for n8n authentication
WEBHOOK_SECRET = os.getenv("N8N_WEBHOOK_SECRET")

# Configure retry strategy
retry_strategy = Retry(
    total=3,  # number of retries
    backoff_factor=1,  # wait 1, 2, 4 seconds between retries
    status_forcelist=[500, 502, 503, 504],  # retry on these status codes
)
http_adapter = HTTPAdapter(max_retries=retry_strategy)
session = requests.Session()
session.mount("http://", http_adapter)
session.mount("https://", http_adapter)

# Configure n8n URL based on environment
N8N_URL = os.getenv("N8N_URL", "http://n8n:5678")  # Default for local Docker

# Enhancement prompts
ENHANCEMENT_PROMPTS = {
    "all": """You are a professional content enhancer. Your task is to improve the given message while maintaining its core meaning.

Follow these enhancement steps:
1. Fix any grammatical or spelling errors
2. Improve clarity and readability
3. Add relevant context where beneficial
4. Format for better structure
5. Add citations or references if claims are made
6. Maintain a professional tone

Original message: {message}

Enhanced version (maintain concise yet comprehensive format):""",
    "grammar": "Fix any grammatical errors while maintaining the original meaning: {message}",
    "references": "Add relevant references and citations to support any claims in this message: {message}",
}


# @app.route("/chat", methods=["POST"])
# def chat():
#     """[DEPRECATED] Direct chat endpoint - Now handled by n8n workflow
#     This endpoint was previously used for direct chat requests but has been replaced
#     by n8n workflows to allow for more flexible agent configuration and processing.
#     See /webhook/n8n endpoint for the new implementation."""
#     try:
#         data = request.json
#         message = data.get("message")
#         model = data.get("model", "claude-3-sonnet")
#
#         if not message:
#             return jsonify({"error": "No message provided"}), 400
#
#         print(f"\nReceived request - Message: {message}, Model: {model}")
#
#         response = chatbot.get_response(message, model=model)
#         return jsonify({"response": response})
#
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500


@app.route("/enhance-message", methods=["POST"])
def enhance_message():
    """Handle message enhancement requests"""
    try:
        data = request.json
        message = data.get("message")
        model = data.get("model", "claude-3-5-sonnet-20240620")
        enhancement_type = data.get("enhancement_type", "all")

        if not message:
            return jsonify({"error": "No message provided"}), 400

        # Get the appropriate enhancement prompt
        prompt = ENHANCEMENT_PROMPTS.get(
            enhancement_type, ENHANCEMENT_PROMPTS["all"]
        ).format(message=message)

        print(f"\nEnhancing message - Model: {model}, Type: {enhancement_type}")
        print(f"Original message: {message}")

        # Use the chatbot to enhance the message with the specific prompt
        enhanced_message = chatbot.get_response(prompt, model=model)

        return jsonify(
            {
                "original_message": message,
                "enhanced_message": enhanced_message,
                "enhancement_type": enhancement_type,
            }
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/webhook/chat", methods=["POST"])
def chat_webhook():
    """Handle chat webhook from frontend"""
    try:
        # Add debug logging for incoming request
        print("\n[DEBUG] Incoming request details:")
        print(f"[DEBUG] Request headers: {dict(request.headers)}")
        print(f"[DEBUG] Request origin: {request.headers.get('Origin')}")
        print(f"[DEBUG] Request method: {request.method}")

        data = request.json
        print(f"[DEBUG] Request data: {data}")

        message = data.get("message")
        model = data.get("model", "claude-3-5-sonnet-20240620")

        if not message:
            return jsonify({"error": "No message provided"}), 400

        print(f"\n[DEBUG] Attempting to forward message to n8n:")
        print(f"[DEBUG] Message: {message}")
        print(f"[DEBUG] Model: {model}")
        print(f"[DEBUG] Target URL: {N8N_URL}/webhook/n8n")

        max_retries = 3
        retry_delay = 2  # seconds

        for attempt in range(max_retries):
            try:
                print(f"\n[DEBUG] Attempt {attempt + 1}/{max_retries}")

                # Forward to n8n for processing
                n8n_response = session.post(
                    f"{N8N_URL}/webhook/n8n",
                    json={
                        "action": "chat",
                        "payload": {
                            "message": message,
                            "model": model,
                            "system_prompt": UNIVERSAL_AGENTS_PROMPT,
                        },
                    },
                    timeout=30,  # Increased timeout
                )

                print(f"[DEBUG] n8n Response Status: {n8n_response.status_code}")
                print(f"[DEBUG] n8n Response Headers: {dict(n8n_response.headers)}")
                print(
                    f"[DEBUG] n8n Response Content: {n8n_response.text[:500]}..."
                )  # Print first 500 chars

                if n8n_response.ok:
                    break  # Success, exit retry loop

                error_message = f"n8n error (status {n8n_response.status_code}): {n8n_response.text}"
                print(
                    f"[DEBUG] Error from n8n (attempt {attempt + 1}/{max_retries}): {error_message}"
                )

                if attempt < max_retries - 1:  # Don't sleep on last attempt
                    print(
                        f"[DEBUG] Waiting {retry_delay} seconds before next attempt..."
                    )
                    time.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff
                else:
                    return jsonify({"error": error_message}), 502

            except requests.exceptions.ConnectionError as e:
                error_message = f"Could not connect to n8n (attempt {attempt + 1}/{max_retries}). Error: {str(e)}"
                print(f"[DEBUG] Connection Error: {error_message}")

                if attempt < max_retries - 1:
                    print(
                        f"[DEBUG] Waiting {retry_delay} seconds before next attempt..."
                    )
                    time.sleep(retry_delay)
                    retry_delay *= 2
                else:
                    return jsonify({"error": error_message}), 503

            except requests.exceptions.Timeout as e:
                error_message = f"Request to n8n timed out (attempt {attempt + 1}/{max_retries}). Error: {str(e)}"
                print(f"[DEBUG] Timeout Error: {error_message}")

                if attempt < max_retries - 1:
                    print(
                        f"[DEBUG] Waiting {retry_delay} seconds before next attempt..."
                    )
                    time.sleep(retry_delay)
                    retry_delay *= 2
                else:
                    return jsonify({"error": error_message}), 504

        # Get the response data from n8n
        try:
            response_data = n8n_response.json()
            print(f"[DEBUG] Raw n8n response text: {n8n_response.text}")
            print(f"[DEBUG] Successfully parsed n8n response: {response_data}")
            print(f"[DEBUG] Response data type: {type(response_data)}")

            # Handle different response formats
            answer = None
            if isinstance(response_data, dict):
                # First try standard response formats
                answer = (
                    response_data.get("answer")
                    or response_data.get("response")
                    or response_data.get("result")
                    or response_data.get("output")
                )

                # If no direct answer, try to extract from Slack message format
                if not answer and "message" in response_data:
                    message_text = response_data["message"].get("text", "")
                    # Try to extract the response part
                    if "Response:" in message_text:
                        # Split on "Response:" and take everything after it
                        parts = message_text.split("Response:", 1)
                        if len(parts) > 1:
                            answer = parts[1].strip()
                    else:
                        # If no "Response:" marker, just use the whole message
                        answer = message_text

                if not answer and "data" in response_data:
                    data = response_data["data"]
                    if isinstance(data, dict):
                        answer = (
                            data.get("answer")
                            or data.get("response")
                            or data.get("result")
                            or data.get("output")
                        )
            elif isinstance(response_data, str):
                # If response is just a string, use it as the answer
                answer = response_data

            if not answer:
                print(f"[DEBUG] Could not find answer in response: {response_data}")
                return jsonify(
                    {
                        "error": "No valid response found in n8n output",
                        "raw_response": response_data,
                    }
                ), 502

            formatted_response = {
                "question": message,  # Use original message as question
                "answer": answer,
            }
            print(
                f"[DEBUG] Extracted answer from response: {answer[:100]}..."
            )  # Print first 100 chars
            print(
                f"[DEBUG] Sending formatted response to frontend: {formatted_response}"
            )
            return jsonify(formatted_response)
        except ValueError as e:
            error_message = (
                f"Invalid JSON response from n8n: {n8n_response.text[:500]}..."
            )
            print(f"[DEBUG] JSON Parse Error: {error_message}")
            return jsonify({"error": error_message}), 502

    except Exception as e:
        error_message = f"Unexpected error: {str(e)}"
        print(f"[DEBUG] Unexpected Error: {error_message}")
        return jsonify({"error": error_message}), 500


@app.route("/webhook/n8n", methods=["POST"])
def n8n_webhook():
    """Handle n8n webhook triggers"""
    try:
        # Verify webhook secret if provided
        if WEBHOOK_SECRET:
            auth_header = request.headers.get("x-n8n-signature")
            if not auth_header or auth_header != WEBHOOK_SECRET:
                return jsonify({"error": "Invalid webhook signature"}), 401

        data = request.json
        action = data.get("action")
        payload = data.get("payload", {})

        # Handle different workflow actions
        if action == "chat":
            message = payload.get("message")
            model = payload.get("model", "claude-3-5-sonnet-20240620")

            if not message:
                return jsonify({"error": "No message provided"}), 400

            print(f"\nReceived chat webhook - Message: {message}, Model: {model}")

            # Forward to n8n for processing with system prompt
            return jsonify(
                {
                    "message": message,
                    "model": model,
                    "system_prompt": UNIVERSAL_AGENTS_PROMPT,
                }
            )

        return jsonify({"error": "Unknown action"}), 400

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    port = int(os.getenv("PORT", 3001))
    debug = os.getenv("ENVIRONMENT", "development") == "development"
    app.run(host="0.0.0.0", port=port, debug=debug)
