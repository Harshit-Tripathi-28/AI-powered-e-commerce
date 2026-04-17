from config import db

carts_collection = db["carts"]


def get_cart(user_email):
    return carts_collection.find_one({"user_email": user_email})


def create_cart(user_email):
    return carts_collection.insert_one({
        "user_email": user_email,
        "items": []
    })


def update_cart(user_email, items):
    return carts_collection.update_one(
        {"user_email": user_email},
        {"$set": {"items": items}}
    )