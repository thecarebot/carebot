import copytext
import datetime
import logging
from oauth import get_document
import os
from peewee import IntegrityError
import pytz
import time

import app_config
from util.models import Story
from scrapers.npr_api import NPRAPIScraper
from scrapers.screenshot import Screenshotter

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

npr_api_scraper = NPRAPIScraper()
screenshotter = Screenshotter()

POCKY_TRACKER = os.environ.get('POCKY_SHEET')

class PockyScraper:
    """
    From https://github.com/tarbell-project/tarbell/blob/1.0.5/tarbell/app.py#L251
    """
    def __init__(self, source):
        self.source = source

    @staticmethod
    def parse_date(value):
        """
        Attemts to parse a date from Excel into something the rest of the world
        can use.
        """
        value = float(value)
        seconds = (value - 25569) * 86400.0
        parsed = datetime.datetime.utcfromtimestamp(seconds)
        tz = pytz.timezone(app_config.PROJECT_TIMEZONE)
        parsed = tz.localize(parsed)
        print "parsed"
        print parsed

        return parsed

    def scrape_and_load(self, path=app_config.STORIES_PATH):
        if not POCKY_TRACKER:
            return

        get_document(POCKY_TRACKER, path)
        raw_stories = self.scrape_spreadsheet()
        stories = self.write(stories=raw_stories, team=self.source['team'])
        return stories

    def scrape_spreadsheet(self, path=app_config.STORIES_PATH):
        """
        Scrape the pocky tracker spreadsheet
        """
        spreadsheet = copytext.Copy(path)
        data = spreadsheet['reviews']
        return data

    def write(self, stories, team=None):
        """
        Save rows to the database
        """
        new_stories = []
        for story in stories:
            slug = story['official flavor description'] + ' - ' + story['taster']

            try:
                story = Story.create(
                    name=story['name'].strip(),
                    slug=slug,
                    date=PockyScraper.parse_date(story['date tasted']),
                    story_type='pocky',
                    team=team,
                )
                logger.info('Added {0}'.format(story.name))
                new_stories.append(story)
            except IntegrityError:
                # Story probably already exists.
                logger.info('Not adding %s to database: probably already exists' % (slug))
                pass

        return new_stories
