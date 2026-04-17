import pandas as pd
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans


# -------------------------
# Text cleaning
# -------------------------
def normalize(text):
    text = text.lower()
    text = re.sub(r"[^a-z0-9 ]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


# -------------------------
# Product matching
# -------------------------
def match_products(df):
    print("➡️ Cleaning titles...")

    df = df.copy()
    df["title"] = df["title"].astype(str).str.strip()
    df = df[df["title"].str.len() > 3]

    titles = df["title"].apply(normalize)

    print(f"✅ Valid products after cleaning: {len(df)}")

    # -------------------------
    # TF-IDF Vectorization
    # -------------------------
    print("➡️ Vectorizing titles (TF-IDF)...")

    vectorizer = TfidfVectorizer(
        stop_words="english",
        max_features=3000,
        min_df=2
    )

    X = vectorizer.fit_transform(titles)

    print(f"✅ TF-IDF matrix shape: {X.shape}")

    # -------------------------
    # Clustering (FAST & SAFE)
    # -------------------------
    print("➡️ Clustering products (KMeans)...")

    kmeans = KMeans(
        n_clusters=1500,
        random_state=42,
        n_init=10
    )

    labels = kmeans.fit_predict(X)
    df["product_group_id"] = labels

    print("✅ Clustering completed")

    return df


# -------------------------
# MAIN
# -------------------------
if __name__ == "__main__":
    print("🚀 Product matching script started")

    products = pd.read_csv("data/products.csv")

    print(f"📦 Products loaded: {products.shape}")

    matched_products = match_products(products)

    print(
        "🎯 Total unique product groups:",
        matched_products["product_group_id"].nunique()
    )

    matched_products.to_csv(
        "data/matched_products.csv",
        index=False
    )

    print("💾 matched_products.csv saved successfully")
    print("🏁 Script finished")
