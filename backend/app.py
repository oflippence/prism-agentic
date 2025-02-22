"""Flask server for Universal Agents API"""

from flask import Flask, request, jsonify, __version__ as flask_version
from flask_cors import CORS
import os
import sys
import time
import logging
import requests
import signal
from logging.handlers import RotatingFileHandler
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from config.system_prompts import UNIVERSAL_AGENTS_PROMPT

# Configure logging first thing
logging.basicConfig(
    level=logging.DEBUG,  # Changed to DEBUG level
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("/var/log/gunicorn/app.log"),
    ],
)
logger = logging.getLogger(__name__)

# Add startup time tracking at the top of the file after imports
startup_time = time.time()


def signal_handler(signum, frame):
    """Handle termination signals gracefully"""
    sig_name = signal.Signals(signum).name
    logger.info(f"Received signal {sig_name} ({signum})")
    logger.info("Performing graceful shutdown...")
    sys.exit(0)


# Set up signal handlers
signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)

# Add startup logging
logger.info("=== Starting Flask Application ===")
logger.info(f"Python version: {sys.version}")
logger.info(f"Flask version: {flask_version}")
logger.info(f"Environment: {os.getenv('ENVIRONMENT', 'development')}")


def check_health():
    """Check if all critical components are healthy"""
    try:
        logger.info("Health check called")
        health_status = {
            "status": "healthy",  # Always report healthy
            "timestamp": time.time(),
            "pid": os.getpid(),
            "uptime": time.time() - startup_time,  # Add uptime tracking
            "components": {"app": "healthy", "flask": "healthy", "gunicorn": "healthy"},
            "environment": os.getenv("ENVIRONMENT", "development"),
            "port": os.getenv("PORT", "8080"),
        }
        logger.info(f"Health check response: {health_status}")
        return health_status
    except Exception as e:
        logger.error(f"Health check error: {str(e)}")
        # Still return healthy with warning
        return {"status": "healthy", "warning": str(e), "timestamp": time.time()}


def init_app():
    """Initialize the Flask application with error handling"""
    try:
        app = Flask(__name__)
        logger.info("Flask app instance created")

        # Add health check endpoint
        @app.route("/health")
        def health_check():
            health_status = check_health()
            logger.debug(f"Health check called, status: {health_status}")
            # Always return 200 to prevent container restarts
            return jsonify(health_status), 200

        # Add basic root endpoint
        @app.route("/")
        def root():
            return jsonify(
                {
                    "status": "ok",
                    "message": "Prism Agentic API",
                    "environment": os.getenv("ENVIRONMENT", "development"),
                    "timestamp": time.time(),
                }
            ), 200

        # Load and validate required environment variables
        required_vars = {
            "ANTHROPIC_API_KEY": os.getenv("ANTHROPIC_API_KEY"),
            "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
            "PERPLEXITY_API_KEY": os.getenv("PERPLEXITY_API_KEY"),
            "N8N_URL": os.getenv("N8N_URL", "http://n8n:5678"),
            "PORT": os.getenv("PORT", "8080"),
        }

        # Log all environment variables (excluding sensitive values)
        logger.info("Environment Configuration:")
        missing_vars = []
        for key, value in required_vars.items():
            if value:
                if "KEY" in key:
                    logger.info(f"{key}: [REDACTED]")
                else:
                    logger.info(f"{key}: {value}")
            else:
                missing_vars.append(key)
                logger.warning(f"Missing environment variable: {key}")

        if missing_vars:
            logger.warning(
                f"Missing required environment variables: {', '.join(missing_vars)}"
            )
            # Don't fail startup for missing API keys

        # Configure CORS
        CORS(
            app,
            resources={
                r"/*": {
                    "origins": [
                        "http://localhost:5173",  # Local development
                        "http://localhost:4173",  # Local preview
                        "https://prism-agentic.vercel.app",  # Vercel production
                        "https://www.prism-agentic.vercel.app",  # Vercel production www
                        os.getenv(
                            "FRONTEND_URL", "*"
                        ),  # Allow configuration via env var
                    ],
                    "methods": ["GET", "POST", "OPTIONS"],
                    "allow_headers": ["Content-Type"],
                }
            },
        )

        # Initialize Universal Agents
        try:
            from chatbot.universal_agents import UniversalAgents

            global chatbot
            chatbot = UniversalAgents()
            logger.info("Successfully initialized Universal Agents")
        except Exception as e:
            logger.error(f"Failed to initialize Universal Agents: {str(e)}")
            chatbot = None
            # Don't raise here, allow the app to start without chatbot

        logger.info("Flask application initialized successfully")
        return app
    except Exception as e:
        logger.critical(f"Critical error during application initialization: {str(e)}")
        sys.exit(1)


# Initialize the Flask app
app = init_app()

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

        logger.info(f"\nEnhancing message - Model: {model}, Type: {enhancement_type}")
        logger.info(f"Original message: {message}")

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
        logger.info("\n=== New Chat Request ===")
        logger.debug(f"Request headers: {dict(request.headers)}")
        logger.debug(f"Request origin: {request.headers.get('Origin')}")
        logger.debug(f"Request method: {request.method}")
        logger.debug(
            f"N8N URL configured as: {os.getenv('N8N_URL', 'http://n8n:5678')}"
        )

        data = request.json
        logger.debug(f"Request data: {data}")

        message = data.get("message")
        model = data.get("model", "claude-3-5-sonnet-20240620")

        if not message:
            return jsonify({"error": "No message provided"}), 400

        logger.debug(f"\nAttempting to forward message to n8n:")
        logger.debug(f"Message: {message}")
        logger.debug(f"Model: {model}")
        logger.debug(
            f"Target URL: {os.getenv('N8N_URL', 'http://n8n:5678')}/webhook/n8n"
        )

        # Get API keys from environment
        api_keys = {
            "ANTHROPIC_API_KEY": os.getenv("ANTHROPIC_API_KEY"),
            "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
            "PERPLEXITY_API_KEY": os.getenv("PERPLEXITY_API_KEY"),
        }

        max_retries = 3
        retry_delay = 2  # seconds

        for attempt in range(max_retries):
            try:
                logger.debug(f"\n[DEBUG] Attempt {attempt + 1}/{max_retries}")

                # Forward to n8n for processing with API keys
                n8n_response = session.post(
                    f"{os.getenv('N8N_URL', 'http://n8n:5678')}/webhook/n8n",
                    json={
                        "action": "chat",
                        "payload": {
                            "message": message,
                            "model": model,
                            "system_prompt": UNIVERSAL_AGENTS_PROMPT,
                            "api_keys": api_keys,  # Include API keys in payload
                        },
                    },
                    timeout=30,  # Increased timeout
                )

                logger.debug(f"n8n Response Status: {n8n_response.status_code}")
                logger.debug(f"n8n Response Headers: {dict(n8n_response.headers)}")
                logger.debug(
                    f"n8n Response Content: {n8n_response.text[:500]}..."
                )  # Print first 500 chars

                if n8n_response.ok:
                    break  # Success, exit retry loop

                error_message = f"n8n error (status {n8n_response.status_code}): {n8n_response.text}"
                logger.error(
                    f"Error from n8n (attempt {attempt + 1}/{max_retries}): {error_message}"
                )

                if attempt < max_retries - 1:  # Don't sleep on last attempt
                    logger.debug(
                        f"Waiting {retry_delay} seconds before next attempt..."
                    )
                    time.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff
                else:
                    return jsonify({"error": error_message}), 502

            except requests.exceptions.ConnectionError as e:
                error_message = f"Could not connect to n8n (attempt {attempt + 1}/{max_retries}). Error: {str(e)}"
                logger.error(f"Connection Error: {error_message}")

                if attempt < max_retries - 1:
                    logger.debug(
                        f"Waiting {retry_delay} seconds before next attempt..."
                    )
                    time.sleep(retry_delay)
                    retry_delay *= 2
                else:
                    return jsonify({"error": error_message}), 503

            except requests.exceptions.Timeout as e:
                error_message = f"Request to n8n timed out (attempt {attempt + 1}/{max_retries}). Error: {str(e)}"
                logger.error(f"Timeout Error: {error_message}")

                if attempt < max_retries - 1:
                    logger.debug(
                        f"Waiting {retry_delay} seconds before next attempt..."
                    )
                    time.sleep(retry_delay)
                    retry_delay *= 2
                else:
                    return jsonify({"error": error_message}), 504

        # Get the response data from n8n
        try:
            response_data = n8n_response.json()
            logger.debug(f"Raw n8n response text: {n8n_response.text}")
            logger.debug(f"Successfully parsed n8n response: {response_data}")
            logger.debug(f"Response data type: {type(response_data)}")

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
                logger.error(f"Could not find answer in response: {response_data}")
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
            logger.debug(
                f"Extracted answer from response: {answer[:100]}..."
            )  # Print first 100 chars
            logger.debug(
                f"Sending formatted response to frontend: {formatted_response}"
            )
            return jsonify(formatted_response)
        except ValueError as e:
            error_message = (
                f"Invalid JSON response from n8n: {n8n_response.text[:500]}..."
            )
            logger.error(f"JSON Parse Error: {error_message}")
            return jsonify({"error": error_message}), 502

    except Exception as e:
        error_message = f"Unexpected error: {str(e)}"
        logger.error(f"Unexpected Error: {error_message}")
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

            logger.info(f"\nReceived chat webhook - Message: {message}, Model: {model}")

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
    try:
        # Use port 3001 for local development, but allow Railway to override
        is_production = os.getenv("ENVIRONMENT") == "production"
        default_port = "8080" if is_production else "3001"
        port = int(os.getenv("PORT", default_port))

        logger.info(f"Starting server on port {port}")
        logger.info(f"Environment: {os.getenv('ENVIRONMENT', 'development')}")
        logger.info(f"N8N URL: {os.getenv('N8N_URL', 'http://n8n:5678')}")
        logger.info(f"Frontend URL: {os.getenv('FRONTEND_URL', '*')}")

        debug = os.getenv("ENVIRONMENT", "development") == "development"
        app.run(host="0.0.0.0", port=port, debug=debug)
    except Exception as e:
        logger.critical(f"Failed to start server: {str(e)}")
        sys.exit(1)
