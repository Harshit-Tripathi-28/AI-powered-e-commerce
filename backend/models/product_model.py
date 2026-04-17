from config import db

products_collection = db["products"]


# GET ALL PRODUCTS
def get_all_products():
    products = list(products_collection.find({}, {"_id": 0}))
    return products


# SEARCH PRODUCTS
def search_products(query):
    products = list(
        products_collection.find(
            {"name": {"$regex": query, "$options": "i"}},
            {"_id": 0}
        )
    )
    return products