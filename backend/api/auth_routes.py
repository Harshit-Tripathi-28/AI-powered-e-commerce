from flask import Blueprint, request, jsonify, current_app
from flask_bcrypt import Bcrypt
from models.user_model import create_user, find_user_by_email
import jwt
import datetime

auth_bp = Blueprint("auth", __name__)

bcrypt = Bcrypt()


# -------------------------
# REGISTER
# -------------------------
@auth_bp.route("/register", methods=["POST"])
def register():

    data = request.json

    name = data.get("name")
    email = data.get("email")
    password = data.get("password")

    if not name or not email or not password:
        return jsonify({"error": "All fields required"}), 400

    if find_user_by_email(email):
        return jsonify({"error": "User already exists"}), 400

    hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")

    user = {
        "name": name,
        "email": email,
        "password": hashed_password
    }

    create_user(user)

    return jsonify({"message": "User registered successfully"}), 201


# -------------------------
# LOGIN
# -------------------------
@auth_bp.route("/login", methods=["POST"])
def login():

    data = request.json

    email = data.get("email")
    password = data.get("password")

    user = find_user_by_email(email)

    if not user:
        return jsonify({"error": "User not found"}), 404

    if not bcrypt.check_password_hash(user["password"], password):
        return jsonify({"error": "Invalid password"}), 401

    # Generate JWT Token
    token = jwt.encode(
        {
            "email": user["email"],
            "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=24)
        },
        current_app.config["SECRET_KEY"],
        algorithm="HS256"
    )

    return jsonify({
        "message": "Login successful",
        "token": token
    }), 200