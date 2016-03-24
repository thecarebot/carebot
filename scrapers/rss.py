import copytext
from datetime import datetime, timedelta
import feedparser
import logging
from peewee import IntegrityError
import time

from util.models import Story
from scrapers.nprapi import NPRAPIScraper

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class RSSScraper:
    def __init__(self, path):
        self.path = path

        # We'll ignore stories older than this.
        self.magic_date_cutoff = datetime.now() - timedelta(days=5)

    """
    From https://github.com/tarbell-project/tarbell/blob/1.0.5/tarbell/app.py#L251
    """
    def parse_date(self, value):
        value = float(value)
        seconds = (value - 25569) * 86400.0
        parsed = datetime.utcfromtimestamp(seconds).date()
        return parsed

    """
    Scrae an RSS feed
    """
    def get_posts(self):
        feed = feedparser.parse(self.path)
        stories = []
        for entry in feed.entries:
            date = entry.published
            print "parsed date"
            print date
            print type(date)

            if date > self.magic_date_cutoff:
                stories.append({
                    'name': entry.title,
                    'slug': entry.id,
                    'url': entry.link,
                    'date': date,
                    'article_posted': date
                })

        return stories

    def write(self, stories):
        new_stories = []
        for story in stories:
            try:
                story = Story.create(
                    name = story['name'],
                    slug = story['slug'],
                    date = story['date'],
                    article_posted = story['date'],
                    url = story['url']
                )
                new_stories.append(story)
            except IntegrityError:
                # Story probably already exists.
                logger.info('Not adding %s to database: probably already exists' % (story['story_headline']))


        return new_stories
