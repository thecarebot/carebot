from analytics import Analytics
from models import Story
import time

MINUTES_BETWEEN_CHECKS = 15
MINUTES_BETWEEN_REPORTS = [
    240,  # 4 hours
    480   # 8 hours
]

a = Analytics()

"""
Get updated linger rate stats for every story we track
"""
def get_stats():
    stories = Story.select()
    for story in stories:
        print story.slug
        print story.tracking_started
        print (a.get_linger_rate(story.slug))
        # TODO: get message

get_stats()
