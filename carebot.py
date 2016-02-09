from analytics import Analytics

from slackbot.bot import Bot
from slackbot.bot import respond_to
from slackbot.bot import listen_to
import re

@respond_to('.*', re.IGNORECASE)
def hi(message):
    message.reply("Hi! There's a lot I don't understand yet, but I'm learning.")

@listen_to('Carebot is cool')
def cool(message):
    message.reply('Sure am!!')

@respond_to('[Hh]ow many people donated on (\w*)?', re.IGNORECASE)
def donators(message, category):
    a = Analytics()
    data = a.donation_data(category)
    if data.get('rows', []):
        row = data.get('rows')[0]
        cell = row[0]
        print(cell)
        message.reply(u"I don't know exactly how many people donated yet, but there were %s donation events on %s." % (cell, category))
    else:
        message.reply("I wasn't able to figure out how many people donated on %s" % category)


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
