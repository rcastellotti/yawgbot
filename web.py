from yawgbot import Bot, Listing
from flask import Flask, render_template
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker,scoped_session

from flask import Flask, render_template
from celery import Celery

CELERY_RESULT_DBURI = "db+sqlite:///celerydb.sqlite"
BROKER_URL = "sqla+sqlite:///celerydb.sqlite"


engine = create_engine("sqlite:///test.db", echo=False)
Base = declarative_base()
session_factory = sessionmaker(bind=engine)
Session = scoped_session(session_factory)


celery = Celery("main", broker=BROKER_URL, backend=CELERY_RESULT_DBURI)
app = Flask(__name__, template_folder=".")


@celery.task
def runBot():
    URL = "https://www.wg-gesucht.de/1-zimmer-wohnungen-in-Munchen.90.1.1.{}.html"
    bot = Bot(url=URL)
    bot.run()


@celery.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    # Calls runBot('hello') every 20 minutes.
    sender.add_periodic_task(60*20, runBot.s(), name="runBot every 5 minutes")


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
