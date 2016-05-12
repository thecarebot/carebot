import logging
logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

import app_config


class Config:
    def __init__(self, path=None):
        self.teams = app_config.TEAMS

    def get_team_for_story(self, story):
        for key in self.teams:
            if key == story.team:
                return self.teams[key]

        return self.teams['default']

    def get_team_for_stories(self, stories):
        """
        Return the team of the first story in a list
        If the collection is empty, return the default team
        """
        try:
            return self.get_team_for_story(stories[0])
        except:
            return self.teams['default']

    def get_default_team(self):
        return self.teams['default']

    def get_team_for_channel(self, channel):
        for key in self.teams:
            print key, self.teams[key]['channel']
            if self.teams[key]['channel'] == channel:
                return key

        # Default to the first team's channel
        # Not robust, since dictionaries are not ordered.
        return 'default'
