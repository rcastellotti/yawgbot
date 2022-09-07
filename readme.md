# yawgbot

Yet Another WG helper bot. WG stands for *Wohngemeinschaft*, a German word that refers to a living arrangement in which
several tenants share an apartment. It is aimed to automate the extremely complex and time-consuming task of finding a
room or an apartment to rent. Initially it was only working for [wg-gesucht.de](https://wg-gesucht.de), now it's a
plugin-based system ready to be extended for every platform to find accommodation.

`yawgbot` is a simple python bot that scrapes websites offering accommodation ads and contacts landlords. It uses a
SQLite database to save contacted ads and to perform fewer requests to platforms. It also offers a simple web UI to
track your progress and gather your findings across different platforms.

## configuration

## creating a plugin

## running periodically

## instructions

- create a python virtual environment with `python3 -m venv vev`
- activate the virtual environment with `source venv/bin/activate` (might be different if not using bash)
- install the dependencies with `pip3 install -r requirements.txt`
- configure `.env.sample` and rename it to `.env`

When configuring for use go on [https://wg-gesucht.de](https://wg-gesucht.de) and copy the url you are using to look for
accommodation, then replace the last number with `{}` in order to be able to search across multiple pages, for example,
if looking for apartments in Munich: base url
is `https://www.wg-gesucht.de/1-zimmer-wohnungen-in-Munchen.90.1.1.1.html`, replace the last `1` as
follows: `https://www.wg-gesucht.de/1-zimmer-wohnungen-in-Munchen.90.1.1.{}.html`

## running manually

Running the bot manually is as simple as creating a new file named `bot.py` with the following content and running it:

```python
from yawgbot.bot import Bot
import logging

logging.basicConfig(level=logging.DEBUG)

URL = "https://www.wg-gesucht.de/1-zimmer-wohnungen-in-Munchen.90.1.1.{}.html"
bot = Bot()
bot.run()
```

## running periodically with celery and web UI

Yawgbot uses [Celery](https://docs.celeryq.dev/en/stable/) to schedule tasks. By default, it runs each 10 minutes. It is
configured to use [SQLite](https://sqlite.org) as
both [backend and broker](https://docs.celeryq.dev/en/stable/getting-started/backends-and-brokers/index.html), to know
more read the docs.

- run the web UI with `python3 app.py`
- run `celery -A bot.celery worker` to run the worker
- run `celery -A bot.celery beat` to schedule the bot

Now you can check the web UI to have a summary of contacted ads, reach it locally at: <http://localhost:5000/> or at `/`
wherever you deployed Yawgbot

