import datetime
import json

import requests

OPENDATA_PASSPORT_URL = "https://torgi.gov.ru/new/opendata/7710568760-notice/data-{}T0000-{}T0000-structure-20220101.json"
PASSPORT_FILENAME = "passport.json"


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


def main():
    passport_url = get_opendata_passport_url(days_count=1)
    try:
        passport_json = fetch_opendata_passport(
            url=passport_url, verify_ssl=True, filename=PASSPORT_FILENAME
        )
    except requests.exceptions.SSLError:
        passport_json = fetch_opendata_passport(
            url=passport_url, verify_ssl=False, filename=PASSPORT_FILENAME
        )


if __name__ == "__main__":
    main()
