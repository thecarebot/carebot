import datetime
from dateutil.parser import parse
from fabric.api import task
import importlib
import logging
from pydoc import locate, ErrorDuringImport
import pytz

import app_config
from util.models import Story
from util.slack import SlackTools
from util.config import Config
from scrapers.npr_api import NPRAPIScraper
from scrapers.npr_pocky import PockyScraper
from scrapers.rss import RSSScraper
from scrapers.screenshot import Screenshotter
from scrapers.npr_spreadsheet import SpreadsheetScraper


config = Config()
screenshotter = Screenshotter()
slack_tools = SlackTools()

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Fix sys.path :-/
# It doesn't include the project dir by default
# http://stackoverflow.com/questions/714063/importing-modules-from-parent-folder
import os,sys,inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir)


"""
Data tasks
"""

@task
def load_new_stories():
    """
    Goes through the sources you configured in `app_config` and adds any new
    stories to the database.
    """
    for source in app_config.SOURCES:
        if source['type'] == 'spreadsheet':
            stories = SpreadsheetScraper(source).scrape_and_load()

        elif source['type'] == 'rss':
            stories = RSSScraper(source).scrape_and_load()

        if source['type'] == 'pocky':
            stories = PockyScraper(source).scrape_and_load()

        for story in stories:
            slack_tools.send_tracking_started_message(story)

def seconds_since(a):
    """
    Calculates the seconds since a timepoint
    """
    now = datetime.datetime.now(pytz.timezone(app_config.PROJECT_TIMEZONE))
    return (now - a).total_seconds()

def time_bucket(t):
    """
    Takes a datetime
    Converts that into a string for the "time bucket" since that datetime.
    These are used to control how often article updates are automatically posted
    to channels.

    For example, if an article was published 1 day and 16 hours ago, the time
    bucket is "day 1 hour 15". An article published 6 hours ago gets bucketed
    in "hour 4".
    """
    if not t:
        return False

    # For some reason, dates with timezones tend to be returned as unicode
    if type(t) is not datetime.datetime:
        t = parse(t)

    seconds = seconds_since(t)

    # 7th message, 2nd day midnight + 10 hours
    # 8th message, 2nd day midnight + 15 hours
    second_day_midnight_after_publishing = t + datetime.timedelta(days=2)
    second_day_midnight_after_publishing.replace(hour = 0, minute = 0, second=0, microsecond = 0)
    seconds_since_second_day = seconds_since(second_day_midnight_after_publishing)

    if seconds_since_second_day > 15 * 60 * 60: # 15 hours
        return 'day 2 hour 15'

    if seconds_since_second_day > 10 * 60 * 60: # 10 hours
        return 'day 2 hour 10'

    # 5th message, 1st day midnight + 10 hours
    # 6th message, 1st day midnight + 15 hours
    midnight_after_publishing = t + datetime.timedelta(days=1)
    midnight_after_publishing.replace(hour = 0, minute = 0, second=0, microsecond = 0)
    seconds_since_first_day = seconds_since(midnight_after_publishing)

    if seconds_since_second_day > 10 * 60 * 60: # 15 hours
        return 'day 1 hour 15'

    if seconds_since_second_day > 10 * 60 * 60: # 10 hours
        return 'day 1 hour 10'

    # 2nd message, tracking start + 4 hours
    # 3rd message, tracking start + 8 hours
    # 4th message, tracking start + 12 hours
    if seconds > 12 * 60 * 60: # 12 hours
        return 'hour 12'

    if seconds > 8 * 60 * 60: # 8 hours
        return 'hour 8'

    if seconds > 4 * 60 * 60: # 4 hours
        return 'hour 4'

    # Too soon to check
    return False

@task
def add_story_screenshots(regenerate=False, article_id='storytext'):
    """
    Utility. Used to generate a screenshot of every article.
    pass regenerate=true to regenerate all screenshots (otherwise it'll skip
    stories where that field already has a URL).

    Pass an articleid to specify the CSS ID of the article. The image will be
    cropped to that ID.
    """
    if regenerate:
        for story in Story.select():
            logger.info("About to check {0}".format(story.name))

            story.screenshot = screenshotter.get_story_image(story_url=story.url,
                article_id=article_id)
            story.save()

    else:
        for story in Story.select().where(Story.screenshot == None):
            logger.info("About to check {0}".format(story.name))

            story.screenshot = screenshotter.get_story_image(story_url=story.url,
                article_id=article_id)
            logger.info("Got screenshot {0}".format(story.screenshot))
            story.save()

@task
def get_story_stats():
    """
    Loop through every story we know about.
    If there hasn't been an update recently, fetch stats for that article.
    """

    # TODO use a SQL query instead of app logic to exclude stories that are
    # too old.
    for story in Story.select():
        logger.info("About to check %s" % (story.name))

        team = config.get_team_for_story(story)
        story_time_bucket = time_bucket(story.date)
        last_bucket = story.last_bucket

        # Check when the story was last reported on
        if last_bucket:

            # Skip stories that have been checked recently
            # And stories that are too old.
            if last_bucket == story_time_bucket:
                logger.info("Checked recently. Bucket is still %s", story_time_bucket)
                continue

        if not story_time_bucket:
            logger.info("Story is too new; skipping for now")
            continue

        plugins = [getattr(importlib.import_module(mod), cls) for (mod, cls) in (plugin.rsplit(".", 1) for plugin in team['plugins'])]
        for plugin in plugins:
            plugin = plugin()

            try:
                message = plugin.get_update_message(story)
                if message:
                    slack_tools.send_message(
                        team['channel'],
                        message['text'],
                        message.get('attachments', None)
                    )

            except NotImplementedError:
                pass

        # Mark the story as checked
        story.last_checked = datetime.datetime.now(pytz.timezone(app_config.PROJECT_TIMEZONE))
        story.last_bucket = story_time_bucket
        story.save()
