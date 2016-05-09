#!/usr/bin/env python

import app_config
app_config.DATABASE_NAME = 'carebot_test.db'
app_config.DEFAULT_CONFIG_PATH = 'tests/config_test.yml'

try:
    import unittest2 as unittest
except ImportError:
    import unittest

import datetime

from plugins.npr.scrolldepth import NPRScrollDepth
from util.config import Config


class TestNPRSCrollDepth(unittest.TestCase):
    def test_fill_in_max(self):
        test_data = [[1, 100, 3], [1, 200, 3], [1, 500, 3], [1, 200, 3]]

        results = NPRScrollDepth.fill_in_max(test_data)
        self.assertEqual(results[0][1], 500)
        self.assertEqual(results[1][1], 500)
        self.assertEqual(results[2][1], 500)
        self.assertEqual(results[3][1], 200)

