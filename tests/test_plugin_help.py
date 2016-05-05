#!/usr/bin/env python

try:
    import unittest2 as unittest
except ImportError:
    import unittest

import datetime

from plugins.npr.help import NPRHelp

class TestNPRHelp(unittest.TestCase):
    def test_regex(self):
        """
        Test if the regular expressions match patterns we
        """
        matches = [
            '@carebot help',
            'What can you do ',
            'What are you up to'
        ]
        should_not_match = 'unsuck pageviews'

        patterns = NPRHelp().get_listeners()
        for i, pattern in enumerate(patterns):
            match = pattern[1].findall(matches[i])
            assert len(match) is 1

            match = pattern[1].findall(should_not_match)
            # print match, len(match)
            assert len(match) is 0

    def test_respond(self):
        """
        Make sure the respond function exists, runs, and returns text we expect
        to be in the help message.
        """
        message = NPRHelp().respond('example')
        assert 'calculate' in message['text']
