import copytext
import datetime
import logging
from peewee import IntegrityError
import time

from util.models import Story

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


# Right now, we don't care about stories before this time
MAGIC_DATE_CUTOFF = datetime.date(2016, 02, 22)

class SpreadsheetScraper:
    """
    Don't read this.
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
            if self.parse_date(row['date']) > MAGIC_DATE_CUTOFF:
                stories.append(row)
        return stories

    def write(self, stories):
        new_stories = []
        for story in stories:
            try:
                story = Story.create(
                    name = story['story_headline'],
                    slug = story['graphic_slug'],
                    date = self.parse_date(story['date']),
                    story_type = story['graphic_type'],
                    url = story['story_url']
                )
                new_stories.append(story)
            except IntegrityError:
                # Story probably already exists.
                pass

        return new_stories
