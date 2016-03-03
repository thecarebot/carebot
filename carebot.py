# from analytics import Analytics
import datetime
from dateutil.parser import parse
import json
import pytz
import re
from slackbot.bot import Bot
from slackbot.bot import respond_to
from slackbot.bot import listen_to

from scrapers.analytics import GoogleAnalyticsScraper
from util.models import Story
from util.slack import SlackTools
slackTools = SlackTools()

# Set up analytics to handle inquiries
analytics = GoogleAnalyticsScraper()

LINGER_RATE_REGEX = 'slug ((\w*-*)+)'
START_TRACKING_REGEX = '[Tt]rack ((\w*-*)+)'

GRUBER_URLINTEXT_PAT = re.compile(ur'(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:\'".,<>?\xab\xbb\u201c\u201d\u2018\u2019]))')

"""
Given a message, figure out what is being requested.def
"""
def parse_message(text):
    m = re.search('[Hh]ow many people donated on (\w*)?', text)
    if m:
        return 'donation'

    if 'slug' in text:
        m = re.search(LINGER_RATE_REGEX, text)
        if m:
            return 'linger'

    m = re.search(START_TRACKING_REGEX, text)
    if m:
        return 'track'

    m = GRUBER_URLINTEXT_PAT.findall(text)
    if m:
        print("Has URL")
        print(m[0])
        if 'doing' in text:
            return 'linger-update'

    return False

"""
Get information on how many people clicked the donate button on a story
"""
def get_donation_data(message, category):
    data = analytics.donation_data(category)

    if data.get('rows', []):
        row = data.get('rows')[0]
        return row[0]
    else:
        return False

def handle_donation_question(message):
    m = re.search('[Hh]ow many people donated on (\w*)?', message.body['text'])

    if not m:
        return False

    category = m.group(1)

    if category:
        count = get_donation_data(message, category)
        if count:
            message.reply(u"I don't know exactly how many people donated yet, but there were %s donation events on %s." % (count, category))
            return True
        else:
            message.reply("I wasn't able to figure out how many people donated on %s" % category)
            return False
    else:
        return False

def linger_histogram_link(rows):
    chdt='chd=t:' # Chart data
    chco='chco=' # Colors of each bar
    chxl='chxl=1:||0:|' # X-axis labels

    counts = []
    for row in rows:
        print (row)

        if row[0] == 300:
            chco += '3612b5' # color
            chxl += '5%2B'

        elif row[0] >= 60:
            chco +='12b5a3|' # color

            minutes = str(row[0] / 60)
            if minutes == '1':
                chxl += '1m|'
            else:
                chxl += minutes + '|'
        else:
            chco +='ffcc00|' # color

            # Set legend
            if row[0] == 10:
                chxl += '10s|'
            else:
                chxl += str(row[0]) + '|'


        counts.append(str(row[1]))

    chdt += ','.join(counts)

    # Uses the Google Chart API
    # Super deprecated but still running!
    # https://developers.google.com/chart/image/docs/chart_params
    base = 'http://chart.googleapis.com/chart?'
    base += '&'.join([
        chdt, # Data
        chco, # Colors
        chxl, # X-axis Labels
        'cht=bvg',
        'chs=400x200',
        'chxt=x,x,y',
        'chxs=0,b8b8b8,10,0,_|2,N*s*,b8b8b8,10,1,_',
        'chof=png',
        'chma=50,10,15,0', # Padding: l r t b
        'chxp=1,50',
        'chds=a' # Auto-scale
    ])

    # Append chof=validate to debug
    print(base)
    return base


def handle_linger_slug_question(message):
    m = re.search(LINGER_RATE_REGEX, message.body['text'])

    if not m:
        return False

    slug = m.group(1)

    if slug:
        rate = analytics.get_linger_rate(slug)
        if rate:
            people = "{:,}".format(rate['total_people'])
            time_text = humanist_time_bucket(rate)
            reply = u"%s people spent an average of %s on %s." % (people, time_text, slug)

            rows = analytics.get_linger_histogram(slug)
            histogram_url = linger_histogram_link(rows)
            attachments = [
                {
                    "fallback": slug + " update",
                    "text": 'Time users spent on graphic in number of sessions',
                    "color": "#eeeeee",
                    "title": slug,
                    "image_url": histogram_url
                }
            ]

            message.send_webapi(reply, json.dumps(attachments))

            # message.reply()
            return True
        else:
            message.reply("I wasn't able to figure out the linger rate of %s" % slug)
            return False
    else:
        return False


# SUPER HACKY -- ABSTRACT THIS AND TIME_BUCKET ASAP
def seconds_since(a):
    now = datetime.datetime.now(pytz.timezone('US/Eastern'))
    return (now - a).total_seconds()

def time_bucket(t):
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

def humanist_time_bucket(linger):
    time = ''
    if linger['minutes'] > 0:
        time += str(linger['minutes'])
        if linger['minutes'] == 1:
            time += ' minute'
        else:
            time += ' minutes'

    if linger['seconds'] > 0:
        if linger['minutes'] > 0:
            time += ' '

        time += str(linger['seconds'])
        if linger['seconds'] == 1:
            time += ' second'
        else:
            time += ' seconds'

    return time


def handle_linger_update(message):
    m = GRUBER_URLINTEXT_PAT.findall(message.body['text'])

    if not m[0]:
        return False

    url = str(m[0][0])
    url = url.replace('&amp;', '&')
    print("looking for url %s" % url)

    try:
        story = Story.select().where(Story.url == url).get()
    except:
        message.reply("Sorry, I don't have stats for %s" % url)
        return False

    # TODO -- refactor this copied code out from here and fabfile.py
    # Some stories have multiple slugs
    story_slugs = story.slug.split(',')
    story_slugs = [slug.strip() for slug in story_slugs]
    stats_per_slug = []
    story_time_bucket = time_bucket(story.article_posted)

    # Get the linger rate for each
    for slug in story_slugs:
        stats = analytics.get_linger_rate(slug)
        if stats:
            stats_per_slug.append({
                "slug": slug,
                "stats": stats
            })

        else:
            logger.info("No stats found for %s" % (slug))

    if len(stats_per_slug) is not 0:
        print(stats_per_slug)
        print(story_time_bucket)

        reply = ("Here's what I know about the graphics on _%s_:") % (
            story.name
        )

        fields = []
        for stat in stats_per_slug:
            time = humanist_time_bucket(stat['stats'])
            fields.append({
                "title": stat['slug'],
                "value": time,
                "short": True
            })

        rows = analytics.get_linger_histogram(slug)
        histogram_url = linger_histogram_link(rows)
        attachments = [
            {
                "fallback": story.name + " update",
                "color": "#eeeeee",
                "title": story.name,
                "title_link": story.url,
                "fields": fields
            }
        ]

        message.send_webapi(reply, json.dumps(attachments))

        # self.slack.chat.post_message(app_config.LINGER_UPDATE_CHANNEL, message, as_user=True, parse='full', attachments=attachments)



def start_tracking(message):
    m = re.search(START_TRACKING_REGEX, message.body['text'])

    if not m:
        return False

    slug = m.group(1)

    if slug:
        # Check if the slug is in the database.
        try:
            story = Story.select().where(Story.slug == slug).get()
            message.reply("Thanks! I'm already tracking %s, so you should start seeing results within a couple hours." % slug)
        except Story.DoesNotExist:
            # If it's not in the database, start tracking it.
            story = Story.create(slug=slug, tracking_started=datetime.datetime.now())
            story.save()
            message.reply("Ok, I've started tracking %s. The first stats will come in about 4 hours." % slug)
    else:
        message.reply("Sorry, I wasn't able to start tracking %s right now." % slug)

    return True


# We start out responding to everything -- there doesn't seem to be a way for a
# more specific regex to take precedence over the generic case.
@respond_to('.*', re.IGNORECASE)
def response_dispatcher(message, text=None):
    if not text:
        text = message.body['text']

    message_type = parse_message(text);
    print("Got message", text, message_type)

    if message_type == 'track':
        start_tracking(message)
    elif message_type == 'donation':
        handle_donation_question(message)
    elif message_type == 'help':
        pass
    elif message_type == 'linger':
        print("handling slug linger")
        handle_linger_slug_question(message)
    elif message_type == 'linger-update':
        print("Handling linger update")
        handle_linger_update(message)
    else:
        message.reply("Hi! I got your message, but I don't know enough yet to respond to it.")


# Listen passively for any mention of Carebot: at the beginning of the line
@listen_to('^@*[Cc]arebot[:|,]\s*(.*)', re.IGNORECASE)
def reply(message, text):
    response_dispatcher(message, text)

def main():
    bot = Bot()
    # bot._client.rtm_send_message('secret-carebot-test', 'hi there')
    bot.run()

if __name__ == "__main__":
    main()
