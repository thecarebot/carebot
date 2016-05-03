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

    def humanist_time_bucket(self, linger):
        time = ''
        if linger['minutes'] > 0:
            time += str(linger['minutes'])
            if linger['minutes'] == 1:
                time += ' minute'
            else:
                time += ' minutes'

        if linger['seconds'] > 0:
            if linger['minutes'] > 0:
                time += ' '

            time += str(linger['seconds'])
            if linger['seconds'] == 1:
                time += ' second'
            else:
                time += ' seconds'

        return time

    def send_scroll_depth_update(self, story, data, time_bucket):
        channel = story.channel()

        message = ("%s hours in and here's what I know about the graphics on _%s_:") % (
            self.hours_since(story.date),
            story.name,
        )

        # remove `Baseline` from data
        data = data[1:]

        histogram_url = ChartTools.scroll_histogram_link(data, labels=(
            '100%', '75%', '50%', '25%',))

        if story.screenshot:
            histogram_url = ChartTools.add_screenshot_to_chart(
                story.screenshot, histogram_url)

        fields = []

        for row in data:
            fields.append({
                "title": row[0],
                "value": row[2],
                "short": True,
            })

        attachments = [
            {
                "fallback": story.name + " update",
                "color": "#eeeeee",
                "title": story.name,
                "title_link": story.url,
                "fields": fields,
                "image_url": histogram_url,
            }
        ]

        self.slack.chat.post_message(
            channel, message, as_user=True, parse='full',
            attachments=attachments)
