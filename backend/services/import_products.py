import sys
import os

# backend folder ko python path me add kar rahe hain
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
from config import db

products_collection = db["products"]

def import_products():

    df = pd.read_csv("../datasets/amazon-products.csv")

    products = df.to_dict(orient="records")

    products_collection.insert_many(products)
    products["price"] = float(products["price"]) * 83

    print("Products imported:", len(products))


if __name__ == "__main__":
    import_products()