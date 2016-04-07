from peewee import *
from playhouse.migrate import *

db = SqliteDatabase('carebot.db')
migrator = SqliteMigrator(db)

screenshot = CharField(null=True)

with db.transaction():
    migrate(
        migrator.add_column('story', 'screenshot', screenshot)
    )
