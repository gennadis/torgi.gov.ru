import locale
import os
from pprint import pprint

from dotenv import load_dotenv
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
        lots_summary.append((lot_description, lot_price))

    return {"link": link, "lots_summary": lots_summary}


def main():
    locale.setlocale(locale.LC_ALL, "ru_RU")

    load_dotenv()
    mongodb_url = os.getenv("MONGODB_URL")
    mongodb_client = get_database(mongodb_url)

    apartments = mongodb_client["moscow_apartments"].find()
    for apartment in apartments:
        pprint(get_notification_summary(apartment))

    print("--------------------------------")

    offices = mongodb_client["moscow_offices"].find()
    for office in offices:
        pprint(get_notification_summary(office))


if __name__ == "__main__":
    main()
