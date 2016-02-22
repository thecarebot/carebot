import copytext
import logging

from models import Story

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
        data = spreadsheet['Form Responses 1']
        for row in data:
            story = Story(row)
            stories.append(story)
        return stories

    def write(self, db, stories):
        table = db['spreadsheet']
        for story in stories:
            logger.info('Updating {0}'.format(story.seamus_id))
            database_story = table.find_one(seamus_id=story.seamus_id)
            if not database_story:
                table.insert(story.serialize())
            elif story.duration > database_story['duration']:
                table.upsert(story.serialize(), ['seamus_id'])
