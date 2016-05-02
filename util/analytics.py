from __future__ import division
from datetime import datetime
import logging

import app_config
from oauth import get_credentials
from util.config import Config


logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

config = Config()

class GoogleAnalytics:
    def __init__(self):
        self.run_time = datetime.utcnow()

    @staticmethod
    def query_ga(params):
        api_url = 'https://www.googleapis.com/analytics/v3/data/ga'
        credentials = get_credentials()
        resp = app_config.authomatic.access(credentials, api_url, params=params)
        data = resp.data
        return data

    def get_user_data(self, team, start_date=None):

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

        return self.query_ga(params)


    # based on http://scrolldepth.parsnip.io/ event data
    def get_scroll_depth_depth_data(self, slug=None):
        filters = [
            'ga:pagePath=={}'.format(slug),
            'ga:eventCategory==Scroll Depth',
            'ga:eventAction==Percentage',
        ]

        filters = ';'.join(filters)

        params = {
            'ids': 'ga:{0}'.format(app_config.GA_ORGANIZATION_ID),
            'start-date': '90daysAgo', # start_date.strftime('%Y-%m-%d'),
            'end-date': 'today',
            'metrics': 'ga:users,ga:eventValue',
            'dimensions': 'ga:eventLabel',
            'filters': filters,
            'max-results': app_config.GA_RESULT_SIZE,
            'samplingLevel': app_config.GA_SAMPLING_LEVEL,
            'start-index': 1,
        }

        return self.query_ga(params)


    def get_depth_data(self, team, slug=None):
        if slug:
            filters = 'ga:eventCategory==%s;ga:eventAction==scroll-depth' % slug
        else:
            filters = 'ga:eventAction==scroll-depth'

        params = {
            'ids': 'ga:{0}'.format(team['ga_org_id']),
            'start-date': '90daysAgo', # start_date.strftime('%Y-%m-%d'),
            'end-date': 'today',
            'metrics': 'ga:users,ga:eventValue',
            'dimensions': 'ga:eventLabel',
            'filters': filters,
            'max-results': app_config.GA_RESULT_SIZE,
            'samplingLevel': app_config.GA_SAMPLING_LEVEL,
            'start-index': 1,
        }

        return self.query_ga(params)


    def get_linger_data_for_story(self, story):
        story_slugs = story.slug_list()
        stats_per_slug = []

        team = config.get_team_for_story(story)

        # Get the linger rate for each slug
        for slug in story_slugs:
            stats = self.get_linger_rate(team=team, slug=slug)
            if stats:
                stats_per_slug.append({
                    "slug": slug,
                    "stats": stats
                })

            else:
                logger.info("No stats found for %s" % (slug))

        return stats_per_slug


    """
    Given a list of [percent_depth, total_users, seconds]
    1. Find the max number of total_users
    2. Fill in results before that with that max

    We do this because people with larger screens start on the 20% bucket, or
    30%, and so the 10% bucket number is often smaller than it technically is.
    """
    @staticmethod
    def fill_in_max(data):
        max_people = max(data, key=lambda item:item[1])[1]

        for row in data:
            if row[1] == max_people:
                break

            row[1] = max_people

        return data


    def process_scroll_depth_data(self, data):
        rows = []

        for row in data:
            row[0] = row[0] # Percent depth on page
            row[1] = int(row[1]) # Total users
            row[2] = int(row[2]) # Total number of users that reached depth
            rows.append(row)

        # Sorts the data returned by Scroll Depth
        rows = GoogleAnalyticsScraper.sort_scroll_depth(rows)

        # Calculate the percentage of users
        total_engaged = rows[0][1] # 100% of the users see bucket 1.
        for row in rows:
            pct = round((row[1] / total_engaged) * 100)
            row.append(int(pct))

        truncated = rows[:10]
        return truncated


    def process_depth_data(self, data):
        rows = []
        for row in data:
            row[0] = int(row[0]) # Percent depth on page
            row[1] = int(row[1]) # Total users
            row[2] = int(row[2]) # Seconds on page
            rows.append(row)

        # Sort the row data from 10% => 100%
        rows.sort(key=lambda tup: tup[0])

        row = GoogleAnalyticsScraper.fill_in_max(rows)

        # Calculate the percentage of users
        total_engaged = rows[0][1] # 100% of the users see bucket 1.
        for row in rows:
            pct = round((row[1] / total_engaged) * 100)
            row.append(int(pct))

        truncated = rows[:10]
        return truncated


    def get_depth_rate(self, team, slug=None):
        data = self.get_depth_data(team=team, slug=slug)

        if not data.get('rows'):
            logger.info('No rows found, done.')
            return False

        rows = self.process_scroll_depth_data(data.get('rows'))
        return rows


    # def get_depth_rate_for_story(self, story):
    #     """
    #     Get the scroll depth stats for a story.
    #     Returns a list of stats per slug in the format
    #     [{
    #         slug: my-slug-here,
    #         stats: [
    #             [
    #                 Percent depth on page,
    #                 Total users,
    #                 Seconds on page,
    #                 Percentage of users
    #             ], ...
    #         ]
    #     }, ...]
    #     """
    #     story_slugs = story.slug_list()
    #     stats_per_slug = []
#
    #     team = config.get_team_for_story(story)
#
    #     # Get the linger rate for each slug
    #     for slug in story_slugs:
    #         stats = self.get_depth_rate(team=team, slug=slug)
    #         if stats:
    #             stats_per_slug.append({
    #                 "slug": slug,
    #                 "stats": stats
    #             })
#
    #         else:
    #             logger.info("No stats found for %s" % (slug))
#
    #     return stats_per_slug


    @staticmethod
    def sort_scroll_depth(data):
        """
        A helper function for sorting the results generated by the Scroll Depth
        library.

        Source: http://stackoverflow.com/a/12814719

        """
        source = ('Baseline', '25%', '50%', '75%', '100%',)

        return sorted(data, key=lambda x: source.index(x[0]))
