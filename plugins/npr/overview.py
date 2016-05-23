import datetime
import re
from sets import Set

import app_config
from util.models import Story
from plugins.base import CarebotPlugin
from plugins.npr.linger import NPRLingerRate
from util.analytics import GoogleAnalytics

class NPROverview(CarebotPlugin):
    """
    Get an overview of what's been happening in the last week
    """
    HELLO_REGEX = re.compile(ur'Hello', re.IGNORECASE)

    def get_listeners(self):
        return [
            ['help', self.HELLO_REGEX, self.respond, self.get_wait_message],
        ]

    def get_wait_message(self):
        return "I'm getting stats for the last week. This will take a minute."

    def get_user_data(self, team, start_date=None):
        """
        Get the number of users in the last seven days
        """
        if not start_date:
            start_date = '90daysAgo'

        params = {
            'ids': 'ga:{0}'.format(team['ga_org_id']),
            'start-date': start_date, # start_date.strftime('%Y-%m-%d'),
            'end-date': 'today',
            'metrics': 'ga:users',
            # 'dimensions': 'ga:eventLabel',
            # 'filters': filters,
            'max-results': app_config.GA_RESULT_SIZE,
            'samplingLevel': app_config.GA_SAMPLING_LEVEL,
            'start-index': 1,
        }

        return GoogleAnalytics.query_ga(params)

    def respond(self, message):
        """
        Respond to requests about the last seven days of data
        TODO: Loop over all stories and report stats on each
        """
        seven_days_ago = datetime.datetime.now() - datetime.timedelta(days=7)
        stories = Story.select().where(Story.tracking_started > seven_days_ago)

        slugs = Set()
        for story in stories:
            print story.name
            story_slugs = story.slug.split(',')
            for slug in story_slugs:
                slugs.add(slug)

        try:
            team = self.config.get_team_for_story(stories[0])
        except:
            team = self.config.get_default_team()

        total_users = self.get_user_data(team=team, start_date='7daysAgo')
        total_users = int(total_users['rows'][0][0])
        total_users = "{:,}".format(total_users)

        npr_linger = NPRLingerRate()
        linger_rows = npr_linger.get_linger_data(team=team, start_date='7daysAgo')
        median = NPRLingerRate.get_median(linger_rows)
        linger_histogram_url = npr_linger.get_histogram_url(linger_rows, median)

        attachments = [{
            "fallback": "linger update",
            "color": "#eeeeee",
            "title": "Time spent on graphics over the last week",
            "image_url": linger_histogram_url
        }]

        text = "In the past 7 days, I've tracked {0} stories and {1} graphics.".format(len(stories), len(slugs))
        text += "\n\n"
        text += "{0} people looked at graphics on the property. Here's how much time they spent:".format(total_users)

        fields = []
        for story in stories:
            fields.append({
                "title": story.name.strip(),
                "value": "<{0}|{1}>".format(story.url, story.slug.strip()),
                "short": True
            })

        attachments.append({
            "fallback": "linger update",
            "color": "#eeeeee",
            # "title": "What we have done",
            "fields": fields
        })

        return {
            'text': text,
            'attachments': attachments
        }

