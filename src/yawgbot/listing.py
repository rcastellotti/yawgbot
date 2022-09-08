from sqlalchemy import Column, Integer, String, DateTime
import datetime
from sqlalchemy.orm import declarative_base

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
    color = Column(String)
    platform = Column(String)

    def __repr__(self):
        return "<Listing(name='%s')>" % (self.name,)
