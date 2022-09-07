from yawgbot.yawgbot import Bot

from celery import Celery

CELERY_RESULT_DBURI = "db+sqlite:///celerydb.sqlite"
BROKER_URL = "sqla+sqlite:///celerydb.sqlite"

celery = Celery("main", broker=BROKER_URL, backend=CELERY_RESULT_DBURI)


@celery.task
def runBot():
    URL = "https://www.wg-gesucht.de/wg-zimmer-und-1-zimmer-wohnungen-in-Munchen.90.0+1.1.{}.html"
    bot = Bot(url=URL, telegram=True)
    bot.run()


@celery.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(60 * 5, runBot.s(), name="runBot every 5 minutes")
