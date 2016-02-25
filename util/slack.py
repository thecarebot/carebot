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

    def send_tracking_started_message(self, story):
        message = ("I've just started tracking %s. The first update should appear in an hour. %s") % (
            story.name,
            story.url
        )

        print message

        self.send_message(app_config.LINGER_UPDATE_CHANNEL, message)


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

        hours_since = self.hours_since(story.date)

        if hours_since < 5:
            hours_since_message = str(hours_since) + ' hour'
            if hours_since > 1:
                hours_since_message += 's'

            # "It's been just..."
            if hours_since < 5:
                hours_since_message = 'just ' + hours_since_message

            message = ("It's been %s since I started tracking _%s_ and users have "
                "spent, on average, *%s* studying the graphic.") % (
                hours_since_message,
                story.name,
                time
            )

        if hours_since >= 5 and hours_since <= 8:
            message = ("%s hours in and _%s_ had users spending about *%s* "
                "interacting with the graphic.") % (
                hours_since,
                story.name,
                time
            )

        if hours_since > 8 and hours_since < 12:
            message = ("So far, users have spent an average of *%s* viewing the "
                "graphic on _%s_.") % (
                time,
                story.name
            )

        if hours_since >= 12 and hours_since <= 18:
            message = ("It's been %s hours since publishing _%s_ and users have"
                " spent, on average, *%s* studying the graphic.") % (
                hours_since,
                story.name,
                time
            )

        if hours_since > 18 and hours_since < 24:
            message = ("_%s_ has had users study the graphic for *%s*, on average.") % (
                story.name,
                time
            )

        if hours_since > 24 and hours_since <= 36:
            message = ("After 2 days, _%s_ users have spent, on average, *%s* "
                "studying the graphic.") % (
                story.name,
                time
                )

        if hours_since > 36:
            message = ("_%s_ users have viewed the graphic for *%s*, on average."
                "\n\n"
                "I'll keep tracking _%s_ but won't ping you again with updates."
                " Let me know if this has been useful. <3") % (
                story.name,
                time,
                story.name
            )

        # TODO:
        # 8 hours in and _story_title_

        # Longer:
        # So far, users have spent an average of *time* viewing
        # the graphic on _story title_

        # It's been 18 hours since publishing _story title_ and
        # users have spent an average *time* studying the graphic

        # _story title_ has had users study the graphic for *time*,
        # on average.

        # After x days, _story title_ have spent, on average,
        # *time* interacting with the graphic
        #
        #  _story title_ users have iewed the graphic for *time*,
        #  on average.

        print message

        self.send_message(app_config.LINGER_UPDATE_CHANNEL, message)
