from flask import Blueprint, request, jsonify
from models.cart_model import get_cart, create_cart, update_cart

cart_bp = Blueprint("cart", __name__)


# -------------------------
# GET CART
# -------------------------
@cart_bp.route("/cart/<email>", methods=["GET"])
def view_cart(email):

    cart = get_cart(email)

    if not cart:
        create_cart(email)
        cart = get_cart(email)

    cart["_id"] = str(cart["_id"])

    return jsonify(cart)


# -------------------------
# ADD TO CART
# -------------------------
@cart_bp.route("/cart/add", methods=["POST"])
def add_to_cart():

    data = request.json

    email = data.get("email")
    product = data.get("product")

    cart = get_cart(email)

    if not cart:
        create_cart(email)
        cart = get_cart(email)

    items = cart["items"]

    items.append(product)

    update_cart(email, items)

    return jsonify({"message": "Product added to cart"})


# -------------------------
# REMOVE FROM CART
# -------------------------
@cart_bp.route("/cart/remove", methods=["POST"])
def remove_from_cart():

    data = request.json

    email = data.get("email")
    product_id = data.get("product_id")

    cart = get_cart(email)

    if not cart:
        return jsonify({"error": "Cart not found"}), 404

    items = [item for item in cart["items"] if item["product_id"] != product_id]

    update_cart(email, items)

    return jsonify({"message": "Product removed"})