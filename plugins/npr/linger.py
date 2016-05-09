import inflect
import logging
import matplotlib
import matplotlib.pyplot as plt
import re

import app_config
from plugins.base import CarebotPlugin
from util.analytics import GoogleAnalytics
from util.config import Config
from util.models import Story
from util.s3 import Uploader
from util.time import TimeTools

config = Config()
inflector = inflect.engine()
s3 = Uploader()

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class NPRLingerRate(CarebotPlugin):
    """
    Get linger rate stats on NPR stories
    Eg '1,000 people spent a median 10 seconds studying the graphic'
    """

    SLUG_SEARCH_REGEX = re.compile(ur'slug ((\w*-*)+)')
    GRUBER_URLINTEXT_PAT = re.compile(ur'(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:\'".,<>?\xab\xbb\u201c\u201d\u2018\u2019]))')

    def __init__(self, *args, **kwargs):
        super(NPRLingerRate, self).__init__(*args, **kwargs)

    def get_listeners(self):
        """
        Associate regular expression matches to the appropriate handler
        """
        return [
            ['linger', self.SLUG_SEARCH_REGEX, self.handle_slug_inquiry],
            ['linger-url', self.GRUBER_URLINTEXT_PAT, self.handle_url_inquiry],
        ]

    def get_query_params(self, team, slug=None, start_date=None):
        """
        Set up the Google Analytics query parameters for the linger rate stat
        """
        filters = 'ga:eventAction==on-screen;ga:eventLabel==10s,ga:eventLabel==20s,ga:eventLabel==30s,ga:eventLabel==40s,ga:eventLabel==50s,ga:eventLabel==1m,ga:eventLabel==2m,ga:eventLabel==3m,ga:eventLabel==4m,ga:eventLabel==5m,ga:eventLabel==10m'

        if slug:
            filters = ('ga:eventCategory==%s;' % slug) + filters

        if not start_date:
            start_date = '90daysAgo'

        params = {
            'ids': 'ga:{0}'.format(team['ga_org_id']),
            'start-date': start_date, # start_date.strftime('%Y-%m-%d'),
            'end-date': 'today',
            'metrics': 'ga:totalEvents',
            'dimensions': 'ga:eventLabel',
            'sort': '-ga:totalEvents',
            'filters': filters,
            'max-results': app_config.GA_RESULT_SIZE,
            'samplingLevel': app_config.GA_SAMPLING_LEVEL,
            'start-index': 1,
        }

        return params

    def clean_data(self, data):
        """
        Fix data types, truncate the data, and otherwise make it fit for
        consumption.
        """
        rows = []
        for row in data['rows']:
            time = row[0]
            seconds = 0
            if 'm' in time:
                time = time[:-1] # remove 'm' from the end
                seconds = int(time) * 60
            else:
                time = time[:-1] # remove 's'
                seconds = int(time)

            row[0] = seconds
            row[1] = int(row[1])
            rows.append(row)

        # Calculate the number of visitors in each bucket
        for index, row in enumerate(rows):
            if index == len(rows) - 1:
                continue

            next_row = rows[index + 1]
            row[1] = row[1] - next_row[-1]

        # Exclude everybody in the last bucket
        # (they've been lingering for way too long -- 10+ minutes)
        rows = rows[:-1]
        return rows

    def get_linger_data(self, team, slug=None):
        params = self.get_query_params(team=team, slug=slug)
        data = GoogleAnalytics.query_ga(params)

        if not data.get('rows'):
            logger.info('No rows found, done.')
            return False

        rows = self.clean_data(data)
        return rows

    @staticmethod
    def median_of_time_buckets(time_buckets):
        """
        Take a list of [seconds, count] tuples and get the median seconds.
        """
        lst = []

        # Flatten the [seconds, count] tuples
        # This is a really bad way to do this!
        # Yuuuuge number of objects created!
        for bucket in time_buckets:
            for _ in range(bucket[1]):
                lst.append(bucket[0])

        median = GoogleAnalytics.median(lst)
        return int(median)

    @staticmethod
    def get_median(linger_rows):
        """
        Get the median number of seconds spent on the data in nice, easy
        to consume formats.
        """
        # Get the average number of seconds
        total_seconds = 0
        total_people = 0
        for row in linger_rows:
            total_seconds = total_seconds + (row[0] * row[1])
            total_people = total_people + row[1]

        # average_seconds = total_seconds/total_people # average
        average_seconds = NPRLingerRate.median_of_time_buckets(linger_rows) # median
        minutes = int(average_seconds / 60)
        seconds = average_seconds % 60

        return {
            'total_people': total_people,
            'raw_avg_seconds': average_seconds,
            'minutes': minutes,
            'seconds': seconds
        }

    def get_histogram_url(self, rows, median=None):
        """
        Create and upload a histogram chart for the linger rate data
        """
        r = range(1, len(rows) + 1)

        labels = ['10s', '20', '30', '40', '50', '1m', '2m', '3m', '4m', '5m+',]
        colors = [
            '#ffcc00',
            '#ffcc00',
            '#ffcc00',
            '#ffcc00',
            '#ffcc00',
            '#12b5a3',
            '#12b5a3',
            '#12b5a3',
            '#12b5a3',
            '#3612b5',
        ]

        data = []
        for row in rows:
            data.append(row[1])

        # Set the chart size
        plt.figure(figsize=(4,2), dpi=100)

        # Remove the plot frame lines. They are unnecessary chartjunk.
        ax = plt.subplot(111)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.spines["bottom"].set_visible(False)
        ax.spines["left"].set_visible(False)

        # Ensure that the axis ticks only show up on the bottom and left of the plot.
        # Ticks on the right and top of the plot are generally unnecessary chartjunk.
        ax.get_xaxis().tick_bottom()
        ax.get_yaxis().tick_left()

        # Configure y-axis ticks
        # plt.ylim(0, 100)
        plt.axes().yaxis.set_ticks_position('none')
        ax.tick_params(axis='y', colors='#b8b8b8', labelsize=8)
        plt.axes().yaxis.set_major_formatter(
            matplotlib.ticker.FuncFormatter(lambda x, p: format(int(x), ',')))

        # Configure x-axis ticks
        plt.axes().xaxis.set_ticks_position('none')
        ax.tick_params(axis='x', colors='#b8b8b8', labelsize=8)
        plt.xticks(r, labels)

        chart = plt.bar(r, data, align="center")

        for index, color in enumerate(colors):
            chart[index].set_color(color)

        # Add the median marker
        if median:
            position = (median['raw_avg_seconds'] / 10) - 1
            bar = chart[position]
            height = bar.get_height()
            ax.text(
                bar.get_x() + bar.get_width()/2.,
                1.05*height,
                "MED",
                ha='center',
                va='bottom',
                color='#b8b8b8',
                fontsize=8
            )

        # TODO: Save to a better temp path.
        plt.savefig('tmp.png', bbox_inches='tight')
        f = open('tmp.png', 'rb')
        url = s3.upload(f)
        return url

    def get_stats_for_slug(self, team, slug):
        """
        Return clean stats about how long people looked at a slug
        """
        linger_rows = self.get_linger_data(team=team, slug=slug)

        if not linger_rows:
            return False

        median = NPRLingerRate.get_median(linger_rows)
        return {
            'median': median,
            'people': "{:,}".format(median['total_people']),
            'time_text': TimeTools.humanist_time_bucket(median)
        }

    def get_update_message(self, story):
        """
        Handle periodic checks on the metric.
        For each slug in the story, get the analytics we need, and craft
        an relevant update message.
        """
        story_slugs = story.slug_list()
        team = config.get_team_for_story(story)
        hours_since = TimeTools.hours_since(story.date)

        messages = []

        if len(story_slugs) > 1:
            # Some stories have many slugs.
            # We break out the stats into a nice little grid so they're
            # easier to read.
            message = ("%s hours in and here's what I know about the graphics on _%s_:") % (
                hours_since,
                story.name
            )

            fields = []
            for slug in story_slugs:
                stats = self.get_stats_for_slug(team=team, slug=slug)
                if stats:
                    fields.append({
                        "title": slug,
                        "value": stats['time_text'],
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

            return {
                'text': message,
                'attachments': attachments
            }

        else:
            # For stories with only one slug, we have a slightly different
            # message:
            stats = self.get_stats_for_slug(team=team, slug=story_slugs[0])
            if stats:
                message = "%s hours in, *%s users* have spent a median *%s* on _%s_ (`%s`)" % (
                    hours_since,
                    stats['people'],
                    stats['time_text'],
                    story.name,
                    story_slugs[0]
                )

                return {
                    'text': message
                }

    def handle_url_inquiry(self, message):
        """
        Respond to "How is http://example.com/foo doing?"
        """
        if 'doing' not in message.body['text']:
            return

        match = self.GRUBER_URLINTEXT_PAT.findall(message.body['text'])

        if not match[0]:
            return

        url = str(match[0][0])
        url = url.replace('&amp;', '&')
        logger.info("Looking for url %s" % url)

        try:
            story = Story.select().where(Story.url == url).get()
        except:
            return {
                'text': "Sorry, I don't have stats for %s" % url
            }

        return self.get_update_message(story)

    def handle_slug_inquiry(self, message):
        """
        Respond to an inquiry about the slug with stats and charts
        """
        match = re.search(self.SLUG_SEARCH_REGEX, message.body['text'])
        slug = match.group(1)

        if slug:

            # Try to match the story to a slug to accurately get a team
            # The Google Analytics property ID comes from the team config
            # We use the default team if none is found
            stories = Story.select().where(Story.slug.contains(slug))
            team = config.get_team_for_stories(stories)

            linger_rows = self.get_linger_data(team=team, slug=slug)

            if not linger_rows:
                return {
                    'text': "Sorry, I wasn't able to find linger rate stats for %s" % slug
                }

            median = NPRLingerRate.get_median(linger_rows)
            print "Got median"
            print median
            people = "{:,}".format(median['total_people'])
            time_text = TimeTools.humanist_time_bucket(median)

            reply = u"*%s* people spent a median *%s* on `%s`." % (people, time_text, slug)

            reply += '\n\nThis graphic appears in %s %s I am tracking:' % (inflector.number_to_words(len(stories)),
                inflector.plural('story', len(stories)))

            for story in stories:
                reply += '\n' + '*<%s|%s>*' % (story.url, story.name.strip())

            # Get linger rate data for charting.

            all_graphics_rows = self.get_linger_data(team=team)
            all_graphics_median = NPRLingerRate.get_median(all_graphics_rows)

            attachments = [
                {
                    "fallback": slug + " update",
                    "color": "#eeeeee",
                    "title": slug,
                    "image_url": self.get_histogram_url(linger_rows, median)
                },
                {
                    "fallback": slug + " update",
                    "color": "#eeeeee",
                    "title": "How all graphics performed",
                    "image_url": self.get_histogram_url(all_graphics_rows,
                                                        all_graphics_median)
                }
            ]

            return {
                'text': reply,
                'attachments': attachments
            }
