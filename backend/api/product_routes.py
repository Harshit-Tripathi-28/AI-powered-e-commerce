from flask import Blueprint, request, jsonify
from services.search_service import search_products
from config import products_collection, reviews_collection
from services.trust_service import get_sentiment
import math

product_bp = Blueprint("products", __name__, url_prefix="/api")


# ── NaN Cleaner ──
def clean_nan(obj):
    if isinstance(obj, float) and math.isnan(obj):
        return None
    if isinstance(obj, dict):
        return {k: clean_nan(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [clean_nan(i) for i in obj]
    return obj


# ── Generate multiple image URLs from Amazon CDN pattern ──
def get_image_list(image_url):
    if not image_url or str(image_url).strip() == "" or str(image_url) == "None":
        return []
    try:
        # Extract base ID from Amazon URL
        # e.g. https://m.media-amazon.com/images/I/71QeGmahUnL._AC_UX500_.jpg
        base = image_url.split("._")[0]
        return [
            base + "._AC_UX500_.jpg",   # main image
            base + "._AC_SX522_.jpg",   # side view
            base + "._AC_UL1500_.jpg",  # large view
            base + "._AC_SY741_.jpg",   # tall view
        ]
    except:
        return [image_url]


# ── Find product by asin OR product_id ──
def find_product(product_id):
    # Try asin first (main key in dataset)
    product = products_collection.find_one(
        {"asin": product_id}, {"_id": 0}
    )
    if not product:
        # Try product_id field
        product = products_collection.find_one(
            {"product_id": product_id}, {"_id": 0}
        )
    return product


# ── Find reviews by asin ──
def find_reviews(product_id):
    reviews = list(
        reviews_collection.find(
            {"asin": product_id}, {"_id": 0}
        ).limit(20)
    )
    if not reviews:
        reviews = list(
            reviews_collection.find(
                {"product_id": product_id}, {"_id": 0}
            ).limit(20)
        )
    return reviews


# ─────────────────────────────────────
# SEARCH
# ─────────────────────────────────────
@product_bp.route("/search", methods=["GET"])
def search():
    query = request.args.get("q")
    if not query:
        return jsonify({"error": "query required"}), 400

    result = search_products(query)
    # Add image list to each product
    for p in result:
        p["images_list"] = get_image_list(p.get("image_url", ""))
    return jsonify(clean_nan(result))


# ─────────────────────────────────────
# ALL PRODUCTS (homepage)
# ─────────────────────────────────────
@product_bp.route("/products", methods=["GET"])
def get_products():
    limit = int(request.args.get("limit", 20))
    category = request.args.get("category", None)

    query = {}
    if category:
        query = {"category": {"$regex": category, "$options": "i"}}

    products = list(
        products_collection.find(query, {"_id": 0}).limit(limit)
    )

    # Add image list to each product
    for p in products:
        p["images_list"] = get_image_list(p.get("image_url", ""))

    return jsonify(clean_nan(products))


# ─────────────────────────────────────
# PRODUCT DETAIL + TRUST SCORE
# ─────────────────────────────────────
@product_bp.route("/products/<product_id>", methods=["GET"])
def get_product_detail(product_id):

    product = find_product(product_id)

    if not product:
        return jsonify({"error": "Product not found"}), 404

    # Multiple images
    product["images_list"] = get_image_list(product.get("image_url", ""))

    # Fetch reviews
    reviews = find_reviews(product_id)

    # Trust score
    trust_score = calculate_live_trust_score(reviews)
    product["trust_score"] = trust_score / 100  # keep 0-1 for consistency
    product["trust_score_display"] = trust_score  # 0-100 for display
    product["trust_label"] = get_trust_label(trust_score)

    # Clean reviews for frontend
    clean_reviews = []
    for r in reviews[:10]:
        clean_reviews.append({
            "body": r.get("body") or r.get("review_text") or "",
            "stars": float(r.get("stars") or r.get("rating") or 0),
            "verified_purchase": r.get("verified_purchase"),
            "date": r.get("date") or "",
            "title": r.get("title") or "",
        })

    product["reviews"] = clean_reviews
    product["review_count"] = len(reviews)

    return jsonify(clean_nan(product))


# ─────────────────────────────────────
# TRUST SCORE (standalone)
# ─────────────────────────────────────
@product_bp.route("/trust-score/<product_id>", methods=["GET"])
def get_trust_score(product_id):
    reviews = find_reviews(product_id)
    trust_score = calculate_live_trust_score(reviews)

    return jsonify(clean_nan({
        "product_id": product_id,
        "trust_score": trust_score,
        "review_count": len(reviews),
        "label": get_trust_label(trust_score)
    }))


# ─────────────────────────────────────
# TRUST SCORE LOGIC
# ─────────────────────────────────────
def calculate_live_trust_score(reviews):
    if not reviews:
        return 50

    total = len(reviews)
    sentiments = []
    ratings = []
    verified_count = 0
    fake_count = 0

    for r in reviews:
        text = r.get("body") or r.get("review_text") or ""
        rating = float(r.get("stars") or r.get("rating") or 0)
        verified = r.get("verified_purchase")

        sentiments.append(get_sentiment(text))
        ratings.append(rating)

        if verified and float(verified) == 1.0:
            verified_count += 1

        # Simple fake detection
        if is_fake_review(text, rating):
            fake_count += 1

    avg_sentiment = sum(sentiments) / total
    avg_rating = sum(ratings) / total if ratings else 0
    verified_ratio = verified_count / total
    genuine_ratio = (total - fake_count) / total

    # Normalize
    rating_norm   = avg_rating / 5
    sentiment_norm = (avg_sentiment + 1) / 2
    count_score   = min(math.log(total + 1) / math.log(1001), 1)

    # Weighted formula
    trust_score = (
        0.30 * rating_norm +
        0.25 * sentiment_norm +
        0.20 * verified_ratio +
        0.15 * genuine_ratio +
        0.10 * count_score
    ) * 100

    return round(trust_score, 1)


def is_fake_review(text, stars):
    if not text:
        return False
    text = str(text).lower()
    signals = [
        len(text) < 15,
        text.count("!") > 3,
        "buy now" in text,
        "click here" in text,
        "limited offer" in text,
        stars == 5 and len(text) < 20,
    ]
    return sum(signals) >= 2


def get_trust_label(score):
    if score >= 71:
        return "Highly Trusted"
    elif score >= 41:
        return "Moderate"
    else:
        return "Risky"