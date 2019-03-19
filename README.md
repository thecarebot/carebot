[Carebot](http://thecarebot.github.io) is an effort in thinking about
alternative ways to look at analytics for journalism: both the measures and
indicators used to understand story impact, and the way which analytics data is
used in the newsroom.

Carebot takes [your metrics](http://github.com/theCarebot/carebot-tracker) and
posts them to your team's [Slack](http://slack.com) channels.


## Quick Start Guide
To get Carebot up and running you will need to:

1. Add the [Carebot Tracker](http://github.com/theCarebot/carebot-tracker) to your content.
2. Set up the [Carebot Slackbot](#what-is-this) to report data through notifications.

Note: You will need accounts with [Google Analytics](http://analytics.google.com) and [Slack](http://slack.com/create).

# Carebot: The Slackbot

* [Using Carebot](#using-carebot)
* [Installing Carebot](#installing-carebot)
* [Run the project](#run-the-project)
* [Setup analytics](#setup-analytics)

## Using Carebot

Here's how to work with Carebot once you've invited it to your channels.

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

## Installing Carebot

### Assumptions

The following things are assumed to be true in this documentation.

* You are running OSX.
* You are using Python 2.7.
* You have [virtualenv](https://pypi.python.org/pypi/virtualenv) and [virtualenvwrapper](https://pypi.python.org/pypi/virtualenvwrapper) installed and working.
* You have an Amazon Web Services account, and know how to create an S3 bucket
and associated access keys.
* You are using Google Analytics
* You are using Slack

If you need assistance setting up a development environment to work with this for the first time, we recommend [NPR Visuals' Setup](http://blog.apps.npr.org/2013/06/06/how-to-setup-a-developers-environment.html).


### First steps

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
Fill in the values (see detailed instructions below). Then, run `source dev.env`
to make them availabe to the app.

Copy `sample.env` to `staging.env` and `production.env` to store keys for those
environments. The appropriate `.env` file is copied to the server on deploy.

#### Add S3 credentials

Create an S3 bucket and add the bucket name, access key, and secret to your
`.env` file. You might want to set up a user that only has read-write access
to that bucket. No other Amazon services are needed.

#### Adding a slackbot integration

You'll need to add a slackbot integration to get a `SLACKBOT_API_TOKEN`:

1. Browse to http://yourteam.slack.com/apps/manage/custom-integrations
2. Navigate to "Bots"
3. Select "Add integration"
4. Fill in the username with "@carebot"
5. Select "Add integration"
6. Copy the API token to your `.env`

After adding the bot, invite it to your Slack channels. You might want to set up
a private channel for testing. (Note that you can't make a channel private
channel public later.)

####  Add Google credentials, including `GOOGLE_OAUTH_CLIENT_ID` and `GOOGLE_OAUTH_CONSUMER_SECRET`:

The first time you run Carebot, you'll need to authorize the app with your
Google account.

First, you'll need to create a Google API project via the [Google developer
console](http://console.developers.google.com). There's a more detailed guide
on the [NPR Apps blog](http://blog.apps.npr.org/2015/03/02/app-template-oauth.html)

Then, enable the Drive and Analytics APIs for your project.

Finally, create a "web application" client ID. For the redirect URIs use:

* `http://localhost:8000/authenticate/`
* `http://127.0.0.1:8000/authenticate`
* `http://localhost:8888/authenticate/`
* `http://127.0.0.1:8888/authenticate`

For the Javascript origins use:

* `http://localhost:8000`
* `http://127.0.0.1:8000`
* `http://localhost:8888`
* `http://127.0.0.1:8888`

Copy the Client ID and Client Secret from the project's Credentials tab to
`GOOGLE_OAUTH_CLIENT_ID` and `GOOGLE_OAUTH_CONSUMER_SECRET` in your `.env` file.

After you have set these up, from the the project root, run:

```
source dev.env
fab app
```

And follow the on-screen instructions. If you have already set up an app using
the [NPR Apps template](https://github.com/nprapps/app-template), you may not
have to do this.

#### NPR API credentials

If you're running this internally at NPR, you'll want a key for the NPR API.
This will be used to pull more details about articles, like primary image and a
more accurate "published at" date.
You can [register for one here](http://www.npr.org/api/index.php).

#### Troubleshooting problems with credentials

* Double check the Google Analytics organization IDs you set in `app_config`
* Test your analytics query in the (Query Explorer](https://ga-dev-tools.appspot.com/query-explorer/)
and make sure you get the results you expect there.
* Review the step-by-step [oauth instructions](http://blog.apps.npr.org/2015/03/02/app-template-oauth.html) on the NPR Visuals Team blog.

### Run the optional screenshot tool

Scroll depth stats use an [optional screenshot tool](https://github.com/thecarebot/screenshotter) to
take snaps of your pages. We've hardcoded in the URL to our service and you can run it on your own if
you prefer. It runs well on Heroku or any other place you can run a Node app. However, it's totally
optional and the bot will function just fine without it.

## Running Carebot

### Run the bot

```
python carebot.py
```

After starting the bot, make sure to invite it to the channel you set in `.env`.

### Configuring Carebot to load new stories

Configure Carebot to pull stores from various sources by customizing the `TEAMS`
and `SOURCES` in `app_config.py`.

Under `TEAMS`, define team names and the channel messages for that team should
post to. Make sure you have a `default` team (it can have the same properties as
another team).

`ga_org_id` should be the ID of the team's Google Analytics account. You can
find the ID you need using the [Analytics API explorer](https://ga-dev-tools.appspot.com/query-explorer/):
select the account, property, and view, then copy the number after `ga:` in
the `ids` field.

Under `SOURCES`, define where content should be pulled from, and what team it
belongs to. There currently are two supported sources:

* `spreadsheet` pulls from a google doc using its `doc_key`
* `rss` pulls from an RSS feed via a `url`. It recognizes many typical feeds.

### Load new stories

This is usually run via a cronjob, but you can fire it manually to test it out:

```
fab carebot.load_new_stories
```

### Get stats on stories

This is usually run via a cronjob after `load_new_stories`, but you can fire it
manually:

```
fab carebot.get_story_stats
```

## Carebot in production

### Server setup

You'll need a couple packages:

* SQLite: `sudo apt-get install sqlite3 libsqlite3-dev`
* `sudo apt-get install libjpeg-dev` for pil
* `sudo apt-get install python-dev` for pycrypto
* `sudo apt-get install libpng-dev` for matplotlib
* `sudo apt-get install libfreetype6-dev libxft-dev` for matplotlib
* Any other basics: python, pip.

If you have trouble running carebot with matplotlib, [this command may help](https://dev.netzob.org/issues/266):

```
echo "backend: TkAgg" > ~/.matplotlib/matplotlibrc
```

### First deploy

Make sure you have a `.env` file with your production keys (see "add
creditials"). Also make sure that you've run the server locally, and logged into Google through the OAuth flow. **Note: although the filename for the token is the same, you cannot use the same creds as you do for Dailygraphics or the app template.** The credential scopes for Carebot are a superset of our other applications--you can use Dailygraphics after logging into Carebot, but not vice versa.

Then, run:

```
fab production setup
```

### Deploying

To deploy carebot to production:

```
fab production deploy
```

### Starting and stoppping

You may occasionally need to stop and start a remote carebot instance:

* `fab staging stop_service:bot`
* `fab staging start_service:bot`

### Debugging deploys

We use `upstart` to keep carebot running on deploys. Sometimes carebot doesn't
start. The debug process is fairly annoying, but here are some things that might
help.

* Logs should be available in `/var/log/upstart/carebot.log`
* Not all errors go there :-/. You might want to try outputting each command in `confs/bot.conf`, eg `...command >> {{ SERVER_PROJECT_PATH }}/log.txt`
* The cron file is `/etc/cron.d/carebot`
* Cron errors might end up in `/var/log/syslog`; check `tail -100 /var/log/syslog`
* By default, cron errors will be in `/var/log/carebot/`

## Developing Carebot

### Tracking your stats with plugins

Are you collecting stats not built into Carebot? Great! You can write plugins to
fetch and share the stats.

Plugins have two functions:

1. Pull stats regularly and announce them to a channel

2. Respond to inquiries ("@carebot, help!")

Here's how to write a new plugin:

#### Use the base class as a reference

The `CarebotPlugin` base class is in `/plugins/base.py`. Extend `CarebotPlugin`
to create a new plugin. You can also copy one of the existing plugins to a new
file.

#### Listen for questions
If you want your plugin to listen for questions sent to Carebot, (for example,
"@carebot, what should I have for lunch?") implement `get_listeners` on your
class. The optional `get_listeners` function should return a list of regular
expressions and  corresponding handler functions that will match and respond to
incoming slack messages. For a simple example, see the `help` plugin.

#### Regularly share stats about articles
Carebot will regularly check every story in the database. If the story has not
been checked recently, the optional `get_update_message` function of each plugin
will be called. You can return a mesage and attachments, for example with the
latest stat for the article. Check the `linger` or `scrolldepth` plugins for
example code.

If you're pulling stats from Google Analytics, the [Query Explorer](https://ga-dev-tools.appspot.com/query-explorer/)
is a helpful way to test your parameters before coding them into Carebot.

#### Enable your plugin

To enable a plugin, list it in two places in `app_config.py`:

1. Add the full path to the list of `CAREBOT_PLUGINS`

2. Add the full path of the plugin to the `plugins` array on the teams you want
to report that stat.

Here's an example:

```
CAREBOT_PLUGINS = (
    'plugins.npr.help.NPRHelp',
    'plugins.npr.linger.NPRLingerRate',
    'plugins.npr.scrolldepth.NPRScrollDepth',
)

TEAMS = {
    'default': {
        'channel': 'visuals-graphics',
        'ga_org_id': '100693289',
        'plugins': [
            'plugins.npr.linger.NPRLingerRate',
            'plugins.npr.scrolldepth.NPRScrollDepth',
        ],
    }
```

### Load your stories into Carebot with scrapers

Carebot regularly runs scrapers to load new stories into its database. You'll
probably have to write or customize a scraper to get Carebot to learn about your
stories.

Scraper code is located in `/scrapers`. We've included an RSS scraper and a
scraper that pulls articles from a Google Spreadsheet. You can copy or customize
these to pull in your stories, or write a new scraper from scratch.

Scrapers are instantiated with the `SOURCES` pulled from `app_config`. All
scrapers should implement a `scrape_and_load` method that returns a list of
stories.

Once you've got a scraper, register it in `/fabfile/carebot.py` in the
`load_new_stories` method.

### Tests

To run tests:

```
nosetests
```

These tests help you make sure that scrapers, plugins, and analytics tools
are running as expected. We highly recommend writing simple tests for your
plugins to make sure they respond correctly.

### The cron file

Carebot loads new stories and checks for stats regularly by running the fabfile
via cron jobs. These are set for staggered 15-minute runs. You can configure
them by editing the `crontab` file.

### Migrations
If you make changes to existing models in `models.py`, you will need to [write
a migration](http://docs.peewee-orm.com/en/latest/peewee/playhouse.html#migrate).

For now, migrations are not automatically run on deploy and may need to be run
manually. Inside the environment, run `python MIGRATION_NAME.py`
