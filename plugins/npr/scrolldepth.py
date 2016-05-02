from util.analytics import GoogleAnalytics
from util.config import Config
from plugins.base import CarebotPlugin


class NPRScrolldepth(CarebotPlugin):
    """
    Get scroll depth stats on NPR stories
    """

    def __init__(self, *args, **kwargs):
        super(NPRScrolldepth, self).__init__(*args, **kwargs)


    def get_slug_query_params(self, slug):
        """
        Given a slug, get parameters needed to query google analytics for the
        scroll depth
        """
        filters = 'ga:eventCategory==%s;ga:eventAction==scroll-depth' % slug

        params = {
            'ids': 'ga:{0}'.format(self.team['ga_org_id']),
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

        # Only take the first 10 rows.
        truncated = rows[:10]
        return truncated


    def get_median(self, data):
        """
        10%: 200
        20%: 150
        30%: 120
        40%: 110
        50%: 100
        60%: 70
        70%: 55
        80%: 30
        90%: 20
        100%: 15
        """



    def get_total_people(self, data):
        """
        Find the tuple with the max number of people.
        """
        return max(data, key=lambda item:item[1])[1]


    def get_chart(self, data):
        pass


    def get_update_message(self):
        """
        For each slug in the story, get the analytics we need, and craft
        an update message for each.
        """
        story_slugs = self.story.slug_list()
        messages = []

        for slug in story_slugs:
            # Query Google Analytics
            params = self.get_slug_query_params(slug=slug)
            data = GoogleAnalytics.query_ga(params)
            if not data.get('rows'):
                logger.info('No rows found for slug %s' % slug)

            # Clean up the data
            clean_data = self.clean_data(data)
            median = self.get_median(clean_data)
            total_people = self.get_total_people(clean_data)
            friendly_people = "{:,}".format(total_people) # Comma-separated #s

            # Craft the mssages
            message = "%s people got a median of %s% down the page" % people, median



    # def responds_to(self, story):

