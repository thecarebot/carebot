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

### Add Slack credentials

The bot requires a `SLACKBOT_API_TOKEN` environment variable.
You can set that from the command line by running:

```
export SLACKBOT_API_TOKEN=foo
```

### Add Google Analytics credentials

Using analytics requires a client ID and secret in a `client_secrets.json` file in the project root. Follow the [Google Analytics python setup instructions](https://developers.google.com/analytics/devguides/reporting/core/v3/quickstart/installed-py#enable) to get that file.

```
Dev notes for Matt:
Sample analytics code:
https://github.com/google/google-api-python-client/tree/master/samples/analytics

https://developers.google.com/api-client-library/python/auth/web-app
```

### Run the project

To run the bot:

```
python carebot.py
```


