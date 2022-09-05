from yawgbot import Listing
from flask import Flask, render_template
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, scoped_session

from flask import Flask, render_template

engine = create_engine("sqlite:///yawgbot.sqlite", echo=False)
Base = declarative_base()
session_factory = sessionmaker(bind=engine)
Session = scoped_session(session_factory)

app = Flask(__name__, template_folder=".")


@app.get("/")
def index():
    session = Session()
    listings = (
        session.query(Listing)
        .order_by(Listing.added_at.desc())
        .filter(Listing.price.isnot(""))
        .all()
    )
    Session.remove()
    return render_template("index.html", listings=listings)


if __name__ == "__main__":
    app.run(host="0.0.0.0")
