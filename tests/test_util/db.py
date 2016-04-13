from util.models import Story

def clear_stories():
  q = Story.delete()
  q.execute()
