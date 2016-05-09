#!/usr/bin/env python

from datetime import datetime, timedelta
import pytz

try:
    import unittest2 as unittest
except ImportError:
    import unittest

import app_config
from util.time import TimeTools

class TestTimeTools(unittest.TestCase):
    def test_time_bucket(self):
        now = datetime.now(pytz.timezone(app_config.PROJECT_TIMEZONE))
        five_hours_ago = now - timedelta(hours=5)
        ten_hours_ago = now - timedelta(hours=10)
        bucket = TimeTools.time_bucket(five_hours_ago)
        self.assertEqual(bucket, '4 hours')

        bucket = TimeTools.time_bucket(ten_hours_ago)
        self.assertEqual(bucket, '8 hours')

    def test_humanist_time_bucket(self):
        bucket = TimeTools.humanist_time_bucket({
            'minutes': 5,
            'seconds': 5
        })
        self.assertEqual(bucket, '5 minutes 5 seconds')

        bucket = TimeTools.humanist_time_bucket({
            'minutes': 0,
            'seconds': 1
        })
        self.assertEqual(bucket, '1 second')

        bucket = TimeTools.humanist_time_bucket({
            'minutes': 5,
            'seconds': 0
        })
        self.assertEqual(bucket, '5 minutes')

        bucket = TimeTools.humanist_time_bucket({
            'minutes': 1,
            'seconds': 1
        })
        self.assertEqual(bucket, '1 minute 1 second')
