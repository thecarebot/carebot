[Carebot](http://thecarebot.github.io) is an effort in thinking about alternative ways to look at analytics for journalism: both the measures and indicators used to understand story impact, and the way which analytics data is used in the newsroom. 

##Quick Start Guide
To get Carebot up and running you will need to:

1. Add the [Carebot Tracker](http://github.com/theCarebot/carebot-tracker) to your content.
2. Set up the Carebot Slackbot to report data through notifications.

Note: You will need a Google Analytics account and a Slack account.

Coming soon: See the **Carebot Newsroom Analytics Guide** for a more detailed walkthrough of how to plan for analytics in the newsroom and make decisions about the right tools for the job.

# Carebot: The Slackbot

* [What is this?](#what-is-this)
* [Assumptions](#assumptions)
* [Bootstrap the project](#bootstrap-the-project)
* [Run the project](#run-the-project)
* [Setup analytics](#setup-analytics)

## What is this?

Carebot reports data insights from [tracked metrics](http://github.com/theCarebot/carebot-tracker) in the form of notifications. This slackbot implementation allows you to push those notifications into [Slack](http://slack.com) channels for your team.

## Using Carebot

Here's how to work with Carebot if it's in your channels. 

### Handy commands

Help!

> @carebot help

To find out details about a story: 

> @carebot slug story-slug-here

> @carebot What's going on with slug story-slug-here?

> @carebot Give me the scoop on slug another-slug-here please! 

To see an overview of the last week: 

> @carebot hello!

Carebot will automatically track stories (see "Running Carebot", below). Sometimes you want to manually add stories to the queue:

> @carebot track story-slug-here http://example.com/story

## Assumptions for developing

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

### NPR API credentials

You'll need a key for the NPR API. You can [register for one here](http://www.npr.org/api/index.php)

### Add Google Analytics credentials

The first time you run Carebot, you'll need to authorize the app with your
Google account. To do that, run

```
fab app
```

And follow the on-screen instructions. If you have already set up an app using
the NPR Apps template, you may not have to do this.

### Run the optional screenshot tool

Scroll depth stats use an [optional screenshot tool](https://github.com/thecarebot/screenshotter) to 
take snaps of your pages. We've hardcoded in the URL to our service and you can run it on your own if 
you prefer. It runs well on Heroku or any other place you can run a Node app. However, it's totally 
optional and the bot will run just fine without it. 

## Running Carebot

### Run the bot

```
python carebot.py
```

After starting the bot, make sure to invite it to the channel you set in `.env`.

### Configuring Carebot to load new stories

Configure Carebot to pull stores from various sources by customizing `config.yml`.

Under `teams`, define team names and the channel messages for that team should
post to.

Under `sources` define where content should be pulled from, and what team it
belongs to. Here's an example:

```
teams:
  viz:
    channel: "visuals-graphics"
  carebot:
    channel: "carebot-dev"
sources:
  -
    team: "viz"
    type: "spreadsheet"
    doc_key: "1Gcumd0uOl3eSUvc0y5CWmmHVOKwX609-js5EnE8i3lI"
  -
    team: "carebot"
    type: "rss"
    url: "https://thecarebot.github.io/feed.xml"

```

### Get new stories from the story spreadsheet

This is usually run via a cronjob, but you can fire it manually:

```
fab load_new_stories
```

### Get stats on stories

This is usually run via a cronjob after `load_new_stories`, but you can fire it
manually:

```
fab get_story_stats
```

## Carebot in production 

To deploy carebot to production:

```
fab production deploy
```

### Server setup

You'll need a couple packages:

* SQLite: `sudo apt-get install sqlite3 libsqlite3-dev`
* `sudo apt-get install python-dev` for pycrypto
* `sudo apt-get install libpng-dev` for matplotlib
* `sudo apt-get install libfreetype6-dev libxft-dev` for matplotlib
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
* Not all errors go there :-/. You might want to try outputting each command in `confs/bot.conf`, eg `...command >> {{ SERVER_PROJECT_PATH }}/log.txt`
* The cron file is `/etc/cron.d/carebot`
* Cron errors might end up in `/var/log/syslog`; check `tail -100 /var/log/syslog`
* By default, cron errors will be in `/var/log/carebot/`

## Developing Carebot

### Tests

To run tests:

```
nosetests
```

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

