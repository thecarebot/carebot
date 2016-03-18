import app_config

from datetime import datetime
from oauth import get_credentials

import logging

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

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

    def get_linger_data(self, slug=None):
        if slug:
            filters = 'ga:eventCategory==%s;ga:eventAction==on-screen;ga:eventLabel==10s,ga:eventLabel==20s,ga:eventLabel==30s,ga:eventLabel==40s,ga:eventLabel==50s,ga:eventLabel==1m,ga:eventLabel==2m,ga:eventLabel==3m,ga:eventLabel==4m,ga:eventLabel==5m,ga:eventLabel==10m' % slug
        else:
            filters = 'ga:eventAction==on-screen;ga:eventLabel==10s,ga:eventLabel==20s,ga:eventLabel==30s,ga:eventLabel==40s,ga:eventLabel==50s,ga:eventLabel==1m,ga:eventLabel==2m,ga:eventLabel==3m,ga:eventLabel==4m,ga:eventLabel==5m,ga:eventLabel==10m'

        params = {
            'ids': 'ga:{0}'.format(app_config.GA_ORGANIZATION_ID),
            'start-date': '90daysAgo', # start_date.strftime('%Y-%m-%d'),
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

        # Get the linger rate for each slug
        for slug in story_slugs:
            stats = self.get_linger_rate(slug)
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


    def get_linger_rate(self, slug=None):
        if slug:
            data = self.get_linger_data(slug)
        else:
            data = self.get_linger_data()

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
        minutes = average_seconds / 60
        seconds = average_seconds % 60

        return {
            'total_people': total_people,
            'raw_avg_seconds': average_seconds,
            'minutes': minutes,
            'seconds': seconds
        }

    def get_linger_rows(self, slug=None):
        if slug:
            data = self.get_linger_data(slug)
        else:
            data = self.get_linger_data()

        if not data.get('rows'):
            logger.info('No rows found, done.')
            return False

        rows = self.linger_data_to_rows(data)
        return rows

    def autodiscover_stories(self):
        rows = []

        api_url = 'https://www.googleapis.com/analytics/v3/data/ga'
        credentials = get_credentials()

        params = {
            'ids': 'ga:{0}'.format(app_config.GA_ORGANIZATION_ID),
            'start-date': '5daysAgo', # start_date.strftime('%Y-%m-%d'),
            'end-date': 'today',
            'metrics': 'ga:totalEvents',
            'dimensions': 'ga:eventCategory',
            'max-results': app_config.GA_RESULT_SIZE,
            'samplingLevel': app_config.GA_SAMPLING_LEVEL,
            'start-index': 1,
        }

        resp = app_config.authomatic.access(credentials, api_url, params=params)
        data = resp.data

        if not data.get('rows'):
            logger.info('No rows found, done.')

        for row in resp.data['rows']:
            rows.append(row)

        return rows
