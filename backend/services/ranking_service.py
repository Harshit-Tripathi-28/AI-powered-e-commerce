import pandas as pd

def rank_products(df):
    print("➡️ Ranking products based on trust score...")

    # Sort by trust score (descending)
    df = df.sort_values("trust_score", ascending=False)

    # Add rank column
    df["rank"] = range(1, len(df) + 1)

    return df


if __name__ == "__main__":

    print("🚀 Ranking engine started")

    trusted_products = pd.read_csv("data/trusted_products.csv")

    print("📦 Columns:", trusted_products.columns.tolist())

    ranked_products = rank_products(trusted_products)

    ranked_products.to_csv("data/ranked_products.csv", index=False)

    print("✅ Ranking completed")
    print("📁 Output saved to data/ranked_products.csv")
