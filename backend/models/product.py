from config import products_collection


def get_all_products(limit=20):
    products = list(products_collection.find({}, {"_id": 0}).limit(limit))
    return products


def get_product_by_id(product_id):
    product = products_collection.find_one({"product_id": product_id}, {"_id": 0})
    return product


def search_products(query):
    products = list(
        products_collection.find(
            {
                "$or": [
                    {"title": {"$regex": query, "$options": "i"}},
                    {"brand": {"$regex": query, "$options": "i"}},
                    {"category": {"$regex": query, "$options": "i"}}
                ]
            },
            {"_id": 0}
        ).limit(20)
    )
    return products


def get_products_by_category(category):
    products = list(
        products_collection.find(
            {"category": {"$regex": category, "$options": "i"}},
            {"_id": 0}
        ).limit(20)
    )
    return products