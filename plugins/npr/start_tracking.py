import logging
import re

from scrapers.nprapi import NPRAPIScraper
from util.analytics import GoogleAnalytics
from util.config import Config
from util.models import Story
from util.slack import SlackTools
from plugins.base import CarebotPlugin

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

config = Config()
npr_api_scraper = NPRAPIScraper()
slack_tools = SlackTools()

class NPRStartTracking(CarebotPlugin):
    """
    Start tracking a story by asking:
    @carebot Track slug-here http://npr.org/example/...
    """
    START_TRACKING_REGEX = re.compile(ur'[Tt]rack (((\w*-*)+,?)+)')

    # Gruber's URL extraction regex
    # http://daringfireball.net/2010/07/improved_regex_for_matching_urls
    GRUBER_URLINTEXT_PAT = re.compile(ur'(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:\'".,<>?\xab\xbb\u201c\u201d\u2018\u2019]))')

    def __init__(self, *args, **kwargs):
        super(NPRStartTracking, self).__init__(*args, **kwargs)

    def get_listeners(self):
        return [
            ['start-tracking', self.START_TRACKING_REGEX, self.respond],
        ]

    def respond(self, message):
        m = re.search(self.START_TRACKING_REGEX, message.body['text'])

        if not m:
            return False

        slug = m.group(1)

        if slug:
            # Check if the slug is in the database.
            try:
                story = Story.select().where(Story.slug.contains(slug)).get()
                text = "Thanks! I'm already tracking `%s`, and you should start seeing results within a couple hours." % slug
            except Story.DoesNotExist:
                # If it's not in the database, start tracking it.
                url = re.search(self.GRUBER_URLINTEXT_PAT, message.body['text'])

                if not url:
                    logger.error("Couldn't find story URL in message %s", message.body['text'])
                    text = "Sorry, I need a story URL to start tracking."
                    return

                details = npr_api_scraper.get_story_details(url.group(1))

                if not details:
                    logger.error("Couldn't find story in API for URL %s", url.group(1))
                    text = "Sorry, I wasn't able to find that story in the API, so I couldn't start tracking it."
                    return

                # Find out what team we need to save this story to
                channel = slack_tools.get_channel_name(message.body['channel'])
                team = config.get_team_for_channel(channel)

                # Create the story
                story = Story.create(name=details['title'],
                                     slug=slug,
                                     date=details['date'],
                                     url=url.group(1),
                                     image=details['image'],
                                     team=team
                                    )
                story.save()
                text = "Ok, I've started tracking `%s`. The first stats should arrive in 4 hours or less." % slug

        else:
            text = "Sorry, I wasn't able to start tracking `%s` right now." % slug

        if text:
            return {
                'text': text
            }

