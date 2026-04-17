from config import users_collection


def create_user(user_data):
    return users_collection.insert_one(user_data)


def find_user_by_email(email):
    return users_collection.find_one({"email": email})


def get_user_by_email(email):
    user = users_collection.find_one({"email": email}, {"_id": 0, "password": 0})
    return user


def update_user(email, update_data):
    return users_collection.update_one(
        {"email": email},
        {"$set": update_data}
    )