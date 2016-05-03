#!/usr/bin/env python

import app_config
app_config.DATABASE_NAME = 'carebot_test.db'
app_config.DEFAULT_CONFIG_PATH = 'tests/config_test.yml'

try:
    import unittest2 as unittest
except ImportError:
    import unittest

import datetime

from util.config import Config
from scrapers.analytics import GoogleAnalyticsScraper

class TestAnalytics(unittest.TestCase):
    @unittest.skip("TODO")
    def test_median(self):
        pass

    @unittest.skip("TODO")
    def test_median_of_time_buckets(self):
        pass

    @unittest.skip("TODO")
    def test_get_median(self):
        pass

    @unittest.skip("TODO")
    def test_get_update_message(self):
        pass

    @unittest.skip("TODO")
    def test_clean_data(self, data):
        pass
