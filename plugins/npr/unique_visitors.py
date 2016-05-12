import logging
import re

import app_config
from plugins.base import CarebotPlugin
from util.analytics import GoogleAnalytics
from util.config import Config
from util.models import Story
from util.slack import SlackTools

config = Config()
slack_tools = SlackTools()

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class NPRUniqueVisitors(CarebotPlugin):
    UNSUCK_SLUG_SEARCH_REGEX = re.compile(ur'unsuck ((\w*-*)+)')

    # def __init__(self, *args, **kwargs):
        # super(NPRUniqueVisitors, self).__init__(*args, **kwargs)

    def get_query_params(self, team, slug=None, start_date=None):
        """
        Set up the Google Analytics query parameters for the linger rate stat
        """
        filters = 'ga:'

        if slug:
            filters = ('ga:eventCategory==%s;' % slug) + filters

        if not start_date:
            start_date = '90daysAgo'

        params = {
            'ids': 'ga:{0}'.format(team['ga_org_id']),
            'start-date': start_date, # start_date.strftime('%Y-%m-%d'),
            'end-date': 'today',
            'metrics': 'ga:uniquePageviews',
            'filters': 'ga:pagePath=@{0}'.format(slug),
            'max-results': app_config.GA_RESULT_SIZE,
            'samplingLevel': app_config.GA_SAMPLING_LEVEL,
            'start-index': 1,
        }

        return params

    def get_unique_visitor_data(self, team, slug):
        params = self.get_query_params(team=team, slug=slug)
        data = GoogleAnalytics.query_ga(params)
        # import pdb; pdb.set_trace();

        if not data.get('rows'):
            logger.info('No rows found, done.')
            return False

        return data.get('rows')[0][0]

    def handle_pageviews_inquiry(self, message):
        match = re.search(self.UNSUCK_SLUG_SEARCH_REGEX, message.body['text'])
        slug = match.group(1)

        stories = Story.select().where(Story.slug.contains(slug))
        team = config.get_team_for_stories(stories)

        unique_pageviews = self.get_unique_visitor_data(team=team, slug=slug)
        unique_pageviews = int(unique_pageviews)
        unique_pageviews = "{:,}".format(unique_pageviews)

        if not unique_pageviews:
            return {
                'text': "Sorry, I wasn't able to find unique visitor stats for %s" % slug
            }

        return {
            'text': '`{0}` has had *{1}* unique pageviews'.format(slug, unique_pageviews)
        }

    def get_listeners(self):
        return [
            ['unique_pageviews', self.UNSUCK_SLUG_SEARCH_REGEX, self.handle_pageviews_inquiry]
        ]
