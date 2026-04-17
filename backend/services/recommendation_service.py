from config import db

products_collection = db["products"]

def recommend_products(query):

    # similar products search
    products = list(
        products_collection.find(
            {"title": {"$regex": query, "$options": "i"}},
            {"_id": 0}
        ).limit(10)
    )

    recommendations = []

    if products:
        base_product = products[0]

        category = base_product.get("category", "")
        brand = base_product.get("brand", "")

        recommendations = list(
            products_collection.find(
                {
                    "$or": [
                        {"category": category},
                        {"brand": brand}
                    ]
                },
                {"_id": 0}
            ).limit(10)
        )

    return recommendations