# yawgbot

Yet Another WG-gesucht bot, stupid problems require stupid solutions :)

Yawgbot is a simple python bot to find accomodation using the popular website [https://wg-gesucht.de](https://wg-gesucht.de), it uses a SQLite database to save contacted ads in order to perform less requests to the website and escaping rate-limiting, it also offers a simple web UI to track your progress.

## instructions

- create a python virtual environment with `python3 -m venv vev`
- activate the virtual environment with `source venv/bin/activate` (might be different if not using bash)
- install the dependencies with `pip3 install -r requirements.txt`
- configure `.env.sample` and rename it to `.env`

When configuring for use go on [https://wg-gesucht.de](https://wg-gesucht.de) and copy the url you are using to look for accomodation, then subsitute the last number with `{}` in order to be able to search across multiple pages, for example, if looking for appartments in Munich: base url is `https://www.wg-gesucht.de/1-zimmer-wohnungen-in-Munchen.90.1.1.1.html`, replace the last `1` as follows: `https://www.wg-gesucht.de/1-zimmer-wohnungen-in-Munchen.90.1.1.{}.html`

## running manually

Running the bot manually is as simple as creating a new file named `bot.py` with the following content and running it:

```python
from yawgbot import Bot
import logging
logging.basicConfig(level=logging.DEBUG)

URL = "https://www.wg-gesucht.de/1-zimmer-wohnungen-in-Munchen.90.1.1.{}.html"
bot = Bot(url=URL)
bot.run()
```

## running periodically with celery and web UI

Yawgbot uses [Celery](https://docs.celeryq.dev/en/stable/) to schedule tasks. By default it runs each 10 minutes. It is configured to use [SQLite](https://sqlite.org) as both [backend and broker](https://docs.celeryq.dev/en/stable/getting-started/backends-and-brokers/index.html), to know more read the docs.

- run the web UI with `python3 web.py`
- run `celery -A web.celery worker` to run the worker
- run `celery -A web.celery beat` to schedule the bot

Now you can check the web UI to have a summary of contacted ads, reach it locally at: <http://localhost:5000/> or at `/` wherever you deployed Yawgbot
