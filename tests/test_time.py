#!/usr/bin/env python

try:
    import unittest2 as unittest
except ImportError:
    import unittest

from util.time import TimeTools

class TestTimeTools(unittest.TestCase):
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
