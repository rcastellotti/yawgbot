import requests
from bs4 import BeautifulSoup as bs
import logging
from yawgbot.pluginBase import PluginBase
from yawgbot.yawgbot import Listing
import re
import os
import json


class YawgbotPlugin(PluginBase):
    ID_REGEX = r"\.(\d*)\.html"
    IMG_REGEX = r"\(([^\)]+)\)"
    WG_GESUCHT_USERNAME = os.environ["WG_GESUCHT_USERNAME"]
    WG_GESUCHT_PASSWORD = os.environ["WG_GESUCHT_PASSWORD"]
    WG_GESUCHT_TEMPLATE_MESSAGE = os.environ["WG_GESUCHT_TEMPLATE_MESSAGE"]

    def __init__(self):
        self.s = requests.Session()
        r = self.s.post(
            "https://www.wg-gesucht.de/ajax/sessions.php?action=login",
            json={
                "login_email_username": self.WG_GESUCHT_USERNAME,
                "login_password": self.WG_GESUCHT_PASSWORD,
            },
        )
        self.csrf_token = json.loads(r.text)["csrf_token"]
        self.user_id = json.loads(r.text)["user_id"]
        logging.debug(r.text)

    def getAds(self, url):
        r = requests.get(url)
        soup = bs(r.text, "html.parser")
        logging.debug(soup.prettify())
        ads = soup.select(".wgg_card:not(.noprint)")
        return ads

    def createListing(self, ad):
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
        )
        session = self.Session()

        if not session.query(Listing).filter_by(slug=listing.slug).first():
            logging.info(f"new ad found: {listing.name}")
            session.add(listing)
            self.contactAd(listing.slug)
            session.commit()
        else:
            logging.info(f"skipping ad:{listing.name}")

    def contactAd(self, slug):

        json_data = {
            "user_id": self.user_id,
            "csrf_token": self.csrf_token,
            "messages": [
                {
                    "content": self.WG_GESUCHT_TEMPLATE_MESSAGE,
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
        ads = self.getAds(
            url="https://www.wg-gesucht.de/wg-zimmer-und-1-zimmer-wohnungen-in-Munchen.90.0+1.1.0.html"
        )
        logging.debug(ads)
        for ad in ads:
            self.createListing(ad)
