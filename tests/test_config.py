#!/usr/bin/env python

import app_config
try:
    import unittest2 as unittest
except ImportError:
    import unittest

from util.config import Config

app_config.TEAMS = {
    'default': {
        'channel': 'default-channel',
        'ga_org_id': 'DEFAULT-ID',
    },
    'viz': {
        'channel': 'visuals-graphics',
        'ga_org_id': 'visuals-sample-id',
    },
    'carebot': {
        'channel': 'carebot-dev',
        'ga_org_id': 'sample',
    },
}

class TestConfig(unittest.TestCase):
    def test_config_get_team_for_channel(self):
        config = Config()
        team = config.get_team_for_channel('carebot-dev')
        self.assertEqual(team, 'carebot')

    def test_config_get_team_for_channel_default(self):
        config = Config()
        team = config.get_team_for_channel('doesnotexist')
        self.assertEqual(team, 'default')

    def test_config_get_default_team(self):
        config = Config()
        team = config.get_default_team()
        self.assertEqual(team['ga_org_id'], 'DEFAULT-ID')

    def test_config_get_team_for_story(self):
        config = Config()
        class FakeStory:
            team = 'viz'

        team = config.get_team_for_story(FakeStory)
        self.assertEqual(team['ga_org_id'], 'visuals-sample-id')

    def test_config_get_team_for_story_none(self):
        config = Config()
        class FakeStory:
            team = 'no-such-team'

        team = config.get_team_for_story(FakeStory)
        self.assertEqual(team['ga_org_id'], 'DEFAULT-ID')
