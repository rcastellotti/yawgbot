from yawgbot.yawgbot import Listing
from flask import Flask, render_template, request
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, scoped_session
import random
from flask import Flask, render_template

engine = create_engine("sqlite:///yawgbot.sqlite", echo=False)
Base = declarative_base()
session_factory = sessionmaker(bind=engine)
Session = scoped_session(session_factory)

app = Flask(__name__, template_folder=".")

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


def randomClass():
    return random.choice(wes)




@app.get("/")
def index():
    page = request.args.get("page")
    if page is None:
        page = 0
        nextPage = 1
    page=int(page)
    nextPage = page + 1
    prevPage = page - 1
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
        randomClass=randomClass,
        prevPage=prevPage,
        nextPage=nextPage,
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0")
