import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy_utils import database_exists
import importlib
from yawgbot.pluginBase import PluginBase
from platformdirs import user_data_dir

load_dotenv()
db_uri = f"{user_data_dir('yawgbot', 'rcastellotti')}/yawgbot.sqlite"
engine = create_engine(f"sqlite:///{db_uri}", echo=False)
Base = declarative_base()


class Bot:
    def __init__(self, platforms: list = []):
        self._platforms = []
        if platforms:
            for plugin in platforms:
                plugin_to_add = importlib.import_module(
                    f"yawgbot.plugins.{plugin}"
                ).YawgbotPlugin()
                if isinstance(plugin_to_add, PluginBase):
                    self._platforms.append(plugin_to_add)

        os.makedirs(user_data_dir("yawgbot", "rcastellotti"), exist_ok=True)
        if not database_exists(f"sqlite:///{db_uri}"):
            Base.metadata.create_all(engine)

    def run(self):
        for platform in self._platforms:
            platform.run()
