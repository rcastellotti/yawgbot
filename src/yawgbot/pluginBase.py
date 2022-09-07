from abc import ABCMeta, abstractmethod
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from typing import List
from platformdirs import user_data_dir

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
    def create_listing(self, ad) -> None:
        """this method should extract relevant information from an ad (an element of the list returned by getAds)"""

    @abstractmethod
    def run(self):
        """this method runs the plugin"""

    # metodo che notifica
    # inventarsi qualcosa per assegnare alla piattaforma un colore ``
    # ogni plugin deve occuparsi di definire la condizione "ho trovato una immagine buona"
    # voglio che tutto sia typato
    # cambiare gli hover dei bottoni giu in basso
