import datetime
import os
import urllib3
from time import sleep

import requests
from dotenv import load_dotenv
from pymongo import MongoClient

from mongo_db_client import (
    get_database,
    push_notifications_to_db,
    push_passport_to_db,
)


OPENDATA_PASSPORT_URL = "https://torgi.gov.ru/new/opendata/7710568760-notice/data-{}T0000-{}T0000-structure-20220101.json"
DAYS_DELTA = 1
VERIFY_SSL = False

MOSCOW_APARTMENTS_COLLECTION = "moscow_apartments"
MOSCOW_OFFICES_COLLECTION = "moscow_offices"
PASSPORTS_COLLECTION = "passports"

MOSCOW_REGION_CODE = "77"
APARTAMENTS_CODE = "9"
OFFICES_CODE = "11"

PARSER_SLEEP_INTERVAL = 86400


def get_dates(days_count: int) -> list:
    today = datetime.date.today()
    past_day = today - datetime.timedelta(days=days_count)
    dates = [date.strftime("%Y%m%d") for date in (past_day, today)]

    return dates


def fetch_opendata_passport(url: str) -> dict:
    response = requests.get(url, verify=VERIFY_SSL)
    response.raise_for_status()

    passport = response.json()

    return passport


def get_notification(url: str) -> dict:
    response = requests.get(url, verify=VERIFY_SSL)
    response.raise_for_status()

    notification = response.json()["exportObject"]
    for attachment in notification.get("attachments"):
        del attachment["detachedSignature"]

    return notification


def check_for_category(notification: dict, category_code: str) -> bool:
    lots = notification["structuredObject"]["notice"]["lots"]
    for lot in lots:
        if (
            lot["biddingObjectInfo"]["subjectRF"]["code"] == MOSCOW_REGION_CODE
            and lot["biddingObjectInfo"]["category"]["code"] == category_code
        ):
            return True


def get_filtered_notifications(passport: dict) -> dict[str : list[dict]]:
    notification_urls = [
        notification["href"]
        for notification in passport["listObjects"]
        if notification["documentType"] == "notice"
    ]

    notifications = {
        MOSCOW_APARTMENTS_COLLECTION: [],
        MOSCOW_OFFICES_COLLECTION: [],
    }

    for url in notification_urls:
        notification = get_notification(url)
        if check_for_category(notification, category_code=APARTAMENTS_CODE):
            notifications[MOSCOW_APARTMENTS_COLLECTION].append(notification)
        if check_for_category(notification, category_code=OFFICES_CODE):
            notifications[MOSCOW_OFFICES_COLLECTION].append(notification)

    return notifications


def run_parser(mongodb_client: MongoClient, sleep_interval: int):
    yesterday, today = get_dates(DAYS_DELTA)

    passport_url = OPENDATA_PASSPORT_URL.format(yesterday, today)
    passport = fetch_opendata_passport(url=passport_url)
    filtered_notifications = get_filtered_notifications(passport=passport)

    try:
        push_passport_to_db(
            client=mongodb_client,
            collection_name=PASSPORTS_COLLECTION,
            document=passport,
        )
    except TypeError:
        print(f"Empty passport")

    for collection, notifications in filtered_notifications.items():
        try:
            push_notifications_to_db(
                client=mongodb_client,
                collection_name=collection,
                documents=notifications,
            )
        except TypeError:
            print(f"No {collection} objects were found.")

    sleep(sleep_interval)


def main():
    load_dotenv()
    mongodb_url = os.getenv("MONGODB_URL")
    mongodb_client = get_database(mongodb_url)

    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    while True:
        run_parser(mongodb_client, PARSER_SLEEP_INTERVAL)


if __name__ == "__main__":
    main()
