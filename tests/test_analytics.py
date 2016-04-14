#!/usr/bin/env python

try:
    import unittest2 as unittest
except ImportError:
    import unittest

import datetime

from util.config import Config
from scrapers.analytics import GoogleAnalyticsScraper

class TestAnalytics(unittest.TestCase):
    def test_fill_in_max(self):
        test_data = [[1, 100, 3], [1, 200, 3], [1, 500, 3], [1, 200, 3]]

        results = GoogleAnalyticsScraper.fill_in_max(test_data)
        self.assertEqual(results[0][1], 500)
        self.assertEqual(results[1][1], 500)
        self.assertEqual(results[2][1], 500)
        self.assertEqual(results[3][1], 200)
