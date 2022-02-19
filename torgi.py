import datetime


OPENDATA_PASSPORT_URL = "https://torgi.gov.ru/new/opendata/7710568760-notice/data-{}T0000-{}T0000-structure-20220101.json"


def get_opendata_passport_url(days_count: int) -> str:
    today = datetime.date.today()
    past_day = today - datetime.timedelta(days=days_count)
    dates = [date.strftime("%Y%m%d") for date in (past_day, today)]

    passport_url = OPENDATA_PASSPORT_URL.format(*dates)

    return passport_url


def main():
    passport_url = get_opendata_passport_url(days_count=1)
    print(passport_url)


if __name__ == "__main__":
    main()
