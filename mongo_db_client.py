import json
import os

from dotenv import load_dotenv
from pymongo import MongoClient


def get_database(atlas_url: str) -> MongoClient:
    client = MongoClient(atlas_url)
    return client["notifications"]


def save_notice(client: MongoClient, filename: str):
    collection_name = client[filename]

    with open(filename, "r") as file:
        notice = json.load(file)

    collection_name.insert_one(notice)


if __name__ == "__main__":
    load_dotenv()
    atlas_url = os.getenv("ATLAS_DB_URL")

    mongo_client = get_database(atlas_url)
    save_notice(
        mongo_client,
        "notice_22000002660000000001_bd4eeb85-e005-4f94-bd59-d484b21dce68.json",
    )
