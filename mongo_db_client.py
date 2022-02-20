from pymongo import MongoClient


def get_database(mongodb_url: str) -> MongoClient:
    client = MongoClient(mongodb_url)
    return client["notifications"]


def save_notification(
    client: MongoClient, collection_name: str, notification: dict
) -> None:
    collection = client[collection_name]
    collection.insert_one(notification)
