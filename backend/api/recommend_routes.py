from flask import Blueprint, request, jsonify
from services.recommendation_service import recommend_products

recommend_bp = Blueprint("recommend", __name__)

@recommend_bp.route("/recommend", methods=["GET"])
def recommend():

    query = request.args.get("q")

    if not query:
        return jsonify({"error": "query required"}), 400

    result = recommend_products(query)

    return jsonify(result)