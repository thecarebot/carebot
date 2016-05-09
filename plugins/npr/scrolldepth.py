import logging
import matplotlib
import matplotlib.pyplot as plt
from PIL import Image
import re
import requests
import StringIO
import tempfile

import app_config
from util.analytics import GoogleAnalytics
from util.chart import ChartTools
from util.models import Story
from util.s3 import Uploader
from plugins.base import CarebotPlugin

s3 = Uploader()

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class NPRScrollDepth(CarebotPlugin):
    """
    Get scroll depth stats on NPR stories
    """

    SLUG_SEARCH_REGEX = re.compile(ur'slug ((\w*-*)+)')

    def __init__(self, *args, **kwargs):
        super(NPRScrollDepth, self).__init__(*args, **kwargs)

    def get_listeners(self):
        """
        Associate regular expression matches to the appropriate handler
        """
        return [
            ['depth', self.SLUG_SEARCH_REGEX, self.handle_slug_inquiry],
            # ['linger-url', self.GRUBER_URLINTEXT_PAT, self.handle_url_inquiry],
        ]

    def get_slug_query_params(self, team, slug=None):
        """
        Given a slug, get parameters needed to query google analytics for the
        scroll depth
        """
        filters = 'ga:eventCategory==%s;ga:eventAction==scroll-depth' % slug

        params = {
            'ids': 'ga:{0}'.format(team['ga_org_id']),
            'start-date': '90daysAgo', # start_date.strftime('%Y-%m-%d'),
            'end-date': 'today',
            'metrics': 'ga:users,ga:eventValue',
            'dimensions': 'ga:eventLabel',
            'filters': filters,
            'max-results': app_config.GA_RESULT_SIZE,
            'samplingLevel': app_config.GA_SAMPLING_LEVEL,
            'start-index': 1,
        }

        return params

    @staticmethod
    def fill_in_max(data):
        """
        Sometime people start at 20, 30, 40% of the article read because their
        screens are lare or the article is short.

        fill_in_max finds the starting bucket with the largest number of people
        and fills in all previous buckets with that count.that

        That way we get an accurate count of how many people read the top of the
        article.
        """
        max_people = max(data, key=lambda item:item[1])[1]
        for row in data:
            if row[1] == max_people:
                break

            row[1] = max_people

        # Calculate the percentage of users
        for row in data:
            pct = round((row[1] / float(max_people)) * 100)
            row.append(int(pct))

        return data

    def clean_data(self, data):
        """
        Fix data types, truncate the data, and otherwise make it fit for
        consumption.
        """
        rows = []
        for row in data:
            row[0] = int(row[0]) # Percent depth on page
            row[1] = int(row[1]) # Total users
            row[2] = int(row[2]) # Seconds on page
            rows.append(row)

        # Sort the row data from 10% => 100%
        rows.sort(key=lambda tup: tup[0])

        rows = NPRScrollDepth.fill_in_max(rows)

        # Only take the first 10 rows.
        truncated = rows[:10]
        return truncated

    def get_median(self, data):
        """
        Take the scroll depth data we have (number of people per percent)
        Then calculate how many people only got to THAT bucket (aka didn't get
        to the next percent bucket)
        """
        length = len(data)
        for i, row in enumerate(data):
            if not i == length - 1:
                row[1] = row[1] - data[i + 1][1]

        lst = []

        # Flatten the [percent, count] tuples
        # This is a really inefficient way to do this!
        for bucket in data:
            for _ in range(bucket[1]):
                lst.append(bucket[0])

        median = GoogleAnalytics.median(lst)
        return int(median)

    def get_total_people(self, data):
        """
        Find the tuple with the max number of people.
        """
        return max(data, key=lambda item:item[1])[1]

    def get_chart(self,
                  rows,
                  median=None,
                  labels=None):
        """
        Create a scroll depth histogram
        """
        if labels is None:
            labels = ['100%', '90%', '80%', '70%', '60%', '50%', '40%', '30%', '20%', '10%']
        r = range(1, len(rows) + 1)
        data = []

        # Rows are drawn "upside down" so we need to reverse them:
        rows.reverse()

        for row in rows:
            data.append(row[3])

        # Set the chart size
        plt.figure(figsize=(2,4), dpi=100)

        # Remove the plot frame lines. They are unnecessary chartjunk.
        ax = plt.subplot(1, 1, 1)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.spines["bottom"].set_visible(False)
        ax.spines["left"].set_visible(False)

        # Ensure that the axis ticks only show up on the bottom and left of the plot.
        # Ticks on the right and top of the plot are generally unnecessary chartjunk.
        ax.get_xaxis().tick_bottom()
        ax.get_yaxis().tick_left()

        # Configure x-axis ticks
        plt.xlim(0, 100)
        ax.tick_params(axis='x', colors='#b8b8b8', labelsize=8, labelbottom='off')
        plt.axes().xaxis.set_ticks_position('none')

        # Configure y-axis ticks
        plt.axes().yaxis.set_ticks_position('none')
        ax.tick_params(axis='y', colors='#b8b8b8', labelsize=7)
        ax.yaxis.label.set_fontsize(10)
        plt.yticks(r, labels)

        chart = plt.barh(r, data, align="center")

        for index, value in enumerate(data):
            chart[index].set_color('#4b7ef0')

        # TODO: Median line
        # for bar in chart:
        #     width = bar.get_width()
        #     print width
        #     print bar.get_y()
        #     if bar.get_y() == 1.6:
        #         print
        #         ax.text(
        #             bar.get_y() + bar.get_height()/2.,
        #             1.05 * width,
        #             "MED",
        #             ha='center',
        #             va='bottom',
        #             color='#b8b8b8',
        #             fontsize=8
        #         )

        with tempfile.TemporaryFile(suffix=".png") as tmpfile:
            plt.savefig(tmpfile, bbox_inches='tight')
            tmpfile.seek(0) # Rewind the file to the beginning
            url = s3.upload(tmpfile)
            return url

    def get_slug_message(self, slug, story=None):
        # Try to match the story to a slug to accurately get a team
        # The Google Analytics property ID comes from the team config
        # We use the default team if none is found
        stories = Story.select().where(Story.slug.contains(slug))
        team = self.config.get_team_for_stories(stories)

        params = self.get_slug_query_params(team=team, slug=slug)
        data = GoogleAnalytics.query_ga(params)
        if not data.get('rows'):
            logger.info('No rows found for slug %s' % slug)
            return

        # Clean up the data
        clean_data = self.clean_data(data.get('rows'))
        total_people = self.get_total_people(clean_data)
        friendly_people = "{:,}".format(total_people) # Comma-separated #s
        median = self.get_median(clean_data)

        # Set up the chart
        scroll_histogram_url = self.get_chart(clean_data)
        if story:
            scroll_histogram_url = ChartTools.add_screenshot_to_chart(story,
                                                                scroll_histogram_url)

        # TODO: Not confident in median calculations so far
        # text = "*%s people* got a median of *%s percent* down the page." % (friendly_people, median)
        text = ''
        attachments = [{
            "fallback": slug + " update",
            "color": "#eeeeee",
            "title": "How far down did people scroll?",
            "image_url": scroll_histogram_url
        }]

        return {
            'text': text,
            'attachments': attachments
        }

    def handle_slug_inquiry(self, message):
        """
        Respond to an inquiry about the slug with stats and charts
        """
        match = re.search(self.SLUG_SEARCH_REGEX, message.body['text'])
        slug = match.group(1)

        if slug:
            return self.get_slug_message(slug)

    def get_update_message(self, story):
        """
        Only one slug in the story (should be the first) will return scroll
        depth results.

        TODO: Will need to handle the case when it's not the first slug
        reporting depth data.
        """
        story_slugs = story.slug_list()
        team = self.config.get_team_for_story(story)

        return self.get_slug_message(story_slugs[0])

