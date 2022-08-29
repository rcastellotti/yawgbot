from dataclasses import dataclass
import requests
from bs4 import BeautifulSoup as bs
import re
import json
import logging
import os
from dotenv import load_dotenv

URL = "https://www.wg-gesucht.de/1-zimmer-wohnungen-in-Munchen.90.1.1.{}.html"

ID_REGEX = r"\.(\d*)\.html"
load_dotenv()
USER = os.environ["LOGIN_EMAIL_USERNAME"]
PASSWORD = os.environ["LOGIN_PASSWORD"]
TEMPLATE_MESSAGE = os.environ["TEMPLATE_MESSAGE"]

logging.basicConfig(level=logging.INFO)


@dataclass
class Listing:
    name: str
    price: int
    dates: str
    url: str
    square_meters: str
    id: int

    def __init__(self, name, dates, price, url, square_meters):
        self.name = name
        self.square_meters = square_meters
        self.dates = dates
        self.price = price
        self.url = "https://www.wg-gesucht.de" + url
        self.id = re.findall(ID_REGEX, self.url)[0]

    def send_message(self):
        s = requests.Session()
        r = s.post(
            "https://www.wg-gesucht.de/ajax/sessions.php?action=login",
            json={
                "login_email_username": USER,
                "login_password": PASSWORD,
                "login_form_auto_login": "1",
                "display_language": "de",
            },
        )
        csrf_token = json.loads(r.text)["csrf_token"]
        user_id = json.loads(r.text)["user_id"]

        json_data = {
            "user_id": user_id,
            "csrf_token": csrf_token,
            "messages": [
                {
                    "content": TEMPLATE_MESSAGE,
                    "message_type": "text",
                },
            ],
            "ad_type": "0",
            "ad_id": self.id,
        }

        response = s.post(
            "https://www.wg-gesucht.de/ajax/conversations.php",
            params={"action": "conversations"},
            json=json_data,
        )
        # logging.info(f"contacted ad: {self.name} - {self.price} - {self.dates}")
        logging.info(f"contacted ad: {self.name}")
        logging.debug(response.text)


def main():
    logging.info(f"loaded config for user {USER}")
    for i in range(5):
        r = requests.get(URL.format(i))
        soup = bs(r.text, "html.parser")
        listingSoup = soup.select(".wgg_card:not(.noprint)")

        for l in listingSoup:
            listing = Listing(
                name=l.find_all("a")[1].text.strip(),
                url=l.find_all("a")[1]["href"],
                square_meters=l.find_all(attrs={"class": "col-xs-3"})[1].text.strip(),
                dates="".join(
                    l.find(attrs={"class": "col-xs-5 text-center"}).text.split()
                ),
                price=l.find_all(attrs={"class": "col-xs-3"})[0].text.strip(),
            )
            listing.send_message()


if __name__ == "__main__":
    main()
