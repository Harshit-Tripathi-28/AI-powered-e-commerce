from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017")

db = client["h2p_vision"]

# Collections
users_collection = db["users"]
products_collection = db["products"]
carts_collection = db["carts"]
reviews_collection = db["reviews"]
orders_collection = db["orders"]