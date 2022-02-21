import datetime
import json
import os
import urllib3
from urllib.parse import unquote, urlsplit

import requests
from dotenv import load_dotenv
from tqdm import tqdm

from mongo_db_client import get_database, save_to_database


OPENDATA_PASSPORT_URL = "https://torgi.gov.ru/new/opendata/7710568760-notice/data-{}T0000-{}T0000-structure-20220101.json"
NOTIFICATIONS_DIRPATH = "notifications/{}_{}/"
PASSPORT_FILEPATH = "notifications/passport.json"
DAYS_DELTA = 1
MONGODB_COLLECTION_NAME = "MOSCOW_APARTAMENTS"
PASSPORTS_COLLECTION_NAME = "PASSPORTS"
MOSCOW_REGION_CODE = "77"
APARTAMENTS_CODE = "9"
OFFICES_CODE = "11"


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


def check_for_apartament_in_moscow(notification: dict) -> bool:
    lots = notification["structuredObject"]["notice"]["lots"]
    for lot in lots:
        if (
            lot["biddingObjectInfo"]["subjectRF"]["code"] == MOSCOW_REGION_CODE
            and lot["biddingObjectInfo"]["category"]["code"] == APARTAMENTS_CODE
        ):
            return True


def fetch_filtered_notifications(passport: dict, dirpath: str) -> None:
    notification_urls = [
        notification["href"]
        for notification in passport["listObjects"]
        if notification["documentType"] == "notice"
    ]

    for url in tqdm(notification_urls):
        notification = get_notification(url)
        if check_for_apartament_in_moscow(notification):
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

    # yesterday, today = get_dates(DAYS_DELTA)
    yesterday, today = "20220217", "20220218"

    notifications_dirpath = NOTIFICATIONS_DIRPATH.format(yesterday, today)
    os.makedirs(notifications_dirpath, exist_ok=True)

    passport_url = OPENDATA_PASSPORT_URL.format(yesterday, today)
    passport = fetch_opendata_passport(url=passport_url, filepath=PASSPORT_FILEPATH)
    fetch_filtered_notifications(passport=passport, dirpath=notifications_dirpath)

    mongodb_client = get_database(mongodb_url)

    for filename in tqdm(os.listdir(notifications_dirpath)):
        filepath = os.path.join(notifications_dirpath, filename)
        with open(filepath, "r") as file:
            notification = json.load(file)
            save_to_database(
                client=mongodb_client,
                collection_name=MONGODB_COLLECTION_NAME,
                document=notification,
            )

    save_to_database(
        client=mongodb_client,
        collection_name=PASSPORTS_COLLECTION_NAME,
        document=passport,
    )
    os.remove(PASSPORT_FILEPATH)


if __name__ == "__main__":
    main()
