from util.config import Config

class CarebotPlugin(object):
    def __init__(self, story=None):
        self.config = Config()

        if story:
            self.story = story
            self.team = config.get_team_for_story(self.story)

    def get_update_message(self, story):
        """
        Given a story, iterate through the slugs and return an update message
        for each slug.

        This will likely implement a "get_story_stats" method that pulls the
        appropriate stats for each slug in the story.

        Should return a message in the format
        {
            'text': 'Update text here',
            'attachments': [
                (optional) slack attachments, see slack documentation:
                https://api.slack.com/docs/attachments
            ]
        }
        """
        raise NotImplementedError("Update message is not implmeneted")

    def get_wait_message(self):
        """
        Optional.
        Called before any listener is triggered. Use this to let the user know
        that stats may take a minute to arrive.
        """
        raise NotImplementedError("Update message is not implmeneted")

    def get_listeners(self):
        """
        Can register one or more expressions this plugin will listen and respond
        to. For example, "Carebot, how is slug x-y-z doing?"

        format:
        listeners = [
            ['listener-slug', regular expression to match, handler, get_wait_message (optional)],
            ...
        ]
        """
        raise NotImplementedError("Plugin has no listeners")
