import pandas as pd

DATASET_PATH = "../datasets/"

def load_csv(file_name, platform):
    df = pd.read_csv(DATASET_PATH + file_name)

    df.columns = df.columns.str.lower().str.replace(" ", "_")

    df["platform"] = platform

    # -------- NUMERIC CLEANING START --------
    numeric_cols = ["final_price", "initial_price", "reviews_count"]

    for col in numeric_cols:
        if col in df.columns:
            df[col] = (
                df[col]
                .astype(str)
                .str.replace("₹", "", regex=False)
                .str.replace(",", "", regex=False)
            )
            df[col] = pd.to_numeric(df[col], errors="coerce")
    # -------- NUMERIC CLEANING END --------

    return df



def load_all_products():
    amazon = load_csv("amazon-products.csv", "Amazon")
    walmart = load_csv("walmart-products.csv", "Walmart")
    shopee = load_csv("shopee-products.csv", "Shopee")
    lazada = load_csv("lazada-products.csv", "Lazada")
    shein = load_csv("shein-products.csv", "Shein")

    all_products = pd.concat(
        [amazon, walmart, shopee, lazada, shein],
        ignore_index=True
    )

    return all_products


def load_reviews():
    reviews = pd.read_csv(DATASET_PATH + "reviews.csv")
    reviews.columns = reviews.columns.str.lower().str.replace(" ", "_")
    return reviews


if __name__ == "__main__":
    products_df = load_all_products()
    reviews_df = load_reviews()

    print("Products:", products_df.shape)
    print("Reviews:", reviews_df.shape)
