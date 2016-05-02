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

    LINGER_RATE_REGEX = re.compile(ur'slug ((\w*-*)+)')

    def __init__(self, *args, **kwargs):
        super(NPRLingerRate, self).__init__(*args, **kwargs)

    def get_listeners(self):
        """
        Associate regular expression matches to the appropriate handler
        """
        return [
            ['linger', self.LINGER_RATE_REGEX, self.respond],
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

    def median(self, lst):
        """
        Get the median of a list of numbers
        """
        sorted_lst = sorted(lst)
        list_len = len(lst)
        index = (list_len - 1) // 2

        if list_len % 2:
            return sorted_lst[index]
        else:
            return (sorted_lst[index] + sorted_lst[index + 1])/2.0

    def median_of_time_buckets(self, time_buckets):
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

        median = self.median(lst)
        return int(median)

    def get_median(self, linger_rows):
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
        average_seconds = self.median_of_time_buckets(linger_rows) # median
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

        labels = ['10s', '20', '30', '40', '50', '1m', '2m', '3m', '4m', '5m+']
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

    def get_update_message(self, story):
        """
        TODO
        Handle periodic checks on the metric.
        For each slug in the story, get the analytics we need, and craft
        an relevant update message.
        """
        story_slugs = self.story.slug_list()
        messages = []

        for slug in story_slugs:
            # Query Google Analytics
            params = self.get_query_params(slug=slug, team=team)
            data = GoogleAnalytics.query_ga(params)

            if not data.get('rows'):
                logger.info('No rows found for slug %s' % slug)

            # Clean up the data
            clean_data = self.clean_data(data)
            median = self.get_median(clean_data)
            total_people = self.get_total_people(clean_data)
            friendly_people = "{:,}".format(total_people) # Comma-separated #s

            # Craft the message
            message = "%s hours in and %s have spent a median %s hours on the graphic" % hours, people, median
            return message

    def respond(self, message):
        """
        Respond to an inquiry about the slug with more detail
        """
        match = re.search(self.LINGER_RATE_REGEX, message.body['text'])
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

            median = self.get_median(linger_rows)
            people = "{:,}".format(median['total_people'])
            time_text = TimeTools.humanist_time_bucket(median)

            reply = u"*%s* people spent a median *%s* on `%s`." % (people, time_text, slug)

            reply += '\n\nThis graphic appears in %s %s I am tracking:' % (inflector.number_to_words(len(stories)),
                inflector.plural('story', len(stories)))

            for story in stories:
                reply += '\n' + '*<%s|%s>*' % (story.url, story.name.strip())

            # Get linger rate data for charting.

            all_graphics_rows = self.get_linger_data(team=team)
            all_graphics_median = self.get_median(all_graphics_rows)

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
