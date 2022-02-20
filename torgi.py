import datetime
import json
import os
import urllib3
from urllib.parse import unquote, urlsplit

import requests
from dotenv import load_dotenv
from tqdm import tqdm

from mongo_db_client import get_database, save_notification


OPENDATA_PASSPORT_URL = "https://torgi.gov.ru/new/opendata/7710568760-notice/data-{}T0000-{}T0000-structure-20220101.json"
NOTIFICATIONS_DIRPATH = "notifications/{}_{}/"
PASSPORT_FILEPATH = "notifications/{}_{}/passport.json"
DAYS_DELTA = 1
MONGODB_COLLECTION_NAME = "NOTIFICATIONS"


def get_dates(days_count: int) -> list:
    today = datetime.date.today()
    past_day = today - datetime.timedelta(days=days_count)
    dates = [date.strftime("%Y%m%d") for date in (past_day, today)]

    return dates


def fetch_opendata_passport(url: str, filepath: str, verify_ssl: bool = False) -> dict:
    response = requests.get(url, verify=verify_ssl)
    response.raise_for_status()

    passport = response.json()
    with open(filepath, "w") as file:
        json.dump(passport, file, indent=2)

    return passport


def get_notification(url: str) -> dict:
    response = requests.get(url, verify=False)
    response.raise_for_status()

    notification = response.json()["exportObject"]
    for attachment in notification.get("attachments"):
        del attachment["detachedSignature"]

    return notification


def fetch_all_notifications(passport: dict, dirpath: str) -> None:
    notification_urls = [
        notification["href"] for notification in passport["listObjects"]
    ]

    for url in tqdm(notification_urls):
        notification = get_notification(url)
        filename = get_filename(url)
        with open(os.path.join(dirpath, filename), "w") as file:
            json.dump(notification, fp=file, ensure_ascii=False, indent=2)


def get_filename(url: str) -> str:
    url_unqoted = unquote(url)
    _, _, path, _, _ = urlsplit(url_unqoted)
    _, filename = os.path.split(path)

    return filename


def main():
    load_dotenv()
    mongodb_url = os.getenv("MONGODB_URL")

    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    yesterday, today = get_dates(DAYS_DELTA)
    # yesterday, today = "20220218", "20220219"

    notifications_dirpath = NOTIFICATIONS_DIRPATH.format(yesterday, today)
    passport_filepath = PASSPORT_FILEPATH.format(yesterday, today)
    os.makedirs(notifications_dirpath, exist_ok=True)

    passport_url = OPENDATA_PASSPORT_URL.format(yesterday, today)
    passport = fetch_opendata_passport(url=passport_url, filepath=passport_filepath)
    fetch_all_notifications(passport=passport, dirpath=notifications_dirpath)

    mongodb_client = get_database(mongodb_url)

    for filename in tqdm(os.listdir(notifications_dirpath)):
        with open(os.path.join(notifications_dirpath, filename), "r") as file:
            notification = json.load(file)
            save_notification(mongodb_client, MONGODB_COLLECTION_NAME, notification)


if __name__ == "__main__":
    main()
