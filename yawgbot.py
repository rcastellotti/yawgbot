import requests
from bs4 import BeautifulSoup as bs
import re
import json
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
import datetime
import logging
from sqlalchemy_utils import database_exists
import time

ID_REGEX = r"\.(\d*)\.html"

load_dotenv()
engine = create_engine("sqlite:///yawgbot.sqlite", echo=False)
Base = declarative_base()
Session = sessionmaker(bind=engine)


class Listing(Base):
    __tablename__ = "listings"
    id = Column(Integer, primary_key=True)
    wg_id = Column(Integer, unique=True)
    added_at = Column(DateTime, default=datetime.datetime.now)
    price = Column(Integer)
    name = Column(String)
    url = Column(String)
    location = Column(String)
    square_meters = Column(String)
    dates = Column(String)

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def send_message(self):
        s = requests.Session()
        r = s.post(
            "https://www.wg-gesucht.de/ajax/sessions.php?action=login",
            json={
                "login_email_username": Bot.USER,
                "login_password": Bot.PASSWORD,
            },
        )
        logging.debug(r.text)
        csrf_token = json.loads(r.text)["csrf_token"]
        user_id = json.loads(r.text)["user_id"]

        json_data = {
            "user_id": user_id,
            "csrf_token": csrf_token,
            "messages": [
                {
                    "content": Bot.TEMPLATE_MESSAGE,
                    "message_type": "text",
                },
            ],
            "ad_type": "0",
            "ad_id": self.wg_id,
        }

        response = s.post(
            "https://www.wg-gesucht.de/ajax/conversations.php",
            params={"action": "conversations"},
            json=json_data,
        )
        logging.debug(response.text)


class Bot:

    TG_API_KEY = os.environ["TG_API_KEY"]
    TG_CHAT_ID = os.environ["TG_CHAT_ID"]
    USER = os.environ["LOGIN_EMAIL_USERNAME"]
    PASSWORD = os.environ["LOGIN_PASSWORD"]
    TEMPLATE_MESSAGE = os.environ["TEMPLATE_MESSAGE"]

    def __init__(self, url, telegram=False):
        self.url = url
        self.telegram = telegram
        if not database_exists("sqlite:///test.sqlite"):
            Base.metadata.create_all(engine)

    def tg_send_message(self, listing):
        r = requests.get(
            f"https://api.telegram.org/bot{self.TG_API_KEY}/sendMessage",
            params={
                "text": f"""<b>yawgbot telegram updates</b>

ℹ️ contacted ad <a href="{listing.url}">#{listing.wg_id}</a>
📍<a href='https://www.google.com/maps/search/?api=1&query={listing.location}'>view location on Google Maps</a>
📐 {listing.square_meters}
💰 {listing.price}
📅 {listing.dates}
🔗 <a href='{listing.url}'>view on wg-gesucht.de</a>

powered by: <a href="https://github.com/rcastellotti/yawgbot">yawgbot</a> // made with ❤️ by @rcastellotti
""",
                "chat_id": self.TG_CHAT_ID,
                "parse_mode": "HTML",
                "disable_web_page_preview": True,
            },
        )
        logging.debug(r.text)

    def run(self):
        logging.info(f"loaded config for user:{self.USER}")
        for i in range(0, 5):
            logging.info(f"requesting page:{self.url.format(i)}")
            r = requests.get(self.url.format(i))
            soup = bs(r.text, "html.parser")
            listingSoup = soup.select(".wgg_card:not(.noprint)")

            for l in listingSoup:
                url = "https://www.wg-gesucht.de" + l.find_all("a")[1]["href"]
                name = l.find_all("a")[1].text.strip()
                square_meters = l.find_all(attrs={"class": "col-xs-3"})[1].text.strip()
                dates = "".join(
                    l.find(attrs={"class": "col-xs-5 text-center"}).text.split()
                )
                price = l.find_all(attrs={"class": "col-xs-3"})[0].text.strip()
                location_string = (
                    l.find_all(attrs={"class": "col-xs-11"})[0]
                    .text.replace("\n", "")
                    .replace(" ", "")
                )
                location = location_string[location_string.find("|") + 1 :].replace(
                    "|", " | "
                )

                listing = Listing(
                    name=name,
                    url=url,
                    wg_id=re.findall(ID_REGEX, url)[0],
                    square_meters=square_meters,
                    location=location,
                    dates=dates,
                    price=price,
                )
                session = Session()

                exists = bool(
                    session.query(Listing).filter_by(wg_id=listing.wg_id).first()
                )
                if not exists:
                    session.add(listing)
                    listing.send_message()
                    if self.telegram:
                        self.tg_send_message(listing=listing)
                    logging.info(f"contacting ad: {listing.name}")
                    session.commit()
                else:
                    logging.warning(f"skipping ad:{listing.name}")
            time.sleep(40)
