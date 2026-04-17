from flask import Blueprint, request, jsonify
from services.comparison_service import compare_products

compare_bp = Blueprint("compare", __name__, url_prefix="/api")

@compare_bp.route("/compare", methods=["GET"])
def compare():

    query = request.args.get("q")

    if not query:
        return jsonify({"error": "Query required"}), 400

    result = compare_products(query)

    return jsonify(result)