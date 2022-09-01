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
    chat_url = Column(String)
    read = Column(Integer)
    square_meters = Column(String)
    dates = Column(String)

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
            "ad_id": self.id,
        }

        response = s.post(
            "https://www.wg-gesucht.de/ajax/conversations.php",
            params={"action": "conversations"},
            json=json_data,
        )
        logging.debug(response.text)


class Bot:

    USER = os.environ["LOGIN_EMAIL_USERNAME"]
    PASSWORD = os.environ["LOGIN_PASSWORD"]
    TEMPLATE_MESSAGE = os.environ["TEMPLATE_MESSAGE"]

    def __init__(self, url):
        self.url = url
        if (not database_exists("sqlite:///test.sqlite")):
            Base.metadata.create_all(engine)

    def add_conversation_url_and_read_info(self):
        s = requests.Session()
        r = s.post(
            "https://www.wg-gesucht.de/ajax/sessions.php?action=login",
            json={
                "login_email_username": self.USER,
                "login_password": self.PASSWORD,
            },
        )

        r = s.get(
            "https://www.wg-gesucht.de/ajax/conversations.php?action=all-conversations-notifications"
        )
        session = Session()
        for item in r.json()["_embedded"]["conversations"]:
            try:
                listing = session.query(Listing).filter_by(wg_id=item["ad_id"]).first()
                listing.chat_url = f"https://www.wg-gesucht.de/nachricht.html?nachrichten-id={item['conversation_id']}"
                listing.read = not item["unread"]
                session.commit()
            except:
                pass

    def run(self):
        logging.info(f"loaded config for user:{self.USER}")
        for i in range(1, 25):

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

                listing = Listing(
                    name=name,
                    url=url,
                    wg_id=re.findall(ID_REGEX, url)[0],
                    square_meters=square_meters,
                    dates=dates,
                    price=price,
                )
                session = Session()

                exists = bool(
                    session.query(Listing).filter_by(wg_id=listing.wg_id).first()
                )
                if not exists:
                    session.add(listing)
                    logging.info(f"contacting ad: {listing.name}")
                    listing.send_message()
                    session.commit()
                else:
                    logging.warning(f"skipping ad:{listing.name}")

        logging.info(f"now updating chat_urls and read ")
