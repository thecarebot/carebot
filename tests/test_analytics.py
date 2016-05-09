#!/usr/bin/env python
try:
    import unittest2 as unittest
except ImportError:
    import unittest

import datetime


import app_config
app_config.DATABASE_NAME = 'carebot_test.db'
from util.config import Config
from util.analytics import GoogleAnalytics

class TestAnalytics(unittest.TestCase):
    def test_median(self):
        values = [1, 1, 2, 2, 2, 3, 3]
        median = GoogleAnalytics.median(values)
        self.assertEqual(median, 2)

