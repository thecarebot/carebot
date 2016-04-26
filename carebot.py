# from analytics import Analytics
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
from scrapers.nprapi import NPRAPIScraper
from util.config import Config
from util.chart import ChartTools
from util.models import Story
from util.slack import SlackTools
from util.time import TimeTools

slackTools = SlackTools()
npr_api_scraper = NPRAPIScraper()
config = Config()
inflector = inflect.engine()

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Set up analytics to handle inquiries
analytics = GoogleAnalyticsScraper()

LINGER_RATE_REGEX = re.compile(ur'slug ((\w*-*)+)')
SCROLL_RATE_REGEX = re.compile(ur'scroll ((\w*-*)+)')
GRUBER_URLINTEXT_PAT = re.compile(ur'(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:\'".,<>?\xab\xbb\u201c\u201d\u2018\u2019]))')
START_TRACKING_REGEX = re.compile(ur'[Tt]rack ((\w*-*)+)')
HELLO_REGEX = re.compile(ur'Hello', re.IGNORECASE)
HELP_REGEX_1 = re.compile(ur'Help', re.IGNORECASE)
HELP_REGEX_2 = re.compile(ur'What can you do', re.IGNORECASE)
HELP_REGEX_3 = re.compile(ur'What are you up to', re.IGNORECASE)

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

    slackTools.send_message(message.body['channel'], "In the past 7 days, I've tracked %s stories and %s graphics." % (len(stories), len(slugs)))
    slackTools.send_message(message.body['channel'], "%s people looked at graphics on those stories. Here's how much time they spent:" % total_users, attachments, unfurl_links=False)

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

    slackTools.send_message(message.body['channel'], "Here's everything:", attachments, unfurl_links=False)



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

            slackTools.send_message(message.body['channel'], reply, attachments, unfurl_links=False)

        else:
            message.reply("I wasn't able to find scroll data for %s" % slug)


def handle_slug_question(message):
    m = re.search(LINGER_RATE_REGEX, message.body['text'])

    if not m:
        return

    slug = m.group(1)

    if slug:
        stories = Story.select().where(Story.slug.contains(slug))
        if stories:
            team = config.get_team_for_story(stories[0])
        else:
            team = config.get_default_team()

        median = analytics.get_linger_rate(team=team, slug=slug)

        message.reply("Ok! I'm looking up %s. This may take a second." % slug)

        if median:
            people = "{:,}".format(median['total_people'])
            time_text = TimeTools.humanist_time_bucket(median)
            reply = u"*%s* people spent a median *%s* on `%s`." % (people, time_text, slug)

            # List the stories this slug appears on
            reply += '\n\nThis graphic appears in %s %s:' % (inflector.number_to_words(len(stories)),
                inflector.plural('story', len(stories)))

            for story in stories:
                reply += '\n' + '*<%s|%s>*' % (story.url, story.name.strip())

            # Get linger rate data
            linger_rows = analytics.get_linger_rows(team=team, slug=slug)
            linger_histogram_url = ChartTools.linger_histogram_link(linger_rows, median)

            all_graphics_rows = analytics.get_linger_rows(team=team)
            all_graphics_median = analytics.get_linger_rate(team=team)
            all_histogram = ChartTools.linger_histogram_link(all_graphics_rows, all_graphics_median)

            attachments = [
                {
                    "fallback": slug + " update",
                    "color": "#eeeeee",
                    "title": slug,
                    "image_url": linger_histogram_url
                },
                {
                    "fallback": slug + " update",
                    "color": "#eeeeee",
                    "title": "How all graphics performed",
                    "image_url": all_histogram
                }
            ]

            # Get scroll data, if any.
            scroll_depth_rows = analytics.get_depth_rate(team=team, slug=slug)
            if scroll_depth_rows:
                scroll_histogram_url = ChartTools.scroll_histogram_link(scroll_depth_rows)

                if stories[0].screenshot:
                    scroll_histogram_url = ChartTools.add_screenshot_to_chart(stories[0].screenshot, scroll_histogram_url)

                attachments.append({
                    "fallback": slug + " update",
                    "color": "#eeeeee",
                    "title": "How far down did people scroll?",
                    "image_url": scroll_histogram_url
                })


            slackTools.send_message(message.body['channel'], reply, attachments, unfurl_links=False)

        else:
            message.reply("I wasn't able to figure out the linger rate of %s" % slug)

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
            story.name.strip()
        )

        fields = []
        for stat in stats_per_slug:
            time = TimeTools.humanist_time_bucket(stat['stats'])
            fields.append({
                "title": stat['slug'],
                "value": time,
                "short": True
            })

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

def help(message):
    text = """I'm currently tracking two measures:
1. *On-screen visibility* of a graphic in a story: how much time a user views a \
graphic on their screen
2. *Scroll depth* across a story: how far down the length of a story a user \
scrolled.

I use those to calculate two indicators:
1. *Graphic Linger Rate*: The median visibility of a graphic across all users \
who viewed it.
2. *Engaged Completion Rate*: Percentage of people who start and complete the \
story.

Lately I have been focusing on graphics-only stories. I start tracking a story \
when it is published. I start posting notifications when someone \
adds the story to an RSS feed or story spreadsheet. You'll hear from me every \
4 hours on the first day and twice daily for days two and and three.

If you ask me about a specific graphic, I'll give you the most up to date \
Graphic Linger Rate distribution for the graphic in a nifty histogram. I'll also show \
how the story that graphic is in is comparing to all other graphic stories overall. \
Just mention me with the word "slug" followed by your slug:

> @carebot, how is slug red-rackhams-treasure doing?
> @carebot, what about slug tintin-in-tibet?

I am learning to answer questions so if you have them, please send them over and \
I'll get cracking!
"""

    slackTools.send_message(message.body['channel'], text)



def start_tracking(message):
    m = re.search(START_TRACKING_REGEX, message.body['text'])

    if not m:
        return False

    slug = m.group(1)

    if slug:
        # Check if the slug is in the database.
        try:
            story = Story.select().where(Story.slug.contains(slug)).get()
            message.reply("Thanks! I'm already tracking `%s`, and you should start seeing results within a couple hours." % slug)
        except Story.DoesNotExist:

            # If it's not in the database, start tracking it.
            url = re.search(GRUBER_URLINTEXT_PAT, message.body['text'])

            if not url:
                logger.error("Couldn't find story URL in message %s", message.body['text'])
                message.reply("Sorry, I need a story URL to start tracking.")
                return

            details = npr_api_scraper.get_story_details(url.group(1))

            if not details:
                logger.error("Couldn't find story in API for URL %s", url.group(1))
                message.reply("Sorry, I wasn't able to find that story in the API, so I couldn't start tracking it.")
                return

            # Find out what team we need to save this story to
            channel = slackTools.get_channel_name(message.body['channel'])
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
            message.reply("Ok, I've started tracking `%s`. The first stats should arrive in 4 hours or less." % slug)

    else:
        message.reply("Sorry, I wasn't able to start tracking `%s` right now." % slug)


patterns = [
    ['start tracking', START_TRACKING_REGEX, start_tracking],
    ['linger update', LINGER_RATE_REGEX, handle_slug_question],
    ['scroll update', SCROLL_RATE_REGEX, handle_scroll_slug_question],
    ['linger details', GRUBER_URLINTEXT_PAT, handle_linger_update],
    ['hello', HELLO_REGEX, handle_overview_question],
    ['help', HELP_REGEX_1, help],
    ['help', HELP_REGEX_2, help],
    ['help', HELP_REGEX_3, help]
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
            logger.info("Dispatching to %s with message %s" % (pattern[0], message.body['text']))
            pattern[2](message)
            return # Stop at the first match.

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
    print "Carebot is running. Invite it to a channel to begin."
    bot.run()

if __name__ == "__main__":
    main()
