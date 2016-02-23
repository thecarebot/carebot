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

    def scrape_google_analytics(self):
        rows = []

        api_url = 'https://www.googleapis.com/analytics/v3/data/ga'
        credentials = get_credentials()

        metrics = ','.join(['ga:{0}'.format(metric) for metric in app_config.GA_METRICS])
        dimensions = ','.join(['ga:{0}'.format(dimensions) for dimensions in app_config.GA_DIMENSIONS])

        params = {
            'ids': 'ga:{0}'.format(app_config.GA_ORGANIZATION_ID),
            'end-date': 'yesterday',
            'start-date': '30daysAgo', # start_date.strftime('%Y-%m-%d'),
            'metrics': 'ga:sessions,ga:pageviews',
            'dimensions': 'ga:pagePath,ga:source,ga:deviceCategory',
            'max-results': app_config.GA_RESULT_SIZE,
            'samplingLevel': app_config.GA_SAMPLING_LEVEL,
            'start-index': 1,
        }

        while True:
            resp = app_config.authomatic.access(credentials, api_url, params=params)
            data = resp.data

            logger.info('Processing rows {0} - {1}'.format(params['start-index'], params['start-index'] + app_config.GA_RESULT_SIZE - 1))

            if not data.get('rows'):
                logger.info('No rows found, done.')
                break

            for row in resp.data['rows']:
                analytics_row = GoogleAnalyticsRow(row, app_config.GA_METRICS, app_config.GA_DIMENSIONS, data)
                rows.append(analytics_row.serialize())

            params['start-index'] += app_config.GA_RESULT_SIZE

        #import ipdb; ipdb.set_trace();
        return rows

    # def write(self, db, rows):
    #     table = db['google_analytics']
    #     table.delete()
    #     table.insert_many(rows)
