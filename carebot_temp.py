import datetime
import json
import inflect
import logging
import re
from sets import Set
from slackbot.bot import Bot
from slackbot.bot import respond_to
from slackbot.bot import listen_to
import unicodedata

from scrapers.analytics import GoogleAnalyticsScraper
from scrapers.npr_api import NPRAPIScraper
from util.chart import ChartTools
from util.time import TimeTools


from util.config import Config
from util.models import Story
from util.slack import SlackTools

inflector = inflect.engine()

# Set up analytics to handle inquiries
analytics = GoogleAnalyticsScraper()


slack_tools = SlackTools()
npr_api_scraper = NPRAPIScraper()
config = Config()

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

LINGER_RATE_REGEX = re.compile(ur'slug ((\w*-*)+)')
SCROLL_RATE_REGEX = re.compile(ur'scroll ((\w*-*)+)')
GRUBER_URLINTEXT_PAT = re.compile(ur'(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:\'".,<>?\xab\xbb\u201c\u201d\u2018\u2019]))')
HELLO_REGEX = re.compile(ur'Hello', re.IGNORECASE)

def handle_overview_question(message):
    message.reply("Let me check what's been happening. This may take a second.")
    seven_days_ago = datetime.datetime.now() - datetime.timedelta(days=7)
    stories = Story.select().where(Story.tracking_started > seven_days_ago)

    slugs = Set()
    for story in stories:
        print story.name
        story_slugs = story.slug.split(',')
        for slug in story_slugs:
            slugs.add(slug)

    team = config.get_team_for_story(stories[0])
    total_users = analytics.get_user_data(team=team, start_date='7daysAgo')
    total_users = int(total_users['rows'][0][0])
    total_users = "{:,}".format(total_users)

    median = analytics.get_linger_rate(team=team, start_date='7daysAgo')
    linger_rows = analytics.get_linger_rows(team=team, start_date='7daysAgo')
    linger_histogram_url = ChartTools.linger_histogram_link(linger_rows, median)

    attachments = [{
        "fallback": "linger update",
        "color": "#eeeeee",
        "title": "Time spent on graphics over the last week",
        "image_url": linger_histogram_url
    }]

    slack_tools.send_message(message.body['channel'], "In the past 7 days, I've tracked %s stories and %s graphics." % (len(stories), len(slugs)))
    slack_tools.send_message(message.body['channel'], "%s people looked at graphics on those stories. Here's how much time they spent:" % total_users, attachments, unfurl_links=False)

    fields = []
    for story in stories:
        print "Adding %s" % story.name
        fields.append({
            "title": story.name.strip(),
            "value": '<' + story.url + '|' + story.slug.strip() + '>',
            "short": True
        })

    attachments = [{
        "fallback": "linger update",
        "color": "#eeeeee",
        # "title": "What we have done",
        "fields": fields
    }]

    slack_tools.send_message(message.body['channel'], "Here's everything:", attachments, unfurl_links=False)


def handle_scroll_slug_question(message):
    m = re.search(SCROLL_RATE_REGEX, message.body['text'])

    if not m:
        return

    slug = m.group(1)

    if slug:
        stories = Story.select().where(Story.slug.contains(slug))

        team = config.get_team_for_story(stories[0])
        rows = analytics.get_depth_rate(team=team, slug=slug)

        if rows:
            reply = u"Here's what I know about `%s`." % slug

            reply += '\n\nThis graphic appears in %s %s:' % (inflector.number_to_words(len(stories)),
                inflector.plural('story', len(stories)))

            for story in stories:
                reply += '\n' + '*<%s|%s>*' % (story.url, story.name.strip())

            histogram_url = ChartTools.scroll_histogram_link(rows)

            if story.screenshot:
                histogram_url = ChartTools.add_screenshot_to_chart(story.screenshot,
                    histogram_url)

            attachments = [
                {
                    "fallback": slug + " update",
                    "color": "#eeeeee",
                    "title": slug,
                    "image_url": histogram_url
                }
            ]

            slack_tools.send_message(message.body['channel'], reply, attachments, unfurl_links=False)

        else:
            message.reply("I wasn't able to find scroll data for %s" % slug)

