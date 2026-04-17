from flask import Blueprint, request, jsonify
from services.chatbot_service import chatbot_search

chatbot_bp = Blueprint("chatbot", __name__)

@chatbot_bp.route("/chat", methods=["GET", "POST"])
def chat():

    if request.method == "POST":
        data = request.json
        message = data.get("message")

    else:
        message = request.args.get("message")

    if not message:
        return jsonify({"error": "message required"}), 400

    result = chatbot_search(message)

    return jsonify(result)