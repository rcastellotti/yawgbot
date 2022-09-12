import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy_utils import database_exists
import importlib
from yawgbot.pluginBase import PluginBase
from platformdirs import user_data_dir, user_config_dir
import yaml
import logging
import sys

load_dotenv()
db_uri = f"{user_data_dir('yawgbot', 'rcastellotti')}/yawgbot.sqlite"
config_uri = f"{user_config_dir('yawgbot', 'rcastellotti')}/config.yml"
engine = create_engine(f"sqlite:///{db_uri}", echo=False)
Base = declarative_base()


class Bot:
    @staticmethod
    def config():
        with open(config_uri, "r+") as f:
            data = yaml.safe_load(f)
        return data

    def register_plugin(self, plugin):
        plugin_to_add = importlib.import_module(plugin).YawgbotPlugin()
        self._platforms.append(plugin_to_add)

    def __init__(self, platforms: list = []):
        self._platforms = []
        if platforms:
            for plugin in platforms:
                try:
                    plugin_to_add = importlib.import_module(
                        f"yawgbot.plugins.{plugin}"
                    ).YawgbotPlugin()
                except KeyError as e:
                    logging.exception(f"config value {str(e)} not found")
                    sys.exit(1)
                if isinstance(plugin_to_add, PluginBase):
                    self._platforms.append(plugin_to_add)

        os.makedirs(user_data_dir("yawgbot", "rcastellotti"), exist_ok=True)
        os.makedirs(user_config_dir("yawgbot", "rcastellotti"), exist_ok=True)
        if not database_exists(f"sqlite:///{db_uri}"):
            Base.metadata.create_all(engine)

    def run(self):
        for platform in self._platforms:
            platform.run()
