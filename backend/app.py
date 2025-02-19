"""Flask server for Universal Agents API"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from chatbot.universal_agents import UniversalAgents
import os

app = Flask(__name__)
CORS(app)

# Initialize the chatbot
chatbot = UniversalAgents()

# Webhook secret for n8n authentication
WEBHOOK_SECRET = os.getenv("N8N_WEBHOOK_SECRET")

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


@app.route("/chat", methods=["POST"])
def chat():
    """Handle chat requests"""
    try:
        data = request.json
        message = data.get("message")
        model = data.get("model", "claude-3-sonnet")

        if not message:
            return jsonify({"error": "No message provided"}), 400

        print(f"\nReceived request - Message: {message}, Model: {model}")

        response = chatbot.get_response(message, model=model)
        return jsonify({"response": response})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


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
        workflow_id = data.get("workflow_id")
        action = data.get("action")
        payload = data.get("payload", {})

        print(f"\nReceived n8n webhook - Workflow: {workflow_id}, Action: {action}")

        # Handle different workflow actions
        if action == "generate_ai_response":
            response = chatbot.get_response(
                payload.get("message", ""),
                model=payload.get("model", "claude-3-5-sonnet-20240620"),
            )
            return jsonify({"response": response})
        elif action == "enhance_message":
            return enhance_message()

        return jsonify({"error": "Unknown action"}), 400

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000, debug=True)
