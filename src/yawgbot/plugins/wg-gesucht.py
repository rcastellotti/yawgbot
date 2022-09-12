import requests
from bs4 import BeautifulSoup as bs
import logging
from yawgbot.pluginBase import PluginBase
from yawgbot.listing import Listing
from yawgbot.bot import Bot
import re
import json
import sys


class YawgbotPlugin(PluginBase):
    ID_REGEX = r"\.(\d*)\.html"
    IMG_REGEX = r"\(([^\)]+)\)"
    COLOR = "#f97316"
    PLATFORM = "https://www.wg-gesucht.de/"

    def __init__(self):
        config = Bot.config()["wg-gesucht"]
        self.username = config["username"]
        self.password = config["password"]
        self.base_url = config["base_url"]
        self.message_template = config["message_template"]
        self.s = requests.Session()
        r = self.s.post(
            "https://www.wg-gesucht.de/ajax/sessions.php?action=login",
            json={
                "login_email_username": self.username,
                "login_password": self.password,
            },
        )

        self.csrf_token = json.loads(r.text)["csrf_token"]
        self.user_id = json.loads(r.text)["user_id"]
        logging.debug(r.text)

    def get_ads(self, url):
        r = requests.get(url)
        soup = bs(r.text, "html.parser")
        logging.debug(soup.prettify())
        ads = soup.select(".wgg_card:not(.noprint)")
        return ads

    def parse_ad(self, ad):
        url = "https://www.wg-gesucht.de" + ad.find_all("a")[1]["href"]
        name = ad.find_all("a")[1].text.strip()
        slug = re.findall(self.ID_REGEX, url)[0]
        size = ad.find_all(attrs={"class": "col-xs-3"})[1].text.strip()
        dates = "".join(ad.find(attrs={"class": "col-xs-5 text-center"}).text.split())
        price = ad.find_all(attrs={"class": "col-xs-3"})[0].text.strip()
        location_string = (
            ad.find_all(attrs={"class": "col-xs-11"})[0]
            .text.replace("\n", "")
            .replace(" ", "")
        )
        location = location_string[location_string.find("|") + 1 :].replace("|", " | ")
        image = re.findall(
            self.IMG_REGEX, str(ad.find(attrs={"class": "card_image"}).find("a"))
        )[0]

        listing = Listing(
            name=name,
            url=url,
            slug=slug,
            size=size,
            location=location,
            image=image,
            dates=dates,
            price=price,
            platform=self.PLATFORM,
            color=self.COLOR,
        )
        return listing

    def contact_ad(self, slug):
        json_data = {
            "user_id": self.user_id,
            "csrf_token": self.csrf_token,
            "messages": [
                {
                    "content": self.message_template,
                    "message_type": "text",
                },
            ],
            "ad_type": "0",
            "ad_id": slug,
        }

        r = self.s.post(
            "https://www.wg-gesucht.de/ajax/conversations.php",
            params={"action": "conversations"},
            json=json_data,
        )
        logging.debug(r.text)
        pass

    def run(self):
        logging.info("running wg-gesucht plugin")
        for i in range(5):
            ads = self.get_ads(self.base_url.format(i))
            logging.debug(ads)
            for ad in ads:
                listing = self.parse_ad(ad)
                self.create_listing(listing)
