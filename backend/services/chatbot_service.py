from config import db

products_collection = db["products"]

def chatbot_search(message):

    message = message.lower()
    words = message.split()

    price_limit = None

    for i in range(len(words)):
        if words[i] == "under":
            try:
                inr_price = int(words[i+1])
                price_limit = inr_price / 83
            except:
                pass

    query = {}

    if "shirt" in message:
        query["title"] = {"$regex": "shirt", "$options": "i"}

    if price_limit:
        query["price"] = {"$lte": price_limit}

    products = list(
        products_collection.find(query, {"_id": 0}).limit(5)
    )

    return products