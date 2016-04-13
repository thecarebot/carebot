import datetime
from peewee import *

import app_config
from util.config import Config
from util.time import TimeTools

config = Config()

db = SqliteDatabase(app_config.DATABASE_NAME)

class Story(Model):
    name = CharField(null = True)
    slug = CharField(unique=True)
    story_type = CharField(null=True)
    url = CharField(null=True)
    image = CharField(null=True)
    date = DateField(null=True)

    team = CharField(null=True)
    article_posted = DateTimeField(null = True)
    tracking_started = DateTimeField(default=datetime.datetime.now)
    last_checked = DateTimeField(null = True)
    last_bucket = CharField(null = True)
    screenshot = CharField(null=True)

    def slug_list(self):
        slugs = self.slug.split(',')
        slugs = [slug.strip() for slug in slugs]
        return slugs

    def time_bucket(self):
        return TimeTools.time_bucket(self.article_posted)

    def channel(self):
        channel = app_config.DEFAULT_CHANNEL
        if self.team:
            teams = config.get_teams()
            try:
                channel = teams[self.team]['channel']
            except:
                pass

            channel = '#' + channel

        print 'Using channel %s' % channel
        return channel


    class Meta:
        database = db

db.connect()

# Only create tables if they don't already exist
db.create_tables([Story], safe=True)
