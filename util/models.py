import datetime
from peewee import *

db = SqliteDatabase('carebot.db')

class Story(Model):
    name = CharField(null = True)
    slug = CharField(unique=True)
    story_type = CharField(null=True)
    url = CharField(null=True)
    date = DateField(null=True)

    tracking_started = DateTimeField(default=datetime.datetime.now)
    last_checked = DateTimeField(null = True)

    class Meta:
        database = db

db.connect()

# Only create tables if they don't already exist
db.create_tables([Story], safe=True)
