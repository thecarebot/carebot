import datetime
from dateutil.parser import parse
import logging
import pytz
from slacker import Slacker
import app_config

from util.chart import ChartTools

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

"""
Right now, Slacker offers a full range of slack tools
But slackbot is much better at listening to things.
We want both!
We'll probably do somethign to join them up here.
"""
class SlackTools:
    slack = Slacker(app_config.SLACK_KEY)

    def send_message(self, channel, message, attachments=None, unfurl_links=True):
        if attachments:
            self.slack.chat.post_message(channel,
                                         message,
                                         as_user=True,
                                         attachments=attachments,
                                         unfurl_links=unfurl_links
                                        )

        else:
            self.slack.chat.post_message(channel, message, as_user=True, unfurl_links=unfurl_links)

    def get_channel_name(self, channel_id):
        """
        Given a Channel ID, get the name of the channel from the Slack API
        """
        try:
            results = self.slack.channels.info(channel_id)
            results['name']
        except:
            logger.error("Channel %s not found" % channel_id)
            return None

    def send_tracking_started_message(self, story):
        if not story.date:
            logger.error("No start date for %s; not announcing." % story.name)
            return

        attachments = [
            {
                "fallback": "I just started tracking " + story.name,
                "color": "good",
                "pretext": "I just started tracking:",
                "title": story.name,
                "text": "Published " + story.date.strftime('%B %d, %Y at %I:%M %p'),
                "title_link": story.url,
                "image_url": story.image
            }
        ]
        channel = story.channel()
        self.slack.chat.post_message(channel, "", as_user=True, attachments=attachments)
        logger.info("Started tracking %s with image %s" % (story.name, story.image))

