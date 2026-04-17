from flask import Flask, render_template
from api.compare_routes import compare_bp
from api.tryon_routes import tryon_bp
from services.load_data import load_all_products
from api.auth_routes import auth_bp
from flask_bcrypt import Bcrypt
from api.cart_routes import cart_bp
from api.product_routes import product_bp
from api.recommend_routes import recommend_bp
from api.chatbot_routes import chatbot_bp
bcrypt = Bcrypt()

def create_app():
    app = Flask(__name__)
    app.register_blueprint(auth_bp)
    bcrypt.init_app(app)
    app.config["SECRET_KEY"] = "h2p_super_secret_key"
    app.register_blueprint(cart_bp)
    app.register_blueprint(product_bp)
    app.register_blueprint(recommend_bp)
    app.register_blueprint(chatbot_bp)

    # Config
    app.config["UPLOAD_FOLDER"] = "static/uploads"
    app.config["OUTPUT_FOLDER"] = "static/outputs"

    # Load data once
    app.config["PRODUCT_DF"] = load_all_products()

    # Register blueprints
    app.register_blueprint(compare_bp)
    app.register_blueprint(tryon_bp)

    # Home route inside factory
    @app.route("/")
    def home():
        return render_template("welcome.html")

    @app.route("/home")
    def index():
        return render_template("index.html")
    @app.route("/search")
    def search_page():
        return render_template("search.html")

    @app.route("/product-page/")
    @app.route("/product-page/<product_id>")
    def product_detail(product_id="demo"):
        return render_template("product.html")
    @app.route("/compare")
    def compare_page():
        return render_template("compare.html")
    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)