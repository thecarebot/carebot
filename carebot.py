from analytics import Analytics

from slackbot.bot import Bot
from slackbot.bot import respond_to
from slackbot.bot import listen_to
import re

# Set up analytics to handle inquiries
a = Analytics()

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


# We start out responding to everything -- there doesn't seem to be a way for a
# more specific regex to take precedence over the generic case.
@respond_to('.*', re.IGNORECASE)
def response_dispatcher(message):
    if not handle_donation_question(message):
        message.reply("Hi! There's a lot I don't understand yet, but I'm learning.")

# Carebot listens for questions!
# Listen passively for any mention of "Carebot, ..."
@listen_to('^[Cc]arebot,*\s*(.*)', re.IGNORECASE)
def reply(message, text):
    text = text.decode('utf-8')
    print message.body
    message.reply(u'Ok, you asked me "%s"' % text)

def main():
    bot = Bot()
    bot.run()

if __name__ == "__main__":
    main()
