from abc import ABCMeta, abstractmethod
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from typing import List
from platformdirs import user_data_dir
from yawgbot.listing import Listing
import logging

db_uri = f"{user_data_dir('yawgbot', 'rcastellotti')}/yawgbot.sqlite"


class PluginBase(metaclass=ABCMeta):
    """Base class for plugins"""

    engine = create_engine(f"sqlite:///{db_uri}", echo=False)
    Base = declarative_base()
    Session = sessionmaker(bind=engine)

    @abstractmethod
    def contact_ad(self) -> None:
        """this method should contact the ad"""

    @abstractmethod
    def get_ads(self, url) -> List[str]:
        """this method should scrape a platform and return the HTML containing all the ads"""

    @abstractmethod
    def parse_ad(self, ad) -> Listing:
        """this method should parse an ad and return the data needed to create the listing"""

    # @abstractmethod
    def create_listing(self, listing: Listing) -> None:
        session = self.Session()

        if not session.query(Listing).filter_by(slug=listing.slug).first():
            logging.info(f"new ad found: {listing.name}")
            session.add(listing)
            self.contact_ad(listing.slug)
            session.commit()
        else:
            logging.info(f"skipping ad:{listing.name}")

    @abstractmethod
    def run(self):
        """this method runs the plugin"""

    # ogni plugin deve occuparsi di definire la condizione "ho trovato una immagine buona"
    # voglio che tutto sia typato
