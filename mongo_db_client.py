import os
from pprint import pprint

from dotenv import load_dotenv
from pymongo import MongoClient


def get_database(mongodb_url: str) -> MongoClient:
    client = MongoClient(mongodb_url)
    return client["notifications"]


def save_notification(
    client: MongoClient, collection_name: str, notification: dict
) -> None:
    collection = client[collection_name]
    collection.insert_one(notification)


def filter_by_region(db: MongoClient, region_code: str):
    region_notifications = db["NOTIFICATIONS"].find(
        {"structuredObject.notice.lots.biddingObjectInfo.subjectRF.code": region_code}
    )
    apartments = db["NOTIFICATIONS"].find(
        {"structuredObject.notice.lots.biddingObjectInfo.category.code": "9"}
    )

    return region_notifications


def main():
    load_dotenv()
    mongodb_url = os.getenv("MONGODB_URL")

    db = get_database(mongodb_url)

    moscow_notifications = filter_by_region(db, "77")
    for notification in list(moscow_notifications):
        lots = notification["structuredObject"]["notice"]["lots"]
        for lot in lots:
            pprint(lot["lotDescription"])
        print("-------------")


if __name__ == "__main__":
    main()
