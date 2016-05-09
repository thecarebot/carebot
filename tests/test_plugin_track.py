#!/usr/bin/env python

try:
    import unittest2 as unittest
except ImportError:
    import unittest

from mock import patch

import app_config
app_config.DATABASE_NAME = 'carebot_test.db'

from plugins.npr.start_tracking import NPRStartTracking
from util.models import Story
from tests.test_util.db import clear_stories

class TestSpreadsheet(unittest.TestCase):
    @patch('util.slack.SlackTools.get_channel_name')
    def test_start_tracking(self, mock_get_channel_name):
        """
        Test if we can start tracking a new story given only a NPR URL and a
        graphic slug
        """
        mock_get_channel_name.return_value = 'default-channel'
        clear_stories()
        tracker = NPRStartTracking()

        class FakeMessage(object):
            body = {
                'text': '@carebot track slug-a-b-c on http://www.npr.org/sections/13.7/2016/02/16/466109612/was-einstein-wrong',
                'channel': 'default-channel'
            }

        expected = "Ok, I've started tracking `slug-a-b-c` on http://www.npr.org/sections/13.7/2016/02/16/466109612/was-einstein-wrong"
        message = tracker.respond(FakeMessage)
        print message
        assert expected in message['text']

        results = Story.select()
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].url, 'http://www.npr.org/sections/13.7/2016/02/16/466109612/was-einstein-wrong')

    @patch('util.slack.SlackTools.get_channel_name')
    def test_change_tracking(self, mock_get_channel_name):
        """
        Check if we can start tracking a URL, then update the slugs that are
        tracked on it
        """
        mock_get_channel_name.return_value = 'default-channel'
        clear_stories()
        tracker = NPRStartTracking()

        class FakeMessage(object):
            body = {
                'text': '@carebot track slug-a-b-c on http://www.npr.org/sections/13.7/2016/02/16/466109612/was-einstein-wrong',
                'channel': 'default-channel'
            }

        expected = "Ok, I've started tracking `slug-a-b-c` on http://www.npr.org/sections/13.7/2016/02/16/466109612/was-einstein-wrong"
        message = tracker.respond(FakeMessage)
        assert expected in message['text']

        # Now try to change the slug
        FakeMessage.body['text'] = '@carebot track slug-a-b-c,slug-x-y-z on http://www.npr.org/sections/13.7/2016/02/16/466109612/was-einstein-wrong'
        message = tracker.respond(FakeMessage)
        results = Story.select()
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].url, 'http://www.npr.org/sections/13.7/2016/02/16/466109612/was-einstein-wrong')
        self.assertEqual(results[0].slug, 'slug-a-b-c,slug-x-y-z')

