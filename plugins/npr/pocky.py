import copytext
import datetime
from oauth import get_document
import os
import pytz
import re
from sets import Set

import app_config
from util.models import Story
from plugins.base import CarebotPlugin
from plugins.npr.linger import NPRLingerRate
from util.analytics import GoogleAnalytics


POCKY_TRACKER = os.environ.get('POCKY_SHEET')
DATA_PATH = 'data/pocky.xlsx'

class NPRPocky(CarebotPlugin):
    """
    Get stats on a particular pocky
    """
    POCKY_REGEX = re.compile(ur'pocky', re.IGNORECASE)

    def __init__(self, *args, **kwargs):
        get_document(POCKY_TRACKER, DATA_PATH)
        spreadsheet = copytext.Copy(DATA_PATH)
        self.data = data = spreadsheet['reviews']

        super(NPRPocky, self).__init__(*args, **kwargs)

    def get_listeners(self):
        return [
            ['pocky', self.POCKY_REGEX, self.respond],
        ]

    @staticmethod
    def parse_date(value):
        """
        Attemts to parse a date from Excel into something the rest of the world
        can use.
        """
        value = float(value)
        seconds = (value - 25569) * 86400.0
        parsed = datetime.datetime.utcfromtimestamp(seconds).date()
        return parsed

    def rating_to_color(self, rating):
        rating = rating.strip()

        if rating == '/////':
            return '#099830'
        if rating == '////':
            return '#f3d73a'
        if rating == '///':
            return '#f38d3a'
        if rating == '//':
            return '#f34b3a'
        if rating == '/':
            return '#f34b3a'
        return '#666666'

    def get_result_attachments(self, result):
        d = NPRPocky.parse_date(result['date tasted'])
        formatted_date = d.strftime('%m/%d/%Y')

        fields = [{
            'title': 'Taster',
            'value': result['taster'],
            'short': True
        }, {
            'title': 'Date Tested',
            'value': formatted_date,
            'short': True
        }]

        if result['official flavor description']:
            fields.append({
                'title': 'Official Flavor Description',
                'value': result['official flavor description'],
                'short': False
            })

        fields.append({
            'title': 'Stick Impression',
            'value': result['stick impression'],
            'short': False
        })
        fields.append({
            'title': 'Flavor Impression',
            'value': result['flavor impression'],
            'short': False
        })

        if result['miscellaneous observations']:
            fields.append({
                'title': 'Miscellaneous Observations',
                'value': result['miscellaneous observations'],
                'short': False
            })

        fields.append({
            'title': 'Overall Rating',
            'value': result['overall rating\n(1 - 5 sticks)'],
            'short': True
        })

        return {
            'fallback': result['name'],
            'color': self.rating_to_color(result['overall rating\n(1 - 5 sticks)']),
            'title': result['name'],
            'fields': fields,
        }

    def respond(self, message):
        query = message.body['text'].strip().lstrip('pocky ').lower()

        results = []
        for row in self.data:
            if query in row['official flavor description'].lower() or query in row['name'].lower():
                results.append(row)

        attachments = []
        for result in results:
            attachments.append(self.get_result_attachments(result))

        if len(results) is not 0:
            return {
                'text': "Ok, here's what I know about {0} pocky".format(query),
                'attachments': attachments
            }

        return {
            'text': "I couldn't find anything about {0} pocky".format(query)
        }

    def get_update_message(self, story):
        """
        Handle periodic checks on the pocky
        """

        if story.last_bucket:
            # Really, let's just send one update
            print "We already announced this pocky."
            return

        attributes = story.slug.split(' - ')

        for row in self.data:
            if attributes[0] in row['official flavor description'] and attributes[1] in row['taster']:
                return {
                    'text': "New pocky stat:",
                    'attachments': [
                        self.get_result_attachments(row)
                    ]
                }




