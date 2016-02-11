#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright 2014 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


# Query constructor: https://ga-dev-tools.appspot.com/query-explorer/
#

"""
Simple intro to using the Google Analytics API v3.

This application demonstrates how to use the python client library to access
Google Analytics data. The sample traverses the Management API to obtain the
authorized user's first profile ID. Then the sample uses this ID to
contstruct a Core Reporting API query to return the top 25 organic search
terms.

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

    """
    # Try to make a request to the API. Print the results or handle errors.
    try:
      results = get_event_data(service)
      print_results(results)

    except TypeError as error:
      # Handle errors in constructing a query.
      print(('There was an error in constructing your query : %s' % error))

    except HttpError as error:
      # Handle API errors.
      print(('Arg, there was an API error : %s : %s' %
             (error.resp.status, error._get_reason())))

    except AccessTokenRefreshError:
      # Handle Auth errors.
      print ('The credentials have been revoked or expired, please re-run '
             'the application to re-authorize')
    """

  def donation_data(self, category):
    """Executes and returns data from the Core Reporting API.

    This queries the API for XXX

    Args:
      service: The service object built by the Google API Python client library.
      profile_id: String The profile ID from which to retrieve analytics data.

    Returns:
      The response returned from the Core Reporting API.
    """

    self.results = self.service.data().ga().get(
        ids='ga:100688391', #'ga:' + profile_id,
        start_date='90daysAgo',
        end_date='today',
        metrics='ga:totalEvents',
        # dimensions='ga:date',
        sort='-ga:totalEvents',
        filters='ga:eventCategory==%s;ga:eventLabel==donate' % category,
        start_index='1',
        max_results='25').execute()

    return self.results
    # ga:eventCategory==carebot
    # ga:eventLabel==10m
    # dimensions: eventCategory, eventLabel, eventAction

    #TODO
    #        sampling_level='HIGHER_PRECISION',


  def get_time_visible(self, category):
    """Executes and returns data from the Core Reporting API.

    This queries the API for XXX

    Args:
      service: The service object built by the Google API Python client library.
      profile_id: String The profile ID from which to retrieve analytics data.

    Returns:
      The response returned from the Core Reporting API.
    """

    self.results = self.service.data().ga().get(
        ids='ga:100693289', #'ga:' + profile_id,
        start_date='30daysAgo',
        end_date='today',
        metrics='ga:totalEvents',
        dimensions='ga:eventLabel,ga:eventAction',
        sort='-ga:totalEvents',
        filters='ga:eventCategory==%s;ga:eventLabel==on-screen',
        start_index='1',
        max_results='25').execute()

    # ga:eventCategory==carebot
    # ga:eventLabel==10m
    # dimensions: eventCategory, eventLabel, eventAction

  def print_results(self):
    """Prints out the results.

    This prints out the profile name, the column headers, and all the rows of
    data.

    Args:
      results: The response returned from the Core Reporting API.
    """

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

a = Analytics()
data = a.donation_data('elections16')
if data.get('rows', []):
  row = data.get('rows')[0]
  cell = row[0]
  print(cell)

# a.print_results()
