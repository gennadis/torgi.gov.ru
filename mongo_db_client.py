import locale
import os
from pprint import pprint

from dotenv import load_dotenv
from pymongo import MongoClient

MOSCOW_REGION_CODE = "77"
APARTAMENTS_CODE = "9"


def get_database(mongodb_url: str) -> MongoClient:
    client = MongoClient(mongodb_url)
    return client["notifications"]


def save_to_database(client: MongoClient, collection_name: str, document: dict) -> None:
    collection = client[collection_name]
    collection.insert_one(document)


def filter_notifications(db: MongoClient, region_code: str, category_code: str):
    region_notifications = db["NOTIFICATIONS"].find(
        {
            "structuredObject.notice.lots.biddingObjectInfo.subjectRF.code": region_code,
            "structuredObject.notice.lots.biddingObjectInfo.category.code": category_code,
        }
    )

    return region_notifications


def main():
    locale.setlocale(locale.LC_ALL, "ru_RU")

    load_dotenv()
    mongodb_url = os.getenv("MONGODB_URL")

    db = get_database(mongodb_url)
    apartaments = list(db["MOSCOW_APARTAMENTS"].find())
    for notification in apartaments:
        print(notification["structuredObject"]["notice"]["commonInfo"]["href"])
        lots = notification["structuredObject"]["notice"]["lots"]
        for lot in lots:
            price = locale.currency(float(lot["priceMin"]), grouping=True)
            print(price)
            print(lot["lotDescription"])
        print("-------------")


if __name__ == "__main__":
    main()
