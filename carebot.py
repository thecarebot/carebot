# from analytics import Analytics
import json
import logging
import re
from slackbot.bot import Bot
from slackbot.bot import respond_to
from slackbot.bot import listen_to

from scrapers.analytics import GoogleAnalyticsScraper
from util.models import Story
from util.chart import ChartTools
from util.slack import SlackTools
from util.time import TimeTools

slackTools = SlackTools()

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Set up analytics to handle inquiries
analytics = GoogleAnalyticsScraper()

LINGER_RATE_REGEX = re.compile(ur'slug ((\w*-*)+)')
GRUBER_URLINTEXT_PAT = re.compile(ur'(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:\'".,<>?\xab\xbb\u201c\u201d\u2018\u2019]))')

def handle_linger_slug_question(message):
    m = re.search(LINGER_RATE_REGEX, message.body['text'])

    if not m:
        return False

    slug = m.group(1)

    if slug:
        rate = analytics.get_linger_rate(slug)
        if rate:
            people = "{:,}".format(rate['total_people'])
            time_text = TimeTools.humanist_time_bucket(rate)
            reply = u"%s people spent an average of %s on %s." % (people, time_text, slug)

            rows = analytics.get_linger_histogram(slug)
            histogram_url = ChartTools.linger_histogram_link(rows)
            attachments = [
                {
                    "fallback": slug + " update",
                    "color": "#eeeeee",
                    "title": slug,
                    "image_url": histogram_url
                }
            ]

            slackTools.send_message(message.body['channel'], reply, attachments)

            # message.send_webapi(reply, json.dumps(attachments))

            # TODO -- how to send?
            # message.reply()
            return True
        else:
            message.reply("I wasn't able to figure out the linger rate of %s" % slug)
            return False
    else:
        return False

def handle_linger_update(message):
    if 'doing' not in message.body['text']:
        return

    m = GRUBER_URLINTEXT_PAT.findall(message.body['text'])

    if not m[0]:
        return

    url = str(m[0][0])
    url = url.replace('&amp;', '&')
    logger.info("Looking for url %s" % url)

    try:
        story = Story.select().where(Story.url == url).get()
    except:
        message.reply("Sorry, I don't have stats for %s" % url)
        return

    story_time_bucket = story.time_bucket()
    stats_per_slug = analytics.get_linger_data_for_story(story)

    if len(stats_per_slug) is not 0:
        reply = ("Here's what I know about the graphics on _%s_:") % (
            story.name
        )

        fields = []
        for stat in stats_per_slug:
            time = TimeTools.humanist_time_bucket(stat['stats'])
            fields.append({
                "title": stat['slug'],
                "value": time,
                "short": True
            })

            # rows = analytics.get_linger_histogram(stat['slug'])
            # histogram_url = ChartTools.linger_histogram_link(rows)
        attachments = [
            {
                "fallback": story.name + " update",
                "color": "#eeeeee",
                "title": story.name,
                "title_link": story.url,
                "fields": fields
            }
        ]

        # Use send_message instead of message.reply, otherwise we lose
        # the bot icon.
        slackTools.send_message(message.body['channel'], reply, attachments)

patterns = [
    ['linger update', LINGER_RATE_REGEX, handle_linger_slug_question],
    ['linger details', GRUBER_URLINTEXT_PAT, handle_linger_update]
]


"""
We start out responding to everything -- there doesn't seem to be a way for a
more specific regex to take precedence over the generic case.
"""
@respond_to('.*', re.IGNORECASE)
def response_dispatcher(message, text=None):
    if not text:
        text = message.body['text']

    for pattern in patterns:
        match = pattern[1].findall(text)
        if match:
            pattern[2](message)
            return

    message.reply("Hi! I got your message, but I don't know enough yet to respond to it.")


"""
Listen passively for any mention of Carebot: at the beginning of the line
If we don't listen to this generic message, users would have to use exact
syntax to get a response out of carebot.
"""
@listen_to('^@*[Cc]arebot[:|,]\s*(.*)', re.IGNORECASE)
def reply(message, text):
    response_dispatcher(message, text)

def main():
    bot = Bot()
    bot.run()

if __name__ == "__main__":
    main()
