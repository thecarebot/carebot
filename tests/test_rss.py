#!/usr/bin/env python

try:
    import unittest2 as unittest
except ImportError:
    import unittest

from util.config import Config
from scrapers.rss import RSSScraper

class TestRSS(unittest.TestCase):
    def test_parse(self):
        scraper = RSSScraper(path='http://feedparser.org/docs/examples/atom10.xml')
        stories = scraper.get_posts()
