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
        fake_source = {
            'team': "carebot",
            'type': "rss",
            'url': "http://thecarebot.github.io/sample.feed.xml",
            'date_field': 'published',
            'url_field': 'id',
            'title_field':'title'
        }

        scraper = RSSScraper(fake_source)
        stories = scraper.scrape()
        self.assertEqual(stories[0]['name'], 'Carebot Design Principles')
        self.assertEqual(type(stories[1]['date']), datetime.datetime)
