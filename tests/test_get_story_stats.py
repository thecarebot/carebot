#!/usr/bin/env python
# http://stackoverflow.com/questions/10277397/python-mock-patch-a-function-within-another-function

import app_config
app_config.DATABASE_NAME = 'carebot_test.db'
app_config.DEFAULT_CONFIG_PATH = 'tests/config_test.yml'

try:
    import unittest2 as unittest
except ImportError:
    import unittest

from datetime import date
from mock import patch
from mock import ANY

from fabfile import get_story_stats
from scrapers.spreadsheet import SpreadsheetScraper
from util.models import Story
from tests.test_util.db import clear_stories


class TestGetStoryStats(unittest.TestCase):

    @patch('scrapers.analytics.GoogleAnalyticsScraper.get_linger_data_for_story')
    @patch('util.slack.SlackTools.send_linger_time_update')
    @patch('util.s3.Uploader.upload')
    @patch('fabfile.time_bucket')
    def test_get_story_stats(self,
                             mock_time_bucket,
                             mock_upload,
                             mock_update,
                             mock_linger,
                            ):

        # Set some fake analytics
        linger_data = [{
            'slug': 'slug-here',
            'stats': {
                'total_people': 100,
                'raw_avg_seconds': 330,
                'minutes': 5,
                'seconds': 30
            }
        }]
        mock_upload.return_value = 'http://image-url-here'
        mock_linger.return_value = linger_data
        mock_time_bucket.return_value = 'time bucket'


        # Load a fake story
        clear_stories()
        scraper = SpreadsheetScraper()
        stories = scraper.scrape_spreadsheet('tests/data/stories.xlsx')
        stories = scraper.write([stories[0]])

        get_story_stats()

        # Check the updater
        mock_update.assert_called_once_with(stories[0], linger_data, 'time bucket')

