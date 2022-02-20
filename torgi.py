import datetime
import urllib3
import json
import os
from urllib.parse import unquote, urlsplit

import requests
from dotenv import load_dotenv
from tqdm import tqdm

from mongo_db_client import save_notice, get_database


OPENDATA_PASSPORT_URL = "https://torgi.gov.ru/new/opendata/7710568760-notice/data-{}T0000-{}T0000-structure-20220101.json"
PASSPORT_FILENAME = "passport.json"
NOTIFICATIONS_DIRNAME = "notifications"


def get_opendata_passport_url(days_count: int) -> str:
    today = datetime.date.today()
    past_day = today - datetime.timedelta(days=days_count)
    dates = [date.strftime("%Y%m%d") for date in (past_day, today)]

    passport_url = OPENDATA_PASSPORT_URL.format(*dates)

    return passport_url


def fetch_opendata_passport(url: str, verify_ssl: bool, filename: str) -> str:
    response = requests.get(url, verify=verify_ssl)
    response.raise_for_status()

    with open(filename, "w") as file:
        json.dump(response.json(), file, indent=2)

    return filename


def fetch_notification(url: str):
    response = requests.get(url, verify=False)
    response.raise_for_status()

    filename = get_filename(url)
    notification = response.json()
    clean_notification(notification)

    with open(os.path.join(NOTIFICATIONS_DIRNAME, filename), "w") as file:
        json.dump(notification, file, ensure_ascii=False, indent=2)


def fetch_all_notifications(source_filename: str):
    with open(source_filename, "r") as file:
        notifications = json.load(file)

    hrefs = [
        notification["href"]
        for notification in notifications["listObjects"]
        if notification["documentType"] == "notice"
    ]

    for href in tqdm(hrefs):
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        fetch_notification(url=href)


def clean_notification(notification: dict):
    for attachment in notification["exportObject"]["attachments"]:
        del attachment["detachedSignature"]


def get_filename(url: str) -> str:
    url_unqoted = unquote(url)
    _, _, path, _, _ = urlsplit(url_unqoted)
    _, filename = os.path.split(path)

    return filename


def main():
    load_dotenv()
    atlas_url = os.getenv("ATLAS_DB_URL")

    mongo_client = get_database(atlas_url)

    os.makedirs("notifications", exist_ok=True)
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    passport_url = get_opendata_passport_url(days_count=1)
    # passport_url = "https://torgi.gov.ru/new/opendata/7710568760-notice/data-20220218T0000-20220219T0000-structure-20220101.json"
    passport_json = fetch_opendata_passport(
        url=passport_url, verify_ssl=False, filename=PASSPORT_FILENAME
    )

    fetch_all_notifications(passport_json)

    for file in tqdm(os.listdir(NOTIFICATIONS_DIRNAME)):
        save_notice(
            mongo_client,
            NOTIFICATIONS_DIRNAME,
            os.path.join(NOTIFICATIONS_DIRNAME, file),
        )


if __name__ == "__main__":
    main()
