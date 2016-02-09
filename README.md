# Carebot: The Slackbot

## Bootstrapping

Work on a virtualenvironment:

```
mkvirtualenv carebot --no-site-packages
workon carebot
```

Install the dependencies:

```
pip install -r requirements.txt
```

## Running Carebot

The bot requires a `SLACKBOT_API_TOKEN` environment variable.
You can set that from the command line by running:

```
export SLACKBOT_API_TOKEN=foo
```

To run carebot the bot:

```
python carebot.py
```
