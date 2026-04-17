from config import db

products_collection = db["products"]


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