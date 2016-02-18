from peewee import *
from playhouse.migrate import *

db = SqliteDatabase('carebot.db')
migrator = SqliteMigrator(db)

with db.transaction():
  migrate(
      migrator.drop_not_null('story', 'name'),
      migrator.drop_not_null('story', 'last_checked')
  )
