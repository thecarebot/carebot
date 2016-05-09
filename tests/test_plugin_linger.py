#!/usr/bin/env python

import datetime
try:
    import unittest2 as unittest
except ImportError:
    import unittest

from mock import patch
from mock import ANY

import app_config
app_config.DATABASE_NAME = 'carebot_test.db'

from plugins.npr.linger import NPRLingerRate
from util.config import Config
from util.models import Story
from tests.test_util.db import clear_stories

class TestAnalytics(unittest.TestCase):
    def test_median_of_time_buckets(self):
        test_data = [
            [1, 10],
            [2, 20],
            [3, 10]
        ]
        median = NPRLingerRate.median_of_time_buckets(test_data)
        self.assertEqual(median, 2)

    def test_get_median(self):
        test_data = [
            [60, 25],
            [90, 50],
            [120, 25],
        ]
        median = NPRLingerRate.get_median(test_data)
        self.assertEqual(median['total_people'], 100)
        self.assertEqual(median['raw_avg_seconds'], 90)
        self.assertEqual(median['minutes'], 1)
        self.assertEqual(median['seconds'], 30)

    @patch('plugins.npr.linger.NPRLingerRate.get_linger_data')
    @patch('util.s3.Uploader.upload')
    def test_handle_slug_inquiry(self,
                                 mock_upload,
                                 mock_linger,
                                ):

        # Set some fake analytics
        linger_data = [
            [10, 10],
            [20, 10],
            [30, 10],
            [40, 10],
            [50, 10],
            [60, 10],
            [120, 10],
            [180, 10],
            [240, 10],
            [300, 10],
        ]
        mock_linger.return_value = linger_data
        mock_upload.return_value = 'http://image-url-here'

        slug = 'x-y-z'
        linger = NPRLingerRate()
        class FakeMessage(object):
            body = {
                'text': 'check slug ' + slug
            }

        clear_stories()
        Story.create(
            name = 'example',
            slug = slug,
            date = datetime.datetime.now(),
            url = 'example.com',
            team = 'deafult'
        )

        message = linger.handle_slug_inquiry(FakeMessage)
        print message
        assert u'*100* people spent a median *55 seconds* on `x-y-z`' in message['text']
        self.assertEqual(message['attachments'][0]['title'], slug)
