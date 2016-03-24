from peewee import *
from playhouse.migrate import *

db = SqliteDatabase('carebot.db')
migrator = SqliteMigrator(db)

team_field = CharField(default='')

with db.transaction():
  migrate(
    migrator.add_column('story', 'team', team_field)
  )
