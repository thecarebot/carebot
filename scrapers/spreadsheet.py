import copytext
import datetime
import logging
from peewee import IntegrityError
import time

from util.models import Story
from scrapers.nprapi import NPRAPIScraper
from scrapers.screenshot import Screenshotter

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

npr_api_scraper = NPRAPIScraper()
screenshotter = Screenshotter()

# Right now, we don't care about stories before this time
MAGIC_DATE_CUTOFF = datetime.date(2016, 02, 28)

class SpreadsheetScraper:
    """
    From https://github.com/tarbell-project/tarbell/blob/1.0.5/tarbell/app.py#L251
    """
    def parse_date(self, value):
        value = float(value)
        seconds = (value - 25569) * 86400.0
        parsed = datetime.datetime.utcfromtimestamp(seconds).date()
        return parsed

    """
    Scrape the NPR Visuals 'did we touch it?' spreadsheet
    """
    def scrape_spreadsheet(self, filename):
        stories = []
        spreadsheet = copytext.Copy(filename)
        data = spreadsheet['published']
        for row in data:
            if str(row['graphic_slug']) is not '' and str(row['date']) is not '':
                if self.parse_date(row['date']) > MAGIC_DATE_CUTOFF:
                    stories.append(row)
            else:
                logger.info('Not adding %s to database: missing slug or date' % (row['story_headline']))
        return stories

    """
    Save rows to the database
    """
    def write(self, stories, team=None):
        new_stories = []
        for story in stories:
            info_from_api = npr_api_scraper.get_story_details(story['story_url'])

            if not info_from_api:
                logger.info('Not adding %s to database: could not get story' % (story['story_headline']))
                pass

            exists = Story.select().where(Story.url == story['story_url'])
            if exists:
                logger.info('Not adding %s to database: already exists' % (story['story_headline']))

            else:
                try:
                    screenshot_url = screenshotter.get_story_image(story['story_url'])
                    story = Story.create(
                        name = story['story_headline'].strip(),
                        slug = story['graphic_slug'].strip(),
                        date = info_from_api['date'],
                        story_type = story['graphic_type'].strip(),
                        url = story['story_url'].strip(),
                        image = info_from_api['image'],
                        team = team,
                        screenshot = screenshot_url
                    )
                    new_stories.append(story)
                except IntegrityError:
                    # Story probably already exists.
                    logger.info('Not adding %s to database: probably already exists' % (story['story_headline']))
                    pass
        return new_stories
