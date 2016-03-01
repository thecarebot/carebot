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

        response = requests.get('http://api.npr.org/query', params={
            'id': story_id,
            'apiKey': app_config.NPR_API_KEY,
            'format': 'JSON'
        })

        doc = json.loads(response.content)

        date_added = doc['list']['story'][0]['storyDate']['$text']
        date = parse(date_added) #, ignoretz=True

        try:
            image = doc['list']['story'][0]['image'][0]['src']
        except:
            image = None

        info = {
            'date': date,
            'image': image
        }

        return info



    """
    Get details for a story URL
    """
    def get_story_date(self, story_url):
        story_id = self.get_story_id(story_url)

        if not story_id:
            return False

        response = requests.get('http://api.npr.org/query', params={
            'id': story_id,
            'apiKey': app_config.NPR_API_KEY,
            'format': 'JSON'
        })

        doc = json.loads(response.content)
        date_added = doc['list']['story'][0]['storyDate']['$text']
        date = parse(date_added) #, ignoretz=True
        return date
