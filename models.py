from peewee import *

db = SqliteDatabase('carebot.db')

class Story(Model):
    name = CharField(null = True)
    slug = CharField()
    tracking_started = DateTimeField()
    last_checked = DateTimeField(null = True)

    class Meta:
        database = db

db.connect()

# Only create tables if they don't already exist
db.create_tables([Story], safe=True)
