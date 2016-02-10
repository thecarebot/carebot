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

To run the bot:

```
python carebot.py
```

## Analytics setup

Using analytics requires a client ID and secret in client_secrets.json. Instructions on getting those are available here:
https://developers.google.com/analytics/devguides/reporting/core/v3/quickstart/service-py#clientId

Sample analytics code:
https://github.com/google/google-api-python-client/tree/master/samples/analytics
