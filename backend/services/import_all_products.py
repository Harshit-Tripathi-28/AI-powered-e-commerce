import sys
import os
import pandas as pd

# backend path add
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import db

products_collection = db["products"]

DATASET_FOLDER = "../datasets"


def import_all_products():

    total = 0

    for file in os.listdir(DATASET_FOLDER):

        if file.endswith(".csv"):

            path = os.path.join(DATASET_FOLDER, file)

            print("Importing:", file)

            df = pd.read_csv(path)

            products = df.to_dict(orient="records")

            products_collection.insert_many(products)

            total += len(products)

    print("Total products imported:", total)


if __name__ == "__main__":
    import_all_products()