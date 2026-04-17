from config import db
import math

products_collection = db["products"]


def calculate_score(product):
    # ── Factors ──
    price    = float(product.get("final_price") or product.get("price") or 0)
    rating   = float(product.get("rating") or 0)
    reviews  = int(product.get("reviews_count") or product.get("reviews") or 0)
    trust    = float(product.get("trust_score") or 0)  # 0–1
    verified = float(product.get("verified_purchase_ratio") or 0)  # 0–1

    # ── Normalized scores ──
    rating_score    = (rating / 5) * 30          # max 30
    review_score    = math.log(reviews + 1) * 3  # log scale
    trust_score     = trust * 25                 # max 25
    verified_score  = verified * 15              # max 15
    price_penalty   = (price / 5000) * 10        # max -10

    final = rating_score + review_score + trust_score + verified_score - price_penalty

    return round(final, 2)


def get_sentiment_label(score):
    if score >= 0.3:
        return "Mostly Positive"
    elif score >= -0.1:
        return "Mixed"
    else:
        return "Mostly Negative"


def compare_products(query):
    products = list(
        products_collection.find(
            {"title": {"$regex": query, "$options": "i"}},
            {"_id": 0}
        ).limit(20)
    )

    # Clean NaN + calculate score
    import math as _math
    for p in products:
        # NaN cleanup
        for k, v in p.items():
            if isinstance(v, float) and _math.isnan(v):
                p[k] = None

        # Multi-factor score
        p["score"] = calculate_score(p)

        # Sentiment label
        sentiment = float(p.get("avg_sentiment") or 0)
        p["sentiment_label"] = get_sentiment_label(sentiment)

        # Trust label
        trust = float(p.get("trust_score") or 0)
        score = round(trust * 100)
        p["trust_score_display"] = score
        p["trust_label"] = (
            "Highly Trusted" if score >= 71
            else "Moderate" if score >= 41
            else "Risky"
        )

        # Multiple images from Amazon URL pattern
        img = p.get("image_url") or ""
        if img:
            base = img.split("._")[0]
            p["images_list"] = [
                base + "._AC_UX500_.jpg",
                base + "._AC_SX522_.jpg",
                base + "._AC_UL1500_.jpg",
            ]

    # Sort by score
    products = sorted(products, key=lambda x: x["score"], reverse=True)

    # Mark best
    if products:
        products[0]["best_choice"] = True

    return products