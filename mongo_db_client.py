import json

from pymongo import MongoClient


def get_database(atlas_url: str) -> MongoClient:
    client = MongoClient(atlas_url)
    return client["notifications"]


def save_notice(client: MongoClient, dirname: str, filename: str):
    collection_name = client[dirname]

    with open(filename, "r") as file:
        notice = json.load(file)

    collection_name.insert_one(notice)
