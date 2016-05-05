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
from util.analytics import GoogleAnalytics

class TestAnalytics(unittest.TestCase):
    def test_median(self):
        values = [1, 1, 2, 2, 2, 3, 3]
        median = GoogleAnalytics.median(values)
        self.assertEqual(median, 2)

