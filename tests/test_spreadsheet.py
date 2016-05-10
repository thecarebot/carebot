#!/usr/bin/env python

try:
    import unittest2 as unittest
except ImportError:
    import unittest

from mock import patch

import app_config
app_config.DATABASE_NAME = 'carebot_test.db'

from scrapers.npr_spreadsheet import SpreadsheetScraper
from util.config import Config
from util.models import Story
from tests.test_util.db import clear_stories

class TestSpreadsheet(unittest.TestCase):
    source = {
        'doc_key': 'foo-bar-baz'
    }

    def test_scrape_spreadsheet(self):
        """
        Make sure we grab the right data from spreadsheets
        """
        scraper = SpreadsheetScraper(self.source)
        stories = scraper.scrape_spreadsheet('tests/data/stories.xlsx')
        self.assertEqual(len(stories), 4)

        self.assertEqual(stories[0]['date'], '42467') # Crappy excel date format
        self.assertEqual(stories[0]['graphic_slug'], 'voting-wait-20160404')
        self.assertEqual(stories[0]['graphic_type'], 'Graphic')
        self.assertEqual(stories[0]['story_headline'], 'What Keeps Election Officials Up At Night? Fear Of Long Lines At The Polls')
        self.assertEqual(stories[0]['story_url'], 'http://www.npr.org/2016/04/07/473293026/what-keeps-election-officials-up-at-night-fear-of-long-lines-at-the-polls')
        self.assertEqual(stories[0]['contact'], 'Alyson Hurt')

        self.assertEqual(stories[0]['date'], '42467')
        self.assertEqual(stories[3]['graphic_slug'], 'seed-market-20160405')
        self.assertEqual(stories[3]['graphic_type'], 'Graphic')
        self.assertEqual(stories[3]['story_headline'], 'Big Seed: Consolidation Is Shrinking The Industry Even Further')
        self.assertEqual(stories[3]['story_url'], 'http://www.npr.org/sections/thesalt/2016/04/06/472960018/big-seed-consolidation-is-shrinking-the-industry-even-further')
        self.assertEqual(stories[3]['contact'], 'Alyson Hurt')

    @patch('util.s3.Uploader.upload', return_value='http://image-url-here')
    def test_write_spreadsheet(self, mock_upload):
        """
        Make sure we save the stories to the database when scraping from a
        spreadsheet
        """
        clear_stories()

        scraper = SpreadsheetScraper(self.source)
        stories = scraper.scrape_spreadsheet('tests/data/stories.xlsx')

        scraper.write(stories)

        results = Story.select()
        self.assertEqual(len(results), 4)

        for idx, story in enumerate(stories):
            self.assertEqual(results[idx].name, story['story_headline'])
            self.assertEqual(results[idx].url, story['story_url'])

    @patch('util.s3.Uploader.upload')
    def test_write_spreadsheet_duplicates(self, mock_upload):
        """
        Make sure stories don't get inserted more than once
        """
        mock_upload.return_value = 'http://image-url-here'

        clear_stories()

        scraper = SpreadsheetScraper(self.source)
        stories = scraper.scrape_spreadsheet('tests/data/stories.xlsx')

        # Insert the stories
        scraper.write(stories)
        results = Story.select()
        self.assertEqual(len(results), 4)

        # Now insert them again and make sure we don't have duplicates
        scraper.write(stories)
        results = Story.select()
        self.assertEqual(len(results), 4)
