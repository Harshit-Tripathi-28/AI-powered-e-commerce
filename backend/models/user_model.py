from config import users_collection


def create_user(user_data):
    return users_collection.insert_one(user_data)


def find_user_by_email(email):
    return users_collection.find_one({"email": email})