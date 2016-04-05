#!/usr/bin/env python

try:
    import unittest2 as unittest
except ImportError:
    import unittest

from util.config import Config

class TestConfig(unittest.TestCase):
    def test_config_teams(self):
        config = Config(path='tests/config_test.yml')
        teams = config.get_teams()
        self.assertEqual(teams['carebot']['channel'], 'carebot-dev')

    def test_config_sources(self):
        config = Config(path='tests/config_test.yml')
        sources = config.get_sources()
        self.assertEqual(sources[1]['team'], 'carebot')

    def test_config_get_team_for_channel(self):
        config = Config(path='tests/config_test.yml')
        team = config.get_team_for_channel('carebot-dev')
        self.assertEqual(team, 'carebot')

    def test_config_get_team_for_channel_default(self):
        config = Config(path='tests/config_test.yml')
        team = config.get_team_for_channel('doesnotexist')
        self.assertEqual(team, 'viz')
