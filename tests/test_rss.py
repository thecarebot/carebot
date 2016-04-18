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
        class FakeSource:
            team = "carebot"
            type = "rss"
            url = "https://thecarebot.github.io/feed.xml"
            date_field = 'published'
            url_field = 'id'
            title_field = 'title'

        scraper = RSSScraper(FakeSource)
        stories = scraper.scrape()
        self.assertEqual(stories[0]['name'], 'Carebot Design Principles')
        self.assertEqual(type(stories[1]['article_posted']), datetime.datetime)
