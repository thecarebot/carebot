# Query constructor: https://ga-dev-tools.appspot.com/query-explorer/
#

"""
Before you begin, you must sigup for a new project in the Google APIs console:
https://code.google.com/apis/console

Then register the project to use OAuth2.0 for installed applications.

Finally you will need to add the client id, client secret, and redirect URL
into the client_secrets.json file that is in the same directory as this sample.

Sample Usage:

  $ python analytics.py
"""
from __future__ import print_function

import argparse
import sys

from googleapiclient.errors import HttpError
from googleapiclient import sample_tools
from oauth2client.client import AccessTokenRefreshError

class Analytics:
  def __init__(self):
    # Authenticate and construct service.
    argv = []
    self.service, flags = sample_tools.init(
        argv, 'analytics', 'v3', __doc__, __file__,
        scope='https://www.googleapis.com/auth/analytics.readonly')

  def donation_data(self, slug):
    self.results = self.service.data().ga().get(
        ids='ga:100688391',
        start_date='90daysAgo',
        end_date='today',
        metrics='ga:totalEvents',
        # dimensions='ga:date',
        sort='-ga:totalEvents',
        filters='ga:eventCategory==%s;ga:eventLabel==donate' % slug,
        start_index='1',
        max_results='25').execute()

    return self.results
    # ga:eventCategory==carebot
    # ga:eventLabel==10m
    # dimensions: eventCategory, eventLabel, eventAction

  def get_linger_rate(self, slug):
    print ("Getting linger rate for " + slug)
    self.results = self.service.data().ga().get(
        ids='ga:100688391', #'ga:' + profile_id,
        start_date='90daysAgo',
        end_date='today',
        metrics='ga:totalEvents',
        dimensions='ga:eventLabel',
        sort='-ga:totalEvents',
        filters='ga:eventCategory==%s;ga:eventAction==on-screen;ga:eventLabel==10s,ga:eventLabel==20s,ga:eventLabel==30s,ga:eventLabel==40s,ga:eventLabel==50s,ga:eventLabel==1m,ga:eventLabel==2m,ga:eventLabel==3m,ga:eventLabel==4m,ga:eventLabel==5m,ga:eventLabel==10m' % slug,
        start_index='1',
        max_results='25').execute()

    if self.results.get('rows', []):
        data = []

        for row in self.results.get('rows'):
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
            data.append(row)

        # Calculate the number of visitors in each bucket
        for index, row in enumerate(data):
            if index == len(data) - 1:
                continue

            next_row = data[index + 1]
            row[1] = row[1] - next_row[-1]

        # Exclude everybody in the last bucket
        # (they've been lingering for way too long -- 10+ minutes)
        data = data [:-1]

        # Get the average number of seconds
        total_seconds = 0
        total_people = 0
        for row in data:
            total_seconds = total_seconds + (row[0] * row[1])
            total_people = total_people + row[1]

        average_seconds = total_seconds/total_people
        minutes = average_seconds / 60
        seconds = average_seconds % 60
        return (total_people, minutes, seconds)



  def print_results(self):
        print()
        print('Profile Name: %s' % self.results.get('profileInfo').get('profileName'))
        print()

        # Print header.
        output = []
        for header in self.results.get('columnHeaders'):
            output.append('%30s' % header.get('name'))
        print(''.join(output))

        # Print data table.
        if self.results.get('rows', []):
            for row in self.results.get('rows'):
                output = []
                for cell in row:
                    output.append('%30s' % cell)
                print(''.join(output))

        else:
            print('No Rows Found')


# Testing -- move to a separate folder
# slugs: elections16
# a = Analytics()
# data = a.get_linger_rate('space-time-stepper-20160208')
# a.print_results()

# if data.get('rows', []):
#   row = data.get('rows')[0]
#   cell = row[0]
#   print(cell)

# a.print_results()
