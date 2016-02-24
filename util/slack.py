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

        # Convert any dates to datetime
        # (yes yes imprecise & hacky)
        if type(a) is datetime.date:
            a = datetime.datetime.combine(a, datetime.datetime.min.time())

        hours = int((now - a).total_seconds() % 60)
        print hours
        return hours

    def send_message(self, channel, message):
        self.slack.chat.post_message(channel, message, as_user=True, parse='full')

    def send_linger_time_update(self, story, linger):
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

        message = ("It's been %s hours since I started tracking _%s_ and users have "
            "spent on average *%s* studying the graphic: %s") % (
            self.hours_since(story.date),
            story.name,
            time,
            story.url
        )

        print message

        self.send_message(app_config.LINGER_UPDATE_CHANNEL, message)
