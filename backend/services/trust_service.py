import pandas as pd
from textblob import TextBlob
import math


def get_sentiment(text):
    if not text or str(text).strip() == "":
        return 0
    try:
        analysis = TextBlob(str(text))
        return analysis.sentiment.polarity
    except:
        return 0


def is_fake_review(text, stars):
    """Simple fake review detection heuristics"""
    if not text:
        return False
    text = str(text).lower()
    fake_signals = [
        len(text) < 15,                          # too short
        text.count("!") > 3,                     # too many exclamations
        "buy now" in text,
        "click here" in text,
        "limited offer" in text,
        "best product ever" == text.strip(),
        stars == 5 and len(text) < 20,           # 5 star but no explanation
    ]
    return sum(fake_signals) >= 2


def calculate_trust_score(products_df, reviews_df):
    print("➡️ Cleaning review data...")

    reviews_df["body"] = reviews_df["body"].fillna("").astype(str)
    reviews_df["stars"] = pd.to_numeric(reviews_df["stars"], errors="coerce").fillna(0)
    reviews_df["verified_purchase"] = pd.to_numeric(
        reviews_df["verified_purchase"], errors="coerce"
    ).fillna(0)

    print("➡️ Calculating sentiment + fake detection...")

    reviews_df["sentiment"]   = reviews_df["body"].apply(get_sentiment)
    reviews_df["is_fake"]     = reviews_df.apply(
        lambda r: is_fake_review(r["body"], r["stars"]), axis=1
    )
    reviews_df["is_genuine"]  = ~reviews_df["is_fake"]

    print("➡️ Aggregating per product...")

    review_agg = reviews_df.groupby("asin").agg(
        avg_sentiment         = ("sentiment",         "mean"),
        avg_rating            = ("stars",             "mean"),
        review_count          = ("sentiment",         "count"),
        verified_count        = ("verified_purchase", "sum"),
        genuine_count         = ("is_genuine",        "sum"),
        fake_count            = ("is_fake",           "sum"),
    ).reset_index()

    # Verified purchase ratio
    review_agg["verified_purchase_ratio"] = (
        review_agg["verified_count"] / (review_agg["review_count"] + 1)
    )

    # Genuine review ratio
    review_agg["genuine_ratio"] = (
        review_agg["genuine_count"] / (review_agg["review_count"] + 1)
    )

    print("➡️ Merging with products...")

    merged = products_df.merge(review_agg, on="asin", how="left")

    # Fill missing
    for col in ["avg_sentiment","avg_rating","review_count",
                "verified_purchase_ratio","genuine_ratio"]:
        merged[col] = merged[col].fillna(0)

    print("➡️ Computing Trust Score...")

    # Normalize
    merged["rating_norm"]   = merged["avg_rating"] / 5
    merged["sentiment_norm"] = (merged["avg_sentiment"] + 1) / 2

    # Trust Score Formula — 4 factors
    merged["trust_score"] = (
        0.35 * merged["rating_norm"]            # Rating quality
      + 0.30 * merged["sentiment_norm"]         # Review sentiment
      + 0.20 * merged["verified_purchase_ratio"] # Verified buyers
      + 0.15 * merged["genuine_ratio"]          # Fake detection
    )

    # Cap at 1.0
    merged["trust_score"] = merged["trust_score"].clip(0, 1)

    return merged


if __name__ == "__main__":
    print("🚀 Trust score engine started")

    matched_products = pd.read_csv("data/matched_products.csv")
    reviews          = pd.read_csv("data/reviews.csv")

    print(f"📦 Products: {matched_products.shape}")
    print(f"🧾 Reviews:  {reviews.shape}")

    trusted = calculate_trust_score(matched_products, reviews)
    trusted.to_csv("data/trusted_products.csv", index=False)

    print("✅ Done! Saved to data/trusted_products.csv")