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

class GoogleAnalyticsScraper:
    def __init__(self):
        self.run_time = datetime.utcnow()

    @staticmethod
    def median(lst):
        sorted_lst = sorted(lst)
        list_len = len(lst)
        index = (list_len - 1) // 2

        if list_len % 2:
            return sorted_lst[index]
        else:
            return (sorted_lst[index] + sorted_lst[index + 1])/2.0

    @staticmethod
    def median_of_time_buckets(time_buckets):
        lst = []

        # Flatten the [seconds, count] tuples
        # This is a really bad way to do this!
        # Yuuuuge number of objects created!
        # TODO: calculate bucket quickly :-)
        for bucket in time_buckets:
            for _ in range(bucket[1]):
                lst.append(bucket[0])

        median = GoogleAnalyticsScraper.median(lst)
        return int(median)

    def query_ga(self, params):
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

    def get_linger_data(self, team, slug=None, start_date=None):
        if slug:
            filters = 'ga:eventCategory==%s;ga:eventAction==on-screen;ga:eventLabel==10s,ga:eventLabel==20s,ga:eventLabel==30s,ga:eventLabel==40s,ga:eventLabel==50s,ga:eventLabel==1m,ga:eventLabel==2m,ga:eventLabel==3m,ga:eventLabel==4m,ga:eventLabel==5m,ga:eventLabel==10m' % slug
        else:
            filters = 'ga:eventAction==on-screen;ga:eventLabel==10s,ga:eventLabel==20s,ga:eventLabel==30s,ga:eventLabel==40s,ga:eventLabel==50s,ga:eventLabel==1m,ga:eventLabel==2m,ga:eventLabel==3m,ga:eventLabel==4m,ga:eventLabel==5m,ga:eventLabel==10m'

        if not start_date:
            start_date = '90daysAgo'

        params = {
            'ids': 'ga:{0}'.format(team['ga_org_id']),
            'start-date': start_date, # start_date.strftime('%Y-%m-%d'),
            'end-date': 'today',
            'metrics': 'ga:totalEvents',
            'dimensions': 'ga:eventLabel',
            'sort': '-ga:totalEvents',
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

    def linger_data_to_rows(self, data):
        rows = []
        for row in data['rows']:
            time = row[0]
            seconds = 0
            if 'm' in time:
                time = time[:-1] # remove 'm' from the end
                seconds = int(time) * 60
            else:
                time = time[:-1] # remove 's'
                seconds = int(time)

            row[0] = seconds
            row[1] = int(row[1])
            rows.append(row)

        # Calculate the number of visitors in each bucket
        for index, row in enumerate(rows):
            if index == len(rows) - 1:
                continue

            next_row = rows[index + 1]
            row[1] = row[1] - next_row[-1]

        # Exclude everybody in the last bucket
        # (they've been lingering for way too long -- 10+ minutes)
        rows = rows[:-1]
        return rows

    def get_linger_rate(self, team, slug=None, start_date=None):
        if slug:
            data = self.get_linger_data(team=team, slug=slug, start_date=start_date)
        else:
            data = self.get_linger_data(team=team, start_date=start_date)

        if not data.get('rows'):
            logger.info('No rows found, done.')
            return False

        rows = self.linger_data_to_rows(data)

        # Get the average number of seconds
        total_seconds = 0
        total_people = 0
        for row in rows:
            total_seconds = total_seconds + (row[0] * row[1])
            total_people = total_people + row[1]
        # average_seconds = total_seconds/total_people

        average_seconds = self.median_of_time_buckets(rows)
        minutes = int(average_seconds / 60)
        seconds = average_seconds % 60

        return {
            'total_people': total_people,
            'raw_avg_seconds': average_seconds,
            'minutes': minutes,
            'seconds': seconds
        }

    def get_linger_rows(self, team, slug=None, start_date=None):
        if slug:
            data = self.get_linger_data(team=team, slug=slug, start_date=start_date)
        else:
            data = self.get_linger_data(team=team, start_date=start_date)

        if not data.get('rows'):
            logger.info('No rows found, done.')
            return False

        rows = self.linger_data_to_rows(data)
        return rows

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

    def get_depth_rate_for_story(self, story):
        """
        Get the scroll depth stats for a story.
        Returns a list of stats per slug in the format
        [{
            slug: my-slug-here,
            stats: [
                [
                    Percent depth on page,
                    Total users,
                    Seconds on page,
                    Percentage of users
                ], ...
            ]
        }, ...]
        """
        story_slugs = story.slug_list()
        stats_per_slug = []

        team = config.get_team_for_story(story)

        # Get the linger rate for each slug
        for slug in story_slugs:
            stats = self.get_depth_rate(team=team, slug=slug)
            if stats:
                stats_per_slug.append({
                    "slug": slug,
                    "stats": stats
                })

            else:
                logger.info("No stats found for %s" % (slug))

        return stats_per_slug

    @staticmethod
    def sort_scroll_depth(data):
        """
        A helper function for sorting the results generated by the Scroll Depth
        library.

        Source: http://stackoverflow.com/a/12814719

        """
        source = ('Baseline', '25%', '50%', '75%', '100%',)

        return sorted(data, key=lambda x: source.index(x[0]))
