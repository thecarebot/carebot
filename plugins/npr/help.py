import re

from plugins.base import CarebotPlugin
from util.analytics import GoogleAnalytics


class NPRHelp(CarebotPlugin):
    """
    Get scroll depth stats on NPR stories
    """
    HELP_REGEX_1 = re.compile(ur'Help', re.IGNORECASE)
    HELP_REGEX_2 = re.compile(ur'What can you do', re.IGNORECASE)
    HELP_REGEX_3 = re.compile(ur'What are you up to', re.IGNORECASE)

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

Here are the commands you can run:

*Find out more about a slug:*
> @carebot, how is slug red-rackhams-treasure doing?
> @carebot, what about slug tintin-in-tibet?

*Get pageviews for a slug:*
> @carebot, unsuck prisoners-of-the-sun

*Find out more about all graphics on a page:*
> @carebot, how is is http://npr.org/example doing?

*Get an overview of the last week:*
> @carebot hello!

*Start tracking a slug:*
> @carebot track castafiore-emerald on http://npr.org/example

To update a page with another slug, or remove a slug, ask carebot to track it
again:
> @carebot track castafiore-emerald,flight-714 on http://npr.org/example
"""

        return {
            'text': text
        }

