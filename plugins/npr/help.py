import re

from util.analytics import GoogleAnalytics
from util.config import Config
from plugins.base import CarebotPlugin


class NPRHelp(CarebotPlugin):
    """
    Get scroll depth stats on NPR stories
    """
    HELP_REGEX_1 = re.compile(ur'Help', re.IGNORECASE)
    HELP_REGEX_2 = re.compile(ur'What can you do', re.IGNORECASE)
    HELP_REGEX_3 = re.compile(ur'What are you up to', re.IGNORECASE)

    def __init__(self, *args, **kwargs):
        super(NPRHelp, self).__init__(*args, **kwargs)

    def get_listeners(self):
        return [
            ['help', self.HELP_REGEX_1, self.respond],
            ['help', self.HELP_REGEX_2, self.respond],
            ['help', self.HELP_REGEX_3, self.respond]
        ]

    def respond(self, message):
        text = """I'm currently tracking two measures:
1. *On-screen visibility* of a graphic in a story: how much time a user views a \
graphic on their screen
2. *Scroll depth* across a story: how far down the length of a story a user \
scrolled.

I use those to calculate two indicators:
1. *Graphic Linger Rate*: The median visibility of a graphic across all users \
who viewed it.
2. *Engaged Completion Rate*: Percentage of people who start and complete the \
story.

Lately I have been focusing on graphics-only stories. I start tracking a story \
when it is published. I start posting notifications when someone \
adds the story to an RSS feed or story spreadsheet. You'll hear from me every \
4 hours on the first day and twice daily for days two and and three.

If you ask me about a specific graphic, I'll give you the most up to date \
Graphic Linger Rate distribution for the graphic in a nifty histogram. I'll also show \
how the story that graphic is in is comparing to all other graphic stories overall. \
Just mention me with the word "slug" followed by your slug:

> @carebot, how is slug red-rackhams-treasure doing?
> @carebot, what about slug tintin-in-tibet?

I am learning to answer questions so if you have them, please send them over and \
I'll get cracking!
"""
        return text
        #     slackTools.send_message(message.body['channel'], text)

