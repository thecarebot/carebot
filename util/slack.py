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

    def hours_since(self, a):
        # For some reason, dates with timezones tend to be returned as unicode
        if type(a) is not datetime.datetime:
            a = parse(a)

        now = datetime.datetime.now(pytz.timezone(app_config.PROJECT_TIMEZONE))
        seconds = (now - a).total_seconds()

        hours = int(seconds / 60 / 60)
        return hours

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

    def get_truncated_name(self, name):
        parts = name.split(' ')
        short_name = ' '.join(parts[:5])
        if len(parts) > 5:
            short_name += '...'

        return short_name

    def get_linger_time_message_and_attachment(self, story, stats_per_slug, time_bucket):
        time = self.humanist_time_bucket(stats_per_slug[0]['stats'])
        hours_since = self.hours_since(story.date)

        if time_bucket == 'hour 4':
            hours_since_message = str(hours_since) + ' hour'
            if hours_since > 1:
                hours_since_message += 's'

            hours_since_message = 'just ' + hours_since_message

            message = ("It's been %s since I started tracking _%s_ and users have "
                "spent, on average, *%s* studying the graphic.") % (
                hours_since_message,
                story.name,
                time
            )

        if time_bucket == 'Two and a half days':
            message = ("%s in, users viewed the graphic on _%s_ for an average *%s*."
                "\n\n"
                "I'll keep tracking this story but won't ping you again with updates.") % (
                hours_since,
                story.name,
                time
            )

        else:
            message = ("%s in, users viewed the graphic on _%s_ for an average *%s*.") % (
                hours_since,
                story.name,
                time,
            )


        attachments = None
        if len(stats_per_slug) > 1:
            # Use a generic message for now
            message = ("%s hours in and here's what I know about the graphics on _%s_:") % (
                hours_since,
                story.name
            )

            fields = []
            for stat in stats_per_slug:
                time = self.humanist_time_bucket(stat['stats'])
                fields.append({
                    "title": stat['slug'],
                    "value": time,
                    "short": True
                })

            attachments = [
                {
                    "fallback": story.name + " update",
                    "color": "#eeeeee",
                    "title": story.name,
                    "title_link": story.url,
                    "fields": fields
                }
            ]

        return (message, attachments)

    def send_linger_time_update(self, story, stats_per_slug, time_bucket):
        if not stats_per_slug[0]:
            return

        composed = self.get_linger_time_message_and_attachment(story, stats_per_slug, time_bucket)
        message = composed[0]
        attachments = composed[1]

        channel = story.channel()

        logger.info(message)
        self.slack.chat.post_message(channel, message, as_user=True, parse='full', attachments=attachments)

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
