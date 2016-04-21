import yaml

import logging
logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

import app_config


class Config:
    def __init__(self, path=None):
        if not path:
            path = app_config.DEFAULT_CONFIG_PATH

        with open(path, 'r') as yaml_file:
            data = yaml.load(yaml_file)
            self.config = data

    def get_teams(self):
        return self.config['teams']

    def get_team_for_story(self, story):
        teams = self.config['teams']
        for key in teams:
            if key == story.team:
                return teams[key]

    def get_default_team(self):
        teams = self.config['teams']
        print self.config['teams']
        return teams['default']

    def get_team_for_channel(self, channel):
        teams = self.config['teams']
        for key in teams:
            print key, teams[key]['channel']
            if teams[key]['channel'] == channel:
                return key

        # Default to the first team's channel
        # Not robust, since dictionaries are not ordered.
        return 'default'

    def get_sources(self):
        return self.config['sources']
