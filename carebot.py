from analytics import Analytics
import datetime
from models import Story
import re
from slackbot.bot import Bot
from slackbot.bot import respond_to
from slackbot.bot import listen_to

# Set up analytics to handle inquiries
a = Analytics()

LINGER_RATE_REGEX = '[Ww]hat is the linger rate on ((\w*-*)+)?'
START_TRACKING_REGEX = '[Tt]rack ((\w*-*)+)'

"""
Given a message, figure out what is being requested.def
"""
def parse_message(text):
    m = re.search('[Hh]ow many people donated on (\w*)?', text)
    if m:
        return 'donation'

    m = re.search(LINGER_RATE_REGEX, text)
    if m:
        return 'linger'

    m = re.search(START_TRACKING_REGEX, text)
    if m:
        return 'track'

    return False

"""
Get information on how many people clicked the donate button on a story
"""
def get_donation_data(message, category):
    data = a.donation_data(category)

    if data.get('rows', []):
        row = data.get('rows')[0]
        print(row[0])
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

def handle_linger_question(message):
    m = re.search(LINGER_RATE_REGEX, message.body['text'])

    if not m:
        return False

    slug = m.group(1)

    if slug:
        rate = a.get_linger_rate(slug)
        if rate:
            message.reply(u"%s people spent an average of %s minutes and %s seconds on %s." % (rate[0], rate[1], rate[2], slug))
            return True
        else:
            message.reply("I wasn't able to figure out the linger rate of %s" % slug)
            return False
    else:
        return False

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
        print("handling linger")
        handle_linger_question(message)
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
