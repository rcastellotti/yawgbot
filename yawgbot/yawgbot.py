import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.orm import declarative_base
import datetime
from sqlalchemy_utils import database_exists
import importlib
from yawgbot.pluginBase import PluginBase

load_dotenv()
engine = create_engine("sqlite:///yawgbot.sqlite", echo=False)
Base = declarative_base()


class Listing(Base):
    __tablename__ = "listings"
    id = Column(Integer, primary_key=True)
    slug = Column(Integer, nullable=False)
    added_at = Column(DateTime, default=datetime.datetime.now)
    price = Column(Integer)
    name = Column(String)
    url = Column(String)
    image = Column(String)
    location = Column(String)
    size = Column(String)
    dates = Column(String)


class Bot:
    TG_API_KEY = os.environ["TG_API_KEY"]
    TG_CHAT_ID = os.environ["TG_CHAT_ID"]

    def __init__(self, platforms: list = []):
        self._platforms = []
        if platforms != []:
            for plugin in platforms:
                pluginToAdd = importlib.import_module(
                    f"yawgbot.plugins.{plugin}"
                ).YawgbotPlugin()
                if isinstance(pluginToAdd, PluginBase):
                    self._platforms.append(pluginToAdd)

        if not database_exists("sqlite:///test.sqlite"):
            Base.metadata.create_all(engine)

    def run(self):
        for platform in self._platforms:
            platform.run()
