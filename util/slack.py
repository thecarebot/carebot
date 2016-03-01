import datetime
from dateutil.parser import parse
import logging
import pytz
from slacker import Slacker

import app_config

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
    slack = Slacker(app_config.slack_key)

    def hours_since(self, a):
        # For some reason, dates with timezones tend to be returned as unicode
        if type(a) is not datetime.datetime:
            a = parse(a)

        now = datetime.datetime.now(pytz.timezone('US/Eastern'))
        seconds = (now - a).total_seconds()

        hours = int(seconds / 60 / 60)
        return hours

    def send_message(self, channel, message):
        self.slack.chat.post_message(channel, message, as_user=True, parse='full')

    def send_tracking_started_message(self, story):
        attachments = [
            {
                "fallback": "I just started tracking " + story.name,
                "color": "good",
                "pretext": "I just started tracking:",
                "title": story.name,
                "text": "Published " + story.article_posted.strftime('%B %d, %Y at %I:%M %p'),
                "title_link": story.url,
                "image_url": story.image
            }
        ]

        self.slack.chat.post_message(app_config.LINGER_UPDATE_CHANNEL, "", as_user=True, attachments=attachments)
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

    def send_linger_time_update(self, story, stats_per_slug, time_bucket):
        if not stats_per_slug[0]:
            return

        time = self.humanist_time_bucket(stats_per_slug[0]['stats'])
        hours_since = self.hours_since(story.article_posted)

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

        if time_bucket == 'hour 8':
            message = ("%s hours in and _%s_ had users spending about *%s* "
                "interacting with the graphic.") % (
                hours_since,
                story.name,
                time
            )

        if time_bucket == 'hour 12':
            message = ("So far, users have spent an average of *%s* viewing the "
                "graphic on _%s_.") % (
                time,
                story.name
            )

        if time_bucket == 'day 1 hour 10':
            message = ("It's been %s hours since publishing _%s_ and users have"
                " spent, on average, *%s* studying the graphic.") % (
                hours_since,
                story.name,
                time
            )

        if time_bucket == 'day 1 hour 15':
            message = ("_%s_ has had users study the graphic for *%s*, on average.") % (
                story.name,
                time
            )

        if time_bucket == 'day 2 hour 10':
            message = ("After 2 days, _%s_ users have spent, on average, *%s* "
                "studying the graphic.") % (
                story.name,
                time
                )

        if time_bucket == 'day 2 hour 15':
            message = ("_%s_ users have viewed the graphic for *%s*, on average."
                "\n\n"
                "I'll keep tracking _%s_ but won't ping you again with updates."
                " Let me know if this has been useful. <3") % (
                story.name,
                time,
                story.name
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

        logger.info(message)
        self.slack.chat.post_message(app_config.LINGER_UPDATE_CHANNEL, message, as_user=True, parse='full', attachments=attachments)
