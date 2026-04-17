from flask import Blueprint, request, jsonify, current_app
from services.tryon_services.glasses import apply_glasses
from services.tryon_services.clothes import apply_clothes
import os

tryon_bp = Blueprint("tryon", __name__)

@tryon_bp.route("/tryon")
def tryon_page():
    from flask import render_template
    return render_template("tryon.html")


@tryon_bp.route("/tryon/glasses", methods=["POST"])
def tryon_glasses():

    user_file = request.files["user_image"]
    glasses_file = request.files["glasses_image"]

    upload_folder = current_app.config["UPLOAD_FOLDER"]
    output_folder = current_app.config["OUTPUT_FOLDER"]

    os.makedirs(upload_folder, exist_ok=True)
    os.makedirs(output_folder, exist_ok=True)

    user_path = os.path.join(upload_folder, user_file.filename)
    glasses_path = os.path.join(upload_folder, glasses_file.filename)
    output_path = os.path.join(output_folder, "output.png")

    user_file.save(user_path)
    glasses_file.save(glasses_path)

    success = apply_glasses(user_path, glasses_path, output_path)

    if not success:
        return jsonify({"error": "Face not detected"}), 400

    return jsonify({
        "output_image": request.host_url + "static/outputs/output.png"
    })


@tryon_bp.route("/tryon/clothes", methods=["POST"])
def tryon_clothes():

    user_file = request.files["user_image"]
    cloth_file = request.files["cloth_image"]

    upload_folder = current_app.config["UPLOAD_FOLDER"]
    output_folder = current_app.config["OUTPUT_FOLDER"]

    os.makedirs(upload_folder, exist_ok=True)
    os.makedirs(output_folder, exist_ok=True)

    user_path = os.path.join(upload_folder, user_file.filename)
    cloth_path = os.path.join(upload_folder, cloth_file.filename)
    output_path = os.path.join(output_folder, "cloth_output.png")

    user_file.save(user_path)
    cloth_file.save(cloth_path)

    success = apply_clothes(user_path, cloth_path, output_path)

    if not success:
        return jsonify({"error": "Body not detected"}), 400

    return jsonify({
        "output_image": request.host_url + "static/outputs/cloth_output.png"
    })