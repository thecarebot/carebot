import copytext
import logging
from peewee import IntegrityError
import time

import app_config
from oauth import get_document

from util.models import Story

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class SpreadsheetScraper:
    """
    Scrape the NPR Visuals 'did we touch it?' spreadsheet
    """
    def scrape_spreadsheet(self, filename):
        stories = []
        spreadsheet = copytext.Copy(filename)
        data = spreadsheet['published']
        for row in data:
            print row['date'], row['graphic_slug']
            # story = Story(row)
            # stories.append(story)
        return data

    def write(self, stories):
        for story in stories:
            try:
                Story.create(
                    name = story['story_headline'],
                    slug = story['graphic_slug'],
                    # Dates aren't pulled right from the spreadsheet
                    # date = time.strptime(story['date'], '%m/%d/%Y'),
                    story_type = story['graphic_type'],
                    url = story['story_url']
                )
            except IntegrityError:
                # Story probably already exists.
                pass

get_document(app_config.STORIES_GOOGLE_DOC_KEY, app_config.STORIES_PATH)
scraper = SpreadsheetScraper()
stories = scraper.scrape_spreadsheet(app_config.STORIES_PATH)
scraper.write(stories)

# scraper.write(db, stories)
