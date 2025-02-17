"""Flask server for Universal Agents API"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from chatbot.universal_agents import UniversalAgents

app = Flask(__name__)
CORS(app)

# Initialize the chatbot
chatbot = UniversalAgents()


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


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000, debug=True)
