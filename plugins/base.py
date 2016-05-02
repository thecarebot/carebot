from util.config import Config
config = Config()

class CarebotPlugin(object):
    def __init__(self, story=None):
        if story:
            self.story = story
            self.team = config.get_team_for_story(self.story)

    def get_update_message(self, story):
        """
        Given a story, iterate through the slugs and return an update message
        for each slug.

        This will likely implement a "get_story_stats" method that pulls the
        appropriate stats for each slug in the story.
        """
        raise NotImplementedError("Update message is not implmeneted")

    def get_listeners(self):
        """
        Can register one or more expressions this plugin will listen and respond
        to. For example, "Carebot, how is slug x-y-z doing?"

        format:
        listeners = [
            ['listener-slug', regular expression to match, handler],
            ...
        ]
        """
        raise NotImplementedError("Plugin has no listeners")
