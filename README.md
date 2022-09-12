# yawgbot

[![PyPI version](https://badge.fury.io/py/yawgbot.svg)](https://badge.fury.io/py/yawgbot) [![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

Yet Another WG helper bot. WG stands for *Wohngemeinschaft*, a German word that refers to a living arrangement in which
several tenants share an apartment. It is aimed to automate the extremely complex and time-consuming task of finding a
room or an apartment to rent. Initially it was only working for [wg-gesucht.de](https://wg-gesucht.de), now it's a
plugin-based system ready to be extended for every platform to find accommodation.

`yawgbot` is a simple python bot that scrapes websites offering accommodation ads and contacts landlords. It uses a
SQLite database to save contacted ads and to perform fewer requests to platforms. It also offers a simple web UI to
track your progress and gather your findings across different platforms.

## running manually

To run the bot manually:

+ install the package with `pip3 install yawgbot` (a [virtual environment](https://docs.python.org/3/tutorial/venv.html)
  is suggested)
+ configure `.env.sample` and rename it to `.env`
+ create a new file named `bot.py` with the following content and run it:

```python
from yawgbot import Bot
import logging

logging.basicConfig(level=logging.INFO)

bot = Bot(platfors=["wg-gesucht"])
bot.run()
```

## running periodically with celery

Yawgbot uses [Celery](https://docs.celeryq.dev/en/stable/) to schedule tasks. It is configured to
use [SQLite](https://sqlite.org) as
both [backend and broker](https://docs.celeryq.dev/en/stable/getting-started/backends-and-brokers/index.html), to know
more read the docs. The file `run_yawgbot.py` is provided to run the bot each 5 minutes, to use it:

- run `celery -A run_yawgbot.celery worker --loglevel=INFO` to run the worker
- run `celery -A run_yawgbot.celery beat` to schedule the bot

## web UI

To start the web UI simply run `yawgbot-web`

## plugins

### creating a plugin

Extending `yawgbot` is a pretty straightforward process. A plugin is a simple module extending the `PluginBase` class,
an example is [`wg-gesucht.py`](https://github.com/rcastellotti/yawgbot/blob/master/src/yawgbot/plugins/wg-gesucht.py),
supported plugins can be used just by instantiating `Bot` with the `platforms` argument. Custom plugins can be
registered using the `Bot.register_plugin()` method. To start creating a template you can use this boilerplate code:

```python3
from yawgbot.pluginBase import PluginBase


class YawgbotPlugin(PluginBase):
    def __init__(self):
        pass

    def get_ads(self, url):
        pass

    def parse_ad(self, ad):
        pass

    def contact_ad(self, slug):
        pass

    def run(self):
        pass
```

If you develop a plugin, consider creating a PR, I will be more than happy to work with you to make it an official
plugin and ship it with `yawgbot`.

### wg-gesucht

```yml
wg-gesucht:
  username: ""
  password: ""
  message_template: ""
  base_url: ""
```

When configuring for use go on [https://wg-gesucht.de](https://wg-gesucht.de) and copy the url you are using to look for
accommodation, then replace the last number with `{}` in order to be able to search across multiple pages, for example,
if looking for apartments in Munich: base url is `https://www.wg-gesucht.de/1-zimmer-wohnungen-in-Munchen.90.1.1.1.html`
, replace the last `1` as follows: `https://www.wg-gesucht.de/1-zimmer-wohnungen-in-Munchen.90.1.1.{}.html`