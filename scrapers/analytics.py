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

    def get_linger_rate(self, slug):
        rows = []

        api_url = 'https://www.googleapis.com/analytics/v3/data/ga'
        credentials = get_credentials()

        filters = 'ga:eventCategory==%s;ga:eventAction==on-screen;ga:eventLabel==10s,ga:eventLabel==20s,ga:eventLabel==30s,ga:eventLabel==40s,ga:eventLabel==50s,ga:eventLabel==1m,ga:eventLabel==2m,ga:eventLabel==3m,ga:eventLabel==4m,ga:eventLabel==5m,ga:eventLabel==10m' % slug
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

        resp = app_config.authomatic.access(credentials, api_url, params=params)
        data = resp.data

        logger.info('Processing rows {0} - {1}'.format(params['start-index'], params['start-index'] + app_config.GA_RESULT_SIZE - 1))

        if not data.get('rows'):
            logger.info('No rows found, done.')
            return False

        for row in resp.data['rows']:
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

        # Get the average number of seconds
        total_seconds = 0
        total_people = 0
        for row in rows:
            total_seconds = total_seconds + (row[0] * row[1])
            total_people = total_people + row[1]

        average_seconds = total_seconds/total_people
        minutes = average_seconds / 60
        seconds = average_seconds % 60

        return {
            'total_people': total_people,
            'minutes': minutes,
            'seconds': seconds
        }

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

        logger.info('Processing rows {0} - {1}'.format(params['start-index'], params['start-index'] + app_config.GA_RESULT_SIZE - 1))

        if not data.get('rows'):
            logger.info('No rows found, done.')

        for row in resp.data['rows']:
            print(row)
            rows.append(row)

            # for row in resp.data['rows']:
            #     analytics_row = GoogleAnalyticsRow(row, app_config.GA_METRICS, app_config.GA_DIMENSIONS, data)
            #     rows.append(analytics_row.serialize())
#
            # params['start-index'] += app_config.GA_RESULT_SIZE

        #import ipdb; ipdb.set_trace();
        return rows

    # def write(self, db, rows):
    #     table = db['google_analytics']
    #     table.delete()
    #     table.insert_many(rows)