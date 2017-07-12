import importlib
import logging
import re
from slackbot.bot import Bot
from slackbot.bot import respond_to
from slackbot.bot import listen_to
import sys

import app_config
from util.slack import SlackTools

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
slack_tools = SlackTools()

"""
Go through the plugins and add any listeners we need
"""
listeners = []
plugins = [getattr(importlib.import_module(mod), cls) for (mod, cls) in (plugin.rsplit(".", 1) for plugin in app_config.CAREBOT_PLUGINS)]
for plugin in plugins:
    plugin = plugin()
    try:
        listeners.extend(plugin.get_listeners())
    except NotImplementedError:
        pass

@respond_to('.*', re.IGNORECASE)
def response_dispatcher(message, text=None):
    """
    We start out responding to everything -- there doesn't seem to be a way for a
    more specific regex to take precedence over the generic case.
    """
    if not text:
        text = message.body['text']

    any_match = False
    for listener in listeners:
        match = listener[1].findall(text)
        if match:
            logger.info("Recognized message: %s", message.body['text'])
            logger.info("Dispatching to message: %s", listener[0])
            any_match = True

            # Some listeners have a first message that says "hold tight, stats
            # are coming soon":
            try:
                slack_tools.send_message(
                    message.body['channel'],
                    listener[3](),
                    None,
                    unfurl_links=False,
                )
            except:
                pass

            # Get the reply
            reply = listener[2](message)

            if reply:
                slack_tools.send_message(
                    message.body['channel'],
                    reply['text'],
                    reply.get('attachments', None),
                    unfurl_links=False,
                )

    if not any_match:
        logger.info("Did not recognize message: {0}".format(message.body['text']))
        message.reply("Hi! I got your message, but I don't know enough yet to respond to it.")


@listen_to('^@*test-[Cc]arebot[:|,]\s*(.*)', re.IGNORECASE)
def reply(message, text):
    """
    Listen passively for any mention of Carebot: at the beginning of the line
    If we don't listen to this generic message, users would have to use exact
    syntax to get a response out of carebot.
    """
    response_dispatcher(message, text)


def main():
    bot = Bot()
    print "Carebot is running. Invite it to a channel to begin."
    bot.run()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print "Thanks for caring! See you next time."
        sys.exit()
