from slackbot.bot import Bot
from slackbot.bot import respond_to
from slackbot.bot import listen_to
import re

@respond_to('.*', re.IGNORECASE)
def hi(message):
    message.reply('Hello world!')

@listen_to('Carebot is cool')

@listen_to('Carebot is cool')
def cool(message):
    message.reply('Sure am!!')

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
