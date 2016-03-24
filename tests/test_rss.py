#!/usr/bin/env python

try:
    import unittest2 as unittest
except ImportError:
    import unittest

import datetime

from util.config import Config
from scrapers.rss import RSSScraper

class TestRSS(unittest.TestCase):
    def test_parse(self):
        scraper = RSSScraper(path='http://thecarebot.github.io/sample.feed.xml')
        stories = scraper.scrape()
        self.assertEqual(stories[0]['name'], 'Carebot Design Principles')
        self.assertEqual(type(stories[1]['date']), datetime.datetime)
