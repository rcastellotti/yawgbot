from yawgbot import Bot

from celery import Celery

CELERY_RESULT_DBURI = "db+sqlite:///celerydb.sqlite"
BROKER_URL = "sqla+sqlite:///celerydb.sqlite"

celery = Celery("main", broker=BROKER_URL, backend=CELERY_RESULT_DBURI)


@celery.task
def runBot():
    bot = Bot(platforms=["wg-gesucht"])
    bot.run()


@celery.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(60 * 5, runBot.s(), name="run yawgbot every 5 minutes")
