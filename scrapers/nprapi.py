import copytext
from dateutil.parser import parse
import json
import logging
from peewee import IntegrityError
import re
import requests
import time

import app_config

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

STORY_ID_REGEX = '.*\/(\d{5,})'

class NPRAPIScraper:
    """
    Given a story URL, get the Seamus ID
    """
    def get_story_id(self, story_url):
        id = re.search(STORY_ID_REGEX, story_url)
        if id:
            return id.group(1)

        return False

    """
    Get details for a story
    """
    def get_story_details(self, story_url):
        story_id = self.get_story_id(story_url)

        if not story_id:
            return False

        # Look up the story in the NPR API
        response = requests.get('http://api.npr.org/query', params={
            'id': story_id,
            'apiKey': app_config.NPR_API_KEY,
            'format': 'JSON'
        })

        doc = json.loads(response.content)

        if 'story' in doc['list']:
            # print(doc['list'])
            date_added = doc['list']['story'][0]['storyDate']['$text']
            date = parse(date_added) #, ignoretz=True
        else:
            logger.error("No details found for %s in NPR API." % story_id)
            date = None

        # Check if we have an image for this story
        try:
            image = doc['list']['story'][0]['image'][0]['src']
        except:
            image = None

        try:
            title = doc['list']['story'][0]['title']['$text']
        except:
            title = None

        info = {
            'date': date,
            'image': image,
            'title': title
        }

        return info
