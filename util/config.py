import yaml

import logging
logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class Config:
    def __init__(self, path='config.yml'):
        with open(path, 'r') as yaml_file:
            data = yaml.load(yaml_file)
            self.config = data

    def get_teams(self):
        return self.config['teams']

    def get_team_for_channel(self, channel):
        teams = self.config['teams']
        for key in teams:
            print key, teams[key]['channel']
            if teams[key]['channel'] == channel:
                return key

        # Default to the first team's channel
        # Not robust, since dictionaries are not ordered.
        return teams.keys()[0]

    def get_sources(self):
        return self.config['sources']
