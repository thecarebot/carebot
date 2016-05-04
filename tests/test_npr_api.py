#!/usr/bin/env python

try:
    import unittest2 as unittest
except ImportError:
    import unittest

from datetime import date

from util.config import Config
from scrapers.npr_api import NPRAPIScraper

class TestNPRAPIScraper(unittest.TestCase):
    def test_get_story_id(self):
        scraper = NPRAPIScraper()
        url = 'http://www.npr.org/2016/04/07/473293026/what-keeps-election-officials-up-at-night-fear-of-long-lines-at-the-polls'
        story_id = scraper.get_story_id(url)
        self.assertEqual(story_id, '473293026')

    def test_get_story_details(self):
        scraper = NPRAPIScraper()
        url = 'http://www.npr.org/2016/04/07/473293026/what-keeps-election-officials-up-at-night-fear-of-long-lines-at-the-polls'
        details = scraper.get_story_details(url)

        self.assertEqual(details['date'].date(), date(2016, 04, 07))
        self.assertEqual(details['image'], u'https://media.npr.org/assets/img/2016/04/06/gettyimages-513187994_wide-2d1e9d8e5ed0ccd424c01ff0dbb2906ebe91a1ea.jpg?s=12')
        self.assertEqual(details['title'], 'What Keeps Election Officials Up At Night? Fear Of Long Lines At The Polls')
