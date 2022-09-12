from yawgbot.listing import Listing
from flask import request
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, scoped_session
import random
from flask import Flask, render_template
from platformdirs import user_data_dir

db_uri = f"{user_data_dir('yawgbot', 'rcastellotti')}/yawgbot.sqlite"

engine = create_engine(f"sqlite:///{db_uri}", echo=False)
Base = declarative_base()
session_factory = sessionmaker(bind=engine)
Session = scoped_session(session_factory)

app = Flask(__name__, template_folder=".")


def random_class():
    wes = [
        "Royal2q0",
        "Royal2q1",
        "Royal2q2",
        "Royal2q3",
        "Royal2q4",
        "Zissou1q1",
        "GrandBudapest2q3",
        "BottleRocket2q1",
        "GrandBudapest1q3",
        "IsleofDogs1q0",
    ]


@app.get("/")
def index():
    page = request.args.get("page")
    if page is None:
        page = 0
        next_page = 1
    page = int(page)
    next_page = page + 1
    prev_page = page - 1
    session = Session()
    listings = (
        session.query(Listing)
        .order_by(Listing.added_at.desc())
        .filter(Listing.price.isnot(""))
        .limit(20)
        .offset(page * 20)
        .all()
    )
    Session.remove()
    return render_template(
        "index.html",
        listings=listings,
        random_class=random_class,
        prev_page=prev_page,
        next_page=next_page,
    )


def run():
    app.run(host="0.0.0.0")


if __name__ == "__main__":
    app.run(host="0.0.0.0")
