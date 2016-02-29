import datetime
from slacker import Slacker

import app_config

"""
Right now, Slacker offers a full range of slack tools
But slackbot is much better at listening to things.
We want both!
We'll probably do somethign to join them up here.
"""
class SlackTools:
    slack = Slacker(app_config.slack_key)

    def hours_since(self, a):
        now = datetime.datetime.now()
        seconds = (now - a).total_seconds()

        hours = int(seconds / 60 / 60)
        return hours

    def send_message(self, channel, message):
        self.slack.chat.post_message(channel, message, as_user=True, parse='full')

    def send_tracking_started_message(self, story):
        message = ("I've just started tracking %s. The first update should appear in an hour. %s") % (
            story.name,
            story.url
        )

        logger.info(message)

        self.send_message(app_config.LINGER_UPDATE_CHANNEL, message)


    def send_linger_time_update(self, story, linger, time_bucket):
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

        logger.info(message)
        self.send_message(app_config.LINGER_UPDATE_CHANNEL, message)
