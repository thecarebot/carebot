# Carebot: The Slackbot

* [What is this?](#what-is-this)
* [Assumptions](#assumptions)
* [Bootstrap the project](#bootstrap-the-project)
* [Run the project](#run-the-project)
* [Setup analytics](#setup-analytics)

## What is this?

Carebot is a prototype approach to more meaningful analytics in journalism. We are [currently developing](https://github.com/thecarebot/carebot/wiki) a set of experimental metrics (measures and indicators) for a variety of storytelling approaches and exploring new ways to offer insights in a timely and conveniant manner to journalists after stories are published.

The project is currently under development, thanks to a Knight Foundation [Prototype Grant](http://www.knightfoundation.org/grants/201551645/). The first implementation of Carebot is using a Slack bot account (this repo) and a [tracker component](https://github.com/thecarebot/carebot-tracker). This code is free to use. See [license](https://github.com/thecarebot/carebot/blob/master/LICENSE.md) for details.

## Assumptions

The following things are assumed to be true in this documentation.

* You are running OSX.
* You are using Python 2.7.
* You have [virtualenv](https://pypi.python.org/pypi/virtualenv) and [virtualenvwrapper](https://pypi.python.org/pypi/virtualenvwrapper) installed and working.

If you need assistance setting up a development environment to work with this for the first time, we recommend [NPR Visuals' Setup](http://blog.apps.npr.org/2013/06/06/how-to-setup-a-developers-environment.html).

## Bootstrap the project

Clone this repository and create a virtual environment:
```
git clone https://github.com/thecarebot/carebot.git
cd carebot
mkvirtualenv carebot --no-site-packages
workon carebot
```

### Install the dependencies

```
pip install -r requirements.txt
```

### Add credentials

The bot requires several API credentials available as environment variables.
An easy way to add them is to use a `.env` file. Copy `sample.env` to `dev.env`.
Fill in the values. Then, run `source dev.env` to make them availabe.

Copy `sample.env` to `production.env` to store production keys. The `.env` file
is copied to the server on deploy.

### Add Google Analytics credentials

The first time you run Carebot, you'll need to authorize the app with your
Google account. To do that, run

```
fab app
```

And follow the on-screen instructions. If you have already set up an app using
the NPR Apps template, you may not have to do this.

## Using Carebot

### Run the bot

```
python carebot.py
```

### Get new stories from the story spreadsheet

```
fab load_new_stories
```

## Deploying the project

To deploy carebot to production:

```
fab production deploy
```

### Server setup

You'll need a couple packages:

* SQLite: `sudo apt-get install sqlite3 libsqlite3-dev`
* `sudo apt-get install python-dev` for pycrypto
* Any other basics: python, pip.

### First deploy

Make sure you have a `.env` file with your production keys (see "add
creditials"). Also, ensure you have an `analytics.dat` file (see "Add Google
Analytics Credentials" above).

Then, run:

```
fab production setup
```

### Later depoy

```
fab production deploy
```

### Debugging deploy

We use `upstart` to keep carebot running on deploys. Sometimes carebot doesn't
start. The debug process is fairly annoying, but here are some things that might
help.

* Logs should be available in `/var/log/upstart/carebot.log`
* Not all errors go there :-/. You might want to try outputting each command in `confs/bot.conf`, eg `...command >> {{ SERVER_PROJECT_PATH }}/log.txt
* The cron file is `/etc/cron.d/carebot`
* Cron errors might end up in `/var/log/syslog`; check `tail -100 /var/log/syslog`
* By defauly, cron errors will be in `/var/log/carebot/`

## Developing Carebot

### Migrations
If you make changes to existing models in `models.py`, you will need to [write
a migration](http://docs.peewee-orm.com/en/latest/peewee/playhouse.html#migrate).

For now, migrations are not automatically run on deploy and may need to be run
manually. Inside the environment, run `python MIGRATION_NAME.py`

### Misc
```
Dev notes for Matt:
Sample analytics code:
https://github.com/google/google-api-python-client/tree/master/samples/analytics

https://developers.google.com/api-client-library/python/auth/web-app
```

