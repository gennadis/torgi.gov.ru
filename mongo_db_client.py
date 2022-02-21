import locale

from pymongo import MongoClient


def get_database(mongodb_url: str) -> MongoClient:
    client = MongoClient(mongodb_url)
    return client["notifications"]


def push_notifications_to_db(
    client: MongoClient, collection_name: str, documents: list[dict]
) -> None:
    collection = client[collection_name]
    collection.insert_many(documents)


def push_passport_to_db(
    client: MongoClient, collection_name: str, document: dict
) -> None:
    collection = client[collection_name]
    collection.insert_one(document)


def get_notification_summary(apartment: dict):
    link = apartment["structuredObject"]["notice"]["commonInfo"]["href"]
    lots = apartment["structuredObject"]["notice"]["lots"]

    lots_summary = []
    for lot in lots:
        lot_price = locale.currency(float(lot["priceMin"]), grouping=True)
        lot_description = lot["lotDescription"]
        lots_summary.append((lot_price, lot_description))

    return {"link": link, "lots_summary": lots_summary}
